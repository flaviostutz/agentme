// Prints every PR comment as one normalized JSON array. See ../../../../SKILL.md.
import { runPrCommentsList } from '../../app/pr-comments-list';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(runPrCommentsList, process.argv.slice(2), defaultDeps());
};

if (require.main === module) {
  void main();
}
