---
name: _core-adr-skill-008-write-xdrs-doc
description: >
  Use when writing documents such as decisions, policies, skills, procedures, research, plans, articles, or presentations.
  Activate this skill when the user asks to create or write any XDRS element.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Routes the request to the appropriate XDRS authoring skill based on the type of document the user wants to create. Reads the target skill at runtime and follows its instructions in full.

## Instructions

### Phase 1: Infer Document Type

1. Infer the target document type from the user's request and context using the mapping below. Do not ask the user unless the type is genuinely ambiguous after reading the request.
   - **Policy** (ADR/BDR/EDR) — user wants to record a decision, rule, standard, guideline, or architectural/business/engineering policy
   - **Skill** — user wants to create an agent skill, SKILL.md, or reusable workflow instruction
   - **Research** — user wants to produce a study, investigation, evidence-based analysis, or IMRAD-style document
   - **Plan** — user wants to create an execution plan, project plan, roadmap, or milestone document
   - **Article** — user wants to create a guide, overview, or synthetic document that combines multiple XDRS elements
   - **Presentation** — user wants to create slides or a Marp deck for an existing XDRS document

2. If the type cannot be confidently inferred, ask the user one focused question: *"What type of XDRS document do you want to create — Policy, Skill, Research, Plan, Article, or Presentation?"* Wait for the answer before proceeding.

### Phase 2: Load and Follow Target Skill

Read the full content of the skill file for the inferred type, then follow all its phases and instructions exactly as if that skill had been activated directly.

| Document type | Skill file to read and follow |
|---|---|
| Policy (ADR / BDR / EDR) | `.xdrs/_core/adrs/principles/skills/002-write-policy/SKILL.md` |
| Skill | `.xdrs/_core/adrs/principles/skills/003-write-skill/SKILL.md` |
| Article | `.xdrs/_core/adrs/principles/skills/004-write-article/SKILL.md` |
| Research | `.xdrs/_core/adrs/principles/skills/005-write-research/SKILL.md` |
| Plan | `.xdrs/_core/adrs/principles/skills/006-write-plan/SKILL.md` |
| Presentation | `.xdrs/_core/adrs/principles/skills/007-write-presentation/SKILL.md` |

### Constraints

- MUST read the full target SKILL.md before proceeding — do not rely on summaries or prior knowledge of the target skill.
- MUST follow all phases of the target skill from Phase 1 onward; do not skip any phase.
- MUST NOT create documents of a type not listed in the routing table above.
