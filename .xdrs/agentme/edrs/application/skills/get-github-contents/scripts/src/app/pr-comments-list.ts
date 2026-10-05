import { parseArgs, requireString } from './args';
import { normalizeComments, THREADS_QUERY, threadsFromGraphql } from './comments';
import { flattenPages, parseJsonStream } from './json-stream';
import type { Deps } from './ports';
import { parsePrUrl } from './urls';

const USAGE = 'pr-comments-list --pr-url <url>';

// Prints every PR comment (issue comments, review comments, review summaries) as one normalized array.
export const runPrCommentsList = (argv: readonly string[], deps: Deps): number => {
  const { owner, repo, pr } = parsePrUrl(requireString(parseArgs(argv), 'pr-url', USAGE));
  const rest = <T>(path: string): T[] =>
    flattenPages<T>(deps.gh.run(['api', '--paginate', `repos/${owner}/${repo}/${path}`]));
  const threads = threadsFromGraphql(
    parseJsonStream(
      deps.gh.run([
        'api',
        'graphql',
        '--paginate',
        '-f',
        `query=${THREADS_QUERY}`,
        '-f',
        `owner=${owner}`,
        '-f',
        `repo=${repo}`,
        '-F',
        `pr=${pr}`,
      ]),
    ),
  );
  const records = normalizeComments({
    issueComments: rest(`issues/${pr}/comments`),
    reviewComments: rest(`pulls/${pr}/comments`),
    reviews: rest(`pulls/${pr}/reviews`),
    threads,
  });
  deps.output.out(`${JSON.stringify(records, null, 2)}\n`);
  return 0;
};
