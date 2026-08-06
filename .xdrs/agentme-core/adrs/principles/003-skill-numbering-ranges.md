---
name: agentme-core-adr-policy-003-skill-numbering-ranges
description: >
  Defines a global semantic skill numbering scheme where a skill's number encodes its category
  (connectivity, operation type, and autonomy level), ordered by increasing complexity and risk.
  Human and agentic skills share the same ranges — the number reflects the operation, not the
  executor. Overrides the per-namespace sequential numbering from _core-adr-policy-003 for all
  scopes except _core. Use when assigning a number to a new skill or reviewing whether an
  existing skill number is correct.
apply-to: all agentme scope contributors assigning numbers to new skills
valid-from: 2026-08-06
---

# agentme-core-adr-policy-003: skill numbering ranges

## Context and Problem Statement

[`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md) assigns skill numbers sequentially within each `scope/type/subject/skills/` namespace. As the skill library grows across multiple scopes, namespaces, and automation types, sequential-only numbers give no information about what a skill does or how risky it is to run. Discovering all connector skills, all autonomous-write skills, or all multi-system read skills requires scanning every namespace.

How should skill numbers be structured so that the number itself communicates the skill's category — its external connectivity, operation type, and autonomy level — regardless of which scope or namespace it lives in?

## Decision Outcome

**Skill numbers are globally semantic: the number encodes the skill's category, ordered by increasing complexity and risk. Human and agentic skills share the same ranges — the number reflects the nature of the operation, not who or what executes it. All scopes except `_core` MUST assign skill numbers according to the range table in rule `01`. The per-namespace sequential assignment rule from `_core-adr-policy-003` is overridden by this policy for all scopes other than `_core`.**

### Details

#### 01-range-table

A skill MUST be assigned a number from the range whose category best describes the skill's primary purpose. Each range is exactly 50 numbers wide. Higher numbers indicate higher complexity and risk. Ranges 650–899 are reserved for future categories; MUST NOT be used until a category is formally defined.

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

A connector skill (range 250–299) MUST:
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

When a skill sits on the boundary between two ranges, apply the following tiebreaker rules:

**Template vs. procedure (1–49 vs. 150–199)**
If the skill produces a blank artifact for a human to fill in (template, checklist form), assign it to 1–49 (framework & meta). If the skill walks through the steps to execute a process, assign it to 150–199 (operational & business procedures).

**Live-system integration tests (200–249 vs. 300–349)**
If all external dependencies are mocked or stubbed, assign the skill to 200–249 (testing/QA). If the skill requires a live external system to execute, assign it to 300–349 (read-only, single system).

**Notification side-effect vs. primary write target (400–449 vs. 450–499)**
Writing to a notification or messaging system (Slack, email, webhook) counts as the primary write target only when that write is the main purpose of the skill. If the notification is a side-effect of a write to a different primary system, it does not elevate the skill to multi-system (450–499); the skill stays in 400–449 (single system).

#### 06-number-assignment

When assigning a number to a new skill:

1. Identify the range from rule `01` whose category best matches the skill's primary purpose.
2. Apply tiebreaker rules from rule `05` if the skill sits on a boundary.
3. Scan all skills across all scopes to find the lowest unoccupied number within that range.
4. If a collision exists between two scopes using the same number, the scope listed last in the root `index.md` wins. Avoid collisions by choosing the next unoccupied number.
5. MUST NOT reuse numbers of deleted skills (per [`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md)).
6. If the preferred range is fully occupied, use the overflow range (900+) and add a comment in the skill's `## Overview` section noting which range it logically belongs to.

#### 07-core-exemption

Skills in the `_core` scope (numbers 001–009) are exempt from this policy. They retain their existing sequential numbers and are not required to align with the range table in rule `01`.

## References

- [`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md) — Skill package standards (structure, SKILL.md format, per-namespace sequential numbering — overridden by this policy for non-`_core` scopes)
- [`agentme-edr-127`](../../../agentme/edrs/application/127-external-system-adapter-skills.md) — External system adapter skills (authoring standards for connector skills in the 250–299 range)
