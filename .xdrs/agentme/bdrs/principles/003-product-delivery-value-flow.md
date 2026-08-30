---
name: agentme-bdr-policy-003-product-delivery-value-flow
description: Defines the end-to-end product delivery value chain — how roles, artifacts, and decisions connect from Strategic OKRs through to fulfilled Tactical OKRs. Use as the authoritative reference for understanding how the pieces of the agentme framework fit together.
apply-to: All contexts where understanding the full delivery flow is needed — strategy, planning, onboarding, skill design, and system engineering processes
valid-from: 2026-08-30
---

# agentme-bdr-policy-003: Product delivery value flow

## Context and Problem Statement

The agentme framework defines organisational levels (`agentme-bdr-001`), OKR structure (`agentme-bdr-002`), delivery artefacts (`agentme-bdr-401`), and roles (`agentme-bdr-402`) as independent policies. Without a connecting document, the relationships between these concepts remain implicit — creating gaps in how practitioners understand who hands off what to whom, and how a fulfilled Tactical OKR connects back to the decisions made at the strategic level.

How do roles, artefacts, and decisions connect from Strategic OKRs all the way to measurable outcomes that fulfil Tactical OKRs?

## Decision Outcome

**A defined end-to-end value delivery chain mapping each role's inputs and outputs, the artefacts produced at each stage, and the feedback loop that closes when Tactical OKRs are fulfilled**

### Details

#### 01-value-chain-stages

The delivery value chain consists of the following ordered stages. Each stage produces an artefact that becomes the input for the next stage.

| Stage | Role | Input | Output / Artefact |
|---|---|---|---|
| 1 — Strategic direction | Group / Company / BU | Business context, market signals | Strategic OKRs (annual or multi-quarter) |
| 2 — Tactical planning | Product Manager (PM) | Strategic OKRs | Tactical OKRs (quarterly) + prioritised Epics |
| 3 — Epic definition | Product Owner (PO) | Tactical OKRs | Epics scoped and accepted by the team |
| 4 — Requirements | Business Analyst (BA) or AI BA | Epics | Features + refined User Stories with acceptance criteria |
| 5 — Architecture (conditional) | Solution Architect | Epic requirements | Architectural Blueprints |
| 6 — Technical refinement | Tech Lead / AI Lead | User Stories + Blueprints | Technically refined Stories ready for implementation |
| 7 — Implementation | Engineers (Backend, Frontend, DevOps/Infra, Full Stack, AI) | Refined Stories | Code, models, deployments |
| 8 — Production | Product team | Deployments | Measurable outcomes in production |
| 9 — Outcome measurement | Product Owner (PO) + PM | Measurable outcomes | Progress against Tactical OKR Key Results |

#### 02-stage-notes

**Stage 1 — Strategic direction**: Strategic OKRs are set at the Group, Company, or Business Unit level. See `agentme-bdr-001` for organisational level definitions and `agentme-bdr-002` for OKR characteristics.

**Stage 2 — Tactical planning**: The Product Manager (PM) translates Strategic OKRs into quarterly Tactical OKRs and communicates them to Product Owners (POs). The PM also prioritises which Epics should be executed to contribute to those OKRs. Tactical OKRs are owned at the organisation level, not by product teams. See `agentme-bdr-002`.

**Stage 3 — Epic definition**: The Product Owner (PO) accepts Tactical OKRs and Epics as the team's delivery mandate, scopes them within the team's capacity, and owns the team backlog. See `agentme-bdr-401` for the Epic / Feature / User Story planning structure.

**Stage 4 — Requirements**: The Business Analyst (BA) or AI Business Analyst (AI BA) decomposes Epics into Features and User Stories with testable acceptance criteria. Their work is directly connected to the Tactical OKR objectives — requirements MUST trace to the changes in processes or systems needed to achieve those objectives.

**Stage 5 — Architecture (conditional)**: The Solution Architect is engaged when an Epic requires new cross-system standards, new platform adoptions, integrations with external systems, or solutions with significant security or compliance concerns. When none of those conditions apply, Stage 5 is skipped and teams proceed directly from User Stories to technical refinement.

**Stage 6 — Technical refinement**: The Tech Lead (for non-AI components) and AI Lead (for AI components) add technical detail to User Stories and Architectural Blueprints so that Engineers can implement them without ambiguity.

**Stage 7 — Implementation**: Engineers implement the refined Stories, producing code, models, agents, and deployments. Engineer sub-types are defined in `agentme-bdr-402`.

**Stage 8 — Production**: Deployments reach production. The product team monitors outcomes against the acceptance criteria defined in User Stories and the Key Results of the Tactical OKRs.

**Stage 9 — Outcome measurement**: The PO and PM review measurable production outcomes against the Tactical OKR Key Results. When Key Results are met, the Tactical OKR is considered fulfilled. Learnings from the cycle inform the next Strategic OKR planning round, closing the feedback loop.

#### 03-parallel-support-roles

The following roles operate in parallel alongside the main value chain. They do not produce primary chain artefacts but are essential to flow and quality:

| Role | Parallel contribution |
|---|---|
| Project Manager (PjM) | Cross-squad and cross-team dependency coordination; stakeholder management; unblocking delivery at all stages |
| Principal Engineer | Engineering standards, platform guidance, and mentoring that inform stages 5–7 |
| Specialists (UX Designer, Tester, Business SME, etc.) | Embedded or shared support at specific stages — UX at stage 4 and 6; Testers at stages 7–8; Business SME at stages 3–4 |

See `agentme-bdr-402` for full definitions of all roles referenced here.

#### 04-operational-okrs-parallel-track

Product teams MAY define Operational OKRs for day-to-day execution tracking. Operational OKRs run in parallel with the delivery chain — they reflect the team's BAU stability and operational health, not the feature delivery flow. They are NOT connected to individual Epics or User Stories. See `agentme-bdr-002` for the full OKR framework.

#### 05-feedback-loop

When Stage 9 confirms that Tactical OKR Key Results are met, the feedback loop closes:

- Fulfilled Tactical OKRs are reported to the Group, Company, or Business Unit level
- Learnings about what worked and what did not MUST be captured and fed into the next Strategic OKR cycle
- The next Strategic OKR cycle begins Stage 1 again, informed by the outcomes of the completed cycle

An unfulfilled Tactical OKR at cycle end MUST be explicitly reviewed — either carried forward with a documented gap, redesigned, or dropped. Silent rollovers are not acceptable. See `agentme-bdr-002` for OKR cycle governance.

## References

- [`agentme-bdr-001`](001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-002`](002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions and rules
- [`agentme-bdr-401`](../operations/401-epic-feature-story-planning.md) — Epic / Feature / User Story planning: structure and OKR connection rules
- [`agentme-bdr-402`](../operations/402-digital-product-roles.md) — Digital product roles: full role definitions for all roles referenced in this policy
