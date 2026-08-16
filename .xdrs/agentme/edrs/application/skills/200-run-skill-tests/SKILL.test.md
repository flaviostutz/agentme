---
skill: 200-run-skill-tests
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Successfully executes scenarios and reports results

**Trigger / Input**
You are an agent with the `200-run-skill-tests` skill loaded. The workspace has a skill at `.agents/skills/001-review` with both `SKILL.md` and `SKILL.test.md` present. The user says:

"Test the skill at `.agents/skills/001-review`"

**Expected Behaviour**
1. Skill resolves the path to the real directory (following the symlink).
2. Skill confirms `SKILL.test.md` is present.
3. Skill reads `SKILL.test.md` in full and parses all scenarios.
4. Skill reads `SKILL.md` and verifies `skill-version` matches.
5. Skill executes each scenario by presenting the trigger to the target skill.
6. Skill evaluates every assertion for each scenario and records PASS or FAIL.
7. Skill outputs a structured report using the mandated template with a final Outcome line.

**Assertions**
- [ ] Output contains `## Skill Test Report: 001-review`.
- [ ] Output contains a `### Scenario` section for each scenario in `SKILL.test.md`.
- [ ] Each scenario section lists individual assertion results as `PASS` or `FAIL`.
- [ ] Output ends with a `## Summary` block containing `Scenarios:`, `Passed:`, `Failed:`, and `Outcome:`.

### Scenario 2: Halts with ERROR when SKILL.test.md is missing

**Trigger / Input**
You are an agent with the `200-run-skill-tests` skill loaded. The workspace has a skill directory `.xdrs/agentme/edrs/application/skills/050-create-javascript-project` that contains `SKILL.md` but no `SKILL.test.md`. The user says:

"Run tests for `.xdrs/agentme/edrs/application/skills/050-create-javascript-project`"

**Expected Behaviour**
1. Skill resolves the path to the directory.
2. Skill checks for `SKILL.test.md` and finds it absent.
3. Skill immediately outputs an ERROR message referencing the missing file and the policy.
4. Skill does NOT proceed to execute any scenarios.

**Assertions**
- [ ] Output contains `ERROR` indicating `SKILL.test.md` was not found.
- [ ] Output references the resolved path of the skill directory.
- [ ] Output does NOT contain any `### Scenario` execution section.
- [ ] Output does NOT contain a `## Summary` report block.

### Scenario 3: Injects simulated human responses when present

**Trigger / Input**
You are an agent with the `200-run-skill-tests` skill loaded. The workspace has a skill at `.xdrs/agentme/edrs/principles/skills/150-plan-mode-consistency` with both `SKILL.md` and `SKILL.test.md` present. Scenario 1 in that `SKILL.test.md` includes a `**Simulated Human Responses**` section with 9 ordered responses. The user says:

"Test the skill at `.xdrs/agentme/edrs/principles/skills/150-plan-mode-consistency`"

**Expected Behaviour**
1. Skill reads `SKILL.test.md` and detects the `**Simulated Human Responses**` section in Scenario 1.
2. When executing Scenario 1, the skill injects each listed response in order each time the target skill pauses for human input.
3. Execution continues through all HITL pause points using the injected responses rather than waiting for a real human.
4. If the response list is exhausted before the skill finishes, the runner notes "Simulated responses exhausted" and captures remaining output as-is.
5. Assertions are evaluated against the full captured output after all injected responses are consumed.

**Assertions**
- [ ] Runner parses the `**Simulated Human Responses**` section and does not ask the user for input during Scenario 1 execution.
- [ ] Output contains the Scenario 1 result section with individual assertion PASS/FAIL results.
- [ ] Output does NOT contain any prompt asking the real user to respond on behalf of the simulated skill interaction.
- [ ] If responses are exhausted, output notes "Simulated responses exhausted" for that scenario.
