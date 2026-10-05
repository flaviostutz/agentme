import { parseArgs, requireString } from './args';
import type { Deps } from './ports';
import { type PrDetails, pickPrMetadata } from './pr';
import { parsePrUrl } from './urls';

const USAGE = 'pr-metadata-get --pr-url <url>';

// Prints Azure DevOps PR metadata as JSON.
export const runPrMetadataGet = (argv: readonly string[], deps: Deps): number => {
  const { pr, orgUrl, webUrl } = parsePrUrl(requireString(parseArgs(argv), 'pr-url', USAGE));
  const raw = JSON.parse(
    deps.az.run([
      'repos',
      'pr',
      'show',
      '--id',
      String(pr),
      '--organization',
      orgUrl,
      '--output',
      'json',
    ]),
  ) as PrDetails;
  deps.output.out(`${JSON.stringify(pickPrMetadata(raw, webUrl), null, 2)}\n`);
  return 0;
};
