import { makeWorld } from '../../app/world_mock';

import { defaultDeps, main, run } from './open-browser';

describe('open-browser CLI', () => {
  it('runs the tidy command through the injected dependencies', async () => {
    const world = makeWorld();
    await expect(run(['tidy', 's1'], world.deps)).resolves.toBe(0);
    expect(world.stdout.join('')).toContain('RESULT: no-session');
  });

  it('runs the open command through the injected dependencies', async () => {
    const world = makeWorld();
    await expect(run(['s1', 'https://app.example.com/'], world.deps)).resolves.toBe(0);
    expect(world.stdout.join('')).toContain('RESULT: authenticated');
  });

  it('runs the wait command and reports a missing browser as exit 3', async () => {
    const world = makeWorld();
    await expect(main(['wait', 's1', 'https://app.example.com/'], world.deps)).resolves.toBe(3);
    expect(world.stderr.join('')).toMatch(/^RESULT: error - no open browser for session s1/);
  });

  it('maps usage errors to exit 64 without any output on stdout', async () => {
    const world = makeWorld();
    await expect(main([], world.deps)).resolves.toBe(64);
    expect(world.stderr.join('')).toMatch(/^RESULT: error - /);
    expect(world.stdout).toEqual([]);
  });

  it('maps unexpected failures to exit 3', async () => {
    const world = makeWorld();
    world.deps.browser.version = async () => {
      throw new Error('unexpected');
    };
    world.seedSession('s1', {});
    await expect(main(['tidy', 's1'], world.deps)).resolves.toBe(3);
    expect(world.stderr.join('')).toBe('RESULT: error - unexpected\n');
  });

  it('fails with exit 64 when the runtime has no WebSocket', async () => {
    const world = makeWorld();
    const original = Object.getOwnPropertyDescriptor(globalThis, 'WebSocket');
    Reflect.deleteProperty(globalThis, 'WebSocket');
    try {
      await expect(main(['tidy', 's1'], world.deps)).resolves.toBe(64);
      expect(world.stderr.join('')).toContain('Node.js 22+ required');
    } finally {
      if (original) Object.defineProperty(globalThis, 'WebSocket', original);
    }
  });
});

describe('defaultDeps', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('wires the real connectors, clock, output and host', async () => {
    const deps = defaultDeps();
    expect(deps.host.platform).toBe(process.platform);
    expect(typeof deps.host.env).toBe('object');
    expect(deps.clock.now()).toBeLessThanOrEqual(Date.now());
    await expect(deps.clock.sleep(1)).resolves.toBeUndefined();
    const out = jest.spyOn(process.stdout, 'write').mockReturnValue(true);
    const err = jest.spyOn(process.stderr, 'write').mockReturnValue(true);
    deps.output.out('a');
    deps.output.err('b');
    expect(out).toHaveBeenCalledWith('a');
    expect(err).toHaveBeenCalledWith('b');
  });
});
