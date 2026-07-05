---
name: agentme-core-adr-policy-001-agentme-core
description: Defines the agentme scope's identity, target audience, distribution model, and writing standards. Use when adding, updating, or reviewing any XDR or skill in the agentme scope.
apply-to: agentme scope contributors, maintainers, and agents processing agentme content
valid-from: 2026-07-05
---

# agentme-core-adr-policy-001: agentme scope identity and content standards

## Context and Problem Statement

The `agentme` scope ships opinionated XDRs and skills to other projects. Without a clear definition of its audience, purpose, and writing conventions, contributors may add content that is too abstract, misses examples, or fails to cover design/implementation/testing in a way that a coding agent or PR review bot can act on.

What is the `agentme` scope's identity, who does it serve, and how must content be written to be useful to those consumers?

## Decision Outcome

**The `agentme` scope targets the software development phase of codebases in any language, and its primary consumers are AI coding agents and automated PR review bots. All content must be pragmatic, example-driven, and structured to cover design, implementation, and testing in coherent, immediately actionable guidance.**

### Details

#### 01-scope-identity

The `agentme` scope is a curated library of engineering XDRs and agent skills encoding best practices for software development. It is distributed to other projects as an npm package preset. The companion `agentme-core` scope that governs authoring conventions MUST NOT be included in any preset or published distribution — it is for internal use only.

#### 02-audience-and-consumers

The primary consumers of `agentme` content are:

1. **AI coding agents** — autonomous or semi-autonomous agents (e.g., VS Code Copilot Agent, custom LangGraph agents) that implement features, refactor code, write tests, or scaffold projects.
2. **PR review bots** — automated reviewers that check whether submitted code follows established standards.
3. **Human developers** — engineers who adopt agentme standards as their own project baseline.

All three consumers operate during the **development phase** of a codebase — from design and initial implementation through testing and code review. They work across multiple languages (JavaScript/TypeScript, Go, Python) without deep project-specific context.

#### 03-content-scope

Content in `agentme` MUST address at least one of the following development-phase concerns:

- Design: structure, architecture, module boundaries, abstraction levels.
- Implementation: concrete coding patterns, idioms, tool usage, naming, error handling.
- Testing: unit testing, integration testing, AI-specific evals, test structure, coverage requirements.

Content that addresses only documentation, deployment, or organizational process does not belong in `agentme` unless it directly enables the development phase (e.g., a CI/CD standard that enforces test gates belongs; a personnel policy does not).

#### 04-pragmatic-approach

Content MUST be immediately actionable. Rules MUST state what to do, not just what to avoid.

Examples SHOULD be used when they make a complex rule significantly clearer. When included, examples MUST:

- Be short and focused on the core idea of the rule — omit boilerplate that does not illustrate the point.
- Use the language or tool most applicable to the rule (pseudo-code is allowed only when the pattern is genuinely language-agnostic).

Do not add examples for rules that are already self-explanatory from their prose alone.

#### 05-cover-design-implementation-and-testing-coherently

A policy that introduces a design pattern (e.g., hexagonal architecture, agent composition) MUST also state how that pattern is implemented and tested. It is not sufficient to define the structure without also stating the testing strategy. Likewise, a testing policy MUST reference the implementation conventions it validates.

Every policy that involves testable behavior MUST define the mocking strategy: whether tests for that concern MUST use mocks, MUST NOT use mocks, or MAY choose — and the reason for that choice. Only leave the mock strategy open if not applicable or the actual implementation strategy is still unknown for the specific case.

When a single document would become too long, a policy MAY delegate to a linked policy or skill for one of the three concerns, but the linking document MUST explicitly point to the delegate and explain the relationship.

#### 06-language-and-tone

Content MUST be:

- Written in plain, direct language. Avoid hedging words like "should consider" or "might want to" for mandatory rules. Use MUST for requirements, SHOULD for strong recommendations, and MAY for options.
- Concise. Each rule MUST state one decision clearly. Split compound decisions into separate rules.
- Free from vendor marketing language, hype, or jargon without definition.

#### 07-conflict-free-across-scope

No policy in `agentme` MAY contradict another policy in `agentme` or `_core` without an explicit "Conflicts" section that names the conflicting policy, explains the conflict, and justifies why the override is intentional.

#### 08-no-project-internal-content

`agentme` MUST NOT contain decisions that describe how to work within the agentme repository itself (contributor workflows, internal conventions, scope placement rules). Those belong in `_local`.

#### 09-distribution-model

The `agentme` scope is published as a preset. Changes to which files are included in a preset are breaking changes. Before adding a new file to a preset, verify it is self-contained, conflict-free, and meets all writing standards in this policy.

## References

- [_core-adr-policy-011 - core scope type](../../../_core/adrs/principles/011-core-scope-type.md)
- [_core-adr-policy-010 - Scope governance](../../../_core/adrs/principles/010-scope-governance.md)
- [_core-adr-policy-002 - Policy standards](../../../_core/adrs/principles/002-policy-standards.md)
