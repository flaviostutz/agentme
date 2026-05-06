# agentme-article-001: Continuous XDR improvement

## Overview

This article explains how architects, engineers and business professionals should recognize, organize, and promote reusable delivery decisions into XDRs as a continuous improvement activity. It is aimed at people working with coding agents, vibe-coding loops, or SDD-oriented delivery who need a practical path from task friction to shared documentation.

Continuous improvement matters because delivery decisions do not stay correct forever. Team structures change, platforms evolve, tools mature, and the trade-offs behind earlier choices shift over time. If XDRs are not revisited and improved continuously, previously useful decisions become stale guidance and eventually turn into a form of legacy documentation that misleads delivery instead of guiding it.

Continuous improvement also keeps the target state explicit. As XDRs evolve across projects and tracks, teams need a clear shared view of where they are trying to converge, what remains intentionally different, and what should be treated as technical debt on the path toward that target. Keeping XDRs current reduces confusion about the desired future state and helps each project evolve toward it deliberately instead of drifting through ad hoc local decisions.

## Content

### Start from delivery friction

The trigger for a new XDR is usually undocumented work that creates friction. That friction often appears when a feature needs repeated clarification about a business flow, integration pattern, code organization rule, or tool choice before the agent can produce acceptable code.

Common signals:

- The coding agent needs the same steering more than once.
- Reviews keep repeating the same correction or design preference.
- A flow depends on rules that are stable beyond one feature.
- A team solved a delivery problem in a way that other teams could reuse.

### What is an XDR?

An XDR is a short decision record that captures a reusable choice and the reason for it. XDRs can be architectural (ADR), business (BDR), or engineering (EDR). They are the durable source of truth; prompts, review comments, and specs are not.

### Decide whether it should become an XDR

Write or propose an XDR when a task depends on a decision that will likely be reused beyond one feature or repository. Common triggers are repeated prompt explanations, recurring review comments, and cases where an agent needed heavy steering on a framework, coding standard, tool, architecture pattern, or business flow.

Keep genuinely application-specific details in `_local`. Shared XDRs should capture decisions that help more than one team, product area, or recurring workflow.

Before drafting, reduce the issue to one reusable decision:

1. Name the friction clearly.
2. Identify the decision behind it.
3. Decide whether it is shared or local.
4. Choose the right XDR type and subject.
5. Capture only durable guidance, not ticket-specific detail.

### How do you initiate the discussion?

Start with the decision gap, not the preferred answer. Explain what slowed the work down, what had to be clarified manually, and who else would benefit from the guidance. If useful, ask the coding agent which missing XDRs made the task harder or caused extra vibe coding rounds.

Good opening questions:

- Which reusable decision was missing during this feature?
- Should this live in a shared scope or stay local to one repository?
- What trade-off are we trying to standardize?

### How should you organize the XDR?

Follow the XDR template from [_core-adr-002](../../../../_core/adrs/principles/002-xdr-standards.md). Keep the document small, explicit, and decision-focused.

Use this checklist:

1. Choose the right type: ADR for architecture, BDR for business, EDR for engineering practice.
2. Choose the broadest safe scope; use `_local` only for repository-specific decisions.
3. Pick the subject folder that best matches the topic.
4. Write the context as a problem statement ending with a clear question.
5. State one chosen outcome and the concrete implementation details.
6. Add considered options only when the alternatives matter.
7. Link to related XDRs, skills, and discussions instead of duplicating long instructions.

### Promote it into shared documentation

Once the decision is organized, move it from local discussion into a proposal that can be reviewed and published.

The practical workflow is:

1. Notice the gap during development, review, or specification.
2. Check existing XDRs first to avoid duplicates or conflicts.
3. Decide whether the guidance is shared or truly local.
4. Draft a concise XDR proposal with the standard template.
5. Ask the leaders responsible for that scope to review, adjust, and publish it.
6. Update the relevant index and any related skills or articles.
7. On later reviews, check whether big decisions are now covered well enough to keep the team near the 80% target.

### How does this fit coding agents, vibe coding, and SDD?

Coding agents are effective when durable guardrails already exist. Vibe-coding loops are useful for exploration, but if the same correction keeps being typed, the team is paying a documentation debt. SDD should keep feature-specific intent and acceptance criteria, while XDRs should hold reusable rules that must survive across features.

### Practical rule of thumb

If the same clarification would likely be needed in another feature, by another team, or by another agent, it is a good XDR candidate. Move it into an XDR when the guidance is reusable, stable enough to standardize, and broad enough to help future delivery.

## References

- [_core-adr-001](../../../../_core/adrs/principles/001-xdrs-core.md) - XDR structure, numbering, and mandatory template
- [_core-article-001](../../../../_core/adrs/principles/articles/001-xdrs-overview.md) - XDR introduction and general adoption guidance
- [agentme-edr-012](../012-continuous-xdr-enrichment.md) - Shared-first XDR enrichment policy and 80% coverage target
- [002-write-xdr skill](../../../../../.github/skills/002-write-xdr/SKILL.md) - Step-by-step procedure for drafting new XDRs
