#!/usr/bin/env node
'use strict';

// Prints every PR comment (issue comments, review comments, review summaries) as one
// normalized JSON array. Usage: pr-comments-list.js --pr-url <url>
const { parsePrUrl, parseArgs, runGh, flattenPages, parseJsonStream, THREADS_QUERY, threadsFromGraphql, normalizeComments } = require('./github-lib');

function main(argv) {
  const args = parseArgs(argv);
  if (typeof args['pr-url'] !== 'string') {
    console.error('Usage: pr-comments-list.js --pr-url <url>');
    return 2;
  }
  const { owner, repo, pr } = parsePrUrl(args['pr-url']);
  const rest = (path) => flattenPages(runGh(['api', '--paginate', `repos/${owner}/${repo}/${path}`]));
  const threads = threadsFromGraphql(
    parseJsonStream(
      runGh(['api', 'graphql', '--paginate', '-f', `query=${THREADS_QUERY}`, '-f', `owner=${owner}`, '-f', `repo=${repo}`, '-F', `pr=${pr}`]),
    ),
  );
  const records = normalizeComments({
    issueComments: rest(`issues/${pr}/comments`),
    reviewComments: rest(`pulls/${pr}/comments`),
    reviews: rest(`pulls/${pr}/reviews`),
    threads,
  });
  process.stdout.write(`${JSON.stringify(records, null, 2)}\n`);
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
