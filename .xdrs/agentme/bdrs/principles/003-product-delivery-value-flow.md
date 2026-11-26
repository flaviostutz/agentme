---
name: agentme-bdr-policy-003-product-delivery-value-flow
description: Defines the end-to-end product delivery value chain — how OKRs, roles, artifacts, and the eight lifecycle phases connect from Strategic OKRs through to fulfilled Tactical OKRs. Use as the authoritative reference for understanding how the pieces of the agentme framework fit together.
apply-to: All contexts where understanding the full delivery flow is needed — strategy, planning, onboarding, skill design, and system engineering processes
valid-from: 2026-08-30
---

# agentme-bdr-policy-003: Product delivery value flow

## Context and Problem Statement

The agentme framework defines organisational levels (`agentme-bdr-001`), OKR structure (`agentme-bdr-002`), the lifecycle phases (`agentme-bdr-004`), delivery artefacts (`agentme-bdr-401`), and roles (`agentme-bdr-402` and `agentme-bdr-404`) as independent policies. Without a connecting document, the relationships between these concepts remain implicit — creating gaps in how practitioners understand who hands off what to whom, and how a fulfilled Tactical OKR connects back to the decisions made at the strategic level.

How do OKRs, roles, artefacts, and lifecycle phases connect from Strategic OKRs all the way to measurable outcomes that fulfil Tactical OKRs?

## Decision Outcome

**A value delivery chain that frames the eight lifecycle phases with Strategic and Tactical OKRs before them and an outcome feedback loop after them**

### Details

#### 01-value-chain

Strategic and Tactical OKRs come before the lifecycle phases and outcome measurement comes after them. The phases themselves, their names and numbers are defined only in `agentme-bdr-004` and MUST NOT be redefined here.

| Step | Role | Input | Output / Artefact |
|---|---|---|---|
| Strategic direction | Group / Company / BU | Business context, market signals | Strategic OKRs (annual or multi-quarter) |
| Tactical planning | Product Manager (PM) | Strategic OKRs | Tactical OKRs (quarterly) + prioritised Epics |
| Phases 1 to 8 | Product team and the roles of `agentme-bdr-405` | Tactical OKRs and Epics | Explored, scoped, assessed, designed, built, approved, deployed and operated solution |
| Outcome measurement | Product Owner (PO) + PM | Measurable outcomes | Progress against Tactical OKR Key Results |

#### 02-notes-per-step

Each step MUST be performed as described below.

**Strategic direction**: Strategic OKRs are set at the Group, Company, or Business Unit level. See `agentme-bdr-001` for organisational level definitions and `agentme-bdr-002` for OKR characteristics.

**Tactical planning**: The PM translates Strategic OKRs into quarterly Tactical OKRs and communicates them to Product Owners (POs). The PM also prioritises which Epics should be executed to contribute to those OKRs. Tactical OKRs are owned at the organisation level, not by product teams. See `agentme-bdr-002`.

**Phases 1 and 2**: The PO accepts Tactical OKRs and Epics as the team's delivery mandate. Ideas are explored in phase 1 (`agentme-bdr-407`) and scoped in phase 2 (`agentme-bdr-408`), where Business Analysts decompose Epics into Features and User Stories with testable acceptance criteria that trace to the Tactical OKR objectives (`agentme-bdr-401`).

**Phases 3 and 4**: Risk and impact are assessed (`agentme-bdr-409`) and the Solution Architect, Enterprise Architect, Tech Lead and AI Lead design the architecture, security and controls (`agentme-bdr-410`). Architectural Blueprints are produced when an Epic requires new cross-system standards, platform adoptions, external integrations or significant security or compliance concerns.

**Phase 5**: Engineers implement the refined Stories, producing code, models, agents, configurations and deployments (`agentme-bdr-411`). Engineer sub-types are defined in `agentme-bdr-404`.

**Phases 6 and 7**: The change is validated and approved (`agentme-bdr-412`) and deployed to production (`agentme-bdr-413`).

**Phase 8**: The product team operates and improves the solution and monitors outcomes against the acceptance criteria defined in User Stories and the Key Results of the Tactical OKRs (`agentme-bdr-414`).

**Outcome measurement**: The PO and PM review measurable production outcomes against the Tactical OKR Key Results. When Key Results are met, the Tactical OKR is considered fulfilled. See `agentme-bdr-405` for the accountability split between the PO (team-level outcome measurement) and PM (Tactical OKR fulfillment reporting).

#### 03-parallel-support-roles

The following roles operate in parallel alongside the main value chain. Teams MUST engage these roles in the phases where their contribution is listed. They SHOULD be involved proactively rather than reactively to avoid rework.

| Role | Parallel contribution |
|---|---|
| Project Manager (PjM) | Cross-squad and cross-team dependency coordination; stakeholder management; unblocking delivery in all phases |
| Principal Engineer | Engineering standards, platform guidance, and mentoring that inform phases 4 to 5 |
| Enterprise Architect | Solution, platform, and security architecture standards that inform phases 3 to 4 |
| Business Owner | Business plan and go-live consequences in phases 2 and 6 |
| Specialists (UX Designer, Tester, Business SME, etc.) | Embedded or shared support in specific phases — UX in phases 2 and 5; Testers in phases 5 to 8; Business SME in phases 2 and 3 |

See `agentme-bdr-402` for org-level and cross-team role definitions and `agentme-bdr-404` for team-level and specialist role definitions.

#### 04-operational-okrs-parallel-track

Product teams MAY define Operational OKRs for day-to-day execution tracking. Operational OKRs run in parallel with the delivery chain — they reflect the team's BAU stability and operational health, not the feature delivery flow. They are NOT connected to individual Epics or User Stories. See `agentme-bdr-002` for the full OKR framework.

#### 05-feedback-loop

When outcome measurement confirms that Tactical OKR Key Results are met, the feedback loop closes:

- Fulfilled Tactical OKRs are reported to the Group, Company, or Business Unit level
- Learnings about what worked and what did not MUST be captured and fed into the next Strategic OKR cycle
- The next Strategic OKR cycle begins with strategic direction again, informed by the outcomes of the completed cycle

An unfulfilled Tactical OKR at cycle end MUST be explicitly reviewed — either carried forward with a documented gap, redesigned, or dropped. Silent rollovers are not acceptable. See `agentme-bdr-002` for OKR cycle governance.

## References

- [`agentme-bdr-001`](001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-002`](002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions and rules
- [`agentme-bdr-004`](004-business-and-software-lifecycle.md) — The eight lifecycle phases
- [`agentme-bdr-401`](../operations/401-plan-epic-feature-story.md) — Epic / Feature / User Story planning: structure and OKR connection rules
- [`agentme-bdr-402`](../operations/402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Principal Engineer, Solution Architect, Enterprise Architect and Business Owner definitions
- [`agentme-bdr-404`](../operations/404-team-roles-and-specialists.md) — Digital product roles (team & specialists): full role definitions for all team-level roles and specialists referenced in this policy
- [`agentme-bdr-405`](../operations/405-digital-product-roles-raci.md) — RACI rules and tables assigning decision rights across the phases
- [`agentme-bdr-407`](../operations/407-phase-1-ideation.md) to [`agentme-bdr-414`](../operations/414-phase-8-operate-improve-and-retire.md) — Phase policies
