---
name: 200-run-skill-tests
description: >
  Executes the SKILL.test.md test scenarios for a given skill, evaluates each assertion against the skill's
  actual output, and reports a pass/fail result per scenario. Activate when the user asks to test, verify,
  or validate a skill, or before merging a PR that modifies a skill or its SKILL.test.md.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Loads `SKILL.test.md` from a skill directory, runs each scenario by invoking the target skill with the specified trigger, evaluates every assertion against the output, and produces a structured test report.

## Instructions

### Phase 1: Locate and Validate SKILL.test.md

1. Accept the skill path from the user (e.g., `.agents/skills/001-review` or `.xdrs/_local/adrs/principles/skills/005-my-skill`). If no path is given, ask: *"Which skill do you want to test? Provide the path to the skill directory."*
2. Resolve the path to the directory containing `SKILL.md`. If the path is a symlink, follow it to the real directory.
3. Check that `SKILL.test.md` exists in the same directory as `SKILL.md`. If it is missing, output:

   ```
   ERROR: SKILL.test.md not found in [resolved path].
   Create it following agentme-edr-policy-017 before running tests.
   ```

   Then halt — do not proceed.
4. Read `SKILL.test.md` in full. Parse the frontmatter (`skill`, `skill-version`) and all `### Scenario N:` sections. Each scenario has three sub-sections: `**Trigger / Input**`, `**Expected Behaviour**`, and `**Assertions**`.
5. Read `SKILL.md` in full to understand what the skill does. Verify that the `skill-version` in `SKILL.test.md` matches the `version` field in `SKILL.md` metadata. If they differ, output a WARNING and continue.

### Phase 2: Execute Scenarios

For each scenario in order:

1. Record the scenario title and number.
2. Present the trigger/input to a fresh agent context with the target skill loaded, exactly as written in `**Trigger / Input**`. Do not add context beyond what the trigger specifies.
3. Capture the full output from the skill execution.
4. Move to Phase 3 for this scenario before executing the next.

### Phase 3: Evaluate Assertions

For each assertion in the current scenario:

1. Read the assertion text.
2. Determine whether the captured output satisfies the assertion. Apply the following rules:
   - An assertion is PASS if the output unambiguously satisfies the stated condition.
   - An assertion is FAIL if the output clearly does not satisfy the condition.
   - An assertion is INCONCLUSIVE if the output is ambiguous with respect to the condition; treat INCONCLUSIVE as FAIL and note the reason.
3. Record the result (PASS / FAIL) and, for FAIL/INCONCLUSIVE, a one-sentence explanation referencing the specific output evidence.

### Phase 4: Report Results

After all scenarios are executed, produce the report using this template exactly:

```
## Skill Test Report: [skill-name] v[skill-version]
Tested: [ISO date]

### Scenario 1: [Title]
- Assertion 1: [PASS|FAIL] — [one-line reason if FAIL]
- Assertion 2: [PASS|FAIL] — [one-line reason if FAIL]
...
Overall: [PASS|FAIL]

### Scenario 2: [Title]
...

---
## Summary
- Scenarios: [total]
- Passed: [count]
- Failed: [count]
- Outcome: [PASS — all scenarios passed | FAIL — [N] scenario(s) failed]
```

A scenario passes only when every one of its assertions passes. The overall outcome is PASS only when every scenario passes.

### Constraints

- MUST NOT modify the skill or its test file.
- MUST execute scenarios in the order they appear in `SKILL.test.md`.
- MUST treat INCONCLUSIVE assertions as FAIL.
- MUST halt and report ERROR if `SKILL.test.md` is absent (Phase 1).
- MUST follow the report template exactly; do not add commentary outside the template.

## Examples

**Input**: "Test the skill at `.agents/skills/001-review`"

- Phase 1 resolves the symlink → `.xdrs/_core/adrs/principles/skills/001-review/`
- Reads `SKILL.test.md`, parses 3 scenarios
- Executes each scenario with the target skill loaded
- Reports per-assertion PASS/FAIL and an overall outcome

**Input**: "Verify `.xdrs/agentme/edrs/application/skills/050-setup-project` before merging"

- Phase 1 reads the real directory (no symlink)
- If `SKILL.test.md` is missing → ERROR and halt
- Otherwise proceeds through all phases

## Edge Cases

- If the skill path does not exist, output `ERROR: skill directory not found at [path].` and halt.
- If `SKILL.test.md` contains no scenarios, output `ERROR: SKILL.test.md has no scenarios.` and halt.
- If the target skill fails to activate (e.g., not registered in VS Code), note this in the report as FAIL with reason "skill could not be activated" and continue to remaining scenarios.
- If `skill-version` in `SKILL.test.md` does not match `SKILL.md`, emit a WARNING at the top of the report but do not halt.

## References

- [`agentme-edr-policy-017`](../../017-skill-testing.md) — Skill testing mandate and SKILL.test.md format specification
- [`_core-adr-policy-003`](../../../../../_core/adrs/principles/003-skill-standards.md) — Skill package standards and folder layout
