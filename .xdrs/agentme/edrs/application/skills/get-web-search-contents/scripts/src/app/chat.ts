import { ANSWER_WAIT_MS, MAX_CHAT_TEXT_CHARS, POLL_MS } from '../shared/constants';
import { usageError } from '../shared/errors';

import { classifyPage } from './classify';
import { currentBudget, reserveSearch } from './counter';
import { cutAfterPrompt, normalizeAnswer } from './normalize';
import { pageCall } from './page-call';
import type { Deps } from './ports';
import { clickAiCitations, clickConsentReject, extractAiMode, probePage } from './scripts';
import type { AiAnswer, PageProbe, RawAnswer, SearchBudget, Status } from './types';
import { aiModeUrl } from './urls';

export const AI_MODE_INPUT = 'textarea[aria-label="Ask anything"]';
const MIN_STABLE_POLLS = 2;

export type ChatOptions = {
  prompt: string;
  freshThread: boolean;
  close: boolean;
  runId: string;
  maxSearches: number;
  googleConfirmed: boolean;
  lang?: string;
  region?: string;
};

export type ChatOutput = {
  status: Status;
  engine: 'google-ai-mode';
  prompt: string;
  answer?: AiAnswer;
  flags: string[];
  notes: string[];
  searches: SearchBudget;
};

const readAnswer = async (deps: Deps): Promise<RawAnswer> =>
  (await deps.browser.evalJson(pageCall(extractAiMode))) as RawAnswer;

// The answer is settled once its length stops changing for MIN_STABLE_POLLS polls in a row.
const waitForSettled = async (deps: Deps, prompt: string): Promise<RawAnswer | undefined> => {
  const maxPolls = Math.ceil(ANSWER_WAIT_MS / POLL_MS);
  const step = async (
    left: number,
    lastLength: number,
    stable: number,
  ): Promise<RawAnswer | undefined> => {
    await deps.clock.sleep(POLL_MS);
    const raw = await readAnswer(deps);
    const length = raw.text.includes(prompt) ? cutAfterPrompt(raw.text, prompt).length : 0;
    const nextStable = length > 0 && length === lastLength ? stable + 1 : 0;
    if (nextStable >= MIN_STABLE_POLLS) return raw;
    return left <= 1 ? undefined : step(left - 1, length, nextStable);
  };
  return step(maxPolls, -1, 0);
};

const failure = (
  status: Status,
  options: ChatOptions,
  budget: SearchBudget,
  notes: string[],
  flags: string[] = [],
): ChatOutput => ({
  status,
  engine: 'google-ai-mode',
  prompt: options.prompt,
  flags,
  notes,
  searches: budget,
});

const start = async (deps: Deps, options: ChatOptions): Promise<number | undefined> => {
  if (options.freshThread) {
    return deps.browser.openTab(aiModeUrl(options.prompt, options));
  }
  const index = await deps.browser.findTab('udm=50');
  if (index === undefined) return undefined;
  await deps.browser.selectTab(index);
  await deps.browser.fillAndSubmit(AI_MODE_INPUT, options.prompt);
  return index;
};

export const runChat = async (deps: Deps, options: ChatOptions): Promise<ChatOutput> => {
  if (!options.googleConfirmed) {
    throw usageError(
      "Google AI Mode needs the person's confirmation: ask once per run, then pass --google-confirmed",
    );
  }
  await deps.browser.ensureSession();
  const reservation = await reserveSearch(deps, options.runId, options.maxSearches, 'chat');
  if (!reservation.allowed) {
    return failure(
      'cap-reached',
      options,
      await currentBudget(deps, options.runId, options.maxSearches),
      [`search cap of ${options.maxSearches} reached for run ${options.runId}`],
    );
  }
  const index = await start(deps, options);
  if (index === undefined) {
    throw usageError('no open AI Mode chat tab found; start a thread with --new-thread');
  }
  try {
    const state = classifyPage(
      'google',
      (await deps.browser.evalJson(pageCall(probePage))) as PageProbe,
    );
    if (state === 'consent') await deps.browser.evalJson(pageCall(clickConsentReject));
    if (state === 'captcha' || state === 'blocked' || state === 'login-required') {
      return failure(state === 'login-required' ? state : 'blocked', options, reservation.budget, [
        `Google answered with ${state}; no fallback exists for chat`,
      ]);
    }
    const settled = await waitForSettled(deps, options.prompt);
    if (!settled) {
      return failure(
        'error',
        options,
        reservation.budget,
        ['the answer did not settle in time'],
        ['ai-summary-unreadable'],
      );
    }
    await deps.browser.evalJson(pageCall(clickAiCitations));
    await deps.clock.sleep(POLL_MS);
    const withSources = await readAnswer(deps);
    const text = cutAfterPrompt(withSources.text, options.prompt);
    return {
      status: 'ok',
      engine: 'google-ai-mode',
      prompt: options.prompt,
      answer: normalizeAnswer('google-ai-mode', withSources, text, MAX_CHAT_TEXT_CHARS),
      flags: [],
      notes: [],
      searches: reservation.budget,
    };
  } finally {
    if (options.close) await deps.browser.closeTab(index);
  }
};
