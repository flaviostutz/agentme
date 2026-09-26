#!/usr/bin/env node
'use strict';

// Replies inside existing PR threads.
// Input: JSON array of {prUrl, commentId, body} via --input <file> or stdin.
const { cliMain, replyHandler } = require('./azure-devops-lib');

if (require.main === module) {
  process.exitCode = cliMain(process.argv.slice(2), 'pr-comment-reply.js [--input <file>] < items.json', (item) => replyHandler(item));
}
