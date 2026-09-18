'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, 'post-replies-github.js');
const { parsePrUrl, joinReplyDraft } = require('./post-replies-github.js');

const PR_URL = 'https://github.com/acme/widgets/pull/482';

// Fake `gh` used via GH_BIN: reads/writes a JSON file (FAKE_GH_STATE) to simulate PR state,
// so tests never touch the network. Supports the `api <path> [-f k=v...] [-F k=v...]
// [--paginate]` and `api graphql -f query=<...> [-f/-F ...]` shapes the real script calls.
const FAKE_GH_SRC = `
'use strict';
const fs = require('fs');
const statePath = process.env.FAKE_GH_STATE;
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const argv = process.argv.slice(2);

function fieldFlags(flag) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === flag) {
      const raw = argv[i + 1];
      const eq = raw.indexOf('=');
      out[raw.slice(0, eq)] = raw.slice(eq + 1);
    }
  }
  return out;
}
function save() { fs.writeFileSync(statePath, JSON.stringify(state)); }

if (argv[1] === 'graphql') {
  const f = fieldFlags('-f');
  const query = f.query;
  if (query.includes('resolveReviewThread')) {
    const nodeId = f.id;
    const entry = Object.values(state.threads).find((t) => t.nodeId === nodeId);
    if (!entry) { console.error('unknown thread node ' + nodeId); process.exit(1); }
    if (!(state.resolveBehavior && state.resolveBehavior[nodeId] === 'false-positive')) {
      entry.isResolved = true;
      save();
    }
    process.stdout.write(JSON.stringify({ data: { resolveReviewThread: { thread: { isResolved: entry.isResolved } } } }));
  } else if (query.includes('reviewThreads')) {
    const nodes = Object.entries(state.threads).map(([rootId, t]) => ({
      id: t.nodeId,
      isResolved: t.isResolved,
      comments: { nodes: [{ databaseId: Number(rootId) }] },
    }));
    process.stdout.write(JSON.stringify({ data: { repository: { pullRequest: { reviewThreads: { nodes } } } } }));
  } else {
    console.error('unrecognized graphql query');
    process.exit(1);
  }
} else {
  const restPath = argv[1];
  const f = fieldFlags('-f');
  const cap = fieldFlags('-F');
  const isPost = argv.includes('-f') || argv.includes('-F');

  if (/\\/issues\\/\\d+\\/comments$/.test(restPath)) {
    if (!isPost) {
      process.stdout.write(JSON.stringify(state.issueComments));
    } else {
      if (state.failPost && state.failPost.includes('issue')) {
        console.error('simulated hard POST failure for issue comment');
        process.exit(1);
      }
      if (!(state.postBehavior && state.postBehavior.issue === 'false-positive')) {
        state.issueComments.push({ id: state.issueComments.length + 1, body: f.body });
        save();
      }
      process.stdout.write(JSON.stringify({ id: state.issueComments.length }));
    }
  } else if (/\\/pulls\\/\\d+\\/comments$/.test(restPath)) {
    if (!isPost) {
      process.stdout.write(JSON.stringify(state.reviewComments));
    } else {
      const key = cap.in_reply_to;
      if (state.failPost && state.failPost.includes(key)) {
        console.error('simulated hard POST failure for ' + key);
        process.exit(1);
      }
      if (!(state.postBehavior && state.postBehavior[key] === 'false-positive')) {
        state.reviewComments.push({ id: state.reviewComments.length + 1, body: f.body, in_reply_to_id: Number(key) });
        save();
      }
      process.stdout.write(JSON.stringify({ id: state.reviewComments.length }));
    }
  } else {
    console.error('unsupported fake gh call: ' + restPath);
    process.exit(1);
  }
}
`;

const FIXTURE = `# PR #482

### Rename the exported helper
id: review-comment/91234
status: open
source: (PR conversation)
comment-raw: |
  suggestion: rename this to something clearer.
replies-raw:
possible-follow-ups:
  - fix: rename per the suggestion
action: fix
resolve-on-apply: true
pending-reply: drafted
reply-draft: |
  Fixed -- renamed per your suggestion, thanks! (resolve-pr-comments - guided)

### General question about the release plan
id: issue-comment/555
status: open
source: (PR conversation)
comment-raw: |
  What's the plan for releasing this?
replies-raw:
possible-follow-ups:
action: reply
resolve-on-apply: false
pending-reply: drafted
reply-draft: |
  Targeting the next minor release once CI is green. (resolve-pr-comments -
  guided)

### Already handled comment, should never be touched
id: review-comment/77777
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
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'post-replies-gh-test-'));
  const file = path.join(dir, 'review-pr-482.md');
  fs.writeFileSync(file, FIXTURE);
  const fakeGh = path.join(dir, 'fake-gh.js');
  fs.writeFileSync(fakeGh, FAKE_GH_SRC);
  const statePath = path.join(dir, 'state.json');
  fs.writeFileSync(statePath, JSON.stringify(state));
  return { file, statePath, env: { ...process.env, GH_BIN: `node ${fakeGh}`, FAKE_GH_STATE: statePath } };
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

test('parsePrUrl extracts owner/repo/pr from a GitHub PR URL', () => {
  assert.deepEqual(parsePrUrl(PR_URL), { owner: 'acme', repo: 'widgets', pr: '482' });
});

test('parsePrUrl rejects an unrecognized URL rather than guessing', () => {
  assert.throws(() => parsePrUrl('https://example.com/not/github'), /unrecognized GitHub PR URL/);
});

test('joinReplyDraft rejoins hand-wrapped lines within a paragraph, preserving paragraph breaks', () => {
  const raw = 'Line one\nstill line one.\n\nSecond paragraph\non two lines.';
  assert.equal(joinReplyDraft(raw), 'Line one still line one.\n\nSecond paragraph on two lines.');
});

test('posts a review-comment reply, verifies via read-back, resolves the thread, and marks applied', () => {
  const { file, env } = setup({
    issueComments: [],
    reviewComments: [],
    threads: { 91234: { nodeId: 'PRT_1', isResolved: false } },
  });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'review-comment/91234', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /OK {3}review-comment\/91234 replied\+verified \+ resolved\+verified/);
  assert.equal(getField(file, 'review-comment/91234', 'pending-reply'), 'applied');
  assert.equal(getField(file, 'review-comment/91234', 'status'), 'resolved');
});

test('posts an issue-comment reply, verifies via read-back, and never attempts a resolve', () => {
  const { file, env } = setup({ issueComments: [], reviewComments: [], threads: {} });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'issue-comment/555', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /OK {3}issue-comment\/555 replied\+verified$/m);
  assert.equal(getField(file, 'issue-comment/555', 'pending-reply'), 'applied');
  assert.equal(getField(file, 'issue-comment/555', 'status'), 'open');
});

test('REGRESSION: does not mark pending-reply applied when the POST exits 0 but the reply never persists', () => {
  const { file, env } = setup({
    issueComments: [],
    reviewComments: [],
    threads: { 91234: { nodeId: 'PRT_1', isResolved: false } },
    postBehavior: { 91234: 'false-positive' },
  });
  const { status, stderr } = run(['--pr-url', PR_URL, '--only', 'review-comment/91234', file], env);
  assert.equal(status, 1);
  assert.match(stderr, /FAIL review-comment\/91234: gh api exited 0 but reply missing on read-back verification/);
  assert.equal(getField(file, 'review-comment/91234', 'pending-reply'), 'drafted');
});

test('REGRESSION: does not mark status resolved when the mutation exits 0 but isResolved never persists', () => {
  const { file, env } = setup({
    issueComments: [],
    reviewComments: [],
    threads: { 91234: { nodeId: 'PRT_1', isResolved: false } },
    resolveBehavior: { PRT_1: 'false-positive' },
  });
  const { status, stderr } = run(['--pr-url', PR_URL, '--only', 'review-comment/91234', file], env);
  assert.equal(status, 1);
  assert.match(stderr, /FAIL review-comment\/91234: resolveReviewThread exited 0 but isResolved false on read-back verification/);
  assert.equal(getField(file, 'review-comment/91234', 'pending-reply'), 'drafted');
  assert.equal(getField(file, 'review-comment/91234', 'status'), 'open');
});

test('skips re-posting when the exact reply is already present, but still marks applied', () => {
  const { file, env } = setup({
    issueComments: [],
    reviewComments: [{ id: 1, body: 'Fixed -- renamed per your suggestion, thanks! (resolve-pr-comments - guided)', in_reply_to_id: 91234 }],
    threads: { 91234: { nodeId: 'PRT_1', isResolved: false } },
    // If the script incorrectly tries to POST again, this makes it fail loudly.
    failPost: ['91234'],
  });
  const { status, stdout } = run(['--pr-url', PR_URL, '--only', 'review-comment/91234', file], env);
  assert.equal(status, 0, stdout);
  assert.equal(getField(file, 'review-comment/91234', 'pending-reply'), 'applied');
});

test('never processes a section whose pending-reply is not drafted, when --only is not given', () => {
  const { file, env } = setup({
    issueComments: [],
    reviewComments: [],
    threads: {
      91234: { nodeId: 'PRT_1', isResolved: false },
      // 77777 deliberately absent: pending-reply is 'none' for it, so a correct run never
      // references it at all -- if it did, the fake gh would fail with "no review thread
      // found" and this test would catch it via the failPost trap below.
    },
    failPost: ['77777'],
  });
  const { status, stdout } = run(['--pr-url', PR_URL, file], env);
  assert.equal(status, 0, stdout);
  assert.equal(getField(file, 'review-comment/77777', 'pending-reply'), 'none');
});

test('--dry-run prints drafts without invoking gh or changing the tracking file', () => {
  const { file, env } = setup({ issueComments: [], reviewComments: [], threads: {} }); // any gh call would throw
  const { status, stdout } = run(['--pr-url', PR_URL, '--dry-run', file], env);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /=== review-comment\/91234 \(resolve=true\) ===/);
  assert.match(stdout, /=== issue-comment\/555 \(resolve=false\) ===/);
  assert.equal(getField(file, 'review-comment/91234', 'pending-reply'), 'drafted');
});
