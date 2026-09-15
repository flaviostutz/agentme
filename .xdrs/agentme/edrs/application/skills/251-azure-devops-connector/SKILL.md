---
name: 251-azure-devops-connector
description: >
  Base connector providing authentication, read access, and write access to Azure DevOps
  pull requests and their comment threads via the az CLI. Pure I/O -- no triage logic, no
  business decisions. Activate when an agent or skill (such as pr-owner-assistant) needs to
  fetch or post PR thread comments, change thread status, or check out a PR branch on Azure
  DevOps.
metadata:
  author: flaviostutz
  version: "1.1"
---

## Overview

Reusable authentication and connection skill for Azure DevOps pull requests, per
[agentme-edr-127](../../127-external-system-adapter-skills.md) rule 06 (connector naming).
Wraps the `az` CLI (with the `azure-devops` extension) -- Azure DevOps's own supported API
client -- plus `az rest` for the handful of operations the extension does not expose as a
dedicated subcommand. Contains no business logic (per rule 05): it only reads and writes
data and normalizes it to the shape consumed by
[`400-pr-owner-assistant`](../../../principles/skills/400-pr-owner-assistant/SKILL.md).

This is a base connector skill (number range 250-299).

## Instructions

### Authentication check

1. Verify the `az` CLI is installed (`az --version`); if missing, ask the human whether to
   install it now via the appropriate package manager for their OS (e.g. `brew install
   azure-cli` on macOS). Only run the install command after explicit confirmation; if the
   human declines or the install fails, report the install requirement and stop.
2. Verify the `azure-devops` extension is present; if missing, install it with
   `az extension add --name azure-devops` (auto-installs on first use in most `az` versions,
   but check explicitly rather than assuming).
3. Run `az account show`. If authenticated, proceed -- prefer `az login`'s own session over
   handling a token directly.
4. If not authenticated, check the OS keychain for a stored Azure DevOps PAT per
   [agentme-edr-124](../../124-secrets-management.md) rather than any `.env` file, hardcoded
   value, or shell profile export. If found, export it only transiently as
   `AZURE_DEVOPS_EXT_PAT` for the current command invocation -- never persist it to disk.
5. If no session and no stored PAT exist, prompt the human to run `az login` interactively
   or to store a PAT in the keychain first, per agentme-edr-124's `setup-secrets` pattern.
   Do not proceed with a write operation without one of these. Unlike `gh auth login`, bare
   `az login` already opens the browser directly with no preceding host/protocol/method
   questions, so no extra flags are needed here to keep it non-interactive.
6. Set the default organization/project once per session
   (`az devops configure --defaults organization=<url> project=<project>`) to shorten
   subsequent commands.
7. Never substitute `az`/`az rest` with a direct HTTP call (`curl`, `fetch`, or any other
   HTTP client) against the Azure DevOps REST API, and never scrape the PR's web UI as a
   workaround -- this applies to reads as much as writes, and applies even when the target
   data looks read-only. If `az`, the `azure-devops` extension, or a valid session/PAT is
   missing, stop and resolve that first (steps 1-5 above); do not degrade to an alternative
   retrieval method to route around it.

### Reading data

All read commands are exempt from HITL confirmation (per agentme-edr-127 rule 04, read-only
operations need no confirmation -- but they are not exempt from the CLI-only channel).
Every read below MUST go through `az`/`az rest`; never construct the equivalent REST call
with `curl`/another HTTP client, and never fetch or scrape the PR's web UI as a substitute.

- PR metadata: `az repos pr show --id <n> --output json`
- All comment threads (Azure DevOps has no separate "list comments" call -- threads are the
  unit of data and already include every comment and their status):
  `az rest --method GET --uri "https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{n}/threads?api-version=7.1"`
  There is no dedicated `az repos pr` subcommand for threads -- `az rest` is required for both
  reads and writes; verify this generic-URI capability with `az rest --help` and a smoke-test
  GET before first use in a new environment.

Normalize every thread's comments to the shared record shape (`id`, `kind`, `status`,
`can_reply`, `can_resolve`, `path`, `line`, `content`, `author`, `in_reply_to`, `diff_hunk`,
`url`):
- `id` is `"thread-comment/<threadId>.<commentId>"` -- Azure DevOps ids are scoped per PR, not
  global, so always keep the PR number alongside when persisting.
- `kind` is always `"thread-comment"` -- Azure DevOps has no separate review-summary concept;
  never emit a `"review-summary"` kind for this provider.
- `status` maps from the thread's `status` field: `"active"` -> `"open"`, `"fixed"` /
  `"closed"` -> `"resolved"`, `"wontFix"` -> `"wontfix"`, `"pending"` -> `"open"`.
- `path`/`line` come from `threadContext.filePath` and the relevant line range; when
  `threadContext` is `null`, this is a general (PR-level, not file-scoped) comment -- classify
  it as a general comment, not a parsing error.
- `can_reply` and `can_resolve` are `true` for any non-deleted comment in a non-deleted
  thread; Azure DevOps does not have GitHub's permission-driven resolve restriction in the
  same way, but a 403 on write still means `can_resolve` should be treated as `false` for
  that session (see Known Issues).
- `in_reply_to` is the thread's first comment id whenever the target is a reply within the
  same thread -- Azure DevOps threads are flat, so there is no root-vs-reply distinction to
  resolve.
- `diff_hunk` has no native equivalent in the Azure DevOps API -- `threadContext` exposes
  only a file path and line range, not a unified-diff-style hunk string. Leave `diff_hunk`
  null rather than fabricating one; `pr-owner-assistant` degrades to relying on
  `source-lines` alone in that case, exactly as it does for a general (non-file-scoped)
  comment.
- `url` has no direct field in the thread-comment response either. Synthesize a best-effort
  permalink from the PR's own web URL plus a `?discussionId=<threadId>` anchor (Azure
  DevOps' web UI convention for deep-linking to a thread); fall back to the PR's own URL
  with no anchor when this convention cannot be confirmed reliable for the target
  organization, rather than risking a broken or misleading link (see Known Issues).

### Writing data

Before any write below, show the mandatory confirmation (per agentme-edr-127 rule 04):
**System** (org/project/repo + PR number), **Operation**, **Fields** (exact verbatim text to
post), **Estimated impact** (visible to PR participants, triggers notifications). Wait for
explicit confirmation; never proceed on an assumed "yes."

- Reply within an existing thread:
  `az rest --method POST --uri ".../pullRequests/{n}/threads/{threadId}/comments?api-version=7.1" --body '{"content": "...", "parentCommentId": <id>}'`
- Post a new general (non-file-scoped) comment as a new thread:
  `az rest --method POST --uri ".../pullRequests/{n}/threads?api-version=7.1" --body '{"comments": [{"content": "..."}]}'`
- Change thread status (the resolve/won't-fix equivalent):
  `az rest --method PATCH --uri ".../pullRequests/{n}/threads/{threadId}?api-version=7.1" --body '{"status": "fixed"}'` (use `"wontFix"` or `"closed"` as appropriate instead of `"fixed"`).
- Check out the PR branch: `az repos pr checkout --id <n>`.

### Constraints

- MUST use `az`/`az rest` for every read and write handled by this connector -- never fall
  back to `curl`, another raw HTTP client, or scraping the PR's web UI, even when `az` is
  missing, unauthenticated, or erroring, and even when the target data looks read-only.
- MUST stop and follow the Authentication check steps above when `az` cannot complete a
  request, instead of silently degrading to an alternative retrieval method.

## Examples

**Input**: fetch all comments for
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029`

Runs `az repos pr show --id 1029` for metadata, then the single threads `az rest GET` call
above, and returns a single normalized list built from every thread's comments.

**Input**: reply to thread comment id `thread-comment/12.1` and set the thread to fixed

Shows the mandatory confirmation summary first. On explicit "yes," posts the reply via the
threads/comments `POST`, then updates thread status via the `PATCH` call.

## Edge Cases

- **Modern vs legacy URL formats**: recognize both
  `dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{id}` and
  `{org}.visualstudio.com/{project}/_git/{repo}/pullrequest/{id}` as valid Azure DevOps PR
  URLs; extract org/project/repo/id from either shape.
- **`threadContext` is `null`**: classify as a general PR-level comment, never as a parse
  failure.
- **PR-scoped ids**: never assume a thread or comment id is unique outside its PR; always
  carry the PR number alongside when the tracking file persists an id.

## Known Issues

- **Symptom:** the `azure-devops` extension has no `az repos pr comment` or `az repos pr
  thread` subcommand at all.
  **Cause:** the extension only covers a subset of the Git PR API; thread and comment
  operations were never added as first-class subcommands.
  **Fix:** always use `az rest` with the documented REST endpoints above for every thread
  and comment read or write; do not search for a nonexistent dedicated subcommand.
- **Symptom:** a thread that should be resolvable cannot be updated; the `PATCH` call returns
  HTTP 403 despite `az account show` showing a valid, logged-in session.
  **Cause:** the authenticated identity lacks the "Contribute to pull requests" permission
  on the repository.
  **Fix:** degrade to reply-only for that thread, report the permission gap plainly, and
  never retry the same call silently.
- **Symptom:** a fetched thread has no obvious "kind" like GitHub's review-summary.
  **Cause:** Azure DevOps genuinely has no equivalent concept -- every comment lives inside a
  thread.
  **Fix:** never emit a `"review-summary"` kind for this connector; always normalize to
  `"thread-comment"`.
- **Symptom:** an agent fetched PR metadata or thread comments via `curl`/direct REST calls
  or by scraping the PR's web UI instead of using `az`/`az rest`.
  **Cause:** `az` was missing, unauthenticated, or lacked the `azure-devops` extension, and
  the agent treated a direct unauthenticated REST call or the rendered PR page as an
  acceptable substitute since the target data looked read-only.
  **Fix:** never substitute `az`/`az rest` with a direct HTTP call or a page scrape. Stop at
  the Authentication check step, report the missing or failed `az` session plainly, and wait
  for the human to install, extend, or authenticate `az` before retrying the same read or
  write through `az`.
- **Symptom:** a synthesized comment permalink (`url`) 404s, or lands on the PR overview
  instead of the specific thread, when opened.
  **Cause:** Azure DevOps' web UI deep-link format for a specific thread
  (`?discussionId=<threadId>`) is a UI convention, not a documented, versioned part of the
  REST API, and can vary by organization or Azure DevOps version.
  **Fix:** verify the `?discussionId=<threadId>` anchor against a live PR in the target
  organization before relying on it; degrade to the PR's own URL with no anchor when
  uncertain, rather than guessing at a format that might mislead the human.

## References

- [`400-pr-owner-assistant`](../../../principles/skills/400-pr-owner-assistant/SKILL.md) -- consumes this connector's normalized output.
- [`agentme-edr-127`](../../127-external-system-adapter-skills.md) -- external system adapter skill rules (connector naming, Known Issues format, HITL-before-write).
- [`agentme-edr-124`](../../124-secrets-management.md) -- credential storage and retrieval.
- [`agentme-core-adr-003`](../../../../../agentme-core/adrs/principles/003-skill-numbering-ranges.md) -- skill numbering ranges (250-299 base connectors).
