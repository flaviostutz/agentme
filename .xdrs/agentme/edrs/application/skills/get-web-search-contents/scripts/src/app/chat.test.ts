import { AI_MODE_INPUT, runChat, type ChatOptions } from './chat';
import type { PageCall } from './page-call';
import type { PageProbe, RawAnswer } from './types';
import { createWorld } from './world_mock';

const options = (overrides: Partial<ChatOptions> = {}): ChatOptions => ({
  prompt: 'how to build a kit',
  freshThread: true,
  close: false,
  runId: 'run-1',
  maxSearches: 10,
  googleConfirmed: true,
  ...overrides,
});

const ready: PageProbe = {
  url: 'https://www.google.com/search?udm=50&q=x',
  title: 'AI Mode',
  text: '',
};

// Answers grow for a few polls and then stay stable.
const growingPage = (probe: PageProbe = ready, final = 'Step one. Step two.') => {
  let reads = 0;
  return (call: PageCall): unknown => {
    switch (call.name) {
      case 'probePage': {
        return probe;
      }
      case 'extractAiMode': {
        reads += 1;
        const text =
          reads === 1
            ? 'AI Mode conversation: how to build a kit Step'
            : `how to build a kit ${final}`;
        const answer: RawAnswer = {
          text,
          links: [{ text: 'Src', href: 'https://src.example/p?utm_x=1' }],
        };
        return answer;
      }
      case 'clickAiCitations': {
        return 2;
      }
      case 'clickConsentReject': {
        return 'Reject all';
      }
      default: {
        throw new Error(`unexpected page call ${call.name}`);
      }
    }
  };
};

describe('runChat', () => {
  it('requires the Google confirmation flag before touching the browser', async () => {
    const world = createWorld({ page: growingPage() });
    await expect(runChat(world.deps, options({ googleConfirmed: false }))).rejects.toThrow(
      /confirmation/,
    );
    expect(world.calls).toEqual([]);
  });

  it('starts a new thread and returns the settled answer cut after the prompt, with citations', async () => {
    const world = createWorld({ page: growingPage() });
    const output = await runChat(world.deps, options());
    expect(output.status).toBe('ok');
    expect(output.answer?.text).toBe('Step one. Step two.');
    expect(output.answer?.citations).toEqual([{ title: 'Src', url: 'https://src.example/p' }]);
    expect(output.searches).toEqual({ used: 1, max: 10 });
    expect(world.calls).toContain(
      'openTab https://www.google.com/search?udm=50&q=how%20to%20build%20a%20kit&hl=en',
    );
    expect(world.calls).not.toContain('closeTab 1');
    expect(world.calls).toContain('eval clickAiCitations');
  });

  it('closes its tab with --close', async () => {
    const world = createWorld({ page: growingPage() });
    await runChat(world.deps, options({ close: true }));
    expect(world.calls.at(-1)).toBe('closeTab 1');
  });

  it('sends a follow-up into the existing AI Mode tab and counts it as a search', async () => {
    const world = createWorld({ page: growingPage(), findTab: () => 3 });
    const output = await runChat(world.deps, options({ freshThread: false }));
    expect(output.status).toBe('ok');
    expect(world.calls).toEqual(
      expect.arrayContaining([
        'findTab udm=50',
        'selectTab 3',
        `fill ${AI_MODE_INPUT} how to build a kit`,
      ]),
    );
    expect(world.calls.some((c) => c.startsWith('openTab'))).toBe(false);
  });

  it('fails with a usage error when a follow-up has no open chat tab', async () => {
    const world = createWorld({ page: growingPage() });
    await expect(runChat(world.deps, options({ freshThread: false }))).rejects.toThrow(
      /no open AI Mode chat tab/,
    );
  });

  it('returns blocked when Google shows a challenge and does not fall back', async () => {
    const world = createWorld({
      page: growingPage({ url: 'https://www.google.com/sorry/index', title: 'Sorry', text: '' }),
      openTab: () => 7,
    });
    const output = await runChat(world.deps, options({ close: true }));
    expect(output.status).toBe('blocked');
    expect(output.notes[0]).toMatch(/no fallback exists for chat/);
    expect(world.calls.at(-1)).toBe('closeTab 7');
  });

  it('returns login-required when Google asks to sign in', async () => {
    const world = createWorld({
      page: growingPage({
        url: 'https://accounts.google.com/v3/signin/x',
        title: 'Sign in',
        text: '',
      }),
    });
    expect((await runChat(world.deps, options())).status).toBe('login-required');
  });

  it('rejects the consent dialog instead of accepting it', async () => {
    const world = createWorld({
      page: growingPage({
        url: 'https://consent.google.com/m',
        title: 'Before you continue',
        text: '',
      }),
    });
    await runChat(world.deps, options());
    expect(world.calls).toContain('eval clickConsentReject');
  });

  it('returns error with ai-summary-unreadable when the answer never settles', async () => {
    let n = 0;
    const world = createWorld({
      page: (call) => {
        if (call.name === 'probePage') return ready;
        n += 1;
        return { text: `how to build a kit ${'x'.repeat(n)}`, links: [] };
      },
    });
    const output = await runChat(world.deps, options());
    expect(output.status).toBe('error');
    expect(output.flags).toEqual(['ai-summary-unreadable']);
  });

  it('returns cap-reached once the run budget is used', async () => {
    const world = createWorld({ page: growingPage() });
    await runChat(world.deps, options({ maxSearches: 1 }));
    const second = await runChat(world.deps, options({ maxSearches: 1 }));
    expect(second.status).toBe('cap-reached');
    expect(second.searches).toEqual({ used: 1, max: 1 });
  });
});
