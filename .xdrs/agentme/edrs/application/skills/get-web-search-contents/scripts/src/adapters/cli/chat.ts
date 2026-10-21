// Asks Google AI Mode one question (new thread or follow-up) through the open browser and prints the answer as JSON. See ../../../../SKILL.md.
import { chatCommand } from '../../app/commands';

import { defaultWiring, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(chatCommand, process.argv.slice(2), defaultWiring());
};

if (require.main === module) {
  void main();
}
