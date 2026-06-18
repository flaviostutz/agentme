---
name: 001-review
description: >
   Reviews code changes, xdrs docs or any other files against applicable Policies and reports violations as structured findings.
   Activate this skill when the user asks to review, lint, audit, check, verify, validate, or assess any files or Policies, or when checking whether a document or implementation is consistent with, compliant with, or conforms to a standard or Policy.
   Also activate when you identify a need to check compliance with Policies during implementation.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Performs a structured review of code changes or files against the Policies in the repository, categorizing findings by severity and type, and reporting them without modifying any code.

## Instructions

### Phase 1: Code Gathering

1. Identify changes based on requested scope:
   - For diffs: run and parse `git diff refs/remotes/origin/HEAD`
   - For files: analyze file contents directly

### Phase 2: Policy Compilation

1. Gather all Policies from the Policy root `index.md` (default: `.xdrs/index.md`) starting from the working directory.
   - Policy scopes are controlled by nested folders; some are broad, others domain-specific.
   - Extract frontmatter first to decide whether each Policy should be used for the current review context.
   - All documents present in the collection are considered active.
   - Check `valid-from:` first. If a date is present and has not yet been reached, the decision SHOULD be adopted for new implementations but is not enforced during reviews.
   - Check `apply-to:` second. Keep only Policies whose stated scope fits the files, systems, or workflows under review.
   - Check the decision text itself last for additional boundaries or exceptions that metadata does not encode.
2. Filter relevance based on file types, domains, and architectural patterns in scope.

### Phase 3: Policy Review

1. Cross-reference each file in scope against active, applicable Policies.
   - **Drop any finding that cannot be traced to a specific rule in an Accepted Policy.** General good-practice observations, personal opinions, or inferred issues without an explicit Policy backing must not be reported.
   - Classify as ERROR (mandatory) or WARNING (advisory).
   - Include: location, description, Policy reference (file + line), suggestion.
2. Reduce false positives:
   - Evaluate ERROR findings for mandatory language in the Policy ("must", "always", "never", "required", "mandatory"). Drop or downgrade to WARNING if the language is advisory ("should", "recommended", "advised").
   - Remove findings unrelated to actual changes.
   - Consolidate duplicates.
   - Consider context (existing style, legacy sections, etc.).
3. For related Policies and files, lookup for the specific line number in both the Policy and the code that are related to the finding. This will be used in the reporting phase to provide precise references and actionable suggestions.

### Phase 4: Judgment
1. Judgment criteria (all must be true to keep a finding):
   - Is the violation explicitly stated as a rule in an Accepted Policy using mandatory or advisory language? Templates, examples, and diagrams in Policies are illustrative only — they do not constitute rules. If the only evidence for the violation is an implicit pattern in a code sample or template, drop it.
   - Is there concrete evidence in the code or diff?
   - Is the finding actionable?
   - Would fixing it meaningfully improve compliance with the Policies?

### Phase 5: Reporting

**Report template**
```text
### Code Review Against Policies
Scope: [scope identifier]

## Findings
### 1. [ERROR|WARNING] - [filename:line_number](filename:line_number)
- Title of the finding (<=15 words)
- Policy reference: [policy-file:line_number](policy-file:line_number)
- Why: Brief description of the issue in 20 words
- Fix: Specific action to fix this issue in 15 words
- Relevance: Why this matters / What to watch for in 15 words

### 2. [second finding etc]

## Summary
- Errors: [count]
- Warnings: [count]
- Outcome: [PASS|FAIL]
```

### Constraints
- MUST NOT include any text or explanations outside the required output format.
- MUST NOT edit code. Instruct the user on how to request code changes in suggestions.

## Examples
- A Policy mentions that "Every code MUST have a header comment with author name", if you find a codebase without the author name, report as ERROR.
- A Policy mentions that "Functions SHOULD be no longer than 50 lines", if you find a function with 80 lines, report as WARNING.

## Edge Cases
- If no Policies apply to the scope, output "No applicable Policies found" and skip reporting.
- If a potential violation is in pre-existing code outside the diff, report it as WARNING only.

## References

- [_core-adr-policy-001 - Policies core](../../001-xdrs-core.md)
- [_core-adr-policy-002 - Policy standards](../../002-policy-standards.md)
- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)

