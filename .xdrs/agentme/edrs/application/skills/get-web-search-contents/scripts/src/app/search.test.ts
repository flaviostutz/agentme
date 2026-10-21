import type { PageCall } from './page-call';
import { runSearch, type SearchOptions } from './search';
import type { PageProbe, RawAnswer, RawSearchPage } from './types';
import { createWorld } from './world_mock';

const options = (overrides: Partial<SearchOptions> = {}): SearchOptions => ({
  query: 'offline first aid',
  engine: 'duckduckgo',
  runId: 'run-1',
  maxSearches: 10,
  googleConfirmed: false,
  ...overrides,
});

const duckPage: RawSearchPage = {
  results: [
    { title: 'One', href: 'https://one.example/a', snippet: 'first' },
    { title: 'Two', href: 'https://two.example/b', snippet: 'second' },
  ],
  assistAvailable: true,
};

const probeOf = (url: string, text = ''): PageProbe => ({ url, title: 'Page', text });

type Page = {
  probe?: () => PageProbe;
  duck?: RawSearchPage;
  google?: RawSearchPage;
  assist?: RawAnswer;
  consent?: string;
};

const pageFor =
  (page: Page) =>
  (call: PageCall): unknown => {
    switch (call.name) {
      case 'probePage': {
        return page.probe ? page.probe() : probeOf('https://duckduckgo.com/?q=x');
      }
      case 'extractDuckResults': {
        return page.duck ?? { results: [], assistAvailable: false };
      }
      case 'extractGoogleResults': {
        return page.google ?? { results: [], assistAvailable: false };
      }
      case 'clickDuckAssist': {
        return true;
      }
      case 'extractDuckAssist': {
        return page.assist ?? { text: '', links: [] };
      }
      case 'clickConsentReject': {
        return page.consent ?? '';
      }
      default: {
        throw new Error(`unexpected page call ${call.name}`);
      }
    }
  };

describe('runSearch on DuckDuckGo', () => {
  it('returns results and the Search Assist answer, clicking the button automatically', async () => {
    const world = createWorld({
      page: pageFor({
        duck: duckPage,
        assist: { text: 'Assist answer', links: [{ text: 'Src', href: 'https://src.example/p' }] },
      }),
    });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('ok');
    expect(output.engine).toBe('duckduckgo');
    expect(output.results.map((r) => r.url)).toEqual([
      'https://one.example/a',
      'https://two.example/b',
    ]);
    expect(output.ai).toEqual({
      source: 'duckduckgo-search-assist',
      text: 'Assist answer',
      citations: [{ title: 'Src', url: 'https://src.example/p' }],
    });
    expect(output.searches).toEqual({ used: 1, max: 10 });
    expect(world.calls).toContain('eval clickDuckAssist');
    expect(world.calls.at(-1)).toBe('closeTab 1');
    expect(world.calls[1]).toBe('openTab https://duckduckgo.com/?q=offline%20first%20aid');
  });

  it('flags ai-summary-none when no Search Assist button is shown', async () => {
    const world = createWorld({
      page: pageFor({ duck: { ...duckPage, assistAvailable: false } }),
    });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('ok');
    expect(output.ai).toBeUndefined();
    expect(output.flags).toEqual(['ai-summary-none']);
    expect(world.calls).not.toContain('eval clickDuckAssist');
  });

  it('flags ai-summary-unreadable when the answer never renders, keeping the results', async () => {
    const world = createWorld({ page: pageFor({ duck: duckPage }) });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('ok');
    expect(output.ai).toBeUndefined();
    expect(output.flags).toEqual(['ai-summary-unreadable']);
    expect(output.results).toHaveLength(2);
  });

  it('returns no-results after the wait window when nothing renders', async () => {
    const world = createWorld({ page: pageFor({}) });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('no-results');
    expect(output.results).toEqual([]);
    expect(world.calls.at(-1)).toBe('closeTab 1');
  });
});

describe('runSearch blocking and fallback', () => {
  const captcha = (): PageProbe => probeOf('https://duckduckgo.com/', 'bots use DuckDuckGo too');

  it('stops with captcha and asks for confirmation before falling back to Google', async () => {
    const world = createWorld({ page: pageFor({ probe: captcha }) });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('captcha');
    expect(output.engine).toBe('duckduckgo');
    expect(output.notes.join(' ')).toMatch(/needs the person's confirmation/);
    expect(world.calls.filter((c) => c.startsWith('openTab'))).toHaveLength(1);
    expect(world.calls.at(-1)).toBe('closeTab 1');
    expect(output.searches.used).toBe(1);
  });

  it('falls back to Google when confirmed, reports the engine used and counts both attempts', async () => {
    let calls = 0;
    const world = createWorld({
      page: pageFor({
        probe: () => {
          calls += 1;
          return calls === 1 ? captcha() : probeOf('https://www.google.com/search?q=x');
        },
        google: {
          results: [{ title: 'G', href: 'https://g.example/', snippet: 's' }],
          assistAvailable: false,
        },
      }),
    });
    const output = await runSearch(world.deps, options({ googleConfirmed: true }));
    expect(output.status).toBe('ok');
    expect(output.engine).toBe('google');
    expect(output.requestedEngine).toBe('duckduckgo');
    expect(output.notes[0]).toMatch(/duckduckgo was blocked \(captcha\); used google/);
    expect(output.searches).toEqual({ used: 2, max: 10 });
    expect(world.sleeps).toContain(3000);
  });

  it('falls back from Google to DuckDuckGo without needing a new confirmation', async () => {
    const world = createWorld({
      page: pageFor({
        probe: (() => {
          let n = 0;
          return () => {
            n += 1;
            return n === 1
              ? probeOf('https://www.google.com/sorry/index')
              : probeOf('https://duckduckgo.com/?q=x');
          };
        })(),
        duck: { ...duckPage, assistAvailable: false },
      }),
    });
    const output = await runSearch(
      world.deps,
      options({ engine: 'google', googleConfirmed: true }),
    );
    expect(output.engine).toBe('duckduckgo');
    expect(output.status).toBe('ok');
  });

  it('refuses Google without the confirmation flag, before touching the browser', async () => {
    const world = createWorld({ page: pageFor({}) });
    await expect(runSearch(world.deps, options({ engine: 'google' }))).rejects.toThrow(
      /confirmation/,
    );
    expect(world.calls).toEqual([]);
  });

  it('reports a blocked state without trying a fallback when the fallback needs confirmation', async () => {
    const world = createWorld({
      page: pageFor({
        probe: () => ({ url: 'https://duckduckgo.com/', title: 'Too Many Requests', text: '' }),
      }),
    });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('blocked');
    expect(world.calls.filter((c) => c.startsWith('openTab'))).toHaveLength(1);
  });

  it('reports login-required without a fallback', async () => {
    const world = createWorld({
      page: pageFor({ probe: () => probeOf('https://x.org', 'Sign in to continue') }),
    });
    const output = await runSearch(world.deps, options());
    expect(output.status).toBe('login-required');
    expect(world.calls.filter((c) => c.startsWith('openTab'))).toHaveLength(1);
  });
});

describe('runSearch cap and consent', () => {
  it('returns cap-reached without opening a tab once the run is used up', async () => {
    const world = createWorld({ page: pageFor({ duck: duckPage }) });
    const output = await runSearch(world.deps, options({ maxSearches: 1 }));
    expect(output.status).toBe('ok');
    const second = await runSearch(world.deps, options({ maxSearches: 1 }));
    expect(second.status).toBe('cap-reached');
    expect(second.notes.join(' ')).toMatch(/cap of 1 reached for run run-1/);
    expect(world.calls.filter((c) => c.startsWith('openTab'))).toHaveLength(1);
  });

  it('keeps separate counters per run id', async () => {
    const world = createWorld({ page: pageFor({ duck: duckPage }) });
    await runSearch(world.deps, options({ maxSearches: 1 }));
    const other = await runSearch(world.deps, options({ maxSearches: 1, runId: 'run-2' }));
    expect(other.status).toBe('ok');
  });

  it('stops with cap-reached when the cap is hit between the first attempt and the fallback', async () => {
    const world = createWorld({
      page: pageFor({ probe: () => probeOf('https://duckduckgo.com/', 'bots use DuckDuckGo too') }),
    });
    const output = await runSearch(world.deps, options({ maxSearches: 1, googleConfirmed: true }));
    expect(output.status).toBe('cap-reached');
    expect(output.notes[0]).toBe('duckduckgo was blocked');
  });

  it('rejects the consent dialog with the reject choice and reports consent-handled', async () => {
    let n = 0;
    const world = createWorld({
      page: pageFor({
        probe: () => {
          n += 1;
          return n === 1
            ? probeOf('https://consent.google.com/m')
            : probeOf('https://www.google.com/search?q=x');
        },
        consent: 'Reject all',
        google: {
          results: [{ title: 'G', href: 'https://g.example/', snippet: '' }],
          assistAvailable: false,
        },
      }),
    });
    const output = await runSearch(
      world.deps,
      options({ engine: 'google', googleConfirmed: true }),
    );
    expect(output.status).toBe('ok');
    expect(output.flags).toContain('consent-handled');
    expect(world.calls).toContain('eval clickConsentReject');
  });

  it('treats a consent dialog that cannot be rejected as blocked and never accepts it', async () => {
    const world = createWorld({
      page: pageFor({ probe: () => probeOf('https://consent.google.com/m'), consent: '' }),
    });
    const output = await runSearch(
      world.deps,
      options({ engine: 'google', googleConfirmed: true }),
    );
    expect(output.status).toBe('blocked');
    expect(output.engine).toBe('duckduckgo');
    expect(output.flags).not.toContain('consent-handled');
  });
});
