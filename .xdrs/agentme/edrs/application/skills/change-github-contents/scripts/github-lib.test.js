#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const lib = require('./github-lib');

const PR = 'https://github.com/acme/widgets/pull/7';

// In-memory stand-in for the gh runner, injected into handlers.
function fakeGh({ issue = [], review = [], threads = [], dropWrites = false, failPost = false } = {}) {
  const calls = [];
  const gh = (args) => {
    calls.push(args);
    const [, second, third, fourth] = args;
    if (args[1] === 'graphql') {
      const query = args.find((a) => a.startsWith('query='));
      if (query.includes('resolveReviewThread')) {
        const id = args.find((a) => a.startsWith('id=')).slice(3);
        if (!dropWrites) threads.find((t) => t.id === id).isResolved = true;
        return '{}';
      }
      const half = Math.ceil(threads.length / 2);
      const page = (nodes) => JSON.stringify({ data: { repository: { pullRequest: { reviewThreads: { nodes } } } } });
      return page(threads.slice(0, half)) + page(threads.slice(half));
    }
    const store = (args.find((a) => a.startsWith('repos/')) || '').includes('/pulls/') ? review : issue;
    if (second === '--paginate') return JSON.stringify(store);
    if (second === '--method' && third === 'POST') {
      if (failPost) {
        const err = new Error('boom');
        err.stderr = 'HTTP 403: Resource not accessible\n';
        throw err;
      }
      const body = args.find((a) => a.startsWith('body=')).slice(5);
      const replyTo = args.find((a) => a.startsWith('in_reply_to='));
      if (!dropWrites) {
        store.push({ id: 1000 + store.length, body, in_reply_to_id: replyTo ? Number(replyTo.slice(12)) : undefined, html_url: `u-${fourth}` });
      }
      return '{}';
    }
    throw new Error(`unexpected gh call: ${args.join(' ')}`);
  };
  gh.calls = calls;
  return gh;
}

test('parsePrUrl, parseArgs and splitBin', () => {
  assert.deepStrictEqual(lib.parsePrUrl(PR), { owner: 'acme', repo: 'widgets', pr: 7 });
  assert.throws(() => lib.parsePrUrl('https://example.com/x'), /unrecognized/);
  assert.deepStrictEqual(lib.parseArgs(['--input', 'f', '--x']), { input: 'f', x: true });
  assert.throws(() => lib.parseArgs(['bad']), /unexpected/);
  assert.deepStrictEqual(lib.splitBin('node a.js', 'gh'), { bin: 'node', prefix: ['a.js'] });
  assert.deepStrictEqual(lib.splitBin('', 'gh'), { bin: 'gh', prefix: [] });
});

test('parseJsonStream handles pages, strings and truncation', () => {
  assert.deepStrictEqual(lib.flattenPages('[{"b":"x]\\"["}][{"b":"y"}]{"c":1}'), [{ b: 'x]"[' }, { b: 'y' }, { c: 1 }]);
  assert.throws(() => lib.parseJsonStream('["a'), /truncated/);
});

test('runGh forces GH_PAGER=cat', () => {
  assert.strictEqual(lib.runGh(['-e', 'process.stdout.write(process.env.GH_PAGER)'], { ...process.env, GH_BIN: process.execPath }), 'cat');
});

test('readItems reads --input file or stdin and validates', () => {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'cgc-')), 'items.json');
  fs.writeFileSync(file, '[{"a":1}]');
  assert.deepStrictEqual(lib.readItems({ input: file }), [{ a: 1 }]);
  assert.deepStrictEqual(lib.readItems({}, () => '[]'), []);
  assert.throws(() => lib.readItems({}, () => '{'), /not valid JSON/);
  assert.throws(() => lib.readItems({}, () => '{}'), /JSON array/);
});

test('requireFields and parseCommentId validate items', () => {
  assert.throws(() => lib.requireFields({ prUrl: PR }, ['prUrl', 'body']), /body/);
  assert.throws(() => lib.requireFields(null, ['prUrl']), /prUrl/);
  assert.deepStrictEqual(lib.parseCommentId('review-comment/5'), { kind: 'review-comment', numericId: 5 });
  assert.throws(() => lib.parseCommentId('thread-comment/1.2'), /kind/);
});

test('findRootId walks reply chains to the thread root', () => {
  const comments = [{ id: 1 }, { id: 2, in_reply_to_id: 1 }, { id: 3, in_reply_to_id: 2 }, { id: 4, in_reply_to_id: 99 }];
  assert.strictEqual(lib.findRootId(comments, 3), 1);
  assert.strictEqual(lib.findRootId(comments, 1), 1);
  assert.strictEqual(lib.findRootId(comments, 4), 99);
  assert.throws(() => lib.findRootId(comments, 5), /not found/);
});

test('replyHandler posts a review reply to the root and verifies it', () => {
  const review = [{ id: 1 }, { id: 2, in_reply_to_id: 1 }];
  const gh = fakeGh({ review });
  const result = lib.replyHandler({ prUrl: PR, commentId: 'review-comment/2', body: 'Done' }, gh);
  assert.strictEqual(result.status, 'verified');
  assert.ok(gh.calls.some((c) => c.includes('in_reply_to=1')));
  assert.strictEqual(review.at(-1).in_reply_to_id, 1);
});

test('replyHandler skips identical existing reply', () => {
  const gh = fakeGh({ review: [{ id: 1 }, { id: 2, in_reply_to_id: 1, body: 'Done', html_url: 'u2' }] });
  assert.deepStrictEqual(lib.replyHandler({ prUrl: PR, commentId: 'review-comment/1', body: 'Done' }, gh), {
    commentId: 'review-comment/1',
    status: 'already-present',
    url: 'u2',
  });
  assert.ok(!gh.calls.some((c) => c.includes('POST')));
});

test('replyHandler routes issue comments and review summaries to issue comments', () => {
  const issue = [];
  const gh = fakeGh({ issue });
  assert.strictEqual(lib.replyHandler({ prUrl: PR, commentId: 'review-summary/9', body: 'Thanks' }, gh).status, 'verified');
  assert.strictEqual(issue.length, 1);
});

test('postIdempotent reports error when read-back misses the write', () => {
  const gh = fakeGh({ dropWrites: true });
  const result = lib.createHandler({ prUrl: PR, body: 'hello' }, gh);
  assert.strictEqual(result.status, 'error');
  assert.match(result.error, /read-back/);
});

test('resolveHandler resolves, skips resolved and rejects non-review kinds', () => {
  const threads = [
    { id: 'T0', isResolved: false, comments: { nodes: [{ databaseId: 1 }] } },
    { id: 'T1', isResolved: false, comments: { nodes: [{ databaseId: 5 }, { databaseId: 6 }] } },
  ];
  const gh = fakeGh({ threads });
  assert.strictEqual(lib.resolveHandler({ prUrl: PR, commentId: 'review-comment/6' }, gh).status, 'verified');
  assert.strictEqual(threads[1].isResolved, true);
  assert.strictEqual(lib.resolveHandler({ prUrl: PR, commentId: 'review-comment/5' }, gh).status, 'already-present');
  assert.throws(() => lib.resolveHandler({ prUrl: PR, commentId: 'issue-comment/5' }, gh), /only review-comment/);
  assert.throws(() => lib.resolveHandler({ prUrl: PR, commentId: 'review-comment/77' }, gh), /no review thread/);
});

test('resolveHandler reports error when thread stays unresolved', () => {
  const gh = fakeGh({ dropWrites: true, threads: [{ id: 'T', isResolved: false, comments: { nodes: [{ databaseId: 3 }] } }] });
  assert.strictEqual(lib.resolveHandler({ prUrl: PR, commentId: 'review-comment/3' }, gh).status, 'error');
});

test('runBatch isolates failures and exitCodeFor reflects them', () => {
  const gh = fakeGh({ failPost: true });
  const results = lib.runBatch([{ prUrl: PR, commentId: 'issue-comment/1', body: 'x' }, { prUrl: PR, body: 'y' }], (i) => lib.replyHandler(i, gh));
  assert.strictEqual(results[0].status, 'error');
  assert.strictEqual(results[0].error, 'HTTP 403: Resource not accessible');
  assert.strictEqual(results[1].index, 1);
  assert.strictEqual(lib.exitCodeFor(results), 1);
  assert.strictEqual(lib.exitCodeFor([{ status: 'verified' }]), 0);
});

test('cliMain returns 2 on invalid input and 0 on empty batch', (t) => {
  const writes = [];
  t.mock.method(process.stdout, 'write', (s) => writes.push(s));
  assert.strictEqual(lib.cliMain([], 'usage', () => ({}), () => 'nope'), 2);
  assert.strictEqual(lib.cliMain([], 'usage', () => ({}), () => '[]'), 0);
  assert.strictEqual(lib.cliMain([], 'usage', () => ({ status: 'verified' }), () => '[{}]'), 0);
  t.mock.restoreAll();
  assert.match(writes[0], /not valid JSON/);
  assert.strictEqual(writes[1].trim(), '[]');
});
