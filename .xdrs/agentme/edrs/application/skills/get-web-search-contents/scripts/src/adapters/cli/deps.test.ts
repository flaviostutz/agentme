import { createWorld } from '../../app/world_mock';
import { ExitError } from '../../shared/errors';

import { defaultWiring, runCli } from './deps';

describe('runCli', () => {
  it('returns the command exit code', async () => {
    const world = createWorld();
    expect(await runCli(() => 0, [], { ...world.deps, connect: () => world.deps.browser })).toBe(0);
  });

  it('maps usage errors to 2 and other failures to 1 and prints the message', async () => {
    const world = createWorld();
    const wiring = { ...world.deps, connect: () => world.deps.browser };
    expect(
      await runCli(
        () => {
          throw new ExitError(2, 'bad usage');
        },
        [],
        wiring,
      ),
    ).toBe(2);
    expect(
      await runCli(
        () => {
          throw new Error('boom');
        },
        [],
        wiring,
      ),
    ).toBe(1);
    expect(world.stderr.join('')).toBe('Error: bad usage\nError: boom\n');
  });
});

describe('defaultWiring', () => {
  it('wires the real connectors', async () => {
    const wiring = defaultWiring();
    expect(typeof wiring.connect('s', 9231).evalJson).toBe('function');
    expect(typeof wiring.state.read).toBe('function');
    expect(wiring.clock.now()).toBeGreaterThan(0);
    await wiring.clock.sleep(1);
    const out = jest.spyOn(process.stdout, 'write').mockReturnValue(true);
    const err = jest.spyOn(process.stderr, 'write').mockReturnValue(true);
    wiring.output.out('a');
    wiring.output.err('b');
    expect(out).toHaveBeenCalledWith('a');
    expect(err).toHaveBeenCalledWith('b');
    out.mockRestore();
    err.mockRestore();
  });
});
