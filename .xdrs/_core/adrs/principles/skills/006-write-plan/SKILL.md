---
name: 006-write-plan
description: >
  Creates a new plan document following XDR plan standards: selects scope, type, subject, and number;
  then writes a focused execution plan with problem context, proposed solution, approach, milestones, and deliverables.
  Activate this skill when the user asks to create, add, or write a plan, project plan, or execution plan within an XDR project.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured plan document by following `_core-adr-007`, consulting `xdr-standards` for every core element definition, researching related XDRs and existing plans, and producing a focused execution document that connects to the decisions, research, and skills it relates to.

## Instructions

### Phase 1: Understand the Plan Goal

1. Read `.xdrs/_core/adrs/principles/007-plan-standards.md` in full to internalize the template, placement rules, numbering rules, and the constraint that plans are ephemeral and must be deleted after implementation.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full before defining the plan's core elements. Treat it as the canonical source for how to choose and write type, scope, subject, numbering, naming, and folder placement.
3. Identify the problem being solved, the proposed solution, and the expected timeline from user input or context. Do NOT proceed without a clear problem statement and proposed solution.
4. Ask the user clarifying questions to fill any gaps before writing the plan. Use the following rules:
   - Ask all initial questions in a single batch so the user can answer them together.
   - After receiving the answers, evaluate whether any answer introduces new ambiguity or opens a related topic that requires further clarification. If it does, ask a focused follow-up question (or a small batch of follow-up questions) before proceeding.
   - Repeat this question-answer loop until you have enough information to write the plan with confidence.
   - Typical questions cover: the problem being solved, the proposed solution, the expected timeline, the scope, the key stakeholders, and any known constraints or risks.
   - Do NOT ask questions whose answers are already clear from context.


### Phase 2: Select Scope, Type, and Subject

Consult `001-xdrs-core` while making each choice in this phase. The summaries below are orientation only; when any detail is unclear, the standard decides.

**Scope** — use `_local` unless the user explicitly names another scope.
- If the user names a scope other than `_local`, check the workspace root `.filedist` file. If any file under `.xdrs/[scope]/` appears in `.filedist`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Type** — match the type of the XDRs the plan primarily implements or relates to (`adrs`, `bdrs`, or `edrs`).
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure, pipelines

**Subject** — pick the subject that best matches the plan's topic (required list per type is in `_core-adr-001`). If the plan spans more than one subject, place it in `principles`.

### Phase 3: Assign a Number and Name

1. List `.xdrs/[scope]/[type]/[subject]/plans/` (create the folder if it does not exist).
2. Find the highest existing plan number in that namespace and increment by 1. Never reuse numbers.
3. Choose a short lowercase kebab-case title that describes the initiative clearly.
   - Good: `checkout-performance`, `onboarding-redesign`, `api-migration-v2`
   - Avoid: `plan`, `project`, `misc`

### Phase 4: Research Related Artifacts

1. Read all XDRs, Research documents, Skills, and existing Plans relevant to the plan topic across all scopes listed in the XDR root `index.md`.
2. Evaluate XDR metadata before treating any decision as current context. All documents present in the collection are considered active. `validFrom:` determines the convergence date for adoption, `applyTo:` determines whether the decision fits the intended context, and the decision text defines any remaining boundaries.
3. Identify Decisions that this plan implements, Research that informs the planning, and any existing Plans that overlap.
4. Collect artifact IDs and file paths for cross-references.

### Phase 5: Write the Plan

Use the mandatory template from `007-plan-standards`:

```markdown
# [scope]-plan-[number]: [Short Title]

## Executive Summary

[Required. Bullet points summarizing all sections below. Under 500 words.]

## Context and Problem Statement

[Required. Why are we executing this plan? What is the impact? Who is impacted? Under 200 words.]

## Proposed Solution

[Required. What we expect to achieve. Under 200 words.]

Expected end date: YYYY-MM-DD

## Acceptance Criteria

[Optional. Expected result and how to verify the goal is achieved. Under 100 words.]

## Approach

[Optional. Strategy and high-level how. Under 300 words.]

## Key Deliverables

[Optional. Main outputs needed. Under 300 words.]

## Key Resources

[Optional. Equipment, people, budget, dependencies. Under 100 words.]

## Milestones

[Optional. Goals with acceptance criteria, owners, and due dates. Under 1000 words per milestone.]

## Risks Identified

[Optional. Risks with description and mitigation strategy. Under 1000 words.]

## References

- [Related XDR or artifact](relative/path.md) - Brief description of relevance
```

Rules to apply while drafting:

- Focus on the problem, solution, and approach. Avoid bloating with generic project management content.
- Link to Decisions the plan implements, Research that informs it, and Skills that guide execution.
- The Expected end date must be in ISO format (YYYY-MM-DD), placed inside the `## Proposed Solution` section, and should not be more than 2 years from the plan creation date.
- If the plan scope is too large for 2 years, break it into multiple plans.
- Remember that this plan must be deleted after full implementation. Write it with that ephemeral nature in mind.
- Prefer plain Markdown, tables, or ASCII art for structure and flow.
- If the plan genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/plans/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- Use lowercase file names. Never use emojis.

### Phase 6: Place and Register

1. Save the file at `.xdrs/[scope]/[type]/[subject]/plans/[number]-[short-title].md`.
2. Add a link to the plan in the canonical index for that scope+type (`.xdrs/[scope]/[type]/index.md`).
3. Add back-references in the XDRs, Research documents, and Skills that the plan relates to, under their `## References` section.
4. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new plan. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-001`.

### Phase 7: Verify with Lint

1. Run the CLI lint utility from the repository root:
   ```
   npx -y xdrs-core lint .
   ```
2. Fix all reported errors before considering the task complete.

## Examples

**Input:** "Create a plan for migrating our API to v2."

**Expected actions:**
1. Read `007-plan-standards.md`.
2. Topic: API v2 migration. Scope: `_local`.
3. Type: `adrs` (architectural). Subject: `integration` or `application`.
4. Research related XDRs about API design and integration patterns.
5. Draft the plan with clear problem, solution, milestones, and expected end date.
6. Save, register in canonical index, and lint.

## Edge Cases

- If a plan is too large (more than 2 years), split it into multiple smaller plans. Each plan should be independently actionable and produce its own deliverables.
- If a plan spawns sub-plans during implementation, each sub-plan is a separate plan document in the appropriate subject folder. Link them in the References section.
- If a plan is fully implemented, delete it and confirm that all lasting outputs (Decisions, Skills, Articles, etc.) are properly linked and indexed.
- If the user asks for a plan that is really just a decision, guide them to create an XDR instead.

## References

- [_core-adr-001 - XDRs core](../../001-xdrs-core.md)
- [_core-adr-007 - Plan standards](../../007-plan-standards.md)
- [_core-adr-002 - XDR standards](../../002-xdr-standards.md)

## Constraints

- MUST follow the plan template and section-goal rules from `007-plan-standards`.
- MUST consult `001-xdrs-core` as the canonical source for every core element definition, especially type, scope, subject, numbering, naming, and placement.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist`).
