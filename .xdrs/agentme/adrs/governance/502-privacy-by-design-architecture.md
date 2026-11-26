---
name: agentme-adr-policy-502-privacy-by-design-architecture
description: Defines the architectural rules for systems that process personal data under the GDPR: minimisation, EU/EEA residency, processors, security baseline, automated decisions and AI. Use when designing or reviewing architecture of a system whose GDPR applicability is "applicable".
apply-to: Systems whose hub policy (agentme-adr-policy-501) declares GDPR as applicable, in design, implementation and review
valid-from: 2026-11-23
---

# agentme-adr-policy-502: Privacy by design architecture

## Context and Problem Statement

Privacy added after the architecture is fixed is expensive and usually incomplete. The GDPR requires data protection by design and by default (Art. 25) and security appropriate to the risk (Art. 32).

Question: Which architectural rules must a system follow so it can process personal data lawfully and securely?

## Decision Outcome

**Systems that process personal data MUST minimise it by design, keep it in the EU/EEA by default, share it only with contracted processors, and protect it with a fixed security baseline**

Applicability, classification and declarations are defined in [agentme-adr-policy-501](501-gdpr-applicability-and-declarations.md). Retention and erasure are in [agentme-adr-policy-201](../data/201-personal-data-retention-and-erasure.md). Nothing here is legal advice.

### Details

#### 01-minimise-and-limit-purpose

Each personal data field MUST map to a declared purpose, and fields without one MUST NOT be collected. Defaults MUST be the most privacy-protective option (Art. 5(1)(b)-(c), Art. 25(2)). Data collected for one purpose MUST NOT be reused for an incompatible one without a new lawful basis.

#### 02-inventory-in-architecture-docs

Architecture documentation MUST list every store, queue, cache, log, index, analytics sink and third party that holds personal data, with category, tier (see agentme-adr-policy-501 rule 02), purpose and location. This list is the evidence behind the `ropa` and `processors-and-transfers` hub items and MUST be updated in the same change that adds a new data flow.

#### 03-eu-eea-residency-by-default

Personal data MUST be stored and processed in the EU/EEA by default. A transfer outside the EEA MUST rely on an adequacy decision, standard contractual clauses or another Chapter V mechanism (Art. 44-49), and MUST be recorded in the `processors-and-transfers` hub item with the destination and the mechanism. Remote access from a third country counts as a transfer.

#### 04-processors-before-data

Personal data MUST NOT be sent to a third-party service (SaaS, analytics, email, support desk, CDN with logs, LLM API) before an Art. 28 agreement exists and the service is listed in `processors-and-transfers`. Adding or replacing a sub-processor MUST update that list before release.

#### 05-security-baseline

Systems MUST apply all of the following (Art. 32):

- TLS for every network path carrying personal data, and encryption at rest for every store holding it.
- Encryption keys and secrets managed outside the data store, per [agentme-edr-124](../../edrs/application/124-secrets-management.md).
- Least-privilege access with named identities, and an audit log of reads and changes of personal data. Audit logs MUST NOT contain the personal data itself.
- Pseudonymisation where the purpose allows it, with the re-identification key held separately from the pseudonymised data.
- Backups with tested restore and a regular, recorded review of these controls.

#### 06-breach-detection-is-designed-in

The architecture MUST give the team the means to learn of a breach quickly: alerting on anomalous access and an audit trail sufficient to determine which data subjects and categories were affected. This supports the 72-hour authority notification of Art. 33.

#### 07-automated-decisions

A system MUST NOT take a decision based solely on automated processing, including profiling, that produces legal or similarly significant effects on a person, unless an Art. 22(2) exception applies. When it applies, the system MUST provide human intervention, a way for the person to express a view and contest the decision, and an explanation of the logic involved. Decisions based on special category data MUST meet Art. 22(4). Such processing MUST have a DPIA (Art. 35(3)(a)). Bias and fairness evaluation follows [agentme-edr-156](../../edrs/application/156-ai-eval-fairness-bias.md).

#### 08-ai-and-personal-data

Personal data MUST NOT enter prompts, fine-tuning sets, evals or vector stores unless the purpose has a lawful basis, the data is minimised, and the model provider is a listed processor that does not train on it. Where possible, data SHOULD be pseudonymised or removed before it reaches the model. LLM development rules are in [agentme-edr-141](../../edrs/application/141-ai-llm-development-standards.md).

#### 09-environments

Production personal data MUST NOT leave `prd` unless masked or pseudonymised, per [agentme-edr-policy-202](../../edrs/data/202-personal-data-storage-and-erasure.md) and the environment rules of [agentme-adr-301](../platform/301-computational-environments.md).

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 5, 22, 25, 28, 32, 33, 35, 44-49.
