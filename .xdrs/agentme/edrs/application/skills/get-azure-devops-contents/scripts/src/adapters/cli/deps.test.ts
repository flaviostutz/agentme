import { createWorld } from '../../app/world_mock';
import { usageError } from '../../shared/errors';

import { runCli } from './deps';

describe('runCli', () => {
  it('returns the command exit code', async () => {
    expect(await runCli(() => 0, [], createWorld().deps)).toBe(0);
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
        throw Object.assign(new Error('Command failed'), { stderr: 'ERROR: TF400813\n' });
      },
      [],
      world.deps,
    );
    expect(code).toBe(1);
    expect(world.stderr.join('')).toBe('Error: ERROR: TF400813\n');
  });
});
