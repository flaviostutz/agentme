---
name: agentme-adr-policy-201-personal-data-retention-and-erasure
description: Defines how a system declares retention per personal data category and how erasure is designed to reach every store, including backups, caches, indexes, event logs and processors. Use when designing data stores, purge jobs, backups or erasure flows for personal data.
apply-to: Systems whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-adr-policy-201: Personal data retention and erasure

## Context and Problem Statement

Personal data may be kept no longer than necessary (Art. 5(1)(e)) and must be erased on valid request (Art. 17). Data copied into replicas, caches, indexes, event streams, backups and third-party systems is routinely forgotten.

Question: How must a system declare retention and design erasure so it reaches every copy of personal data?

## Decision Outcome

**Every personal data category MUST have a declared retention period and an automated purge, and erasure MUST propagate to every copy of the data**

Declaration lives in the `retention` item of the hub policy defined in [agentme-adr-policy-501](../governance/501-gdpr-applicability-and-declarations.md). Implementation rules are in [agentme-edr-policy-202](../../edrs/data/202-personal-data-storage-and-erasure.md). Nothing here is legal advice.

### Details

#### 01-retention-per-category

Each personal data category MUST have a retention period or an objective end criterion (for example "until the account is closed plus 30 days") recorded with its purpose. "Indefinitely" and "until needed" MUST NOT be used. Retention MUST be re-evaluated when the purpose changes.

#### 02-purge-is-automated-and-verifiable

Expired data MUST be removed by a scheduled, idempotent job. Each run MUST record what was purged (counts and categories, never the personal data) so a reviewer can verify the purge ran.

#### 03-erasure-propagates-everywhere

Erasure and anonymisation MUST reach all of: primary stores, read replicas, caches, search indexes, event logs and streams, data warehouses and analytics, file and object storage, and processors that hold the data. Each store MUST have a named erasure mechanism in the architecture inventory ([agentme-adr-policy-502](../governance/502-privacy-by-design-architecture.md) rule 02). A store with no mechanism MUST NOT hold personal data.

#### 04-soft-delete-is-not-erasure

Flags such as `deleted=true` MUST NOT count as erasure. Soft-deleted personal data MUST be hard-deleted or irreversibly anonymised within the declared retention period.

#### 05-backups-and-restore

Backups holding personal data MUST expire on a fixed schedule, by default no longer than 35 days. After any restore, the log of erasures performed since the backup MUST be re-applied before the system serves traffic. Longer backup retention MUST be justified in the `retention` item.

#### 06-operational-data-defaults

Application and access logs that can contain personal data (including IP addresses) MUST be retained no longer than 30 days by default. Longer periods MUST be justified in the `retention` item. These two numeric defaults apply only to operational data; business data periods are declared per rule 01.

#### 07-legal-retention-exceptions

Data MAY be kept beyond its normal period only for a legal obligation or legal claims (Art. 17(3)). The exception MUST be documented with its legal reason and end date, access MUST be restricted, and the data MUST NOT be used for other purposes.

#### 08-anonymisation-must-be-irreversible

Data counts as anonymised only if re-identification is not reasonably possible, including by combining it with other data the system holds. The technique MUST be recorded. Otherwise it is pseudonymised and remains personal data.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 5(1)(e), 17.
