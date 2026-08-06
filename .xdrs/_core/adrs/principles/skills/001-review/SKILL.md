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
2. **Prerequisites gate — MUST complete before any review work:** For each scope containing files under review, read its `index.md` frontmatter and check for `follows` and `extends` fields. `_core` Policies always apply to all scopes. Perform ALL of the following checks before proceeding; if ANY check fails, output a FAIL result immediately and do not continue the review:
   - **Follows scopes:** If the scope declares `follows:` entries (e.g., `follows: myarea-core, shared-standards`), verify that each listed scope directory exists in the workspace AND contains an accessible `index.md` (e.g., `.xdrs/[scope-name]/index.md`). If any listed scope is missing or its index is unreadable, output: `FAIL — Review cannot proceed: scope \`[scope-name]\` is listed in \`follows\` but its policies are not present in the workspace. Install it before reviewing, as compliance with its governance cannot be verified.`
   - **Extends scopes:** If the scope declares `extends:` entries, verify that each listed scope directory exists in the workspace AND contains an accessible `index.md`. If any listed scope is missing or its index is unreadable, output: `FAIL — Review cannot proceed: scope \`[scope-name]\` is listed in \`extends\` but its policies are not present in the workspace. Install it before reviewing, as inherited policies cannot be verified.`
   - **Local meta-policies:** Scan the scope's `[type]/principles/` directories for all files whose filename title starts with `core` (i.e., `NNN-core.md` or `NNN-core-{qualifier}.md`), excluding scope-type definition files. If any are found but cannot be read, output: `FAIL — Review cannot proceed: local meta-policy \`[filename]\` exists in scope \`[scope-name]\` but could not be read. Without it, full compliance cannot be verified.` Zero matches is valid — absence of local meta-policies is not an error.
   - **Rationale:** A review that silently omits mandatory governance layers produces false PASS results. Every governance layer declared by the scope MUST be loaded and applied; if any layer is inaccessible, the review result is unreliable and MUST be rejected.
   - **Scope-type:** Read the scope's `scope-type` from its `index.md`. Normalise the value to a list: split on commas and trim whitespace (`scope-type: typeA, typeB` becomes `[typeA, typeB]`). For **each** type in the list, search the `[type]/principles/` directories of all `core`-type scopes in the workspace for a file whose name ends with `{scope-type}-scope-type.md`. If the scope declares any `scope-type` elements but no matching file is found for ANY of them, output: `FAIL — Review cannot proceed: scope \`[scope-name]\` declares \`scope-type: [scope-type]\` but no \`[scope-type]-scope-type.md\` policy exists in any \`core\`-type scope in the workspace. The scope is READ-ONLY; install the scope-type governance before reviewing.`
   - Once all prerequisites pass, load the `follows` scopes' Policies and apply them as mandatory governance. Last-listed scope in `follows` takes precedence when the same topic is addressed by multiple scopes.
   - **Scope-type standards (application):** For each declared scope-type (single or comma-separated list), resolve its full ancestor chain (see `_core-adr-policy-010` rule 22): load the primary `{scope-type}-scope-type.md`, load all companion files (`{scope-type}-scope-type-{qualifier}.md`) alphabetically, then follow `NN-parent-scope-type` rules transitively until no more parents are declared. Stop on cycles. Concatenate all resolved chains in declaration order and deduplicate keeping first occurrence. Apply all policies from the deduplicated list as mandatory conventions. Then run conflict detection using the shared module at `.xdrs/_core/adrs/principles/skills/.assets/conflict-detection.md` across all loaded governance layers. See `_core-adr-policy-010` rules 22, 24, and 26 for the full application model.
   - **Extends chain loading (policy documents only):** If the scope declares `extends:` entries (and the extends check above passed), load the inherited policy documents depth-first (see `_core-adr-policy-010` rule 33). For each extends entry in declaration order, recursively resolve that scope's own `extends:` chain, then append its policies. Deduplicate keeping first occurrence. The reviewing scope's own policies take precedence over all inherited policies. Apply the resolved extended policy set as additional context during the review — inherited policies MUST be evaluated for compliance just as if they were authored in this scope.
   - **Local meta-policies (policy documents only):** Apply all found local meta-policy files as mandatory conventions when reviewing policy documents in the scope. Local meta-policies take highest precedence in the chain. See `_core-adr-policy-010` rules 23, 24, and 26.
3. Filter relevance based on file types, domains, and architectural patterns in scope.

### Phase 3: Policy Review

1. Cross-reference each file in scope against active, applicable Policies.
   - **Drop any finding that cannot be traced to a specific rule in an Accepted Policy.** General good-practice observations, personal opinions, or inferred issues without an explicit Policy backing must not be reported.
   - Classify as ERROR (mandatory) or WARNING (advisory).
   - Include: location, description, Policy reference (file + line), suggestion.
   - **Normative language check (Policy documents only):** For every Policy document in scope, verify that normative statements use uppercase BCP 14 keywords as required by `_core-adr-policy-001`. Flag as ERROR when a lowercase `must`, `must not`, `always`, or `never` is used in a normative requirement context (Details or Decision Outcome sections). Flag as WARNING when lowercase `should`, `should not`, `recommended`, `advised`, `may`, `possibly`, or `optionally` appear in a normative or permissive context where the uppercase form is expected. Context sections and question statements are exempt.
   - **Extends chain conflict check:** If the reviewed scope has an `extends:` field, check for undeclared semantic conflicts in the following combinations (use AI judgment; report as ERROR citing `[_core-adr-policy-010.34-extends-conflict-declaration]` for each undeclared conflict found):
     - Between the reviewing scope's own policies and policies from any extended scope (where the same topic is addressed differently and no `## Conflicts` section declares the override).
     - Between two or more extended scopes that address the same topic differently without documented resolution.
     - Between extended scopes' policies and the policies of **all scopes that appear after the reviewed scope in the root index** (those scopes have higher root-index precedence and silently override the inherited policy set for non-extends consumers; if no `## Conflicts` section exists in the later-listed scope's policy to acknowledge the inherited policy it overrides, flag as ERROR).
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

- [_core-adr-policy-001 - XDRS standards](../../001-xdrs-standards.md)
- [_core-adr-policy-002 - Policy standards](../../002-policy-standards.md)
- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)

