---
name: _core-adr-policy-007-initiative-standards
description: Defines initiative document standards for describing problems, solutions, and activities. Use when creating or reviewing initiatives.
apply-to: All initiative documents
valid-from: 2025-01-01
---

# _core-adr-policy-007: Initiative standards

## Context and Problem Statement

Teams need a structured way to describe a problem, propose a solution, and lay out the approach and activities needed to solve it. Without a standard format, initiative documents drift in structure and completeness, making it hard to assess scope, track progress, and verify that an initiative was fully implemented.

How should initiatives be structured and organized so they provide clear guidance for execution while remaining connected to the decisions, research, and skills they relate to?

## Decision Outcome

**Subject-level ephemeral initiative documents co-located with Policies**

Initiatives are Markdown documents placed inside a subject folder alongside policies. They describe a problem, a proposed solution, and the approach to solve it. Initiatives have a clear start and end and a well-defined scope.

### Details

- Initiatives describe a problem (why), what we will do to solve the problem, and the approach and activities needed to solve it (how).
- Initiatives are NOT the source of truth. When an initiative and a Policy disagree, the Policy takes precedence.
- Initiatives are ephemeral. They MUST be deleted after full implementation. The lasting outputs of an initiative are actual actions or Decisions, Skills, Articles, Research documents, and other artifacts that result from execution.
- Initiatives MAY be used to implement a certain Decision. They MAY also use Research documents to help with the planning process. Articles MAY be written on top of an initiative to give more context and connect more details present in other decisions and research to people involved in the initiative.
- During the implementation of an initiative, new Decisions, Articles, Skills, Research documents, and even other Initiatives MAY be created. All related elements MUST be linked to each other.
- An initiative can be high level, describing only one milestone, or more complex, describing a WBS (work breakdown structure) along with owners, multiple milestones in a tactical sequence, and checklists to verify completeness. Actual tasks performed by actors SHOULD be tracked in specialized software such as GitHub or Azure DevOps.
- The total time to deliver an initiative SHOULD NOT be more than 2 years. If more time is needed, create a new initiative later with what was learned.
- Initiatives MUST live under `initiatives/` inside the relevant subject folder: `.xdrs/[scope]/[type]/[subject]/initiatives/[number]-[short-title].md`
- The `[subject]` component MUST be one of the allowed subjects for the chosen type. The required list of allowed subjects per type is defined in `_core-adr-policy-001`.
- Initiatives MUST include an `Expected end date:` field in ISO format (YYYY-MM-DD) inside the `## Proposed Solution` section.
- File names MUST be lowercase.
- MUST NOT use emojis in initiative content.
- For diagram format preferences and non-Markdown asset rules, see [`_core-adr-policy-020`](020-media-and-asset-standards.md).

**Folder layout**

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        initiatives/
          [number]-[short-title].md
          .assets/
```

Examples:
- `.xdrs/_local/adrs/principles/initiatives/001-checkout-performance.md`
- `.xdrs/business-x/bdrs/product/initiatives/002-onboarding-redesign.md`

**Initiative numbering**

- Each initiative has a number unique within its `scope/type/subject/initiatives/` namespace.
- Determine the next number by checking the highest number already present in that namespace.
- MUST NOT reuse numbers of deleted initiatives. Gaps in the sequence are expected and allowed.

**Initiative template**

All initiatives MUST follow this template:

```markdown
# [scope]-[type]-initiative-[number]: [Short Title]

## Executive Summary

[Required. A summary of all sections below using bullet points, focused on the most important items. Under 500 words.]

## Context and Problem Statement

[Required. Describe clearly why we are executing this initiative. What is the impact? Who is impacted? Why is this important? Under 200 words.
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

[Optional. List of equipment, people, other project results, budget, areas or dependencies that need to be engaged or allocated for this initiative to be implemented. Under 100 words.]

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

- [Related Policy or artifact](relative/path.md) - Brief description of relevance
```

## Considered Options

* (REJECTED) **Inline planning in Policies** — Embed planning details inside policies.
  * Reason: Initiatives are ephemeral execution documents while Policies are lasting decisions. Mixing them bloats Policies and creates confusion about what to delete after execution.
* (CHOSEN) **Subject-level initiatives folder co-located with Policies** — Keeps initiatives alongside the decisions they implement, with clear lifecycle expectations.
  * Reason: Consistent with how skills, articles, and research are organized. The explicit deletion requirement after implementation keeps the document base clean.

## References

- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md) - Framework elements: types, scopes, subjects, folder structure
- [_core-adr-policy-004 - Article standards](004-article-standards.md) - Companion artifact type for synthetic views
- [_core-adr-policy-006 - Research standards](006-research-standards.md) - Companion artifact type for exploratory evidence
- [006-write-initiative skill](skills/006-write-initiative/SKILL.md) - Step-by-step instructions for creating a new initiative
