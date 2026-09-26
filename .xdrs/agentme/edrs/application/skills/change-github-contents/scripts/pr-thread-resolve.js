#!/usr/bin/env node
'use strict';

// Resolves the review threads holding the given review comments.
// Input: JSON array of {prUrl, commentId} via --input <file> or stdin.
const { cliMain, resolveHandler } = require('./github-lib');

if (require.main === module) {
  process.exitCode = cliMain(process.argv.slice(2), 'pr-thread-resolve.js [--input <file>] < items.json', (item) => resolveHandler(item));
}
