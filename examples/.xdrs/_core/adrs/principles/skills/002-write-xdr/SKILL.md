---
name: 002-write-xdr
description: >
  Creates a new XDR (Decision Record) interactively: selects type, scope, subject, and writes a focused, conflict-checked decision document.
  Activate this skill when the user asks to create, add, or write a new XDR, ADR, BDR, or EDR.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured XDR by following the standards in `_core-adr-001`, researching existing records for conflicts, and iterating until the document is concise and decision-focused.

## Instructions

### Phase 1: Understand the Decision

1. Read `.xdrs/index.md` to discover all active scopes and their canonical indexes.
2. Read `.xdrs/_core/adrs/principles/001-xdr-standards.md` in full to internalize structure rules, mandatory language, and the XDR template.
3. Ask the user (or infer from context) the topic of the decision. Do NOT proceed to Phase 2 without a clear topic.

### Phase 2: Select Type, Scope, and Subject

**Type** — choose exactly one based on the nature of the decision:
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure

**Scope** — use `_local` unless the user explicitly names another scope.

**Subject** — pick one from the allowed list for the chosen type (from `001-xdr-standards`):
- ADR: `principles`, `application`, `data`, `integration`, `platform`, `controls`, `operations`
- BDR: `principles`, `marketing`, `product`, `controls`, `operations`, `organization`, `finance`, `sustainability`
- EDR: `principles`, `application`, `infra`, `ai`, `observability`, `devops`, `governance`

**XDR ID** — format: `[scope]-[type]-[next available number]`
- Scan `.xdrs/[scope]/[type]/` for the highest existing number in that scope+type and increment by 1.
- Never reuse numbers from deleted XDRs.

### Phase 3: Choose the Title

Choose a title that clearly states the question this XDR answers, not the answer itself. The title should let a reader know at a glance what decision scope this record covers.

- Good: "Package manager for Node.js projects", "Phone marketing procedures", "Integration patterns for systems connectivity"
- Avoid: "Use pnpm", "We chose pnpm", or overly vague titles like "Tooling decisions"

### Phase 4: Research Related XDRs

1. Read all existing XDRs relevant to the topic across all scopes listed in `.xdrs/index.md`.
2. Identify decisions that already address the topic (full or partial overlap).
3. Note decisions that might conflict with the intended outcome.
4. Collect XDR IDs and file paths for cross-references.

### Phase 5: Write the First Draft

Use the mandatory template from `001-xdr-standards`:

```
# [scope]-[type]-[number]: [Short Title]

## Context and Problem Statement
[4 lines max: background, who is impacted, and the explicit question being answered]

## Decision Outcome

**[Chosen Option Title]**
[One sentence: what is the decision]

### Implementation Details
[Rules, specifics, examples — under 100 lines]

## Considered Options (if meaningful options exist)

## Conflicts (mandatory if conflicts found in Phase 3)

## References (optional)
```

Mandatory rules to apply while drafting:
- Use mandatory language ("must", "always", "never") only for hard requirements; use advisory language ("should", "recommended") for guidance.
- Do not duplicate content already in referenced XDRs — link instead.
- No emojis. Lowercase filenames.
- Target under 100 lines total; 200 lines max for complex decisions.

### Phase 6: Review the Draft

Check every item before finalizing:

1. **Length**: Is it under 100 lines? Trim verbose explanations. Move detailed skills to a separate file and link.
2. **Originality**: Does every sentence add value that cannot be found in a generic web search? Remove obvious advice. Keep only the project-specific decision.
3. **Clarity**: Is the chosen option unambiguous? Is the "why" clear in one reading?
4. **Conflicts section**: Is it present and filled if Phase 3 found any conflicts?
5. **Index entries**: Will the new XDR be added to `[scope]/[type]/index.md` and `.xdrs/index.md`?

If any check fails, revise and re-run this phase before proceeding.

### Phase 7: Write Files

1. Create the XDR file at `.xdrs/[scope]/[type]/[subject]/[number]-[short-title].md`.
2. Add an entry to `.xdrs/[scope]/[type]/index.md` (create the file if it does not exist).
3. Add or verify the scope entry in `.xdrs/index.md`.

### Constraints

- MUST follow the XDR template from `001-xdr-standards` exactly.
- MUST NOT add personal opinions or general best-practice content not tied to a decision.
- MUST NOT create an XDR that duplicates a decision already captured in another XDR — extend or reference instead.
- MUST keep scope `_local` unless the user explicitly states otherwise.
