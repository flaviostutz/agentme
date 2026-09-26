---
skill: resolve-pr-comments
skill-version: "4.5.0"
---

## Test Scenarios

### Scenario 1: End-to-end GitHub PR review, happy path with guided mode and a Phase 6 edit

**Trigger / Input**

"Let's review this PR: https://github.com/acme/widgets/pull/482" (run from a clean, up to
date local clone of `acme/widgets`, which has 2 open comments).

**Expected Behaviour**

The skill: (1) parses the URL host as `github.com` and activates `get-github-contents`; (2)
Phase 1 fetches PR #482 metadata and every comment, then confirms the local repo matches
`acme/widgets` and offers to check out the PR branch; (3) Phase 2 calls `init` to write
`.tmp/review-pr-482.md`'s header before analysing anything, then computes each comment's
fields and calls `append-section` to write its section immediately, one comment at a time --
rendering each section's `source` field as a clickable markdown link to the matching file in
the local checkout (never a provider URL), `source-lines` with the commented line(s) plus
padding, `diff-hunk-raw`/`author-raw`/`comment-url` verbatim from the read skill,
`possible-user-intention` (an under-20-word, silently generated read of the author's likely
concern), and `possible-follow-ups` (2-4 candidate next actions); (4) Phase 3 renders the
2-row summary table and asks the literal numbered 4-way automation-level question -- the
human picks option 3 (guide all), so both comments use the guided flow; (5) Phase 4 walks
each comment one at a time, rendering its full focus card before asking the human to choose
an action, then drafts the reply/fix text, persists it as `pending-reply: drafted`, and shows
one FYI outcome line -- no confirmation question, nothing sent yet; (6) Phase 6 gathers both
now-drafted comments, renders a numbered consolidated preview table (`#`, `id`, title,
action, resolve-on-apply) followed by each row's exact draft text, and the human uses a
free-text instruction naming comment 2's `#` to change its reply text before applying both
together in a single apply-all batch confirmation -- resolving comment 1's thread as
requested -- then reports the final summary by action taken and send status.

**Simulated Human Responses**
1. "Yes, check out the PR branch."
2. (Phase 3) "3. I want to guide all comments solutions."
3. "For comment 1: confirm criticality, action = reply. Yes, resolve the thread once
   applied." (accepts the drafted text unedited)
4. "For comment 2: confirm criticality, action = fix." (drafted text left as-is at Phase 4)
5. (Phase 6) "For comment 2, reply with 'Renamed per your suggestion, thanks!' instead, then
   apply all now."

**Assertions**

- [ ] Skill activates `get-github-contents` because the URL host is `github.com`.
- [ ] Skill calls `init` to write the tracking file's header before analysing any comment,
      then calls `append-section` once per comment, immediately, one at a time -- never
      accumulating every section in memory until the end.
- [ ] Skill renders each section's `source` field as a markdown link to the matching local
      file, relative to the tracking file's own location -- never a link to the provider's
      website.
- [ ] Skill's Phase 3 renders a summary table (`#`, title, author, automation-suggestion,
      criticality) and asks the literal numbered 4-way automation-level question before
      Phase 4 asks anything else.
- [ ] Skill asks about exactly one comment at a time in Phase 4, posting each comment's full
      focus card as its own chat message before the action question.
- [ ] Skill's focus card shows the comment's location, states why the action needs the
      human's decision, lists each possible follow-up with its consequence, and shows a
      `Recommended action` with a one-line reason, while the human still chooses the action.
- [ ] Skill's action question fills the `vscode_askQuestions` question, message, option
      labels, and option descriptions with the title, context, actions, and consequences,
      not a bare "see above" reference to the focus card.
- [ ] Skill's Phase 6 apply confirmation states System, Operation, Fields, and Estimated
      impact before asking.
- [ ] Skill shows no confirmation question in Phase 4 -- only a one-line FYI outcome after
      each draft is persisted, for both comments.
- [ ] Skill's Phase 6 renders a numbered consolidated preview table (`#`, `id`, title,
      action, resolve-on-apply) followed by each row's exact draft text below the table.
- [ ] Skill accepts a Phase 6 free-text instruction naming comment 2's preview `#` to change
      its reply text before applying, persisting the change immediately.
- [ ] Skill applies both comments' drafts together in a single apply-all batch confirmation
      in Phase 6, resolving comment 1's thread as requested.
- [ ] Skill runs skill `change-github-contents` once with one JSON batch holding both
      replies and comment 1's resolve item, and marks each item applied only after a
      `verified` or `already-present` result.
- [ ] Skill suffixes both comment 1's reply (accepted as drafted) and comment 2's reply
      (changed at Phase 6) with the identical `(resolve-pr-comments - guided)` literal --
      no distinction between the two cases.
- [ ] Skill records the section's original comment text under `comment-raw` and any existing
      thread replies under `replies-raw`.
- [ ] Skill populates `possible-user-intention` with an under-20-word inference silently,
      with no dedicated confirmation prompt of its own.

### Scenario 2: Phase 3's "something else" free text drives a mixed fully-auto/guided run

**Trigger / Input**

Phase 2 populates 3 open comments: comment A (a simple, repetitive rename request with a
clean `suggested-fix`, classified `automation-suggestion: fully-auto`), comment B (a vague
architectural question, classified `automation-suggestion: guided`), and comment C (a minor
style nitpick, classified `automation-suggestion: fully-auto`, not mentioned in the human's
free text below). At Phase 3, the human answers option 4 with "automate everything, but
guide comment B".

**Expected Behaviour**

Phase 4 reaches comment A and, matching the free text's "automate everything", skips its
focus card and action question entirely: before starting, it shows one starting banner line
(`Starting comment A of 3 (fix): "<short title>".`), then auto-chooses `fix`, applies the
`suggested-fix` verbatim, defaults `resolve-on-apply` from `can_resolve` with no ask, drafts
and persists `pending-reply: drafted` immediately, and shows one brief outcome line
(`Auto-handled comment A (fix): ...`). The drafted text carries the
`(resolve-pr-comments - fully-auto)` suffix unconditionally. Comment B, explicitly named for
guidance, still gets its full focus card and action question exactly as documented, with the
human choosing `reply` and editing the drafted text, earning the
`(resolve-pr-comments - guided)` suffix. Comment C, not explicitly addressed by the free
text, follows its own `automation-suggestion` (`fully-auto`) and is handled the same
no-question way as comment A, each with its own starting banner and outcome line. Phase 6
later gathers all three comments together and requires the same explicit apply confirmation
for all of them -- no comment's fully-auto origin grants it a bypass of that gate.

**Simulated Human Responses**
1. (Phase 3) "4. Automate everything, but guide comment B."
2. "For comment B: action = reply. Use this reply text instead: 'We considered that
   approach; here's why we didn't take it...'" (replaces the drafted text with free text)
3. (Phase 6) "Apply all now."

**Assertions**

- [ ] Skill's Phase 3 renders the summary table and asks the literal numbered 4-way
      automation-level question before Phase 4 begins.
- [ ] Skill interprets the free-text option-4 answer against the numbered table, applying the
      no-question path to comments A and C and the guided path to comment B by name.
- [ ] Skill never shows comment A's or comment C's focus card or an action question for
      either, auto-choosing and applying each one's action with no human confirmation.
- [ ] Skill shows one starting banner line before each of comment A's and comment C's work
      begins, and one brief outcome line after, suffixing both with
      `(resolve-pr-comments - fully-auto)` unconditionally.
- [ ] Skill shows comment B's full focus card and action question, unaffected by comments A
      and C's no-question handling.
- [ ] Skill suffixes comment B's reply -- replaced with human-supplied free text -- with
      `(resolve-pr-comments - guided)`.
- [ ] Skill's Phase 6 requires the same explicit apply confirmation for all three comments --
      being drafted via the no-question path grants no bypass of Phase 6's gate.

### Scenario 3: Phase 2 writes the tracking file incrementally, surviving a mid-run interruption

**Trigger / Input**

A PR has 6 open comments. The session runs Phase 2 against a brand-new tracking file, then is
interrupted (e.g. context compaction or a cancelled session) immediately after the 4th
comment's section has been written, before the 5th comment's fields are computed.

**Expected Behaviour**

Phase 2 first calls `init` to durably write `.tmp/review-pr-<N>.md`'s header (PR link, raw
summary, auto-generated summary) before analysing any single comment. It then computes
comment 1's fields and calls `append-section` to write its section immediately, repeating
this one-comment-at-a-time for comments 2, 3, and 4 -- never holding more than one comment's
computed-but-unwritten section in memory at a time. When the interruption happens right
after comment 4's `append-section` call returns, comments 1-4 are already durably present on
disk. A fresh invocation re-reads the existing file, finds comments 1-4 already recorded (and
does not recompute or rewrite them), and resumes by computing and appending comments 5 and 6
the same incremental way.

**Simulated Human Responses**
(none -- Phase 2 asks nothing; the interruption and resume are session-level events, not
human decisions)

**Assertions**

- [ ] Skill calls `init` once, before computing any comment's fields, to write the tracking
      file's header (PR link, raw summary, auto-generated summary).
- [ ] Skill calls `append-section` once per comment, immediately after that comment's fields
      are computed, rather than batching multiple comments' sections into one write.
- [ ] Skill's on-disk tracking file already contains comments 1 through 4's full sections at
      the moment of interruption, before comment 5 is ever analysed.
- [ ] Skill's fresh invocation after the interruption re-reads the existing file and does not
      recompute or rewrite comments 1-4's already-written sections.
- [ ] Skill's fresh invocation computes and appends comments 5 and 6 the same
      one-comment-at-a-time way, completing the file.

