---
name: _core-adr-policy-012-reference-scope-type
description: Defines the `reference` scope type — scopes that hold blueprints, standards, regulations, or reference models meant to be adopted or adapted, not consumed as live services. Covers technical architectures, business procedures, compliance frameworks, and operational standards.
apply-to: All XDRS scope authors declaring reference-type scopes
valid-from: 2026-07-01
---

# _core-adr-policy-012: reference scope type

## Context and Problem Statement

Some XDRS scopes exist to publish standards, regulations, or reference models that teams can adopt or adapt. These include technical blueprints, industry compliance frameworks, business procedure standards, and operational guidelines.

These scopes are structurally different from scopes representing live services or active teams: they describe how something should be done or built, not what is currently running or actively managed.

How should a scope that exists as a reference model or standard be identified?

## Decision Outcome

**Declare `scope-type: reference` for any scope that holds models, standards, or procedures to be adopted or adapted — not live operational content.**

### Details

#### 01-scope-type-name

The scope type defined by this policy is `reference`. A scope MUST declare it by setting `scope-type: reference` in its `index.md` YAML frontmatter.

#### 02-when-to-use

Use `scope-type: reference` when the scope contains:

- Industry standards or compliance frameworks to be adopted or mapped against (e.g., ISO 27001, SOC2, PCI-DSS, GDPR, financial regulations, accounting standards).
- Vendor best-practice patterns or recommended architectures.
- Reference architectures or canonical system blueprints meant to be instantiated or adapted locally.
- Business area procedure standards: how sales processes SHOULD be conducted, how customer data MUST be handled, how marketing communications MUST comply with applicable regulations.
- Operational compliance guidelines: finance controls, accounting procedures, public communication standards, customer data management rules.

Do not use `scope-type: reference` for scopes that represent a live service, an active team, or a production system. Use `scope-type: platform` for those.

#### 03-naming-convention

A scope of type `reference` MUST follow the naming pattern `{domain}-ref-{name}`, where `{domain}` identifies the owning domain or team and `{name}` identifies the specific reference area. Examples: `domain1-ref-mobile`, `security-ref-baseline`, `aws-ref-landing-zone`, `sales-ref-procedures`, `finance-ref-compliance`, `marketing-ref-standards`.

#### 04-content-guidance

Content in a `reference`-type scope describes how something could be done — whether that is building a system, running a business process, or complying with a regulation. It SHOULD NOT describe what is currently deployed or actively managed.

Policies, decisions, and standards here are to be read, adopted, adapted, or mapped — not consumed directly as live service or operational documentation. Examples include:

- Architectural blueprints and system design patterns.
- Sales procedure standards and customer engagement guidelines.
- Accounting, finance, and compliance regulations to be followed by specific teams.
- Marketing and public communication standards, including legal and regulatory constraints.
- Customer data management policies establishing rules for data classification, retention, and handling.

## References

- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — scope-type definition convention and governance application model
- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — scope structure and `scope-type` field definition
