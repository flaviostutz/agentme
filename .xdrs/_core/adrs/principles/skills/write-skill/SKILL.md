---
name: write-skill
description: >
  Creates a new skill package following XDRS skill standards: determines type, scope, and subject;
  then writes a focused SKILL.md with correct frontmatter, phased instructions, examples, and edge cases.
  Activate this skill when the user asks to create, add, or write a new skill, agent skill, or SKILL.md file.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-09-19
---

## Overview

Guides the creation of a well-structured skill package by following `_core-adr-policy-003` skill standards, consulting `xdrs-core` for every core element definition, checking existing skills to avoid duplication, and producing a complete SKILL.md ready to activate in VS Code.

### Inputs

#### Required

- A description of the task the skill should perform

#### Optional

- None

### Outputs

#### Contents

- A complete SKILL.md file

#### Changes

- A symlink under `.agents/skills/`

### Halt Conditions

- No writable scope can be found or inferred

### User Interaction

- A clarifying question when scope or type is ambiguous

### Runtime Requirements

- Write access to the target scope.

## Instructions

### Phase 0: Scope Placement and Prerequisites Gate — MUST complete before writing

1. Run the scope placement analysis from the shared module at `.xdrs/_core/adrs/principles/skills/.assets/scope-placement.md` to determine and confirm the target scope.
2. Once the scope is confirmed, run the prerequisites gate from the shared module at `.xdrs/_core/adrs/principles/skills/.assets/prerequisites-gate.md`. Substitute `[DOCUMENT TYPE]` with `skill`.

### Phase 1: Understand the Skill Goal

1. Read `.xdrs/_core/adrs/principles/003-skill-standards.md` in full to internalize the SKILL.md format and folder layout.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-standards.md` in full before defining any core element for the skill package. Treat it as the canonical source for type, scope, subject, naming constraints, and folder placement rules.
3. Identify what the skill must do, the concrete outcome it should produce, and the exact conditions under which an agent should activate it. Do NOT proceed without a clear goal, outcome, and activation trigger.

### Phase 2: Select Type, Scope, and Subject

Consult `001-xdrs-standards` while making each choice in this phase. The summaries below are orientation only; when there is any ambiguity or edge case, the standard decides.

**Type** — choose one based on the skill's activity:
- **EDR skill**: engineering workflows, tool usage, coding procedures, implementation how-tos
- **ADR skill**: architectural evaluation, pattern compliance, technology selection guidance
- **BDR skill**: business process execution, operations procedures, policy-driven activities

Quick test:
- "How to implement or operate something?" → EDR
- "How to evaluate or decide on architecture?" → ADR
- "How to execute a business process or policy?" → BDR

**Scope** — confirmed in Phase 0. Follow the external-scope validation in `.xdrs/_core/adrs/principles/skills/.assets/scope-selection.md`.

**Subject** — follow the subject selection guidance in `.xdrs/_core/adrs/principles/skills/.assets/scope-selection.md`.

**Skill name** — a short, descriptive, lowercase kebab-case name (e.g. `code-review`), max 64 characters total. The directory name matches the `name` field exactly. Check `.xdrs/[scope]/[type]/[subject]/skills/` first to avoid colliding with an existing skill name.

### Phase 3: Research Existing Skills and Related Policies

1. List `.xdrs/[scope]/[type]/[subject]/skills/` for existing skills. If one already covers the goal, extend or reference it instead of creating a duplicate.
2. Read all Policies relevant to the skill's domain to collect rules and cross-references.
3. Evaluate Policy metadata before operationalizing those rules. All documents present in the collection are considered active. `valid-from:` determines the convergence date for adoption, `apply-to:` determines whether the decision fits the intended task context, and the decision text defines any remaining boundaries. Keep out-of-window or out-of-scope Policies as background only.
4. Decide whether the skill is merely guidance or is being referenced by a Policy as a mandatory procedure. Do not encode policy in the skill unless it comes from a referenced Policy.

### Phase 4: Write the SKILL.md

Use the mandatory agentskills format:

```
---
name: [skill-name]
description: >
  [What the skill does AND exactly when an agent should activate it. Max 1024 chars.]
metadata:
  author: [author]
  version: "1.0.0"
  updated: [YYYY-MM-DD]
---

## Overview

[1–3 sentence goal statement with the task objective, expected outcome, and relevant prerequisites or tools when they matter.]

### Inputs

#### Required

[Bare-minimum bullets needed to invoke the skill, or a single "None" bullet. Each under 10 words.]

#### Optional

[Extra helpful-context bullets, or a single "None" bullet. Each under 10 words.]

### Outputs

#### Contents

[End-objective files/chat text produced, or a single "None" bullet. Each under 10 words.]

#### Changes

[End-objective external system mutations, or a single "None" bullet. Each under 10 words.]

### Halt Conditions

[This skill's specific stop-before-completing triggers, or a single "None" bullet. Each under 10 words.]

### User Interaction

[Optional. Human-in-the-loop exchanges during execution: clarifying questions or approval gates, or a single "None" bullet. Each under 10 words. Omit the whole section if none apply.]

### Runtime Requirements

[Optional. Tooling/network prerequisites as free-form bullets. Omit the whole section if none apply.]

## Instructions

### Phase 1: …
[Step-by-step agent instructions organized into named phases. Use imperative language and include verification or acceptance criteria at the end of the task or major phases.]

## Examples

[At least one concrete input/context → expected agent action pair. Include 2-3 example prompts a user could type to trigger the skill.]

## Edge Cases

[Situations where the skill must not activate or must behave differently.]

## Anti-Patterns

[At least 3 entries. Each with **Mistake:**/**Why it happens:**/**Instead:** structure, grounded in this specific skill's domain.]

## References

[Links to related Policies and skills.]
```

If the skill needs to be distributed as a standalone package outside the full `xdrs-core` package, it MAY also add a bundling `Makefile` following the optional mechanism in [`_core-adr-policy-021`](../../021-skill-bundling.md). This is not required for skills that are always consumed as part of the full package.

Rules:
- Use imperative language ("Read …", "Ask …", "Create …").
- The `description` field must state both *what* the skill does and *when* to activate it.
- Keep the skill task-oriented. It should have a clear starting trigger and a concrete ending result.
- Mention tools or prerequisites when they are required to complete the task reliably.
- Do not duplicate content from referenced Policies — link instead.
- Do not present the skill itself as policy; mandatory behavior must come from referenced Policies or other policy artifacts.
- When the skill depends on Policies, make the activation logic and instructions consistent with the Policy metadata so the skill does not operationalize inactive or out-of-scope decisions.
- For diagrams and non-Markdown assets, follow `_core-adr-policy-020`: prefer plain Markdown tables/lists first, then ASCII art for very simple cases, then Mermaid.js (sequence, state, activity, entity diagrams) for complex ones, then draw.io when Mermaid is insufficient — save as Editable Vector (File → Save As → Editable Vector) and store as `.svg` in the sibling `.assets/` folder.
- If `SKILL.md` genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/skills/[skill-name]/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- No emojis. Lowercase filenames. Target under 7000 words.

### Phase 5: Review the Draft

Before writing files, verify:

1. **Activation criteria**: Is it unambiguous when this skill loads vs. when it should not?
2. **Completeness**: Does every phase have actionable steps?
3. **Length**: Under 7000 words? Trim verbose explanations.
4. **Duplication**: Does this overlap an existing skill? If yes, revise.
5. **References**: Are all related XDRs and skills linked, including the cases where the skill operationalizes multiple XDRs?
6. **Anti-Patterns**: Does the skill include at least 3 genuine, domain-specific `## Anti-Patterns` entries (not generic filler)?
7. **Required sections**: Does `## Overview` contain nested `### Inputs` (Required/Optional bullets), `### Outputs` (Contents/Changes bullets), and `### Halt Conditions` listing this skill's specific stop triggers — each bullet under 10 words or a single "None"?
8. **Meta-policy compliance**: Run the shared module at `.xdrs/_core/adrs/principles/skills/.assets/meta-policy-compliance.md`. Substitute `[DOCUMENT]` with `skill`.

If any check fails, revise before continuing.

### Phase 6: Write Files

1. Create the skill file at `.xdrs/[scope]/[type]/[subject]/skills/[skill-name]/SKILL.md`.
2. Create a symlink at `.agents/skills/[skill-name]` so VS Code picks it up immediately:
   ```
   mkdir -p .agents/skills
   ln -s ../../.xdrs/[scope]/[type]/[subject]/skills/[skill-name] .agents/skills/[skill-name]
   ```
3. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new skill. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-policy-001`.

### Phase 7: Verify with Lint

Follow the lint verification steps in `.xdrs/_core/adrs/principles/skills/.assets/lint-verification.md`.

### Constraints

- MUST follow the agentskills SKILL.md format from `003-skill-standards` exactly.
- MUST consult `001-xdrs-standards` as the canonical source for every core element definition, especially type, scope, subject, naming, and placement.
- MUST NOT create a skill that duplicates an existing one — extend or reference it instead.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist.lock`).
- MUST include a References section linking to `003-skill-standards`.
- MUST include nested `### Inputs`, `### Outputs`, and `### Halt Conditions` subsections inside `## Overview` with skill-specific content.

**Input**: "Create a skill to help debug CI pipelines"
- Type: EDR (engineering workflow)
- Scope: `_local`
- Subject: `platform`
- Output: `.xdrs/_local/edrs/platform/skills/debug-ci-pipeline/SKILL.md`

**Input**: "Create a skill to review API designs"
- Type: ADR (architectural evaluation)
- Scope: `_local`
- Subject: `application`
- Output: `.xdrs/_local/adrs/application/skills/review-api-design/SKILL.md`

**Input**: "Add a skill for our onboarding checklist"
- Asks a clarifying question if scope or type is ambiguous, then drafts the skill package.

## Edge Cases

- If the user's goal is already covered by an existing skill, inform the user and offer to extend it instead of creating a new one.
- If scope is ambiguous, default to `_local` and note the assumption.
- If the goal spans multiple types (e.g., both EDR and ADR), favor the type that best matches the primary activity.

## Anti-Patterns

- **Mistake:** Omitting the `metadata.author`/`metadata.version`/`metadata.updated` fields, or using a partial version like `1.0` instead of full semantic versioning.
  **Why it happens:** These feel like optional bookkeeping details rather than required fields.
  **Instead:** `author`, `version` (full `MAJOR.MINOR.PATCH`), and `updated` (ISO date) are all required per `_core-adr-policy-003`.

- **Mistake:** Writing a boilerplate `## Anti-Patterns` section that restates the Edge Cases content instead of describing real authoring mistakes.
  **Why it happens:** Anti-Patterns and Edge Cases both describe "things that can go wrong", which invites duplication.
  **Instead:** Edge Cases describe when the skill should behave differently; Anti-Patterns describe mistakes an agent following the skill is likely to make and how to avoid them.

- **Mistake:** Creating a new skill that duplicates an existing one instead of extending it, because the existing skill wasn't searched for first.
  **Why it happens:** Writing fresh instructions feels faster than reading and understanding an existing skill.
  **Instead:** Always list `.xdrs/[scope]/[type]/[subject]/skills/` first (Phase 3) and extend or reference an existing skill when one already covers the goal.

## References

- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)
- [_core-adr-policy-001 - XDRS standards](../../001-xdrs-standards.md)
- [_core-adr-policy-021 - Skill bundling](../../021-skill-bundling.md)
- [write-policy skill](../write-policy/SKILL.md)
