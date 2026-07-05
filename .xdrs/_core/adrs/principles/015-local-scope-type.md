---
name: _core-adr-policy-015-local-scope-type
description: Defines the `_local` scope type — reserved exclusively for the `_local` scope, which holds workspace-local decisions that MUST NOT be distributed or shared outside the current repository. Use when understanding what the `_local` scope type means.
apply-to: All XDRS workspace authors
valid-from: 2026-07-01
---

# _core-adr-policy-015: _local scope type

## Context and Problem Statement

Every XDRS workspace may need project-specific overrides or local decisions that are not applicable elsewhere. These decisions must be kept in the workspace and never distributed or shared. A reserved scope type is needed to identify and enforce this boundary.

## Decision Outcome

**Reserve `scope-type: _local` exclusively for the `_local` scope, which holds workspace-local decisions that MUST NEVER leave the repository.**

### Details

#### 01-scope-type-name

The scope type defined by this policy is `_local`. A scope declares it by setting `scope-type: _local` in its `index.md` YAML frontmatter.

#### 02-when-to-use

Use `scope-type: _local` only for the built-in `_local` scope. This scope type is reserved and MUST NOT be used for any other scope.

The `_local` scope holds project-specific decisions, local overrides, and workspace-specific content that applies only to the current repository. Examples: local tooling decisions, workspace-specific process overrides, temporary decisions during a transition.

#### 03-exclusive-reservation

The value `scope-type: _local` is reserved exclusively for the single scope named `_local`. Other scopes MUST NOT use this scope type.

#### 04-never-distributed

Content in the `_local` scope MUST NOT be shared with or propagated to any other context. It is workspace-local only and is never packaged for distribution.

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — scope-type definition convention and governance application model
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — `_local` structural rules (placement, linking restrictions, root index behaviour)
