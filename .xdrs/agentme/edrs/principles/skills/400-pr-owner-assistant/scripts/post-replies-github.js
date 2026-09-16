#!/usr/bin/env node
'use strict';

/**
 * Applies pr-owner-assistant tracking-file drafts to a live GitHub PR, using the `gh`
 * commands documented in 250-github-connector's "Writing data" section. Delegates every
 * tracking-file read/write to the sibling `update-section.js` script so there is exactly
 * one place that understands the file format. Mirrors post-replies-azure-devops.js's
 * interface and verify-after-write discipline for parity across both connectors.
 *
 * Every write is confirmed by an independent read-back before the tracking file is ever
 * marked `pending-reply: applied` -- not because `gh` is known to exit 0 without persisting
 * (unlike `az rest`, see 251-azure-devops-connector's Known Issues), but so both scripts
 * make the same guarantee and a GraphQL mutation's rarer partial-failure shape is still
 * caught.
 *
 * Usage:
 *   post-replies-github.js --pr-url <url> <tracking-file> [--dry-run] [--only <id>[,<id>...]]
 *
 * <url> is the PR's GitHub URL; owner/repo/PR number are all parsed from it.
 * Processes every section whose `pending-reply:` is currently `drafted`, or exactly the
 * `--only` ids (regardless of their current `pending-reply` state) when given. For each:
 * skips posting if the exact reply text is already present (verified idempotency, never
 * assumed), otherwise posts `reply-draft` per the section's `id` kind (`issue-comment` via
 * the issue-comments endpoint, `review-comment` via the review-comments endpoint with
 * `in_reply_to`) and verifies via a follow-up read; then, if `resolve-on-apply: true` and
 * the kind is `review-comment` (the only resolvable kind), resolves the review thread via
 * the `resolveReviewThread` GraphQL mutation and verifies `isResolved` too. Only after these
 * checks pass does it mark `pending-reply: applied` (and `status: resolved`) via
 * update-section.js. `GH_BIN` (default `gh`) overrides the CLI binary invoked, for testing
 * with a stub.
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const UPDATE_SECTION = path.join(__dirname, 'update-section.js');
const [GH_BIN, ...GH_PREFIX_ARGS] = (process.env.GH_BIN || 'gh').split(' ');

function parsePrUrl(url) {
  const m = /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/.exec(url);
  if (!m) throw new Error(`unrecognized GitHub PR URL: ${url}`);
  return { owner: m[1], repo: m[2], pr: m[3] };
}

// Rejoins hand-wrapped lines within a paragraph into one logical line, preserving genuine
// blank-line paragraph breaks -- tolerant of drafts written either wrapped or unwrapped.
function joinReplyDraft(rawText) {
  const paragraphs = [];
  let cur = [];
  for (const line of rawText.split('\n')) {
    if (line.trim() === '') {
      if (cur.length) {
        paragraphs.push(cur.join(' '));
        cur = [];
      }
    } else {
      cur.push(line.trimEnd());
    }
  }
  if (cur.length) paragraphs.push(cur.join(' '));
  return paragraphs.join('\n\n');
}

function parseArgs(argv) {
  const args = { file: null, prUrl: null, dryRun: false, only: null };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--pr-url') args.prUrl = argv[++i];
    else if (a === '--dry-run') args.dryRun = true;
    else if (a === '--only') {
      args.only = argv[++i]
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
    } else rest.push(a);
  }
  [args.file] = rest;
  return args;
}

function runUpdateSection(cmdArgs, input) {
  return execFileSync('node', [UPDATE_SECTION, ...cmdArgs], { input, encoding: 'utf8' });
}

function listCandidateSections(file, only) {
  const stdout = runUpdateSection(['list', file]);
  const rows = [];
  let cur = null;
  for (const line of stdout.split('\n')) {
    const idMatch = /^- id: (.*)$/.exec(line);
    if (idMatch) {
      if (cur) rows.push(cur);
      cur = { id: idMatch[1] };
      continue;
    }
    if (!cur) continue;
    const fieldMatch = /^ {2}([\w-]+): ?(.*)$/.exec(line);
    if (fieldMatch) cur[fieldMatch[1]] = fieldMatch[2];
  }
  if (cur) rows.push(cur);
  return rows.filter((r) => (only ? only.includes(r.id) : r['pending-reply'] === 'drafted'));
}

function gh(args) {
  return execFileSync(GH_BIN, [...GH_PREFIX_ARGS, ...args], { stdio: 'pipe' });
}

function ghJson(args) {
  return JSON.parse(gh(args).toString());
}

function commentsEndpoint(ctx, kind) {
  const { owner, repo, pr } = ctx;
  return kind === 'review-comment' ? `repos/${owner}/${repo}/pulls/${pr}/comments` : `repos/${owner}/${repo}/issues/${pr}/comments`;
}

function findReviewThread(ctx, rootCommentId) {
  const query = `query($owner:String!,$repo:String!,$pr:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$pr){reviewThreads(first:100){nodes{id isResolved comments(first:1){nodes{databaseId}}}}}}}`;
  const out = ghJson(['api', 'graphql', '-f', `query=${query}`, '-f', `owner=${ctx.owner}`, '-f', `repo=${ctx.repo}`, '-F', `pr=${ctx.pr}`]);
  const nodes = out.data.repository.pullRequest.reviewThreads.nodes;
  return nodes.find((n) => String(n.comments.nodes[0] && n.comments.nodes[0].databaseId) === String(rootCommentId));
}

function resolveReviewThread(nodeId) {
  const mutation = `mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}`;
  return ghJson(['api', 'graphql', '-f', `query=${mutation}`, '-f', `id=${nodeId}`]);
}

function applySection(ctx, file, row) {
  const m = /^(issue-comment|review-comment|review-summary)\/(\d+)$/.exec(row.id);
  if (!m) return { id: row.id, ok: false, error: `id is not a <kind>/<numeric-id> value: ${row.id}` };
  const [, kind, numericId] = m;
  const resolveOnApply = row['resolve-on-apply'] === 'true' && kind === 'review-comment';
  const rawDraft = runUpdateSection(['get', file, row.id, 'reply-draft']).replace(/\n$/, '');
  const replyText = joinReplyDraft(rawDraft);
  const endpoint = commentsEndpoint(ctx, kind);

  try {
    const isReviewComment = kind === 'review-comment';
    const before = ghJson(['api', endpoint, '--paginate']);
    let alreadyPosted = isReviewComment
      ? before.some((c) => c.body === replyText && String(c.in_reply_to_id) === numericId)
      : before.some((c) => c.body === replyText);

    if (!alreadyPosted) {
      const postArgs = ['api', endpoint, '-f', `body=${replyText}`];
      if (isReviewComment) postArgs.push('-F', `in_reply_to=${numericId}`);
      gh(postArgs);

      // A 2xx exit is not proof the write persisted -- always read back to confirm.
      const after = ghJson(['api', endpoint, '--paginate']);
      alreadyPosted = isReviewComment
        ? after.some((c) => c.body === replyText && String(c.in_reply_to_id) === numericId)
        : after.some((c) => c.body === replyText);
      if (!alreadyPosted) {
        return { id: row.id, ok: false, error: 'gh api exited 0 but reply missing on read-back verification' };
      }
    }

    let resolved = false;
    if (resolveOnApply) {
      const thread = findReviewThread(ctx, numericId);
      if (!thread) return { id: row.id, ok: false, error: `no review thread found rooted at comment ${numericId}` };
      if (thread.isResolved) {
        resolved = true;
      } else {
        resolveReviewThread(thread.id);
        const after = findReviewThread(ctx, numericId);
        resolved = Boolean(after && after.isResolved);
        if (!resolved) {
          return { id: row.id, ok: false, error: 'resolveReviewThread exited 0 but isResolved false on read-back verification' };
        }
      }
    }

    // Only ever mark the tracking file after independent verification above, never on a
    // bare `gh` exit code.
    runUpdateSection(['set', file, row.id, 'pending-reply', 'applied']);
    if (resolved) runUpdateSection(['set', file, row.id, 'status', 'resolved']);
    return { id: row.id, ok: true, resolved };
  } catch (e) {
    return { id: row.id, ok: false, error: String(e.stderr || e.message) };
  }
}

function main(argv) {
  const args = parseArgs(argv);
  if (!args.file || !args.prUrl) {
    console.error('Usage: post-replies-github.js --pr-url <url> <tracking-file> [--dry-run] [--only <id>[,<id>...]]');
    process.exit(1);
    return;
  }
  const ctx = parsePrUrl(args.prUrl);

  const rows = listCandidateSections(args.file, args.only);
  if (rows.length === 0) {
    console.log('No sections to apply (nothing pending-reply: drafted).');
    return;
  }

  const results = [];
  if (args.dryRun) {
    for (const row of rows) {
      const rawDraft = runUpdateSection(['get', args.file, row.id, 'reply-draft']).replace(/\n$/, '');
      console.log(`\n=== ${row.id} (resolve=${row['resolve-on-apply'] === 'true'}) ===\n${joinReplyDraft(rawDraft)}`);
      results.push({ id: row.id, ok: true, dryRun: true });
    }
  } else {
    for (const row of rows) {
      const result = applySection(ctx, args.file, row);
      results.push(result);
      if (result.ok) {
        console.log(`OK   ${result.id} replied+verified${result.resolved ? ' + resolved+verified' : ''}`);
      } else {
        console.error(`FAIL ${result.id}: ${result.error}`);
      }
    }
  }

  console.log('\n--- SUMMARY ---');
  console.log(JSON.stringify(results, null, 2));
  if (results.some((r) => !r.ok)) process.exit(1);
}

if (require.main === module) {
  try {
    main(process.argv.slice(2));
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

module.exports = { parsePrUrl, joinReplyDraft };
