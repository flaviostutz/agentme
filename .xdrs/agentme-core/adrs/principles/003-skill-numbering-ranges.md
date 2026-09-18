---
name: agentme-core-adr-policy-003-skill-numbering-ranges
description: >
  Defines an OPTIONAL semantic skill numbering scheme a scope MAY adopt once its skill library
  is complex enough to benefit from it (multiple layers of related skills, many categories
  needing at-a-glance risk signaling). When adopted, a skill's number encodes its category
  (connectivity, operation type, and autonomy level), ordered by increasing complexity and
  risk; human and agentic skills share the same ranges. The `agentme` and `agentme-core`
  scopes never use it. Use when deciding whether a new skill in another scope should be
  numbered, assigning a number once a scope has opted in, or reviewing whether an existing
  skill number is correct.
apply-to: agentme scope contributors, and agents helping author skills in any scope that has opted into this numbering scheme
valid-from: 2026-09-18
---

# agentme-core-adr-policy-003: skill numbering ranges

## Context and Problem Statement

[`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md) does not auto-number skills: a skill's folder and `name:` field are a plain, descriptive, lowercase-kebab identifier, and any digits present are expected to be an organic part of that descriptive name (e.g. `2fa-setup`), not an externally-imposed sequence or category code. That default works well for a small or single-purpose skill library, but as a skill library grows across multiple scopes, namespaces, and automation types — especially once related skills form multiple layers, such as the base/domain/operation adapter-skill hierarchy in [`agentme-edr-127`](../../../agentme/edrs/application/127-external-system-adapter-skills.md) — a purely descriptive name gives no signal of category or risk at a glance. Discovering all connector skills, all autonomous-write skills, or all multi-system read skills requires reading every skill in every namespace.

Should skill numbering ever be used on top of `_core-adr-policy-003`'s default, and if so, under what conditions, by whom, and with what scheme?

## Decision Outcome

**Skill numbering is OPTIONAL. Every scope defaults to `_core-adr-policy-003`'s plain descriptive kebab-case naming — including `agentme` and `agentme-core`, which MUST NOT number their own skills. A scope MAY explicitly opt in to the semantic numbering scheme below once its own skill library is complex enough to benefit from it (rule `06`). When a scope opts in, a skill's number encodes its category — connectivity, operation type, and autonomy level — ordered by increasing complexity and risk; human and agentic skills share the same ranges, and the range table in rule `01` applies to that scope's skills. Before creating a new skill in any scope other than `agentme`/`agentme-core`, ask the human whether it should be numbered (rule `07`) before assigning a number (rule `08`).**

### Details

#### 01-range-table

A skill in a scope that has opted in to numbering (rule `07`) MUST be assigned a number from the range whose category best describes the skill's primary purpose. Each range is exactly 50 numbers wide. Higher numbers indicate higher complexity and risk. Ranges 650–899 are reserved for future categories; MUST NOT be used until a category is formally defined.

| Range | Category | Key constraints |
|-------|----------|-----------------|
| 1–49 | Framework & meta | XDRS tooling, document authoring, code review, agent governance |
| 50–99 | Software engineering | Project scaffolding, codegen, refactoring, language and build tooling |
| 100–149 | Local data & file processing | Transform, parse, analyse local data; no external systems |
| 150–199 | General operational & business procedures | HOWTOs, guidelines, call center scripts, runbooks (without automation), business process guidance, business analysis; no external system connections required; see rule `05` for tiebreakers |
| 200–249 | Testing, QA, compliance, local security | Linting, scanning, validation; no external systems; see rule `05` for live-system test tiebreaker |
| 250–299 | Base connectors | Reusable auth and connection skill for one external system; see rule `02` |
| 300–349 | Read-only, single system | Query, fetch, inspect, or list from one external system; artifact generation (reports, files) counts as output, not a write |
| 350–399 | Read-only, multi-system | Cross-system diff, conciliation, comparison, audit |
| 400–449 | Human-in-the-loop (HITL) write, single system | Human approves at each significant step before writing |
| 450–499 | HITL write, multi-system | Cross-system writes with per-step human approval; see rule `05` for side-effect tiebreaker |
| 500–549 | Autonomous write, single system | Executes writes without per-step approval; see rule `03` |
| 550–599 | Autonomous write, multi-system | Executes writes across multiple systems without per-step approval; see rule `03` |
| 600–649 | Complex orchestrations | Multi-step pipelines combining generic, read, and write operations across multiple systems; MAY invoke lower-range skills as sub-procedures |
| 650–899 | Reserved | Not available for assignment until a category is formally defined in this policy |
| 900+ | Overflow | Skills that do not clearly fit any category above, or experimental skills pending reclassification; add a comment in `## Overview` noting the intended range |

#### 02-connector-naming

A connector skill that is numbered (range 250–299) MUST:
- Cover exactly one external system, or one focused scope within a system.
- Include the system name and the suffix `connector` in both the folder name and the `name:` field. A scope qualifier MAY be inserted between the system name and the suffix (e.g., `260-github-connector`, `261-github-actions-connector`, `275-jira-connector`, `276-servicenow-incidents-connector`).
- Provide reusable authentication patterns, connection scripts (curl, Python, or Playwright depending on system complexity), and connection tricks for that system.
- Be referenced by higher-numbered skills that interact with the same system rather than duplicating connection logic.

#### 03-autonomous-write-permission-notice

Every autonomous-write skill (range 500–599) MUST include a mandatory upfront permission prompt as the first step of its `## Instructions` section. The prompt MUST:
- Explicitly state which external system(s) will be modified.
- Name the categories of changes that may be made (e.g., create, update, delete record types).
- Require explicit human confirmation before any write operation begins.
- Not proceed if confirmation is withheld.

#### 04-metadata-tags

The following concerns are handled through metadata tags on the skill, NOT through separate number ranges:

| Concern | Metadata tag | Example value |
|---------|-------------|---------------|
| Event-driven / reactive trigger | `trigger` | `webhook`, `cron`, `event-stream` |
| Batch or scheduled execution | `schedule` | `true` |
| Dry-run / preview mode | `dry-run` | `true` |

A skill's number MUST reflect the operation type the skill performs, not how it is triggered or whether it previews changes.

#### 05-boundary-tiebreakers

When a skill sits on the boundary between two ranges, the assignee MUST apply the following tiebreaker rules to determine the correct range:

**Template vs. procedure (1–49 vs. 150–199)**
If the skill produces a blank artifact for a human to fill in (template, checklist form), assign it to 1–49 (framework & meta). If the skill walks through the steps to execute a process, assign it to 150–199 (operational & business procedures).

**Live-system integration tests (200–249 vs. 300–349)**
If all external dependencies are mocked or stubbed, assign the skill to 200–249 (testing/QA). If the skill requires a live external system to execute, assign it to 300–349 (read-only, single system).

**Notification side-effect vs. primary write target (400–449 vs. 450–499)**
Writing to a notification or messaging system (Slack, email, webhook) counts as the primary write target only when that write is the main purpose of the skill. If the notification is a side-effect of a write to a different primary system, it does not elevate the skill to multi-system (450–499); the skill stays in 400–449 (single system).

#### 06-when-to-opt-in

Numbering SHOULD only be adopted when a scope's skill library is genuinely complex, for example:

- Multiple layers of related skills for the same domain, such as the base connector → domain → operation hierarchy described in [`agentme-edr-127`](../../../agentme/edrs/application/127-external-system-adapter-skills.md).
- Many skills spread across several of the categories in rule `01`, where a plain descriptive name no longer makes category or risk obvious at a glance.

A scope with only a handful of skills, or a single-purpose skill library, SHOULD stay with `_core-adr-policy-003`'s plain descriptive naming and MUST NOT adopt numbering just for its own sake.

#### 07-ask-before-numbering-other-scopes

The `agentme` and `agentme-core` scopes (this repository's own skills) MUST NOT use numbering; new skills there always follow `_core-adr-policy-003`'s plain kebab-case naming, with no exception. `_core` skills likewise follow `_core-adr-policy-003` directly and are never in scope for this policy.

Before creating a new skill in any OTHER scope — for example a project's own `_local` scope, or a custom scope in a project that has adopted the `agentme` preset — an agent or contributor MUST ask the human whether the new skill should be numbered, briefly explaining the trade-off from rule `06`. If the human confirms, assign a number per rule `08` and prefix both the skill's folder name and its `name:` field with that number (e.g. `344-assess-codebase`). If declined, or when in doubt, default to no numeric prefix.

#### 08-number-assignment

Once a scope has opted in (rule `07`) and a new skill needs a number:

1. Identify the range from rule `01` whose category best matches the skill's primary purpose.
2. Apply tiebreaker rules from rule `05` if the skill sits on a boundary.
3. Scan all skills across all scopes to find the lowest unoccupied number within that range.
4. If a collision exists between two scopes using the same number, the scope listed last in the root `index.md` wins. Avoid collisions by choosing the next unoccupied number.
5. MUST NOT reuse the number of a skill that was previously deleted from that range.
6. If the preferred range is fully occupied, use the overflow range (900+) and add a comment in the skill's `## Overview` section noting which range it logically belongs to.

## References

- [`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md) — Skill package standards (structure, SKILL.md format; default plain kebab-case naming, not auto-numbered — this policy defines an optional, explicit category-numbering convention some scopes choose to layer on top)
- [`agentme-edr-127`](../../../agentme/edrs/application/127-external-system-adapter-skills.md) — External system adapter skills (base/domain/operation layering that motivates rule `06`; connector skill authoring standards)
