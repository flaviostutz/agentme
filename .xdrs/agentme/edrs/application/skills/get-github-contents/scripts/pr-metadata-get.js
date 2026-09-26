#!/usr/bin/env node
'use strict';

// Prints GitHub PR metadata as JSON. Usage: pr-metadata-get.js --pr-url <url>
const { parsePrUrl, parseArgs, runGh } = require('./github-lib');

const FIELDS = 'number,title,body,state,url,baseRefName,headRefName,isCrossRepository,headRepositoryOwner,headRepository';

function main(argv) {
  const args = parseArgs(argv);
  if (typeof args['pr-url'] !== 'string') {
    console.error('Usage: pr-metadata-get.js --pr-url <url>');
    return 2;
  }
  const { owner, repo, pr } = parsePrUrl(args['pr-url']);
  const out = runGh(['pr', 'view', String(pr), '--repo', `${owner}/${repo}`, '--json', FIELDS]);
  process.stdout.write(`${JSON.stringify(JSON.parse(out), null, 2)}\n`);
  return 0;
}

if (require.main === module) {
  try {
    process.exitCode = main(process.argv.slice(2));
  } catch (err) {
    console.error(`Error: ${String(err.stderr || err.message).trim()}`);
    process.exitCode = 1;
  }
}

module.exports = { main };
