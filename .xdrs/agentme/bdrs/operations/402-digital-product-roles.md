---
name: agentme-bdr-policy-402-digital-product-roles
description: Defines roles, responsibilities, and skills for all digital product roles — from organisation-level strategy through cross-team standards to team execution and specialist support. Use when staffing, onboarding, or assigning responsibilities across any level of a digital product organisation.
apply-to: All roles involved in building and operating digital products, from organisation level through team specialists
valid-from: 2026-08-30
---

# agentme-bdr-policy-402: Digital product roles

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

#### 06-team-roles

The following roles MUST belong to a product team. Some roles are shared across squads within the team; others are dedicated to a squad.

---

**Product Owner (PO)**

*Purpose*: Own the product vision for the team's scope, define sprint goals, and ensure team priorities align with broader OKRs.

*Responsibilities*:
- Define and maintain the product vision for the team
- Set sprint goals and prioritise the team backlog
- Align team-level OKRs with Product Manager direction and execute against Tactical OKRs set by the PM
- Define and track Operational OKRs for the team's day-to-day execution, when applicable
- Accept or reject completed work against acceptance criteria
- Communicate product direction to stakeholders and team members

*Shared across squads*: Yes — the PO connects to all squads in the team.

*Soft skills*: Vision articulation, prioritisation under uncertainty, stakeholder management, decisiveness, facilitation

*Hard skills*: Backlog management, OKR definition and tracking, user story writing, roadmap planning, basic domain knowledge of the product area

*Common activities*: Sprint planning, backlog refinement, sprint reviews, stakeholder presentations, OKR reviews, acceptance testing participation

---

**Project Manager (PjM)**

*Purpose*: Own stakeholder management, reporting, and cross-team coordination. Proactively unblock the team by connecting priorities and people across organisational boundaries.

*Responsibilities*:
- Manage relationships with external stakeholders and report on progress
- Identify and resolve cross-team dependencies and scheduling conflicts before they block delivery
- Coordinate cross-squad dependencies within the team
- Track risks, assumptions, issues, and dependencies (RAID)
- Facilitate communication between the team and external parties

*Authority*: No authority over technical or product decisions. Facilitates and connects; does not override PO or Tech Lead decisions.

*Soft skills*: Communication, relationship management, proactive problem-solving, negotiation, organisation, cross-team coordination

*Hard skills*: Project planning, risk management, reporting, dependency tracking, facilitation, RAID log management

*Common activities*: Stakeholder updates, dependency mapping sessions, risk reviews, cross-team syncs, status reporting, escalation facilitation

---

**Business Analyst (BA)**

*Purpose*: Understand what needs to be built and translate business problems into clear, implementable requirements for non-AI features and processes.

*Responsibilities*:
- Research business problems through stakeholder interviews, process observation, and analysis — focusing on changes to processes and systems that contribute to Tactical OKR objectives
- Model as-is and design to-be business processes
- Define system requirements at requirement level: data inputs/outputs, business rules, human interactions, and external dependencies
- Write user stories and acceptance criteria at a level implementable within a few days
- Support engineers during implementation by clarifying requirements

*Squad assignment*: Ideally one BA per squad, working ahead on upcoming features while available for in-sprint requirement clarification. May move between squads when demand shifts (self-organised with PO awareness).

*Soft skills*: Curiosity, structured thinking, stakeholder communication, facilitation, attention to detail

*Hard skills*: Business process modelling (BPMN or equivalent), requirements writing, user story authoring, process analysis, data mapping

*Common activities*: Stakeholder interviews, process workshops, requirements documentation, backlog refinement support, acceptance criteria authoring, sprint demo observation

---

**AI Business Analyst (AI BA)**

*Purpose*: Define what needs to be built for AI-powered solutions by translating business needs into clear, implementable AI requirements — covering workflows, agents, models, integrations, controls, and test criteria.

*Responsibilities*:
- Research business problems through analysis, stakeholder interviews, and process discovery
- Design target business processes, AI workflows, agents, models, and required system integrations
- Identify AI opportunities, risks, controls, and regulatory requirements
- Define data inputs, outputs, business rules, human interactions, and external dependencies for AI systems
- Specify which models, agents, and workflows need to be implemented, and the detailed input/output of all internal and external systems involved
- Create detailed user stories and acceptance criteria that engineers can implement within a few days
- Define test and evaluation requirements for AI systems

*Research boundary*: The AI BA researches business problems, requirements, and AI opportunities before implementation begins. The AI Engineer researches technical approaches, model selection, data characteristics, and evaluation methods during implementation. These boundaries must not blur.

*Squad assignment*: Same mobility rules as BA. AI BA and BA may exchange squad positions depending on which phase the squad is in and whether AI or non-AI features dominate.

*Accountability*: The AI BA owns WHAT is required — business requirements, AI workflows, data definitions, controls, and acceptance criteria. Engineering teams own HOW the solution is implemented, including architecture, technology choices, infrastructure, security, and deployment.

*Deliverables*: Business and AI requirements, process and workflow designs, AI agent and model specifications, integration and data requirements, risk and control assessments, test and evaluation requirements for AI systems, epics, features, and user stories

*Soft skills*: Curiosity about AI capabilities and limits, structured thinking, stakeholder communication, ability to bridge business and technical language, attention to regulatory and ethical risk

*Hard skills*: AI system design, prompt engineering concepts, AI workflow and agent specification, business process modelling, requirements writing, data input/output definition, AI risk and control frameworks, regulatory awareness (EU AI Act, sector-specific rules)

*Common activities*: AI opportunity workshops, stakeholder interviews, AI workflow design, agent specification authoring, risk and control assessment, acceptance criteria for AI outputs, backlog refinement support

---

**AI Lead**

*Purpose*: Own the technical design of AI implementations within the team — architectures, platforms, implementation order, and output quality standards — and develop AI engineers through mentoring and pairing.

*Responsibilities*:
- Design the technical architecture for tests, models, agents, and workflows
- Define implementation platforms and tooling for AI development
- Sequence AI implementation work and define quality and monitoring standards for AI outputs
- Refine user stories related to AI development with sufficient technical detail
- Mentor AI Engineers through pairing, code review, and knowledge sharing
- Co-design integrated features with Tech Lead (tiebreaker on AI component decisions)

*Shared across squads*: Yes — the AI Lead connects to all squads in the team.

*Soft skills*: Technical leadership, mentoring, clear communication of complex AI concepts, cross-functional collaboration, pragmatic decision-making

*Hard skills*: ML/AI system architecture, LLM and agent frameworks, model evaluation and observability, MLOps, prompt engineering, AI safety and testing practices, Python, relevant ML libraries

*Common activities*: AI architecture design sessions, technical story refinement, AI code reviews, pairing sessions with AI Engineers, model evaluation design, cross-lead technical alignment with Tech Lead

---

**AI Engineer**

*Purpose*: Implement AI components — tests, models, agents, and workflows — according to the technical design provided by the AI Lead.

*Responsibilities*:
- Implement models, agents, and AI workflows to specification
- Build evaluations (evals), regression tests, and datasets for AI systems
- Research technical approaches, model selection, data characteristics, and evaluation methods during implementation (not business requirements — that is AI BA scope)
- Perform data analysis to support model development and evaluation
- Raise technical blockers and edge cases to the AI Lead

*Soft skills*: Curiosity, structured problem-solving, willingness to experiment and discard, attention to evaluation rigour

*Hard skills*: Python, ML frameworks (PyTorch, scikit-learn, or equivalent), LLM and agent frameworks (LangChain, LangGraph, or equivalent), prompt engineering, evaluation design, data analysis, experiment tracking

*Common activities*: Model and agent implementation, eval authoring, dataset creation and curation, data analysis, technical research, code review participation, pairing with AI Lead

---

**Tech Lead**

*Purpose*: Own the technical design of non-AI implementations — services, choreographers, web pages, app pages, CI/CD, monitoring, and incident procedures — and develop engineers through mentoring and pairing.

*Responsibilities*:
- Design technical architecture for services, choreographers, web pages, and mobile app pages
- Define monitoring, alerting, and Change Management procedures integrated with CI/CD
- Define and maintain Incident Management procedures
- Sequence engineering implementation work
- Refine user stories related to engineering with sufficient technical detail
- Mentor Engineers through pairing, code review, and knowledge sharing
- Co-design integrated features with AI Lead (tiebreaker on system boundary decisions)
- Escalate to Solution Architect when an Epic requires new cross-system standards or integrations; escalate to Principal Engineer when new engineering standards are needed

*Shared across squads*: Yes — the Tech Lead connects to all squads in the team.

*Soft skills*: Technical leadership, mentoring, structured communication, cross-functional collaboration, pragmatic decision-making under uncertainty

*Hard skills*: Software architecture, API design, event-driven systems, CI/CD pipelines, observability and alerting, incident management, security engineering basics, relevant languages and frameworks used by the team

*Common activities*: Architecture design sessions, technical story refinement, code reviews, pairing sessions with Engineers, incident post-mortems, CI/CD pipeline design, cross-lead technical alignment with AI Lead

---

**Backend Engineer**

*Purpose*: Implement server-side software components — APIs, business workflows, batch processes, event-driven integrations, and database access layers.

*Responsibilities*:
- Design and implement RESTful and event-driven APIs
- Build business logic, workflows, and batch processing components
- Develop database access layers and manage schema migrations
- Implement integrations with external systems and third-party services
- Support incident investigation for backend services

*Hard skills*: Backend languages (Java, Go, Python, Node.js, or equivalent), API design, SQL and NoSQL databases, event-driven systems, containerisation

*Common activities*: API implementation, data layer development, external integration work, schema migrations, code review participation, incident support

---

**Frontend Engineer**

*Purpose*: Implement user-facing software components — web applications, mobile apps, and UI interactions.

*Responsibilities*:
- Build web pages, single-page applications, and responsive UI components
- Implement mobile app screens and navigation flows (where applicable)
- Integrate frontend with backend APIs and services
- Ensure accessibility, performance, and cross-browser or cross-platform compatibility
- Collaborate with UX Designers on interaction and visual design implementation

*Hard skills*: HTML/CSS, modern frontend frameworks (React, Vue, Angular, or equivalent), mobile development (React Native, Flutter, or equivalent where applicable), API integration, browser and mobile performance tooling

*Common activities*: UI component implementation, API integration, accessibility and performance testing, mobile screen development, code review participation

---

**DevOps/Infra Engineer**

*Purpose*: Own the delivery pipeline and cloud infrastructure that enables teams to ship and run software reliably — covering both CI/CD automation and cloud provisioning.

*Responsibilities*:
- Build and maintain CI/CD pipelines, deployment automation, and release procedures including blue/green deployments and automated rollouts
- Design and provision cloud infrastructure using templates and infrastructure-as-code blueprints
- Manage networking, connectivity, certificates, and platform-level security controls
- Define validation scripts and deployment checks that gate production releases
- Monitor infrastructure health and respond to platform-level incidents

*Hard skills*: CI/CD tooling (GitHub Actions, GitLab CI, or equivalent), cloud platforms (AWS, Azure, GCP, or equivalent), infrastructure-as-code (Terraform, Pulumi, or equivalent), containerisation and orchestration (Docker, Kubernetes), networking fundamentals

*Common activities*: Pipeline authoring and maintenance, cloud resource provisioning, infrastructure monitoring, deployment procedure definition, certificate and connectivity management, incident response for platform issues

---

**Full Stack Engineer**

*Purpose*: Implement non-AI software components across the full stack — APIs, workflows, web pages, mobile apps, CI/CD pipelines, database access, and event-based flows. Suited to teams and contexts where frontend and backend work are tightly coupled or where a generalist profile is preferred over specialisation.

*Responsibilities*:
- Implement services, APIs, database access layers, event-based flows, and non-AI workflows
- Build and maintain CI/CD pipelines
- Implement web pages, mobile app screens, and frontend components
- Write and maintain scripts and automation for platform and operational needs
- Support AI Engineers with software engineering knowledge gaps (e.g., API integration, data pipelines, infrastructure)

*Soft skills*: Breadth of technical knowledge, pragmatism, collaborative problem-solving, ownership of delivered quality

*Hard skills*: Full stack development (frontend and backend), API design and implementation, database access (SQL and NoSQL), event-driven systems, CI/CD tooling, containerisation, scripting, mobile development (where applicable)

*Common activities*: Feature implementation, API and data layer development, CI/CD pipeline work, code review participation, pairing with AI Engineers, frontend development, incident support

#### 07-specialists

Specialists are professionals with focused domain expertise who contribute to specific phases of product delivery. They MAY be shared across multiple product teams or embedded within a specific team when the scope or duration of work justifies it. Teams SHOULD plan specialist involvement proactively — engaging them ahead of the phases where their input is needed rather than reactively.

| Specialist | Purpose | Typical engagement |
|---|---|---|
| UX Designer | Design user interactions, information architecture, and visual language for user-facing features | Embedded for user-facing feature phases; shared otherwise |
| Tester / QA Specialist | Define test strategies, execute exploratory and structured testing, and validate acceptance criteria beyond automated test coverage | Embedded during high-complexity delivery phases; shared for periodic quality reviews |
| Communication Specialist | Author internal and external communications, release announcements, and user-facing documentation | Shared; engaged at release and major milestone points |
| Journalist / Technical Writer | Produce structured content — user guides, API documentation, internal knowledge bases | Shared or embedded when documentation volume is significant |
| Business SME (Subject Matter Expert) | Validate requirements and processes against business domain knowledge; bridge between business stakeholders and product teams | Shared; engaged during requirements and validation phases |

## References

- [`_core-adr-policy-016`](../../../_core/adrs/principles/016-policy-subjects.md) — Policy subjects: BDR operations subject definition
- [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) — Policy numbering: BDR operations block 401–500
- [`agentme-bdr-001`](../principles/001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-002`](../principles/002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions
- [`agentme-bdr-003`](../principles/003-product-delivery-value-flow.md) — Product delivery value flow: end-to-end chain from Strategic OKRs to fulfilled Tactical OKRs
- [`agentme-bdr-403`](403-product-team-composition.md) — Team composition models, squad dynamics, and known structural gaps
