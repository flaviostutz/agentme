---
name: _core-adr-policy-010-core-scope-naming-convention
description: Defines the -core suffix naming convention for XDRS scopes used to hold meta governance content such as writing standards, structural templates, ownership, and process guidance for a domain. Use when designing or evaluating shared scopes.
apply-to: All XDRS scope authors and maintainers
valid-from: 2026-06-24
---

# _core-adr-policy-010: Core scope naming convention

## Context and Problem Statement

When teams create shared XDRS scopes (e.g., `security-standards`, `platform-engineering`), they often mix two kinds of content:

- **Consumable policies**: rules and decisions that other teams or repositories must follow.
- **Meta governance**: writing standards, structural templates, skill guidance, ownership definitions, and process rules that govern how content is authored within the domain.

Mixing both kinds makes shared scopes harder to consume selectively and causes confusion about which content represents actual rules versus internal governance for scope contributors.

How should teams separate meta governance from consumable policies within a scope domain?

## Decision Outcome

**Use a `-core` suffix sibling scope to hold all meta governance content for a domain.**

A scope named `[domain]-core` (e.g., `security-core`, `platform-core`) is reserved for the meta organization of the `[domain]` scope family. It contains content that governs how policies are written and maintained within the domain — not the actual policies themselves.

### Details

#### 01-core-suffix-definition

A scope name ending in `-core` signals that the scope holds meta governance content for scopes sharing the same prefix. It MUST NOT contain policies intended for direct consumption by other teams or repositories.

Content that belongs in a `-core` scope:

- Writing standards and templates specific to the domain.
- Structural conventions for that domain's policies.
- Process guidance for authoring or reviewing policies within the domain.
- Skill files for domain-specific review or authoring workflows.
- Ownership, contact, and governance information for the domain.

Content that does NOT belong in a `-core` scope:

- Actual rules or constraints for other teams to follow (e.g., security requirements, compliance rules).
- Any policy intended to be enforced by external teams or repositories.

#### 02-core-governs-same-prefix-scopes

All XDRS scopes sharing the same prefix as a `-core` scope (e.g., `security-standards`, `security-cloud`) are governed by the standards defined in the corresponding `-core` scope (e.g., `security-core`). Authors of those scopes MUST follow the `-core` scope standards when writing, reviewing, or extending policies in any same-prefix scope.

#### 03-core-scope-is-optional-but-recommended

Creating a `-core` scope is optional. It is strongly recommended whenever a domain scope is intended to be shared with multiple teams or repositories. Separating meta governance into a `-core` scope prevents unnecessary internal content from being distributed to consumers and keeps the consumable scope focused on actual rules.

#### 04-core-vs-local-scope

The `-core` suffix is distinct from the `_local` scope:

- `_local` holds project-specific overrides that are never shared and apply only to the current repository. It is implicitly present in every workspace and may contain a mix of local overrides unrelated to any particular domain.
- A `-core` scope is a formal, named scope scoped to a domain. It can be shared selectively with contributors and is required to be followed by all authors writing content in any same-prefix scope.

Use `_local` when meta governance is relevant only to the current repository. Use a `-core` scope when the governance applies to a named domain shared across teams or repositories.

#### 05-core-scope-distribution

A `-core` scope MAY be distributed to consumers alongside the companion consumable scope, or kept internal to the team that maintains the domain. When distributed, consumers who extend or contribute to the domain scope locally MUST follow its standards. When not distributed, internal contributors must still comply.

## Considered Options

1. **`_local` scope for meta content** — simple to set up, but mixes local project overrides with domain-level governance. Becomes confusing in large teams, especially when `_local` already contains project-specific policies.
2. **Meta content embedded inside the consumable scope** — makes the shared scope noisier and harder for consumers to parse; no clear separation between governance and rules.
3. **`-core` sibling scope (chosen)** — cleanly separates meta governance from consumable content, makes the governance explicit and discoverable, and enables selective distribution.
