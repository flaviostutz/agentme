// Prints GitHub PR metadata as JSON. See ../../../../SKILL.md.
import { runPrMetadataGet } from '../../app/pr-metadata-get';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(runPrMetadataGet, process.argv.slice(2), defaultDeps());
};

if (require.main === module) {
  void main();
}
