---
name: agentme-adr-policy-501-gdpr-applicability-and-declarations
description: Defines when GDPR applies to an application, how it is classified, and the single mandatory applicability policy (hub) in which an application declares an explicit opt-out or points to how each GDPR item is handled. Use when scoping, declaring or auditing GDPR compliance of an application.
apply-to: Every application, service or library whose XDRS scope follows agentme, whether or not it handles personal data
valid-from: 2026-11-23
---

# agentme-adr-policy-501: GDPR applicability and declarations

## Context and Problem Statement

Applications often handle personal data without anyone deciding, in writing, whether the GDPR applies, who is responsible, or where records and runbooks live. Auditors and agents then cannot tell "not applicable" from "forgotten".

Question: How does an application declare, explicitly and verifiably, whether the GDPR applies and how each obligation is handled?

## Decision Outcome

**Every application scope MUST contain one applicability policy, `010-gdpr-applicability`, that either opts out of the GDPR with a reason or explains and points to how each GDPR item is handled**

This policy is the single source for the hub contract. Other policies and the `review-gdpr` skill link here and never restate it. Nothing here is legal advice. Legal sources are cited from the consolidated GDPR text on [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj).

### Details

#### 01-applicability-test

The GDPR MUST be treated as applicable when the application processes personal data of natural persons: end users, employees, B2B contacts, and online identifiers such as IP address, device ID, cookie ID or advertising ID. Pure development-time metadata (for example git authors, build logs without user identifiers) does not trigger applicability. Pseudonymised data is still personal data; only effectively anonymised data is out of scope. When unsure, the application MUST be treated as in scope until the inventory proves otherwise.

#### 02-classification-tiers

Data MUST be classified into these tiers, each stricter than the previous:

1. **Personal**: any information relating to an identifiable person (Art. 4).
2. **Children**: data of minors; consent age is 16 unless the Member State lowers it, never below 13 (Art. 8).
3. **Special category**: health, biometrics, genetics, ethnicity, religion, political or union views, sex life, orientation (Art. 9).
4. **Criminal**: convictions and offences (Art. 10).

Pseudonymised and anonymised data MUST be labelled as such with the technique used; the stricter tier of the source data applies until anonymisation is demonstrated.

#### 03-hub-policy-is-mandatory

Each application scope MUST contain exactly one ADR policy at `adrs/principles/010-gdpr-applicability.md`, in `_local` or in any scope that follows agentme. It MUST use the structured rule format of `_core-adr-policy-008`. A scope with no hub, or with two, is non-compliant, even if it holds no personal data.

#### 04-hub-entry-format

Every entry MUST be a rule heading `#### NN-<id>` followed by `Key: value` lines, one per line, so humans and the `check` script read the same text. Keys: `Status`, `Reason`, `Inventory`, `Role`, `Data-categories`, `Pointer`, `Explanation`, `Reasoning`, `Owner`, `Review-date` (`YYYY-MM-DD`). Rule `01-applicability` MUST be first; item entries follow.

#### 05-opt-out-form

An application opts out only by writing `01-applicability` with `Status: opted-out` and all of: `Reason` (why no personal data is processed), `Inventory` (the data stores, logs and integrations reviewed, showing no personal data), `Owner`, and `Review-date` at most 12 months ahead. An opted-out hub:

- MUST NOT contain item entries.
- MUST NOT coexist with any other `gdpr-*` policy in the scope (ADR, BDR or EDR); a dedicated policy next to an opt-out is a contradiction.
- MUST be re-confirmed by the owner before the review date. An expired date makes the opt-out invalid.
- Is invalid when the code, configuration or data contradicts the claim; the contradiction is a finding on the claim, not a reason to ignore the data.

An opt-out MUST NOT be inferred from silence, from a missing hub, or from a README sentence.

#### 06-applicable-form

An applicable hub writes `01-applicability` with `Status: applicable`, `Data-categories` (the categories and tiers from rule 02) and `Explanation` (how the GDPR applies to this application). It then declares **every** item in the table below. Each item entry gives an `Explanation` of what the item means for this application, and either `Status: pointer` with a `Pointer` (relative link, or URL for external documents) or `Status: not-applicable` under rule 07. A pointer MUST resolve to a non-empty document that meets the content listed for that item. The `roles` entry also carries `Role: controller`, `processor` or `joint`.

| Item id | Required content at the pointer | May be not-applicable |
|---|---|---|
| `roles` | Controller, processor or joint role, and EU representative if not established in the EU (Art. 27) | No |
| `dpo` | DPO designation and contact (Art. 37-39) | Yes, when Art. 37(1) is not met |
| `ropa` | Record of processing (Art. 30) | Yes, under the Art. 30(5) exemption |
| `dpia` | Impact assessment, or the screening showing it is not needed (Art. 35) | Yes, when a documented screening finds no high risk and no Art. 35(3) trigger |
| `processors-and-transfers` | Processor list, agreements (Art. 28), transfer mechanism and residency (Art. 44-49) | Yes, when no processor and no non-EEA transfer exists |
| `retention` | Retention period per data category and purge approach (Art. 5(1)(e)) | No |
| `lawful-bases-and-consents` | Lawful basis per purpose (Art. 6), consent records (Art. 7), privacy notice (Art. 13-14) | No (a processor points to the controller's agreement) |
| `dsr-and-breach-runbooks` | Location of the data subject request and breach runbooks (Art. 12-22, 33-34) | No |

#### 07-not-applicable-entry

`Status: not-applicable` is allowed only for the items marked "Yes" in rule 06. It MUST include `Reasoning` citing the legal condition, an `Owner`, and a `Review-date` at most 12 months ahead. An expired date, or a reason contradicted by the evidence, is invalid like an opt-out.

#### 08-processor-role

When `Role` is `processor`, the application MUST also meet the processor duties of Art. 28 (documented instructions, sub-processor list, assistance, breach notice to the controller). For `lawful-bases-and-consents`, the entry MAY be `Status: pointer` to the data processing agreement and state that the controller owns lawful basis and the privacy notice.

#### 09-dedicated-policies-are-optional

When an item needs its own document, it MAY be a policy `NNN-gdpr-<item-id>.md` in ADR `principles`, numbered 011 to 019, and the hub points to it. A dedicated policy MUST NOT be created empty, as a placeholder, or for an item the hub marks not-applicable. Items MAY instead point to runbooks, registers or external documents that meet rule 06.

#### 10-single-source

Other policies and skills MUST link to the item ids in rule 06 and MUST NOT restate the table. The `check` script of [agentme-edr-policy-504](../../edrs/governance/504-gdpr-automated-checks.md) keeps its item list identical to rule 06; a test enforces that.

## Related policies

- [agentme-adr-policy-502](502-privacy-by-design-architecture.md) and [agentme-adr-policy-201](../data/201-personal-data-retention-and-erasure.md): architecture and retention rules.
- [agentme-bdr-policy-501](../../bdrs/governance/501-gdpr-organisational-obligations.md): organisational duties behind the items.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 4, 5, 6, 7, 8, 9, 10, 12-22, 27, 28, 30, 33-35, 37-39, 44-49.
- [_core-adr-policy-008 - Structured policy rules](../../../_core/adrs/principles/008-policy-structured-standards.md)
