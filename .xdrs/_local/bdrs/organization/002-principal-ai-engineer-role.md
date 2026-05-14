---
name: _local-bdr-policy-002-bank-lead-ai-engineer-role-charter
description: Defines the Bank Lead AI Engineer role charter, responsibilities, organizational positioning, and required skills at NN Bank. Use when hiring, onboarding, or evaluating the role's scope and authority.
---

# _local-bdr-policy-002: Bank Lead AI Engineer Role Charter

## Context and Problem Statement

Nationale-Nederlanden (NN Bank) is scaling AI adoption across multiple business units (mortgage handling, payments, customer service), but AI initiatives are scattered with no single role owning the end-to-end AI engineering lifecycle. Data science prototypes do not meet production engineering standards, teams lack clear direction on which shared baselines to adopt and what day-two practices their agents require (monitoring, versioning, retraining); as this is a fast-moving target, the organization needs a governed approach to capture and evolve that knowledge. Additionally, agentic tooling for coding, architecture review, and business rule validation is adopted ad-hoc rather than governed.

Business units also need someone to help them translate AI possibilities into concrete initiatives.

The CTO organization has architects, engineering managers, and platform teams, but none of these roles holds the combined wide and deep knowledge needed to connect all the disciplines involved in professional AI delivery. Data scientists, engineers, architects, business analysts, and controls officers each see their own slice of the AI lifecycle but lack the cross-disciplinary depth to align their decisions. The result is AI initiatives where each discipline optimizes locally while the overall system suffers from misalignment. The organization needs a glue role that speaks all these languages and connects them into a coherent whole.

Question: How should NN Bank formally charter a Bank Lead AI Engineer role to unify AI adoption across business units, covering agentic for business, coding, architecture, engineering, governance, and AI controls advisory?

## Decision Outcome

**Advisory Bank Lead AI Engineer role across all business units, reporting through the CTO organization**

The Bank Lead AI Engineer is a connective glue role that bridges data science, software engineering, architecture, business analysis, and controls. It requires someone with the rare combination of deep AI/ML expertise and wide practical experience across these disciplines, because the glue function only works when the person genuinely understands each domain well enough to translate between specialists and earn their credibility.

### Details

#### Organizational positioning

- Advisory role (no direct reports) reporting through the CTO organization
- Works alongside enterprise architects and platform teams, with influence across all AI-active business units
- Requires CTO-level sponsorship for mandate and escalation support
- Scales through standards, enablement, and direct team support rather than command-and-control

#### Responsibility domains

**1. Strategic alignment**
- Define the AI engineering vision and roadmap aligned with CTO and architecture direction
- Identify opportunities for AI and agentic systems across business units
- Propose and prioritize AI initiatives based on business impact and technical feasibility
- Maintain awareness of AI industry trends, tools, and research; bring relevant innovations to the organization

**2. Agentic for business**
- Partner with business units during project inception to translate requirements into agentic system designs
- Define patterns for agent orchestration, tool use, memory, and human-in-the-loop workflows
- Ensure business-facing agents meet compliance, auditability, and explainability requirements for financial services
- Guide teams through ideation, prototyping, productionization, and post-launch improvement

**3. Agentic for coding**
- Evaluate and recommend AI-assisted development tools (code generation, completion, review, testing)
- Define standards for how engineers use AI coding assistants (prompt guidelines, review requirements, security checks)
- Propose automated enforcement of engineering and architecture standards through AI-powered code review and linting
- Spike and prototype new agentic coding workflows; share findings with engineering teams

**4. Agentic for architecture and engineering**
- Collaborate with enterprise architects to define reference architectures for AI/agent systems
- Define engineering standards for AI systems: model versioning, experiment tracking, reproducibility, testing strategies
- Own the bridge between data science outputs and production engineering: packaging, serving, scaling, monitoring
- Establish day-two practices: model drift detection, retraining pipelines, performance monitoring, incident response
- Define and maintain templates, starter kits, and documentation for teams starting new AI projects

**5. Agentic for governance**
- Propose tools and processes that automatically validate business rules, architecture decisions, and engineering standards in the development pipeline
- Define quality gates for AI project milestones (PoC, MVP, production, post-launch); mandatory sign-off before progression
- Work with compliance and risk teams to ensure AI governance meets financial regulatory requirements

**6. AI controls advisory**
- Partner with the controls department to define AI-specific risk controls that are technically sound, practically adoptable, and proportionate to actual risk
- Translate AI-specific risks (hallucination, model drift, data leakage, bias, prompt injection) into control frameworks the controls department can operationalize
- Advise on what evidence and monitoring is feasible so controls are verifiable rather than aspirational
- Help distinguish between blocking controls, detective controls, and advisory guidelines for AI systems
- Ensure controls enable safe AI adoption rather than creating blanket restrictions that block innovation

**7. Advisory and knowledge transfer**
- Act as the go-to advisor for any team starting or scaling an AI project; conduct hands-on pairing, workshops, and architecture reviews
- Build internal communities of practice around AI engineering
- Document patterns, anti-patterns, and lessons learned as reusable organizational knowledge

#### Authority model

- Defines standards and reference architectures that apply across business units
- Participates in architecture review boards for AI-related decisions
- Advisory (not blocking) on tool and framework selection; escalation through CTO when alignment is needed
- Acts as go-to advisor for any team starting or scaling an AI project; conducts hands-on pairing, workshops, and architecture reviews
- Maintains awareness of AI industry trends and brings relevant innovations to the organization
- Builds internal communities of practice around AI engineering

| Category | Requirements |
|---|---|
| **Technical depth** | 5+ years in AI/ML engineering with production deployment experience; agentic AI frameworks (LangChain, CrewAI, AutoGen, or similar); LLM integration patterns (RAG, fine-tuning, prompt engineering, evaluation) |
| **Technical breadth** | Strong software engineering, cloud platforms (AWS/Azure/GCP), distributed systems; MLOps (model serving, experiment tracking, CI/CD for ML, monitoring); data engineering fundamentals |
| **Architecture** | System design for large-scale applications; reference architecture definition; AI/agent integration patterns |
| **Leadership** | Cross-functional collaboration without direct authority; technical mentoring and knowledge transfer; stakeholder communication at engineering and business levels; balancing strategic thinking with hands-on execution |
| **Business** | Translating business requirements into AI solutions; financial services domain (banking, insurance, mortgages, payments); cost-benefit analysis for AI investments; risk awareness for AI in regulated environments |

#### Success metrics

Measure organizational AI capability growth, not individual project delivery: teams delivering AI to production, time-to-production reduction, adoption of shared standards, and quality of day-two practices. Target: every team the role engages with should need less support over time, not more.

## Considered Options

* (CHOSEN) **Model B: Advisory across all teams** - No direct reports, influences through standards, enablement, and direct support
  * Reason: Best fit for NN Bank's existing BU-based structure. Does not require organizational restructuring. Scales through standards and gravitational pull. Works alongside existing architects and platform teams.
  * Acknowledged weaknesses: low accountability clarity, advisory lag risk, harder to hire (wide+deep profile is rare). These are trade-offs, not disqualifiers, given that only two to three BUs are actively running AI projects today. As AI adoption scales beyond three simultaneous BUs, a transition toward a lightweight Model C (small complementary team led by the Bank Lead AI Engineer) should be planned.
* (REJECTED) **Model A: Embedded in a single team** - Role sits inside one team, serves others on request
  * Reason: Limited influence scope, poor knowledge transfer, creates single-team dependency. Does not address the cross-BU convergence need.
* (REJECTED) **Model C: Dedicated AI team lead** - Leads standalone AI team consumed as a service
  * Reason: Requires creating a new team, which risks becoming a bottleneck. Management overhead reduces hands-on capability. Less effective for knowledge transfer than direct advisory. Becomes the right model at scale (3+ active BUs), but not for current state.

Related research:
- [Bank Lead AI Engineer Role Definition](researches/001-principal-ai-engineer-role.md) - Gap analysis, responsibility domain mapping, positioning comparison, and skills derivation

## References

- [_local-research-001](researches/001-principal-ai-engineer-role.md) - Research backing this role definition
- [_local-bdr-001 (principles)](../principles/001-agentme-product-purpose.md) - Product context for the agentme project
- [Executive presentation slides](.assets/002-principal-ai-engineer-role-slides-executive.md) - Marp slide deck for executive audience
