import type { Deps } from '../../app/ports';
import { ExitError } from '../../shared/errors';
import { dnsConnector } from '../connectors/dns/dns';
import { httpConnector } from '../connectors/http/http';

export const defaultDeps = (): Deps => ({
  http: httpConnector,
  dns: dnsConnector,
  output: {
    out: (text) => process.stdout.write(text),
    err: (text) => process.stderr.write(text),
  },
});

// Runs one command; usage errors exit 2 and every other failure exits 1.
export const runCli = async (
  command: (argv: readonly string[], deps: Deps) => number | Promise<number>,
  argv: readonly string[],
  deps: Deps,
): Promise<number> => {
  try {
    return await command(argv, deps);
  } catch (error) {
    deps.output.err(`Error: ${(error as Error).message}\n`);
    return error instanceof ExitError ? error.code : 1;
  }
};
