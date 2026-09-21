---
name: write-xdrs-doc
description: >
  Use when writing documents such as decisions, policies, skills, procedures, research, initiatives, articles, or presentations.
  Activate this skill when the user asks to create or write any XDRS element.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-09-19
---

## Overview

Routes the request to the appropriate XDRS authoring skill based on the type of document the user wants to create. Reads the target skill at runtime and follows its instructions in full.

### Inputs

#### Required

- A free-form request to write a document.

#### Optional

- None.

### Outputs

#### Contents

- The delegated skill's fully written file.

#### Changes

- Whatever changes the delegated skill makes.

### Halt Conditions

- No document type identifiable even after clarification.

### User Interaction

- A single disambiguation question when type is unclear.

### Runtime Requirements

- Same as the delegated skill's, if any.

## Instructions

### Phase 1: Infer Document Type

1. Infer the target document type from the user's request and context using the mapping below. Do not ask the user unless the type is genuinely ambiguous after reading the request.
   - **Policy** (ADR/BDR/EDR) — user wants to record a decision, rule, standard, guideline, or architectural/business/engineering policy
   - **Skill** — user wants to create an agent skill, SKILL.md, or reusable workflow instruction
   - **Research** — user wants to produce a study, investigation, evidence-based analysis, or IMRAD-style document
   - **Initiative** — user wants to create an execution plan, project plan, roadmap, or milestone document
   - **Article** — user wants to create a guide, overview, or synthetic document that combines multiple XDRS elements
   - **Presentation** — user wants to create slides or a Marp deck for an existing XDRS document

2. If the type cannot be confidently inferred, ask the user one focused question: *"What type of XDRS document do you want to create — Policy, Skill, Research, Initiative, Article, or Presentation?"* Wait for the answer before proceeding.

### Phase 1.5: Prerequisites Gate — MUST complete before writing

For the target scope where the document will be created, run the prerequisites gate from the shared module at `.xdrs/_core/adrs/principles/skills/.assets/prerequisites-gate.md`. Substitute `[DOCUMENT TYPE]` with `document`. When routing to the policy skill, apply all local meta-policies found during the gate as mandatory conventions.

### Phase 2: Load and Follow Target Skill

Read the full content of the skill file for the inferred type, then follow all its phases and instructions exactly as if that skill had been activated directly.

| Document type | Skill file to read and follow |
|---|---|
| Policy (ADR / BDR / EDR) | `.xdrs/_core/adrs/principles/skills/write-policy/SKILL.md` |
| Skill | `.xdrs/_core/adrs/principles/skills/write-skill/SKILL.md` |
| Article | `.xdrs/_core/adrs/principles/skills/write-article/SKILL.md` |
| Research | `.xdrs/_core/adrs/principles/skills/write-research/SKILL.md` |
| Initiative | `.xdrs/_core/adrs/principles/skills/write-initiative/SKILL.md` |
| Presentation | `.xdrs/_core/adrs/principles/skills/write-presentation/SKILL.md` |

### Phase 3: Validate Mermaid Diagrams

1. After the delegated skill completes, scan all files written in this session for fenced ` ```mermaid ` code blocks.
2. For each diagram found, extract the content to a temporary `.mmd` file and run:
   ```bash
   npx -y @mermaid-js/mermaid-cli -i <tempfile>.mmd --quiet 2>&1
   ```
3. For each diagram that fails validation, report the error to the user and ask them to correct the diagram before saving.
4. Delete all temporary files created in this step.

### Constraints

- MUST read the full target SKILL.md before proceeding — do not rely on summaries or prior knowledge of the target skill.
- MUST follow all phases of the target skill from Phase 1 onward; do not skip any phase.
- MUST NOT create documents of a type not listed in the routing table above.
- When routing to the Policy skill, MUST also read `_core-adr-policy-016` (`.xdrs/_core/adrs/principles/016-policy-subjects.md`) before choosing a subject — it contains the allowed subject list, descriptions, and disambiguation tiebreaker rules.
- When routing to the Policy skill, MUST also read `_core-adr-policy-017` (`.xdrs/_core/adrs/principles/017-policy-numbering-ranges.md`) before choosing a policy number — it defines the subject-based block ranges that determine valid numbers for each subject.

## Anti-Patterns

- **Mistake:** Authoring the document directly from general knowledge of the target type instead of reading the target skill file.
  **Why it happens:** The router already knows roughly what a Policy or Skill looks like, so reading the full target skill feels redundant.
  **Instead:** Always read the full target SKILL.md and follow it phase by phase; this skill is a router, not an author.

- **Mistake:** Guessing the document type without asking when the request is genuinely ambiguous (e.g., could be Research or Article).
  **Why it happens:** Asking feels like it slows the user down.
  **Instead:** Ask the single focused disambiguation question in Phase 1 rather than guessing wrong and producing the wrong document type.

- **Mistake:** Creating a document type not present in the routing table (e.g., a generic README) by improvising a new template.
  **Why it happens:** The user's request doesn't map cleanly onto the six known types.
  **Instead:** MUST NOT create documents of a type not listed in the routing table; clarify with the user instead.
