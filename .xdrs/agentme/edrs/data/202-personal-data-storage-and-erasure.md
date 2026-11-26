---
name: agentme-edr-policy-202-personal-data-storage-and-erasure
description: Defines how databases, object storage, backups and exports implement personal data protection: field tagging, encryption, key separation, pseudonymisation, masking, production data outside prd, purge jobs and export format. Use when implementing stores, migrations, seed data, data copies or purge jobs for personal data.
apply-to: Databases, object stores, data pipelines, IaC and operational data copies of applications whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-edr-policy-202: Personal data storage and erasure

## Context and Problem Statement

Stores, pipelines and copies are where personal data silently multiplies. Architecture decisions on retention and security need concrete implementation rules for schemas, encryption, data copies and purge jobs.

Question: How must databases, storage, data copies and purge jobs be implemented for personal data?

## Decision Outcome

**Personal data MUST be tagged at field level, encrypted, kept in `prd` unless masked or pseudonymised, and purged by tested jobs that follow the declared retention**

Architecture is in [agentme-adr-policy-201](../../adrs/data/201-personal-data-retention-and-erasure.md) and [agentme-adr-policy-502](../../adrs/governance/502-privacy-by-design-architecture.md). Application code rules are in [agentme-edr-policy-162](../application/162-personal-data-handling-in-code.md). Nothing here is legal advice.

### Details

#### 01-field-level-tagging

Schemas MUST mark personal columns and fields with category and tier through a machine-readable convention (column comments, metadata files or schema annotations). Migrations that add a personal field MUST add the tag and the retention entry in the same change.

#### 02-encryption-and-key-separation

Stores holding personal data MUST use encryption at rest provided by the platform or application-level encryption for special category fields. Keys MUST live in a managed key service separate from the data store and its backups, rotated on a documented schedule.

#### 03-pseudonymisation-and-masking

Direct identifiers SHOULD be stored apart from behavioural or event data and linked by a pseudonymous key. Views, exports and analytics datasets MUST expose masked or pseudonymised values unless the purpose requires direct identifiers.

#### 04-no-production-personal-data-outside-prd

Production personal data MUST NOT be copied to `sbx`, `dev`, `tst`, `acc`, a laptop or a CI runner (environments in [agentme-adr-301](../../adrs/platform/301-computational-environments.md)), unless first masked or pseudonymised by an automated, reviewed process that removes direct identifiers and cannot be reversed in the target environment. Other environments MUST use synthetic data by default.

#### 05-purge-jobs

Purge jobs MUST implement the declared retention for each tagged category, run on a schedule, be idempotent, handle replicas, caches, indexes and object storage listed in the inventory, and log counts only. Each job MUST have a test with synthetic expired and non-expired records proving only the expired ones are removed.

#### 06-erasure-requests

An erasure operation MUST be a transaction or compensating saga across all stores, report per-store success, and retry failures until complete. Erasures MUST be written to an erasure log (subject pseudonym and timestamp, no personal data) so restores can re-apply them ([agentme-adr-policy-201](../../adrs/data/201-personal-data-retention-and-erasure.md) rule 05).

#### 07-backups

Backup expiry MUST be configured in IaC to the declared period (default at most 35 days) and backups MUST be encrypted with keys separate from the live store. A restore drill MUST be run at least yearly.

#### 08-export-format

Data export for access and portability MUST be produced from the tags in rule 01, in JSON or CSV with a documented schema, include only the requester's data, and be delivered through an authenticated channel with a limited lifetime.

#### 09-ci-evidence

Where the application's CI runs the checker of [agentme-edr-policy-504](../governance/504-gdpr-automated-checks.md), new personal fields without a tag or retention entry SHOULD fail review.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 5(1)(e), 17, 20, 25, 32.
