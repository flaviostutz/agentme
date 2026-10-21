import { mkdtemp, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

import { fsState } from './state';

describe('fsState', () => {
  const original = process.cwd();

  let dir = '';

  beforeEach(async () => {
    dir = await mkdtemp(path.join(os.tmpdir(), 'wsc-state-'));
    process.chdir(dir);
  });

  afterEach(async () => {
    process.chdir(original);
    await rm(dir, { recursive: true, force: true });
  });

  it('returns undefined for an unknown run and round-trips a written state', async () => {
    expect(await fsState.read('run-1')).toBeUndefined();
    await fsState.write('run-1', { searches: 3, chatTurns: 1, lastAt: 42 });
    expect(await fsState.read('run-1')).toEqual({ searches: 3, chatTurns: 1, lastAt: 42 });
    expect(await fsState.read('run-2')).toBeUndefined();
  });
});
