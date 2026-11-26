---
name: agentme-edr-policy-408-gdpr-runbooks
description: Defines the required content of GDPR data subject request and personal data breach runbooks, as checklists, and the drill evidence expected. Use when writing, reviewing or auditing a runbook that a hub policy points to.
apply-to: Runbooks pointed to by the dsr-and-breach-runbooks item of hub policies (agentme-adr-policy-501)
valid-from: 2026-11-23
---

# agentme-edr-policy-408: GDPR runbooks

## Context and Problem Statement

Runbooks exist on paper but often miss steps needed to meet GDPR deadlines: how to verify identity, which systems to search, who notifies the authority and with what content.

Question: What must a data subject request runbook and a breach runbook contain to be considered adequate?

## Decision Outcome

**Each runbook MUST contain every item of its checklist below, name its owner and last drill, and live at the location declared in the hub policy**

Workflow roles and time targets are defined in [agentme-bdr-policy-406](../../bdrs/operations/406-gdpr-request-and-breach-workflow.md); deadlines in [agentme-bdr-policy-501](../../bdrs/governance/501-gdpr-organisational-obligations.md). These are checklists of required content, not templates. Nothing here is legal advice.

### Details

#### 01-common-requirements

Every runbook MUST state: owner, contact for the privacy contact or DPO, date of last review (within 12 months), date and result of last drill, the register where cases are recorded, and links to the systems inventory. A runbook that is an empty file or a title only MUST be reported as inadequate.

#### 02-data-subject-request-checklist

The request runbook MUST cover:

- Channels where requests can arrive (form, email, support, social, post) and how each reaches the register.
- Request types: access, portability, rectification, erasure, restriction, objection, withdrawal of consent, and automated-decision contest.
- Identity verification method and when to ask for more proof.
- Deadline calculation (one month from receipt), the extension rule and the extension notice.
- Where to search: the list of every store, processor and backup, taken from the architecture inventory.
- How to execute each request type per store, and exceptions where erasure may be refused with the reason to give.
- Response content, delivery channel and the right to complain to the authority.
- Handling of requests made on behalf of others, of children, and of excessive or repeated requests.

#### 03-breach-checklist

The breach runbook MUST cover:

- Definition of a breach with examples (loss, unauthorised access, ransomware, misdirected data).
- How anyone reports a suspicion and to whom, around the clock.
- Containment and evidence preservation steps.
- Assessment of categories and number of people and records, and of the risk to people.
- Decision tree for authority notification within 72 hours and for informing people when risk is high, with who decides.
- Content of the authority notification (nature, categories and approximate numbers, contact, consequences, measures) and the contact for the competent authority.
- Obligations when acting as processor: notify the controller without undue delay.
- Documentation of every breach, including those not notified, and the post-incident review.

#### 04-drill-evidence

Each runbook MUST be backed by drill evidence from the last 12 months with scenario, participants, time to complete and gaps found, per [agentme-bdr-policy-406](../../bdrs/operations/406-gdpr-request-and-breach-workflow.md) rule 06.

#### 05-location

The runbook location MUST be in the `dsr-and-breach-runbooks` hub item of [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md). External locations (wiki, ticketing) are allowed when reachable by the on-call team; the audit marks unverifiable ones as warnings.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 12, 15-22, 33-34.
