---
name: _core-adr-policy-011-core-scope-type
description: Defines the `core` scope type — meta-governance scopes that hold writing standards, templates, process guidance, and authoring conventions for a domain. Use when creating or evaluating a scope whose purpose is to govern how content is authored in a group of related scopes.
apply-to: All XDRS scope authors and maintainers
valid-from: 2026-06-24
---

# _core-adr-policy-011: core scope type

## Context and Problem Statement

When teams create shared XDRS scopes, they often mix two kinds of content:

- **Consumable policies**: rules and decisions that other teams or repositories must follow.
- **Meta governance**: writing standards, structural templates, skill guidance, ownership definitions, and process rules that govern how content is authored within the domain.

Mixing both kinds makes shared scopes harder to consume selectively and causes confusion about which content represents actual rules versus internal governance for scope contributors.

How should a scope that exists to govern how other scopes are authored be defined and identified?

## Decision Outcome

**Use a dedicated scope of type `core` to hold all meta governance content for a domain.**

A scope declared with `scope-type: core` is reserved for the meta organisation of a scope family. It contains content that governs how policies are written and maintained within the domain — not the actual policies themselves.

### Details

#### 01-scope-type-name

The scope type defined by this policy is `core`. A scope declares it by setting `scope-type: core` in its `index.md` YAML frontmatter.

#### 02-when-to-use

Use `scope-type: core` when the scope's purpose is to hold meta governance content for a domain: writing standards, structural templates, process guidance for authoring or reviewing, skill files for domain-specific workflows, and ownership or contact information. Do not use it for scopes that contain actual rules or decisions intended for other teams to follow.

#### 03-naming-convention

A scope of type `core` MUST have "core" somewhere in its name (e.g., `_core`, `myarea-core`, `security-core`). The `-core` suffix is the recommended pattern. The built-in `_core` scope is the only exception to the suffix requirement.

#### 04-allowed-content

Content that belongs in a `core`-type scope:

- Writing standards and templates specific to the domain.
- Structural conventions for that domain's policies.
- Process guidance for authoring or reviewing policies within the domain.
- Skill files for domain-specific review or authoring workflows.
- Ownership, contact, and governance information for the domain.

#### 05-forbidden-content

Content that MUST NOT be placed in a `core`-type scope:

- Actual rules or constraints for other teams to follow (e.g., security requirements, compliance rules).
- Any policy intended to be enforced by external teams or repositories.

#### 06-follows-required

A scope that is governed by a `core` scope MUST declare this relationship explicitly using `follows: [{core-scope-name}]` in its `index.md` frontmatter.

#### 07-distribution

A `core`-type scope MAY be distributed to consumers alongside the companion consumable scope, or kept internal to the team that maintains the domain. When distributed, consumers who extend or contribute to the domain scope locally MUST follow its standards. When not distributed, internal contributors must still comply.

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — full scope governance model including when to prefer a `{scope-name}-core` policy (scope-local) vs. this pattern
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure, `follows:` field, scope index frontmatter
