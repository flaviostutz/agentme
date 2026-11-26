---
name: agentme-bdr-policy-406-gdpr-request-and-breach-workflow
description: Defines the organisational workflow, roles, RACI, escalation and drill cadence for GDPR data subject requests and personal data breaches. Use when assigning responsibilities or reviewing whether the organisation can meet request and breach deadlines.
apply-to: Organisations operating applications whose hub policy (agentme-adr-policy-501) declares GDPR as applicable
valid-from: 2026-11-23
---

# agentme-bdr-policy-406: GDPR request and breach workflow

## Context and Problem Statement

Legal deadlines for data subject requests (one month) and breach notifications (72 hours) are missed when nobody knows who does what. Obligations are in [agentme-bdr-policy-501](../governance/501-gdpr-organisational-obligations.md); a workflow is needed to meet them.

Question: Who does what, in which order and by when, when a request or breach arrives?

## Decision Outcome

**One written workflow with named roles, a RACI and internal time targets MUST exist for data subject requests and for breaches, and be rehearsed at least yearly**

Runbook content requirements are in [agentme-edr-policy-408](../../edrs/operations/408-gdpr-runbooks.md); the location is declared in the `dsr-and-breach-runbooks` hub item of [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md). Nothing here is legal advice.

### Details

#### 01-roles

The workflow MUST name these roles (one person may hold several; map to team roles in [agentme-bdr-404](404-team-roles-and-specialists.md)):

- **Application owner**: accountable for the outcome.
- **Privacy contact or DPO**: assesses, advises, talks to the authority and data subjects.
- **Engineering lead**: finds, exports, corrects or erases data.
- **Security lead**: leads breach containment and investigation.
- **Legal**: confirms obligations, exceptions and notification duty.
- **Communications**: drafts messages to affected people when needed.

#### 02-raci

Every step MUST have exactly one Accountable (A) owner, and the table MUST be kept in the runbook with named people or roles for each letter.

| Step | Owner | Privacy/DPO | Engineering | Security | Legal | Comms |
|---|---|---|---|---|---|---|
| Intake and logging of request | A | R | I | - | - | - |
| Identity verification | A | R | C | - | - | - |
| Locate and act on data | A | C | R | - | C | - |
| Review and respond to requester | A | R | C | - | C | - |
| Breach triage and containment | A | C | R | R | I | - |
| Notify authority | A | R | C | C | C | - |
| Notify affected people | A | R | C | C | C | R |
| Post-incident review | A | R | R | R | C | I |

R = does the work, A = accountable, C = consulted, I = informed.

#### 03-internal-time-targets

Requests: log within 2 working days, acknowledge the requester within 5, and complete well before the one-month limit, leaving at least 5 days for review. Breaches: the privacy contact MUST be notified within 4 hours of anyone suspecting a breach, triage MUST finish within 24 hours of awareness, and the notification decision MUST be taken with at least 24 hours left of the 72. The clock starts when the organisation becomes aware, not when the investigation ends.

#### 04-escalation

A request that cannot meet its deadline MUST be escalated to the owner by half the period, and the extension notice of Art. 12(3) MUST be sent within the first month. A breach with likely high risk MUST be escalated to the owner and legal at once.

#### 05-records

Requests and breaches MUST be kept in a register with dates, decisions, who acted and outcomes. The register MUST NOT hold more personal data than needed to evidence the handling.

#### 06-drills

The organisation MUST rehearse one request scenario and one breach scenario at least once a year, and after any change of roles, processors or the workflow. Drill evidence (date, scenario, time to complete, gaps and fixes) MUST be retained.

## References

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj), Art. 12, 15-22, 33-34.
