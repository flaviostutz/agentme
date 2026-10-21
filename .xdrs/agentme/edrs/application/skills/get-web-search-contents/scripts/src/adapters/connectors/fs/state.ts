import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

import type { RunState, StatePort } from '../../../app/ports';
import { STATE_ROOT } from '../../../shared/constants';

const counterFile = (runId: string): string => path.join(STATE_ROOT, runId, 'counter.json');

// Keeps the per-run counter in the workspace .tmp folder; the run id is validated before it gets here.
export const fsState: StatePort = {
  read: async (runId): Promise<RunState | undefined> => {
    try {
      return JSON.parse(await readFile(counterFile(runId), 'utf8')) as RunState;
    } catch {
      return undefined;
    }
  },
  write: async (runId, state): Promise<void> => {
    await mkdir(path.dirname(counterFile(runId)), { recursive: true });
    await writeFile(counterFile(runId), `${JSON.stringify(state)}\n`, 'utf8');
  },
};
