import { parseArgs, requireString } from './args';
import type { Deps } from './ports';
import { parsePrUrl } from './urls';

const USAGE = 'pr-metadata-get --pr-url <url>';

const FIELDS =
  'number,title,body,state,url,baseRefName,headRefName,isCrossRepository,headRepositoryOwner,headRepository';

export const runPrMetadataGet = (argv: readonly string[], deps: Deps): number => {
  const { owner, repo, pr } = parsePrUrl(requireString(parseArgs(argv), 'pr-url', USAGE));
  const out = deps.gh.run([
    'pr',
    'view',
    String(pr),
    '--repo',
    `${owner}/${repo}`,
    '--json',
    FIELDS,
  ]);
  deps.output.out(`${JSON.stringify(JSON.parse(out), null, 2)}\n`);
  return 0;
};
