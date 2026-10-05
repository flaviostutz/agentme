// Prints one GitHub issue with comments, attachments and links as JSON. See ../../../../SKILL.md.
import { runIssueGet } from '../../app/issue-get';

import { defaultDeps, runCli } from './deps';

const main = async (): Promise<void> => {
  process.exitCode = await runCli(runIssueGet, process.argv.slice(2), defaultDeps());
};

if (require.main === module) {
  void main();
}
