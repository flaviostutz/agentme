#!/usr/bin/env node
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

// Azure DevOps' well-known, tenant-agnostic AAD resource id; always passed to `az rest`.
const ADO_RESOURCE = '499b84ac-1321-427f-aa17-267ca6975798';
const API_VERSION = '7.1';
const THREAD_STATUSES = ['active', 'pending', 'fixed', 'wontFix', 'closed', 'byDesign'];

function parsePrUrl(url) {
  const s = String(url || '');
  const m =
    /^https:\/\/dev\.azure\.com\/([^/\s]+)\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i.exec(s) ||
    /^https:\/\/([^./\s]+)\.visualstudio\.com\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i.exec(s);
  if (!m) throw new Error(`unrecognized Azure DevOps PR URL: ${url}`);
  const [, org, project, repo, pr] = m;
  const orgUrl = `https://dev.azure.com/${org}`;
  return {
    apiBase: `${orgUrl}/${project}/_apis/git/repositories/${repo}/pullRequests/${pr}`,
    webUrl: `${orgUrl}/${project}/_git/${repo}/pullrequest/${pr}`,
  };
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

function runAz(args, env = process.env) {
  const { bin, prefix } = splitBin(env.AZ_BIN, 'az');
  return execFileSync(bin, [...prefix, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env, maxBuffer: 64 * 1024 * 1024 });
}

// Calls `az rest`; a JSON body goes through a temp file so no text passes through a shell.
function rest(az, method, uri, body) {
  const args = ['rest', '--resource', ADO_RESOURCE, '--method', method, '--uri', `${uri}?api-version=${API_VERSION}`];
  if (body === undefined) return JSON.parse(az(args) || 'null');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'change-ado-'));
  try {
    const file = path.join(dir, 'body.json');
    fs.writeFileSync(file, JSON.stringify(body));
    return JSON.parse(az([...args, '--body', `@${file}`]) || 'null');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
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
  const m = /^thread-comment\/(\d+)\.(\d+)$/.exec(String(id || ''));
  if (!m) throw new Error(`commentId is not a thread-comment/<threadId>.<commentId> value: ${id}`);
  return { threadId: Number(m[1]), commentId: Number(m[2]) };
}

function hasContent(thread, body) {
  return ((thread && thread.comments) || []).some((c) => !c.isDeleted && c.content === body);
}

function replyHandler(item, az = runAz) {
  requireFields(item, ['prUrl', 'commentId', 'body']);
  const { apiBase, webUrl } = parsePrUrl(item.prUrl);
  const { threadId, commentId } = parseCommentId(item.commentId);
  const threadUri = `${apiBase}/threads/${threadId}`;
  const url = `${webUrl}?discussionId=${threadId}`;
  if (hasContent(rest(az, 'GET', threadUri), item.body)) return { commentId: item.commentId, status: 'already-present', url };
  rest(az, 'POST', `${threadUri}/comments`, { content: item.body, parentCommentId: commentId, commentType: 1 });
  // A zero exit from `az rest` is not proof the write persisted; always read back.
  if (!hasContent(rest(az, 'GET', threadUri), item.body)) {
    return { commentId: item.commentId, status: 'error', error: 'write exited 0 but the reply is missing on read-back' };
  }
  return { commentId: item.commentId, status: 'verified', url };
}

function findGeneralThread(threads, body) {
  return threads.find((t) => !t.isDeleted && !t.threadContext && t.comments && t.comments[0] && t.comments[0].content === body) || null;
}

function createHandler(item, az = runAz) {
  requireFields(item, ['prUrl', 'body']);
  const { apiBase, webUrl } = parsePrUrl(item.prUrl);
  const list = () => rest(az, 'GET', `${apiBase}/threads`).value || [];
  const existing = findGeneralThread(list(), item.body);
  if (existing) return { status: 'already-present', url: `${webUrl}?discussionId=${existing.id}` };
  rest(az, 'POST', `${apiBase}/threads`, { comments: [{ parentCommentId: 0, content: item.body, commentType: 1 }], status: 'active' });
  const created = findGeneralThread(list(), item.body);
  if (!created) return { status: 'error', error: 'write exited 0 but the thread is missing on read-back' };
  return { status: 'verified', url: `${webUrl}?discussionId=${created.id}` };
}

function statusSetHandler(item, az = runAz) {
  requireFields(item, ['prUrl', 'commentId', 'status']);
  if (!THREAD_STATUSES.includes(item.status)) throw new Error(`status must be one of ${THREAD_STATUSES.join(', ')}`);
  const { apiBase } = parsePrUrl(item.prUrl);
  const { threadId } = parseCommentId(item.commentId);
  const threadUri = `${apiBase}/threads/${threadId}`;
  if (rest(az, 'GET', threadUri).status === item.status) return { commentId: item.commentId, status: 'already-present' };
  rest(az, 'PATCH', threadUri, { status: item.status });
  if (rest(az, 'GET', threadUri).status !== item.status) {
    return { commentId: item.commentId, status: 'error', error: `write exited 0 but the thread status is not "${item.status}" on read-back` };
  }
  return { commentId: item.commentId, status: 'verified' };
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

module.exports = {
  ADO_RESOURCE,
  THREAD_STATUSES,
  parsePrUrl,
  parseArgs,
  splitBin,
  runAz,
  rest,
  readItems,
  requireFields,
  parseCommentId,
  replyHandler,
  createHandler,
  statusSetHandler,
  runBatch,
  exitCodeFor,
  cliMain,
};
