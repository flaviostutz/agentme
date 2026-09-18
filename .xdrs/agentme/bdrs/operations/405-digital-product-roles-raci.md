---
name: agentme-bdr-policy-405-digital-product-roles-raci
description: Defines a RACI (Responsible, Accountable, Consulted, Informed) matrix assigning decision rights across the digital-product lifecycle, from team formation through outcome measurement. Use when clarifying who owns a decision, resolving accountability ambiguity, or tracing root cause after a delivery or business-outcome failure.
apply-to: All digital product teams and the roles defined in agentme-bdr-402, agentme-bdr-403, and agentme-bdr-404
valid-from: 2026-09-18
---

# agentme-bdr-policy-405: Digital product roles — RACI

## Context and Problem Statement

`agentme-bdr-401` through `agentme-bdr-404` define roles, team composition, and organisational structure, but no policy assigns explicit decision rights across the product lifecycle. Activities such as workforce planning, vendor selection, cross-team dependency coordination, AI evaluation, and on-call ownership have no named Accountable owner, leaving ambiguity during execution and when a failure must be traced to its cause.

Question: Who is Accountable, Responsible, Consulted, and Informed for each activity across the digital-product lifecycle, from team formation to outcome measurement?

## Decision Outcome

**A RACI matrix covering the full digital-product lifecycle, with exactly one Accountable role per activity**

Activities are grouped into six lifecycle stages, ordered as they occur end to end:

| Lifecycle group | Activities | Main Accountable role(s) |
|---|---|---|
| Team formation & enablement | 5 | Engineering Manager (4), Product Owner (1) |
| Discover | 8 | Product Manager (3), Product Owner (2), Project Manager (2), AI Business Analyst (1) |
| Design | 6 | Tech Lead / AI Lead (3), Product Owner (1), Solution Architect (1), designated Tech Lead (1) |
| Implement | 5 | Tech Lead / AI Lead (4), AI Lead (1) |
| Deliver | 4 | Tech Lead (2), Product Owner (2) |
| Operate | 10 | Product Manager (3), Product Owner (3), Tech Lead / AI Lead (2), Engineering Manager (1), Principal Engineer (1) |

The single RACI matrix in rule `10-raci-activity-matrix` below gives the full per-activity Responsible, Accountable, Consulted, and Informed assignments.

### Details

#### 01-raci-definitions

Accountable (A) is the role that owns the outcome of an activity and answers for its success or failure; exactly one role MUST hold it per activity — for example, the Tech Lead is Accountable for code review quality. Responsible (R) is the role that performs the work under the Accountable role's direction, normally in a tight, continuous communication loop with it — for example, Engineers are Responsible for implementation under the Tech Lead. Consulted (C) is a role whose input MUST be sought before a decision is finalised, typically a cross-team or org-level role with broad hands-on experience — for example, the Solution Architect is Consulted on cross-system architecture. Informed (I) is a role that MUST be notified of a decision or outcome because it affects their own work; Informed MAY extend to business stakeholders outside this roster (Sales, Marketing, Finance, executives) even when they are not tracked as a column — for example, the PM is Informed of production incidents that affect business KPIs.

#### 02-exactly-one-accountable-per-activity

Each activity in this policy MUST have exactly one Accountable role — never zero, never more than one. When an existing decision elsewhere in this scope assigns joint accountability to two roles for one activity, it MUST be split into two separate activities, each with its own single Accountable role, as this policy does with `agentme-bdr-003`'s outcome-measurement stage (split into Team-level outcome measurement, Accountable: PO, and Tactical OKR fulfillment reporting, Accountable: PM; see rule `10-raci-activity-matrix`).

#### 03-accountable-role-must-ensure-communication

The Accountable role for an activity MUST ensure its decision or outcome is actively communicated to, and confirmed understood by, that activity's Responsible, Consulted, and Informed roles — especially across time-zone, distributed, or vendor boundaries where asynchronous handoffs are common. A decision that is correct but not effectively communicated to the people executing it MUST be treated as an accountability failure of the Accountable role. Any role SHOULD escalate suspected misalignment rather than silently proceed on possibly outdated information.

#### 04-accountability-network-and-root-cause-tracing

Activities are interdependent: the Accountable role for a failing activity MAY itself depend on another Accountable role's output from an earlier activity. When reviewing a failure — for example, poor business results traced to poor software quality traced to disorganised engineering work — reviewers MUST trace the chain through each activity's Accountable role until reaching the true root cause, rather than stopping at the first or most visible role. Root-cause tracing MUST exclude external or market factors (for example, recession, competitor action, seasonality) that no role in this roster controls; when a shortfall is due to an irreducible external factor, the Accountable role's obligation is to actively manage, escalate, or re-scope the risk, not to have prevented it.

#### 05-role-collapsing-and-conditional-activities

One person MAY hold more than one role concurrently — for example, the same person acting as PO and Tech Lead in a Simple team per `agentme-bdr-403`. The RACI assignment still attaches to the role, not the individual, and each accountability MUST be reasoned about separately even when one person holds both. On small projects without a dedicated PjM, the PjM's activities in this policy MUST collapse onto the PO by default. An activity MUST only be applied when its triggering condition is present (for example, cross-team scope, AI involvement, regulatory context, or vendor involvement); rigor of execution SHOULD scale with risk rather than with project size alone.

#### 06-accountable-is-not-necessarily-the-executor

The Accountable role MUST ensure an activity happens correctly, but is not required to personally execute it. For example, in a two-person team the Tech Lead remains Accountable for code review occurring even when the reviewer, by necessity, is a peer without the Tech Lead title.

#### 07-scope-boundary

This matrix MUST only be used for activities delivered as a digital-product or feature change. A business objective achieved partly or wholly through non-digital-product levers — marketing campaigns, pricing or discount changes, sales incentives, partnerships — MUST have its accountability owned outside this role roster entirely. Formal regulatory or legal sign-off in a regulated environment likewise sits outside this roster: the Solution Architect and PO remain Accountable for designing to, and including, known compliance requirements, but the approval authority itself (Compliance Officer, Legal, Risk) MUST be Consulted before milestones and Informed of changes, and MUST NOT be treated as an Accountable column in this matrix. The same boundary applies to vendor contract signing and legal terms following the PM's vendor-selection activity in rule `10-raci-activity-matrix`.

#### 08-multi-team-application

Activities MUST be applied per contributing team so that exactly one Accountable role exists per activity even when a Strategic Objective spans many teams: each team's PO remains Accountable for its own epic slice, the PM MUST be the single aggregation point for Tactical OKR fulfillment across teams, and the PjM (or PO, per rule `05-role-collapsing-and-conditional-activities`) MUST be the single cross-team dependency coordinator.

#### 09-role-abbreviations

Activities below use the roles defined in `agentme-bdr-402` and `agentme-bdr-404`: PM (Product Manager), PO (Product Owner), PjM (Project Manager), EM (Engineering Manager), BA (Business Analyst), AI BA (AI Business Analyst). Engineers MUST be read as one grouped column spanning the Backend, Frontend, and Full Stack Engineer sub-types defined in `agentme-bdr-404`; DevOps/Infra Engineer and AI Engineer remain distinct columns. Specialists MUST be read as one grouped column spanning the UX Designer, Tester/QA, Communication, Technical Writer, and Business SME specialist roles defined in `agentme-bdr-404`.

#### 10-raci-activity-matrix

Every activity MUST have exactly one Accountable role, per rule `02-exactly-one-accountable-per-activity`. The matrix below assigns Responsible, Accountable, Consulted, and Informed roles to all 38 activities, ordered top-to-bottom by the natural workflow across the six lifecycle groups: team formation & enablement, Discover, Design, Implement, Deliver, and Operate.

| Group | Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Team formation & enablement | Hiring, onboarding, and offboarding | | | | A | | | | R | R | | | | | |
| Team formation & enablement | Performance management, career growth, and compensation/promotion | | | | A | | | | | | | | | | |
| Team formation & enablement | Workforce planning and capacity allocation | C | | | A | | | | | | | | | | |
| Team formation & enablement | Team health, psychological safety, and retention | I | | | A | | | | | | | | | | |
| Team formation & enablement | Workforce-allocation enforcement (the split defined in `agentme-bdr-402`) and team-building/morale | I | A | | C | | | | R/C | | | | | | |
| Discover | Strategic direction and OKR setting¹ | C | | | | | | | | | | | | | |
| Discover | Tactical OKR translation, epic prioritisation, and business case/ROI justification | A | | | | | | | | | | | | | |
| Discover | Vendor/third-party selection, contract, and SLA negotiation | A | C | | | | | C | | | | | | | |
| Discover | Epic definition, backlog scoping/acceptance, and ongoing scope change management | C | A | | | | | C | | | | | | | |
| Discover | Initial compliance/privacy/risk triage, including breach-notification escalation | | A | | | | | C | | | | | | | C (Business SME) |
| Discover | AI opportunity discovery | | | | | | A | | | | | | | | |
| Discover | Cross-team dependency tracking and schedule/milestone reporting² | | | A | | | | C | | | | | | | |
| Discover | Complex or high-risk stakeholder and issue/risk (RAID) management | C | C | A | | | | | | | | | | | |
| Design | Requirements and user stories | | | | | A (non-AI) | A (AI) | | | | | | | | |
| Design | Architecture blueprint (cross-system) | | | | | | | A | | | | | | | |
| Design | Technical refinement | | | | | | | | A (non-AI) | A (AI) | | | | | |
| Design | UX and interaction design | | A | | | | | | | | | | | | R (UX Designer) |
| Design | Non-functional requirements sign-off (performance, accessibility, availability/reliability, security, privacy-by-design, including third-party assessment) | | | | | | | C | A (non-AI) | A (AI) | C | | | | |
| Design | Cross-team shared-component ownership³ | | | | | | | C | A | | | | | | |
| Implement | Feature or model implementation, including migration, cutover, and legacy decommissioning build work | | | | | | | | A (non-AI) | A (AI) | | R | R | | |
| Implement | Code or model review | | | | | | | | A (non-AI) | A (AI) | | | | | |
| Implement | Independent QA and test execution | | | | | | | | A (non-AI) | A (AI) | | | | | R (Tester/QA) |
| Implement | AI model evaluation, safety, and fairness testing | | | | | | | | | A | C | | | | R (Tester/QA) |
| Implement | Dependency and license compliance | | | | | | | | A | | C | | | | |
| Deliver | CI/CD pipeline and deployment automation | | | | | | | | A | | | | | R | |
| Deliver | Production readiness and go-live approval | | A | | | | | | C | C | | | | C | |
| Deliver | Rollback decision authority | | | C | | | | C | A | | | | | | |
| Deliver | Release/rollout communication and user-facing documentation, including deprecation and sunset notices | | A | | | | | | | | | | | | R (Communication/Technical Writer) |
| Operate | Production monitoring, alerting, incident response, and post-incident review, including proactive remediation of disclosed vulnerabilities | | | | | | | | A (non-AI) | A (AI) | | | | | |
| Operate | Cross-team technical emergency declaration and mobilization | I | | C | | | | | C | C | A | | | | |
| Operate | On-call scheduling and compensation | | | | A | | | | | | | | | | |
| Operate | Ongoing operational governance (cost/FinOps, security review cadence and access audits, DR/business-continuity drills, vendor/SLA performance monitoring) | | | | | | | | A | | C | | | R | |
| Operate | Service or system deprecation decision | C | A | | | | | | | | | | | | |
| Operate | Business metrics instrumentation and tracking | | C | | | A | | | C | | | R | | | |
| Operate | Team-level outcome measurement (Operational OKRs) | | A | | | | | | | | | | | | |
| Operate | Tactical OKR fulfillment reporting to the organisation | A | | | | | | | | | | | | | |
| Operate | Strategic OKR fulfillment review (multi-quarter or annual)⁴ | R | | | | | | | | | | | | | |
| Operate | OKR cycle retrospective, learnings capture, and unfulfilled-OKR review | A | | | | | | | | | | | | | |

¹ Accountable: Group/Company/Business Unit leadership, outside this role roster (see rule `07-scope-boundary`). ² Also Consulted: each contributing team's Tech Lead (non-AI) / AI Lead (AI). ³ Accountable: the shared/platform team's Tech Lead if one exists, otherwise one contributing team's Tech Lead designated by the Solution Architect; other contributing teams' Tech Leads are Informed. ⁴ Accountable: Group/Company/Business Unit leadership, outside this role roster; PM is Responsible for aggregating Tactical OKR results upward.

Tech Lead and AI Lead are Responsible for the technical-ramp-up portion of onboarding; Tech Lead is also Responsible for flagging and protecting technical-debt/operational time on the workforce-allocation-enforcement row and Consulted on capacity trade-offs. Specialist columns (R) apply only when that specialist is engaged on the initiative, per rule `05-role-collapsing-and-conditional-activities`; when not engaged, the Accountable role executes the activity directly.

## References

- [`agentme-bdr-401`](401-plan-epic-feature-story.md) — Epic / Feature / User Story planning: structure referenced by the epic-definition activity
- [`agentme-bdr-402`](402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Principal Engineer, Solution Architect, and the workforce-allocation split
- [`agentme-bdr-403`](403-product-team-composition.md) — Team composition models and known structural gaps, including role-collapsing in Simple teams
- [`agentme-bdr-404`](404-team-roles-and-specialists.md) — Full role definitions for all roles referenced in this matrix, including the Engineering Manager
- [`agentme-bdr-003`](../principles/003-product-delivery-value-flow.md) — Product delivery value flow: the value chain stages this matrix assigns accountability across
