// Updates work item title and body from a JSON items file. See ../../../../SKILL.md.
import { runBatchCommand } from '../../app/batch';
import { workItemUpdate } from '../../app/work-item-handlers';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(
    (argv, deps) => runBatchCommand(argv, workItemUpdate, deps),
    process.argv.slice(2),
    defaultDeps(),
  );
};

if (require.main === module) {
  void main();
}
