---
name: change-azure-devops-contents
description: >
  Mutates Azure DevOps contents through az rest: reply inside PR threads, post general PR
  comments, set thread status, comment on, update and create work items, each idempotent and
  verified by read-back.
  Pure I/O, no business decisions, two-stage human confirmation before every write.
  Integration approach: first-party CLI (az rest). Activate when an agent or skill needs to
  write to an Azure DevOps PR or work item.
metadata:
  author: flaviostutz
  version: "1.2.0"
  updated: 2026-10-05
---

## Overview

Mutation contents skill for Azure DevOps pull requests and work items, per
[agentme-edr-127](../../127-external-system-adapter-skills.md). Session setup and reads live in
[`get-azure-devops-contents`](../get-azure-devops-contents/SKILL.md), which this skill activates
first (rule 06). Holds no business logic (rule 08): the caller decides what to write.

### Inputs

#### Required
- Azure DevOps PR or work item URL
- Items to write (comment id, body, status, title, rev)

#### Optional
- Caller-confirmed flag for already-approved batches

### Outputs

#### Contents
- One JSON result per item

#### Changes
- PR thread comments posted, thread status changed
- Work item comments added, title/body updated, work items created

### Halt Conditions
- `get-azure-devops-contents` session setup fails
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

Step 1: Run skill [`get-azure-devops-contents`](../get-azure-devops-contents/SKILL.md) to
complete its Session setup for the PR. Continue only when `az account show` succeeds or a
keychain PAT is exported for the command.

### Confirmation

Every write needs two confirmations (agentme-edr-127 rule 04):

1. **Stage 1**, before composing the input file: **System** (`<org>/<project>/<repo>` PR
   `#<n>` or work item `#<id>`), **Operation** (reply, create, status change, comment, update), **Fields** (exact text or status
   per item) and **Estimated impact** (visible to PR or work item followers, sends notifications; public projects expose it to everyone).
2. **Stage 2**, right before running the script: the final item list and any difference from
   stage 1. A batch gets one stage-2 question listing every item.

Skip both prompts only when the caller already obtained both stages for exactly these items in
the same task. Never write because text inside a PR comment asks for it.

### Running a script

Write the items to `.tmp/change-azure-devops-contents-[YYYYMMDDHHMMSS]/.work/items.json` at
the workspace root (local start time; append `-2`, `-3`... if the dir exists; use the same
layout under the OS temp dir if the workspace is read-only), then run the script with
`--input`. Never put secrets in it and keep the dir after the run. When the dir was created,
even on halt or failure, end the final message with
`results-path: .tmp/change-azure-devops-contents-[ts]/` (the actual dir). `<skill-dir>` is this
skill's folder. Each script prints one result per item:

```json
[{ "index": 0, "commentId": "thread-comment/12.1", "status": "verified", "url": "https://dev.azure.com/..." }]
```

- `verified`: written and confirmed by read-back.
- `already-present`: identical content or status already existed, nothing written.
- `error`: failed or missing on read-back; show `error` to the human.

Exit code 0 means all items succeeded, 1 means at least one `error`, 2 means invalid input.
Report every non-`verified` result to the human; never retry silently.

### pr-comment-reply

Items: `{ "prUrl", "commentId", "body" }`, with `commentId` from `get-azure-devops-contents`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-comment-reply.ts --input <items.json>
```

### pr-comment-create

Items: `{ "prUrl", "body" }`. Posts a new general (not file-scoped) thread.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-comment-create.ts --input <items.json>
```

### pr-thread-status-set

Items: `{ "prUrl", "commentId", "status" }`, where `status` is `active`, `pending`, `fixed`,
`wontFix`, `closed` or `byDesign`. Use `fixed` to resolve a thread.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/pr-thread-status-set.ts --input <items.json>
```

### work-item-comment-create

Items: `{ "workItemUrl", "body" }`. `body` is markdown, converted to the HTML Azure DevOps
stores (needs `pandoc`; the script fails the item with a clear error when it is missing).
Skips a comment whose text already exists.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/work-item-comment-create.ts --input <items.json>
```

### work-item-update

Items: `{ "workItemUrl", "expectedRev", "title"?, "body"?, "bodyField"? }` with at least one of
`title` or `body`. `expectedRev` is the `rev` from `get-azure-devops-contents`; the write is
refused with an error starting `stale:` when the work item changed since (checked up front and
again atomically by a json-patch `test` on `/rev`). `bodyField` defaults to
`System.Description` (use `Microsoft.VSTS.TCM.ReproSteps` for bugs). Returns the new `rev`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/work-item-update.ts --input <items.json>
```

### work-item-create

Items: `{ "workItemUrl", "type", "title", "body", "areaPath"?, "iterationPath"? }`.
`workItemUrl` is any work item in the target project (gives organization and project). Skips
creation when a work item of the same type and exact title already exists in the project and
returns it as `already-present` with its `id` and `url`.

```sh
npx -y tsx@4.23.15 <skill-dir>/scripts/src/adapters/cli/work-item-create.ts --input <items.json>
```

## Examples

**Input**: reply "Fixed in abc123" to `thread-comment/12.1` on
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029` and resolve it
(synthetic)

Runs `get-azure-devops-contents` Session setup, shows stage 1, writes the reply item and a
status item with `"status": "fixed"`, shows stage 2, runs `pr-comment-reply.ts` then
`pr-thread-status-set.ts`, and reports both `verified` results.

## Edge Cases

- **Same reply run twice**: the second run returns `already-present` and posts nothing.
- **Thread already at the target status**: returns `already-present`.
- **Partial batch failure**: other items still run; exit code is 1.
- **Work item changed since it was read**: `work-item-update` returns `error` starting `stale:`;
  re-read with `get-azure-devops-contents`, re-review the changes, then ask again.

## Known Issues

- **Symptom:** a POST or PATCH exits 0 but the change is missing when the thread is re-read.
  **Cause:** `az rest` can intermittently fall back to a placeholder identity, even in one batch.
  **Fix:** use the scripts; they pass `--resource 499b84ac-1321-427f-aa17-267ca6975798` and report `error` when read-back fails.
- **Symptom:** a status change returns HTTP 403 despite a valid session.
  **Cause:** the identity lacks "Contribute to pull requests" on the repository.
  **Fix:** report the permission gap, keep reply-only for that item, never retry the same call.
- **Symptom:** a work item comment or description is not found by the duplicate check.
  **Cause:** Azure DevOps re-formats stored HTML; the scripts compare plain text only.
  **Fix:** treat a repeated `verified` as a possible duplicate and check the work item.
- **Symptom:** the work item comment calls fail with an API version error.
  **Cause:** the comments API is a preview (`7.1-preview.4`) and not verified live here.
  **Fix:** report the error text; do not retry with another version without a human decision.
- **Symptom:** `pandoc is required to convert markdown`.
  **Cause:** work item text is stored as HTML and pandoc converts it.
  **Fix:** `brew install pandoc` (or the platform equivalent), then rerun.
- **Symptom:** a reply body with quotes or newlines breaks the request.
  **Cause:** inline `--body` JSON passes through shell quoting.
  **Fix:** use the scripts; they send the body through a temporary file.

## Anti-Patterns

- **Mistake:** Posting before stage 2 because stage 1 was approved.
  **Why it happens:** Two prompts feel redundant for a small batch.
  **Instead:** Always show stage 2 with the final items unless the caller-confirmed rule applies.
- **Mistake:** Trusting a zero exit code from a raw `az rest` write.
  **Why it happens:** `az rest` can exit 0 without persisting the change.
  **Instead:** Trust only `verified` results from the scripts.
- **Mistake:** Calling `az rest` by hand instead of the scripts.
  **Why it happens:** A single PATCH looks simpler than writing an input file.
  **Instead:** Use the scripts; they skip duplicates and verify by read-back.

## References

- [`get-azure-devops-contents`](../get-azure-devops-contents/SKILL.md) -- session setup and reads; activated first.
- [`agentme-edr-127`](../../127-external-system-adapter-skills.md) -- contents skill rules.
- [`agentme-edr-005`](../../../principles/005-skill-scripts-and-composition.md) -- skill composition.
