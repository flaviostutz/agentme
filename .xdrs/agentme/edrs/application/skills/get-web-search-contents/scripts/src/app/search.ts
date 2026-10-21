import { ASSIST_WAIT_MS, POLL_MS, RESULTS_WAIT_MS } from '../shared/constants';
import { usageError } from '../shared/errors';

import { classifyPage } from './classify';
import { currentBudget, reserveSearch } from './counter';
import { normalizeAnswer, normalizeResults } from './normalize';
import { pageCall } from './page-call';
import type { Deps } from './ports';
import {
  clickConsentReject,
  clickDuckAssist,
  extractDuckAssist,
  extractDuckResults,
  extractGoogleResults,
  probePage,
} from './scripts';
import type {
  AiAnswer,
  Engine,
  PageProbe,
  PageState,
  RawAnswer,
  RawSearchPage,
  SearchBudget,
  SearchResult,
  Status,
} from './types';
import { searchUrl } from './urls';

export type SearchOptions = {
  query: string;
  engine: Engine;
  runId: string;
  maxSearches: number;
  googleConfirmed: boolean;
  lang?: string;
  region?: string;
};

export type SearchOutput = {
  status: Status;
  query: string;
  engine: Engine;
  requestedEngine: Engine;
  results: SearchResult[];
  ai?: AiAnswer;
  flags: string[];
  notes: string[];
  searches: SearchBudget;
};

type Attempt = {
  status: Status;
  results: SearchResult[];
  ai?: AiAnswer;
  flags: string[];
};

const pollUntil = async <T>(
  deps: Deps,
  windowMs: number,
  step: () => Promise<T | undefined>,
): Promise<T | undefined> => {
  const tries = Math.max(1, Math.ceil(windowMs / POLL_MS));
  const attempt = async (left: number): Promise<T | undefined> => {
    const value = await step();
    if (value !== undefined || left <= 1) return value;
    await deps.clock.sleep(POLL_MS);
    return attempt(left - 1);
  };
  return attempt(tries);
};

const probe = async (deps: Deps): Promise<PageProbe> =>
  (await deps.browser.evalJson(pageCall(probePage))) as PageProbe;

type Loaded = { state: PageState; page?: RawSearchPage; flags: string[] };

// Waits for results to render; a consent dialog gets the least-invasive click once.
const loadResults = async (deps: Deps, engine: Engine): Promise<Loaded> => {
  const extract = engine === 'duckduckgo' ? extractDuckResults : extractGoogleResults;
  const flags: string[] = [];
  const outcome = await pollUntil<Loaded>(deps, RESULTS_WAIT_MS, async () => {
    const state = classifyPage(engine, await probe(deps));
    if (state === 'consent') {
      const label = (await deps.browser.evalJson(pageCall(clickConsentReject))) as string;
      if (label.length > 0 && !flags.includes('consent-handled')) flags.push('consent-handled');
      return;
    }
    if (state !== 'ready') return { state, flags };
    const page = (await deps.browser.evalJson(pageCall(extract))) as RawSearchPage;
    return page.results.length > 0 ? { state, page, flags } : undefined;
  });
  if (outcome) return outcome;
  // A consent dialog that could not be rejected blocks the search; never accept it.
  const last = classifyPage(engine, await probe(deps));
  return { state: last === 'consent' ? 'blocked' : last, flags };
};

const readAssist = async (deps: Deps): Promise<{ ai?: AiAnswer; flags: string[] }> => {
  await deps.browser.evalJson(pageCall(clickDuckAssist));
  const raw = await pollUntil<RawAnswer>(deps, ASSIST_WAIT_MS, async () => {
    const answer = (await deps.browser.evalJson(pageCall(extractDuckAssist))) as RawAnswer;
    return answer.text.trim().length > 0 ? answer : undefined;
  });
  return raw
    ? { ai: normalizeAnswer('duckduckgo-search-assist', raw), flags: [] }
    : { flags: ['ai-summary-unreadable'] };
};

const attemptEngine = async (
  deps: Deps,
  engine: Engine,
  options: SearchOptions,
): Promise<Attempt> => {
  const index = await deps.browser.openTab(searchUrl(engine, options.query, options));
  try {
    const loaded = await loadResults(deps, engine);
    if (
      loaded.state === 'captcha' ||
      loaded.state === 'blocked' ||
      loaded.state === 'login-required'
    ) {
      return { status: loaded.state, results: [], flags: loaded.flags };
    }
    const results = normalizeResults(loaded.page?.results ?? []);
    if (results.length === 0) return { status: 'no-results', results, flags: loaded.flags };
    if (engine === 'duckduckgo' && loaded.page?.assistAvailable) {
      const assist = await readAssist(deps);
      return {
        status: 'ok',
        results,
        ai: assist.ai,
        flags: [...loaded.flags, ...assist.flags],
      };
    }
    return { status: 'ok', results, flags: [...loaded.flags, 'ai-summary-none'] };
  } finally {
    await deps.browser.closeTab(index);
  }
};

const other = (engine: Engine): Engine => (engine === 'duckduckgo' ? 'google' : 'duckduckgo');

export const runSearch = async (deps: Deps, options: SearchOptions): Promise<SearchOutput> => {
  if (options.engine === 'google' && !options.googleConfirmed) {
    throw usageError(
      "Google needs the person's confirmation: ask once per run, then pass --google-confirmed",
    );
  }
  await deps.browser.ensureSession();
  const base = { query: options.query, requestedEngine: options.engine };
  const capped = async (
    engine: Engine,
    notes: string[],
    flags: string[],
  ): Promise<SearchOutput> => ({
    ...base,
    engine,
    status: 'cap-reached',
    results: [],
    flags,
    notes: [...notes, `search cap of ${options.maxSearches} reached for run ${options.runId}`],
    searches: await currentBudget(deps, options.runId, options.maxSearches),
  });

  const first = await reserveSearch(deps, options.runId, options.maxSearches, 'search');
  if (!first.allowed) return capped(options.engine, [], []);
  const firstAttempt = await attemptEngine(deps, options.engine, options);
  const blocked = firstAttempt.status === 'captcha' || firstAttempt.status === 'blocked';
  if (!blocked) {
    return { ...base, engine: options.engine, ...firstAttempt, notes: [], searches: first.budget };
  }

  const fallback = other(options.engine);
  if (fallback === 'google' && !options.googleConfirmed) {
    return {
      ...base,
      engine: options.engine,
      ...firstAttempt,
      notes: [
        `${options.engine} blocked the search; falling back to Google needs the person's confirmation: ask, then rerun with --engine google --google-confirmed`,
      ],
      searches: first.budget,
    };
  }
  const second = await reserveSearch(deps, options.runId, options.maxSearches, 'search');
  if (!second.allowed)
    return capped(options.engine, [`${options.engine} was blocked`], firstAttempt.flags);
  const secondAttempt = await attemptEngine(deps, fallback, options);
  return {
    ...base,
    engine: fallback,
    ...secondAttempt,
    notes: [`${options.engine} was blocked (${firstAttempt.status}); used ${fallback} instead`],
    searches: second.budget,
  };
};
