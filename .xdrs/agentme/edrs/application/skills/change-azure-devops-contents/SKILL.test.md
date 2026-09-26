---
skill: change-azure-devops-contents
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: Reply and resolve after two confirmations

**Trigger / Input**

Reply "Fixed" to `thread-comment/12.1` on
`https://dev.azure.com/contoso/Widgets/_git/widgets-api/pullrequest/1029` and resolve the thread.

**Expected Behaviour**

The skill runs `get-azure-devops-contents` Session setup first, shows stage 1 (System,
Operation, Fields, Estimated impact), shows stage 2, then runs `pr-comment-reply.js` and
`pr-thread-status-set.js` with `"status": "fixed"`, and reports both results.

**Assertions**

- [ ] Skill activates `get-azure-devops-contents` in prose before any write.
- [ ] Skill shows stage 1 and stage 2 confirmations and waits for each answer.
- [ ] Skill resolves the thread with `pr-thread-status-set.js` and status `fixed`.
- [ ] Skill's confirmation question has a context line, states each option's consequence,
      prefixes one option with "(recommended)", and fills the question-UI fields.

### Scenario 2: Write missing on read-back is reported as an error

**Trigger / Input**

`pr-comment-reply.js` returns `status: "error"` with "missing on read-back" and exit code 1,
after `az rest` exited 0.

**Expected Behaviour**

The skill reports the failed item to the human and never claims it was posted.

**Assertions**

- [ ] Skill reports the item as not posted, quoting the error.
- [ ] Skill does not retry the write without a new human decision.

### Scenario 3: Caller-confirmed batch skips the skill's own prompts

**Trigger / Input**

`resolve-pr-comments` already showed stage 1 and stage 2 for two replies and activates this
skill with exactly those items.

**Expected Behaviour**

The skill runs Session setup, runs `pr-comment-reply.js` once with both items and returns the
per-item results without asking again.

**Assertions**

- [ ] Skill asks no new confirmation for the caller-confirmed items.
- [ ] Skill runs the script once with both items in one input file.
