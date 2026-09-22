#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, 'update-section.js');

const FIXTURE = `# PR #482

Some raw PR summary text.

### Contributor offers to help
id: issue-comment/111
status: open
source: (PR conversation)
comment-raw: |
  Thanks for this PR!

  Happy to help test it.
replies-raw:
possible-follow-ups:
  - reply thanking them
action:
resolve-on-apply: false
pending-reply: none
reply-draft: |

### Naming taxonomy question
id: review-comment/222
status: open
source: [lib/src/foo.ts:10-10](../lib/src/foo.ts#L10-L10)
author-raw: octocat
suggested-fix: |
  const value = compute();
suggested-fix-assessment: accept-as-is
criticality: medium
automation-suggestion: fully-auto
comment-raw: |
  Shall we rename this?
replies-raw:
possible-follow-ups:
  - "fix: rename for consistency"
  - "mark won't-fix: keep current naming"
similar-to:
  - review-comment/333
action: fix
resolve-on-apply: true
pending-reply: drafted
reply-draft: |
  Renamed as suggested. (resolve-pr-comments - guided)
`;

function writeFixture(content = FIXTURE) {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'update-section-test-')), 'review-pr-482.md');
  fs.writeFileSync(file, content);
  return file;
}

function tmpFilePath(name = 'review-pr-999.md') {
  return path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'update-section-test-')), name);
}

function run(args, input) {
  try {
    const stdout = execFileSync('node', [SCRIPT, ...args], { input, encoding: 'utf8' });
    return { status: 0, stdout };
  } catch (err) {
    return { status: err.status, stdout: err.stdout, stderr: err.stderr };
  }
}

test('list renders one bullet block per section, not tab-aligned columns', () => {
  const file = writeFixture();
  const { status, stdout } = run(['list', file]);
  assert.equal(status, 0);
  assert.equal(stdout.includes('\t'), false, 'list output must not rely on tab alignment');
  assert.match(stdout, /- id: issue-comment\/111/);
  assert.match(stdout, /^ {2}title: Contributor offers to help$/m);
  assert.match(stdout, /^ {2}status: open$/m);
  assert.match(stdout, /- id: review-comment\/222/);
  assert.match(stdout, /^ {2}author-raw: octocat$/m);
  assert.match(stdout, /^ {2}criticality: medium$/m);
  assert.match(stdout, /^ {2}automation-suggestion: fully-auto$/m);
  assert.match(stdout, /^ {2}action: fix$/m);
  assert.match(stdout, /^ {2}pending-reply: drafted$/m);
  assert.match(stdout, /^ {2}similar-to: review-comment\/333$/m);
});

test('list --json renders one JSON object per section with the same fields', () => {
  const file = writeFixture();
  const { status, stdout } = run(['list', file, '--json']);
  assert.equal(status, 0);
  const rows = JSON.parse(stdout);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].id, 'issue-comment/111');
  assert.equal(rows[0].title, 'Contributor offers to help');
  assert.equal(rows[1].id, 'review-comment/222');
  assert.equal(rows[1]['author-raw'], 'octocat');
  assert.equal(rows[1].criticality, 'medium');
  assert.equal(rows[1]['automation-suggestion'], 'fully-auto');
  assert.equal(rows[1].action, 'fix');
  assert.equal(rows[1]['pending-reply'], 'drafted');
  assert.equal(rows[1]['similar-to'], 'review-comment/333');
});

test('get returns a scalar field value', () => {
  const file = writeFixture();
  const { status, stdout } = run(['get', file, 'review-comment/222', 'status']);
  assert.equal(status, 0);
  assert.equal(stdout.trim(), 'open');
});

test('get returns a block field value with blank lines preserved', () => {
  const file = writeFixture();
  const { status, stdout } = run(['get', file, 'issue-comment/111', 'comment-raw']);
  assert.equal(status, 0);
  assert.equal(stdout, 'Thanks for this PR!\n\nHappy to help test it.\n');
});

test('get returns a list field with dash prefixes stripped', () => {
  const file = writeFixture();
  const { status, stdout } = run(['get', file, 'review-comment/222', 'possible-follow-ups']);
  assert.equal(status, 0);
  assert.equal(stdout, '"fix: rename for consistency"\n"mark won\'t-fix: keep current naming"\n');
});

test('get returns the suggested-fix block field extracted for a comment', () => {
  const file = writeFixture();
  const { status, stdout } = run(['get', file, 'review-comment/222', 'suggested-fix']);
  assert.equal(status, 0);
  assert.equal(stdout, 'const value = compute();\n');
});

test('get returns the suggested-fix-assessment scalar field', () => {
  const file = writeFixture();
  const { status, stdout } = run(['get', file, 'review-comment/222', 'suggested-fix-assessment']);
  assert.equal(status, 0);
  assert.equal(stdout.trim(), 'accept-as-is');
});

test('set updates only the targeted scalar field, leaving the rest of the file untouched', () => {
  const file = writeFixture();
  const before = fs.readFileSync(file, 'utf8');
  const { status } = run(['set', file, 'issue-comment/111', 'action', 'reply']);
  assert.equal(status, 0);
  const after = fs.readFileSync(file, 'utf8');
  assert.equal(after, before.replace('action:\nresolve-on-apply: false\npending-reply: none', 'action: reply\nresolve-on-apply: false\npending-reply: none'));
});

test('set with an empty value clears a scalar field to "field:" with no trailing space', () => {
  const file = writeFixture();
  run(['set', file, 'review-comment/222', 'action', '']);
  const { stdout } = run(['get', file, 'review-comment/222', 'action']);
  assert.equal(stdout.trim(), '');
  assert.match(fs.readFileSync(file, 'utf8'), /^action:$/m);
});

test('set-block replaces block content from stdin, preserving a blank line in the middle', () => {
  const file = writeFixture();
  const { status } = run(['set-block', file, 'issue-comment/111', 'reply-draft'], 'Line one.\n\nLine two.\n');
  assert.equal(status, 0);
  const { stdout } = run(['get', file, 'issue-comment/111', 'reply-draft']);
  assert.equal(stdout, 'Line one.\n\nLine two.\n');
});

test('set-list replaces list content from stdin, skipping blank lines', () => {
  const file = writeFixture();
  const { status } = run(['set-list', file, 'issue-comment/111', 'possible-follow-ups'], 'item one\n\nitem two\n');
  assert.equal(status, 0);
  const { stdout } = run(['get', file, 'issue-comment/111', 'possible-follow-ups']);
  assert.equal(stdout, 'item one\nitem two\n');
});

test('set-block replaces suggested-fix content, preserving multi-line code', () => {
  const file = writeFixture();
  const { status } = run(
    ['set-block', file, 'review-comment/222', 'suggested-fix'],
    'const value = 42;\nconst other = 1;\n',
  );
  assert.equal(status, 0);
  const { stdout } = run(['get', file, 'review-comment/222', 'suggested-fix']);
  assert.equal(stdout, 'const value = 42;\nconst other = 1;\n');
});

test('set updates the suggested-fix-assessment scalar field', () => {
  const file = writeFixture();
  const { status } = run(['set', file, 'review-comment/222', 'suggested-fix-assessment', 'evolve-with-changes']);
  assert.equal(status, 0);
  const { stdout } = run(['get', file, 'review-comment/222', 'suggested-fix-assessment']);
  assert.equal(stdout.trim(), 'evolve-with-changes');
});

test('preserves absence of a trailing newline on the original file', () => {
  const file = writeFixture(FIXTURE.replace(/\n$/, ''));
  run(['set', file, 'issue-comment/111', 'action', 'reply']);
  assert.equal(fs.readFileSync(file, 'utf8').endsWith('\n'), false);
});

test('get on an unknown id fails with a clear error', () => {
  const file = writeFixture();
  const { status, stderr } = run(['get', file, 'issue-comment/999', 'status']);
  assert.notEqual(status, 0);
  assert.match(stderr, /no section found with id: issue-comment\/999/);
});

test('get on an ambiguous id (duplicated in a malformed file) fails rather than guessing', () => {
  const file = writeFixture(FIXTURE + FIXTURE.replace('### Contributor offers to help', '### Duplicate section'));
  const { status, stderr } = run(['get', file, 'issue-comment/111', 'status']);
  assert.notEqual(status, 0);
  assert.match(stderr, /ambiguous: 2 sections found with id: issue-comment\/111/);
});

test('set on a block-only field fails and points to set-block', () => {
  const file = writeFixture();
  const { status, stderr } = run(['set', file, 'issue-comment/111', 'reply-draft', 'oops']);
  assert.notEqual(status, 0);
  assert.match(stderr, /use set-block/);
});

test('set-block on a scalar-only field fails and points to set', () => {
  const file = writeFixture();
  const { status, stderr } = run(['set-block', file, 'issue-comment/111', 'action'], 'oops\n');
  assert.notEqual(status, 0);
  assert.match(stderr, /use set \(scalar\)/);
});

test('get/set support the automation-suggestion scalar field', () => {
  const file = writeFixture();
  const { stdout: before } = run(['get', file, 'review-comment/222', 'automation-suggestion']);
  assert.equal(before.trim(), 'fully-auto');
  const { status } = run(['set', file, 'review-comment/222', 'automation-suggestion', 'guided']);
  assert.equal(status, 0);
  const { stdout: after } = run(['get', file, 'review-comment/222', 'automation-suggestion']);
  assert.equal(after.trim(), 'guided');
});

test('get/set-list support the similar-to list field', () => {
  const file = writeFixture();
  const { stdout: before } = run(['get', file, 'review-comment/222', 'similar-to']);
  assert.equal(before, 'review-comment/333\n');
  const { status } = run(
    ['set-list', file, 'review-comment/222', 'similar-to'],
    'review-comment/333\nreview-comment/444\n',
  );
  assert.equal(status, 0);
  const { stdout: after } = run(['get', file, 'review-comment/222', 'similar-to']);
  assert.equal(after, 'review-comment/333\nreview-comment/444\n');
});

test('init creates a new tracking file with the PR header and raw summary', () => {
  const file = tmpFilePath();
  const { status, stdout } = run(
    ['init', file, '999', 'https://github.com/acme/widget/pull/999', 'Adds', 'retry', 'logic'],
    'Raw PR body text.\n\nSecond paragraph.\n',
  );
  assert.equal(status, 0);
  assert.equal(stdout.trim(), 'OK');
  const content = fs.readFileSync(file, 'utf8');
  assert.equal(
    content,
    '# PR #999\n\nhttps://github.com/acme/widget/pull/999\n\nRaw PR body text.\n\nSecond paragraph.\n\n**Summary**: Adds retry logic\n',
  );
});

test('init refuses to overwrite an existing file', () => {
  const file = writeFixture();
  const { status, stderr } = run(
    ['init', file, '999', 'https://example.com/pr/999', 'Some', 'summary'],
    'Raw body.\n',
  );
  assert.notEqual(status, 0);
  assert.match(stderr, /refusing to overwrite existing file/);
});

test('append-section adds a new section after the last one, separated by exactly one blank line', () => {
  const file = writeFixture();
  const newSection =
    '### New finding\nid: issue-comment/777\nstatus: open\nsource: (PR conversation)\ncomment-raw: |\n  A brand new comment.\nreplies-raw:\npossible-follow-ups:\naction:\nresolve-on-apply: false\npending-reply: none\nreply-draft: |\n';
  const { status } = run(['append-section', file], newSection);
  assert.equal(status, 0);
  const content = fs.readFileSync(file, 'utf8');
  assert.match(
    content,
    /\(resolve-pr-comments - guided\)\n\n### New finding\nid: issue-comment\/777/,
  );
  const { stdout } = run(['list', file]);
  assert.match(stdout, /- id: issue-comment\/777/);
});

test('append-section fails when the id already exists', () => {
  const file = writeFixture();
  const { status, stderr } = run(
    ['append-section', file],
    '### Duplicate\nid: issue-comment/111\nstatus: open\n',
  );
  assert.notEqual(status, 0);
  assert.match(stderr, /a section with id "issue-comment\/111" already exists/);
});

test('append-section fails when the file does not exist', () => {
  const file = tmpFilePath();
  const { status, stderr } = run(['append-section', file], '### X\nid: a/1\n');
  assert.notEqual(status, 0);
  assert.match(stderr, /file does not exist/);
});

test('append-section fails when stdin is not a full section', () => {
  const file = writeFixture();
  const { status, stderr } = run(['append-section', file], 'not a section\nid: a/1\n');
  assert.notEqual(status, 0);
  assert.match(stderr, /must be a full section/);
});

test('append-section fails when stdin has no id: line', () => {
  const file = writeFixture();
  const { status, stderr } = run(['append-section', file], '### No id here\nstatus: open\n');
  assert.notEqual(status, 0);
  assert.match(stderr, /missing an "id:" line/);
});
