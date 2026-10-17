---
name: agentme-bdr-policy-401-epic-feature-user-story-planning
description: Defines how to organize software development project management work as epics, features, and user stories using XDRS initiative documents. Use when creating, reviewing, or navigating epic initiatives, feature milestones, or user story files.
apply-to: AI coding agents and developers managing software development work in projects that follow agentme standards
valid-from: 2026-08-28
---

# agentme-bdr-policy-401: Epic / Feature / User Story Planning

## Context and Problem Statement

Development teams need a lightweight, code-adjacent way to organize and track software development work. Without a standard structure, epics, features, and user stories are scattered across external tools or undocumented, making it difficult for agents and developers to discover what has been planned, what is pending, and what has been implemented.

How should software development project management work be organized within an XDRS-enabled workspace so that agents and developers can find, create, and refine work items alongside the code?

## Decision Outcome

**Epics are XDRS initiative documents. Features are Milestones inside those initiatives. User stories are key tasks linked to detail files.**

### Details

#### 01-epic-structure

An epic is a group of features that together achieve a well-defined objective. Epics typically span 1–12 months.

- Each epic MUST be represented as one XDRS initiative document of type BDR, placed at:
  `.xdrs/[scope]/bdrs/operations/initiatives/NNN-epic-slug.md`
- The initiative heading MUST follow the format: `# [scope]-bdr-initiative-NNN: [Epic Title]`
- NNN is the initiative's unique number within the `[scope]/bdrs/operations/initiatives/` namespace, assigned sequentially per `_core-adr-policy-007`.
- The slug MUST be lowercase, hyphen-separated, and descriptive (e.g., `001-epic-improve-checkout.md`).
- Each epic initiative MUST include all required sections from `_core-adr-policy-007`: Executive Summary, Context and Problem Statement, Proposed Solution (with Expected end date), and Milestones.
- Epic initiatives are ephemeral and MUST be deleted after the epic is fully implemented, per `_core-adr-policy-007`.

#### 02-feature-as-milestone

A feature is a specific activity, tool, or functionality that contributes to the epic's objective. Features typically span 2 weeks to 6 months.

- Each feature MUST be represented as one `### Milestone N: [Feature Name]` section inside the epic initiative.
- One Milestone per Feature; do not combine unrelated features into a single Milestone.
- Milestone sections MUST follow the structure defined in `_core-adr-policy-007`:
  - Owner, Due date, Description, optional Acceptance checklist, Key tasks, optional Risks.

#### 03-user-story-as-key-task

A user story is a unit of work within a Feature that delivers perceivable value to a specific audience. User stories MUST be completable in less than 2 weeks. Stories estimated to exceed 2 weeks MUST be split into smaller independent stories.

- Each user story MUST appear as a key task entry inside its parent Milestone's `**Key tasks:**` list, always as a markdown link to its detail file.
- **Pending (not yet refined):** `- [Brief description — pending]{.assets/userstory-NNN-slug.md}` — file has `**Status:** to-be-refined`
- **Refined:** `- [Story title]{.assets/userstory-NNN-slug.md}` — no status field in the file
- NNN is local to the epic initiative's `.assets/` folder; it restarts at 001 for each epic.
- Story slugs MUST be lowercase and hyphen-separated (e.g., `userstory-001-add-login-page`).

#### 04-user-story-detail-file

Each refined user story MUST have a detail file placed at:
`.xdrs/[scope]/bdrs/operations/initiatives/.assets/userstory-NNN-slug.md`

- NNN and slug MUST match the placeholder file that was refined (extracted from its `**Story ID:**` line). For new stories without a placeholder, use the next available NNN in `.assets/` and derive the slug by kebab-casing the story title to at most 7 words.
- The file MUST begin with a `**Story ID:** userstory-NNN-slug` line. A refined file has no `**Status:**` field; the absence of the status field indicates the story is complete. A story with a `## Pending Questions` section keeps `**Status:** to-be-refined`.

A **pending placeholder file** is created for every story added to the epic initiative before it is refined. It MUST contain:
```markdown
**Story ID:** userstory-NNN-slug
**Status:** to-be-refined

## Title
[preliminary description]

## Notes from intake
[Any context captured when this story was created: split rationale, relationship to other stories,
 known API details, contacts, or business rules discovered so far.]

## Related
- [Reason]: [userstory-NNN-other-story](.assets/userstory-NNN-other-story.md)
```

The detail file MUST follow this template. Only Title and User Story are required; every other section is optional and is omitted when it has no content or would repeat a fact held by another section. Never write N/A.

```markdown
**Story ID:** userstory-NNN-slug

## Title
[<10 words, outcome-focused]

## User Story
As a [role], I want to [action], so that [benefit].

## Details
[Prose <30 words and/or <8 bullets of <30 words each. Adds context, rules, constraints, answered decisions and accepted defaults the user story does not say; never repeats it.]
- [rule, behaviour, constraint, measurable need, blocking dependency or assumption]
[A diagram, example or exercise discussed or shown to the person during refinement is kept here as a labelled block and does not count toward the caps.]

## Notes
[optional - at most 6 bullets, <40 words each. Source, link, reuse target, contact or hint that changes how the builder starts.]
- [note]

## Acceptance Criteria
[<4 checklist lines, <12 words each. Only non-standard delivery aspects that decide whether the story can be closed, concrete and easy to check, saying what can be found where.]
- [ ] [delivery result, e.g. "Pipeline fails if F1 score < 0"]

## Out of Scope
[optional - at most 3 bullets, <15 words each. Only subtle boundaries people would doubt; never obvious exclusions.]
- [out-of-scope item]

## Pending Questions
[only while the story is not ready; roles only, <100 words.]
- [OQn (for: role): question]

**Epic initiative:** [NNN-epic-slug.md](../NNN-epic-slug.md)
```

The team's standard Definition of Done is not repeated in the story.

#### 05-readiness-requirement

A user story that lacks enough detail to begin architecture, planning, or implementation is not ready for implementation and MUST be re-refined before it is moved to in-progress.

- When integration or interface details were discovered during refinement (external APIs, data contracts, documentation links, contact names, reuse targets), they MUST be recorded in `## Details` when they constrain behaviour, and in `## Notes` when they are pointers.
- A story whose interfaces are unknown MUST carry a Pending Question instead of an empty section.
- `## Acceptance Criteria` MUST hold only delivery checks, concrete enough that anyone can decide whether the story can be closed.

#### 06-refinement-workflow

Stories MUST be refined using the `refine-user-story` skill. The skill:
- Detects active epic initiative documents and lists pending stories for selection.
- MUST run a structured refinement process including local research and interface/integration spec discovery.
- MUST write the resulting detail file and update the key task link in the initiative's Milestone.
- When a story is split, MUST create placeholder files for each deferred slice and add them as pending task links in the initiative.
- MUST show the original contents in chat first, and the final story at an approval gate before saving locally or writing back; nothing is stored or synced before the human answers it.
- MAY take a URL of the story to refine (GitHub issue, Azure DevOps work item, public web page) and, after the human confirms, write the refined story back to that source and create `[NEEDS REFINING]` placeholder items there for deferred slices; local tracking of deferred slices is kept regardless.

#### 07-ephemeral-lifecycle

Epic initiatives and their associated user story detail files are ephemeral artifacts. Once an epic is fully implemented:
- The epic initiative document MUST be deleted.
- The `.assets/` folder and all user story detail files MUST be deleted with it.
- The lasting outputs of an epic are the implemented code, decisions, skills, articles, and other artifacts produced during execution.

#### 08-okr-connection

Epics SHOULD be connected to one or more Tactical OKRs from `agentme-bdr-002` that represent the quarterly goals the epic is helping achieve.

- The OKR reference MUST be placed in a `## OKRs` section immediately after the heading line of the epic initiative document, listing each Tactical OKR by name or identifier.
- An epic without a linked Tactical OKR MUST document the reason in the `## OKRs` section (e.g., "No Tactical OKR defined for this quarter — tracked as a conscious decision").
- The relationship is many-to-many: one Tactical OKR MAY drive multiple Epics; one Epic MAY contribute to multiple Tactical OKRs.

## References

- [`_core-adr-policy-007`](../../../_core/adrs/principles/007-initiative-standards.md) — Initiative document standards: structure, lifecycle, and Milestone template
- [`agentme-bdr-002`](../principles/002-okr-framework.md) — OKR framework: Tactical OKR definition and epic connection rule
- [`refine-user-story`](../../edrs/principles/skills/refine-user-story/SKILL.md) — Refine user story skill: structured refinement workflow that produces output following this policy
