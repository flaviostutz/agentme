// Prints one web page as readable text plus a status as JSON. See ../../../../SKILL.md.
import { runPageGet } from '../../app/page-get';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(runPageGet, process.argv.slice(2), defaultDeps());
};

if (require.main === module) {
  void main();
}
