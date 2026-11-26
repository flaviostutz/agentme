---
name: agentme-bdr-policy-408-phase-2-scope-requirements
description: Defines phase 2 of the business and software lifecycle, Scope Requirements - business plan, milestones, KPIs, objectives, team and owner assignment - with its entry, activities, RACI, XDRS outputs and exit gate. Use when turning an accepted idea into a scoped, owned and measurable piece of work.
apply-to: Every business application, application service or change whose idea was accepted in phase 1
valid-from: 2026-11-26
---

# agentme-bdr-policy-408: Phase 2 - Scope Requirements

## Context and Problem Statement

Accepted ideas often start building without an agreed plan, KPIs, owners or team, so later phases cannot tell whether the result delivers what the business wanted.

Question: What is settled in phase 2, who is accountable, and what must exist when it ends?

## Decision Outcome

**Phase 2 turns an accepted idea into a business plan with objectives, milestones, KPIs, an assigned team and named owners, plus the requirements that trace to them**

### Details

#### 01-objective-and-entry

The objective is a scoped, owned and measurable mandate. The entry MUST be the Product Owner's acceptance at the phase 1 exit, or a change request from phase 8.

#### 02-activities-and-outputs

Activities and outputs MUST include:

- business plan, milestones, objectives and KPIs, linked to the Tactical OKRs of `agentme-bdr-002`
- epics, features and user stories with acceptance criteria per `agentme-bdr-401`, tracing to those objectives
- usability requirements and data requirements, at the level of what users and the business need
- team assignment and owner assignment: the Business Owner, the Product Owner and the team of `agentme-bdr-403`
- a first list of the applications involved; when more than one application appears, scopes MUST be split per `agentme-bdr-415`

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Strategic direction and OKR setting¹ | C | | | | | | | | | | | | | | | |
| Tactical OKR translation, epic prioritisation, and business case/ROI justification | A | I | | | | | | | | | | | | | | |
| Business plan, milestones, KPIs, and owner assignment | C | R | | | | | | | A | | | | | | | |
| Epic definition, backlog scoping/acceptance, and ongoing scope change management | C | A | | | | | C | | | | | | | | | |
| Requirements and user stories | | | | | A (non-AI) | A (AI) | | | | | | | | | | C (Business SME) |
| UX and interaction design | | A | | | | | | | | | | | | | | R (UX Designer) |
| Cross-team dependency tracking and schedule/milestone reporting² | | | A | | | | C | | | | | | | | | |

¹ Accountable: Group/Company/Business Unit leadership, outside this role roster (`agentme-bdr-405` rule 07). ² Also Consulted: each contributing team's Tech Lead (non-AI) / AI Lead (AI).

#### 04-environments-and-tests

No environment or test group applies. Requirements MUST state the acceptance criteria that phase 6 will test.

#### 05-xdrs-outputs

Business requirements MUST be written as BDRs, usability requirements as BDRs of subject product and data requirements as ADRs of subject data, in the scope of the business application or application service, per `agentme-bdr-416`. The plan and milestones MUST live in an initiative document of that scope.

#### 06-exit-gate

The Product Owner and the Business Owner MUST approve the scope (`agentme-bdr-503` rule 01). A change that alters the plan or KPIs MUST return here and update the same documents.

## References

- [`agentme-bdr-002`](../principles/002-okr-framework.md) - OKR framework
- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview
- [`agentme-bdr-401`](401-plan-epic-feature-story.md) - Epic, feature and user story planning
- [`agentme-bdr-403`](403-product-team-composition.md) - Team composition
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-415`](415-solution-scope-lifecycle.md) - Splitting scopes per application
- [`agentme-bdr-416`](416-solution-content-map.md) - Where each concern is documented
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
