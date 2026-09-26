#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const lib = require('./azure-devops-lib');

const PR = 'https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/9';
const BASE = 'https://dev.azure.com/contoso/Widgets/_apis/git/repositories/widgets-api/pullRequests/9';

// In-memory stand-in for the az runner, injected into handlers.
function fakeAz({ threads = [], dropWrites = false } = {}) {
  const calls = [];
  const az = (args) => {
    calls.push(args);
    const method = args[args.indexOf('--method') + 1];
    const uri = args[args.indexOf('--uri') + 1].replace(/\?api-version=7\.1$/, '').slice(BASE.length);
    const bodyArg = args.indexOf('--body');
    const body = bodyArg >= 0 ? JSON.parse(fs.readFileSync(args[bodyArg + 1].slice(1), 'utf8')) : undefined;
    const threadMatch = /^\/threads\/(\d+)(\/comments)?$/.exec(uri);
    const thread = threadMatch && threads.find((t) => t.id === Number(threadMatch[1]));
    if (method === 'GET' && uri === '/threads') return JSON.stringify({ value: threads });
    if (method === 'GET' && thread) return JSON.stringify(thread);
    if (method === 'POST' && uri === '/threads') {
      if (!dropWrites) threads.push({ id: 100 + threads.length, threadContext: null, ...body });
      return '{}';
    }
    if (method === 'POST' && threadMatch[2]) {
      if (!dropWrites) thread.comments.push({ id: thread.comments.length + 1, ...body });
      return '{}';
    }
    if (method === 'PATCH' && thread) {
      if (!dropWrites) thread.status = body.status;
      return '';
    }
    throw new Error(`unexpected az call: ${args.join(' ')}`);
  };
  az.calls = calls;
  return az;
}

test('parsePrUrl accepts modern and legacy URLs', () => {
  assert.strictEqual(lib.parsePrUrl(PR).apiBase, BASE);
  assert.strictEqual(lib.parsePrUrl('https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/9').apiBase, BASE);
  assert.throws(() => lib.parsePrUrl('https://github.com/a/b/pull/1'), /unrecognized/);
  assert.throws(() => lib.parsePrUrl(undefined), /unrecognized/);
});

test('parseArgs, splitBin and runAz', () => {
  assert.deepStrictEqual(lib.parseArgs(['--input', 'f', '--x']), { input: 'f', x: true });
  assert.throws(() => lib.parseArgs(['y']), /unexpected/);
  assert.deepStrictEqual(lib.splitBin('node a.js', 'az'), { bin: 'node', prefix: ['a.js'] });
  assert.deepStrictEqual(lib.splitBin('', 'az'), { bin: 'az', prefix: [] });
  assert.strictEqual(lib.runAz(['-e', 'process.stdout.write("ok")'], { ...process.env, AZ_BIN: process.execPath }), 'ok');
});

test('rest passes resource, api-version and body file, then removes it', () => {
  let seen;
  let bodyFile;
  const az = (args) => {
    seen = args;
    const i = args.indexOf('--body');
    if (i >= 0) {
      bodyFile = args[i + 1].slice(1);
      assert.deepStrictEqual(JSON.parse(fs.readFileSync(bodyFile, 'utf8')), { a: "it's \"quoted\"" });
    }
    return '';
  };
  assert.strictEqual(lib.rest(az, 'PATCH', 'https://x', { a: "it's \"quoted\"" }), null);
  assert.deepStrictEqual(seen.slice(0, 3), ['rest', '--resource', lib.ADO_RESOURCE]);
  assert.strictEqual(seen[6], 'https://x?api-version=7.1');
  assert.strictEqual(fs.existsSync(bodyFile), false);
  assert.strictEqual(lib.rest(() => '{"k":1}', 'GET', 'https://x').k, 1);
});

test('readItems reads --input file or stdin and validates', () => {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'cado-')), 'items.json');
  fs.writeFileSync(file, '[1]');
  assert.deepStrictEqual(lib.readItems({ input: file }), [1]);
  assert.throws(() => lib.readItems({}, () => 'x'), /not valid JSON/);
  assert.throws(() => lib.readItems({}, () => '{}'), /JSON array/);
});

test('requireFields and parseCommentId validate items', () => {
  assert.throws(() => lib.requireFields({ prUrl: PR, body: '' }, ['prUrl', 'body']), /body/);
  assert.throws(() => lib.requireFields(undefined, ['prUrl']), /prUrl/);
  assert.deepStrictEqual(lib.parseCommentId('thread-comment/12.3'), { threadId: 12, commentId: 3 });
  assert.throws(() => lib.parseCommentId('review-comment/3'), /thread-comment/);
});

test('replyHandler posts, verifies and is idempotent', () => {
  const threads = [{ id: 12, comments: [{ id: 1, content: 'root' }, { id: 2, content: 'Done', isDeleted: true }] }];
  const az = fakeAz({ threads });
  const item = { prUrl: PR, commentId: 'thread-comment/12.1', body: 'Done' };
  assert.deepStrictEqual(lib.replyHandler(item, az), { commentId: item.commentId, status: 'verified', url: `${PR}?discussionId=12` });
  assert.strictEqual(threads[0].comments.at(-1).parentCommentId, 1);
  assert.strictEqual(lib.replyHandler(item, az).status, 'already-present');
});

test('replyHandler reports error when read-back misses the write', () => {
  const az = fakeAz({ dropWrites: true, threads: [{ id: 12 }] });
  assert.strictEqual(lib.replyHandler({ prUrl: PR, commentId: 'thread-comment/12.1', body: 'x' }, az).status, 'error');
});

test('createHandler creates a general thread once', () => {
  const threads = [
    { id: 1, threadContext: { filePath: '/a' }, comments: [{ content: 'hi' }] },
    { id: 2, isDeleted: true, comments: [{ content: 'hi' }] },
    { id: 3, comments: [] },
  ];
  const az = fakeAz({ threads });
  const first = lib.createHandler({ prUrl: PR, body: 'hi' }, az);
  assert.strictEqual(first.status, 'verified');
  assert.strictEqual(threads.at(-1).status, 'active');
  assert.strictEqual(lib.createHandler({ prUrl: PR, body: 'hi' }, az).url, first.url);
  assert.strictEqual(lib.createHandler({ prUrl: PR, body: 'new' }, fakeAz({ dropWrites: true })).status, 'error');
});

test('statusSetHandler sets, skips and verifies status', () => {
  const threads = [{ id: 5, status: 'active', comments: [] }];
  const az = fakeAz({ threads });
  const item = { prUrl: PR, commentId: 'thread-comment/5.1', status: 'fixed' };
  assert.strictEqual(lib.statusSetHandler(item, az).status, 'verified');
  assert.strictEqual(lib.statusSetHandler(item, az).status, 'already-present');
  assert.throws(() => lib.statusSetHandler({ ...item, status: 'done' }, az), /status must be one of/);
  const dropped = fakeAz({ dropWrites: true, threads: [{ id: 5, status: 'active' }] });
  assert.strictEqual(lib.statusSetHandler(item, dropped).status, 'error');
});

test('runBatch isolates failures and cliMain maps exit codes', (t) => {
  const failing = () => {
    const err = new Error('x');
    err.stderr = 'HTTP 403 Forbidden\n';
    throw err;
  };
  const results = lib.runBatch([{ commentId: 'thread-comment/1.1' }, null], failing);
  assert.deepStrictEqual(results[0], { index: 0, commentId: 'thread-comment/1.1', status: 'error', error: 'HTTP 403 Forbidden' });
  assert.strictEqual(results[1].commentId, null);
  assert.strictEqual(lib.exitCodeFor(results), 1);
  const writes = [];
  t.mock.method(process.stdout, 'write', (s) => writes.push(s));
  assert.strictEqual(lib.cliMain([], 'u', () => ({}), () => '{'), 2);
  assert.strictEqual(lib.cliMain([], 'u', () => ({ status: 'verified' }), () => '[{}]'), 0);
  t.mock.restoreAll();
  assert.match(writes[0], /not valid JSON/);
});
