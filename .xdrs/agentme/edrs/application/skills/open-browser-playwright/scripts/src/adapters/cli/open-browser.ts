// Opens a visible Edge window on a per-session copy of the user's profile, checks SSO over CDP and
// opens the target page. See ../../../../SKILL.md for commands, output lines and exit codes.
import os from 'node:os';

import { parseArgs } from '../../app/args';
import { runOpen } from '../../app/open';
import type { Deps } from '../../app/ports';
import { runTidy } from '../../app/tidy';
import { runWait } from '../../app/wait';
import { ExitError } from '../../shared/errors';
import { browserConnector } from '../connectors/cdp/browser';
import { filesConnector } from '../connectors/local-fs/profile';

export const defaultDeps = (): Deps => ({
  browser: browserConnector,
  files: filesConnector,
  clock: {
    now: () => Date.now(),
    sleep: async (ms) =>
      new Promise((resolve) => {
        setTimeout(resolve, ms);
      }),
  },
  output: {
    out: (text) => process.stdout.write(text),
    err: (text) => process.stderr.write(text),
  },
  host: {
    platform: process.platform,
    env: process.env,
    homedir: os.homedir(),
    tmpdir: os.tmpdir(),
  },
});

// Returns the process exit code; usage and runtime failures are thrown as ExitError.
export const run = async (argv: string[], deps: Deps): Promise<number> => {
  if (typeof WebSocket === 'undefined' || typeof fetch === 'undefined') {
    throw new ExitError(64, 'Node.js 22+ required');
  }
  const opts = parseArgs(argv, deps.host.env);
  if (opts.command === 'wait') return runWait(deps, opts);
  if (opts.command === 'tidy') return runTidy(deps, opts);
  return runOpen(deps, opts);
};

export const main = async (argv: string[], deps: Deps): Promise<number> => {
  try {
    return await run(argv, deps);
  } catch (error) {
    deps.output.err(`RESULT: error - ${(error as Error).message}\n`);
    return error instanceof ExitError ? error.code : 3;
  }
};

const start = async (): Promise<void> => {
  process.umask(0o077);
  process.exitCode = await main(process.argv.slice(2), defaultDeps());
};

if (require.main === module) void start();
