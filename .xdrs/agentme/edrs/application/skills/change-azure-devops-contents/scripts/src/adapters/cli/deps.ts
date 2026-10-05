import type { Deps } from '../../app/ports';
import { ExitError } from '../../shared/errors';
import { createAz } from '../connectors/az/az';
import { bodyFileConnector } from '../connectors/body-file/body-file';
import { inputConnector } from '../connectors/input/input';
import { createPandoc } from '../connectors/pandoc/pandoc';

export const defaultDeps = (): Deps => ({
  az: createAz(process.env),
  input: inputConnector,
  bodyFile: bodyFileConnector,
  markdown: createPandoc(process.env),
  output: {
    out: (text) => process.stdout.write(text),
    err: (text) => process.stderr.write(text),
  },
});

const failureText = (error: unknown): string => {
  const { stderr } = error as { stderr?: string };
  return String(stderr ?? (error as Error).message).trim();
};

// Runs one command; usage errors exit 2 and every other failure exits 1.
export const runCli = async (
  command: (argv: readonly string[], deps: Deps) => number | Promise<number>,
  argv: readonly string[],
  deps: Deps,
): Promise<number> => {
  try {
    return await command(argv, deps);
  } catch (error) {
    deps.output.err(`Error: ${failureText(error)}\n`);
    return error instanceof ExitError ? error.code : 1;
  }
};
