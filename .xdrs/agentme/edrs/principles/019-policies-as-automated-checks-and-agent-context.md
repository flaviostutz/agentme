---
name: agentme-edr-policy-019-policies-as-checks-and-agent-context
description: Defines how XDRS policies of a solution scope are written as structured rules and used by agents as full context and as automated checks at any lifecycle phase. Use when writing policies meant for automated checks, preparing agent context, or running reviews at phase gates.
apply-to: Every business application and application service scope, and every agent working on them
valid-from: 2026-11-26
---

# agentme-edr-policy-019: Policies as checks and agent context

## Context and Problem Statement

Policies written as narrative cannot be checked, and agents that load only part of the scope miss inherited rules and skills. The value of a complete XDRS set is lost when it is not used as context for investigating features and as a source of checks at each phase.

Question: How should policies be written and loaded so agents and automated checks can use them at any moment of the lifecycle?

## Decision Outcome

**Write policies as structured, testable rule blocks, load the whole extends chain as context, and run existing XDRS skills at the phase gates**

### Details

#### 01-structured-rule-blocks

Policies that are meant to be checked MUST use the numbered rule blocks of `_core-adr-policy-008`, with normative keywords (MUST, SHOULD) and testable statements. Requirements SHOULD name the artifact, the condition and the expected result.

#### 02-load-the-whole-chain

Before working on a scope, agents MUST load the policies and the skills of the scope and of every scope in its extends chain (`agentme-adr-001` rule 04). The `select-relevant-xdrs` skill SHOULD be used to select the policies relevant to the task.

#### 03-checks-at-gates

Before each phase exit gate of `agentme-bdr-004`, the changed documents and artifacts MUST be reviewed against the applicable policies with the `review` skill, and the findings MUST be fixed or registered as exceptions per `agentme-bdr-502`. A review result is evidence for the gate and MUST NOT replace the human approval (`agentme-bdr-503`).

#### 04-skills-for-evidence

Steps that repeat in several changes, such as evidence generation, control checks and runbook steps, SHOULD be implemented as skills of the scope, with their own tests per `agentme-edr-017`. Skills MUST NOT write sensitive content in XDRS (`agentme-bdr-005` rule 07).

#### 05-new-knowledge-back-to-xdrs

Rules, decisions or exceptions discovered while investigating or implementing MUST be written back to the scope, following `agentme-edr-012`.

## References

- [`agentme-bdr-004`](../../bdrs/principles/004-business-and-software-lifecycle.md) - Lifecycle phases and gates
- [`agentme-bdr-005`](../../bdrs/principles/005-xdrs-single-source-of-truth.md) - XDRS as the single source of truth
- [`agentme-bdr-502`](../../bdrs/governance/502-control-framework-and-standards-setters.md) - Exceptions
- [`agentme-bdr-503`](../../bdrs/governance/503-lifecycle-gate-approvals.md) - Gate approvals
- [`agentme-adr-001`](../../adrs/principles/001-business-application-and-application-service-scopes.md) - Scope model and extends chain
- [`agentme-edr-012`](012-continuous-xdr-enrichment.md) - Continuous XDR enrichment
- [`agentme-edr-017`](017-skill-testing.md) - Skill testing
- [`_core-adr-policy-008`](../../../_core/adrs/principles/008-policy-structured-standards.md) - Structured rule blocks
