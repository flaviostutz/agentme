#!/usr/bin/env node
'use strict';

// Posts new general PR comments as new threads.
// Input: JSON array of {prUrl, body} via --input <file> or stdin.
const { cliMain, createHandler } = require('./azure-devops-lib');

if (require.main === module) {
  process.exitCode = cliMain(process.argv.slice(2), 'pr-comment-create.js [--input <file>] < items.json', (item) => createHandler(item));
}
