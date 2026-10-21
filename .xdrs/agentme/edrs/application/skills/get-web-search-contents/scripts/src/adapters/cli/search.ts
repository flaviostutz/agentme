// Searches DuckDuckGo or Google through the open browser and prints results plus AI summary as JSON. See ../../../../SKILL.md.
import { searchCommand } from '../../app/commands';

import { defaultWiring, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(searchCommand, process.argv.slice(2), defaultWiring());
};

if (require.main === module) {
  void main();
}
