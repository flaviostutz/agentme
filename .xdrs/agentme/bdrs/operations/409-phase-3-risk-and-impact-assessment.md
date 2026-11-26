---
name: agentme-bdr-policy-409-phase-3-risk-and-impact-assessment
description: Defines phase 3 of the business and software lifecycle, Risk and Impact Assessment - CIA levels, AI system type, GDPR assessment, legal and risk appetite - and the risk classification record each business application keeps. Use when classifying a solution or change before designing it.
apply-to: Every business application, application service or change that passed phase 2
valid-from: 2026-11-26
---

# agentme-bdr-policy-409: Phase 3 - Risk and Impact Assessment

## Context and Problem Statement

Standards, controls and approvals depend on how risky a solution is, but risk is often judged late or implicitly. Without a recorded classification, phase 4 cannot choose standards and phase 6 cannot tell what level of approval is needed.

Question: How is a solution classified, by whom, and where is the result kept?

## Decision Outcome

**Phase 3 classifies the solution against the organisation's own scales and keeps the result in a risk classification record in the solution scope; the policy defines the process and the record, not the scales**

### Details

#### 01-objective-and-entry

The objective is a clear risk classification. The entry MUST be the scope approved in phase 2, or a change in phase 8 whose inputs affect risk.

#### 02-activities-and-outputs

The team MUST assess, using the organisation's scales defined by the Risk function (`agentme-bdr-502` rule 03):

- confidentiality, integrity and availability (CIA) levels
- the AI system type, when AI is involved, including relevant AI regulation
- the GDPR assessment per `agentme-adr-501` and `agentme-bdr-501`
- legal and contractual obligations
- the impact on other businesses and systems
- the fit with the organisation's risk appetite, producing one overall risk class

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Initial compliance/privacy/risk triage, including breach-notification escalation | | A | | | | | C | | | | | | | | | C (Business SME) |
| Complex or high-risk stakeholder and issue/risk (RAID) management | C | C | A | | | | | | | | | | | | | |

The Risk function, Legal, Security and the DPO assess and approve outside this matrix (`agentme-bdr-405` rule 07, `agentme-bdr-502`).

#### 04-environments-and-tests

No environment or test group applies. Assessment evidence MUST come from the experiments and requirements of phases 1 and 2.

#### 05-xdrs-outputs

Each business application scope MUST contain exactly one ADR policy `adrs/principles/011-risk-classification.md` in the structured rule format of `_core-adr-policy-008`, following the hub pattern of `agentme-adr-501`. It MUST record the levels, the overall risk class and the resulting set of applicable standards. It MUST NOT contain exploitable details such as vulnerabilities, secrets or credentials. An application service scope inherits it and overrides it only with a `## Conflicts` section. The GDPR applicability hub `010-gdpr-applicability` stays separate.

#### 06-exit-gate

The Risk function MUST confirm that the classification is clear and complete (`agentme-bdr-503` rule 01). A change that alters a level MUST return here and update the record.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview and risk classes
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-416`](416-solution-content-map.md) - Where the record is placed
- [`agentme-bdr-501`](../governance/501-gdpr-organisational-obligations.md) - GDPR organisational obligations
- [`agentme-bdr-502`](../governance/502-control-framework-and-standards-setters.md) - Risk function and standards-setters
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
- [`agentme-adr-501`](../../adrs/governance/501-gdpr-applicability-and-declarations.md) - GDPR tiers and the applicability hub pattern
