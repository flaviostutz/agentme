---
name: _core-bdr-001-xdr-decisions-and-skills-usage
description: Defines how agents and humans must use XDR decisions and skills, separating policy authority from execution guidance across single-agent and multi-agent workflows.
---

# _core-bdr-001: XDR decisions and skills usage

## Context and Problem Statement

Repositories using the XDR framework contain both decision records (BDRs, ADRs, EDRs) and skills. In multi-agent or multi-role workflows, each actor needs to know which artifact carries policy authority and which carries execution guidance.

Question: How must agents and humans use XDR decisions and skills so policy, execution guidance, and role boundaries stay clear?

## Decision Outcome

**BDRs define compliance policy; skills operationalize it**

XDR decisions are the authoritative source of mandatory policy. Skills are execution artifacts that operationalize those decisions and must never substitute them as policy authority.

### Details

- Before treating any XDR as a current requirement, evaluate applicability in order: `validFrom`, `applyTo`, then the decision text.
- The set of policies that an agent or human must comply with for a given operational context must be declared in BDRs.
- If a policy set becomes too large or too mixed in purpose to review clearly in one record, it must be split into multiple focused BDRs.
- Specific work instructions that operationalize BDR policies must be structured as skills when the procedure is detailed enough to benefit from a dedicated operational document.
- Every skill that operationalizes or verifies BDR policies must link to the BDRs it implements or checks.
- If a skill conflicts with an applicable XDR, the XDR prevails. The human or agent must stop relying on the conflicting skill behavior and report the inconsistency.
- If an applicable BDR exists but no supporting skill exists yet, the human or agent may proceed by following the BDR directly when the decision is actionable, and must report the missing skill as an operational gap.
- In multi-agent graphs or staged workflows, every participating agent must remain bounded by the same applicable BDR policies even when agents have different local objectives, prompts, or skills.
- Each agent or human role involved in a workflow must make explicit which applicable BDRs govern its work and which skills it is following.
- Different documents may be consumed by different actors. For example: one agent uses skills for data acquisition, another for plan execution, and a reviewer reads BDRs directly to validate outcomes.

Allowed:
- using multiple skills to operationalize one BDR in different phases of a workflow;
- using one skill to operationalize multiple related BDRs when the skill links them clearly;
- having human-only, agent-only, or mixed human-agent execution for the same skill.

Disallowed:
- treating a skill as policy authority by itself;
- inventing mandatory policy rules only inside prompts, plans, or skills;
- allowing one agent in a workflow to bypass an applicable BDR because another agent checked a different subset of rules.

## Considered Options

- (REJECTED) **Keep policy and execution guidance mixed inside operational BDRs** — Makes decisions harder to reuse, review, and assign across humans and multiple agent roles.
- (CHOSEN) **Separate mandatory policy in BDRs from executable guidance in skills** — Preserves a clear source of truth while allowing different humans and agents to execute specialized procedures.

## References

- [_core-adr-001](../../adrs/principles/001-xdrs-core.md)
- [_core-adr-002](../../adrs/principles/002-xdr-standards.md)
- [_core-adr-003](../../adrs/principles/003-skill-standards.md)
