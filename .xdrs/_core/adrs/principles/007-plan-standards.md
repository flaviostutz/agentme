---
name: _core-adr-007-plan-standards
description: Defines plan document standards for describing problems, solutions, and activities. Use when creating or reviewing plans.
---

# _core-adr-007: Plan standards

## Context and Problem Statement

Teams need a structured way to describe a problem, propose a solution, and lay out the approach and activities needed to solve it. Without a standard format, planning documents drift in structure and completeness, making it hard to assess scope, track progress, and verify that a plan was fully implemented.

How should plans be structured and organized so they provide clear guidance for execution while remaining connected to the decisions, research, and skills they relate to?

## Decision Outcome

**Subject-level ephemeral plan documents co-located with XDRs**

Plans are Markdown documents placed inside a subject folder alongside decision records. They describe a problem, a proposed solution, and the approach to solve it. Plans have a clear start and end and a well-defined scope.

### Details

- Plans describe a problem (why), what we will do to solve the problem, and the approach and activities needed to solve it (how).
- Plans are NOT the source of truth. When a plan and an XDR disagree, the XDR takes precedence.
- Plans are ephemeral. They MUST be deleted after full implementation. The lasting outputs of a plan are actual actions or Decisions, Skills, Articles, Research documents, and other artifacts that result from execution.
- Plans may be used to implement a certain Decision. They may also use Research documents to help with the planning process. Articles may be written on top of a plan to give more context and connect more details present in other decisions and research to people involved in the plan.
- During the implementation of a plan, new Decisions, Articles, Skills, Research documents, and even other Plans may be created. Always link all related elements to each other.
- A plan can be high level, describing only one milestone, or more complex, describing a WBS (work breakdown structure) along with owners, multiple milestones in a tactical sequence, and checklists to verify completeness. Actual tasks performed by actors should normally be tracked in specialized software such as GitHub or Azure DevOps.
- The total time to deliver a plan should not be more than 2 years. If more time is needed, create a new plan later with what was learned.
- Plans MUST live under `plans/` inside the relevant subject folder: `.xdrs/[scope]/[type]/[subject]/plans/[number]-[short-title].md`
- The `[subject]` component MUST be one of the allowed subjects for the chosen type. The required list of allowed subjects per type is defined in `_core-adr-001`.
- Plans MUST include an `Expected end date:` field in ISO format (YYYY-MM-DD) inside the `## Proposed Solution` section.
- Always use lowercase file names.
- Never use emojis in plan content.
- Images and other local resource files referenced by a plan MUST live in `plans/.assets/` next to the plan files.

**Folder layout**

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        plans/
          [number]-[short-title].md
          .assets/
```

Examples:
- `.xdrs/_local/adrs/principles/plans/001-checkout-performance.md`
- `.xdrs/business-x/bdrs/product/plans/002-onboarding-redesign.md`

**Plan numbering**

- Each plan has a number unique within its `scope/type/subject/plans/` namespace.
- Determine the next number by checking the highest number already present in that namespace.
- Never reuse numbers of deleted plans. Gaps in the sequence are expected and allowed.

**Plan template**

All plans MUST follow this template:

```markdown
# [scope]-plan-[number]: [Short Title]

## Executive Summary

[Required. A summary of all sections below using bullet points, focused on the most important items. Under 500 words.]

## Context and Problem Statement

[Required. Describe clearly why we are executing this plan. What is the impact? Who is impacted? Why is this important? Under 200 words.
E.g.: Our checkout abandon rate is 50%, and it's increasing over time.]

## Proposed Solution

[Required. What we expect to achieve to solve the problem described above. Under 200 words.
E.g.: Reduce payment time in our App by 30% and fix the 3 most impactful bugs.]

Expected end date: YYYY-MM-DD

## Acceptance Criteria

[Optional. Used to make it clear what the expected result is and to create a way to verify when the goal is achieved. May include a short checklist. Under 100 words.]

## Approach

[Optional. High level description about how to achieve the result and the strategy used, including how to engage people, projects, organize the work, how to learn unknowns, deal with risks, and distribute workload. May include a WBS with the hierarchy of the work. Under 300 words.]

## Key Deliverables

[Optional. List of the main features, goods, artifacts, data, articles, skills, decisions, training, programs, events etc that will be important to achieve the expected result. Under 300 words.]

## Key Resources

[Optional. List of equipment, people, other project results, budget, areas or dependencies that need to be engaged or allocated for this plan to be implemented. Under 100 words.]

## Milestones

[Optional. List of goals to be followed along with an optional acceptance criteria, owner and due date. Each milestone may have a checklist used as acceptance criteria verification. Key tasks and risks can be listed as part of a milestone. Under 1000 words per milestone.]

### Milestone 1: [Title]
Owner: [name or team]
Due date: YYYY-MM-DD

[Description of the milestone goal.]

**Acceptance checklist:** [optional]
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Key tasks:**
- [Task description]

**Risks:** [optional]
- [Risk description] — Mitigation: [strategy]

## Risks Identified

[Optional. List of risks along with a short description and mitigation strategy. Under 1000 words.]

## References

- [Related XDR or artifact](relative/path.md) - Brief description of relevance
```

## Considered Options

* (REJECTED) **Inline planning in XDRs** — Embed planning details inside decision records.
  * Reason: Plans are ephemeral execution documents while XDRs are lasting decisions. Mixing them bloats XDRs and creates confusion about what to delete after execution.
* (CHOSEN) **Subject-level plans folder co-located with XDRs** — Keeps plans alongside the decisions they implement, with clear lifecycle expectations.
  * Reason: Consistent with how skills, articles, and research are organized. The explicit deletion requirement after implementation keeps the document base clean.

## References

- [_core-adr-001 - XDRs core](001-xdrs-core.md) - Framework elements: types, scopes, subjects, folder structure
- [_core-adr-004 - Article standards](004-article-standards.md) - Companion artifact type for synthetic views
- [_core-adr-006 - Research standards](006-research-standards.md) - Companion artifact type for exploratory evidence
- [006-write-plan skill](skills/006-write-plan/SKILL.md) - Step-by-step instructions for creating a new plan
