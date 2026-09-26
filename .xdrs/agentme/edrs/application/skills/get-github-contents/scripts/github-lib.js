#!/usr/bin/env node
'use strict';

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

// `gh api --paginate` prints one JSON array per page back to back (e.g. `[..][..]`).
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

const THREADS_QUERY =
  'query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$pr){reviewThreads(first:100,after:$endCursor){pageInfo{hasNextPage endCursor}nodes{id isResolved comments(first:100){nodes{databaseId}}}}}}}';

function threadsFromGraphql(pages) {
  return pages.flatMap((p) => p.data.repository.pullRequest.reviewThreads.nodes);
}

function rootId(comment, byId) {
  let cur = comment;
  const seen = new Set();
  while (cur && cur.in_reply_to_id && byId.has(cur.in_reply_to_id) && !seen.has(cur.id)) {
    seen.add(cur.id);
    cur = byId.get(cur.in_reply_to_id);
  }
  return cur && cur.in_reply_to_id ? cur.in_reply_to_id : cur.id;
}

function login(user) {
  return (user && user.login) || null;
}

function normalizeComments({ issueComments = [], reviewComments = [], reviews = [], threads = [] }) {
  const resolvedIds = new Set();
  const threadIds = new Set();
  for (const t of threads) {
    for (const c of t.comments.nodes) {
      threadIds.add(c.databaseId);
      if (t.isResolved) resolvedIds.add(c.databaseId);
    }
  }
  const byId = new Map(reviewComments.map((c) => [c.id, c]));
  const records = [];
  for (const c of issueComments) {
    records.push({
      id: `issue-comment/${c.id}`,
      kind: 'issue-comment',
      status: 'open',
      can_reply: true,
      can_resolve: false,
      path: null,
      line: null,
      content: c.body || '',
      author: login(c.user),
      in_reply_to: null,
      diff_hunk: null,
      url: c.html_url || null,
    });
  }
  for (const c of reviewComments) {
    const root = rootId(c, byId);
    records.push({
      id: `review-comment/${c.id}`,
      kind: 'review-comment',
      status: resolvedIds.has(c.id) ? 'resolved' : 'open',
      can_reply: true,
      can_resolve: threadIds.has(c.id),
      path: c.path || null,
      line: c.line || c.original_line || null,
      content: c.body || '',
      author: login(c.user),
      in_reply_to: root === c.id ? null : root,
      diff_hunk: c.diff_hunk || null,
      url: c.html_url || null,
    });
  }
  for (const r of reviews) {
    if (!r.body) continue;
    records.push({
      id: `review-summary/${r.id}`,
      kind: 'review-summary',
      status: 'open',
      can_reply: true,
      can_resolve: false,
      path: null,
      line: null,
      content: r.body,
      author: login(r.user),
      in_reply_to: null,
      diff_hunk: null,
      url: r.html_url || null,
    });
  }
  return records;
}

module.exports = {
  parsePrUrl,
  parseArgs,
  splitBin,
  parseJsonStream,
  flattenPages,
  runGh,
  THREADS_QUERY,
  threadsFromGraphql,
  normalizeComments,
};
