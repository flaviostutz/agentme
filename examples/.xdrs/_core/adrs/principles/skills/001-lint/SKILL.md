---
name: 001-lint
description: >
  Reviews code changes or files against applicable XDRs (Decision Records) and reports violations as structured findings. 
  Activate this skill when the user asks to review, lint, or audit code, or when you identify a need to check compliance with XDRs during implementation.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Performs a structured review of code changes or files against the XDRs in the repository, categorizing findings by severity and type, and reporting them without modifying any code.

## Instructions

### Phase 1: Code Gathering

1. Identify changes based on requested scope:
   - For diffs: run and parse `git diff origin/main`
   - For files: analyze file contents directly

### Phase 2: XDR Compilation

1. Gather all Decision Records from `.xdrs/index.md` starting from the working directory.
   - XDR scopes are controlled by nested folders; some are broad, others domain-specific.
   - Extract metadata first (status, impact, scope, applicability) to filter relevant XDRs before deep analysis.
2. Filter relevance based on file types, domains, and architectural patterns in scope.

### Phase 3: XDR Review

1. Cross-reference each file in scope against applicable XDRs.
   - **Drop any finding that cannot be traced to a specific rule in an Accepted XDR.** General good-practice observations, personal opinions, or inferred issues without an explicit XDR backing must not be reported.
   - Classify as ERROR (mandatory) or WARNING (advisory).
   - Include: location, description, XDR reference (file + line), suggestion.
2. Reduce false positives:
   - Evaluate ERROR findings for mandatory language in the XDR ("must", "always", "never", "required", "mandatory"). Drop or downgrade to WARNING if the language is advisory ("should", "recommended", "advised").
   - Remove findings unrelated to actual changes.
   - Consolidate duplicates.
   - Consider context (existing style, legacy sections, etc.).
3. For related XDRs and files, lookup for the specific line number in both the XDR and the code that are related to the finding. This will be used in the reporting phase to provide precise references and actionable suggestions.

### Phase 4: Judgment
1. Judgment criteria (all must be true to keep a finding):
   - Is the violation explicitly stated as a rule in an Accepted XDR using mandatory or advisory language? Templates, examples, and diagrams in XDRs are illustrative only — they do not constitute rules. If the only evidence for the violation is an implicit pattern in a code sample or template, drop it.
   - Is there concrete evidence in the code or diff?
   - Is the finding actionable?
   - Would fixing it meaningfully improve compliance with the XDR?

### Phase 5: Reporting

**Report template**
--------
### Code Review Against XDRs
Scope: [scope identifier]

## Findings
### 1. [ERROR|WARNING] - [filename:line_number](filename:line_number)
- Title of the finding (<=15 words)
- XDR reference: [xdr-file:line_number](xdr-file:line_number)
- Why: Brief description of the issue in 20 words
- Fix: Specific action to fix this issue in 15 words
- Relevance: Why this matters / What to watch for in 15 words

### 2. [second finding etc]

## Summary
- Errors: [count]
- Warnings: [count]
- Outcome: [PASS|FAIL]
--------

### Constraints
- MUST NOT include any text or explanations outside the required output format.
- MUST NOT edit code. Instruct the user on how to request code changes in suggestions.

## Examples
- An XDR mentions that "Every code MUST have a header comment with author name", if you find a codebase without the author name, report as ERROR.
- An XDR mentions that "Functions SHOULD be no longer than 50 lines", if you find a function with 80 lines, report as WARNING.

## Edge Cases
- If no XDRs apply to the scope, output "No applicable XDRs found" and skip reporting.
- If a potential violation is in pre-existing code outside the diff, report it as WARNING only.

## References

- [_core-adr-001 - XDR standards](../../001-xdr-standards.md)
- [_core-adr-003 - Skill standards](../../003-skill-standards.md)

