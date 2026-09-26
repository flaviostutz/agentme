---
skill: get-azure-devops-contents
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: List and normalize PR threads

**Trigger / Input**

List comments of `https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029`,
with one fixed file thread holding a root and a reply, one active general thread and one
system vote comment.

**Expected Behaviour**

The skill checks `az account show`, runs `scripts/pr-comments-list.js --pr-url <url>` and
returns one JSON array in the shared record shape.

**Assertions**

- [ ] Skill runs `pr-comments-list.js` instead of composing raw `az rest` reads by hand.
- [ ] Output marks both file-thread comments `status: "resolved"` with the reply's `in_reply_to` set to the root id.
- [ ] Output sets `path: null` for the general thread comment.
- [ ] Output omits the system vote comment and never emits a `review-summary` kind.

### Scenario 2: Legacy visualstudio.com URL

**Trigger / Input**

Read metadata of `https://contoso.visualstudio.com/Widgets/_git/widgets-api/pullrequest/7`.

**Expected Behaviour**

The skill runs `pr-metadata-get.js`, which reads through `https://dev.azure.com/contoso`.

**Assertions**

- [ ] Skill accepts the legacy URL without asking the human to convert it.
- [ ] Output returns `number: 7` and the base and head branch names without `refs/heads/`.

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
