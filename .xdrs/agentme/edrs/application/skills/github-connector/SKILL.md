---
name: github-connector
description: >
  Base connector providing authentication, read access, and write access to GitHub pull
  requests and their comments via the gh CLI. Pure I/O -- no triage logic, no business
  decisions. Activate when an agent or skill (such as resolve-pr-comments) needs to fetch or
  post PR comments, resolve review threads, or check out a PR branch on GitHub.
metadata:
  author: flaviostutz
  version: "1.1"
---

## Overview

Reusable authentication and connection skill for GitHub pull requests, per
[agentme-edr-127](../../127-external-system-adapter-skills.md) rule 06 (connector naming).
Wraps the `gh` CLI -- GitHub's own supported API client -- so callers never construct raw
REST/GraphQL calls or handle GitHub-specific auth themselves. Contains no business logic (per
rule 05): it does not decide what a comment means, what action to take, or when to reply --
it only reads and writes data and normalizes it to the shape consumed by
[`resolve-pr-comments`](../../../principles/skills/resolve-pr-comments/SKILL.md).

## Instructions

### Authentication check

1. Verify the `gh` CLI is installed (`gh --version`); if missing, ask the human whether to
   install it now via the appropriate package manager for their OS (e.g. `brew install gh`
   on macOS). Only run the install command after explicit confirmation; if the human
   declines or the install fails, report the install requirement and stop.
2. Run `gh auth status`. If authenticated, proceed -- this is the preferred path since `gh`
   manages its own session token securely (per agentme-edr-124's least-exposure principle)
   and needs no secret handling here.
3. If not authenticated, run
   `gh auth login --hostname github.com --git-protocol https --web` instead of bare
   `gh auth login` -- these flags answer the "Where do you use GitHub?", "preferred
   protocol?", and "how would you like to authenticate?" prompts non-interactively so the
   human is never asked them. `gh` still asks one local yes/no question ("Authenticate Git
   with your GitHub credentials?"); accept its default (`Y`) automatically, since it only
   wires the existing `gh` credential helper into git and needs no human input. The only
   step that still requires the human is the one-time code / "Press Enter to open ... in
   your browser" prompt that follows -- `gh` stores the resulting token in its own secure
   storage once that completes. Never ask the human for a raw PAT and never read, request,
   or feed a token to `gh` directly. Do not proceed with a write operation until
   `gh auth status` reports an authenticated session.
4. Never substitute `gh` with a direct HTTP call (`curl`, `fetch`, or any other HTTP client)
   against the GitHub REST/GraphQL API, and never scrape the PR's rendered HTML page as a
   workaround -- this applies to reads as much as writes, and applies even when the target
   data is public. If `gh` is missing or unauthenticated, stop and resolve that first (steps
   1-3 above); do not degrade to an alternative retrieval method to route around it.

### Reading data

All read commands are plain `gh` invocations; none require confirmation (per
agentme-edr-127 rule 04, read-only operations are exempt from the HITL confirmation step
only -- they are not exempt from the CLI-only channel). Every read below MUST go through
`gh`; never construct the equivalent call with `curl`/another HTTP client, and never fetch
or scrape the PR's rendered web page as a substitute. When running `gh` from an automated
or non-interactive shell, prefix calls with `GH_PAGER=cat` (see Known Issues) so output is
never lost to a pager.

- PR metadata: `gh pr view <n> --json title,body,baseRefName,headRefName,url,state,isCrossRepository,headRepositoryOwner,headRepository`
- Issue-level (top) comments: `gh api repos/{owner}/{repo}/issues/{n}/comments`
- Review (file/line) comments: `gh api repos/{owner}/{repo}/pulls/{n}/comments`
- Review summaries: `gh api repos/{owner}/{repo}/pulls/{n}/reviews`
- Thread resolution state (REST does not expose this): `gh api graphql` with a
  `reviewThreads` query on the PR, reading `isResolved` and each thread's comment node ids.

Normalize every fetched item to the shared record shape (`id`, `kind`, `status`, `can_reply`,
`can_resolve`, `path`, `line`, `content`, `author`, `in_reply_to`, `diff_hunk`, `url`):
- `kind` is `"issue-comment"`, `"review-comment"`, or `"review-summary"`.
- `status` is `"resolved"` when the GraphQL thread lookup marks it resolved, else `"open"`.
  GitHub has no `wontfix`/`closed` state of its own -- `resolve-pr-comments` tracks those
  locally.
- `can_resolve` is `true` only for `"review-comment"` items belonging to a resolvable
  thread; `"issue-comment"` and `"review-summary"` are never resolvable -- set `false`.
- `in_reply_to` is resolved to the thread's top-level/root comment id, never an intermediate
  reply, so replies always thread correctly.
- If the reply target is a reply-to-a-reply, resolve `in_reply_to` up to the root comment id
  first (GitHub only allows replying to the root of a review thread).
- `diff_hunk` is taken verbatim from the `diff_hunk` field already present on each
  `"review-comment"` item returned by the review-comments read command above -- no extra
  fetch needed. Null for `"issue-comment"` and `"review-summary"` items, since neither is
  file/line-scoped.
- `url` is taken verbatim from the `html_url` field already present on every issue-comment,
  review-comment, and review object returned by the read commands above -- no extra fetch
  needed for any `kind`.

### Writing data

Before any write below, show the mandatory confirmation (per agentme-edr-127 rule 04):
**System** (`owner/repo` + PR number), **Operation**, **Fields** (exact verbatim text to
post), **Estimated impact** (visible to PR participants, triggers notifications). Wait for
explicit confirmation; never proceed on an assumed "yes."

- Reply to an issue-level comment: `gh api repos/{owner}/{repo}/issues/{n}/comments -f body="..."`
- Reply to a review thread: `gh api repos/{owner}/{repo}/pulls/{n}/comments -f body="..." -F in_reply_to=<root-comment-id>`
- Post a new general PR comment: `gh pr comment <n> --body "..."`
- Resolve a review thread: `gh api graphql` with a `resolveReviewThread` mutation, passing
  the thread's GraphQL node id (not the REST numeric id -- these are different identifier
  spaces; see Known Issues).
- Check out the PR branch: `gh pr checkout <n>`.

### Constraints

- MUST use the `gh` CLI for every read and write handled by this connector -- never fall
  back to `curl`, another raw HTTP client, or scraping the PR's HTML page, even when `gh` is
  missing, unauthenticated, rate-limited, or erroring, and even when the target data is
  public.
- MUST stop and follow the Authentication check steps above when `gh` cannot complete a
  request, instead of silently degrading to an alternative retrieval method.

## Examples

**Input**: fetch all comments for `https://github.com/acme/widgets/pull/482`

Runs `gh pr view 482 --json ...` for metadata, then the three read commands above for
issue-comments, review-comments, and reviews, then one `gh api graphql` call for thread
resolution state, and returns a single normalized list.

**Input**: reply to review comment id `review-comment/91234` and mark it resolved

Shows the mandatory confirmation summary first. On explicit "yes," posts the reply via
`gh api repos/{owner}/{repo}/pulls/{n}/comments -F in_reply_to=91234`, then resolves the
thread via the GraphQL mutation using that comment's thread node id.

## Edge Cases

- **PR from a fork**: `headRepositoryOwner`/`headRepository` differ from the base repo;
  checkout and branch comparisons must use the fork's remote, not the base repo's.
- **Review-summary comments**: never resolvable and never file/line-scoped; `path`/`line`
  are always null and `can_resolve` is always `false`.
- **Reply-to-a-reply**: GitHub only supports replying to a thread's root comment; always
  resolve `in_reply_to` up to the root before posting.

## Known Issues

- **Symptom:** `resolveReviewThread` mutation fails with a "could not resolve to a node"
  error even though the comment id is valid.
  **Cause:** the mutation requires the review thread's GraphQL node id, not the numeric
  REST comment id or the numeric review id -- these are three different identifier spaces.
  **Fix:** always fetch the thread's node id via the `reviewThreads` GraphQL query first,
  and cache the numeric-id-to-node-id mapping per PR fetch. Verify the exact mutation shape
  via `gh api graphql` introspection before first use in a new environment.
- **Symptom:** posting a reply or resolving a thread returns HTTP 403 despite `gh auth
  status` showing a valid session.
  **Cause:** the authenticated account lacks write/triage permission on the repository (for
  example, an outside collaborator with read-only access).
  **Fix:** degrade to reply-only where permitted, report the permission gap plainly, and
  never retry the same call silently.
- **Symptom:** any `gh api` call returns HTTP 404 for a repo the human insists exists.
  **Cause:** the authenticated token lacks the `repo` (or fine-grained equivalent) scope, so
  GitHub reports a private resource as not found rather than as forbidden.
  **Fix:** report this distinction explicitly and ask the human to re-run
  `gh auth refresh -s repo` rather than assuming the PR truly does not exist.
- **Symptom:** repeated calls start failing with HTTP 403 and a rate-limit message.
  **Cause:** GitHub's REST/GraphQL rate limits were exceeded, often from re-fetching the
  full comment list too frequently in one session.
  **Fix:** space out calls and reuse the already-fetched result within a session; never
  silently retry in a tight loop.
- **Symptom:** an agent fetched PR metadata, comments, or diffs via `curl`/`api.github.com`
  or by scraping the PR's rendered HTML page instead of using `gh`.
  **Cause:** `gh` was missing or unauthenticated (e.g. `gh auth status` reported not logged
  in), and the agent treated the unauthenticated public REST API or the rendered PR page as
  an acceptable substitute since the target data was technically public.
  **Fix:** never substitute `gh` with a direct HTTP call or a page scrape, regardless of
  whether the data is public. Stop at the Authentication check step, report the missing or
  failed `gh` session plainly, and wait for the human to install or authenticate `gh` before
  retrying the same read or write through `gh`.
- **Symptom:** a `gh api`/`gh pr view` read command run from an automated shell appears to
  hang or return no captured output at all, even though `gh` itself succeeded.
  **Cause:** `gh` falls back to `$PAGER` (commonly `less`) for output it thinks may be
  interactive; this switches the terminal to its alternate screen buffer, and content shown
  there is not part of normal scrollback, so an automated caller never sees it -- piping
  through `| cat` alone does not reliably prevent this.
  **Fix:** prefix every `gh` invocation with `GH_PAGER=cat` (e.g.
  `GH_PAGER=cat gh api repos/{owner}/{repo}/issues/{n}/comments`) when running non-
  interactively, which disables `gh`'s pager unconditionally.

## References

- [`resolve-pr-comments`](../../../principles/skills/resolve-pr-comments/SKILL.md) -- consumes this connector's normalized output.
- [`agentme-edr-127`](../../127-external-system-adapter-skills.md) -- external system adapter skill rules (connector naming, Known Issues format, HITL-before-write).
- [`agentme-edr-124`](../../124-secrets-management.md) -- credential storage and retrieval.
