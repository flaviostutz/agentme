# Story template and persistence

Detail for step 6 of `refine-user-story`: the story template, its caps, and how the refined story is
persisted. Read this file before writing the story.

## Template

Each fact appears once; other sections point to it and never restate it. Only Title and User Story
are required. Every other section is written only when it holds content no other section holds;
never write N/A or fill a section to complete the template. The template follows `agentme-bdr-401`.

```
**Story ID:** userstory-NNN-slug
**Status:** to-be-refined   (only while a Pending Questions section exists)

## Title
[<10 words, outcome-focused]

## User Story
[<50 words] As a [role], I want to [action], so that [benefit].

## Details
[Prose <30 words and/or <8 bullets of <30 words each. Adds context, rules, constraints, answered
 decisions and accepted defaults ("assumption") the user story does not say; never repeats it.
 Diagrams, examples and exercises shown to the person during the run follow the bullets as labelled blocks.]
- [rule, behaviour, constraint, measurable need, blocking dependency or assumption]

## Notes                  (optional; at most 6 bullets, each <40 words)
- [Source, link, reuse target, contact or hint that changes how the builder starts.]

## Acceptance Criteria
[<4 checkbox lines, each <12 words. Only delivery aspects that decide whether the story can be
 closed, concrete and easy to check, saying what can be found where.]
- [ ] [delivery result, e.g. "Pipeline fails if F1 score < 0"]

## Out of Scope            (optional; at most 3 bullets, each <15 words)
- [subtle thing people would really doubt, e.g. "Integration with the team metrics board"]

## Pending Questions       (only while the story is not ready; roles only, <100 words)
- OQn (for: <role>, one-way): [question in that role's wording]. Why: [<20 words]. Proposed: [default with cited source, or "none"]

**Epic initiative:** [NNN-epic-slug.md](../NNN-epic-slug.md)    (omit when no initiative is active)
```

Template guidance lives in these brackets only; never save notices or instructions into the story.

### Details

- State what the user story leaves open: rules, boundaries, data or systems involved, why it matters.
- Keep every answered one-way decision as a bullet with a one-line why. Mark each accepted two-way
  default "(assumption)".
- A rule a policy mandates is a bullet that names the policy path.
- A diagram, example or exercise discussed or shown to the person during the run, and not rejected by
  them, is kept at the end of Details as a labelled block (`Diagram:`, `Examples:`, `Exercises:`) and does
  not count toward the Details caps. Diagram: ASCII, at most 20 lines and 70 columns. Examples: 2-3
  short ones with synthetic data, one an edge case. Exercise: a short worked walk-through from input to
  expected result. Never add one the person did not see.

### Acceptance Criteria

- Delivery aspects only: what is merged, deployed, measured, presented or recorded, and where it can be
  found (pipeline run, dashboard, work item comment, document). Behaviour and rules belong to Details.
- Never write the team's standard Definition of Done (reviewed, tested, deployed) or a repeat of Details.
- Discovery and design stories name each verifiable result and where it is stored.

### Out of Scope

- Write only subtle boundaries people would really ask about. Never write "anything not defined here" or
  other obvious exclusions.

### Notes

- Source and next step: where it is (file link, component, policy id or URL), what it provides, and
  what to do with it ("extend", "follow", "do not use", "add next to"). Example: "`tools/test_calculator.py`
  has a fake connector returning a preset response. Extend it to serve recorded answers per case."
- Facts and pointers only; decisions belong to Details or Acceptance Criteria. Something missing (no
  data, no environment) is a Details bullet, an Acceptance Criteria line or a Pending Question, not a
  note. Say when a file was listed but not opened.
- Links found in the source item or story, API and data contracts, mockups and screenshots that cannot
  be written as text, and named contacts (only a real person the source names) also go here.

### Legacy stories

A saved story with sections from an earlier template (Context, Behaviour, Constraints, Detailed Specs,
Implementation Tips, Diagram, Definition of Done) keeps them on resume and is rewritten to this template
only when the person asks.

### Length

Never pad to reach a cap; shorten rather than cut meaning.

## New epic initiative

Used by step 1 when the human chooses to create an epic.

- Derive the epic slug by kebab-casing the title, keeping at most 7 words.
- Determine the epic NNN by scanning `[scope]/bdrs/operations/initiatives/` for existing initiative
  files and using the next available number (start at 001).
- Create `.xdrs/[scope]/bdrs/operations/initiatives/NNN-epic-slug.md` with the sections required by
  `_core-adr-policy-007`:

```markdown
# [scope]-bdr-initiative-NNN: [Epic Title]

## Executive Summary
[To be completed.]

## Context and Problem Statement
[one-sentence objective collected above]

## Proposed Solution
[To be completed.]

Expected end date: YYYY-MM-DD

## Milestones

### Milestone 1: [First Feature Name]
Owner: TBD
Due date: TBD

**Key tasks:**
```

## Epic / Feature / User Story structure

- **Epic**: an initiative document at `[scope]/bdrs/operations/initiatives/NNN-epic-slug.md`, a group of
  features toward one objective (1-12 months). Heading `# [scope]-bdr-initiative-NNN: [Epic Title]`.
- **Feature**: a `### Milestone N: [Feature Name]` section in the epic (2 weeks to 6 months).
- **User story**: a key task in a Milestone, always a link:
  `- [Brief description]{.assets/userstory-NNN-slug.md}`. Pending stories append ` — pending` to the
  link text and have `**Status:** to-be-refined`. Each story takes under 2 weeks; larger ones are split.
- **Story file**: `.assets/userstory-NNN-slug.md` in the epic's `.assets/` folder. NNN restarts at 001
  per epic; file names are lowercase.

## Initiative document integration

After the story is written, persist it according to the active initiative context.

**When an XDRS initiative doc is active:**
1. Determine NNN and slug:
   - **Placeholder story**: take them from the placeholder's `**Story ID:**` line.
   - **New story**: use the next NNN in the initiative's `.assets/` (list existing `userstory-NNN-*.md`,
     increment the highest; start at 001) and kebab-case the title, at most 7 words.
2. Write `.assets/userstory-NNN-slug.md` with the template, including the `**Story ID:**` line. A ready
   story has no `**Status:**` line. While a Pending Questions section exists keep
   `**Status:** to-be-refined`.
3. Update the task link in the Milestone: when ready, change `[Brief description — pending]` to
   `[Refined Story Title]` (same path); otherwise keep ` — pending`. For new stories insert
   `- [Refined Story Title]{.assets/userstory-NNN-slug.md}` (with ` — pending` when not ready).
4. When splitting, create a placeholder for each non-chosen slice at `.assets/userstory-NNN-slug.md`
   with `**Story ID:**`, `**Status:** to-be-refined`, `## Title` (preliminary), `## Notes from intake`
   (split rationale, relationship to the current story, known API or business details) and `## Related`
   linking the current story. Number them after the highest existing NNN and insert
   ` — pending` task links in the same Milestone (or a new one for a distinct Feature). Do not offer
   TODO.md for deferred slices.
5. Add the back-link at the bottom: `**Epic initiative:** [NNN-epic-slug.md](../NNN-epic-slug.md)`.

**When no XDRS initiative doc is active:** ask where to save the story (default
`userstory-NNN-slug.md` at the workspace root). With deferred stories, ask whether to add them to an
existing epic, create one, or save to `TODO.md` per `agentme-edr-001`.

### Deferred items

For deferred slices or risks without an initiative, offer TODO.md entries per `agentme-edr-001` rules
04-05 (status `open`; `prompt` merging the slice's objective, behaviour and known context plus a
resume prompt naming user-story refinement; `deferred reason` <30 words).
