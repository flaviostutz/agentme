---
name: 001-xdr-lint
description: >
  Reviews code changes or files against applicable XDRs (Decision Records) and reports
  violations as structured findings. Activate this skill when the user asks to review,
  lint, or audit code, or when you identify a need to check compliance with XDRs during implementation.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Performs a structured review of code changes or files against the XDRs in the repository,
categorizing findings by severity and type, and reporting them without modifying any code.

## Instructions

### Phase 1: XDR Compilation

1. Gather all Decision Records from `.xdrs/index.md` starting from the working directory.
   - XDR scopes are controlled by nested folders; some are broad, others domain-specific.
   - Extract metadata first (status, impact, scope, applicability) to filter relevant XDRs before deep analysis.
2. Filter relevance based on file types, domains, and architectural patterns in scope.

### Phase 2: Code Analysis

1. Identify changes based on requested scope:
   - For diffs: run and parse `git diff origin/main`
   - For files: analyze file contents directly
   - For services: scan all files in the service directory
2. Categorize potential findings:
   - Architecture: violations of structural decisions
   - Coding Standards: style and pattern violations
   - Testing: missing or inadequate test coverage
   - Documentation: missing or outdated documentation
   - Security: security practice violations
   - Performance: performance best practice violations
3. Compile specific, measurable rules from each XDR and compare against the changes.
4. Prioritize by criticality: Accepted > Proposed; Impact: critical > high > medium > low.

### Phase 3: Review and Judgment

1. Cross-reference each finding against applicable XDRs.
   - **Drop any finding that cannot be traced to a specific rule in an Accepted XDR.** General good-practice observations, personal opinions, or inferred issues without an explicit XDR backing must not be reported.
   - Classify as ERROR (mandatory) or WARNING (advisory).
   - Include: location, description, XDR reference (file + line), suggestion.
2. Reduce false positives:
   - Re-evaluate ERROR findings for mandatory language in the XDR ("must", "always", "never", "required", "mandatory"). Drop or downgrade to WARNING if the language is advisory ("should", "recommended", "advised").
   - Remove findings unrelated to actual changes.
   - Consolidate duplicates.
   - Consider context (existing style, legacy sections, etc.).
3. Judgment criteria (all must be true to keep a finding):
   - Is the violation explicitly stated in an Accepted XDR? (If no, drop it.)
   - Is there concrete evidence in the code or diff?
   - Is the finding actionable?
   - Would fixing it meaningfully improve compliance with the XDR?

### Phase 4: Reporting

Format each finding as:

```
>> [ERROR|WARNING] [CATEGORY] filename:line_number: Description
   - XDR Reference: .xdrs/scope/type/subject/number-title.md:line_number
   - Rule: Specific rule text from XDR
   - Severity: [ERROR|WARNING]
   - Suggestion: Specific action to fix this issue
   - Context: Why this matters / What to watch for
```

Full output structure:

```
=== Code Review Against XDRs ===
Scope: [scope identifier]
Files Analyzed: [number]
Changes: [+X lines, -Y lines]

=== Findings ===
[findings list]

=== Summary ===
- Errors Found: [count]
- Warnings Found: [count]
- Review Status: [PASS|FAIL]

Affected Files Requiring Changes
[bullet list of files with issues, linked to specific findings and severity]
```

### Constraints

- MUST NOT include any text or explanations outside the required output format.
- MUST NOT edit code. Instruct the user on how to request code changes in suggestions.

## Examples

User: "Review my changes against XDRs"
Agent action: runs `git diff origin/main`, reads `.xdrs/` hierarchy, filters applicable XDRs,
produces structured findings report.

User: "Lint the auth service"
Agent action: scans all files under the auth service directory, applies relevant XDRs,
produces structured findings report.

## Edge Cases

- If no XDRs apply to the scope, output "No applicable XDRs found" and skip reporting.
- If `git diff` fails (no git repo, no remote), fall back to analyzing staged or working tree files.
- If a potential violation is in pre-existing code outside the diff, report it as WARNING only.

## References

- [_general-adr-001 - XDR standards](../../001-xdr-standards.md)
- [_general-adr-003 - Skill standards](../../003-skill-standards.md)

