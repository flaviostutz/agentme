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

The scope type defined by this policy is `core`. A scope MUST declare it by setting `scope-type: core` in its `index.md` YAML frontmatter.

#### 02-when-to-use

`scope-type: core` MUST be used when the scope's purpose is to hold meta governance content for a domain: writing standards, structural templates, process guidance for authoring or reviewing, skill files for domain-specific workflows, and ownership or contact information. It MUST NOT be used for scopes that contain actual rules or decisions intended for other teams to follow.

#### 03-naming-convention

A scope of type `core` MUST have "core" somewhere in its name (e.g., `_core`, `myarea-core`, `security-core`). The `-core` suffix SHOULD be used as the naming pattern. The built-in `_core` scope is the only exception to the suffix requirement.

#### 04-allowed-content

A `core`-type scope SHOULD contain only the following types of content:

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

A scope that is governed by a `core` scope MUST declare this relationship explicitly using `follows: {core-scope-name}` in its `index.md` frontmatter.

#### 07-distribution

A `core`-type scope MAY be distributed to consumers alongside the companion consumable scope, or kept internal to the team that maintains the domain. When distributed, consumers who extend or contribute to the domain scope locally MUST follow its standards. When not distributed, internal contributors MUST still comply.

#### 08-unavailable-core-read-only

A `-core` scope referenced via `follows:` in a companion scope's `index.md` may not be present in the workspace of a consumer of that companion scope. When the referenced `-core` scope is absent, the companion scope MUST be treated as READ-ONLY: no content in it MUST be added, changed, or removed. The scope lacks the meta governance that defines how its content must be authored, and modifications without those standards would produce non-compliant content. Tools and agents MUST NOT propose or apply changes to a READ-ONLY scope and MUST surface the read-only status to the user when the scope is accessed.

#### 09-distribution-advisable

Distributing `-core` scopes alongside their companion consumable scope to downstream consumers SHOULD be done when possible. Having the meta governance available locally allows tools, agents, and contributors to reason about authoring standards, validate content, and apply scope-local conventions correctly. Distribution is not mandatory; the companion scope remains valid and usable in READ-ONLY mode when the `-core` scope is absent (see `08-unavailable-core-read-only`).

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — full scope governance model including when to prefer a `{scope-name}-core` policy (scope-local) vs. this pattern
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure, `follows:` field, scope index frontmatter
