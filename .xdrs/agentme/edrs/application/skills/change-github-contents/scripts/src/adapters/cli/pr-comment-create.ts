// Posts general PR comments from a JSON items file. See ../../../../SKILL.md.
import { runBatchCommand } from '../../app/batch';
import { prCommentCreate } from '../../app/pr-handlers';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(
    (argv, deps) => runBatchCommand(argv, prCommentCreate, deps),
    process.argv.slice(2),
    defaultDeps(),
  );
};

if (require.main === module) {
  void main();
}
