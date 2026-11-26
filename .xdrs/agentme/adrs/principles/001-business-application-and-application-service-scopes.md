---
name: agentme-adr-policy-001-business-application-and-service-scopes
description: Defines the XDRS scope model for a business solution - one scope per business application and one per application service, linked through extends - and what extends does and does not inherit. Use when creating, splitting or organising the scopes of a solution.
apply-to: Every business application and application service documented with XDRS that extends agentme
valid-from: 2026-11-26
---

# agentme-adr-policy-001: Business application and service scopes

## Context and Problem Statement

A business solution may be a single application or several applications that serve one business. One scope for everything mixes unrelated requirements and controls, while many unlinked scopes duplicate shared policies. The `extends` relation of scopes inherits only part of the content, which surprises agents that load a single scope.

Question: How are the scopes of a business solution organised, and what must agents load?

## Decision Outcome

**One scope per Business Application (BA) and one per Application Service (AS), where each AS scope extends its BA scope and the BA scope extends agentme**

### Details

#### 01-scope-per-ba-and-as

A Business Application is the business capability being delivered and has one or more Application Services, each an independently deployable application. There MUST be one scope for the BA and one scope for each AS. A BA with a single application MAY have only the BA scope until a second application appears (`agentme-bdr-415`).

#### 02-extends-chain

The BA scope MUST declare `extends: agentme` and each AS scope MUST declare `extends` with the BA scope name, following `_core-adr-policy-010`. Scopes MUST be `scope-type: standard` and kept in one repository (monorepo). Scope names MUST be `<ba>` for the BA and `<ba>-<as>` for an AS.

#### 03-placement-of-content

Content common to the BA (business policies, risk classification, shared controls and standards) MUST be in the BA scope. Content specific to one application MUST be in its AS scope. An AS scope MAY override a decision of its BA only with a `## Conflicts` section in the overriding policy.

#### 04-extends-inherits-policies-only

The `extends` relation inherits only policy documents. Skills, articles, research and initiatives of an extended scope are not inherited. Agents and checks MUST load the policies and the skills from the whole extends chain, and MUST NOT assume a skill is absent because it is not in the AS scope.

#### 05-extends-constraints

Declaration and precedence MUST follow `_core-adr-policy-010`: `extends` and `follows` are disjoint, `_core` and `_local` are not named, a scope does not extend itself, there are no cycles, and in the case of conflicts the depth-first order of the chain defines precedence.

## References

- [`agentme-bdr-415`](../../bdrs/operations/415-solution-scope-lifecycle.md) - When scopes are created, split and retired
- [`agentme-bdr-416`](../../bdrs/operations/416-solution-content-map.md) - Where each kind of content goes
- [`agentme-edr-019`](../../edrs/principles/019-policies-as-automated-checks-and-agent-context.md) - Loading the context of a scope
- [`_core-adr-policy-010`](../../../_core/adrs/principles/010-scope-governance.md) - Scope governance and extends
- [`_core-adr-policy-014`](../../../_core/adrs/principles/014-standard-scope-type.md) - Standard scope type
