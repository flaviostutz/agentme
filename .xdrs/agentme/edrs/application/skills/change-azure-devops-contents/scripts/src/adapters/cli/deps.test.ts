import { mkdtempSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { createWorld } from '../../app/world_mock';
import { ExitError } from '../../shared/errors';
import { inputConnector } from '../connectors/input/input';

import { defaultDeps, runCli } from './deps';

describe('runCli', () => {
  it('returns the exit code, mapping usage errors to 2 and others to 1', async () => {
    const world = createWorld();
    expect(await runCli(() => 0, [], world.deps)).toBe(0);
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
          throw Object.assign(new Error('x'), { stderr: 'HTTP 500\n' });
        },
        [],
        world.deps,
      ),
    ).toBe(1);
    expect(world.stderr.join('')).toBe('Error: bad usage\nError: HTTP 500\n');
  });
});

describe('defaultDeps and inputConnector', () => {
  it('wires the connectors and reads an items file', () => {
    const deps = defaultDeps();
    const out = jest.spyOn(process.stdout, 'write').mockReturnValue(true);
    const err = jest.spyOn(process.stderr, 'write').mockReturnValue(true);
    deps.output.out('a');
    deps.output.err('b');
    expect(out).toHaveBeenCalledWith('a');
    expect(err).toHaveBeenCalledWith('b');
    out.mockRestore();
    err.mockRestore();
    const file = path.join(mkdtempSync(path.join(os.tmpdir(), 'cgc-')), 'items.json');
    writeFileSync(file, '[1]');
    expect(inputConnector.read(file)).toBe('[1]');
  });
});
