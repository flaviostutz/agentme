---
name: agentme-bdr-policy-404-digital-product-roles-team-specialists
description: Defines team-level roles and specialist roles — Product Owner, Project Manager, Engineering Manager, Business Analyst, AI Business Analyst, AI Lead, AI Engineer, Tech Lead, Backend Engineer, Frontend Engineer, DevOps/Infra Engineer, Full Stack Engineer, and shared specialists. Use when staffing, onboarding, or assigning responsibilities within a product team.
apply-to: All roles that belong to or support a product team
valid-from: 2026-08-30
---

# agentme-bdr-policy-404: Digital product roles — team & specialists

## Context and Problem Statement

Product teams require a well-defined set of roles covering product ownership, project coordination, business analysis, AI and engineering execution, and specialist support. Without explicit definitions of responsibilities, authority boundaries, and skill requirements at the team level, teams experience unclear ownership, misaligned expectations, and delivery gaps.

What roles belong to or support a product team, and what does each role own?

## Decision Outcome

**A defined set of team-level roles and shared specialist roles with explicit responsibilities, authority boundaries, and skill requirements**

### Details

#### 01-team-roles

The following roles MUST belong to a product team. Some roles are shared across squads within the team; others are dedicated to a squad.

---

**Product Owner (PO)**

*Purpose*: Own the product vision for the team's scope, define sprint goals, and ensure team priorities align with broader OKRs.

*Accountability*: Workforce-allocation enforcement (the split defined in `agentme-bdr-402`) and team-building/morale; Epic definition, backlog scoping/acceptance, and ongoing scope change management; Initial compliance/privacy/risk triage, including breach-notification escalation; UX and interaction design; Production readiness and go-live approval; Release/rollout communication and user-facing documentation, including deprecation and sunset notices; Service or system deprecation decision; Team-level outcome measurement (Operational OKRs)

*Consulted on*: Vendor/third-party selection, contract, and SLA negotiation; Complex or high-risk stakeholder and issue/risk (RAID) management; Business metrics instrumentation and tracking

*Informed about*: Tactical OKR translation, epic prioritisation, and business case/ROI justification

*Shared across squads*: Yes — the PO connects to all squads in the team.

*Soft skills*: Vision articulation, prioritisation under uncertainty, stakeholder management, decisiveness, facilitation

*Hard skills*: Backlog management, OKR definition and tracking, user story writing, roadmap planning, basic domain knowledge of the product area

*Common activities*: Sprint planning, backlog refinement, sprint reviews, stakeholder presentations, OKR reviews, acceptance testing participation

---

**Project Manager (PjM)**

*Purpose*: Own stakeholder management, reporting, and cross-team coordination. Proactively unblock the team by connecting priorities and people across organisational boundaries.

*Accountability*: Cross-team dependency tracking and schedule/milestone reporting; Complex or high-risk stakeholder and issue/risk (RAID) management

*Consulted on*: Rollback decision authority; Cross-team technical emergency declaration and mobilization; Engineering standards, platforms, and AI-practice governance

*Authority*: No authority over technical or product decisions. Facilitates and connects; does not override PO or Tech Lead decisions.

*Soft skills*: Communication, relationship management, proactive problem-solving, negotiation, organisation, cross-team coordination

*Hard skills*: Project planning, risk management, reporting, dependency tracking, facilitation, RAID log management

*Common activities*: Stakeholder updates, dependency mapping sessions, risk reviews, cross-team syncs, status reporting, escalation facilitation

---

**Engineering Manager (EM)**

*Purpose*: Own the people and workforce dimension of the team — hiring, career growth, and team health — so the team has the right people, growing in the right direction, at sustainable capacity.

*Accountability*: Hiring, onboarding, and offboarding; Performance management, career growth, and compensation/promotion; Workforce planning and capacity allocation; Team health, psychological safety, and retention; On-call scheduling and compensation

*Consulted on*: Workforce-allocation enforcement (the split defined in `agentme-bdr-402`) and team-building/morale

*Disambiguation*: Unlike the Tech Lead, the Engineering Manager does not own technical direction or code mentoring — only people/HR accountability. Unlike the PjM, the Engineering Manager has no delivery-coordination or stakeholder-facing responsibility — only people authority.

*Shared across squads*: Yes — the Engineering Manager connects to all squads in the team, at the same granularity as the PO, Tech Lead, and AI Lead. In smaller organisations, one Engineering Manager MAY cover multiple teams.

*Soft skills*: Empathy, active listening, coaching, conflict resolution, negotiation, organisational awareness

*Hard skills*: Performance management frameworks, compensation benchmarking, hiring and interviewing, workforce capacity planning, on-call rotation management

*Common activities*: 1:1s, hiring interviews and debriefs, performance and promotion cycles, capacity planning sessions, onboarding/offboarding, on-call schedule management

---

**Business Analyst (BA)**

*Purpose*: Understand what needs to be built and translate business problems into clear, implementable requirements for non-AI features and processes.

*Accountability*: Requirements and user stories (non-AI); Business metrics instrumentation and tracking

*Consulted on*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work

*Squad assignment*: Ideally one BA per squad, working ahead on upcoming features while available for in-sprint requirement clarification. May move between squads when demand shifts (self-organised with PO awareness).

*Soft skills*: Curiosity, structured thinking, stakeholder communication, facilitation, attention to detail

*Hard skills*: Business process modelling (BPMN or equivalent), requirements writing, user story authoring, process analysis, data mapping

*Common activities*: Stakeholder interviews, process workshops, requirements documentation, backlog refinement support, acceptance criteria authoring, sprint demo observation

---

**AI Business Analyst (AI BA)**

*Purpose*: Define what needs to be built for AI-powered solutions by translating business needs into clear, implementable AI requirements — covering workflows, agents, models, integrations, controls, and test criteria.

*Accountability*: AI opportunity discovery; Requirements and user stories (AI)

*Consulted on*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work; AI model evaluation, safety, and fairness testing

*Research boundary*: The AI BA researches business problems, requirements, and AI opportunities before implementation begins. The AI Engineer researches technical approaches, model selection, data characteristics, and evaluation methods during implementation. These boundaries must not blur.

*Squad assignment*: Same mobility rules as BA. AI BA and BA may exchange squad positions depending on which phase the squad is in and whether AI or non-AI features dominate.

*Authority*: The AI BA owns WHAT is required — business requirements, AI workflows, data definitions, controls, and acceptance criteria. Engineering teams own HOW the solution is implemented, including architecture, technology choices, infrastructure, security, and deployment.

*Deliverables*: Business and AI requirements, process and workflow designs, AI agent and model specifications, integration and data requirements, risk and control assessments, test and evaluation requirements for AI systems, epics, features, and user stories

*Soft skills*: Curiosity about AI capabilities and limits, structured thinking, stakeholder communication, ability to bridge business and technical language, attention to regulatory and ethical risk

*Hard skills*: AI system design, prompt engineering concepts, AI workflow and agent specification, business process modelling, requirements writing, data input/output definition, AI risk and control frameworks, regulatory awareness (EU AI Act, sector-specific rules)

*Common activities*: AI opportunity workshops, stakeholder interviews, AI workflow design, agent specification authoring, risk and control assessment, acceptance criteria for AI outputs, backlog refinement support

---

**AI Lead**

*Purpose*: Own the technical design of AI implementations within the team — architectures, platforms, implementation order, and output quality standards — and develop AI engineers through mentoring and pairing.

*Accountability*: Technical refinement (AI); Non-functional requirements sign-off (AI); Feature or model implementation, including migration, cutover, and legacy decommissioning build work (AI); Code or model review (AI); Independent QA and test execution (AI); AI model evaluation, safety, and fairness testing; Production monitoring, alerting, incident response, and post-incident review, including proactive remediation of disclosed vulnerabilities (AI)

*Responsibilities*: Hiring, onboarding, and offboarding (technical ramp-up portion)

*Consulted on*: Cross-team dependency tracking and schedule/milestone reporting (AI); Production readiness and go-live approval; Cross-team technical emergency declaration and mobilization; Engineering standards, platforms, and AI-practice governance

*Shared across squads*: Yes — the AI Lead connects to all squads in the team.

*Soft skills*: Technical leadership, mentoring, clear communication of complex AI concepts, cross-functional collaboration, pragmatic decision-making

*Hard skills*: ML/AI system architecture, LLM and agent frameworks, model evaluation and observability, MLOps, prompt engineering, AI safety and testing practices, Python, relevant ML libraries

*Common activities*: AI architecture design sessions, technical story refinement, AI code reviews, pairing sessions with AI Engineers, model evaluation design, cross-lead technical alignment with Tech Lead

---

**AI Engineer**

*Purpose*: Implement AI components — tests, models, agents, and workflows — according to the technical design provided by the AI Lead.

*Responsibilities*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work; AI model evaluation, safety, and fairness testing

*Soft skills*: Curiosity, structured problem-solving, willingness to experiment and discard, attention to evaluation rigour

*Hard skills*: Python, ML frameworks (PyTorch, scikit-learn, or equivalent), LLM and agent frameworks (LangChain, LangGraph, or equivalent), prompt engineering, evaluation design, data analysis, experiment tracking

*Common activities*: Model and agent implementation, eval authoring, dataset creation and curation, data analysis, technical research, code review participation, pairing with AI Lead

---

**Tech Lead**

*Purpose*: Own the technical design of non-AI implementations — services, choreographers, web pages, app pages, CI/CD, monitoring, and incident procedures — and develop engineers through mentoring and pairing.

*Accountability*: Technical refinement (non-AI); Non-functional requirements sign-off (non-AI); Cross-team shared-component ownership; Feature or model implementation, including migration, cutover, and legacy decommissioning build work (non-AI); Code or model review (non-AI); Independent QA and test execution (non-AI); Dependency and license compliance; CI/CD pipeline and deployment automation; Rollback decision authority; Production monitoring, alerting, incident response, and post-incident review, including proactive remediation of disclosed vulnerabilities (non-AI); Ongoing operational governance (cost/FinOps, security review cadence and access audits, DR/business-continuity drills, vendor/SLA performance monitoring)

*Responsibilities*: Hiring, onboarding, and offboarding (technical ramp-up portion); Workforce-allocation enforcement (the split defined in `agentme-bdr-402`) and team-building/morale

*Consulted on*: Cross-team dependency tracking and schedule/milestone reporting (non-AI); Production readiness and go-live approval; Cross-team technical emergency declaration and mobilization; Business metrics instrumentation and tracking; Architecture blueprint (cross-system); Engineering standards, platforms, and AI-practice governance

*Shared across squads*: Yes — the Tech Lead connects to all squads in the team.

*Soft skills*: Technical leadership, mentoring, structured communication, cross-functional collaboration, pragmatic decision-making under uncertainty

*Hard skills*: Software architecture, API design, event-driven systems, CI/CD pipelines, observability and alerting, incident management, security engineering basics, relevant languages and frameworks used by the team

*Common activities*: Architecture design sessions, technical story refinement, code reviews, pairing sessions with Engineers, incident post-mortems, CI/CD pipeline design, cross-lead technical alignment with AI Lead

---

**Backend Engineer**

*Purpose*: Implement server-side software components — APIs, business workflows, batch processes, event-driven integrations, and database access layers.

*Responsibilities*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work; Business metrics instrumentation and tracking

*Hard skills*: Backend languages (Java, Go, Python, Node.js, or equivalent), API design, SQL and NoSQL databases, event-driven systems, containerisation

*Common activities*: API implementation, data layer development, external integration work, schema migrations, code review participation, incident support

---

**Frontend Engineer**

*Purpose*: Implement user-facing software components — web applications, mobile apps, and UI interactions.

*Responsibilities*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work; Business metrics instrumentation and tracking

*Hard skills*: HTML/CSS, modern frontend frameworks (React, Vue, Angular, or equivalent), mobile development (React Native, Flutter, or equivalent where applicable), API integration, browser and mobile performance tooling

*Common activities*: UI component implementation, API integration, accessibility and performance testing, mobile screen development, code review participation

---

**DevOps/Infra Engineer**

*Purpose*: Own the delivery pipeline and cloud infrastructure that enables teams to ship and run software reliably — covering both CI/CD automation and cloud provisioning.

*Responsibilities*: CI/CD pipeline and deployment automation; Ongoing operational governance (cost/FinOps, security review cadence and access audits, DR/business-continuity drills, vendor/SLA performance monitoring)

*Consulted on*: Production readiness and go-live approval

*Hard skills*: CI/CD tooling (GitHub Actions, GitLab CI, or equivalent), cloud platforms (AWS, Azure, GCP, or equivalent), infrastructure-as-code (Terraform, Pulumi, or equivalent), containerisation and orchestration (Docker, Kubernetes), networking fundamentals

*Common activities*: Pipeline authoring and maintenance, cloud resource provisioning, infrastructure monitoring, deployment procedure definition, certificate and connectivity management, incident response for platform issues

---

**Full Stack Engineer**

*Purpose*: Implement non-AI software components across the full stack — APIs, workflows, web pages, mobile apps, CI/CD pipelines, database access, and event-based flows. Suited to teams and contexts where frontend and backend work are tightly coupled or where a generalist profile is preferred over specialisation.

*Responsibilities*: Feature or model implementation, including migration, cutover, and legacy decommissioning build work; Business metrics instrumentation and tracking

*Soft skills*: Breadth of technical knowledge, pragmatism, collaborative problem-solving, ownership of delivered quality

*Hard skills*: Full stack development (frontend and backend), API design and implementation, database access (SQL and NoSQL), event-driven systems, CI/CD tooling, containerisation, scripting, mobile development (where applicable)

*Common activities*: Feature implementation, API and data layer development, CI/CD pipeline work, code review participation, pairing with AI Engineers, frontend development, incident support

#### 02-specialists

Specialists are professionals with focused domain expertise who contribute to specific phases of product delivery. They MAY be shared across multiple product teams or embedded within a specific team when the scope or duration of work justifies it. Teams SHOULD plan specialist involvement proactively — engaging them ahead of the phases where their input is needed rather than reactively.

| Specialist | Purpose | Typical engagement | RACI (`agentme-bdr-405`) |
|---|---|---|---|
| UX Designer | Design user interactions, information architecture, and visual language for user-facing features | Embedded for user-facing feature phases; shared otherwise | Responsible: UX and interaction design |
| Tester / QA Specialist | Define test strategies, execute exploratory and structured testing, and validate acceptance criteria beyond automated test coverage | Embedded during high-complexity delivery phases; shared for periodic quality reviews | Responsible: Independent QA and test execution; AI model evaluation, safety, and fairness testing |
| Communication Specialist | Author internal and external communications, release announcements, and user-facing documentation | Shared; engaged at release and major milestone points | Responsible: Release/rollout communication and user-facing documentation, including deprecation and sunset notices |
| Journalist / Technical Writer | Produce structured content — user guides, API documentation, internal knowledge bases | Shared or embedded when documentation volume is significant | Responsible: Release/rollout communication and user-facing documentation, including deprecation and sunset notices |
| Business SME (Subject Matter Expert) | Validate requirements and processes against business domain knowledge; bridge between business stakeholders and product teams | Shared; engaged during requirements and validation phases | Consulted: Initial compliance/privacy/risk triage, including breach-notification escalation; Requirements and user stories |

## References

- [`_core-adr-policy-016`](../../../_core/adrs/principles/016-policy-subjects.md) — Policy subjects: BDR operations subject definition
- [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) — Policy numbering: BDR operations block 401–500
- [`agentme-bdr-001`](../principles/001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-002`](../principles/002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions
- [`agentme-bdr-003`](../principles/003-product-delivery-value-flow.md) — Product delivery value flow: end-to-end chain from Strategic OKRs to fulfilled Tactical OKRs
- [`agentme-bdr-402`](402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Principal Engineer, Solution Architect, and team structure context
- [`agentme-bdr-403`](403-product-team-composition.md) — Team composition models, squad dynamics, and known structural gaps
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) — RACI matrix assigning decision rights across the digital-product lifecycle for the roles defined here
