---
name: 003-write-skill
description: >
  Creates a new skill package following XDR skill standards: determines type, scope, subject, and number;
  then writes a focused SKILL.md with correct frontmatter, phased instructions, examples, and edge cases.
  Activate this skill when the user asks to create, add, or write a new skill, agent skill, or SKILL.md file.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured skill package by following `_core-adr-003` skill standards, consulting `xdr-standards` for every core element definition, checking existing skills to avoid duplication, and producing a complete SKILL.md ready to activate in VS Code.

## Instructions

### Phase 1: Understand the Skill Goal

1. Read `.xdrs/_core/adrs/principles/003-skill-standards.md` in full to internalize the SKILL.md format, folder layout, and numbering rules.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full before defining any core element for the skill package. Treat it as the canonical source for type, scope, subject, numbering expectations, naming constraints, and folder placement rules.
3. Identify what the skill must do, the concrete outcome it should produce, and the exact conditions under which an agent should activate it. Do NOT proceed without a clear goal, outcome, and activation trigger.

### Phase 2: Select Type, Scope, Subject, and Number

Consult `001-xdrs-core` while making each choice in this phase. The summaries below are orientation only; when there is any ambiguity or edge case, the standard decides.

**Type** — choose one based on the skill's activity:
- **EDR skill**: engineering workflows, tool usage, coding procedures, implementation how-tos
- **ADR skill**: architectural evaluation, pattern compliance, technology selection guidance
- **BDR skill**: business process execution, operations procedures, policy-driven activities

Quick test:
- "How to implement or operate something?" → EDR
- "How to evaluate or decide on architecture?" → ADR
- "How to execute a business process or policy?" → BDR

**Scope** — use `_local` unless the user explicitly names another scope.
- If the user names a scope other than `_local`, check the workspace root `.filedist` file. If any file under `.xdrs/[scope]/` appears in `.filedist`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Subject** — pick the most specific match for the chosen type (required list per type is in `_core-adr-001`):
- ADR subjects: `principles`, `application`, `data`, `integration`, `platform`, `controls`, `operations`
- BDR subjects: `principles`, `marketing`, `product`, `controls`, `operations`, `organization`, `finance`, `sustainability`
- EDR subjects: `principles`, `application`, `infra`, `observability`, `devops`, `governance`

**Skill number** — scan `.xdrs/[scope]/[type]/[subject]/skills/` for the highest existing number and increment by 1. Never reuse numbers from deleted skills.

**Skill name** — `[number]-[short-kebab-case-description]`, max 64 characters total.

### Phase 3: Research Existing Skills and Related XDRs

1. List `.xdrs/[scope]/[type]/[subject]/skills/` for existing skills. If one already covers the goal, extend or reference it instead of creating a duplicate.
2. Read all XDRs relevant to the skill's domain to collect rules and cross-references.
3. Evaluate XDR metadata before operationalizing those rules. All documents present in the collection are considered active. `validFrom:` determines the convergence date for adoption, `applyTo:` determines whether the decision fits the intended task context, and the decision text defines any remaining boundaries. Keep out-of-window or out-of-scope XDRs as background only.
4. Decide whether the skill is merely guidance or is being referenced by an XDR as a mandatory procedure. Do not encode policy in the skill unless it comes from a referenced XDR.

### Phase 4: Write the SKILL.md

Use the mandatory agentskills format:

```
---
name: [number]-[skill-name]
description: >
  [What the skill does AND exactly when an agent should activate it. Max 1024 chars.]
metadata:
  author: [author]
  version: "1.0"
---

## Overview

[1–3 sentence goal statement with the task objective, expected outcome, and relevant prerequisites or tools when they matter.]

## Instructions

### Phase 1: …
[Step-by-step agent instructions organized into named phases. Use imperative language and include verification or acceptance criteria at the end of the task or major phases.]

## Examples

[At least one concrete input/context → expected agent action pair.]

## Edge Cases

[Situations where the skill must not activate or must behave differently.]

## References

[Links to related XDRs and skills.]
```

Rules:
- Use imperative language ("Read …", "Ask …", "Create …").
- The `description` field must state both *what* the skill does and *when* to activate it.
- Keep the skill task-oriented. It should have a clear starting trigger and a concrete ending result.
- Mention tools or prerequisites when they are required to complete the task reliably.
- Do not duplicate content from referenced XDRs — link instead.
- Do not present the skill itself as policy; mandatory behavior must come from referenced XDRs or other policy artifacts.
- When the skill depends on XDRs, make the activation logic and instructions consistent with the XDR metadata so the skill does not operationalize inactive or out-of-scope decisions.
- Prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams), or ASCII art for simple structure, flow, layout, or relationship indications.
- If `SKILL.md` genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name]/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- No emojis. Lowercase filenames. Target under 6500 words.

### Phase 5: Review the Draft

Before writing files, verify:

1. **Activation criteria**: Is it unambiguous when this skill loads vs. when it should not?
2. **Completeness**: Does every phase have actionable steps?
3. **Length**: Under 6500 words? Trim verbose explanations.
4. **Duplication**: Does this overlap an existing skill? If yes, revise.
5. **References**: Are all related XDRs and skills linked, including the cases where the skill operationalizes multiple XDRs?

If any check fails, revise before continuing.

### Phase 6: Write Files

1. Create the skill file at `.xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name]/SKILL.md`.
2. Create a symlink at `.github/skills/[number]-[skill-name]` so VS Code picks it up immediately:
   ```
   mkdir -p .github/skills/[number]-[skill-name]
   ln -s ../../.xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name] .github/skills/[number]-[skill-name]
   ```
3. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new skill. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-001`.

### Constraints

- MUST follow the agentskills SKILL.md format from `003-skill-standards` exactly.
- MUST consult `001-xdrs-core` as the canonical source for every core element definition, especially type, scope, subject, numbering, naming, and placement.
- MUST NOT create a skill that duplicates an existing one — extend or reference it instead.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist`).
- MUST include a References section linking to `003-skill-standards`.

## Examples

**Input**: "Create a skill to help debug CI pipelines"
- Type: EDR (engineering workflow)
- Scope: `_local`
- Subject: `devops`
- Number: scan `.xdrs/_local/edrs/devops/skills/` → next available
- Output: `.xdrs/_local/edrs/devops/skills/001-debug-ci-pipeline/SKILL.md`

**Input**: "Create a skill to review API designs"
- Type: ADR (architectural evaluation)
- Scope: `_local`
- Subject: `integration`
- Number: scan `.xdrs/_local/adrs/integration/skills/` → next available
- Output: `.xdrs/_local/adrs/integration/skills/001-review-api-design/SKILL.md`

## Edge Cases

- If the user's goal is already covered by an existing skill, inform the user and offer to extend it instead of creating a new one.
- If scope is ambiguous, default to `_local` and note the assumption.
- If the goal spans multiple types (e.g., both EDR and ADR), favor the type that best matches the primary activity.

## References

- [_core-adr-003 - Skill standards](../../003-skill-standards.md)
- [_core-adr-001 - XDRs core](../../001-xdrs-core.md)
- [002-write-xdr skill](../002-write-xdr/SKILL.md)
