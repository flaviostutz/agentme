---
name: agentme-bdr-policy-414-phase-8-operate-improve-and-retire
description: Defines phase 8 of the business and software lifecycle, Operate, Improve and Retire - monitoring, incidents, small improvements, routine tasks, scheduled control checks, KPI reporting and safe decommissioning. Use when running a solution in production, improving it or retiring it.
apply-to: Every business application and application service in production, until its retirement completes
valid-from: 2026-11-26
---

# agentme-bdr-policy-414: Phase 8 - Operate, Improve and Retire

## Context and Problem Statement

Operation, improvement and retirement are the longest part of a solution's life, yet they are often undocumented and retirement is improvised, leaving orphaned assets, backups and dependent systems.

Question: What happens in phase 8, who is accountable, and how is a solution retired safely?

## Decision Outcome

**Phase 8 operates the solution, improves it from business and user feedback, runs scheduled control checks and reports KPIs; retirement is a change that runs phases 3 to 7 and ends by closing the scope**

### Details

#### 01-objective-and-entry

The objective is a stable, controlled solution that meets its KPIs until it is no longer needed. The entry MUST be the end of phase 7.

#### 02-activities-and-outputs

Activities and outputs MUST include:

- monitoring of metrics and alarms, solving incidents and fixing bugs, measured with the DORA metrics of `agentme-edr-402`
- small improvements based on business and user feedback; larger changes re-enter at phase 2 and run the phases whose inputs changed (`agentme-bdr-004`)
- routine tasks that keep the system running
- scheduled control checks (ITGC) run and verified by the Control Owner, and governance continuous monitoring in `prd`
- reports on business and IT KPIs

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Production monitoring, alerting, incident response, and post-incident review, including proactive remediation of disclosed vulnerabilities | | | | | | | | | | A (non-AI) | A (AI) | | | | | |
| Cross-team technical emergency declaration and mobilization | I | | C | | | | | | | C | C | A | | | | |
| On-call scheduling and compensation | | | | A | | | | | | | | | | | | |
| Ongoing operational governance (cost/FinOps, security review cadence and access audits, DR/business-continuity drills, vendor/SLA performance monitoring) | | | | | | | | | | A | | C | | | R | |
| Service or system deprecation decision | C | A | | | | | | | | | | | | | | |
| Business metrics instrumentation and tracking | | C | | | A | | | | | C | | | R | | | |
| Team-level outcome measurement (Operational OKRs) | | A | | | | | | | | | | | | | | |
| Tactical OKR fulfillment reporting to the organisation | A | | | | | | | | | | | | | | | |
| Strategic OKR fulfillment review (multi-quarter or annual)⁴ | R | | | | | | | | | | | | | | | |
| OKR cycle retrospective, learnings capture, and unfulfilled-OKR review | A | | | | | | | | | | | | | | | |

⁴ Accountable: Group/Company/Business Unit leadership, outside this role roster; PM is Responsible for aggregating Tactical OKR results upward.

#### 04-environments-and-tests

The environment is `prd`. The test group is group Production, and group Governance continuous monitoring and periodic control checks MUST run in `prd`. Fixes and improvements MUST pass phases 5 and 6 as any change.

#### 05-retirement

Decommissioning MUST be treated as a change. The business MUST announce the retirement and plan it (phase 2), assess the impact on other businesses and systems (phase 3), define the controls for safe removal of assets and backups (phase 4), implement the removal (phase 5), pass the gate (phase 6) and execute it (phase 7). Afterwards the team MUST check the overall state of other businesses and systems that depended on the application. The scope is then closed per `agentme-bdr-415`.

#### 06-xdrs-outputs

Operational runbooks, incident procedures and control check procedures MUST be EDRs of subject operations or governance, kept current as incidents teach new facts (`agentme-edr-012`).

#### 07-exit-gate

Operation has no exit while the solution lives. Retirement MUST end only when the Control Owner confirms that assets and backups were removed safely and that dependent systems are healthy (`agentme-bdr-503` rule 01).

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-415`](415-solution-scope-lifecycle.md) - Closing the scope at retirement
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
- [`agentme-edr-012`](../../edrs/principles/012-continuous-xdr-enrichment.md) - Continuous XDR enrichment
- [`agentme-edr-402`](../../edrs/operations/402-dora-metrics-framework.md) - DORA metrics
