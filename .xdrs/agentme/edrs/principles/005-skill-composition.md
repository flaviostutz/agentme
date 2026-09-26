---
name: agentme-edr-policy-005-skill-composition
description: Defines how one skill may use another skill (only through a prose step that activates it) and forbids a skill's scripts from executing, importing or reading another skill's scripts or files. Use when writing or reviewing a skill that depends on another skill.
apply-to: All skills in the agentme scope and in any scope that directly or transitively follows or extends agentme
valid-from: 2026-09-26
---

# agentme-edr-policy-005: Skill composition

## Context and Problem Statement

Skills that call each other's scripts by path break when a skill is renamed, bundled or distributed alone, and they bypass the called skill's own checks (auth, confirmations, known issues). How may one skill use another?

## Decision Outcome

**Compose skills through prose activation only**

A skill uses another skill only by activating it in a prose step; the activated skill decides how to fulfil the request with its own instructions and scripts.

### Details

#### 01-activate-other-skills-in-prose

A skill that depends on another skill MUST activate it with an explicit prose step naming the skill and the goal, for example "Step 4: Run skill `get-github-contents` to list the PR comments." The step MAY pass inputs (URLs, JSON items, file paths) and MUST state which outputs it expects back. The activated skill's own confirmations, halt conditions and known issues apply unchanged.

A bundling-enabled skill MUST list every skill it activates in its `DEPS` per [_core-adr-policy-021](../../../_core/adrs/principles/021-skill-bundling.md).

#### 02-no-cross-skill-script-calls

A skill's scripts MUST NOT execute, `require`/`import`, or read another skill's scripts or files, including by relative path, and MUST NOT depend on another skill's folder layout. Helpers needed by two skills MUST be copied into each skill's own `scripts/` folder, containing only what that skill uses.

## Considered Options

- **Shared script library across skills** - rejected because a rename or partial distribution breaks every caller, and callers skip the owning skill's checks.

## References

- [agentme-edr-127](../application/127-external-system-adapter-skills.md) - external system contents skills built on this composition model
- [_core-adr-policy-003](../../../_core/adrs/principles/003-skill-standards.md) - skill standards
