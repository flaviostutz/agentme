#!/usr/bin/env node
'use strict';

const fs = require('fs');
const { execFileSync } = require('child_process');

function parsePrUrl(url) {
  const m = /^https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/pull\/(\d+)(?:[/?#].*)?$/.exec(String(url || ''));
  if (!m) throw new Error(`unrecognized GitHub PR URL: ${url}`);
  return { owner: m[1], repo: m[2], pr: Number(m[3]) };
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`unexpected argument: ${a}`);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) args[a.slice(2)] = true;
    else {
      args[a.slice(2)] = next;
      i++;
    }
  }
  return args;
}

function splitBin(value, fallback) {
  const parts = String(value || fallback)
    .split(' ')
    .filter(Boolean);
  return { bin: parts[0], prefix: parts.slice(1) };
}

// `gh api --paginate` prints one JSON value per page back to back (e.g. `[..][..]`).
function parseJsonStream(text) {
  const values = [];
  let depth = 0;
  let start = -1;
  let inString = false;
  let escaped = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') inString = true;
    else if (ch === '[' || ch === '{') {
      if (depth === 0) start = i;
      depth++;
    } else if (ch === ']' || ch === '}') {
      depth--;
      if (depth === 0) values.push(JSON.parse(text.slice(start, i + 1)));
    }
  }
  if (depth !== 0 || inString) throw new Error('truncated JSON output');
  return values;
}

function flattenPages(text) {
  return parseJsonStream(text).flatMap((v) => (Array.isArray(v) ? v : [v]));
}

function runGh(args, env = process.env) {
  const { bin, prefix } = splitBin(env.GH_BIN, 'gh');
  return execFileSync(bin, [...prefix, ...args], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...env, GH_PAGER: 'cat' },
    maxBuffer: 64 * 1024 * 1024,
  });
}

// Reads the JSON items array from `--input <file>` or stdin. Throws on invalid input.
function readItems(args, readStdin = () => fs.readFileSync(0, 'utf8')) {
  const text = typeof args.input === 'string' ? fs.readFileSync(args.input, 'utf8') : readStdin();
  let items;
  try {
    items = JSON.parse(text);
  } catch (e) {
    throw new Error(`input is not valid JSON: ${e.message}`);
  }
  if (!Array.isArray(items)) throw new Error('input must be a JSON array of items');
  return items;
}

function requireFields(item, fields) {
  const missing = fields.filter((f) => typeof (item && item[f]) !== 'string' || item[f] === '');
  if (missing.length) throw new Error(`item is missing string field(s): ${missing.join(', ')}`);
}

function parseCommentId(id) {
  const m = /^(issue-comment|review-comment|review-summary)\/(\d+)$/.exec(String(id || ''));
  if (!m) throw new Error(`commentId is not a <kind>/<numeric-id> value: ${id}`);
  return { kind: m[1], numericId: Number(m[2]) };
}

// GitHub only accepts review-comment replies anchored to the thread root.
function findRootId(reviewComments, id) {
  const byId = new Map(reviewComments.map((c) => [c.id, c]));
  let cur = byId.get(id);
  if (!cur) throw new Error(`review comment ${id} not found on this PR`);
  const seen = new Set();
  while (cur.in_reply_to_id && byId.has(cur.in_reply_to_id) && !seen.has(cur.id)) {
    seen.add(cur.id);
    cur = byId.get(cur.in_reply_to_id);
  }
  return cur.in_reply_to_id || cur.id;
}

function findComment(comments, body, rootId) {
  return comments.find((c) => c.body === body && (rootId === undefined || c.in_reply_to_id === rootId)) || null;
}

const THREADS_QUERY =
  'query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$pr){reviewThreads(first:100,after:$endCursor){pageInfo{hasNextPage endCursor}nodes{id isResolved comments(first:100){nodes{databaseId}}}}}}}';

const RESOLVE_MUTATION = 'mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{id isResolved}}}';

function findThread(pages, numericId) {
  const nodes = pages.flatMap((p) => p.data.repository.pullRequest.reviewThreads.nodes);
  return nodes.find((t) => t.comments.nodes.some((c) => c.databaseId === numericId)) || null;
}

function errorMessage(err) {
  return String(err.stderr || err.message).trim();
}

// Runs `handler` for every item; one failing item never stops the batch.
function runBatch(items, handler) {
  return items.map((item, index) => {
    try {
      return { index, ...handler(item) };
    } catch (err) {
      return { index, commentId: item && item.commentId, status: 'error', error: errorMessage(err) };
    }
  });
}

function exitCodeFor(results) {
  return results.some((r) => r.status === 'error') ? 1 : 0;
}

// Shared CLI wrapper: exit 2 on bad input, 1 when any item failed, else 0.
function cliMain(argv, usage, handler, readStdin) {
  let items;
  try {
    items = readItems(parseArgs(argv), readStdin);
  } catch (err) {
    process.stdout.write(`${JSON.stringify({ error: err.message, usage }, null, 2)}\n`);
    return 2;
  }
  const results = runBatch(items, handler);
  process.stdout.write(`${JSON.stringify(results, null, 2)}\n`);
  return exitCodeFor(results);
}

// Posts `body` to a comments endpoint unless identical content exists, then reads it back.
function postIdempotent({ gh, endpoint, body, rootId, commentId }) {
  const list = () => flattenPages(gh(['api', '--paginate', endpoint]));
  const existing = findComment(list(), body, rootId);
  if (existing) return { commentId, status: 'already-present', url: existing.html_url || null };
  const args = ['api', '--method', 'POST', endpoint, '-f', `body=${body}`];
  if (rootId !== undefined) args.push('-F', `in_reply_to=${rootId}`);
  gh(args);
  const posted = findComment(list(), body, rootId);
  if (!posted) return { commentId, status: 'error', error: 'write exited 0 but the comment is missing on read-back' };
  return { commentId, status: 'verified', url: posted.html_url || null };
}

function replyHandler(item, gh = runGh) {
  requireFields(item, ['prUrl', 'commentId', 'body']);
  const { owner, repo, pr } = parsePrUrl(item.prUrl);
  const { kind, numericId } = parseCommentId(item.commentId);
  if (kind !== 'review-comment') {
    // Issue comments and review summaries have no threads; a reply is a new PR comment.
    return postIdempotent({ gh, endpoint: `repos/${owner}/${repo}/issues/${pr}/comments`, body: item.body, commentId: item.commentId });
  }
  const endpoint = `repos/${owner}/${repo}/pulls/${pr}/comments`;
  const rootId = findRootId(flattenPages(gh(['api', '--paginate', endpoint])), numericId);
  return postIdempotent({ gh, endpoint, body: item.body, rootId, commentId: item.commentId });
}

function createHandler(item, gh = runGh) {
  requireFields(item, ['prUrl', 'body']);
  const { owner, repo, pr } = parsePrUrl(item.prUrl);
  return postIdempotent({ gh, endpoint: `repos/${owner}/${repo}/issues/${pr}/comments`, body: item.body });
}

function resolveHandler(item, gh = runGh) {
  requireFields(item, ['prUrl', 'commentId']);
  const { owner, repo, pr } = parsePrUrl(item.prUrl);
  const { kind, numericId } = parseCommentId(item.commentId);
  if (kind !== 'review-comment') throw new Error(`only review-comment threads can be resolved, got ${kind}`);
  const lookup = () =>
    findThread(
      parseJsonStream(gh(['api', 'graphql', '--paginate', '-f', `query=${THREADS_QUERY}`, '-f', `owner=${owner}`, '-f', `repo=${repo}`, '-F', `pr=${pr}`])),
      numericId,
    );
  const thread = lookup();
  if (!thread) throw new Error(`no review thread contains comment ${numericId}`);
  if (thread.isResolved) return { commentId: item.commentId, status: 'already-present' };
  gh(['api', 'graphql', '-f', `query=${RESOLVE_MUTATION}`, '-f', `id=${thread.id}`]);
  const after = lookup();
  if (!after || !after.isResolved) return { commentId: item.commentId, status: 'error', error: 'mutation exited 0 but the thread is still unresolved on read-back' };
  return { commentId: item.commentId, status: 'verified' };
}

module.exports = {
  postIdempotent,
  replyHandler,
  createHandler,
  resolveHandler,
  parsePrUrl,
  parseArgs,
  splitBin,
  parseJsonStream,
  flattenPages,
  runGh,
  readItems,
  requireFields,
  parseCommentId,
  findRootId,
  findComment,
  THREADS_QUERY,
  RESOLVE_MUTATION,
  findThread,
  runBatch,
  exitCodeFor,
  cliMain,
};
