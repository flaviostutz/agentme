#!/usr/bin/env node
'use strict';

// Prints every human PR thread comment as one normalized JSON array.
// Usage: pr-comments-list.js --pr-url <url>
const { parsePrUrl, parseArgs, runAz, restGet, normalizeThreads } = require('./azure-devops-lib');

function main(argv) {
  const args = parseArgs(argv);
  if (typeof args['pr-url'] !== 'string') {
    console.error('Usage: pr-comments-list.js --pr-url <url>');
    return 2;
  }
  const { apiBase, webUrl } = parsePrUrl(args['pr-url']);
  const threads = restGet((a) => runAz(a), `${apiBase}/threads`).value || [];
  process.stdout.write(`${JSON.stringify(normalizeThreads(threads, webUrl), null, 2)}\n`);
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
