import { parseArgs, requireString } from './args';
import type { Deps } from './ports';
import { normalizeThreads, type Thread } from './pr';
import { restGet } from './rest';
import { parsePrUrl } from './urls';

const USAGE = 'pr-comments-list --pr-url <url>';

// Prints every human PR thread comment as one normalized JSON array.
export const runPrCommentsList = (argv: readonly string[], deps: Deps): number => {
  const { apiBase, webUrl } = parsePrUrl(requireString(parseArgs(argv), 'pr-url', USAGE));
  const threads = restGet<{ value?: Thread[] }>(deps.az, `${apiBase}/threads`).value ?? [];
  deps.output.out(`${JSON.stringify(normalizeThreads(threads, webUrl), null, 2)}\n`);
  return 0;
};
