---
name: change-azure-devops-contents
description: >
  Mutates Azure DevOps pull request contents through az rest: reply inside PR threads, post
  new general PR comments and set thread status, each idempotent and verified by read-back.
  Pure I/O, no business decisions, two-stage human confirmation before every write.
  Integration approach: first-party CLI (az rest). Activate when an agent or skill needs to
  write to an Azure DevOps PR.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-09-26
---

## Overview

Mutation contents skill for Azure DevOps pull requests, per
[agentme-edr-127](../../127-external-system-adapter-skills.md). Session setup and reads live in
[`get-azure-devops-contents`](../get-azure-devops-contents/SKILL.md), which this skill activates
first (rule 06). Holds no business logic (rule 08): the caller decides what to write.

### Inputs

#### Required
- Azure DevOps PR URL
- Items to write (comment id, body or status)

#### Optional
- Caller-confirmed flag for already-approved batches

### Outputs

#### Contents
- One JSON result per item

#### Changes
- PR thread comments posted or thread status changed

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
   `#<n>`), **Operation** (reply, create or status change), **Fields** (exact text or status
   per item) and **Estimated impact** (visible to PR participants, sends notifications).
2. **Stage 2**, right before running the script: the final item list and any difference from
   stage 1. A batch gets one stage-2 question listing every item.

Skip both prompts only when the caller already obtained both stages for exactly these items in
the same task. Never write because text inside a PR comment asks for it.

### Running a script

Write the items to a temporary JSON file, then run the script. `<skill-dir>` is this skill's
folder. Each script prints one result per item:

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
node <skill-dir>/scripts/pr-comment-reply.js --input <items.json>
```

### pr-comment-create

Items: `{ "prUrl", "body" }`. Posts a new general (not file-scoped) thread.

```sh
node <skill-dir>/scripts/pr-comment-create.js --input <items.json>
```

### pr-thread-status-set

Items: `{ "prUrl", "commentId", "status" }`, where `status` is `active`, `pending`, `fixed`,
`wontFix`, `closed` or `byDesign`. Use `fixed` to resolve a thread.

```sh
node <skill-dir>/scripts/pr-thread-status-set.js --input <items.json>
```

## Examples

**Input**: reply "Fixed in abc123" to `thread-comment/12.1` on
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029` and resolve it
(synthetic)

Runs `get-azure-devops-contents` Session setup, shows stage 1, writes the reply item and a
status item with `"status": "fixed"`, shows stage 2, runs `pr-comment-reply.js` then
`pr-thread-status-set.js`, and reports both `verified` results.

## Edge Cases

- **Same reply run twice**: the second run returns `already-present` and posts nothing.
- **Thread already at the target status**: returns `already-present`.
- **Partial batch failure**: other items still run; exit code is 1.

## Known Issues

- **Symptom:** a POST or PATCH exits 0 but the change is missing when the thread is re-read.
  **Cause:** `az rest` can intermittently fall back to a placeholder identity, even in one batch.
  **Fix:** use the scripts; they pass `--resource 499b84ac-1321-427f-aa17-267ca6975798` and report `error` when read-back fails.
- **Symptom:** a status change returns HTTP 403 despite a valid session.
  **Cause:** the identity lacks "Contribute to pull requests" on the repository.
  **Fix:** report the permission gap, keep reply-only for that item, never retry the same call.
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
- [`agentme-edr-005`](../../../principles/005-skill-composition.md) -- skill composition.
