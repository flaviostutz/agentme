import type { Wiring } from '../../app/ports';
import { ExitError } from '../../shared/errors';
import { playwrightCliBrowser } from '../connectors/playwright-cli/browser';
import { fsState } from '../connectors/fs/state';

export const defaultWiring = (): Wiring => ({
  connect: playwrightCliBrowser,
  state: fsState,
  clock: {
    now: () => Date.now(),
    sleep: async (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  },
  output: {
    out: (text) => process.stdout.write(text),
    err: (text) => process.stderr.write(text),
  },
});

// Runs one command; usage errors exit 2 and every other failure exits 1.
export const runCli = async (
  command: (argv: readonly string[], wiring: Wiring) => number | Promise<number>,
  argv: readonly string[],
  wiring: Wiring,
): Promise<number> => {
  try {
    return await command(argv, wiring);
  } catch (error) {
    wiring.output.err(`Error: ${(error as Error).message}\n`);
    return error instanceof ExitError ? error.code : 1;
  }
};
