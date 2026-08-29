---
name: agentme-bdr-policy-401-epic-feature-user-story-planning
description: Defines how to organize software development project management work as epics, features, and user stories using XDRS plan documents. Use when creating, reviewing, or navigating epic plans, feature milestones, or user story files.
apply-to: AI coding agents and developers managing software development work in projects that follow agentme standards
valid-from: 2026-08-28
---

# agentme-bdr-policy-401: Epic / Feature / User Story Planning

## Context and Problem Statement

Development teams need a lightweight, code-adjacent way to organize and track software development work. Without a standard structure, epics, features, and user stories are scattered across external tools or undocumented, making it difficult for agents and developers to discover what has been planned, what is pending, and what has been implemented.

How should software development project management work be organized within an XDRS-enabled workspace so that agents and developers can find, create, and refine work items alongside the code?

## Decision Outcome

**Epics are XDRS plan documents. Features are Milestones inside those plans. User stories are key tasks linked to detail files.**

### Details

#### 01-epic-structure

An epic is a group of features that together achieve a well-defined objective. Epics typically span 1–12 months.

- Each epic MUST be represented as one XDRS plan document of type BDR, placed at:
  `.xdrs/[scope]/bdrs/operations/plans/NNN-epic-slug.md`
- The plan heading MUST follow the format: `# [scope]-bdr-plan-NNN: [Epic Title]`
- NNN is the plan's unique number within the `[scope]/bdrs/operations/plans/` namespace, assigned sequentially per `_core-adr-policy-007`.
- The slug MUST be lowercase, hyphen-separated, and descriptive (e.g., `001-epic-improve-checkout.md`).
- Each epic plan MUST include all required sections from `_core-adr-policy-007`: Executive Summary, Context and Problem Statement, Proposed Solution (with Expected end date), and Milestones.
- Epic plans are ephemeral and MUST be deleted after the epic is fully implemented, per `_core-adr-policy-007`.

#### 02-feature-as-milestone

A feature is a specific activity, tool, or functionality that contributes to the epic's objective. Features typically span 2 weeks to 6 months.

- Each feature MUST be represented as one `### Milestone N: [Feature Name]` section inside the epic plan.
- One Milestone per Feature; do not combine unrelated features into a single Milestone.
- Milestone sections MUST follow the structure defined in `_core-adr-policy-007`:
  - Owner, Due date, Description, optional Acceptance checklist, Key tasks, optional Risks.

#### 03-user-story-as-key-task

A user story is a unit of work within a Feature that delivers perceivable value to a specific audience. User stories MUST be completable in less than 2 weeks. Stories estimated to exceed 2 weeks MUST be split into smaller independent stories.

- Each user story MUST appear as a key task entry inside its parent Milestone's `**Key tasks:**` list, always as a markdown link to its detail file.
- **Pending (not yet refined):** `- [Brief description — pending]{.assets/userstory-NNN-slug.md}` — file has `**Status:** to-be-refined`
- **Refined:** `- [Story title]{.assets/userstory-NNN-slug.md}` — no status field in the file
- NNN is local to the epic plan's `.assets/` folder; it restarts at 001 for each epic.
- Story slugs MUST be lowercase and hyphen-separated (e.g., `userstory-001-add-login-page`).

#### 04-user-story-detail-file

Each refined user story MUST have a detail file placed at:
`.xdrs/[scope]/bdrs/operations/plans/.assets/userstory-NNN-slug.md`

- NNN and slug MUST match the placeholder file that was refined (extracted from its `**Story ID:**` line). For new stories without a placeholder, use the next available NNN in `.assets/` and derive the slug by kebab-casing the story title to at most 7 words.
- The file MUST begin with a `**Story ID:** userstory-NNN-slug` line. A refined file has no `**Status:**` field; the absence of the status field indicates the story is complete.

A **pending placeholder file** is created for every story added to the plan before it is refined. It MUST contain:
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

The detail file MUST follow this template:

```markdown
**Story ID:** userstory-NNN-slug

## Title
[max 10 words, outcome-focused]

## User Story
As a [role], I want to [action], so that [benefit].

## Scope
[max 200 words. List features, behaviors, screens, or services in scope.]
- [feature or behavior]

## Edge Cases
[optional — max 50 words. Known edge cases and expected handling.]
- [edge case — expected handling]

## Out of Scope
[optional — max 30 words.]
- [out-of-scope item]

## Constraints
[optional — max 30 words. Any rule, technology, regulatory, or business constraint that must be respected.]
- [constraint]

## Detailed Specs
[Required when any API, integration, or data detail was discovered. Mark N/A if none.
 A story lacking sufficient detail here is not ready for implementation.]
- [External API / integration: endpoint, method, payload, auth, behavior]
- [Data field: type, format, valid values, meaning, constraints]
- [Doc link: URL or file path — what it covers]
- [Contact: name/role — what they own or can clarify]
- [Process rule or business constraint not captured in Constraints above]

## Acceptance Criteria
- [ ] [verifiable outcome]

## Attachments
[highly desirable — screenshots, mockups, or diagrams illustrating the feature.]
- [attachment]

**Epic plan:** [NNN-epic-slug.md](../NNN-epic-slug.md)
```

#### 05-detailed-specs-requirement

A user story that lacks enough detail to begin architecture, planning, or implementation is not ready for implementation and MUST be re-refined before it is moved to in-progress.

- The `## Detailed Specs` section MUST be present in every user story detail file.
- When integration or interface details were discovered during refinement (external APIs, data contracts, documentation links, contact names), the section MUST be populated with those details.
- When no such details apply, the section MUST be explicitly marked `N/A`.
- A story with an empty or absent `## Detailed Specs` section is treated as not refined.

#### 06-refinement-workflow

Stories MUST be refined using the `151-refine-user-story` skill. The skill:
- Detects active epic plan documents and lists pending stories for selection.
- MUST run a structured 10-phase refinement process including interface/integration spec discovery.
- MUST write the resulting detail file and update the key task link in the plan's Milestone.
- When a story is split, MUST create placeholder files for each deferred slice and add them as pending task links in the plan.

#### 07-ephemeral-lifecycle

Epic plans and their associated user story detail files are ephemeral artifacts. Once an epic is fully implemented:
- The epic plan document MUST be deleted.
- The `.assets/` folder and all user story detail files MUST be deleted with it.
- The lasting outputs of an epic are the implemented code, decisions, skills, articles, and other artifacts produced during execution.

## References

- [`_core-adr-policy-007`](../../../_core/adrs/principles/007-plan-standards.md) — Plan document standards: structure, lifecycle, and Milestone template
- [`agentme-edr-skill-151`](../../edrs/principles/skills/151-refine-user-story/SKILL.md) — Refine user story skill: structured refinement workflow that produces output following this policy
