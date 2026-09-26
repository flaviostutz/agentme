#!/usr/bin/env node
'use strict';

// Sets PR thread status (e.g. fixed, wontFix, closed, active).
// Input: JSON array of {prUrl, commentId, status} via --input <file> or stdin.
const { cliMain, statusSetHandler } = require('./azure-devops-lib');

if (require.main === module) {
  process.exitCode = cliMain(process.argv.slice(2), 'pr-thread-status-set.js [--input <file>] < items.json', (item) => statusSetHandler(item));
}
