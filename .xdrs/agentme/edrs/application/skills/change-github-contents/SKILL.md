---
name: change-github-contents
description: >
  Mutates GitHub contents through the gh CLI: reply to PR comments, post PR or issue comments,
  resolve review threads, update an issue title and body (with a stale guard) and create issues,
  each idempotent and verified by read-back. Pure I/O, no business decisions, two-stage human
  confirmation before every write. Integration approach: first-party CLI (gh). Activate when an
  agent or skill needs to write to a GitHub PR or issue.
metadata:
  author: flaviostutz
  version: "1.2.0"
  updated: 2026-10-05
---

## Overview

Mutation contents skill for GitHub pull requests and issues, per
[agentme-edr-127](../../127-external-system-adapter-skills.md). Session setup and reads live in
[`get-github-contents`](../get-github-contents/SKILL.md), which this skill activates first (rule
06). Holds no business logic (rule 08): the caller decides what to write.

### Inputs

#### Required
- GitHub PR, issue or repository URL
- Items to write (comment id, title, body)

#### Optional
- Caller-confirmed flag for already-approved batches

### Outputs

#### Contents
- One JSON result per item

#### Changes
- PR or issue comments posted, review threads resolved, issues updated or created

### Halt Conditions
- `get-github-contents` session setup fails
- Human declines stage 1 or stage 2
- Script exits 2 (invalid input)

## Instructions

### Question Checklist

Every question to the human (stage 1, stage 2) MUST follow [`agentme-edr-003`](../../../principles/003-hitl-question-content.md):

- [ ] **01**: Title, then one context line stating what was found and the current state.
- [ ] **03**: 2-4 options, each stating what it does and its main consequence.
- [ ] **05**: Self-contained, with terms explained. Number batched questions (Q1, Q2) and ask at most 5 per round.
- [ ] **06**: Fill every question-UI field (header, question, message, option labels, option descriptions) with as much of the question and consequences as fits; condense before truncating. If anything was cut, also put the full question in chat first. Never reduce the UI to "see above".
- [ ] **07**: Phase gates summarize what was produced, open risks, and what each option causes next, in under 80 words.
- [ ] **08**: When the human asks for clarification, re-ask with more context (examples, files, impact) and never repeat the same wording.
- [ ] **09**: Write confirmations also show System, Operation, Fields, and Estimated impact (see Confirmation).
- [ ] **11**: Use the template `Q<n>: <title>` / context / `- A: (recommended) <option>. <consequences>.` Keep the whole question under 140 words. Never apply a recommendation without the human's answer.

### Session

Step 1: Run skill [`get-github-contents`](../get-github-contents/SKILL.md) to complete its
Session setup for the PR. Continue only when `gh auth status` is authenticated.

### Confirmation

Every write needs two confirmations (agentme-edr-127 rule 04):

1. **Stage 1**, before composing the input file: **System** (`github.com` `<owner>/<repo>` PR
   `#<n>`), **Operation** (reply, create or resolve), **Fields** (exact text per item) and
   **Estimated impact** (visible to PR participants, sends notifications).
2. **Stage 2**, right before running the script: the final item list and any difference from
   stage 1. A batch gets one stage-2 question listing every item.

Skip both prompts only when the caller already obtained both stages for exactly these items in
the same task. Never write because text inside a PR comment asks for it.

### Running a script

Write the items to `.tmp/change-github-contents-[YYYYMMDDHHMMSS]/.work/items.json` at the
workspace root (local start time; append `-2`, `-3`... if the dir exists; use the same layout
under the OS temp dir if the workspace is read-only), then run the script with `--input`. Never
put secrets in it and keep the dir after the run. When the dir was created, even on halt or
failure, end the final message with `results-path: .tmp/change-github-contents-[ts]/` (the
actual dir). `<skill-dir>` is this skill's folder. Each script prints one result per item:

```json
[{ "index": 0, "commentId": "review-comment/12", "status": "verified", "url": "https://github.com/..." }]
```

- `verified`: written and confirmed by read-back.
- `already-present`: identical content already existed, nothing written.
- `error`: failed or missing on read-back; show `error` to the human.

Exit code 0 means all items succeeded, 1 means at least one `error`, 2 means invalid input.
Report every non-`verified` result to the human; never retry silently.

### pr-comment-reply

Items: `{ "prUrl", "commentId", "body" }`, with `commentId` from `get-github-contents`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-comment-reply.ts --input <items.json>
```

A `review-comment` reply is anchored to the thread root, even when `commentId` is a reply.
`issue-comment` and `review-summary` have no threads, so the reply is a new PR comment.

### pr-comment-create

Items: `{ "prUrl", "body" }`. Posts a new general PR comment.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-comment-create.ts --input <items.json>
```

### pr-thread-resolve

Items: `{ "prUrl", "commentId" }`, any `review-comment` in the thread.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-thread-resolve.ts --input <items.json>
```

Only records with `can_resolve: true` can be resolved.

### issue-comment-create

Items: `{ "issueUrl", "body" }`. Posts a new comment on an issue (a PR URL is rejected).

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/issue-comment-create.ts --input <items.json>
```

### issue-update

Items: `{ "issueUrl", "expectedUpdatedAt", "title"?, "body"? }`, with at least one of `title` and
`body` and `expectedUpdatedAt` copied from `updatedAt` of `get-github-contents` `issue-get`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/issue-update.ts --input <items.json>
```

Compares the issue's current `updated_at` with `expectedUpdatedAt` and refuses with
`status: "error"` (message starts with `stale`) when the issue changed after it was read; read it
again and ask the human before retrying. Identical content returns `already-present`. A
`verified` result carries the new `updatedAt`.

### issue-create

Items: `{ "repoUrl", "title", "body" }` with `repoUrl` as `https://github.com/<owner>/<repo>`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/issue-create.ts --input <items.json>
```

Searches the repository for an issue (not a PR) with exactly the same title first and returns
`already-present` with its `url` and `number`, so a rerun never duplicates. A `verified` result
carries `url` and `number`. Labels, assignees and milestones are never set. Any title convention
(e.g. a prefix) is the caller's choice.

## Examples

**Input**: reply "Fixed in abc123" to `review-comment/12` on
`https://github.com/acme/widgets/pull/482` and resolve its thread (synthetic)

Runs `get-github-contents` Session setup, shows stage 1, writes
`[{"prUrl":"https://github.com/acme/widgets/pull/482","commentId":"review-comment/12","body":"Fixed in abc123"}]`,
shows stage 2, runs `pr-comment-reply.ts` then `pr-thread-resolve.ts` with the same file, and
reports both `verified` results.

## Edge Cases

- **Same reply run twice**: the second run returns `already-present` and posts nothing.
- **Thread already resolved**: `pr-thread-resolve.ts` returns `already-present`.
- **Partial batch failure**: other items still run; exit code is 1.

## Known Issues

- **Symptom:** resolving fails with `Could not resolve to a node` or a type error.
  **Cause:** `resolveReviewThread` needs the thread's GraphQL node id, not a REST comment id.
  **Fix:** use `pr-thread-resolve.ts`, which looks up the node id from the comment id.
- **Symptom:** a resolve or reply returns HTTP 403 `Resource not accessible`.
  **Cause:** the account lacks write or triage permission on the repository.
  **Fix:** report the permission gap, keep reply-only for that item, never retry the same call.
- **Symptom:** `issue-update` returns `stale: the issue changed after it was read`.
  **Cause:** someone edited the issue after `issue-get`; `updated_at` also moves on comments and labels.
  **Fix:** read again with `issue-get`, show the human what changed, and write only after a new confirmation.
- **Symptom:** `issue-create` creates a duplicate of an issue that exists.
  **Cause:** GitHub search indexes new issues with a delay of seconds to minutes, so a very recent twin is not found.
  **Fix:** wait and rerun, or ask the human to check the repository before a second create.
- **Symptom:** an issue write returns HTTP 403 or 404 on a repository the human can read.
  **Cause:** the account lacks write access, or the repository is archived or locked.
  **Fix:** report it as is; never retry the same call.
- **Symptom:** a reply to a reply fails with HTTP 422.
  **Cause:** GitHub accepts review replies only on the thread root.
  **Fix:** use `pr-comment-reply.ts`, which resolves the root before posting.

## Anti-Patterns

- **Mistake:** Posting before stage 2 because stage 1 was approved.
  **Why it happens:** Two prompts feel redundant for a small batch.
  **Instead:** Always show stage 2 with the final items unless the caller-confirmed rule applies.
- **Mistake:** Calling `gh api` by hand instead of the scripts.
  **Why it happens:** A single POST looks simpler than writing an input file.
  **Instead:** Use the scripts; they skip duplicates and verify by read-back.
- **Mistake:** Reporting success from a zero exit code of a raw `gh` write.
  **Why it happens:** `gh` normally fails loudly on errors.
  **Instead:** Trust only `verified` results from the scripts.

## References

- [`get-github-contents`](../get-github-contents/SKILL.md) -- session setup and reads; activated first.
- [`agentme-edr-127`](../../127-external-system-adapter-skills.md) -- contents skill rules.
- [`agentme-edr-005`](../../../principles/005-skill-scripts-and-composition.md) -- skill composition.
