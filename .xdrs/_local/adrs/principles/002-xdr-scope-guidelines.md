# _local-adr-002: XDR scope guidelines for agentme

## Context and Problem Statement

The agentme repository contains three XDR scopes (`_general`, `agentme`, and `_local`). Without clear guidelines on which scope should receive which content, contributors may add XDRs to the wrong scope, causing maintenance confusion or unintentional changes to content consumed by external projects.

How should contributors decide which scope to place a new or updated XDR in?

## Decision Outcome

**Each scope has a distinct, non-overlapping purpose. Contributors must place XDRs only in the scope that matches their intent.**

### Scope rules

| Scope | Rule |
|-------|------|
| `_general` | **Never add or modify content here.** This scope is imported from an upstream source and is managed externally. Any local changes will be overwritten on the next import. |
| `agentme` | **Add only XDRs and skills meant to be shared with other projects.** Content here is published and consumed by external projects, so changes must be clear, backwards-compatible where possible, and thoroughly reviewed before merging. |
| `_local` | **Add only XDRs that describe how to work within this repository itself.** These are project-internal decisions (conventions, contributor workflows, repo-specific constraints) that must not be shared. |

### Implementation Details

**When adding a new XDR:**

1. If the decision is specific to how this repository is maintained or how contributors should work within it → place it in `_local`.
2. If the decision encodes a reusable best practice or skill intended for other teams and projects to adopt → place it in `agentme`.
3. Never create files inside `_general/` — treat it as read-only.

**When modifying an existing XDR:**

- `_general`: Do not modify. If a general rule needs to be overridden for this project, create an overriding XDR in `agentme` or `_local` and document the conflict.
- `agentme`: Treat changes as a public API change. Verify the change is still non-conflicting with other XDRs and is clear to external consumers.
- `_local`: Modify freely as needed for repository maintenance.

**Scope precedence (later overrides earlier):**

1. `_general` (lowest precedence)
2. `agentme`
3. `_local` (highest precedence)
