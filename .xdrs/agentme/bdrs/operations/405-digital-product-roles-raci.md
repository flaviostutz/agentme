---
name: agentme-bdr-policy-405-digital-product-roles-raci
description: Defines the RACI (Responsible, Accountable, Consulted, Informed) rules for the digital-product lifecycle - exactly one Accountable per activity - with the activity matrix distributed over the eight phase policies and the team-operations activities kept here. Use when clarifying who owns a decision, resolving accountability ambiguity, or tracing root cause after a delivery or business-outcome failure.
apply-to: All digital product teams and the roles defined in agentme-bdr-402, agentme-bdr-403, and agentme-bdr-404
valid-from: 2026-11-26
---

# agentme-bdr-policy-405: Digital product roles — RACI

## Context and Problem Statement

`agentme-bdr-401` through `agentme-bdr-404` define roles, team composition, and organisational structure, but a role list alone does not assign decision rights across the product lifecycle. Activities such as workforce planning, vendor selection, and on-call ownership need a named Accountable owner, or ambiguity appears during execution and when tracing failure to its cause.

Question: Who is Accountable, Responsible, Consulted, and Informed for each activity across the digital-product lifecycle?

## Decision Outcome

**RACI rules with exactly one Accountable role per activity, and an activity matrix distributed over the eight lifecycle phases of `agentme-bdr-004`, so that each phase policy holds the activities of its phase**

| Group | Policy | Activities | Main Accountable role(s) |
|---|---|---|---|
| Team operations (cross-phase) | this policy, rule `10-raci-activity-matrix` | 5 | Engineering Manager (4), Product Owner (1) |
| 1 Ideation | `agentme-bdr-407` | 2 | AI Business Analyst (1), Product Owner (1) |
| 2 Scope Requirements | `agentme-bdr-408` | 7 | Product Owner (2), Product Manager (1), Business Owner (1), Business Analyst / AI Business Analyst (1), Project Manager (1), outside the roster (1) |
| 3 Risk and Impact Assessment | `agentme-bdr-409` | 2 | Product Owner (1), Project Manager (1) |
| 4 Architecture, Security and Control Design | `agentme-bdr-410` | 7 | Tech Lead / AI Lead (2), Tech Lead (1), Solution Architect (1), Product Manager (1), Enterprise Architect (1), Principal Engineer (1) |
| 5 Develop, Build and Configure | `agentme-bdr-411` | 6 | Tech Lead / AI Lead (3), Tech Lead (2), AI Lead (1) |
| 6 Validate and Approve | `agentme-bdr-412` | 1 | Product Owner (1) |
| 7 Deploy and Rollout | `agentme-bdr-413` | 2 | Tech Lead (1), Product Owner (1) |
| 8 Operate, Improve and Retire | `agentme-bdr-414` | 10 | Product Manager (2), Product Owner (2), Tech Lead / AI Lead (1), Tech Lead (1), Principal Engineer (1), Engineering Manager (1), Business Analyst (1), outside the roster (1) |

### Details

#### 01-raci-definitions

Accountable (A) MUST ensure an activity is done and done correctly, answering for its success or failure; exactly one role holds it per activity — e.g., the Tech Lead is Accountable for code review quality. Responsible (R) performs the task, under the Accountable role's direction and normally in a tight, continuous communication loop with it — e.g., Engineers are Responsible for implementation under the Tech Lead. Consulted (C) MUST participate in the design or decision process before it is finalised, typically a cross-team or org-level role with broad hands-on experience — e.g., the Solution Architect is Consulted on cross-system architecture. Informed (I) MUST receive the resulting reports or information to act on when needed, without shaping the decision; Informed MAY extend to business stakeholders outside this roster (Sales, Finance, executives) even when untracked as a column — e.g., the PM is Informed of production incidents that affect business KPIs.

#### 02-exactly-one-accountable-per-activity

Each activity in this policy and in the phase policies `agentme-bdr-407` to `agentme-bdr-414` MUST have exactly one Accountable role — never zero, never more than one — except where a footnote names an Accountable outside this roster. When an existing decision elsewhere in this scope assigns joint accountability to two roles for one activity, it MUST be split into two separate activities, each with its own single Accountable role, as phase 8 does with outcome measurement (Team-level outcome measurement, Accountable: PO, and Tactical OKR fulfillment reporting, Accountable: PM; see `agentme-bdr-414`).

#### 03-accountable-role-must-ensure-communication

The Accountable role for an activity MUST ensure its decision or outcome is actively communicated to, and confirmed understood by, that activity's Responsible, Consulted, and Informed roles — especially across time-zone, distributed, or vendor boundaries where asynchronous handoffs are common. A decision that is correct but not effectively communicated to the people executing it MUST be treated as an accountability failure of the Accountable role. Any role SHOULD escalate suspected misalignment rather than silently proceed on possibly outdated information.

#### 04-accountability-network-and-root-cause-tracing

Activities are interdependent: the Accountable role for a failing activity MAY itself depend on another Accountable role's output from an earlier activity. When reviewing a failure — for example, poor business results traced to poor software quality traced to disorganised engineering work — reviewers MUST trace the chain through each activity's Accountable role until reaching the true root cause, rather than stopping at the first or most visible role. Root-cause tracing MUST exclude external or market factors (e.g., recession, competitor action, seasonality) that no role in this roster controls; when a shortfall is due to an irreducible external factor, the Accountable role must actively manage, escalate, or re-scope the risk, not prevent it.

#### 05-role-collapsing-and-conditional-activities

One person MAY hold more than one role concurrently — for example, the same person acting as PO and Tech Lead in a Simple team per `agentme-bdr-403`. The RACI assignment still attaches to the role, not the individual, and each accountability MUST be reasoned about separately even when one person holds both. On small projects without a dedicated PjM, the PjM's activities MUST collapse onto the PO by default. An activity MUST only be applied when its triggering condition is present (e.g., cross-team scope, AI involvement, or regulatory/vendor context); rigor of execution SHOULD scale with risk rather than with project size alone. The Control Owner of `agentme-bdr-502` is never collapsed onto a role of the product team.

#### 06-accountable-is-not-necessarily-the-executor

The Accountable role MUST ensure an activity happens correctly, but is not required to personally execute it. For example, in a two-person team the Tech Lead remains Accountable for code review occurring even when the reviewer, by necessity, is a peer without the Tech Lead title.

#### 07-scope-boundary

This matrix MUST only be used for activities delivered as a digital-product or feature change. A business objective achieved partly or wholly through non-digital-product levers — marketing, pricing, sales incentives, or partnerships — MUST have its accountability owned outside this role roster entirely. Formal regulatory or legal sign-off in a regulated environment likewise sits outside this roster: the Solution Architect and PO remain Accountable for designing to, and including, known compliance requirements, but the approval authority itself (Compliance Officer, Legal, Risk) MUST be Consulted before milestones and Informed of changes, and MUST NOT be treated as an Accountable column in this matrix. Their phase approvals are defined in `agentme-bdr-502` and `agentme-bdr-503`. The same boundary applies to vendor contract signing and legal terms following the PM's vendor-selection activity in `agentme-bdr-410`.

#### 08-multi-team-application

Activities MUST be applied per contributing team so that exactly one Accountable role exists per activity even when a Strategic Objective spans many teams: each team's PO remains Accountable for its own epic slice, the PM MUST be the single aggregation point for Tactical OKR fulfillment across teams, and the PjM (or PO, per rule `05-role-collapsing-and-conditional-activities`) MUST be the single cross-team dependency coordinator.

#### 09-role-abbreviations

Activities use the roles defined in `agentme-bdr-402` and `agentme-bdr-404`: PM (Product Manager), PO (Product Owner), PjM (Project Manager), EM (Engineering Manager), BA (Business Analyst), AI BA (AI Business Analyst), EA (Enterprise Architect), BO (Business Owner). Engineers MUST be read as one grouped column spanning the Backend, Frontend, and Full Stack Engineer sub-types defined in `agentme-bdr-404`; DevOps/Infra Engineer and AI Engineer remain distinct columns. Specialists MUST be read as one grouped column spanning the UX Designer, Tester/QA, Communication, Technical Writer, and Business SME specialist roles defined in `agentme-bdr-404`.

#### 10-raci-activity-matrix

The matrix of 42 activities is distributed: each phase policy holds the rows of its phase, and this policy holds the five team-operations rows below. Every table MUST use the same columns, in this order: PM, PO, PjM, EM, BA, AI BA, Solution Architect, Enterprise Architect, Business Owner, Tech Lead, AI Lead, Principal Engineer, Engineers, AI Engineer, DevOps/Infra Engineer, Specialists. Activity names are normative.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hiring, onboarding, and offboarding | | | | A | | | | | | R | R | | | | | |
| Performance management, career growth, and compensation/promotion | | | | A | | | | | | | | | | | | |
| Workforce planning and capacity allocation | C | | | A | | | | | | | | | | | | |
| Team health, psychological safety, and retention | I | | | A | | | | | | | | | | | | |
| Workforce-allocation enforcement (the split defined in `agentme-bdr-402`) and team-building/morale | I | A | | C | | | | | | R | | | | | | |

Tech Lead and AI Lead are Responsible for the technical-ramp-up portion of onboarding; Tech Lead is also Responsible for flagging and protecting technical-debt/operational time on the workforce-allocation-enforcement row. These activities are continuous team activities, not lifecycle phases. Specialist columns (R) apply only when that specialist is engaged, per rule `05-role-collapsing-and-conditional-activities`; when not engaged, the Accountable role executes the activity directly.

#### 11-role-description-must-mirror-the-matrix

Each role's Accountability, Responsibilities, Consulted on, and Informed about fields in `agentme-bdr-402` or `agentme-bdr-404` MUST list the same activity names — footnote markers excluded, `(non-AI)`/`(AI)` qualifiers included — as that role's A/R/C/I assignments in the tables of rule `10-raci-activity-matrix` and of `agentme-bdr-407` to `agentme-bdr-414`. This applies only to roles with a column per rule `09-role-abbreviations`, excluding the Squad Lead (`agentme-bdr-403`, no column) and unnamed Specialists cells. Matrix changes and matching role-field changes MUST ship together; reviewers MUST reject one without the other.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) — Business and software lifecycle: the phases this matrix is distributed over
- [`agentme-bdr-401`](401-plan-epic-feature-story.md) — Epic / Feature / User Story planning: structure referenced by the epic-definition activity
- [`agentme-bdr-402`](402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Business Owner, Enterprise Architect, Principal Engineer, Solution Architect, and the workforce-allocation split
- [`agentme-bdr-403`](403-product-team-composition.md) — Team composition models and known structural gaps, including role-collapsing in Simple teams
- [`agentme-bdr-404`](404-team-roles-and-specialists.md) — Full role definitions for all roles referenced in this matrix, including the Engineering Manager
- [`agentme-bdr-407`](407-phase-1-ideation.md) to [`agentme-bdr-414`](414-phase-8-operate-improve-and-retire.md) — Phase policies that hold the activity rows
- [`agentme-bdr-502`](../governance/502-control-framework-and-standards-setters.md) — Control Owner, Risk function and standards-setters outside this matrix
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) — Phase gate approvals
