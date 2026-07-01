---
name: _core-adr-policy-014-standard-scope-type
description: Defines the `standard` scope type — the default type for business areas, product domains, teams, or any general-purpose scope that does not fit the more specific types. Use when declaring any scope that is not a meta-governance scope, a reference model, a live platform, or workspace-local.
apply-to: All XDRS scope authors declaring standard-type scopes
valid-from: 2026-07-01
---

# _core-adr-policy-014: standard scope type

## Context and Problem Statement

Most XDRS scopes represent a business area, a product, a team, or a general grouping of decisions that does not fit the characteristics of the more specific scope types (`core`, `reference`, `platform`, `_local`). A default scope type is needed for these general-purpose scopes.

## Decision Outcome

**Declare `scope-type: standard` for any scope that represents a business area, product domain, team, or general grouping of decisions.**

`standard` is the default scope type. When no other type fits, use `standard`.

### Details

#### 01-scope-type-name

The scope type defined by this policy is `standard`. A scope declares it by setting `scope-type: standard` in its `index.md` YAML frontmatter.

#### 02-when-to-use

Use `scope-type: standard` for:

- Business areas, business units, or product lines.
- Product or feature team scopes.
- Cross-cutting engineering or architecture scopes that are not a platform or reference model.
- Any scope that does not fit `core`, `reference`, `platform`, or `_local`.

This is the default scope type. When uncertain, use `standard`.

#### 03-naming-convention

There is no naming requirement for `standard`-type scopes. Any valid scope name is acceptable (e.g., `business-x`, `team-43`, `mobile-app`, `checkout`).

#### 04-ordering

In the root `index.md`, `standard`-type scopes are placed after `platform` scopes and before `_local`. Custom scope types should also be placed in this position. Scopes listed later override scopes listed earlier on the same topic.

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — scope-type definition convention and governance application model
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure and `scope-type` field definition
