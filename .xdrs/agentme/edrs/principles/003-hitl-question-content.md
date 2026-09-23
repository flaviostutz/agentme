---
name: agentme-edr-policy-003-hitl-question-content
description: >
  Defines the mandatory content of every question an AI agent asks a human (clarifying, decision,
  approval, or phase-gate question): location, finding, why it is a doubt, options with
  consequences, and a recommended option. Use when writing skills with human-in-the-loop (HITL)
  questions, or whenever an agent asks a human to decide something.
apply-to: Any AI agent question to a human (clarifying, decision, approval, or phase gate), inside or outside skills, in agentme and scopes that follow or extend it.
valid-from: 2026-09-23
---

# agentme-edr-policy-003: HITL question content

## Context and Problem Statement

Agents often ask humans short questions such as "Choose which option? A or B?". Without the surrounding context, the human cannot evaluate the trade-off and either guesses or has to investigate alone.

Question: What must every agent question to a human contain so the human can decide without further investigation?

## Decision Outcome

**Self-contained decision questions**

Every question MUST carry the location, the finding, why the agent cannot resolve it alone, every option with its consequences, and a recommended option with a reason. Long context goes in a chat message right before the question UI.

### Details

A HITL question is any point where an agent pauses and asks a human for input: clarifying questions, choices between options, approvals of writes or destructive actions, and phase-gate confirmations. Pure information requests with no decision weight (e.g. "What is the repository URL?") MAY omit rules 03 and 04.

#### 01-context-must-precede-every-question

Before asking, the agent MUST state where the issue is (file, section, line, artifact, or system, as a link when possible), what was found, and the relevant current state. A question MUST NOT consist of a short title and option labels only.

#### 02-doubt-must-be-explained

The agent MUST state why it cannot resolve the point itself: conflicting sources, missing information, a subjective or domain trade-off, or a risk that requires human accountability.

#### 03-each-option-must-state-consequences

Every option MUST state what it does and its consequences: benefit, cost or risk, relative effort, reversibility, and anything it postpones to the future. Options MUST be distinguishable by their consequences, not only by their labels.

#### 04-one-option-should-be-recommended-with-reason

When one option is preferable, the agent SHOULD mark it as recommended with a one-line reason. The human MUST still make the decision; a recommendation MUST NOT be applied without the human's answer.

#### 05-questions-must-be-self-contained

The human MUST be able to decide from the question text alone, without scrolling back to earlier rounds or opening files. Terms not defined earlier in the same message MUST be explained in plain words. When several questions are batched, each MUST be numbered (Q1, Q2, ...) and carry its own context, doubt, and options.

#### 06-length-limited-ui-fields-must-reference-chat-context

When the question UI limits field length (e.g. `vscode_askQuestions` rejects fields over about 200 characters), the agent MUST place the full context from rules 01-03 in a chat message immediately before the UI call. The UI question MUST stay short and reference that message by number (e.g. "Q1 (see above): ..."), and option labels SHOULD be a letter plus a short gist.

#### 07-phase-gates-must-summarize-outcome

A phase-gate question (continue, re-run, add a comment) MUST summarize what the phase produced, any open risks or deferred items, and what each gate option will cause next.

#### 08-requests-for-more-context-must-be-re-explained

When the human answers with a request for clarification (e.g. "explain better") instead of choosing, the agent MUST re-ask the same question with expanded context, such as concrete file references, examples, or impact, and MUST NOT repeat the original wording.

#### 09-write-confirmations-extend-adapter-rules

Approval questions for external-system writes MUST follow [`agentme-edr-policy-127-external-system-adapter-skills.04-human-in-the-loop-before-mutations`](../application/127-external-system-adapter-skills.md#04-human-in-the-loop-before-mutations) and MUST also apply rules 02-04 of this policy.

#### 10-skills-must-embed-and-test-the-checklist

A skill with HITL questions MUST embed rules 01-08 as a checklist in its instructions. Its `SKILL.test.md` (per [`agentme-edr-017`](017-skill-testing.md)) MUST contain at least one assertion verifying that a decision question includes location, doubt, option consequences, and a recommendation.

### Example

Disallowed:

> Choose which option? A or B?

Allowed:

> In `xyz.md` section "Auth", concept X says tokens expire hourly, while concept Y says sessions never expire. Both cannot hold, and the file does not say which is authoritative, so this is a product decision.
> - A: Align both with concept W (expiring sessions refreshed by tokens). Fixes X and Y permanently; more complex to implement.
> - B: Remove X and Y entirely. Simpler now; postpones the session-lifetime issue to the future.
>
> Recommended: A, because B only defers the conflict.

## References

- [`agentme-edr-017`](017-skill-testing.md) - Skill testing
- [`agentme-edr-127`](../application/127-external-system-adapter-skills.md) - External system adapter skills
