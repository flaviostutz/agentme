// Creates issues from a JSON items file. See ../../../../SKILL.md.
import { runBatchCommand } from '../../app/batch';
import { issueCreate } from '../../app/issue-handlers';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(
    (argv, deps) => runBatchCommand(argv, issueCreate, deps),
    process.argv.slice(2),
    defaultDeps(),
  );
};

if (require.main === module) {
  void main();
}
