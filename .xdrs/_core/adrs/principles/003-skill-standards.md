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

Skills follow the [agentskills](https://agentskills.io/specification) open format and live inside the XDRS subject folder under a `skills/` sub-directory. Each skill occupies its own package folder named after the skill itself, without the numeric prefix used by other XDRS document types.

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
- A skill is not policy by itself. If following a skill is REQUIRED, that obligation MUST come from a Policy or another explicit policy that references the skill.
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
          [skill-name]/
            SKILL.md              # required
            scripts/              # optional: executable scripts the agent may run
            references/           # optional: detailed reference material
            .assets/               # optional: images, templates, data files, and other local resources
```

Examples:
- `.xdrs/_core/adrs/principles/skills/code-review/SKILL.md`
- `.xdrs/business-x/edrs/devops/skills/ci-pipeline-debug/SKILL.md`
- `.xdrs/_local/adrs/principles/skills/my-nice-skill/SKILL.md`

Multiple skills under the same `[subject]/skills/` folder MAY share common instruction modules through a sibling `.assets/` directory placed directly under `skills/` (not inside any individual skill package) — for example `skills/.assets/shared-check.md`, referenced with a relative link from any skill in that folder. This keeps shared procedures DRY without duplicating instructions across skills.

A skill's own `.assets/` folder and the shared `skills/.assets/` folder are exempt from orphan-asset tracking: their files do not need to be linked from `SKILL.md`, because they may hold scripts, templates, installed dependencies (e.g., `node_modules/`), or other runtime resources used by the skill. When `SKILL.md` does link to an asset, the link MUST point either to the skill's own `.assets/` folder or to the shared `../.assets/` folder.

A skill MAY optionally be distributed as a self-contained standalone package (for example, to share it outside this repository) using the bundling mechanism defined in [`_core-adr-policy-021`](021-skill-bundling.md). Bundling is optional; skills that are always consumed as part of the full package do not need it.

**Directory roles**

| Path | Purpose |
|---|---|
| `SKILL.md` | Required entry point: frontmatter + instructions. |
| `scripts/` | Optional executable scripts the agent may run. |
| `references/` | Optional deep reference material split out of `SKILL.md`. |
| `.assets/` | Optional images, templates, scripts, dependencies, and other local resource files. Not subject to orphan-asset tracking. |

**Skill naming**

Unlike Policies, Research, Articles, and Initiatives, skill packages are not auto-numbered. A skill is identified by a descriptive name, keeping it compatible with the wider agentskills ecosystem, where clients (including this framework's own agentskills-format consumers) expect a plain descriptive identifier rather than an auto-generated sequence number. The name MAY still contain digits, including as a prefix, when that is simply part of the descriptive name (e.g., `2fa-setup`). Each skill name MUST be unique within its `scope/type/subject/skills/` namespace; check for an existing skill with the same name before creating a new one.

**SKILL.md format** (agentskills spec)

```
---
name: [skill-name]              # required: matches the folder name exactly; max 64 chars
description: >            # required: what the skill does AND when to activate it; max 1024 chars (SHOULD stay near 250 when the trigger can be stated that tightly)
  Concise explanation of the skill and the situations in which an agent should load it.
license: <license>        # optional
metadata:                 # required
  author: <team-or-person>       # required
  version: "1.0.0"                # required: full semantic versioning
  updated: YYYY-MM-DD              # required: date of the last material content change
---

## Overview

Brief description of the skill goal.

### Inputs

#### Required
- Bare minimum the skill needs to start working, one bullet per item, or "None".

#### Optional
- Extra helpful context the skill can use if given, one bullet per item, or "None".

### Outputs

#### Contents
- Generated files or chat-delivered results, one bullet per item, or "None" (e.g., `Release notes (<300 words)`).

#### Changes
- External system mutations that are part of the skill's main objective, one bullet per item, or "None".

### Halt Conditions
- Specific triggers that make the skill stop before completing, one bullet per item, or "None".

### User Interaction

Optional section: human-in-the-loop (HITL) exchanges during execution — a clarifying question or
an approval gate — one bullet per item, or "None". Omit this section entirely when none apply.

### Runtime Requirements

Optional section: tooling, network access, or environment prerequisites beyond the LLM itself,
one bullet per item. Omit this section entirely when none apply.

## Instructions

Step-by-step instructions the agent should follow. State one clearly recommended approach first when several are viable; note alternatives briefly afterward.

## Examples

Concrete input/output examples that illustrate correct behavior.

## Edge Cases

Known gotchas and how to handle them.

## Anti-Patterns

At least 3 entries, each grounded in a real observed mistake:
- **Mistake:** what an agent or author incorrectly did.
  **Why it happens:** the reasoning or shortcut that leads there.
  **Instead:** the correct approach.
```

Rules:
- The `name` field MUST match the folder name exactly (e.g., `code-review`). This keeps skill identifiers simple and aligned with the filesystem hierarchy.
- The directory name and the `name:` field MUST contain only lowercase alphanumeric characters and hyphens (e.g., `code-review`, `2fa-setup`).
- `metadata` is REQUIRED. `metadata.version` MUST use full semantic versioning (`MAJOR.MINOR.PATCH`, e.g. `1.0.0`), consistent with [`_core-adr-policy-005`](005-semantic-versioning-for-xdrs-packages.md); `metadata.author` MUST be non-empty; `metadata.updated` MUST be an ISO `YYYY-MM-DD` date, refreshed whenever the skill's content materially changes.
- `description` SHOULD stay near 250 characters when the activation trigger can be stated that tightly, even though the hard cap remains 1024 characters — it is loaded into context on every activation scan.
- `## Overview` SHOULD state the task objective, expected outcome, and relevant prerequisites or tools when they matter, and MUST contain nested subsections, in order, for `### Inputs`, `### Outputs`, `### Halt Conditions`, then the optional `### User Interaction` and `### Runtime Requirements`.
- `### Inputs` MUST contain `#### Required` (the bare minimum needed to invoke the skill) then `#### Optional` (helpful extra context), in that order.
- `## Instructions` is REQUIRED. It SHOULD state one clearly recommended approach first when multiple are viable, noting alternatives briefly afterward, and SHOULD include verification steps or acceptance criteria at the end of the task or major phases.
- `## Examples` SHOULD include 2-3 example prompts a user could give as input, alongside a short description of what to expect during execution and as output for each.
- `### Outputs` covers only end-objective results, not intermediary items, and MUST contain `#### Contents` (generated files or chat-delivered results) then `#### Changes` (external system mutations that are part of the main objective), in that order.
- `### Halt Conditions` MUST list this skill's specific stop-before-completing triggers, grounded in at least missing required input, dubious/ambiguous input, and insufficient agent confidence — distinct from `## Edge Cases` (activation/boundary conditions) and `## Anti-Patterns` (execution mistakes). A partial or empty result the skill still finishes and returns belongs in `### Outputs`, not `### Halt Conditions`.
- `### User Interaction` is OPTIONAL: documents human-in-the-loop (HITL) exchanges during execution — a clarifying question or an approval gate — distinct from `### Halt Conditions` (which stop execution rather than pause-and-resume it) and `### Runtime Requirements` (static prerequisites, not an interactive exchange); omit the section entirely when the skill has none.
- `### Runtime Requirements` is OPTIONAL: free-form bullets for tooling, network, or environment prerequisites beyond the LLM itself; omit the section entirely when none apply.
- Every bullet in `#### Required`, `#### Optional`, `#### Contents`, `#### Changes`, `### Halt Conditions`, and `### User Interaction` MUST be under 20 words, or the section MUST contain a single "None" bullet instead.
- `## Anti-Patterns` is REQUIRED with a minimum of 3 entries, each naming a Mistake, Why it happens, and the correct approach Instead, grounded in real observed issues rather than theoretical ones. Keep it distinct from `## Edge Cases`: Edge Cases are activation/boundary conditions, Anti-Patterns are execution mistakes.
- Key recommendations MAY be tagged `[PROVEN]`, `[RECOMMENDED]`, or `[EXPERIMENTAL]` when a skill offers several viable approaches at different confidence levels.
- For diagram format preferences and non-Markdown asset rules, see [`_core-adr-policy-020`](020-media-and-asset-standards.md).
- `SKILL.md` MUST stay under 7000 words. Move lengthy reference material to `references/`; each `references/*.md` file MUST stay under 4000 words, splitting further when a single file grows unwieldy.
- Use relative paths for all links; MUST NOT use absolute paths starting with `/`.
- File names MUST be lowercase.
- MUST NOT use emojis in skill content.

**Script standards**

When a skill includes `scripts/`:
- Each script MUST declare its runtime/interpreter at the top (shebang or equivalent header comment).
- SHOULD use the language already used by the consuming project when known, rather than mandating one language repo-wide.
- MUST avoid non-essential external dependencies, or document install steps in `SKILL.md` when unavoidable.
- SHOULD support both human-readable and machine-readable (JSON) output when producing analysis or report output.
- SHOULD stay single-purpose.

**Quality gate**

Before creating a skill, confirm it removes real ambiguity or repetitive effort compared to not having it. Skills that only restate a Policy, or that handle a one-off task unlikely to recur, SHOULD NOT be created.

**Clarify First**

Generative skills — those producing a deliverable document (Policy, Skill, Article, Research, Initiative, Presentation) — SHOULD list the 2-4 inputs they need confirmed (e.g., topic, scope, audience) and ask the user when any is unknown, stopping once those inputs are confirmed rather than over-interrogating. Skills that route, review, or report instead of authoring a new deliverable do not need this pattern.

**Halt behavior**

Skills MUST halt on missing required input, dubious/ambiguous input, or insufficient agent confidence, unless the user explicitly instructs the agent to proceed anyway. This override applies generally; a skill's own `## Halt Conditions` list does not need to restate it.

**Generated content caps**

Every natural-language content a skill generates MUST declare a hard word cap written exactly as `<N words`, whether a human or an agent executes the skill. This covers files, templates, reports, intermediate chat messages, HITL questions, final summaries, and text posted to external systems (e.g., PR comments, commit messages).
- Exempt, with no marker: code (including its comments), structured data (JSON, YAML, tracking files), verbatim copies, and frontmatter fields already limited in characters by a spec or Policy.
- Caps MUST be in words; other limits MAY coexist but never replace them.
- Declare each cap once: in the template placeholder (including templates in `references/` or `.assets/`), else in the Instructions step producing the content, else in its `#### Contents` bullet.
- A blanket statement MAY cover a content class (e.g., all intermediate messages); a more specific cap overrides it.
- Write the number inline; a Policy reference is optional.
- Content whose size cannot be bounded MUST be marked `(uncapped: <reason>)`, the reason explaining why.
- Caps are hard: condense, or split into another item only where the skill allows it; never split one logical item across messages. An explicit user request lifts the cap for that item only.

**Validation**

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) CLI to validate before committing:

```
skills-ref validate .xdrs/[scope]/[type]/[subject]/skills/[skill-name]
```

## Considered Options

* (REJECTED) **Top-level `skills/` directory separate from XDRS** - Decouples skills from the decisions that govern them.
  * Reason: Breaks the natural association between a decision (Policy) and the skill that implements it; makes navigation harder.
* (CHOSEN) **agentskills-compatible packages co-located with XDRS** - Standardized format with scoped discovery and clear ownership.
  * Reason: Reuses proven agentskills tooling, aligns with the existing XDRS scope/subject hierarchy, and keeps skills close to the decisions they implement.
* (REJECTED) **Fully self-contained skills, no shared assets** - Every skill package repeats any instruction shared with another skill.
  * Reason: Duplicates maintenance burden across skills and drifts out of sync over time.
* (CHOSEN) **Shared `.assets/` modules plus optional bundling** - Keep shared instruction modules DRY in-repo, and offer an optional per-skill bundling mechanism for standalone distribution.
  * Reason: Preserves DRY authoring for the common case while still allowing a single skill to be distributed as a self-contained artifact when needed ([`_core-adr-policy-021`](021-skill-bundling.md)).

## References

- [agentskills specification](https://agentskills.io/specification)
- [agentskills/agentskills repository](https://github.com/agentskills/agentskills)
- [skills-ref validation library](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md)
- [_core-adr-policy-004 - Article standards](004-article-standards.md)
- [_core-adr-policy-005 - Semantic versioning for XDRS packages](005-semantic-versioning-for-xdrs-packages.md)
- [_core-adr-policy-006 - Research standards](006-research-standards.md)
- [_core-adr-policy-021 - Skill bundling](021-skill-bundling.md)
