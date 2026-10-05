import { createWorld, html } from '../../app/world_mock';
import { ExitError } from '../../shared/errors';

import { defaultDeps, runCli } from './deps';

describe('runCli', () => {
  it('returns the command exit code', async () => {
    const world = createWorld();
    expect(await runCli(() => 0, [], world.deps)).toBe(0);
  });

  it('maps usage errors to 2 and other failures to 1 and prints the message', async () => {
    const world = createWorld({ http: () => html('') });
    expect(
      await runCli(
        () => {
          throw new ExitError(2, 'bad usage');
        },
        [],
        world.deps,
      ),
    ).toBe(2);
    expect(
      await runCli(
        () => {
          throw new Error('boom');
        },
        [],
        world.deps,
      ),
    ).toBe(1);
    expect(world.stderr.join('')).toBe('Error: bad usage\nError: boom\n');
  });
});

describe('defaultDeps', () => {
  it('wires the real connectors', () => {
    const deps = defaultDeps();
    expect(typeof deps.http.get).toBe('function');
    expect(typeof deps.dns.lookup).toBe('function');
    const out = jest.spyOn(process.stdout, 'write').mockReturnValue(true);
    const err = jest.spyOn(process.stderr, 'write').mockReturnValue(true);
    deps.output.out('a');
    deps.output.err('b');
    expect(out).toHaveBeenCalledWith('a');
    expect(err).toHaveBeenCalledWith('b');
    out.mockRestore();
    err.mockRestore();
  });
});
