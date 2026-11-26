# GDPR audit checklist

Audit map for `review-gdpr`. Each row says what to look for and which policy rule to cite. Cite findings as `policy-name.NN-rule-title`. A MUST gives an ERROR, a SHOULD a WARNING. Nothing here is legal advice.

## Hub and declarations (agentme-adr-policy-501)

| Look for | Rule |
|---|---|
| Exactly one `adrs/principles/010-gdpr-applicability.md` in the scope | `03-hub-policy-is-mandatory` |
| Entries as `#### NN-<id>` with `Key: value` lines | `04-hub-entry-format` |
| Opt-out has reason, inventory, owner, review date within 12 months, no items, no other `gdpr-*` policy | `05-opt-out-form` |
| Opt-out contradicted by fields, trackers, data files, LLM SDKs, docs | `05-opt-out-form` |
| All 8 items declared, pointers resolve to adequate content | `06-applicable-form` |
| Not-applicable used only on dpo, ropa, dpia, processors-and-transfers, with reasoning, owner, date | `07-not-applicable-entry` |
| Processor role: Art. 28 duties, DPA pointer for lawful bases | `08-processor-role` |
| Dedicated `011-019` policies non-empty, not created for not-applicable items | `09-dedicated-policies-are-optional` |

## Architecture (agentme-adr-policy-502, agentme-adr-policy-201)

| Look for | Rule |
|---|---|
| Fields without a declared purpose; defaults not privacy-protective | `502.01-minimise-and-limit-purpose` |
| Architecture docs listing every store, flow, third party holding personal data | `502.02-inventory-in-architecture-docs` |
| Regions outside the EEA in IaC or config; transfers without mechanism | `502.03-eu-eea-residency-by-default` |
| Third-party SDKs, SaaS, LLM APIs receiving personal data without a listed processor | `502.04-processors-before-data` |
| TLS, encryption at rest, separate keys, least privilege, audit log, pseudonymisation, tested restore | `502.05-security-baseline` |
| Alerting and audit trail for breach detection | `502.06-breach-detection-is-designed-in` |
| Decisions solely automated with significant effects, no human review or contest | `502.07-automated-decisions` |
| Personal data in prompts, fine-tuning sets, evals, vector stores | `502.08-ai-and-personal-data` |
| Retention per category; "indefinite" periods | `201.01-retention-per-category` |
| Purge jobs, soft delete as erasure, propagation to replicas, caches, indexes, streams, analytics | `201.02` to `201.04` |
| Backup expiry over 35 days, no erasure replay; logs over 30 days without justification | `201.05`, `201.06` |

## Consent and UX (agentme-edr-policy-161)

| Look for | Rule |
|---|---|
| Pre-ticked boxes, bundled consent, one choice for all purposes | `01-explicit-opt-in-per-purpose` |
| Refuse harder than accept, nagging, hidden refuse | `02-equal-choice-no-dark-patterns` |
| Analytics, ads, replay, social SDKs initialised before consent; undocumented trackers | `03-cookies-trackers-and-sdks` |
| Privacy notice at collection with required content | `04-informed-at-collection` |
| Withdrawal harder than giving; no persistent control | `05-withdrawal-as-easy-as-giving` |
| Consent record fields, notice version | `06-consent-record` |
| Children: parental consent, no marketing profiling | `07-children` |
| Tests for pre-consent requests and withdrawal | `09-testing` |

## Code (agentme-edr-policy-162) and storage (agentme-edr-policy-202)

| Look for | Rule |
|---|---|
| Untagged personal fields | `162.01-tag-personal-data-in-the-model`, `202.01-field-level-tagging` |
| Missing access, portability, rectification, erasure, restriction, objection operations; no identity verification | `162.02-data-subject-rights-endpoints` |
| Reads without per-user authorisation or audit events; audit events holding personal data | `162.03-least-privilege-and-audit` |
| Personal data in logs, errors, URLs, metrics, analytics, crash reports, prompts | `162.04-keep-personal-data-out-of-side-channels` |
| Calls to services not on the processor list | `162.05-third-party-allowlist` |
| Production extracts in tests, fixtures or non-prd environments | `162.07-secrets-and-test-data`, `202.04-no-production-personal-data-outside-prd` |
| Keys with the data, no encryption at rest | `202.02-encryption-and-key-separation` |
| Purge jobs without tests; erasure not across all stores, no erasure log | `202.05-purge-jobs`, `202.06-erasure-requests` |
| Export not tag-driven, not authenticated, not time-limited | `202.08-export-format` |

## Runbooks and organisation (agentme-edr-policy-408, agentme-bdr-policy-501, agentme-bdr-policy-406)

| Look for | Rule |
|---|---|
| Owner, last review within 12 months, last drill, case register | `408.01-common-requirements` |
| Request runbook checklist items; deadline and extension handling | `408.02-data-subject-request-checklist`, `bdr-501.07-data-subject-requests` |
| Breach runbook checklist; 72-hour decision; processor notice | `408.03-breach-checklist`, `bdr-501.08-breach-notification` |
| Drill evidence within 12 months | `408.04-drill-evidence`, `bdr-406.06-drills` |
| Owner, DPO or reasoned absence, register, DPIA, DPAs, lawful bases and consent records | `bdr-501.01` to `bdr-501.06` |
| Roles, RACI, time targets | `bdr-406.01-roles` to `bdr-406.04-escalation` |

## Evidence rules

- Cite file and line of the evidence and of the policy rule.
- Redact values: report type and location only.
- Unverifiable external evidence is a WARNING, never an ERROR.
