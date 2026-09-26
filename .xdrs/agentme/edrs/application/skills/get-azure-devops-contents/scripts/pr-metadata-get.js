#!/usr/bin/env node
'use strict';

// Prints Azure DevOps PR metadata as JSON. Usage: pr-metadata-get.js --pr-url <url>
const { parsePrUrl, parseArgs, runAz, pickPrMetadata } = require('./azure-devops-lib');

function main(argv) {
  const args = parseArgs(argv);
  if (typeof args['pr-url'] !== 'string') {
    console.error('Usage: pr-metadata-get.js --pr-url <url>');
    return 2;
  }
  const { pr, orgUrl, webUrl } = parsePrUrl(args['pr-url']);
  const raw = JSON.parse(runAz(['repos', 'pr', 'show', '--id', String(pr), '--organization', orgUrl, '--output', 'json']));
  process.stdout.write(`${JSON.stringify(pickPrMetadata(raw, webUrl), null, 2)}\n`);
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
