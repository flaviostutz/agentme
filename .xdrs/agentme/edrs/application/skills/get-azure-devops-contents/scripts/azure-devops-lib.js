#!/usr/bin/env node
'use strict';

const { execFileSync } = require('child_process');

// Azure DevOps' well-known, tenant-agnostic AAD resource id; always passed to `az rest`.
const ADO_RESOURCE = '499b84ac-1321-427f-aa17-267ca6975798';
const API_VERSION = '7.1';

function parsePrUrl(url) {
  const s = String(url || '');
  const m =
    /^https:\/\/dev\.azure\.com\/([^/\s]+)\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i.exec(s) ||
    /^https:\/\/([^./\s]+)\.visualstudio\.com\/([^/\s]+)\/_git\/([^/\s]+)\/pullrequest\/(\d+)(?:[/?#].*)?$/i.exec(s);
  if (!m) throw new Error(`unrecognized Azure DevOps PR URL: ${url}`);
  const [, org, project, repo, pr] = m;
  const orgUrl = `https://dev.azure.com/${org}`;
  return {
    org,
    project,
    repo,
    pr: Number(pr),
    orgUrl,
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

function restGet(az, uri) {
  const sep = uri.includes('?') ? '&' : '?';
  return JSON.parse(az(['rest', '--resource', ADO_RESOURCE, '--method', 'GET', '--uri', `${uri}${sep}api-version=${API_VERSION}`]));
}

const STATUS_MAP = { active: 'open', pending: 'open', fixed: 'resolved', closed: 'resolved', wontFix: 'wontfix', byDesign: 'wontfix' };

function isHumanComment(c) {
  return !c.isDeleted && c.commentType !== 'system';
}

function normalizeThreads(threads, webUrl) {
  const records = [];
  for (const t of threads) {
    if (t.isDeleted) continue;
    const comments = (t.comments || []).filter(isHumanComment);
    if (!comments.length) continue;
    const ctx = t.threadContext || null;
    const start = ctx && (ctx.rightFileStart || ctx.leftFileStart);
    const rootId = comments[0].id;
    for (const c of comments) {
      records.push({
        id: `thread-comment/${t.id}.${c.id}`,
        kind: 'thread-comment',
        status: STATUS_MAP[t.status] || 'open',
        can_reply: true,
        can_resolve: true,
        path: (ctx && ctx.filePath) || null,
        line: (start && start.line) || null,
        content: c.content || '',
        author: (c.author && c.author.displayName) || null,
        in_reply_to: c.id === rootId ? null : rootId,
        diff_hunk: null,
        url: `${webUrl}?discussionId=${t.id}`,
      });
    }
  }
  return records;
}

function pickPrMetadata(pr, webUrl) {
  const branch = (ref) => (ref ? ref.replace(/^refs\/heads\//, '') : null);
  return {
    number: pr.pullRequestId,
    title: pr.title,
    body: pr.description || '',
    state: pr.status,
    isDraft: Boolean(pr.isDraft),
    url: webUrl,
    baseRefName: branch(pr.targetRefName),
    headRefName: branch(pr.sourceRefName),
    repository: (pr.repository && pr.repository.name) || null,
    author: (pr.createdBy && pr.createdBy.displayName) || null,
  };
}

module.exports = { ADO_RESOURCE, API_VERSION, parsePrUrl, parseArgs, splitBin, runAz, restGet, STATUS_MAP, normalizeThreads, pickPrMetadata };
