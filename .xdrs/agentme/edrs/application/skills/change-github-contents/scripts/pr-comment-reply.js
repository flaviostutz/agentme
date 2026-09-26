#!/usr/bin/env node
'use strict';

// Replies to PR comments. Input: JSON array of {prUrl, commentId, body} via --input <file> or stdin.
// review-comment replies go to the thread root; other kinds become a new PR comment.
const { cliMain, replyHandler } = require('./github-lib');

if (require.main === module) {
  process.exitCode = cliMain(process.argv.slice(2), 'pr-comment-reply.js [--input <file>] < items.json', (item) => replyHandler(item));
}
