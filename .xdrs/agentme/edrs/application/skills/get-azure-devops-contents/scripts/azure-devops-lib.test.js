#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const lib = require('./azure-devops-lib');

test('parsePrUrl accepts modern and legacy URLs', () => {
  const modern = lib.parsePrUrl('https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029');
  assert.strictEqual(modern.apiBase, 'https://dev.azure.com/contoso/Widgets/_apis/git/repositories/widgets-api/pullRequests/1029');
  assert.strictEqual(modern.webUrl, 'https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029');
  const legacy = lib.parsePrUrl('https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/7?_a=files');
  assert.deepStrictEqual([legacy.org, legacy.project, legacy.repo, legacy.pr, legacy.orgUrl], ['contoso', 'Widgets', 'widgets-api', 7, 'https://dev.azure.com/contoso']);
  assert.throws(() => lib.parsePrUrl('https://github.com/a/b/pull/1'), /unrecognized/);
  assert.throws(() => lib.parsePrUrl(null), /unrecognized/);
});

test('parseArgs and splitBin', () => {
  assert.deepStrictEqual(lib.parseArgs(['--pr-url', 'u', '--flag']), { 'pr-url': 'u', flag: true });
  assert.throws(() => lib.parseArgs(['x']), /unexpected/);
  assert.deepStrictEqual(lib.splitBin('node stub.js', 'az'), { bin: 'node', prefix: ['stub.js'] });
  assert.deepStrictEqual(lib.splitBin(undefined, 'az'), { bin: 'az', prefix: [] });
});

test('runAz invokes the configured binary', () => {
  assert.strictEqual(lib.runAz(['-e', 'process.stdout.write("ok")'], { ...process.env, AZ_BIN: process.execPath }), 'ok');
});

test('restGet always passes the ADO resource and api-version', () => {
  let seen;
  const az = (args) => {
    seen = args;
    return '{"value":[]}';
  };
  assert.deepStrictEqual(lib.restGet(az, 'https://x/threads'), { value: [] });
  assert.deepStrictEqual(seen.slice(0, 5), ['rest', '--resource', lib.ADO_RESOURCE, '--method', 'GET']);
  assert.strictEqual(seen.at(-1), 'https://x/threads?api-version=7.1');
  lib.restGet(az, 'https://x/threads?top=1');
  assert.strictEqual(seen.at(-1), 'https://x/threads?top=1&api-version=7.1');
});

test('normalizeThreads maps threads to the shared record shape', () => {
  const records = lib.normalizeThreads(
    [
      {
        id: 12,
        status: 'fixed',
        threadContext: { filePath: '/src/a.ts', rightFileStart: { line: 4 } },
        comments: [
          { id: 1, content: 'root', author: { displayName: 'Ann' } },
          { id: 2, content: 'reply', parentCommentId: 1, author: null },
          { id: 3, content: 'gone', isDeleted: true },
        ],
      },
      { id: 13, status: 'active', threadContext: null, comments: [{ id: 1, content: 'general' }] },
      { id: 14, status: 'wontFix', threadContext: { filePath: '/b', leftFileStart: { line: 9 } }, comments: [{ id: 1 }] },
      { id: 15, status: 'weird', threadContext: { filePath: '/c' }, comments: [{ id: 1, content: 'x' }] },
      { id: 16, comments: [{ id: 1, commentType: 'system', content: 'voted' }] },
      { id: 17, isDeleted: true, comments: [{ id: 1 }] },
      { id: 18 },
    ],
    'https://w',
  );
  assert.strictEqual(records.length, 5);
  assert.deepStrictEqual(records[0], {
    id: 'thread-comment/12.1',
    kind: 'thread-comment',
    status: 'resolved',
    can_reply: true,
    can_resolve: true,
    path: '/src/a.ts',
    line: 4,
    content: 'root',
    author: 'Ann',
    in_reply_to: null,
    diff_hunk: null,
    url: 'https://w?discussionId=12',
  });
  assert.strictEqual(records[1].in_reply_to, 1);
  assert.strictEqual(records[1].author, null);
  assert.deepStrictEqual([records[2].status, records[2].path, records[2].line], ['open', null, null]);
  assert.deepStrictEqual([records[3].status, records[3].line, records[3].content], ['wontfix', 9, '']);
  assert.deepStrictEqual([records[4].status, records[4].line], ['open', null]);
});

test('pickPrMetadata keeps the useful fields', () => {
  const meta = lib.pickPrMetadata(
    {
      pullRequestId: 5,
      title: 't',
      status: 'active',
      targetRefName: 'refs/heads/main',
      sourceRefName: 'refs/heads/feat/x',
      repository: { name: 'r' },
      createdBy: { displayName: 'Bo' },
    },
    'https://w',
  );
  assert.deepStrictEqual(meta, {
    number: 5,
    title: 't',
    body: '',
    state: 'active',
    isDraft: false,
    url: 'https://w',
    baseRefName: 'main',
    headRefName: 'feat/x',
    repository: 'r',
    author: 'Bo',
  });
  const bare = lib.pickPrMetadata({ description: 'd', isDraft: true }, 'u');
  assert.deepStrictEqual([bare.body, bare.isDraft, bare.baseRefName, bare.repository, bare.author], ['d', true, null, null, null]);
});
