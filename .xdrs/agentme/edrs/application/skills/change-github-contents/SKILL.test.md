---
skill: change-github-contents
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: Reply to a reply is anchored to the thread root after two confirmations

**Trigger / Input**

Reply "Fixed" to `review-comment/12` on `https://github.com/acme/widgets/pull/482`, where
comment 12 is itself a reply to root comment 10.

**Expected Behaviour**

The skill runs `get-github-contents` Session setup first, shows stage 1 (System, Operation,
Fields, Estimated impact), shows stage 2 with the final item, then runs
`scripts/pr-comment-reply.js`, which posts with `in_reply_to=10` and returns `verified`.

**Assertions**

- [ ] Skill activates `get-github-contents` in prose before any write.
- [ ] Skill shows stage 1 and stage 2 confirmations and waits for each answer.
- [ ] Script posts the reply with `in_reply_to` set to root comment 10.
- [ ] Skill's confirmation question has a context line, states each option's consequence,
      prefixes one option with "(recommended)", and fills the question-UI fields.

### Scenario 2: Permission-denied resolve is reported, not retried

**Trigger / Input**

`pr-thread-resolve.js` returns `status: "error"` with `HTTP 403: Resource not accessible` for
one item of a two-item batch.

**Expected Behaviour**

The skill reports the permission gap for that item, keeps the other item's result, and does
not run the same resolve again.

**Assertions**

- [ ] Skill reports the 403 error to the human in plain words.
- [ ] Skill does not retry the failed resolve call.
- [ ] Skill reports the other item's `verified` result unchanged.

### Scenario 3: Caller-confirmed batch skips the skill's own prompts

**Trigger / Input**

`resolve-pr-comments` already showed stage 1 and stage 2 for three replies and activates this
skill with exactly those three items.

**Expected Behaviour**

The skill runs Session setup, runs `pr-comment-reply.js` once with all three items and
returns the per-item results without asking again.

**Assertions**

- [ ] Skill asks no new confirmation for the caller-confirmed items.
- [ ] Skill runs the script once with all three items in one input file.
