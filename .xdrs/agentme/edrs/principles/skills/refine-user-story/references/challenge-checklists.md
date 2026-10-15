# Challenge checklists (step 4, silent)

Run these on the draft without showing them. A check that finds nothing is not reported. Findings go
through the door rule: a two-way finding becomes a researched default (a Details bullet marked "assumption", shown
in the review defaults list); a one-way finding becomes a question, or a Pending Question with an owner
role when the person cannot answer.

## Which checks run

| Nature of the story | Checks |
|---|---|
| Product behaviour (user-facing) | scope items, user angles, readiness |
| Engineering (API, data, infra, tests) | scope items, implementer angles, user angles that still apply (error feedback, trust) |
| Discovery or design | scope items, readiness; Acceptance Criteria name each verifiable activity result and where it is found |

Add implementer angles when the story is engineering or the person answers engineering questions. Skip angles that do not apply; do not invent
questions to fill them. Investigate deeper only one-way findings; for two-way ones pick the default and move on.

## Scope-item checks

For every Details bullet and Acceptance Criteria line, ask silently:

1. **Completeness**: are trigger, input, output and observable result clear enough to build without guessing?
2. **Edge cases**: errors, empty states, boundaries, retries, duplicates, concurrency not yet captured?
3. **Constraints**: does it imply or conflict with a contract, data model, performance budget or auth model?
4. **Attachments**: would a mockup, screenshot or document make it unambiguous? Ask for that artifact specifically.
5. **Specs**: external APIs, data contracts, doc links, contacts or reuse targets found? Record them in
   Notes; otherwise leave Notes out.

Also check consistency: no two lines contradict each other, terminology is stable, every line is testable
by someone who never saw the code.

## User angles (9)

1. Journey completeness: every step from trigger to completion and what follows.
2. Pain point: removes the root cause or only a symptom.
3. Emotional experience: initiating, waiting, feedback, errors.
4. Mental model: where users are surprised or must adapt.
5. Value clarity and timing: perceivable immediately or delayed.
6. Accessibility and inclusion: abilities, languages, devices, literacy.
7. Edge users: first-time, power, error-recovering, time-pressed.
8. Trust and safety: privacy, error recovery, data handling.
9. Learnability: finishable without documentation.

## Implementer angles (8)

1. Verifiable: each Acceptance Criteria line checkable by someone who never saw the code, with where to look.
2. Error and edge paths beyond the happy path.
3. Blocking dependencies and startability: decisions, access, environments, ordering.
4. Functional dependencies: APIs, systems, teams, with contract, SLA, owner.
5. Non-functional needs: performance, scale, availability, accessibility. A measurable one MUST be a
   Details bullet, and an Acceptance Criteria line when it is a delivery check (for example a failing pipeline).
6. Security: authentication, authorization, sensitive data, input validation, compliance. Usually one-way.
7. Independent releasability: ships without another story; any coupling explicit.
8. Cold dry run: an engineer receiving the story with no briefing finds where to start without wrong
   assumptions. This is the final integration check for engineering stories.

## Door tag

Test: can the decision be undone cheaply, by whom, without data loss or an external commitment?
One-way: public APIs and contracts, data model and migrations, irreversible data changes, security,
privacy, compliance, legal or pricing copy, external commitments and SLAs, rollout without rollback,
persisted user-visible names. Two-way: UI wording and layout, defaults, thresholds, flag-guarded
behaviour, ordering, tone.

## Examples and notes

- Examples: for the 1-3 outputs most likely to be misunderstood (messages, screen copy, payloads, exports),
  add 2-3 short labelled examples including one edge case, in Details. Synthetic data
  only. Mark one illustrative when its exact content may change.
- Notes: at most 6 bullets, each under 40 words, each naming a source and a next step, none repeating another
  Notes line or holding a decision; a listed-but-unopened file is labelled as such.

## Readiness (run at the finish)

Check silently against the final story; ask only for what is missing.

1. Vertical: end-to-end complete, no half-slice that silently assumes parallel work.
2. Size: one person, roughly 2-3 days (see size criteria).
3. Engineering-ready: enough to start architecture without business clarification.
4. External systems documented where they exist (APIs, fields, formats, constraints).
5. User context present: what the user does with it, with concrete examples where useful.
6. Scope boundary explicit: what is included, out of scope, unchanged.
7. Testable lines, error paths, blockers, dependencies, NFRs, security, releasability (engineering stories).
8. Optional sections earn their place: Notes and Out of Scope hold only content no other section holds; an
   Acceptance Criteria line never restates Details or the team's generic Definition of Done.
9. No open decision remains except Pending Questions with an owner role.

## Size criteria

Too large when two or more are true: more than about 8 distinct Details bullets; multiple independent
user outcomes each releasable alone; three or more qualitatively different flows; several actor groups
experiencing the feature in non-overlapping ways. Propose 2-4 vertical slices with a boundary rationale;
never split by technical layer.
