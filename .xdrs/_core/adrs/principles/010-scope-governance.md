---
name: _core-adr-policy-010-scope-governance
description: Defines how scope types and scope-local standards are declared and applied. Covers how to author a custom scope-type policy, how to define scope-local content standards, and how all governance mechanisms (scope-type, follows, scope-local) interact with their precedence chain. Use when defining a new scope type, setting local standards for a scope, or understanding how governance is applied when adding content to a scope.
apply-to: All XDRS scopes, core scopes defining scope types, and tools/agents processing scope content
valid-from: 2026-07-01
---

# _core-adr-policy-010: Scope governance

## Context and Problem Statement

XDRS provides three mechanisms that govern what content belongs in a scope and how it should be structured:

1. **Scope-type standards**: a policy in a `core`-type scope that defines the rules for all scopes of that type.
2. **`follows:` declarations**: a scope explicitly declares that it follows the standards of a named `core`-type scope.
3. **Scope-local standards**: a policy inside a scope that defines content rules specific to that one scope.

Without a clear definition of how these mechanisms are authored and how they interact, tools, agents, and authors cannot reliably determine which standards apply when adding or reviewing content in a scope.

## Decision Outcome

**Define scope types as policies, scope-local standards as named policies, and a clear precedence chain for governance application.**

All scope types — both the five built-in types and any custom types — are defined using the same convention: a `{scope-type}-scope-type` policy in a `core`-type scope. Scope-local standards are optional policies named `{scope-name}-core`. Tools and agents apply all applicable standards in a defined order.

> **Choosing between a scope-local policy and a `-core` sibling scope**: use a `{scope-name}-core` policy (Section B) when the standards apply only to one scope and do not need to be shared. Use a separate `-core` sibling scope (see `_core-adr-policy-011`) when the meta governance needs to be shared with or distributed to other teams, or when it governs a family of scopes sharing the same prefix.

### Details

#### Section A — Scope-type definition standards

##### 01-def-must-live-in-core-scope

A scope-type definition policy MUST be placed in a `core`-type scope (i.e., a scope whose `index.md` declares `scope-type: core`).

##### 02-def-naming

The policy `name` field MUST end with `{scope-type}-scope-type` (e.g., `security-scope-type`, `business-area-scope-type`). The policy file MUST follow the standard numbered filename convention `NNN-{scope-type}-scope-type.md` and MUST be placed in the `principles` subject of any decision type folder within the `core`-type scope (e.g., `_core/adrs/principles/011-core-scope-type.md`).

Note: this naming applies to the **policy name** only, not to any scope directory name. It is distinct from the `-core` scope-name suffix convention defined in `_core-adr-policy-011`.

##### 03-def-required-content

A scope-type definition policy MUST define:

- The scope type name (the value that instances declare in their `scope-type:` field).
- When to use this scope type and what kinds of scopes SHOULD declare it.

##### 04-def-preferred-content

A scope-type definition policy SHOULD define:

- Naming conventions for scope instances of this type.
- What content SHOULD be placed in scopes of this type.
- What content SHOULD NOT be placed in scopes of this type.
- Special instructions on how to organise or write content in scopes of this type.

##### 05-def-instance-declaration

A scope that is an instance of a custom scope type MUST declare `scope-type: {scope-type}` in its `index.md` frontmatter (e.g., `scope-type: business-area`).

##### 06-def-no-underscore-prefix

Custom scope-type names MUST NOT start with `_`. The `_` prefix is reserved for built-in scope types defined in `_core` (currently only `_local`).

##### 07-def-parent-scope-type

A scope-type definition policy MAY declare a parent scope type by including a rule titled `NN-parent-scope-type` in its `### Details` section. The body of that rule MUST reference the parent scope-type name in backticks (e.g., "Instances of this scope type inherit all rules from the `standard` scope type."). Tools and agents MUST resolve the full parent chain transitively. Child scope-type standards override parent standards on any conflict.

##### 08-def-valid-iff-policy-exists

A `scope-type` value in a scope `index.md` is valid if and only if a policy file whose name ends with `{scope-type}-scope-type` exists in the `principles` subject of any `core`-type scope in the workspace. Tools (such as `xdrs-core lint`) MUST enforce this.

---

#### Section B — Scope-local standards

##### 09-local-naming

When a scope wishes to define local content standards specific to itself, it MUST do so in a policy whose `name` field ends with `{scope-name}-core` (e.g., scope `my-team` → policy name ending in `my-team-core`).

Note: this is a **policy name suffix** inside a scope, not a scope directory name. It is distinct from the `-core` scope-name suffix convention in `_core-adr-policy-011`, which refers to a sibling scope directory.

##### 10-local-placement

A scope-local standards policy MUST be placed in the `principles` subject of any type folder within the same scope (e.g., `my-team/adrs/principles/001-my-team-core.md`). Only one such policy per scope is allowed.

##### 11-local-optional

Creating a scope-local standards policy is optional. It SHOULD be created when a scope has specific structural, authoring, or content constraints that differ from `_core` defaults or the scope's declared scope-type standards.

##### 12-local-content

A scope-local standards policy SHOULD define the same kinds of instructions as a scope-type definition policy (rules 03–04 above): naming conventions for content in the scope, allowed content, forbidden content, and organisation rules. These instructions apply only to this one scope.

##### 13-local-mandatory-when-present

When a scope-local standards policy exists, tools and agents MUST apply its instructions as mandatory conventions for any content addition or update within that scope.

---

#### Section C — Governance application and precedence

##### 14-application-follows

A scope's `follows:` frontmatter field lists `core`-type scope names whose policies apply as mandatory conventions to this scope, in addition to `_core`. The last-listed scope takes precedence on conflicts when the same topic is addressed by multiple `follows:` scopes.

##### 15-application-scope-type

When adding or reviewing content in a scope, tools and agents MUST:

1. Read the scope's `scope-type` from its `index.md`.
2. Search the `[type]/principles/` directories of all `core`-type scopes in the workspace for a file whose name ends with `{scope-type}-scope-type.md`.
3. If found, apply its rules as mandatory conventions.
4. If the scope-type policy contains a rule titled `NN-parent-scope-type`, extract the parent type name (backtick-quoted identifier in the rule body) and repeat steps 2–4 for the parent. Continue until no more parents are declared. Detect and stop on cycles.

##### 16-application-local

When adding or reviewing content in a scope, tools and agents MUST:

1. Search the scope's own `[type]/principles/` directories for a policy file whose name ends with `{scope-name}-core.md`.
2. If found, apply its rules as mandatory conventions for content in that scope.

##### 17-precedence

When multiple standards address the same topic, the following precedence applies (later in the list overrides earlier on conflict):

1. Parent scope-type standards (resolved transitively from the declared scope-type's parent chain)
2. Declared scope-type standards
3. `follows:` scope standards (last-listed `follows:` scope wins among themselves)
4. Scope-local `{scope-name}-core` policy standards

All of the above are subordinate to `_core` structural rules, which MUST NOT be overridden.

##### 18-ordering-custom-types

Custom-type scopes SHOULD be placed in the `standard` position in the root `index.md` ordering (i.e., after `platform` scopes and before `_local`).

## References

- [_core-adr-policy-011 - core scope type](011-core-scope-type.md) — defines the `core` scope type and when to use a `-core` sibling scope vs. a scope-local policy
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure, `follows:` field definition, scope index frontmatter fields
