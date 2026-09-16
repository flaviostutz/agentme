#!/usr/bin/env node
'use strict';

/**
 * Applies pr-owner-assistant tracking-file drafts to a live Azure DevOps PR, using the
 * `az rest` commands documented in 251-azure-devops-connector's "Writing data" section.
 * Delegates every tracking-file read/write to the sibling `update-section.js` script so
 * there is exactly one place that understands the file format.
 *
 * Every write is verified by an independent read-back before the tracking file is ever
 * marked `pending-reply: applied` -- a zero exit code from `az rest` alone is never treated
 * as proof a write persisted (see 251-azure-devops-connector's Known Issues: a POST/PATCH
 * can exit 0 without the change actually landing on the server).
 *
 * Usage:
 *   post-replies-azure-devops.js --pr-url <url> <tracking-file> [--dry-run] [--only <id>[,<id>...]]
 *
 * <url> is the PR's Azure DevOps URL (modern dev.azure.com or legacy *.visualstudio.com
 * format); org/project/repo/PR number are all parsed from it.
 * Processes every section whose `pending-reply:` is currently `drafted`, or exactly the
 * `--only` ids (regardless of their current `pending-reply` state) when given. For each:
 * skips posting if the exact reply text is already present on the live thread (verified
 * idempotency, never assumed), otherwise POSTs `reply-draft` as a reply and verifies via
 * GET; then, if `resolve-on-apply: true`, PATCHes the thread to "fixed" and verifies that
 * too. Only after these checks pass does it mark `pending-reply: applied` (and
 * `status: resolved`) via update-section.js. `AZ_BIN` (default `az`) overrides the CLI
 * binary invoked, for testing with a stub.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

const ADO_RESOURCE = '499b84ac-1321-427f-aa17-267ca6975798'; // Azure DevOps' well-known AAD resource id
const UPDATE_SECTION = path.join(__dirname, 'update-section.js');
const [AZ_BIN, ...AZ_PREFIX_ARGS] = (process.env.AZ_BIN || 'az').split(' ');

function parsePrUrl(url) {
  let m = /^https:\/\/dev\.azure\.com\/([^/]+)\/([^/]+)\/_git\/([^/]+)\/pullrequest\/(\d+)/.exec(url);
  if (m) return { org: m[1], project: m[2], repo: m[3], pr: m[4] };
  m = /^https:\/\/([^./]+)\.visualstudio\.com\/([^/]+)\/_git\/([^/]+)\/pullrequest\/(\d+)/.exec(url);
  if (m) return { org: m[1], project: m[2], repo: m[3], pr: m[4] };
  throw new Error(`unrecognized Azure DevOps PR URL: ${url}`);
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

function getThread(base, threadId) {
  const uri = `${base}/threads/${threadId}?api-version=7.1`;
  const out = execFileSync(AZ_BIN, [...AZ_PREFIX_ARGS, 'rest', '--resource', ADO_RESOURCE, '--method', 'GET', '--uri', uri], {
    stdio: 'pipe',
  });
  return JSON.parse(out.toString());
}

function applySection(base, tmpDir, file, row) {
  const m = /^thread-comment\/(\d+)\.(\d+)$/.exec(row.id);
  if (!m) return { id: row.id, ok: false, error: `id is not a thread-comment/<threadId>.<commentId> value: ${row.id}` };
  const [, threadId, commentId] = m;
  const resolveOnApply = row['resolve-on-apply'] === 'true';
  const rawDraft = runUpdateSection(['get', file, row.id, 'reply-draft']).replace(/\n$/, '');
  const replyText = joinReplyDraft(rawDraft);

  try {
    const before = getThread(base, threadId);
    const alreadyPosted = (before.comments || []).some((c) => c.content === replyText);
    if (!alreadyPosted) {
      const bodyFile = path.join(tmpDir, `body-${threadId}.json`);
      fs.writeFileSync(bodyFile, JSON.stringify({ content: replyText, parentCommentId: Number(commentId) }));
      const postUri = `${base}/threads/${threadId}/comments?api-version=7.1`;
      execFileSync(AZ_BIN, [...AZ_PREFIX_ARGS, 'rest', '--resource', ADO_RESOURCE, '--method', 'POST', '--uri', postUri, '--body', `@${bodyFile}`], {
        stdio: 'pipe',
      });

      // az exiting 0 is not proof the write persisted -- always read back to confirm.
      const afterPost = getThread(base, threadId);
      if (!(afterPost.comments || []).some((c) => c.content === replyText)) {
        return { id: row.id, ok: false, error: 'POST exited 0 but reply missing on read-back verification' };
      }
    }

    let resolved = false;
    if (resolveOnApply) {
      const current = getThread(base, threadId);
      if (current.status === 'fixed') {
        resolved = true;
      } else {
        const patchUri = `${base}/threads/${threadId}?api-version=7.1`;
        execFileSync(AZ_BIN, [...AZ_PREFIX_ARGS, 'rest', '--resource', ADO_RESOURCE, '--method', 'PATCH', '--uri', patchUri, '--body', '{"status":"fixed"}'], {
          stdio: 'pipe',
        });
        const afterPatch = getThread(base, threadId);
        resolved = afterPatch.status === 'fixed';
        if (!resolved) {
          return { id: row.id, ok: false, error: 'PATCH exited 0 but status not "fixed" on read-back verification' };
        }
      }
    }

    // Only ever mark the tracking file after independent verification above, never on a
    // bare `az rest` exit code.
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
    console.error('Usage: post-replies-azure-devops.js --pr-url <url> <tracking-file> [--dry-run] [--only <id>[,<id>...]]');
    process.exit(1);
    return;
  }
  const { org, project, repo, pr } = parsePrUrl(args.prUrl);
  const base = `https://dev.azure.com/${org}/${project}/_apis/git/repositories/${repo}/pullRequests/${pr}`;

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
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'post-replies-'));
    for (const row of rows) {
      const result = applySection(base, tmpDir, args.file, row);
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
