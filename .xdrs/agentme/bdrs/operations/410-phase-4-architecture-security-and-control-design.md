---
name: agentme-bdr-policy-410-phase-4-architecture-security-controls
description: Defines phase 4 of the business and software lifecycle, Architecture, Security and Control Design - identifying systems and platforms, applying standards by risk class, turning control objectives into requirements, defining business controls and deriving non-functional requirements. Use when designing a solution after its risk class is known.
apply-to: Every business application, application service or change that passed phase 3
valid-from: 2026-11-26
---

# agentme-bdr-policy-410: Phase 4 - Architecture, security, controls

## Context and Problem Statement

Architecture and security are often designed from the team's preferences and controls are added at audit time. The standards that apply depend on the risk class, so the design must start from the classification and must produce the requirements that later phases test.

Question: What is designed in phase 4, who is accountable, and what must exist when it ends?

## Decision Outcome

**Phase 4 applies the standards of the risk class, transforms control objectives into requirements, defines business controls and derives the non-functional requirements that phases 5 and 6 verify**

### Details

#### 01-objective-and-entry

The objective is a design in which every applicable standard and control has a requirement. The entry MUST be the risk classification of phase 3.

#### 02-activities-and-outputs

Activities and outputs MUST include:

- identification of the systems, platforms and third-party providers involved
- application of the standards of the risk class: architecture, security and legal (`agentme-bdr-502` rule 04)
- the transformation of control objectives (ITGC) into requirements (`agentme-bdr-502` rule 05)
- business controls defined by the Control Owner, with the checks and evidence they need
- non-functional requirements derived from those requirements and standards: performance, availability, accessibility, security, privacy and operability
- the test strategy that maps requirements to test groups of `agentme-edr-503`, including the operational-readiness plan

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Architecture blueprint (cross-system) | | | | | | | A | | | C | | | | | | |
| Vendor/third-party selection, contract, and SLA negotiation | A | C | | | | | C | | | | | | | | | |
| Non-functional requirements sign-off (performance, accessibility, availability/reliability, security, privacy-by-design, including third-party assessment) | | | | | | | C | | | A (non-AI) | A (AI) | C | | | | |
| Cross-team shared-component ownership³ | | | | | | | C | | | A | | | | | | |
| Solution, platform, and security architecture standards | C | | C | | | | C | A | | C | C | C | | | | |
| Engineering and AI-practice standards | C | | C | | | | C | C | | C | C | A | | | | |
| Technical refinement | | | | | | | | | | A (non-AI) | A (AI) | | | | | |

³ Accountable: the shared/platform team's Tech Lead if one exists, otherwise one contributing team's Tech Lead designated by the Solution Architect; other contributing teams' Tech Leads are Informed.

The Control Owner, Security, Legal and the DPO define controls and standards outside this matrix (`agentme-bdr-502`).

#### 04-environments-and-tests

No environment applies. Phase 4 MUST plan the tests: group Development in phase 5, group Governance, group Business and operational readiness in phase 6 (`agentme-edr-503` rule 02).

#### 05-xdrs-outputs

Architecture and security requirements MUST be ADRs, non-functional requirements ADRs or EDRs, business controls BDRs of subject governance and technical controls EDRs of subject governance, all in the scope of the business application or application service per `agentme-bdr-416`. Standards of the risk class are inherited from the scopes of the standards-setters through `extends`.

#### 06-exit-gate

The Control Owner MUST confirm that controls and non-functional requirements are derived, and each applicable standards-setter MUST confirm that their standards are applied (`agentme-bdr-503` rule 01). A requirement without a verifying test or control MUST be fixed here before phase 5.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-416`](416-solution-content-map.md) - Where requirements and controls are documented
- [`agentme-bdr-502`](../governance/502-control-framework-and-standards-setters.md) - Standards-setters, Control Owner and control derivation
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
- [`agentme-edr-503`](../../edrs/governance/503-test-groups-and-release-flow.md) - Test groups and flow
