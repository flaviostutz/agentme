---
name: agentme-bdr-policy-402-digital-product-roles-org-cross-team
description: Defines organisation-level and cross-team roles — Product Manager, Principal Engineer, and Solution Architect — along with team purpose, scope, workforce allocation, and a roles overview table. Use when staffing or assigning responsibilities at the organisation or cross-team level.
apply-to: Organisation-level and cross-team roles in digital product organisations
valid-from: 2026-08-30
---

# agentme-bdr-policy-402: Digital product roles — org & cross-team

## Context and Problem Statement

Digital product organisations involve roles at multiple levels — from strategy and product direction at the organisation level, through cross-team architectural and engineering standards, to daily execution inside product teams. Without a clear definition of each role's responsibilities, boundaries, and expected skills, ambiguity accumulates about who owns what, leading to gaps in coverage, duplicated effort, and unclear escalation paths.

What roles are involved in building and operating digital products, and what does each role own?

## Decision Outcome

**A defined set of organisation-level, cross-team, team-level, and specialist roles with explicit responsibilities, authority boundaries, and skill requirements**

### Details

#### 01-product-team-purpose

A product team is responsible for a product consumed by others: an API used by another team in the company, a business process used by customers, or a platform that other teams build on.

Strategic objectives typically originate outside the team. However, the team MUST own a defined set of OKRs or KPIs and be fully autonomous within its domain to change processes and implement systems that affect those objectives. The team MUST be accountable for results within its domain; it MUST NOT depend on other teams to execute changes within scope.

#### 02-product-team-scope-of-work

The team MUST own the full lifecycle of its product:

- Model as-is business processes and define to-be target processes
- Design architecture and system components
- Implement and deploy features across all environments
- Test software components, runtime services, and business processes
- Monitor production operation
- Fix incidents and manage production stability
- Communicate outages and new feature rollouts to users

The team MUST NOT hand off any of these responsibilities to a separate function. Ownership is end-to-end.

#### 03-workforce-allocation

Teams MUST allocate available capacity across three categories. These are targets, not rigid weekly quotas — they SHOULD balance over a rolling 4–6 week window:

| Category | Target | Scope |
|---|---|---|
| New features | 50% | Spiking, designing, implementing, and testing new capabilities |
| Tech and cognitive debt | 25% | Reducing complexity, improving maintainability, resolving known deficiencies |
| Operations and controls | 25% | Monitoring, incident response, compliance checks, access reviews, process audits |

#### 04-roles-overview

All roles MUST be filled by a person with the required hard skills. Organisation-level roles MUST operate at the Group, Company, or Business Unit level. Cross-team roles MUST operate across all product teams within a domain. Team-level roles MUST belong to a specific product team.

| Role | Scope | Focus |
|---|---|---|
| Product Manager (PM) | Org-level | What / When |
| Principal Engineer | Cross-team | How |
| Solution Architect | Cross-team | What |
| Product Owner (PO) | Team | What / When |
| Project Manager (PjM) | Team | When / How |
| Business Analyst (BA) | Team / Squad | What / How |
| AI Business Analyst (AI BA) | Team / Squad | What / How |
| AI Lead | Team / Squad | How / When |
| AI Engineer | Squad | How |
| Tech Lead | Team / Squad | How / When |
| Backend Engineer | Squad | How |
| Frontend Engineer | Squad | How |
| DevOps/Infra Engineer | Squad | How |
| Full Stack Engineer | Squad | How |

#### 05-organisation-and-cross-team-roles

The following roles operate at the organisation level (Group, Company, or Business Unit) or across all product teams within a domain. They MUST NOT belong to a single product team.

---

**Product Manager (PM)**

*Purpose*: Own the product direction for the organisation — defining what to build and why — and translate strategic objectives into Tactical OKRs that product teams execute.

*Responsibilities*:
- Translate Strategic OKRs (set at Group, Company, or Business Unit level) into Tactical OKRs for quarterly execution
- Prioritise Epics across product teams to maximise contribution to Tactical OKRs
- Communicate Tactical OKRs and Epic priorities to Product Owners (POs) so teams can execute against them; the PO is the primary recipient of this direction and executes it within the team
- Maintain visibility into the product portfolio and adjust priorities as market or business conditions change
- Own the product roadmap and communicate it to stakeholders

*Authority*: The PM owns WHAT the organisation builds at the portfolio level and WHEN Tactical OKRs are set. The PM does NOT own day-to-day team decisions — those remain with each team's Product Owner and Tech Lead. The PM does NOT set engineering practices or platform choices — those are owned by the Principal Engineer.

*Soft skills*: Strategic thinking, product vision, stakeholder communication, prioritisation across competing goals, ability to synthesise market and business context into clear direction

*Hard skills*: OKR methodology, product roadmap management, market and business analysis, Epic-level prioritisation across multiple product teams

*Common activities*: OKR planning cycles, product roadmap reviews, Epic prioritisation sessions, Product Owner alignment meetings, stakeholder presentations, portfolio health reviews

---

**Principal Engineer**

*Purpose*: Own the HOW across all product teams — engineering practices, tooling standards, platform choices, and AI practices — and synthesise them into a blueprint that leads can apply.

*Responsibilities*:
- Define and maintain engineering standards across all product teams (coding practices, testing, CI/CD, observability)
- Select and standardise platforms and tooling used by teams
- Shape AI engineering practices and the adoption of AI-assisted development
- Connect architecture decisions, business requirements, and standardised platforms into a coherent engineering blueprint
- Mentor Tech Leads and AI Leads on standards and practices
- Connect with Product Manager (PM), Project Manager (PjM), Solution Architects, and team leads to translate, converge, and align the technological landscape, standards, and processes

*Soft skills*: Technical leadership, communication across skill levels, systems thinking, mentoring, cross-team influence — a nexialist connecting engineering, management, architecture, platforms, and product

*Hard skills*: Software architecture, platform engineering, AI/ML practices, CI/CD, observability, security engineering, developer experience

*Common activities*: Engineering standards authoring, tech radar reviews, architecture and platform reviews, Tech Lead and AI Lead mentoring sessions, cross-team engineering syncs

---

**Solution Architect**

*Purpose*: Define the architecture for solutions that require new cross-system standards, new platforms, integrations with external systems, or significant security and compliance concerns.

*Responsibilities*:
- Design architectural solutions for Epics or initiatives that span multiple systems or teams
- Define new integration patterns, platform adoptions, and cross-system standards when existing standards do not cover the need
- Produce architectural blueprints that Tech Leads and AI Leads can implement within their teams
- Assess security, compliance, and risk dimensions of proposed architectures
- Ensure architectural consistency across product teams within the domain

*Soft skills*: Holistic thinking, stakeholder communication, structured documentation, facilitation, ability to balance pragmatism with rigour

*Hard skills*: Enterprise architecture, system integration patterns, cloud architecture, security architecture, business process modelling, platform evaluation, domain-driven design

*Common activities*: Architecture design for complex Epics, blueprint authoring, cross-system integration design, security and compliance assessment, architecture review participation, cross-team design alignment sessions

#### 06-team-and-specialist-roles

Team-level and specialist roles are defined in [`agentme-bdr-404`](404-team-roles-and-specialists.md). Practitioners MUST consult that policy when staffing or onboarding team-level roles.

## References

- [`_core-adr-policy-016`](../../../_core/adrs/principles/016-policy-subjects.md) — Policy subjects: BDR operations subject definition
- [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) — Policy numbering: BDR operations block 401–500
- [`agentme-bdr-001`](../principles/001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-002`](../principles/002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions
- [`agentme-bdr-003`](../principles/003-product-delivery-value-flow.md) — Product delivery value flow: end-to-end chain from Strategic OKRs to fulfilled Tactical OKRs
- [`agentme-bdr-403`](403-product-team-composition.md) — Team composition models, squad dynamics, and known structural gaps
- [`agentme-bdr-404`](404-team-roles-and-specialists.md) — Team-level roles and specialists: PO, PjM, BA, AI BA, AI Lead, AI Engineer, Tech Lead, engineers, and specialists
