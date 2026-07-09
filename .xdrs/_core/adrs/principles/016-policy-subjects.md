---
name: _core-adr-policy-016-policy-subjects
description: Defines the allowed subjects per XDRS type (ADR, BDR, EDR) with descriptions, examples, and disambiguation tiebreakers. Use when choosing a subject for any new policy or document.
apply-to: All XDRS scopes and document types
valid-from: 2026-07-09
---

# _core-adr-policy-016: Policy Subjects

## Context and Problem Statement

Policy documents are placed in a subject folder that reflects their primary concern. Without a well-defined and consistently applied subject taxonomy, documents are hard to find, placement decisions are inconsistent, and AI agents cannot reliably determine relevance.

What subjects are allowed per type, and how should ambiguous placements be resolved?

## Decision Outcome

**A reduced, unambiguous subject taxonomy per type with explicit tiebreaker rules**

Each type uses a small, well-separated set of subjects. ADR and EDR share identical subject names, creating a consistent zoom-in relationship: ADR captures architectural decisions at a higher abstraction level; EDR captures engineering implementation decisions for the same concerns. BDR uses a business-specific set.

### Details

#### 01-subject-must-be-from-allowed-list

The subject folder MUST be one of the subjects listed below. `freeze-reference: true` exempts this check (see [`_core-adr-policy-002-policy-standards.01-freeze-reference-exemption`](002-policy-standards.md)).

| Subject | ADR | BDR | EDR |
|---|---|---|
| `principles` | ✓ | ✓ | ✓ |
| `application` | ✓ | | ✓ |
| `data` | ✓ | | ✓ |
| `platform` | ✓ | | ✓ |
| `operations` | ✓ | ✓ | ✓ |
| `governance` | ✓ | ✓ | ✓ |
| `product` | | ✓ | |
| `finance` | | ✓ | |

#### 02-principles-must-be-cross-cutting

A document MUST only be placed in `principles` when its content affects potentially all other subjects in its type. A document that only concerns a single subject MUST be placed in that specific subject instead. Do not use `principles` as a catch-all when a more specific subject applies.

#### 03-adr-and-edr-share-subject-names-at-different-abstraction-levels

ADR and EDR intentionally share the same six subject names. The type disambiguates the abstraction level: ADR captures architectural choices about what to adopt or how systems relate at a high level; EDR captures engineering decisions about how to implement those choices in detail. When both an architectural and an engineering decision exist on the same topic, authors MUST create two separate documents. See tiebreaker 18 for the decision test.

#### 04-subject-descriptions-for-adr

Authors MUST place ADR documents in the subject that best matches the following definitions and examples.

- `principles`: Cross-cutting architectural foundations affecting all other ADR subjects. Examples: architecture style adoption, domain-driven design rules, interoperability rules, long-term technology direction.
- `application`: System and service design decisions. Covers application structure, integration and API patterns, service decomposition, migration patterns, and frontend architecture. Examples: modularization strategy, strangler fig migration, API versioning strategy, service contract approach, sync vs async communication, monolith decomposition, frontend rendering strategy (SSR vs CSR, SPA vs MPA), design system adoption, UI component library selection, mobile app architecture, AI/ML model selection and inference architecture.
- `data`: Data architecture and information modeling choices. Examples: canonical data model, data ownership boundaries, data retention strategy (technical architecture only — regulatory retention obligations MUST go in BDR `governance`), data mesh vs centralized approach, event sourcing, polyglot persistence.
- `platform`: Platform-level runtime and enabling capabilities — includes infrastructure topology, identity and authentication, cloud cost management, and managed external technical services adopted as infrastructure. Examples: cloud provider selection, multi-region topology, Kubernetes adoption, SSO/IAM architecture, mTLS, message broker selection, CDN strategy, FinOps and cloud cost allocation model, workflow orchestration tool selection (Airflow, Temporal), managed SaaS adoption (observability platforms, LLM API providers, data warehouse services), SIEM adoption as security monitoring infrastructure (a mandatory enforcement obligation to have a SIEM belongs in ADR `governance`).
- `operations`: Operational architecture decisions about how systems behave and are owned in production. Examples: resilience and availability objectives, disaster recovery strategy, incident ownership model, SLA definitions, operational accountability boundaries.
- `governance`: Architecture controls for security, compliance, and risk enforcement. Examples: encryption baseline, zero-trust architecture, threat modeling requirements, SOC2/ISO27001 compliance adoption, data classification and PII tiers, architecture review process, technology radar governance, architecture-level penetration testing requirements.

#### 05-subject-descriptions-for-bdr

Authors MUST place BDR documents in the subject that best matches the following definitions and examples.

- `principles`: Cross-cutting business principles that affect all other BDR subjects. Examples: customer-first decision framework, policy precedence rules, strategic guardrails, brand values, patent and IP strategic stance (e.g., patent-first vs open-core), technology debt governance principle.
- `product`: Product offering, go-to-market, marketing, and sales policy decisions. Covers product behavior and lifecycle, brand and communication standards, and sales process and revenue operations. Examples: feature rollout policy, product versioning and end-of-life, pricing tier structure, customer SLA commitments, product accessibility standards, beta program criteria, campaign approval process, social media policy, customer communication tone, brand naming, sales methodology, deal approval and discount authority matrix, CRM standards, sales commission structure, channel and partner sales policy, territory and quota policy.
- `operations`: Day-to-day business processes, organizational structure, responsibility model, and workforce decisions. Covers business process execution, team and organizational decisions, and the employee and contractor lifecycle. Examples: support workflows, vendor selection process, decision rights and RACI, team topology, hiring and interview process, performance management framework, compensation and benefits policy, learning and development standards, remote and hybrid work policy, onboarding and offboarding procedures, workforce planning, internal communication standards, M&A integration process, outage customer communication process, on-call scheduling and compensation policy (on-call ownership model belongs in ADR `operations`).
- `governance`: Legal, regulatory, compliance, risk management, and enterprise control decisions. Covers all mandatory policies imposed by law, regulation, or risk authority — including external regulatory obligations, internal control frameworks, enterprise risk governance, and ESG compliance requirements. Examples: GDPR and data privacy policy, risk appetite statement, KYC/AML procedures, business continuity policy, legal contract standards, employee data privacy, open-source licensing policy, vendor risk and due diligence standards, AI ethics and responsible AI policy, model risk management policy, regulatory compliance programs (SOX, HIPAA, Basel, MiFID, ISO 27001), internal audit requirements, fraud prevention policy, information security policy, ESG reporting requirements, carbon footprint targets, DEI compliance obligations, whistleblower policy, IP and patent compliance obligations, penetration testing regulatory obligation.
- `finance`: Financial and cost-control business decisions. Examples: budgeting process, investment approval thresholds, partner revenue sharing model, procurement policy, pricing approval and margin rules.

#### 06-subject-descriptions-for-edr

Authors MUST place EDR documents in the subject that best matches the following definitions and examples.

- `principles`: Cross-cutting engineering principles that affect all other EDR subjects. Examples: test-driven development philosophy, secure-by-default engineering rule, GitOps as default, immutable infrastructure principle.
- `application`: Code-level implementation patterns and application conventions. Covers coding patterns, API implementation, testing approaches, in-code practices, and frontend and mobile implementation. Examples: framework selection, REST API conventions, error handling patterns, unit testing approach, caching strategy, feature flag implementation, security headers (CSP/HSTS) in code, structured log format, frontend framework selection, UI component library standards, a11y implementation patterns, i18n/l10n patterns, AI/ML inference integration patterns.
- `data`: Data layer implementation and data management decisions. Examples: ORM selection and usage patterns, database migration tooling (Flyway, Liquibase), query optimization guidelines, ETL/ELT implementation, connection pooling standards, data masking in non-production environments.
- `platform`: Infrastructure implementation, delivery pipeline, and developer environment decisions. Covers both production infrastructure and local developer tooling. Examples: IaC tool selection (Terraform, Pulumi), CI/CD pipeline stages, Docker image standards, Kubernetes manifest standards, git branching strategy, secrets management tooling (Vault, AWS Secrets Manager), cloud cost tagging standards, local developer environment and devcontainer setup.
- `operations`: Production behavior and operational response decisions. Covers observability, monitoring, alerting, and runtime incident handling. Examples: log and metric collection standards, distributed tracing implementation, alert routing and escalation, SLO/SLI measurement, incident post-mortem process, rollback procedures, developer productivity and DORA metrics measurement.
- `governance`: Engineering controls enforced as mandatory checks, gates, or approval policies. Examples: mandatory test coverage thresholds, dependency vulnerability scanning, security scanning in CI pipelines, license compliance checking, code review approval policies, breaking change approval process, deprecation enforcement.

#### 07-tiebreaker-rules

When a document could plausibly fit more than one subject, authors MUST apply these rules in order until one subject is clearly indicated.

1. `platform` vs `operations` (ADR and EDR): `platform` covers infrastructure capabilities and the delivery pipeline — decisions made before production. `operations` covers production behavior and response — monitoring, rollback, and incident handling. Multi-region topology MUST go in `platform`; rollback procedures MUST go in `operations`. See tiebreaker 22 for delivery pipeline specifics.

2. `application` vs `governance` (EDR): `application` covers how code is written — patterns, conventions, and in-code practices. `governance` covers mandatory controls enforced externally as a gate or automated scan. Security headers written into HTTP responses MUST go in `application`; a mandatory security scanning gate in CI MUST go in `governance`. Rate limiting middleware in code MUST go in `application`; a gateway-enforced rate limit threshold gate MUST go in `governance`. Container security hardening in Dockerfiles MUST go in `platform`; a mandatory container image vulnerability scan gate in CI MUST go in `governance`.

3. `platform` vs `governance` (ADR): `platform` covers capabilities you adopt as part of the runtime. `governance` covers security or compliance controls you enforce. SSO/IAM infrastructure MUST go in `platform`; encryption baseline policy and data classification tiers MUST go in `governance`. See tiebreaker 19 for extended security infrastructure guidance.

4. `application` vs `data` (EDR): `application` covers the implementation pattern in code. `data` covers storage, schema, and data management. A caching strategy MUST go in `application`; ORM configuration and database migration tooling MUST go in `data`.

5. `product` vs `finance` (BDR): `product` covers what is offered and how it behaves. `finance` covers financial governance and cost control. Pricing tier structure MUST go in `product`; pricing approval rules and margin controls MUST go in `finance`.

6. `product` vs `operations` (BDR): `product` covers the commitment made to customers. `operations` covers the process to deliver on that commitment. A customer SLA commitment MUST go in `product`; the operational workflow and escalation process to meet the SLA MUST go in `operations`.

7. Security decisions across types: Security as a concern distributes across subjects by layer — there is no single `security` subject. Authors MUST place security decisions by domain: architecture security controls in ADR `governance`; identity and auth infrastructure in ADR `platform`; secure coding practices and in-code security in EDR `application`; automated security enforcement gates in EDR `governance`.

8. Performance and capacity decisions: A performance design pattern MUST go in `application`. An enforced performance threshold or budget gate MUST go in `governance`. Performance infrastructure (CDN, autoscaling) MUST go in `platform`. Availability objectives and capacity planning (SLA targets, scaling strategy) MUST go in ADR `operations`.

9. Change management: Process automation and delivery pipeline steps MUST go in `platform`. Human authorization and approval policies for changes MUST go in `governance`.

10. `platform` abstraction level across ADR and EDR: ADR/platform covers the architectural choice — what to adopt, which topology, which strategy. EDR/platform covers the implementation conventions — tool configuration, pipeline stages, naming standards, and developer environment setup. A FinOps cost allocation strategy MUST go in ADR/platform; tagging naming conventions MUST go in EDR/platform. When a concern spans both layers, create two separate documents. See tiebreaker 18 for the general ADR-vs-EDR test.

11. On-call rotation across BDR and ADR: The on-call ownership model and system accountability structure MUST go in ADR `operations`; on-call scheduling, rotation cadence, and compensation policy MUST go in BDR `operations`.

12. AI/ML decisions: Model selection and inference architecture MUST go in ADR `application`; AI/ML inference implementation patterns MUST go in EDR `application`. Training pipeline infrastructure (GPUs, orchestration, experiment tracking) MUST go in `platform`. Dataset management, feature stores, model registries, and data labeling standards MUST go in `data`.

13. AI ethics, responsible AI, and agentic governance: Business-level AI ethics and responsible AI policy MUST go in BDR `governance`. Mandatory architecture-level AI controls (AI risk assessment, model risk governance) MUST go in ADR `governance`. Automated AI compliance gates in CI/CD (bias scanning, model validation) MUST go in EDR `governance`. In-code guardrails, prompt safety patterns, and agentic workflow implementation MUST go in EDR `application`. Human-in-the-loop thresholds as runtime behavior MUST go in ADR `operations`.

14. External technical vendor placement: Adopting a managed external technical service as a runtime capability (LLM API provider, observability SaaS, data warehouse) MUST go in ADR `platform`. Integrating with a third-party API as part of an application flow (payment gateway, identity provider, partner API) MUST go in ADR `application`. Risk assessment and due diligence for any external vendor MUST go in BDR `governance`. The business process for selecting and onboarding vendors MUST go in BDR `operations`.

15. `operations` vs `governance` for workforce and sustainability decisions (BDR): `operations` covers discretionary workforce policies. `governance` covers legally or regulatorily mandated obligations. Remote work policy MUST go in `operations`; labor law compliance and ESG regulatory reporting MUST go in `governance`. Voluntary sustainability targets MUST go in `operations`; mandatory ESG disclosure or regulatory sustainability compliance MUST go in `governance`.

16. `product` vs `operations` for customer-facing process decisions (BDR): `product` covers the policy for what is offered, how it is sold, and how it is communicated. `operations` covers the execution process to deliver on those policies. A sales commission structure MUST go in `product`; the operational workflow for onboarding a new customer MUST go in `operations`.

17. Single policy spanning multiple subjects — mandatory split: When one concern spans two subjects, authors MUST NOT merge them. Create two separate documents — one per subject — linked bidirectionally in each References section. Examples: GDPR erasure → one BDR `governance` (legal obligation) + one BDR `operations` (deletion workflow); DR → one BDR `governance` (DR policy) + one BDR `operations` (drill procedure).

18. ADR vs EDR for the same topic — abstraction-level test: If the decision answers *"what to adopt or how systems relate structurally"* → ADR. If it answers *"how to implement or configure that choice"* → EDR. When a concern spans both levels, create one ADR and one EDR in the same-named subject. Examples: error budget policy MUST go in ADR `operations`; SLO measurement implementation MUST go in EDR `operations`. Chaos engineering tool adoption MUST go in ADR `platform`; the chaos runbook standards MUST go in EDR `operations`.

19. Security infrastructure in ADR — `platform` vs `governance`: If the security technology primarily *provides* a runtime capability other systems depend on (KMS, VPN, network segmentation, certificate authority, PAM tooling) → `platform`. If it primarily *mandates, restricts, or audits* behaviour as a compliance control (encryption baseline, mandatory access review, data classification enforcement) → `governance`. When the same security concern yields both a capability adoption and an enforcement obligation, apply tiebreaker 17.

20. Runtime infrastructure always goes to `platform`: Any technology adopted as a runtime enabling capability — regardless of whether it also stores data (cache, message bus, search runtime, workflow engine, session store) — MUST go in `platform`. Place a technology in `data` only when it is selected for data storage, schema management, query patterns, or data lifecycle with no infrastructure runtime role. When both roles are present, apply tiebreaker 17. Examples: Redis as cache → ADR `platform`; ORM patterns → EDR `data`. Elasticsearch as search runtime → ADR `platform`; index schema standards → EDR `data`.

21. BDR `finance` vs `governance` — obligation vs strategy: If the financial decision is driven by external legal, regulatory, or contractual obligation (IFRS 15, tax law, banking capital rules, mandatory insurance) → `governance`. If it is a discretionary organizational financial decision (budget process, investment thresholds, pricing approval, revenue sharing, ESOP design) → `finance`.

22. Delivery pipeline vs production behavior — `platform` vs `operations`: Any decision governing what happens before or at deployment (build, test, package, deploy, canary rollout, blue-green switch) MUST go in `platform`. Any decision governing runtime behaviour after a successful deployment (monitoring, alerting, rollback trigger, incident response, SLO measurement) MUST go in `operations`. Sharpens tiebreaker 1: blue-green strategy → `platform`; rollback trigger and procedure → `operations`.

## References

- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md) — Framework structure, scopes, types, and subject folder placement
- [_core-adr-policy-002 - Policy standards](002-policy-standards.md) — How to write Policy documents
- [_core-adr-policy-017 - Policy numbering ranges](017-policy-numbering-ranges.md) — Reserved number block per subject
