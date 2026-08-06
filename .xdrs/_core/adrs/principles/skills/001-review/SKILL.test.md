---
skill: 001-review
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Policy violation detected in a file

**Trigger / Input**
You are an agent with the `001-review` skill loaded. The XDRS root index is present at `.xdrs/index.md` and all scopes are accessible. Review the following inline file content for compliance:

```markdown
<!-- file: src/example.ts -->
// this function must always return a value
function compute(x: number) {
  return x * 2;
}
```

A policy in the workspace states: "All functions MUST include a JSDoc comment with a `@param` and `@returns` tag."

**Expected Behaviour**
1. Skill reads `.xdrs/index.md` and compiles active policies.
2. Skill completes the prerequisites gate without failure.
3. Skill identifies that `compute` lacks a JSDoc comment with `@param` and `@returns`.
4. Skill reports the finding with ERROR severity, referencing the violated policy, the filename, and a fix suggestion.
5. Skill produces the structured report using the mandated template.

**Assertions**
- [ ] Output contains at least one `ERROR` finding.
- [ ] The finding references the policy file or rule that mandates JSDoc comments.
- [ ] The finding includes a file location reference (`src/example.ts`).
- [ ] Output contains a `Fix:` suggestion for the finding.
- [ ] Output ends with a `## Summary` section listing error count and `Outcome: FAIL`.

### Scenario 2: Compliant file produces no findings

**Trigger / Input**
You are an agent with the `001-review` skill loaded. Review the following inline file for compliance against the same policy ("All functions MUST include a JSDoc comment with `@param` and `@returns`"):

```typescript
/**
 * Computes the double of a number.
 * @param x - The input value.
 * @returns The doubled value.
 */
function compute(x: number): number {
  return x * 2;
}
```

**Expected Behaviour**
1. Skill compiles active policies.
2. Skill finds no violations in the reviewed function.
3. Skill reports 0 errors and 0 warnings.
4. Outcome is PASS.

**Assertions**
- [ ] Output contains `Errors: 0`.
- [ ] Output contains `Outcome: PASS`.
- [ ] Output does NOT contain any `ERROR` finding block.

### Scenario 3: Prerequisites gate rejects review when a required scope is missing

**Trigger / Input**
You are an agent with the `001-review` skill loaded. The workspace scope at `.xdrs/my-scope/index.md` declares `follows: missing-scope`. The `missing-scope` directory does not exist in the workspace. Review any file within `my-scope`.

**Expected Behaviour**
1. Skill reaches the prerequisites gate in Phase 2.
2. Skill detects that `missing-scope` is declared in `follows:` but its directory is absent.
3. Skill immediately outputs a `FAIL` result explaining the missing scope.
4. Skill does NOT produce any policy findings for the file content — it halts after the gate.

**Assertions**
- [ ] Output contains `FAIL` as the gate result.
- [ ] Output names `missing-scope` as the reason for failure.
- [ ] Output does NOT contain any `## Findings` section with file-level findings.
- [ ] Output explicitly states the review cannot proceed.
