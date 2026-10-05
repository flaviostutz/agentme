// Prints one Azure DevOps work item with comments, attachments and links as JSON. See ../../../../SKILL.md.
import { runWorkItemGet } from '../../app/work-item-get';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(runWorkItemGet, process.argv.slice(2), defaultDeps());
};

if (require.main === module) {
  void main();
}
