---
name: _core-adr-policy-003-skill-standards
description: Defines skill package standards including structure, SKILL.md format, and co-location with XDRS packages. Use when creating or reviewing skills.
apply-to: All skill packages
valid-from: 2025-01-01
---

# _core-adr-policy-003: Skill standards

## Context and Problem Statement

Teams and AI agents benefit from reusable, discoverable procedural packages that encode specific expertise or behaviors. Without a standard, these "skills" accumulate inconsistently across repositories, making them hard to find, validate, or share.

A skill may describe a procedure performed exclusively by a human today but that is expected to be partially or fully automated by an AI agent in the future. Defining skills in a single, shared format from the start allows them to evolve along that automation gradient without restructuring.

How should skills be authored, structured, and organized within a project so that they are consistent, readable by humans and LLMs alike, and easy to discover?

## Decision Outcome

**agentskills-compatible skill packages, co-located with XDRS**

Skills follow the [agentskills](https://agentskills.io/specification) open format and live inside the XDRS subject folder under a `skills/` sub-directory. Each skill occupies its own numbered package folder, mirroring the XDRS numbering convention.

A skill MAY target a human operator, an AI agent, or both. Instructions MUST be written imperatively and at a level of detail that either a person or an agent can follow without additional context. This design allows a skill to start as a human-only procedure and evolve — incrementally — toward partial or full AI automation without restructuring the document.

### Details

**Automation gradient**
Skills exist on a spectrum from fully manual (human-only) to fully automated (agent-only). A skill SHOULD be written so it can be executed at any point on that spectrum:
- Human reads and follows each step manually.
- Human delegates some steps to an AI assistant.
- An AI agent executes the skill autonomously.

Write instructions so that each step is unambiguous and self-contained. Avoid implicit knowledge that only a human or only an AI would have.

**Relation with Policies, Research, and Articles**
Skills are procedures, Policies are guardrails and decisions, Research documents capture the explored option space and findings behind a decision, and Articles are synthetic views that combine information from multiple artifacts.
Skills MUST link back and forth to their related Policies when the relationship is direct, and link to related Research or Articles when they provide important context.
- Skills are task-based artifacts. They SHOULD have a clear starting trigger, an expected end result, and enough detail for a human or agent to verify that the task finished correctly.
- A skill is not policy by itself. If following a skill is mandatory, that obligation MUST come from a Policy or another explicit policy that references the skill.
- When a skill reads, operationalizes, or enforces Policies, it MUST evaluate the Policy metadata first. `valid-from:` determines the convergence date for adoption, `apply-to:` determines whether the decision fits the current task context, and the decision text itself determines any remaining boundaries. All documents present in the collection are considered active. Skills MUST NOT treat out-of-window or out-of-scope Policies as current requirements.
- Skills and Policies have a many-to-many relationship: one skill MAY operationalize multiple Policies, and one Policy MAY be executed through multiple skills in different contexts.

Place a skill under the XDRS type that matches the nature of the activity the skill performs:
- **EDR skills** - engineering workflows, tool usage, coding procedures, implementation how-tos (e.g. how to design a webpage, how to run a CI pipeline, how to debug a service)
- **ADR skills** - architectural evaluation, pattern compliance checks, technology selection guidance (e.g. how to review an architecture diagram, how to assess API design)
- **BDR skills** - business process execution, market analysis, operations procedures, business rules

The `[subject]` component in the folder path MUST be one of the allowed subjects for the chosen type. The required list of allowed subjects per type is defined in `_core-adr-policy-001`.

Quick test:
- "Is the skill about *how to implement or operate* something?" → EDR.
- "Is the skill about *how to evaluate or decide on* architecture?" → ADR.
- "Is the skill about *how to execute a business process, policy, or market activity*?" → BDR.

**Folder layout**

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        skills/
          [number]-[skill-name]/
            SKILL.md              # required
            scripts/              # optional: executable scripts the agent may run
            references/           # optional: detailed reference material
            .assets/               # optional: images, templates, data files, and other local resources
```

Examples:
- `.xdrs/_core/adrs/principles/skills/001-code-review/SKILL.md`
- `.xdrs/business-x/edrs/devops/skills/001-ci-pipeline-debug/SKILL.md`
- `.xdrs/_local/adrs/principles/skills/001-my-nice-skill/SKILL.md`

**Skill numbering**

- Each skill has a number unique within its `scope/type/subject/skills/` namespace.
- Determine the next number by checking the highest number already present in that namespace. MUST NOT reuse numbers of deleted skills.
- Gaps in the sequence are expected and allowed.

**SKILL.md format** (agentskills spec)

```
---
name: [number]-[skill-name]              # required: matches the folder name exactly; max 64 chars
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
- The `name` field MUST match the folder name exactly (e.g., `001-code-review`). This keeps skill identifiers simple and aligned with the filesystem hierarchy.
- The directory name MUST follow the format `[number]-[skill-name]` (e.g., `001-code-review`), matching the `name:` field.
- `## Overview` SHOULD state the task objective, expected outcome, and relevant prerequisites or tools when they matter.
- `## Instructions` SHOULD include verification steps or acceptance criteria at the end of the task, or at the end of major phases when partial validation matters.
- For simple structure, flow, layout, or relationship indications, `SKILL.md` SHOULD prefer plain Markdown, tables, or ASCII art instead of external assets.
- Any non-Markdown files referenced from `SKILL.md` SHOULD be used only when they are materially necessary and MUST live in `.assets/` inside the same skill package. See `_core-adr-policy-001` for the canonical `.assets/` path conventions.
- Keep `SKILL.md` under 6500 words. Move lengthy reference material to `references/`.
- Use relative paths for all links; MUST NOT use absolute paths starting with `/`.
- File names MUST be lowercase.
- MUST NOT use emojis in skill content.

**Validation**

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) CLI to validate before committing:

```
skills-ref validate .xdrs/[scope]/[type]/[subject]/skills/[number]-[skill-name]
```

## Considered Options

* (REJECTED) **Top-level `skills/` directory separate from XDRS** - Decouples skills from the decisions that govern them.
  * Reason: Breaks the natural association between a decision (Policy) and the skill that implements it; makes navigation harder.
* (CHOSEN) **agentskills-compatible packages co-located with XDRS** - Standardized format with scoped discovery and clear ownership.
  * Reason: Reuses proven agentskills tooling, aligns with the existing XDRS scope/subject hierarchy, and keeps skills close to the decisions they implement.

## References

- [agentskills specification](https://agentskills.io/specification)
- [agentskills/agentskills repository](https://github.com/agentskills/agentskills)
- [skills-ref validation library](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md)
- [_core-adr-policy-004 - Article standards](004-article-standards.md)
- [_core-adr-policy-006 - Research standards](006-research-standards.md)
