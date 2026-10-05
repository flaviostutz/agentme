---
skill: get-azure-devops-contents
skill-version: "1.1.0"
---

## Test Scenarios

### Scenario 1: List and normalize PR threads

**Trigger / Input**

List comments of `https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029`,
with one fixed file thread holding a root and a reply, one active general thread and one
system vote comment.

**Expected Behaviour**

The skill checks `az account show`, runs `scripts/src/adapters/cli/pr-comments-list.ts --pr-url <url>` and
returns one JSON array in the shared record shape.

**Assertions**

- [ ] Skill runs `pr-comments-list.ts` instead of composing raw `az rest` reads by hand.
- [ ] Output marks both file-thread comments `status: "resolved"` with the reply's `in_reply_to` set to the root id.
- [ ] Output sets `path: null` for the general thread comment.
- [ ] Output omits the system vote comment and never emits a `review-summary` kind.

### Scenario 2: Read a work item with a legacy URL, attachments and links

**Trigger / Input**

Read `https://contoso.visualstudio.com/My%20Project/_workitems/edit/321`, a User Story with an
HTML description that mentions `https://wiki.example.com/spec`, one attachment that downloads
and one that returns HTTP 403.

**Expected Behaviour**

The skill runs `work-item-get.ts --work-item-url <url>` after Session setup and returns the work
item JSON read through `https://dev.azure.com/contoso`.

**Assertions**

- [ ] Skill accepts the legacy URL without asking the human to convert it.
- [ ] Skill runs `work-item-get.ts` instead of composing `az rest` or `curl` reads by hand.
- [ ] Output returns `project: "My Project"`, `rev` and `projectVisibility`.
- [ ] Output lists the downloaded file with a `path` under `.tmp/work-item-attachments/` and the failed one with an `error`.
- [ ] Output `links` contains the wiki URL.
- [ ] Skill rejects a PR URL for `work-item-get` with a usage error.

### Scenario 3: No session never triggers a curl or scrape fallback

**Trigger / Input**

`az account show` fails and no Azure DevOps PAT is stored in the keychain.

**Expected Behaviour**

The skill asks the human to run `az login` or store a PAT via `setup-secrets`, and reads
nothing until a session exists.

**Assertions**

- [ ] Skill never issues `curl` or another HTTP request to an Azure DevOps endpoint.
- [ ] Skill never fetches or parses the PR's HTML page.
- [ ] Skill never persists a PAT to disk or prints it.
