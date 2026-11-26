---
name: agentme-bdr-policy-415-solution-scope-lifecycle
description: Defines when an XDRS scope for a business or solution is created, split per application, evolved and retired. Use when starting to explore an idea, when more than one application appears, or when a solution is decommissioned.
apply-to: Every business application and application service documented with XDRS
valid-from: 2026-11-26
---

# agentme-bdr-policy-415: Solution scope lifecycle

## Context and Problem Statement

If the XDRS scope of a solution is created late, early decisions live in chats and slides. If one scope mixes several applications, requirements and controls collide. If it is kept forever, it describes systems that no longer exist.

Question: When is the scope of a solution created, split, evolved and retired?

## Decision Outcome

**One scope is created at the first brainstorm for the business application, split into application service scopes when more than one application appears, evolved through all phases and deleted after decommissioning is complete**

### Details

#### 01-create-at-first-brainstorm

The scope of the business application MUST be created when the idea is first brainstormed (phase 1 of `agentme-bdr-004`), before any prototype or requirement is written. The scope model, naming and `extends` chain are defined in `agentme-adr-001`.

#### 02-split-per-application

When the exploration shows that more than one application is involved, the concerns MUST be separated into one scope per application service, extending the scope of the business application. Content that is shared by the applications MUST stay in the business application scope. A split MUST be made when it is detected, even in the middle of a phase, and the documents MUST be moved, not copied.

#### 03-evolve-with-the-solution

Scopes MUST evolve with each phase and with every change to the business or system, through all kinds of content in `agentme-bdr-416`. Documents that no longer describe the solution MUST be edited or deleted (`agentme-bdr-005` rule 03).

#### 04-retire

The scope MUST be kept until decommissioning has completed and its exit gate has passed (`agentme-bdr-414`). Then the final state MUST be tagged in git, the evidence MUST be archived in the record system, and the scope MUST be deleted. Dependent scopes that extend a retired scope MUST be updated before it is deleted.

#### 05-ownership

The Product Owner MUST be accountable for the scope of the business application and the Tech Lead or AI Lead for the scopes of application services (`agentme-bdr-405`).

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle phases
- [`agentme-bdr-005`](../principles/005-xdrs-single-source-of-truth.md) - XDRS as the single source of truth
- [`agentme-bdr-414`](414-phase-8-operate-improve-and-retire.md) - Retirement
- [`agentme-bdr-416`](416-solution-content-map.md) - Where each kind of content goes
- [`agentme-adr-001`](../../adrs/principles/001-business-application-and-application-service-scopes.md) - Scope model and extends chain
- [`_core-adr-policy-010`](../../../_core/adrs/principles/010-scope-governance.md) - Scope governance
