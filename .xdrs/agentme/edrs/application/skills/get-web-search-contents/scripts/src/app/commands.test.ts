import { chatCommand, searchCommand } from './commands';
import type { PageCall } from './page-call';
import type { Wiring } from './ports';
import { createWorld } from './world_mock';

const wiringOf = (
  world: ReturnType<typeof createWorld>,
  seen: { session?: string; port?: number } = {},
): Wiring => ({
  connect: (session, port) => {
    seen.session = session;
    seen.port = port;
    return world.deps.browser;
  },
  state: world.deps.state,
  clock: world.deps.clock,
  output: world.deps.output,
});

const duckPage = (call: PageCall): unknown => {
  switch (call.name) {
    case 'probePage': {
      return { url: 'https://duckduckgo.com/?q=x', title: 'x', text: '' };
    }
    case 'extractDuckResults': {
      return {
        results: [{ title: 'One', href: 'https://one.example/', snippet: 's' }],
        assistAvailable: false,
      };
    }
    default: {
      throw new Error(`unexpected ${call.name}`);
    }
  }
};

describe('searchCommand', () => {
  it('prints the JSON result and uses the default session and port', async () => {
    const world = createWorld({ page: duckPage });
    const seen: { session?: string; port?: number } = {};
    expect(await searchCommand(['--query', 'first aid'], wiringOf(world, seen))).toBe(0);
    const printed = JSON.parse(world.stdout.join('')) as { status: string; engine: string };
    expect(printed.status).toBe('ok');
    expect(printed.engine).toBe('duckduckgo');
    expect(seen).toEqual({ session: 'search', port: 9231 });
  });

  it('passes session, port and run options through', async () => {
    const world = createWorld({ page: duckPage });
    const seen: { session?: string; port?: number } = {};
    await searchCommand(
      [
        '--query',
        'x',
        '--session',
        'wsearch',
        '--cdp-port',
        '9300',
        '--run-id',
        'r1',
        '--max-searches',
        '3',
      ],
      wiringOf(world, seen),
    );
    expect(seen).toEqual({ session: 'wsearch', port: 9300 });
    expect(world.states.get('r1')?.searches).toBe(1);
  });

  it.each([
    [['--engine', 'duckduckgo'], /Usage: search/],
    [['--query', ''], /must not be empty/],
    [['--query', 'x', '--engine', 'bing'], /--engine must be/],
    [['--query', 'x', '--engine', 'google'], /confirmation/],
    [['--query', 'x', '--max-searches', '99'], /1 to 30/],
    [['--query', 'x', '--run-id', '../x'], /must match/],
    [['--query', 'x', '--cdp-port', '80'], /--cdp-port/],
    [['--query', 'mail me at a.b@example.com'], /email/],
    [['--query', 'x', '--session', 'a b'], /must match/],
  ])('rejects %j as a usage error without opening a browser', async (argv, message) => {
    const world = createWorld({ page: duckPage });
    await expect(searchCommand(argv, wiringOf(world))).rejects.toThrow(message);
    expect(world.calls).toEqual([]);
  });
});

describe('chatCommand', () => {
  it('requires a prompt and the Google confirmation', async () => {
    const world = createWorld({ page: duckPage });
    await expect(chatCommand([], wiringOf(world))).rejects.toThrow(/Usage: chat/);
    await expect(chatCommand(['--prompt', 'x'], wiringOf(world))).rejects.toThrow(/confirmation/);
    expect(world.calls).toEqual([]);
  });

  it('refuses a prompt that looks like a secret', async () => {
    const world = createWorld();
    await expect(
      chatCommand(
        ['--prompt', 'use password=hunter2 to log in', '--google-confirmed'],
        wiringOf(world),
      ),
    ).rejects.toThrow(/password/);
  });

  it('prints the JSON answer for a new thread', async () => {
    const world = createWorld({
      page: (call) => {
        if (call.name === 'probePage')
          return { url: 'https://www.google.com/search?udm=50', title: 'AI', text: '' };
        if (call.name === 'extractAiMode') return { text: 'why? because', links: [] };
        return 0;
      },
    });
    expect(
      await chatCommand(
        ['--prompt', 'why?', '--google-confirmed', '--new-thread', '--close', '--run-id', 'r2'],
        wiringOf(world),
      ),
    ).toBe(0);
    const printed = JSON.parse(world.stdout.join('')) as {
      status: string;
      answer: { text: string };
    };
    expect(printed.status).toBe('ok');
    expect(printed.answer.text).toBe('because');
    expect(world.calls).toContain('closeTab 1');
  });
});
