---
skill: 400-pr-owner-assistant
skill-version: "2.3.0"
---

## Test Scenarios

### Scenario 1: End-to-end GitHub PR review, happy path

**Trigger / Input**

"Let's review this PR: https://github.com/acme/widgets/pull/482" (run from a clean, up to
date local clone of `acme/widgets`, which has 2 open comments).

**Expected Behaviour**

The skill: (1) parses the URL host as `github.com` and activates `github-connector`; (2)
Phase 1 fetches PR #482 metadata and every comment via the connector's read commands; (3)
Phase 2 confirms the local repo matches `acme/widgets` and offers to check out the PR
branch; (4) Phase 3 creates `.tmp/review-pr-482.md` with one templated section per open
comment, fully populated before any question is asked -- writing the summary automatically
without asking for confirmation, rendering each section's `source` field as a clickable
markdown link to the matching file in the local checkout (never a provider URL),
populating `source-lines` with the commented line(s) plus padding read from the checked-out
file, `diff-hunk-raw` verbatim from the connector, `author-raw` verbatim from the connector,
`comment-url` verbatim from the connector, `possible-user-intention` (an under-20-word,
silently generated read of the author's likely concern) alongside the existing `type`, and
`possible-follow-ups` (2-4 candidate next actions), and recording the verbatim comment text
and any existing replies under `comment-raw`/`replies-raw`; (5) Phase 4 opens noting every
drafted item is only ever sent later, during Phase 5 -- never mid-walkthrough -- then walks
each of the 2 comments one at a time, rendering its full focus card (comment, code,
criticality/type/possible-user-intention, possible-follow-ups) before asking the human to
choose an action for that single comment; (6) for each, drafts the reply/fix text and shows
the mandatory confirmation titled with the comment's short title, author, and exact reply
text, persisting it as `pending-reply: drafted` once confirmed -- nothing is sent at this
point; (7) Phase 5 gathers both now-drafted comments, renders a consolidated preview table
(id, title, action, resolve-on-apply) followed by each row's exact draft text, runs the
pre-flight commit/push gate (finding the worktree and remote already clean, so it proceeds
silently), then applies both together via a single apply-all batch confirmation -- resolving
comment 1's thread as requested -- and reports the final summary by action taken and send
status.

**Simulated Human Responses**
1. "Yes, check out the PR branch."
2. "For comment 1: confirm criticality, action = reply. Yes, resolve the thread once
   applied." (accepts the drafted text unedited)
3. "For comment 2: confirm criticality, action = fix. Use this reply text instead:
   'Renamed per your suggestion, thanks!'" (replaces the drafted text with free text)
4. (Phase 5) "Apply all now."

**Assertions**

- [ ] Skill activates `github-connector` because the URL host is `github.com`.
- [ ] Skill does not skip Phase 2 workspace validation before creating the tracking file.
- [ ] Skill creates `.tmp/review-pr-482.md` with a templated section per fetched open
      comment only -- already-resolved comments are never recorded.
- [ ] Skill fully populates every comment's section -- including `possible-follow-ups` and
      `diff-hunk-raw` -- before Phase 4 asks its first triage question.
- [ ] Skill writes the tracking file's PR summary automatically, without asking the human to
      confirm or edit it first.
- [ ] Skill renders each section's `source` field as a markdown link to the matching local
      file, relative to the tracking file's own location (file:line-range text for
      file-scoped comments, `(PR conversation)` text with no link otherwise) -- never a link
      to the provider's website.
- [ ] Skill asks about exactly one comment at a time in Phase 4, never batching multiple
      comments' triage questions into a single ask.
- [ ] Skill shows the mandatory confirmation -- titled with the comment's short title,
      author, and exact reply text -- before persisting each draft in Phase 4, and neither
      applies nor posts anything during Phase 4.
- [ ] Skill persists both comments as `pending-reply: drafted` at the end of Phase 4, with
      neither one sent to the provider yet.
- [ ] Skill's Phase 5 renders a consolidated preview table (one row per drafted comment:
      id, title, action, resolve-on-apply) followed by each row's exact draft text shown
      below the table.
- [ ] Skill's Phase 5 runs the pre-flight commit/push gate and, finding the worktree and
      remote clean, proceeds straight to applying without asking anything about git.
- [ ] Skill applies both comments' drafts together in a single apply-all batch confirmation
      in Phase 5, resolving comment 1's thread as requested.
- [ ] Skill suffixes comment 1's reply -- accepted unedited -- with
      `(pr-owner-assistant skill - using defaults)` before posting it.
- [ ] Skill suffixes comment 2's reply -- replaced with human-supplied free text -- with
      `(pr-owner-assistant skill - guided)` before posting it.
- [ ] Skill records the section's original comment text under `comment-raw` and any existing
      thread replies under `replies-raw`, never under the old `comment`/`replies` names.
- [ ] Skill populates `source-lines` with the commented line(s) padded +-3 lines, each line
      prefixed with its absolute line number.
- [ ] Skill populates `author-raw` and `comment-url` verbatim from the connector.
- [ ] Skill populates `possible-user-intention` with an under-20-word inference silently,
      with no dedicated confirmation prompt of its own.

### Scenario 2: Suggested-fix detection drives accept/evolve/decline framing

**Trigger / Input**

Phase 3 populates 3 comments, each containing a fenced `suggestion` block in `comment-raw`:
comment 1 proposes a correct rename with no side effects; comment 2 proposes a fix that is
right in direction but leaves an edge case unhandled; comment 3 proposes a change that would
silently break an unrelated caller.

**Expected Behaviour**

Phase 3 extracts each `suggested-fix` verbatim from its fenced block and records a
`suggested-fix-assessment` with rationale: `accept-as-is` for comment 1, `evolve-with-changes`
for comment 2, `not-recommended` for comment 3. In Phase 4, each focus card renders the
`suggested-fix`/`suggested-fix-assessment` pair right after `diff-hunk-raw`/`source-lines`.
For comment 1, the human applies the suggestion verbatim as a `fix` with no inline code
comment (the rename is self-evident, no rationale needed). For comment 2, the human applies
an evolved fix that also handles the edge case, and the skill adds a short inline code
comment at the changed lines explaining why the fix goes beyond the original suggestion.
For comment 3, the human declines with `wontfix`, and the skill's drafted rationale
explains why the suggestion isn't safe to apply, plus a short inline code comment at the
affected lines pointing back to that rationale.

**Simulated Human Responses**
1. "For comment 1: action = fix, apply the suggestion as-is."
2. "For comment 2: action = fix, but also handle the empty-input case the suggestion
   missed."
3. "For comment 3: action = wontfix -- that suggestion would break the other caller of this
   function."

**Assertions**

- [ ] Skill records a `suggested-fix` verbatim from each comment's fenced `suggestion`
      block, independent of which connector fetched it.
- [ ] Skill records `suggested-fix-assessment: accept-as-is` for comment 1,
      `evolve-with-changes` for comment 2, and `not-recommended` for comment 3, each with a
      short rationale.
- [ ] Skill renders `suggested-fix` and `suggested-fix-assessment` in the focus card right
      after `diff-hunk-raw`/`source-lines`, for all 3 comments.
- [ ] Skill applies comment 1's fix verbatim with no added inline code comment, since the
      rationale is self-evident.
- [ ] Skill adds a short inline code comment at comment 2's changed lines explaining why the
      fix evolves beyond the original suggestion.
- [ ] Skill adds a short inline code comment at comment 3's affected lines explaining why
      the suggested fix was declined, matching the `wontfix` rationale.

### Scenario 3: Phase 5 preview table, apply-all batch, and the commit/push gate

**Trigger / Input**

Phase 5 begins with 3 comments at `pending-reply: drafted` (2 `reply`, 1 `fix`). The local
worktree has one uncommitted change and 2 local commits not yet on the remote tracking
branch. The human chooses apply-all; the connector reports a transient failure applying the
2nd item only.

**Expected Behaviour**

Phase 5 renders the consolidated preview table (3 rows) with each row's exact draft text
shown below it, then runs the pre-flight git check. Finding both the uncommitted change and
the 2 unpushed commits, it shows a reminder that other participants won't see this code
until pushed, advises the human to add/commit/push manually -- never running any git command
itself -- and waits for explicit confirmation before applying anything. Once confirmed, it
applies item 1 successfully, hits the transient failure on item 2 (reporting it plainly
without losing item 1's already-applied state), and continues on to apply item 3
successfully.

**Simulated Human Responses**
1. "Apply all now."
2. "I've committed and pushed -- go ahead."

**Assertions**

- [ ] Skill renders all 3 items in the preview table with exact draft text shown below it,
      before asking how to proceed.
- [ ] Skill's pre-flight git check detects both the uncommitted change and the 2 unpushed
      local commits, and shows a reminder plus advice to add/commit/push manually.
- [ ] Skill never runs `git add`, `git commit`, or `git push` itself, regardless of what the
      check finds.
- [ ] Skill waits for explicit human confirmation after the reminder before applying any
      item.
- [ ] Skill's mid-batch failure on item 2 does not discard or reapply item 1's
      already-applied result.
- [ ] Skill continues on to apply item 3 after item 2's failure, and reports a per-item
      outcome (applied, applied, failed) at the end.
