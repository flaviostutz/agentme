---
skill: azure-devops-connector
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Fetch and normalize thread comments, happy path

**Trigger / Input**

Fetch all comments for
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029`, a PR with one
active file-scoped thread and one active general (PR-level) thread.

**Expected Behaviour**

The connector: (1) confirms `az account show` is authenticated; (2) runs
`az repos pr show --id 1029`; (3) runs the single `az rest --method GET` threads call
(there is no separate "list comments" call); (4) returns a normalized list where the
file-scoped thread's comment has non-null `path`/`line` and `kind: "thread-comment"`, and
the general thread's comment has null `path`/`line` and is still classified as a normal
`"thread-comment"`, both with `status: "open"`.

**Assertions**

- [ ] Output normalizes every fetched comment to the shared record shape (id, kind, status,
      can_reply, can_resolve, path, line, content, author, in_reply_to).
- [ ] Output maps the thread `status: "active"` field to the normalized `status: "open"`.
- [ ] Connector uses `az rest` for the threads read rather than searching for a dedicated
      `az repos pr` comment subcommand.

### Scenario 2: Null threadContext classified as a general comment, not an error

**Trigger / Input**

A fetched thread has `threadContext: null` in the raw API response.

**Expected Behaviour**

Per the Reading data normalization rule and the matching Edge Cases entry, the connector
classifies this thread's comment as a general PR-level comment (`path`/`line` set to null in
the normalized record) rather than treating the missing `threadContext` as a parsing failure
or skipping the comment.

**Assertions**

- [ ] Connector includes the comment in its normalized output with `path`/`line` set to null.
- [ ] Connector does not raise a parse error or silently drop the comment because of the
      null `threadContext`.

### Scenario 3: Thread status change writes via az rest PATCH with mandatory confirmation

**Trigger / Input**

Set thread id 12 on PR 1029 to resolved ("fixed") status after a fix was applied.

**Expected Behaviour**

The connector shows the mandatory System/Operation/Fields/Estimated impact confirmation
(naming org/project/repo + PR number and the target status), waits for explicit
confirmation, then issues
`az rest --method PATCH --uri ".../pullRequests/1029/threads/12?api-version=7.1" --body '{"status": "fixed"}'`.
No dedicated `az repos pr` subcommand is used for this operation.

**Assertions**

- [ ] Connector shows the mandatory confirmation before issuing the PATCH call.
- [ ] Connector does not issue the PATCH call before explicit human confirmation.
- [ ] Connector uses `az rest` rather than a nonexistent dedicated thread-status subcommand.

### Scenario 4: Legacy visualstudio.com URL parses the same as a modern dev.azure.com URL

**Trigger / Input**

`https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/1029` (legacy format)
versus `https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029` (modern
format) for the same underlying PR.

**Expected Behaviour**

The connector extracts the same org (`contoso`), project (`Widgets`), repo
(`widgets-api`), and PR id (`1029`) from either URL shape and proceeds identically from
that point on.

**Assertions**

- [ ] Connector extracts identical org/project/repo/PR-id values from both URL formats.
- [ ] Connector does not require the human to reformat a legacy URL before use.

### Scenario 5: az unavailable or unauthenticated never triggers a curl/scrape fallback

**Trigger / Input**

Fetch PR metadata and thread comments for
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029` while `az account
show` reports no session and no PAT is stored in the keychain (or `az`/the `azure-devops`
extension is not installed).

**Expected Behaviour**

The connector does not issue any direct `curl`/HTTP request against the Azure DevOps REST
API, and does not fetch or scrape the PR's web UI as a substitute -- even if the project
looks publicly reachable. Instead it follows the Authentication check steps, reports the
missing session/PAT or missing installation plainly, and halts every read and write until
`az account show` succeeds or a keychain PAT is available.

**Assertions**

- [ ] Connector does not issue a `curl` or other raw HTTP request to any Azure DevOps
      endpoint as a substitute for `az`/`az rest`.
- [ ] Connector does not fetch or scrape the PR's web UI as a fallback.
- [ ] Connector halts reads and writes and prompts for `az` installation/authentication
      rather than degrading to an alternative retrieval method.
