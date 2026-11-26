---
name: agentme-bdr-policy-416-solution-content-map
description: Maps each kind of information about a business or solution (requirements, controls, data, architecture, runbooks, skills, prototypes) to the XDRS document type, subject and location where it belongs. Use when deciding where to write something about a solution.
apply-to: Every business application and application service scope
valid-from: 2026-11-26
---

# agentme-bdr-policy-416: Solution content map

## Context and Problem Statement

When people can place solution information anywhere, the same fact is written in several places and parts are missing. Auditors and agents need a predictable place for each concern.

Question: Which XDRS document type and location holds each kind of information about a solution?

## Decision Outcome

**Each concern has one place in the solution scope; everything except the codebase and generated evidence is written in XDRS**

### Details

#### 01-content-map

Each kind of content MUST be written where this table places it.

| Content | Where |
|---|---|
| Business requirements, business policies, plan and milestones | BDR (principles or operations), initiative for plan and milestones |
| Usability requirements | BDR of subject product |
| Data requirements | ADR of subject data |
| Architecture, security and non-functional requirements | ADR or EDR of the matching subject |
| Business controls | BDR of subject governance |
| Technical controls (ITGC) | EDR of subject governance |
| Risk classification result | ADR `adrs/principles/011-risk-classification.md` of the solution scope (`agentme-bdr-409`) |
| Platform and coding standards | ADR or EDR of subjects platform and application |
| Runbooks and operational procedures | EDR of subject operations |
| Skills that automate development, operation or evidence generation | Skills of the scope |
| Findings, hypotheses and spikes | Research |
| Work plans and trackers | Initiative |
| Explanations and stakeholder material | Article or presentation |

#### 02-prototypes

A standalone prototype MUST be placed in the `.assets/` folder of the research or initiative that explores it, only when no cloud is involved and no company data is used. Assets carry no policy content and MUST be materially necessary (`_core-adr-policy-020` rules 07 and 08). A prototype that needs cloud or company data is built in phase 5.

#### 03-not-in-xdrs

The codebase, generated evidence (test reports, logs, scan output), secrets, personal data and exploitable details MUST NOT be written in XDRS. XDRS MAY cite their identifiers and locations.

#### 04-one-place

A fact MUST have one home. Other documents MUST link to it instead of repeating it. Content common to several applications belongs in the business application scope, and content of one application in its application service scope (`agentme-adr-001`).

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle phases
- [`agentme-bdr-005`](../principles/005-xdrs-single-source-of-truth.md) - XDRS as the single source of truth
- [`agentme-bdr-409`](409-phase-3-risk-and-impact-assessment.md) - Risk classification record
- [`agentme-bdr-415`](415-solution-scope-lifecycle.md) - Solution scope lifecycle
- [`agentme-adr-001`](../../adrs/principles/001-business-application-and-application-service-scopes.md) - Scope model
- [`_core-adr-policy-016`](../../../_core/adrs/principles/016-policy-subjects.md) - Policy subjects
- [`_core-adr-policy-020`](../../../_core/adrs/principles/020-media-and-asset-standards.md) - Assets
