---
skill: github-connector
skill-version: "1.2.0"
---

## Test Scenarios

### Scenario 1: Fetch and normalize all comment kinds for a PR, happy path

**Trigger / Input**

Fetch all comments for `https://github.com/acme/widgets/pull/482`, a PR with one issue-level
comment, two review (file/line) comments in one resolved thread, and one review-summary.

**Expected Behaviour**

The connector: (1) confirms `gh auth status` is authenticated; (2) runs the PR metadata
read; (3) runs the issue-comments, review-comments, and reviews read commands; (4) runs one
`gh api graphql` call to read thread resolution state; (5) returns a single normalized list
where the issue-level comment has `kind: "issue-comment"` and `can_resolve: false`, the two
review comments have `kind: "review-comment"`, `status: "resolved"`, and `can_resolve:
true`, and the review-summary has `kind: "review-summary"` and `can_resolve: false`.

**Assertions**

- [ ] Output normalizes every fetched item to the shared record shape (id, kind, status,
      can_reply, can_resolve, path, line, content, author, in_reply_to).
- [ ] Output sets `can_resolve: false` for the issue-comment and the review-summary items.
- [ ] Output sets `status: "resolved"` for the two review comments in the resolved thread,
      derived from the GraphQL thread lookup rather than the REST response alone.
- [ ] Connector never branches its own logic on business meaning of comment content.

### Scenario 2: Reply-to-a-reply resolves to the thread root before posting

**Trigger / Input**

Post a reply targeting a review comment that is itself a reply (not the root) within its
thread.

**Expected Behaviour**

Before posting, the connector resolves `in_reply_to` up to the thread's root comment id
(GitHub only accepts replies anchored to the root), shows the mandatory System/Operation/
Fields/Estimated impact confirmation using the resolved root id, and only posts via
`gh api repos/{owner}/{repo}/pulls/{n}/comments -F in_reply_to=<root-id>` after explicit
confirmation.

**Assertions**

- [ ] Connector resolves `in_reply_to` to the thread's root comment id, not the intermediate
      reply id, before constructing the write call.
- [ ] Connector shows the mandatory confirmation (System, Operation, Fields, Estimated
      impact) before posting.
- [ ] Connector does not post before receiving explicit human confirmation.

### Scenario 3: Permission-denied write degrades to reply-only, no silent retry

**Trigger / Input**

A resolve-thread write (`gh api graphql` `resolveReviewThread` mutation) returns HTTP 403
because the authenticated account lacks triage permission on the repository.

**Expected Behaviour**

Per the Known Issues entry for this symptom, the connector reports the permission gap
plainly to the caller, does not retry the same call, and continues to allow a reply-only
write path for that comment (an already-successful or subsequent reply post is unaffected).

**Assertions**

- [ ] Connector reports the permission error explicitly rather than failing silently.
- [ ] Connector does not silently retry the failed resolve call.
- [ ] Connector still allows a reply-only write for the same comment.

### Scenario 4: No GitHub session available halts before any write

**Trigger / Input**

`gh auth status` reports not logged in.

**Expected Behaviour**

The connector runs `gh auth login --hostname github.com --git-protocol https --web`
(non-interactive except for the one local git-credential yes/no, which the connector
auto-accepts on its default) so the human is only asked to complete the browser/device-code
step, and does not attempt any write operation until `gh auth status` reports an
authenticated session. Read-only operations that do not require authentication (if any) are
unaffected.

**Assertions**

- [ ] Connector does not attempt a write operation without an authenticated `gh` session.
- [ ] Connector runs `gh auth login` with `--hostname`/`--git-protocol`/`--web` rather than
      bare `gh auth login`, so the human is not asked the host/protocol/method questions.
- [ ] Connector never asks for, reads, or feeds `gh` a raw PAT/token directly.

### Scenario 5: gh unavailable or unauthenticated never triggers a curl/scrape fallback

**Trigger / Input**

Fetch PR metadata, comments, and diff for `https://github.com/acme/widgets/pull/482` while
`gh auth status` reports not logged in (or `gh` is not installed).

**Expected Behaviour**

The connector does not issue any direct `curl`/HTTP request to `api.github.com`,
`github.com`, or a `.diff`/`.patch` endpoint, and does not fetch or parse the PR's rendered
HTML page as a substitute -- even though the target repository and PR are public. Instead it
follows the Authentication check steps, reports the missing/failed `gh` session plainly, and
halts every read and write until `gh auth status` reports an authenticated session.

**Assertions**

- [ ] Connector does not issue a `curl` or other raw HTTP request to any GitHub endpoint as
      a substitute for `gh`.
- [ ] Connector does not fetch or parse the PR's HTML page as a scraping fallback.
- [ ] Connector halts reads and writes and prompts for `gh` installation/`gh auth login`
      rather than degrading to an alternative retrieval method.
