---
name: agentme-bdr-policy-005-xdrs-as-the-single-source-of-truth
description: Defines XDRS as the single, human-readable source of truth about a business or software solution, written from the first brainstorm and evolved through every lifecycle phase. Use when deciding where to document anything about a solution, or when starting to explore an idea.
apply-to: All business application and application service scopes, from the first brainstorm to retirement
valid-from: 2026-11-26
---

# agentme-bdr-policy-005: XDRS as the single source of truth

## Context and Problem Statement

Knowledge about a solution is spread across slides, tickets, wikis, chats and code. Agents and auditors cannot find a complete, trustworthy context, and policies that could be checked automatically stay prose in documents nobody reads.

Question: How should XDRS be used during the whole lifecycle so that they hold everything about a solution except its codebase?

## Decision Outcome

**XDRS are the single source of information about a solution, written from the first brainstorm as if final and evolved in every phase, readable by humans and auditors and usable by agents and automated checks**

### Details

#### 01-single-source

Everything about a business or solution MUST be registered in XDRS: business requirements and policies, usability and data requirements, architecture, security and control requirements, platform and coding standards, skills that automate development and operation steps, runbooks, research and prototypes. The codebase itself and generated evidence (test reports, logs, scan results) are not XDRS content. Where each kind goes is defined in `agentme-bdr-416`.

#### 02-written-from-the-start

The scope MUST be created at the first brainstorm (`agentme-bdr-415`). Ideas, hypotheses and decisions MUST be written as research, initiative or policy documents while they are discussed, and not afterwards.

#### 03-policies-as-if-final

Policies MUST be written as if the decision were already taken and valid. A policy MUST NOT carry status marks such as draft or proposed. When the idea changes, the policy MUST be edited or deleted. When changes are large, a full refactor of the affected policies MUST be proposed to the owner of the scope instead of accumulating contradictions.

#### 04-evolve-with-phases

Each phase of `agentme-bdr-004` creates or updates XDRS and each exit gate checks that they are consistent with the work done. A decision taken outside XDRS, such as in a meeting or a ticket, MUST be written back before the phase exit.

#### 05-readable-and-checkable

Documents MUST be readable by business, risk, governance and audit people and MUST use structured rules so that agents and automated checks can use them (`agentme-edr-019`). Documents SHOULD state requirements as testable rules instead of narrative.

#### 06-agents-use-the-context

Agents MUST load the full XDRS context of the scope, including the extended scopes and their skills, before investigating features, testing hypotheses, prototyping or implementing (`agentme-edr-019`). Agents MUST NOT take approval decisions (`agentme-bdr-503`).

#### 07-no-sensitive-content

XDRS MUST NOT contain secrets, personal data, exploitable vulnerability details or confidential evidence content. They MAY cite external identifiers of evidence kept in the record system (`agentme-bdr-503`).

## References

- [`agentme-bdr-004`](004-business-and-software-lifecycle.md) - Lifecycle phases
- [`agentme-bdr-415`](../operations/415-solution-scope-lifecycle.md) - Solution scope lifecycle
- [`agentme-bdr-416`](../operations/416-solution-content-map.md) - Solution content map
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Gate approvals and evidence records
- [`agentme-edr-019`](../../edrs/principles/019-policies-as-automated-checks-and-agent-context.md) - Policies as automated checks and agent context
- [`agentme-edr-012`](../../edrs/principles/012-continuous-xdr-enrichment.md) - Continuous XDR enrichment
