---
name: agentme-edr-policy-012-continuous-xdr-improvement-policy
description: Defines how teams should promote reusable implementation guidance into shared XDRs instead of keeping it in prompts or local habits. Use when recurring decisions surface during delivery.
apply-to: All projects using XDR framework
valid-from: 2026-05-25
---

# agentme-edr-policy-012: Continuous xdr improvement policy

## Context and Problem Statement

Teams using AI agents, vibe coding, and SDD often keep important implementation guidance only in prompts, review comments, or local habits. This slows delivery, fragments practices across teams, and forces repeated clarification.

Question: What policy should developers follow to continuously enrich XDRs so reusable engineering decisions are shared instead of remaining implicit?

## Decision Outcome

**Develop features with shared-first XDR enrichment and controlled divergence**

Developers MUST treat reusable missing guidance discovered during implementation as an XDR gap to be proposed and reviewed, not as permanent prompt-only context or repeated vibe coding.

### Details

#### 01-reusable-guidance-must-become-shared-xdr

Developers MUST treat reusable missing guidance discovered during implementation as an XDR gap to be proposed and reviewed, not as permanent prompt-only context or repeated vibe coding. The main objective is sharing, discussing, and converging practices across teams. Controlled divergence during exploration is acceptable, but recurring successful decisions MUST be converged into shared XDRs.

#### 02-local-scope-must-be-for-truly-specific-decisions

Decisions placed in `_local` SHOULD be truly specific to the needs of a single application or repository. The non-`_local` scope exists to share practices across projects, company areas, and functionally organized teams.

#### 03-steering-needs-must-trigger-xdr-reflection

When developers or coding agents need too much detailed steering to complete a task, they MUST reflect on whether those details would help other teams or future implementations. If yes, create or update an XDR proposal in the broadest appropriate shared scope. This includes cases where an agent implemented a feature without a framework, pattern, coding standard, or other practice that should likely be standardized. Missing reusable guardrails SHOULD trigger an XDR proposal.

#### 04-coverage-target-should-be-80-percent

Teams SHOULD aim to keep at least 80% of big coding decisions covered by accepted XDRs. Big decisions include framework or tool selection, overall code organization, monorepo structure, complex business flows, and coding standards. If a big decision is not yet covered, developers SHOULD either propose a new XDR or document why the decision is intentionally local and should not be shared.

#### 05-leaders-must-review-xdr-proposals

Leaders responsible for the affected scope are accountable for reviewing XDR proposals, adjusting them, and publishing the accepted decision.

#### 06-query-agents-for-missing-xdrs

It is good practice to ask the coding agent which missing XDRs made the task harder, increased adjustment rounds, or forced more vibe coding. Those gaps SHOULD feed the XDR backlog.

#### 07-xdrs-are-not-feature-specs

In SDD, specifications describe the feature being built; XDRs describe reusable decisions and guardrails that MUST survive beyond one feature. Do not keep durable engineering policy only inside feature specs.

## Considered Options

* (REJECTED) **Force all decisions into local scopes first** - Safer for a single repository but weak for reuse.
  * Reason: It overuses `_local`, reduces cross-team discussion, and turns shared practices into isolated variants.
* (CHOSEN) **Promote reusable development guidance into shared XDRs while keeping truly specific decisions local** - Balance exploration with convergence.
  * Reason: It preserves local autonomy for application-specific needs while making reusable practices discussable, reviewable, and distributable.

## References

- [_core-adr-001](../../../_core/adrs/principles/001-xdrs-core.md)
- [_core-article-001](../../../_core/adrs/principles/articles/001-xdrs-overview.md)
- [agentme-article-001](articles/001-continuous-xdr-improvement.md)
- [002-write-policy skill](../../../_core/adrs/principles/skills/002-write-policy/SKILL.md)
