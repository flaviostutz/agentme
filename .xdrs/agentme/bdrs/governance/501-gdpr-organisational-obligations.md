---
name: agentme-bdr-policy-501-gdpr-organisational-obligations
description: Defines the organisational duties behind GDPR for applications that process personal data: accountability, DPO, processing register, DPIA, processors, lawful bases and consent records, data subject request deadlines and breach notification. Use when assigning owners or deciding when a duty is triggered.
apply-to: Organisations operating applications whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-bdr-policy-501: GDPR organisational obligations

## Context and Problem Statement

Technical controls alone do not make an application compliant. Someone must own the duties, keep records, decide on impact assessments, and respond to people and regulators within legal deadlines.

Question: Which organisational duties must exist for an application that processes personal data, and who triggers them when?

## Decision Outcome

**Each application MUST have a named owner accountable for the GDPR duties below, each declared as an item of the hub policy and kept current**

Items and declaration format are defined in [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md). Architecture is in [agentme-adr-policy-502](../../adrs/governance/502-privacy-by-design-architecture.md). The workflow for requests and breaches is in [agentme-bdr-policy-406](../operations/406-gdpr-request-and-breach-workflow.md). Nothing here is legal advice.

### Details

#### 01-accountability

The organisation MUST name an owner for each application's GDPR duties and MUST be able to demonstrate compliance on request (Art. 5(2), 24). The owner MUST review the hub policy and its pointers at least every 12 months and on any significant change of data, purpose or processors.

#### 02-roles-and-dpo

The organisation MUST determine, per application, whether it acts as controller, processor or joint controller (`roles` item). A DPO MUST be designated when Art. 37(1) applies (public authority, large-scale regular and systematic monitoring, or large-scale special category data); otherwise the `dpo` item MUST record why not. Contact details MUST be published to data subjects and the authority.

#### 03-processing-register

Unless the Art. 30(5) exemption applies and is recorded, the organisation MUST keep a record of processing activities (`ropa`) with the content of Art. 30(1) (processors: Art. 30(2)). It MUST be updated when a processing activity, purpose, recipient or transfer changes and MUST be available to the authority on request.

#### 04-impact-assessment

A DPIA MUST be completed before processing starts when it is likely to result in high risk, in particular for the cases of Art. 35(3): systematic and extensive profiling with significant effects, large-scale special category or criminal data, and large-scale public-area monitoring. New technologies, large-scale children data and AI decisions about people SHOULD be screened. The DPO MUST be consulted when designated, and the DPIA MUST be reviewed when the risk changes (Art. 35(11)). A screening that concludes "not needed" MUST be written down.

#### 05-processors

Before a processor receives personal data, the organisation MUST have an Art. 28 agreement, MUST have checked the processor's security and sub-processors, and MUST record it in `processors-and-transfers`. Changes in sub-processors MUST be reviewed before they take effect.

#### 06-lawful-bases-and-consents

Before collecting personal data, each purpose MUST have a documented lawful basis (Art. 6), and special category data an Art. 9 condition. Where consent is the basis, the organisation MUST keep a record sufficient to demonstrate it (Art. 7(1)): who, when, what was shown, and what was agreed. The privacy notice MUST be provided at collection (Art. 13-14).

#### 07-data-subject-requests

Requests to exercise rights (Art. 15-22) MUST be answered without undue delay and at the latest within one month of receipt. That period MAY be extended by two further months for complex or numerous requests, and the person MUST be told of the extension and the reasons within the first month (Art. 12(3)). The requester's identity MUST be verified before data is disclosed or erased. Every request and its outcome MUST be recorded.

#### 08-breach-notification

A personal data breach MUST be notified to the supervisory authority without undue delay and, where feasible, within 72 hours of becoming aware of it, unless it is unlikely to result in a risk to people (Art. 33). When the risk is high, the affected people MUST be informed without undue delay (Art. 34). A processor MUST notify the controller without undue delay. Every breach, including unreported ones, MUST be documented with facts, effects and actions taken (Art. 33(5)).

#### 09-storage-limitation-duty

The organisation MUST NOT keep personal data longer than necessary for its purpose (Art. 5(1)(e)) and MUST erase it on a valid request unless an Art. 17(3) exception applies. Technical design is in [agentme-adr-policy-201](../../adrs/data/201-personal-data-retention-and-erasure.md).

#### 10-awareness

People who handle personal data MUST receive data-protection guidance for their role when they join and when the hub policy changes materially.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 5-7, 9, 12-22, 24, 28, 30, 33-35, 37.
