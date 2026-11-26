---
name: agentme-bdr-policy-413-phase-7-deploy-and-rollout
description: Defines phase 7 of the business and software lifecycle, Deploy and Rollout - applying the approved change to production assets, supporting people, monitoring business and IT health and deciding on rollout steps - and when the phase ends. Use when releasing an approved change to production.
apply-to: Every business application, application service or change approved in phase 6
valid-from: 2026-11-26
---

# agentme-bdr-policy-413: Phase 7 - Deploy and Rollout

## Context and Problem Statement

A deployment is often treated as the end of delivery, although risk remains until the change reaches all users and operations take over. Rollout steps, user support and health monitoring need owners and an exit criterion.

Question: What happens in phase 7, who decides rollout steps, and when does the phase end?

## Decision Outcome

**Phase 7 deploys the approved change to the target assets under the rollout plan, supports people, monitors business and IT health, and ends when the rollout reaches GA, the observation period passes and operations take over**

### Details

#### 01-objective-and-entry

The objective is a change live for all intended users with healthy metrics. The entry MUST be the recorded go decision of phase 6.

#### 02-activities-and-outputs

Activities and outputs MUST include:

- deploying or applying configurations to the target assets: platforms, developed systems, databases and third-party providers
- supporting people on the new tools and systems, with release communication and user-facing documentation
- monitoring business and IT health during each rollout stage, against the stage criteria
- the decision on each rollout step (alpha, beta, GA or the strategy chosen in phase 6) by the Product Owner, with rollback authority staying with the Tech Lead (`agentme-edr-503` rule 05)
- group Production tests: deployment verification and live outcome validation (`agentme-edr-503` rule 12)

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Rollback decision authority | | | C | | | | C | | | A | | | | | | |
| Release/rollout communication and user-facing documentation, including deprecation and sunset notices | | A | | | | | | | | | | | | | | R (Communication/Technical Writer) |

#### 04-environments-and-tests

The environment is `prd` (`agentme-adr-301`). The test group is group Production under the rollout plan. Governance continuous monitoring MUST continue in `prd`. An incident or rollback MUST return the change to phase 5 (`agentme-edr-503` rule 02).

#### 05-xdrs-outputs

Rollout runbooks MUST be EDRs of subject operations. Lessons learned from the rollout MUST be written back to the policies they invalidate (`agentme-edr-012`).

#### 06-exit-gate

The phase ends when the rollout reaches GA, the observation period agreed in the rollout plan passes with healthy business and IT metrics, and operations take over. The Product Owner MUST confirm it (`agentme-bdr-503` rule 01).

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
- [`agentme-adr-301`](../../adrs/platform/301-computational-environments.md) - Environment `prd`
- [`agentme-edr-012`](../../edrs/principles/012-continuous-xdr-enrichment.md) - Continuous XDR enrichment
- [`agentme-edr-503`](../../edrs/governance/503-test-groups-and-release-flow.md) - Rollout plan and group Production
