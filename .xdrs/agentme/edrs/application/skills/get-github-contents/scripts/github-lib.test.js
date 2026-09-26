#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const lib = require('./github-lib');

test('parsePrUrl extracts owner, repo, number', () => {
  assert.deepStrictEqual(lib.parsePrUrl('https://github.com/acme/widgets/pull/482'), { owner: 'acme', repo: 'widgets', pr: 482 });
  assert.deepStrictEqual(lib.parsePrUrl('https://github.com/acme/widgets/pull/482/files?x=1').pr, 482);
});

test('parsePrUrl rejects non-GitHub URLs', () => {
  assert.throws(() => lib.parsePrUrl('https://gitlab.com/a/b/pull/1'), /unrecognized/);
  assert.throws(() => lib.parsePrUrl(undefined), /unrecognized/);
});

test('parseArgs reads values and flags', () => {
  assert.deepStrictEqual(lib.parseArgs(['--pr-url', 'u', '--dry-run']), { 'pr-url': 'u', 'dry-run': true });
  assert.throws(() => lib.parseArgs(['stray']), /unexpected argument/);
});

test('splitBin keeps prefix args and falls back to default', () => {
  assert.deepStrictEqual(lib.splitBin('node stub.js', 'gh'), { bin: 'node', prefix: ['stub.js'] });
  assert.deepStrictEqual(lib.splitBin(undefined, 'gh'), { bin: 'gh', prefix: [] });
});

test('parseJsonStream parses concatenated pages including brackets in strings', () => {
  const text = '[{"body":"a ] tricky \\" [ one"}]\n[{"body":"b"}]';
  assert.deepStrictEqual(lib.flattenPages(text), [{ body: 'a ] tricky " [ one' }, { body: 'b' }]);
  assert.deepStrictEqual(lib.flattenPages('{"a":1}'), [{ a: 1 }]);
  assert.throws(() => lib.parseJsonStream('[{"a":1}'), /truncated/);
});

test('runGh invokes the configured binary with GH_PAGER=cat', () => {
  const out = lib.runGh(['-e', 'process.stdout.write(process.env.GH_PAGER)'], { ...process.env, GH_BIN: process.execPath });
  assert.strictEqual(out, 'cat');
});

test('threadsFromGraphql merges paginated pages', () => {
  const page = (id) => ({ data: { repository: { pullRequest: { reviewThreads: { nodes: [{ id }] } } } } });
  assert.deepStrictEqual(lib.threadsFromGraphql([page('T1'), page('T2')]), [{ id: 'T1' }, { id: 'T2' }]);
});

test('normalizeComments maps every kind to the shared record shape', () => {
  const records = lib.normalizeComments({
    issueComments: [{ id: 1, body: 'general', user: { login: 'ann' }, html_url: 'u1' }],
    reviewComments: [
      { id: 10, body: 'root', user: { login: 'bob' }, path: 'a.js', line: 3, diff_hunk: '@@', html_url: 'u10' },
      { id: 11, body: 'reply', user: null, path: 'a.js', original_line: 3, in_reply_to_id: 10 },
      { id: 12, body: 'reply-to-reply', in_reply_to_id: 11 },
      { id: 13, in_reply_to_id: 99 },
    ],
    reviews: [
      { id: 20, body: 'summary', user: { login: 'cy' }, html_url: 'u20' },
      { id: 21, body: '' },
    ],
    threads: [{ id: 'T1', isResolved: true, comments: { nodes: [{ databaseId: 10 }, { databaseId: 11 }, { databaseId: 12 }] } }],
  });
  const byId = Object.fromEntries(records.map((r) => [r.id, r]));
  assert.strictEqual(records.length, 6);
  assert.deepStrictEqual(byId['issue-comment/1'], {
    id: 'issue-comment/1',
    kind: 'issue-comment',
    status: 'open',
    can_reply: true,
    can_resolve: false,
    path: null,
    line: null,
    content: 'general',
    author: 'ann',
    in_reply_to: null,
    diff_hunk: null,
    url: 'u1',
  });
  assert.strictEqual(byId['review-comment/10'].status, 'resolved');
  assert.strictEqual(byId['review-comment/10'].can_resolve, true);
  assert.strictEqual(byId['review-comment/10'].in_reply_to, null);
  assert.strictEqual(byId['review-comment/11'].in_reply_to, 10);
  assert.strictEqual(byId['review-comment/11'].author, null);
  assert.strictEqual(byId['review-comment/11'].line, 3);
  assert.strictEqual(byId['review-comment/12'].in_reply_to, 10);
  assert.strictEqual(byId['review-comment/13'].in_reply_to, 99);
  assert.strictEqual(byId['review-comment/13'].status, 'open');
  assert.strictEqual(byId['review-comment/13'].can_resolve, false);
  assert.strictEqual(byId['review-summary/20'].can_resolve, false);
  assert.strictEqual(byId['review-summary/21'], undefined);
});

test('normalizeComments accepts empty input', () => {
  assert.deepStrictEqual(lib.normalizeComments({}), []);
});
