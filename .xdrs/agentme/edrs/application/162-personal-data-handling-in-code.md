---
name: agentme-edr-policy-162-personal-data-handling-in-code
description: Defines how code handles personal data under the GDPR: field tagging, data subject request endpoints with identity verification, access control and audit, no personal data in logs or URLs, SDK allowlist and AI guardrails. Use when implementing or reviewing code that reads, stores, exports, logs or sends personal data.
apply-to: Source code, APIs and tests of applications whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-edr-policy-162: Personal data handling in code

## Context and Problem Statement

Most GDPR violations in software are small implementation leaks: personal data in logs, URLs and analytics events, unverified deletion requests, or access nobody can audit.

Question: What must code do and avoid when it handles personal data?

## Decision Outcome

**Code MUST tag personal data, expose verified self-service for data subject rights, restrict and audit access, and keep personal data out of logs, URLs, errors, analytics and prompts**

Architecture is in [agentme-adr-policy-502](../../adrs/governance/502-privacy-by-design-architecture.md) and storage implementation in [agentme-edr-policy-202](../data/202-personal-data-storage-and-erasure.md). Nothing here is legal advice.

### Details

#### 01-tag-personal-data-in-the-model

Every field that holds personal data MUST be tagged in the data model or schema with its category and tier (see [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md) rule 02), so export, erasure, masking and review are driven from the tags rather than from memory.

#### 02-data-subject-rights-endpoints

The application MUST provide a way, either self-service or a documented internal operation, for access and portability (Art. 15, 20), rectification (Art. 16), erasure (Art. 17), restriction (Art. 18) and objection (Art. 21). Each operation MUST:

- verify the requester's identity first, using the least data needed, and never accept an email alone as proof for disclosure or deletion;
- cover every store listed in the architecture inventory;
- return exports in a structured, machine-readable format (JSON or CSV);
- be recorded in the request register per [agentme-bdr-policy-406](../../bdrs/operations/406-gdpr-request-and-breach-workflow.md) rule 05.

#### 03-least-privilege-and-audit

Code paths that read personal data MUST check authorisation per user and purpose, not only per role. Reads, exports and changes of personal data MUST write an audit event containing actor, action, subject ID (pseudonymous), timestamp and reason, and MUST NOT contain the personal data itself. Bulk export MUST require elevated permission.

#### 04-keep-personal-data-out-of-side-channels

Personal data MUST NOT appear in log messages, error messages, stack traces, URLs and query strings, metrics labels, analytics events, crash reports or prompts to external AI services. Code MUST log stable pseudonymous IDs instead. Request and response body logging MUST be off by default for endpoints handling personal data, and error handling follows [agentme-edr-123](123-error-handling.md).

#### 05-third-party-allowlist

Application code MUST send personal data only to services on the processor list of the `processors-and-transfers` hub item. SDKs and clients for other services MUST NOT receive it. Adding an SDK that can transmit user data MUST go through review and update the list.

#### 06-ai-guardrails

Code that calls an AI model with personal data MUST minimise or pseudonymise inputs, MUST NOT send special category data unless the lawful basis and processor allow it, and MUST store prompts and outputs under the same retention as the data. Features that decide about people MUST implement the human review and contest path of [agentme-adr-policy-502](../../adrs/governance/502-privacy-by-design-architecture.md) rule 07.

#### 07-secrets-and-test-data

Secrets follow [agentme-edr-124](124-secrets-management.md). Tests and fixtures MUST use synthetic data only, never production extracts.

#### 08-tests

Tests MUST cover each data subject right operation (including identity failure), the audit event on access, absence of personal data in logs for a sample request, and the tags driving export and erasure for every new personal field.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 5, 15-21, 25, 32.
