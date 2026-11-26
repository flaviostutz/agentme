---
name: agentme-bdr-policy-004-business-and-software-lifecycle
description: Defines the eight-phase business and software lifecycle (Ideation to Operate, Improve and Retire), how it applies per change, and how phases map to roles, environments and test groups. Use when planning, scoping, approving, auditing or operating any business or software change.
apply-to: Every business or software change, from the first idea to retirement, in any application or service scope
valid-from: 2026-11-26
---

# agentme-bdr-policy-004: Business and software lifecycle

## Context and Problem Statement

Delivery policies describe roles, test groups, environments and releases separately. Without one shared sequence, teams skip risk assessment, design controls late, approve go-live without clear consequences, and forget retirement. Business, risk, governance and engineering people need the same names and numbers for the same work.

Question: Which phases does every business or software change go through, and how do they connect to the existing roles, environments and test groups?

## Decision Outcome

**Every change goes through eight canonical phases, each defined in its own policy with objective, activities, RACI, environments and tests, XDRS outputs and an exit gate**

The names and numbers below are canonical. Other policies MUST say "phase N" and cite this policy instead of redefining the phases.

### Details

#### 01-phases

Every change MUST go through these phases, each defined by its policy.

| Phase | Policy | Main outcome |
|---|---|---|
| 1 Ideation | `agentme-bdr-407` | Idea explored with spikes and prototypes, worth scoping |
| 2 Scope Requirements | `agentme-bdr-408` | Business plan, milestones, KPIs, objectives, team and owner |
| 3 Risk and Impact Assessment | `agentme-bdr-409` | Risk classification and legal position are clear |
| 4 Architecture, Security and Control Design | `agentme-bdr-410` | Design, standards, controls and NFRs derived from the risk class |
| 5 Develop, Build and Configure | `agentme-bdr-411` | Solution, platforms and control automation built and tested |
| 6 Validate and Approve | `agentme-bdr-412` | Business and governance tests passed, go-live consequence accepted |
| 7 Deploy and Rollout | `agentme-bdr-413` | Released to production, observed, handed to operations |
| 8 Operate, Improve and Retire | `agentme-bdr-414` | Healthy operation, improvement, controls checks and safe retirement |

#### 02-per-change-application

The lifecycle applies per change, not once per application. A change MUST inherit what the business application and application service scopes already settle (`agentme-bdr-415`) and MUST re-run only the phases whose inputs changed. A change MUST always pass the phase 6 gate before production. A phase MAY overlap with the next one for different parts of the work, but a phase exit gate MUST be passed before the work it covers enters the next phase.

#### 03-mapping-to-environments-and-tests

Each phase MUST use only the environments and test groups mapped to it below.

| Phase | Environments (`agentme-adr-301`) | Test groups (`agentme-edr-503`) |
|---|---|---|
| 1 | `sbx` or local | none |
| 2-4 | none | none |
| 5 | `dev`, `tst` | group Development (performance tests are only prepared) |
| 6 | `acc` | group Governance, group Business, performance tests |
| 7-8 | `prd` | group Production, with continuous Governance monitoring |

#### 04-roles-and-approvals

Role activities are defined in the RACI tables of `agentme-bdr-405` (rules and team operations) and of the phase policies. Exit gate approvers and the approval record follow `agentme-bdr-503`. Standards setters follow `agentme-bdr-502`. Approvals MUST be given by humans; agents MAY prepare the evidence.

#### 05-organisation-defined-scales

Risk scales, classes, appetite and rollout strategies are organisation-defined. This policy and the phase policies MUST NOT fix numeric thresholds. The classification result is recorded as defined in `agentme-bdr-409`.

#### 06-loop-backs-and-emergencies

Findings in a later phase MUST return to the earliest phase whose output they change, and only that part is redone. Urgent production fixes MUST follow the emergency path of `agentme-edr-503` rule 06 and be reviewed afterwards in phase 8. Retirement is a change that goes through phases 3 to 7 and then closes the scope (`agentme-bdr-414`).

#### 07-xdrs-throughout

XDRS MUST be written from the first brainstorm and evolve with each phase (`agentme-bdr-005`). Each phase states which XDRS it creates or updates. Where each kind of content goes is defined in `agentme-bdr-416`.

## References

- [`agentme-bdr-001`](001-company-organizational-levels.md) - Organisational levels
- [`agentme-bdr-003`](003-product-delivery-value-flow.md) - Value flow from OKRs to outcomes, anchored on these phases
- [`agentme-bdr-005`](005-xdrs-single-source-of-truth.md) - XDRS as the single source of truth
- [`agentme-bdr-405`](../operations/405-digital-product-roles-raci.md) - RACI rules
- [`agentme-bdr-407`](../operations/407-phase-1-ideation.md) to [`agentme-bdr-414`](../operations/414-phase-8-operate-improve-and-retire.md) - Phase policies
- [`agentme-bdr-415`](../operations/415-solution-scope-lifecycle.md) - Solution scope lifecycle
- [`agentme-bdr-416`](../operations/416-solution-content-map.md) - Solution content map
- [`agentme-bdr-502`](../governance/502-control-framework-and-standards-setters.md) - Control framework and standards setters
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Gate approvals
- [`agentme-adr-301`](../../adrs/platform/301-computational-environments.md) - Environments
- [`agentme-edr-503`](../../edrs/governance/503-test-groups-and-release-flow.md) - Test groups and release flow
