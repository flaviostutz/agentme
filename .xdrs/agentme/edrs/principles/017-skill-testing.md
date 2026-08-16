---
name: agentme-edr-policy-017-skill-testing
description: >
  Mandates a SKILL.test.md test file co-located with every skill, defines the test file format (scenarios with trigger, expected behaviour, and assertions), and requires execution before merging any change to the skill. Use when creating, updating, or reviewing skills.
apply-to: contributors working in any scope that directly or transitively follows or extends agentme
valid-from: 2026-08-06
---

# agentme-edr-policy-017: skill testing

## Context and Problem Statement

Skills evolve over time: phases are reworded, routing tables change, constraints are added. Without an executable specification of what the skill must do, regressions are silent — a changed skill may produce incorrect outputs or miss required steps and nothing catches it until a user files a complaint.

How should skill correctness be verified after every change, in a way that is consistent, co-located with the skill, and executable by either a human or an agent?

## Decision Outcome

**Every skill MUST have a `SKILL.test.md` file in the same directory as its `SKILL.md`. The file defines test scenarios with explicit input triggers and falsifiable assertions. It MUST be executed — using the `200-run-skill-tests` skill or manually — before merging any PR that modifies the skill or its test file.**

### Details

#### 01-mandatory-presence

A skill MUST have a `SKILL.test.md` file in the same directory as `SKILL.md`. The absence of `SKILL.test.md` is treated as an ERROR during any review of the skill directory.

#### 02-file-format

`SKILL.test.md` MUST follow this structure exactly:

```markdown
---
skill: [skill-name matching the name: field in SKILL.md frontmatter]
skill-version: "[x.y matching the version in SKILL.md metadata]"
---

## Test Scenarios

### Scenario N: [Short Title]

**Trigger / Input**
[Exact prompt or agent context given to activate and exercise the skill. Must be
specific enough that two independent agents produce comparable outputs.]

**Expected Behaviour**
[Numbered list of steps the skill must perform, derived from its Instructions section.]

**Simulated Human Responses** *(optional — include when the skill has human-in-the-loop pauses)*
1. [Exact text to inject as the human's answer to the first pause point.]
2. [Answer to the second pause point.]
...

**Assertions**
- [ ] [Specific, falsifiable check on the output or behaviour. Start with a verb.]
- [ ] ...
```

Rules:
- MUST contain at least two scenarios: one happy path and one edge or failure case.
- Each scenario MUST have at least two assertions.
- Assertions MUST be falsifiable (a pass/fail determination must be possible without ambiguity).
- Assertion text MUST start with a verb ("Output contains …", "Skill asks …", "Review reports …").
- MUST NOT duplicate SKILL.md content; reference phases by name only when needed.
- `skill-version` in frontmatter MUST be updated whenever `version` in SKILL.md changes.
- **Simulated Human Responses** is optional. Include it when the skill has human-in-the-loop pause points and automated testing is needed. Responses are injected in order at each pause; if responses are exhausted before the skill finishes, the runner captures the remaining output as-is.

#### 03-execution-requirement

`SKILL.test.md` MUST be executed before merging any PR that modifies the skill or its test file. Execution means running each scenario and verifying all assertions pass.

Use the `200-run-skill-tests` skill to execute the file, or run each scenario manually when automation is not available.


## Considered Options

- **Inline test section in SKILL.md** — rejected because it mixes specification and verification, inflating file size past the 6500-word limit and making test-only changes noisy in diffs.
- **External test registry** — rejected because co-location is the simplest discoverability model and matches the skill folder convention already established by `_core-adr-policy-003`.
- **Required only for new skills** — rejected because existing skills carry the same regression risk after every edit.

## References

- [`_core-adr-policy-003`](../../../_core/adrs/principles/003-skill-standards.md) — Skill package standards and folder layout
- [`200-run-skill-tests`](../application/skills/200-run-skill-tests/SKILL.md) — Runner skill that executes `SKILL.test.md` scenarios
