---
name: agentme-bdr-policy-503-lifecycle-gate-approvals
description: Defines who approves the exit of each lifecycle phase, how governance sign-off blocks go-live, who is accountable for go-live, and what the gate record contains and where it lives. Use when preparing, approving or auditing a phase gate or a go/no-go decision.
apply-to: Every change to a business application or application service, at the exit of every lifecycle phase
valid-from: 2026-11-26
---

# agentme-bdr-policy-503: Lifecycle gate approvals

## Context and Problem Statement

`agentme-edr-503` defines test groups and says the business go/no-go is recorded risk acceptance, but no policy names the approvers of each phase exit, how governance and business approvals combine, or what a gate record must hold. Approvals then happen ad hoc and cannot be audited.

Question: Who approves the exit of each lifecycle phase, and what must the record contain?

## Decision Outcome

**Each phase exit has named approvers; governance sign-off by the Control Owner blocks go-live, the Product Owner stays the single accountable approver of go-live, and every gate leaves a record in the record system**

### Details

#### 01-phase-exit-approvers

A phase MUST NOT be left before its exit approvers confirm the exit criteria in the phase policy:

| Phase exit | Approvers |
|---|---|
| 1 Ideation | Product Owner |
| 2 Scope Requirements | Product Owner and Business Owner |
| 3 Risk and Impact Assessment | Risk function confirms the classification is clear |
| 4 Architecture, Security and Control Design | Control Owner, and the standards-setters whose standards apply to the risk class |
| 5 Develop, Build and Configure | Tech Lead, after group Development passes |
| 6 Validate and Approve | Control Owner, Product Owner, and the Business Owner when the risk class is high |
| 7 Deploy and Rollout | Product Owner |
| 8 Operate, Improve and Retire | Control Owner for scheduled control checks and for closing a retirement |

#### 02-governance-signoff-blocks-go-live

Governance sign-off MUST be a blocking precondition of go-live. It is given by the Control Owner confirming that all control checks passed. The Risk function records and approves any exception; a standards-setter approves only exceptions that touch their own standard. Business MUST NOT waive a governance failure (`agentme-edr-503` rule 03).

#### 03-go-live-accountability

The Product Owner MUST stay the single Accountable role for go-live, as the activity "Production readiness and go-live approval" in `agentme-bdr-405`. The Business Owner MUST co-sign when the risk class is high; the organisation defines the classes (`agentme-bdr-004`). The rollout strategy (dark launch, A/B test, incremental rollout) MUST be chosen at this gate and recorded.

#### 04-gate-record

Each gate MUST leave a record in the record system (ticket or GRC tool), not in XDRS. For the phase 6 gate this is in addition to the content required by `agentme-edr-503` rule 04. The record MUST hold: the change and its risk class, the environment, the result of each test group, the control results, the operational-readiness result, the rollout strategy, governance exceptions with owner and due date, and each approver with date. The record MAY cite external evidence identifiers (ticket, report or run ids) and MUST NOT copy evidence content or exploitable details such as vulnerabilities or secrets.

XDRS MUST define the required content, the approvers and the skill that produces the record, so that parties without XDRS access can still read it.

#### 05-human-approvals

Approvals MUST be given by named people. Agents MAY prepare evidence and draft records, and MUST NOT approve a gate.

#### 06-emergency-path

An emergency change follows the path in `agentme-edr-503` rule 06; its gate record MUST be completed afterwards.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Phases and risk classes
- [`agentme-bdr-405`](../operations/405-digital-product-roles-raci.md) - Go-live accountability and RACI rules
- [`agentme-bdr-502`](502-control-framework-and-standards-setters.md) - Control Owner, Risk function and standards-setters
- [`agentme-edr-503`](../../edrs/governance/503-test-groups-and-release-flow.md) - Test groups, rollout plan, governance exceptions and emergency path
