# _core-adr-003: Skill standards

## Context and Problem Statement

AI agents benefit from reusable, discoverable prompt packages that encode specific expertise or behaviors. Without a standard, these "skills" accumulate inconsistently across repositories, making them hard to find, validate, or share.

How should skills be authored, structured, and organized within a project so that they are consistent, LLM-friendly, and easy to discover?

## Decision Outcome

**agentskills-compatible skill packages, co-located with XDRs**

Skills follow the [agentskills](https://agentskills.io/specification) open format and live inside the XDR subject folder under a `skills/` sub-directory. Each skill occupies its own numbered package folder, mirroring the XDR numbering convention.

### Implementation Details

**Relation with XDRs**
Skills are procedures, XDRs are guardrails and decisions.
Always create links back and forth between skills <-> XDRs as a reference.

Place a skill under the XDR type that matches the nature of the activity the skill performs:
- **EDR skills** - engineering workflows, tool usage, coding procedures, implementation how-tos (e.g. how to design a webpage, how to run a CI pipeline, how to debug a service)
- **ADR skills** - architectural evaluation, pattern compliance checks, technology selection guidance (e.g. how to review an architecture diagram, how to assess API design)
- **BDR skills** - business process execution, market analysis, operations procedures, business rules

Quick test:
- "Is the skill about *how to implement or operate* something?" → EDR.
- "Is the skill about *how to evaluate or decide on* architecture?" → ADR.
- "Is the skill about *how to execute a business process, policy, or market activity*?" → BDR.

**Folder layout**

```
.xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name]/
    SKILL.md              # required
    scripts/              # optional: executable scripts the agent may run
    references/           # optional: detailed reference material
    assets/               # optional: templates, images, data files
```

Examples:
- `.xdrs/_core/adrs/principles/skills/001-code-review/SKILL.md`
- `.xdrs/business-x/edrs/devops/skills/001-ci-pipeline-debug/SKILL.md`
- `.xdrs/_local/adrs/principles/skills/001-my-nice-skill/SKILL.md`

**Skill numbering**

- Each skill has a number unique within its `scope/type/subject/skills/` namespace.
- Determine the next number by checking the highest number already present in that namespace. Never reuse numbers of deleted skills.
- Gaps in the sequence are expected and allowed.

**SKILL.md format** (agentskills spec)

```
---
name: 001-skill-name      # required: must match the parent directory name exactly; max 64 chars
description: >            # required: what the skill does AND when to activate it; max 1024 chars
  Concise explanation of the skill and the situations in which an agent should load it.
license: <license>        # optional
metadata:                 # optional: arbitrary key/value pairs
  author: <team-or-person>
  version: "1.0"
compatibility: <env>      # optional: system requirements or intended products
allowed-tools: <tools>    # optional (experimental): space-delimited pre-approved tools
---

## Overview

Brief description of the skill goal.

## Instructions

Step-by-step instructions the agent should follow.

## Examples

Concrete input/output examples that illustrate correct behavior.

## Edge Cases

Known gotchas and how to handle them.
```

Rules:
- The `name` field must match the parent directory name exactly (e.g., directory `001-code-review` uses `name: 001-code-review`). This preserves agentskills spec compliance while encoding the ordering number.
- Keep `SKILL.md` under 500 lines. Move lengthy reference material to `references/`.
- Reference other files with relative paths from the skill root.
- Always use lowercase file names.
- Never use emojis in skill content.

**Validation**

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) CLI to validate before committing:

```
skills-ref validate .xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name]
```

## Considered Options

* (REJECTED) **Top-level `skills/` directory separate from XDRs** - Decouples skills from the decisions that govern them.
  * Reason: Breaks the natural association between a decision (XDR) and the skill that implements it; makes navigation harder.
* (CHOSEN) **agentskills-compatible packages co-located with XDRs** - Standardized format with scoped discovery and clear ownership.
  * Reason: Reuses proven agentskills tooling, aligns with the existing XDR scope/subject hierarchy, and keeps skills close to the decisions they implement.

## References

- [agentskills specification](https://agentskills.io/specification)
- [agentskills/agentskills repository](https://github.com/agentskills/agentskills)
- [skills-ref validation library](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [_core-adr-001 - XDR standards](001-xdr-standards.md)
