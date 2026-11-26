---
name: agentme-bdr-policy-412-phase-6-validate-and-approve
description: Defines phase 6 of the business and software lifecycle, Validate and Approve - business and governance tests in acceptance, the go/no-go decision, rollout strategy choice and operational readiness. Use when deciding whether and how a change goes live.
apply-to: Every business application, application service or change that passed phase 5
valid-from: 2026-11-26
---

# agentme-bdr-policy-412: Phase 6 - Validate and Approve

## Context and Problem Statement

Go-live decisions are taken on partial evidence, and business, governance and operations each assume another checked what they did not. The consequence of going live must be clear to everyone who approves it.

Question: What is validated and decided in phase 6, who approves, and what must exist when it ends?

## Decision Outcome

**Phase 6 runs group Governance, group Business and performance tests in `acc`, checks operational readiness, and ends with one go/no-go decision whose consequences and rollout strategy are recorded**

### Details

#### 01-objective-and-entry

The objective is a recorded go or no-go. The entry MUST be a build that passed group Development in phase 5 and is deployed to `acc`.

#### 02-activities-and-outputs

Activities and outputs MUST include:

- group Governance tests: the ITGC and business controls of phase 4, with evidence verified by the Control Owner (`agentme-bdr-502`)
- group Business tests: quality, operational readiness and user acceptance (UAT), per `agentme-edr-503` rule 11
- performance runs in `acc`, in parallel with the two groups above (`agentme-edr-503` rule 02)
- operational readiness: business and technical people are ready to operate the new software, procedures, monitoring and incident reaction, shown by rehearsals rather than attendance
- the rollout strategy: dark launch, A/B test, incremental rollout or another, and its rollout plan (`agentme-edr-503` rule 05)
- the gate record of `agentme-bdr-503` rule 04

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Production readiness and go-live approval | | A | | | | | | | C | C | C | | | | C | |

Governance sign-off is a blocking precondition given by the Control Owner (`agentme-bdr-503` rule 02); the Business Owner co-signs when the risk class is high.

#### 04-environments-and-tests

The environment is `acc` (`agentme-adr-301`). The test groups are group Governance, group Business and the group Development performance runs. The three tracks MUST finish before the decision. Governance failures MUST NOT be waived by business (`agentme-edr-503` rule 03). A no-go returns the build to phase 5, or to phase 4 when the design is at fault.

#### 05-xdrs-outputs

XDRS MUST hold the rules for the gate record, the approvers and the skill that produces the record, and the operational readiness checklist as an EDR of subject operations. The record itself lives in the record system (`agentme-bdr-503` rule 04).

#### 06-exit-gate

The approvers of `agentme-bdr-503` rule 01 MUST record the go decision with the consequences, residual risks and rollout strategy. Without a recorded go decision, nothing MUST be deployed to `prd`, including deploys with the feature flag off.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-502`](../governance/502-control-framework-and-standards-setters.md) - Control Owner and standards-setters
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Gate approvals and gate record
- [`agentme-adr-301`](../../adrs/platform/301-computational-environments.md) - Environment `acc`
- [`agentme-edr-503`](../../edrs/governance/503-test-groups-and-release-flow.md) - Test groups, rollout plan and governance exceptions
