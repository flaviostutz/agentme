#!/usr/bin/env node
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, 'post-replies-azure-devops.js');
const { parsePrUrl, joinReplyDraft } = require('./post-replies-azure-devops.js');

const PR_URL = 'https://dev.azure.com/example-org/example-project/_git/example-project/pullrequest/43556';

// Fake `az` used via AZ_BIN: reads/writes a JSON file (FAKE_ADO_STATE) to simulate thread
// state, so tests never touch the network. Supports the same `rest --method GET|POST|PATCH
// --uri <url> [--body <json|@file>]` shape the real script calls.
const FAKE_AZ_SRC = `
'use strict';
const fs = require('fs');
const statePath = process.env.FAKE_ADO_STATE;
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const argv = process.argv.slice(2);
const method = argv[argv.indexOf('--method') + 1];
const uri = argv[argv.indexOf('--uri') + 1];
let body = null;
const bodyIdx = argv.indexOf('--body');
if (bodyIdx !== -1) {
  let raw = argv[bodyIdx + 1];
  if (raw.startsWith('@')) raw = fs.readFileSync(raw.slice(1), 'utf8');
  body = JSON.parse(raw);
}
const commentsMatch = /threads\\/(\\d+)\\/comments/.exec(uri);
const threadMatch = /threads\\/(\\d+)/.exec(uri);
const threadId = (commentsMatch || threadMatch)[1];
const thread = state.threads[threadId];
if (!thread) { console.error('unknown thread ' + threadId); process.exit(1); }
if (method === 'GET') {
  process.stdout.write(JSON.stringify(thread));
} else if (method === 'POST' && commentsMatch) {
  if (state.failPost && state.failPost.includes(threadId)) {
    console.error('simulated hard POST failure for ' + threadId);
    process.exit(1);
  }
  if (!(state.postBehavior && state.postBehavior[threadId] === 'false-positive')) {
    thread.comments.push({ id: thread.comments.length + 1, content: body.content, parentCommentId: body.parentCommentId });
  }
  fs.writeFileSync(statePath, JSON.stringify(state));
  process.stdout.write(JSON.stringify({ id: thread.comments.length }));
} else if (method === 'PATCH') {
  if (!(state.patchBehavior && state.patchBehavior[threadId] === 'false-positive')) {
    thread.status = body.status;
  }
  fs.writeFileSync(statePath, JSON.stringify(state));
  process.stdout.write(JSON.stringify(thread));
} else {
  console.error('unsupported fake az call: ' + method + ' ' + uri);
  process.exit(1);
}
`;

const FIXTURE = `# PR #43556

### Reusing atlas service principal for unrelated pipeline
id: thread-comment/100.1
status: open
source: (PR conversation)
comment-raw: |
  Should we really use atlas service principal even when it is not atlas doing the action?
replies-raw:
possible-follow-ups:
  - fix: create a dedicated service connection
action: fix
resolve-on-apply: false
pending-reply: drafted
reply-draft: |
  Agreed -- good catch. Renamed the parameter to a dedicated codeowners-app service
  connection. Leaving this thread open until it is created. (resolve-pr-comments -
  guided)

### Split run() into smaller functions
id: thread-comment/200.1
status: open
source: (PR conversation)
comment-raw: |
  Can we split this into smaller functions?
replies-raw:
possible-follow-ups:
action: fix
resolve-on-apply: true
pending-reply: drafted
reply-draft: |
  Fixed -- split run() into named single-purpose functions. (resolve-pr-comments -
  guided)

### Already handled comment, should never be touched
id: thread-comment/300.1
status: open
source: (PR conversation)
comment-raw: |
  Unrelated comment still awaiting triage.
replies-raw:
possible-follow-ups:
action:
resolve-on-apply: false
pending-reply: none
reply-draft: |
`;

function setup(state) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'post-replies-test-'));
  const file = path.join(dir, 'review-pr-43556.md');
  fs.writeFileSync(file, FIXTURE);
  const fakeAz = path.join(dir, 'fake-az.js');
  fs.writeFileSync(fakeAz, FAKE_AZ_SRC);
  const statePath = path.join(dir, 'state.json');
  fs.writeFileSync(statePath, JSON.stringify(state));
  return { file, statePath, env: { ...process.env, AZ_BIN: `node ${fakeAz}`, FAKE_ADO_STATE: statePath } };
}

function run(args, env) {
  try {
    const stdout = execFileSync('node', [SCRIPT, ...args], { encoding: 'utf8', env });
    return { status: 0, stdout };
  } catch (err) {
    return { status: err.status, stdout: err.stdout, stderr: err.stderr };
  }
}

function getField(file, id, field) {
  return execFileSync('node', [path.join(__dirname, 'update-section.js'), 'get', file, id, field], { encoding: 'utf8' }).trim();
}

test('parsePrUrl extracts org/project/repo/pr from a modern dev.azure.com URL', () => {
  assert.deepEqual(parsePrUrl(PR_URL), { org: 'example-org', project: 'example-project', repo: 'example-project', pr: '43556' });
});

test('parsePrUrl extracts org/project/repo/pr from a legacy *.visualstudio.com URL', () => {
  assert.deepEqual(parsePrUrl('https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/1029'), {
    org: 'contoso',
    project: 'Widgets',
    repo: 'widgets-api',
    pr: '1029',
  });
});

test('parsePrUrl rejects an unrecognized URL rather than guessing', () => {
  assert.throws(() => parsePrUrl('https://example.com/not/ado'), /unrecognized Azure DevOps PR URL/);
});

test('joinReplyDraft rejoins hand-wrapped lines within a paragraph, preserving paragraph breaks', () => {
  const raw = 'Line one\nstill line one.\n\nSecond paragraph\non two lines.';
  assert.equal(joinReplyDraft(raw), 'Line one still line one.\n\nSecond paragraph on two lines.');
});

test('posts a drafted reply, verifies via read-back, and marks pending-reply applied', () => {
  const { file, env } = setup({
    threads: {
      100: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
    },
  });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'thread-comment/100.1', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /OK {3}thread-comment\/100\.1 replied\+verified$/m);
  assert.equal(getField(file, 'thread-comment/100.1', 'pending-reply'), 'applied');
  assert.equal(getField(file, 'thread-comment/100.1', 'status'), 'open'); // resolve-on-apply: false
});

test('resolves the thread and marks status resolved when resolve-on-apply is true', () => {
  const { file, env } = setup({
    threads: {
      200: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
    },
  });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'thread-comment/200.1', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /replied\+verified \+ resolved\+verified/);
  assert.equal(getField(file, 'thread-comment/200.1', 'pending-reply'), 'applied');
  assert.equal(getField(file, 'thread-comment/200.1', 'status'), 'resolved');
});

test('REGRESSION: does not mark pending-reply applied when POST exits 0 but the reply never persists', () => {
  const { file, env } = setup({
    threads: {
      100: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
    },
    postBehavior: { 100: 'false-positive' },
  });
  const { status, stderr } = run(['--pr-url', PR_URL, '--only', 'thread-comment/100.1', file], env);
  assert.equal(status, 1);
  assert.match(stderr, /FAIL thread-comment\/100\.1: POST exited 0 but reply missing on read-back verification/);
  assert.equal(getField(file, 'thread-comment/100.1', 'pending-reply'), 'drafted');
});

test('REGRESSION: does not mark status resolved when PATCH exits 0 but status never persists', () => {
  const { file, env } = setup({
    threads: {
      200: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
    },
    patchBehavior: { 200: 'false-positive' },
  });
  const { status, stderr } = run(['--pr-url', PR_URL, '--only', 'thread-comment/200.1', file], env);
  assert.equal(status, 1);
  assert.match(stderr, /FAIL thread-comment\/200\.1: PATCH exited 0 but status not "fixed" on read-back verification/);
  assert.equal(getField(file, 'thread-comment/200.1', 'pending-reply'), 'drafted');
  assert.equal(getField(file, 'thread-comment/200.1', 'status'), 'open');
});

test('skips re-posting when the exact reply is already present on the live thread, but still marks applied', () => {
  const alreadyPostedText =
    'Agreed -- good catch. Renamed the parameter to a dedicated codeowners-app service connection. Leaving this thread open until it is created. (resolve-pr-comments - guided)';
  const { file, env } = setup({
    threads: {
      100: {
        status: 'active',
        comments: [
          { id: 1, content: 'orig comment' },
          { id: 2, content: alreadyPostedText },
        ],
      },
    },
    // If the script incorrectly tries to POST again, this makes it fail loudly.
    failPost: ['100'],
  });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'thread-comment/100.1', file], env);
  assert.equal(status, 0, stdout);
  assert.equal(getField(file, 'thread-comment/100.1', 'pending-reply'), 'applied');
});

test('never processes a section whose pending-reply is not drafted, when --only is not given', () => {
  const { file, env } = setup({
    threads: {
      100: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
      200: { status: 'active', comments: [{ id: 1, content: 'orig comment' }] },
      // 300 deliberately absent: pending-reply is 'none' for it, so a correct run never
      // references thread 300 at all -- if it did, the fake az would fail with "unknown
      // thread 300" and this test would catch it.
    },
    failPost: ['300'],
  });
  const { status, stdout } = run(['--pr-url', PR_URL, file], env);
  assert.equal(status, 0, stdout);
  assert.equal(getField(file, 'thread-comment/300.1', 'pending-reply'), 'none');
});

test('--dry-run prints drafts without invoking az or changing the tracking file', () => {
  const { file, env } = setup({ threads: {} }); // no threads defined: any az call would throw
  const { status, stdout } = run(['--pr-url', PR_URL, '--dry-run', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /=== thread-comment\/100\.1 \(resolve=false\) ===/);
  assert.match(stdout, /=== thread-comment\/200\.1 \(resolve=true\) ===/);
  assert.equal(getField(file, 'thread-comment/100.1', 'pending-reply'), 'drafted');
});
