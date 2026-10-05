import { createWorld } from '../../app/world_mock';
import { ExitError, usageError } from '../../shared/errors';

import { runCli } from './deps';

describe('runCli', () => {
  it('returns the command exit code', async () => {
    const world = createWorld();
    expect(await runCli(() => 0, [], world.deps)).toBe(0);
  });

  it('maps usage errors to 2 and prints them', async () => {
    const world = createWorld();
    const code = await runCli(
      () => {
        throw usageError('bad input');
      },
      [],
      world.deps,
    );
    expect(code).toBe(2);
    expect(world.stderr.join('')).toBe('Error: bad input\n');
  });

  it('maps other failures to 1 and prefers the CLI stderr', async () => {
    const world = createWorld();
    const code = await runCli(
      () => {
        throw Object.assign(new Error('Command failed'), { stderr: 'gh: HTTP 404\n' });
      },
      [],
      world.deps,
    );
    expect(code).toBe(1);
    expect(world.stderr.join('')).toBe('Error: gh: HTTP 404\n');
    expect(new ExitError(5, 'x').code).toBe(5);
  });
});
