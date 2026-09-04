---
name: 006-write-initiative
description: >
  Creates a new initiative document following XDRS initiative standards: selects scope, type, subject, and number;
  then writes a focused execution initiative with problem context, proposed solution, approach, milestones, and deliverables.
  Activate this skill when the user asks to create, add, or write an initiative, plan, project plan, roadmap, or execution plan within an XDRS project.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured initiative document by following `_core-adr-policy-007`, consulting `xdrs-core` for every core element definition, researching related Policies and existing initiatives, and producing a focused execution document that connects to the decisions, research, and skills it relates to.

## Instructions

### Phase 0: Scope Placement and Prerequisites Gate — MUST complete before writing

1. Run the scope placement analysis from the shared module at `.xdrs/_core/adrs/principles/skills/.assets/scope-placement.md` to determine and confirm the target scope.
2. Once the scope is confirmed, run the prerequisites gate from the shared module at `.xdrs/_core/adrs/principles/skills/.assets/prerequisites-gate.md`. Substitute `[DOCUMENT TYPE]` with `initiative`.

### Phase 1: Understand the Initiative Goal

1. Read `.xdrs/_core/adrs/principles/007-initiative-standards.md` in full to internalize the template, placement rules, numbering rules, and the constraint that initiatives are ephemeral and must be deleted after implementation.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-standards.md` in full before defining the initiative's core elements. Treat it as the canonical source for how to choose and write type, scope, subject, numbering, naming, and folder placement.
3. Identify the problem being solved, the proposed solution, and the expected timeline from user input or context. Do NOT proceed without a clear problem statement and proposed solution.
4. Ask the user clarifying questions to fill any gaps before writing the initiative. Use the following rules:
   - Ask all initial questions in a single batch so the user can answer them together.
   - After receiving the answers, evaluate whether any answer introduces new ambiguity or opens a related topic that requires further clarification. If it does, ask a focused follow-up question (or a small batch of follow-up questions) before proceeding.
   - Repeat this question-answer loop until you have enough information to write the initiative with confidence.
   - Typical questions cover: the problem being solved, the proposed solution, the expected timeline, the scope, the key stakeholders, and any known constraints or risks.
   - Do NOT ask questions whose answers are already clear from context.


### Phase 2: Select Scope, Type, and Subject

Consult `001-xdrs-standards` while making each choice in this phase. The summaries below are orientation only; when any detail is unclear, the standard decides.

**Scope** — confirmed in Phase 0. Follow the external-scope validation in `.xdrs/_core/adrs/principles/skills/.assets/scope-selection.md`.

**Type** — match the type of the Policies the initiative primarily implements or relates to (`adrs`, `bdrs`, or `edrs`).
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure, pipelines

**Subject** — pick the subject that best matches the initiative's topic (required list per type is in `_core-adr-policy-001`). If the initiative spans more than one subject, place it in `principles`.

### Phase 3: Assign a Number and Name

1. List `.xdrs/[scope]/[type]/[subject]/initiatives/` (create the folder if it does not exist).
2. Find the highest existing initiative number in that namespace and increment by 1. Never reuse numbers.
3. Choose a short lowercase kebab-case title that describes the initiative clearly.
   - Good: `checkout-performance`, `onboarding-redesign`, `api-migration-v2`
   - Avoid: `initiative`, `project`, `misc`

### Phase 4: Research Related Artifacts

1. Read all Policies, Research documents, Skills, and existing Initiatives relevant to the initiative topic across all scopes listed in the Policy root `index.md`.
2. Evaluate Policy metadata before treating any decision as current context. All documents present in the collection are considered active. `valid-from:` determines the convergence date for adoption, `apply-to:` determines whether the decision fits the intended context, and the decision text defines any remaining boundaries.
3. Identify Decisions that this initiative implements, Research that informs the planning, and any existing Initiatives that overlap.
4. Collect artifact IDs and file paths for cross-references.

### Phase 5: Write the Initiative

Use the mandatory template from `007-initiative-standards`:

```markdown
# [scope]-[type]-initiative-[number]: [Short Title]

## Executive Summary

[Required. Bullet points summarizing all sections below. Under 500 words.]

## Context and Problem Statement

[Required. Why are we executing this initiative? What is the impact? Who is impacted? Under 200 words.]

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

- [Related Policy or artifact](relative/path.md) - Brief description of relevance
```

Rules to apply while drafting:

- Focus on the problem, solution, and approach. Avoid bloating with generic project management content.
- Link to Decisions the initiative implements, Research that informs it, and Skills that guide execution.
- The Expected end date must be in ISO format (YYYY-MM-DD), placed inside the `## Proposed Solution` section, and should not be more than 2 years from the initiative creation date.
- If the initiative scope is too large for 2 years, break it into multiple initiatives.
- Remember that this initiative must be deleted after full implementation. Write it with that ephemeral nature in mind.
- For diagrams and non-Markdown assets, follow `_core-adr-policy-020`: prefer plain Markdown tables/lists first, then ASCII art for very simple cases, then Mermaid.js for complex diagrams, then draw.io when Mermaid is insufficient — save as Editable Vector (File → Save As → Editable Vector) and store as `.svg` in the sibling `.assets/` folder.
- If the initiative genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/initiatives/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- Use lowercase file names. Never use emojis.

### Phase 6: Place and Register

1. Save the file at `.xdrs/[scope]/[type]/[subject]/initiatives/[number]-[short-title].md`.
2. Add a link to the initiative in the canonical index for that scope+type (`.xdrs/[scope]/[type]/index.md`).
3. Add back-references in the Policies, Research documents, and Skills that the initiative relates to, under their `## References` section.
4. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new initiative. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-policy-001`.
5. **Meta-policy compliance**: Run the shared module at `.xdrs/_core/adrs/principles/skills/.assets/meta-policy-compliance.md`. Substitute `[DOCUMENT]` with `initiative`.

### Phase 7: Verify with Lint

Follow the lint verification steps in `.xdrs/_core/adrs/principles/skills/.assets/lint-verification.md`.

## Examples

**Input:** "Create a plan for migrating our API to v2."

**Expected actions:**
1. Read `007-initiative-standards.md`.
2. Topic: API v2 migration. Scope: `_local`.
3. Type: `adrs` (architectural). Subject: `application`.
4. Research related Policies about API design and integration patterns.
5. Draft the initiative with clear problem, solution, milestones, and expected end date.
6. Save, register in canonical index, and lint.

## Edge Cases

- If an initiative is too large (more than 2 years), split it into multiple smaller initiatives. Each initiative should be independently actionable and produce its own deliverables.
- If an initiative spawns sub-initiatives during implementation, each sub-initiative is a separate initiative document in the appropriate subject folder. Link them in the References section.
- If an initiative is fully implemented, delete it and confirm that all lasting outputs (Decisions, Skills, Articles, etc.) are properly linked and indexed.
- If the user asks for an initiative that is really just a decision, guide them to create a Policy instead.

## References

- [_core-adr-policy-001 - XDRS standards](../../001-xdrs-standards.md)
- [_core-adr-policy-007 - Initiative standards](../../007-initiative-standards.md)
- [_core-adr-policy-002 - Policy standards](../../002-policy-standards.md)

## Constraints

- MUST follow the initiative template and section-goal rules from `007-initiative-standards`.
- MUST consult `001-xdrs-standards` as the canonical source for every core element definition, especially type, scope, subject, numbering, naming, and placement.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist.lock`).
