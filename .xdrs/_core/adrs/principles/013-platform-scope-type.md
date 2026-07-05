---
name: _core-adr-policy-013-platform-scope-type
description: Defines the `platform` scope type — scopes that represent existing implementations, live services, or operational areas consumable directly without local instantiation. Use when declaring a scope that documents something that already exists and can be used.
apply-to: All XDRS scope authors declaring platform-type scopes
valid-from: 2026-07-01
---

# _core-adr-policy-013: platform scope type

## Context and Problem Statement

Some XDRS scopes represent existing, live infrastructure or services that teams can consume directly — cloud platforms, shared services, call centres, operational areas. These differ from reference architectures (blueprints to adapt) and from domain scopes (business areas or teams): they define something that already exists and is ready to be used.

How should a scope that documents a live, consumable platform or service be identified?

## Decision Outcome

**Declare `scope-type: platform` for any scope that represents an existing implementation or operational area that can be consumed directly.**

### Details

#### 01-scope-type-name

The scope type defined by this policy is `platform`. A scope MUST declare it by setting `scope-type: platform` in its `index.md` YAML frontmatter.

#### 02-when-to-use

`scope-type: platform` MUST be used when the scope documents:

- An existing cloud or runtime environment that teams can deploy to directly.
- A shared foundational service available for consumption (e.g., a payment platform, a data platform, a messaging service).
- An operational area or live capability that can be used without local instantiation.

`scope-type: platform` MUST NOT be used for blueprints or reference architectures — use `scope-type: reference` for those. It MUST NOT be used for business domains, products, or teams — use `scope-type: standard` for those.

#### 03-naming-convention

A scope of type `platform` MUST follow the naming pattern `{domain}-plat-{name}`, where `{domain}` identifies the owning domain or team and `{name}` identifies the specific platform area. Examples: `domain2-plat-aws`, `domain2-plat-callcenter`, `cloud-plat-infra`.

#### 04-content-guidance

Content in a `platform`-type scope SHOULD describe what is available, how to access it, what decisions govern its use, and what constraints or service levels apply. It MUST document a live service — not a blueprint to copy.

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — scope-type definition convention and governance application model
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure and `scope-type` field definition
