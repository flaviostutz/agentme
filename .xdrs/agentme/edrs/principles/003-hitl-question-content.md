---
name: agentme-edr-policy-003-hitl-question-content
description: >
  Defines the mandatory format of every question an AI agent asks a human (clarifying, decision,
  approval, or phase-gate question): a short title with context, 2-4 options with consequences,
  a "(recommended)" prefix on the preferred option, word caps, and question-UI fields filled with
  as much of the question as fits. Use when writing skills with human-in-the-loop (HITL)
  questions, or whenever an agent asks a human to decide something.
apply-to: Any AI agent question to a human (clarifying, decision, approval, or phase gate), inside or outside skills, in agentme and scopes that follow or extend it.
valid-from: 2026-09-23
---

# agentme-edr-policy-003: HITL question content

## Context and Problem Statement

Agents often ask humans short questions such as "Choose which option? A or B?". Without the surrounding context, the human cannot evaluate the trade-off and either guesses or has to investigate alone. Overlong questions get skimmed.

Question: What must every agent question to a human contain so the human can decide quickly without further investigation?

## Decision Outcome

**Compact, self-contained decision questions**

Every question MUST follow a compact template: a short title with one line of context, 2-4 options stating their consequences, and a "(recommended)" prefix on the preferred option.

### Details

A HITL question is any point where an agent pauses and asks a human for input: clarifying questions, choices between options, approvals of writes or destructive actions, and phase-gate confirmations. Pure information requests with no decision weight (e.g. "What is the repository URL?") MAY omit options and the recommendation.

#### 01-context-must-precede-every-question

Right after its title, every question MUST give a context line stating what was found and the relevant current state. A question MUST NOT consist of a title and option labels only. The context MAY link the file, section, or system involved and MAY say why the agent cannot resolve the point alone, within the caps of rule 11.

#### 03-each-option-must-state-consequences

Every option MUST state what it does and its most decision-relevant consequences, chosen from: benefit, cost or risk, relative effort, reversibility, and anything it postpones. Options MUST be distinguishable by their consequences, not only by their labels.

#### 05-questions-must-be-self-contained

The human MUST be able to decide from the question text alone, without scrolling back to earlier rounds or opening files. Terms not defined earlier in the same message MUST be explained in plain words. When several questions are batched, each MUST be numbered (Q1, Q2, ...) and carry its own context and options, and a single round MUST NOT exceed 5 questions.

#### 06-ui-fields-must-carry-maximum-question-content

When asking through a question UI with separate fields (e.g. `vscode_askQuestions`), the agent MUST map each part to its own field: "Q<n> <topic>" to the header, the title to the question, the context to the message, each option with its "(recommended)" prefix to an option label, and that option's consequences to the option description. The agent SHOULD also set the UI's recommended flag on that option when one exists.

The agent MUST fill every field with as much decision-relevant content as fits its length limit (about 200 characters for `vscode_askQuestions`, 50 for its header), condensing wording first and truncating with "..." only as a last resort. When any part was condensed or truncated, the agent MUST also place the full question in a chat message immediately before the UI call and MAY append "(full text above)" to the UI question. The agent MUST NOT reduce the UI to a bare reference such as "Q1 (see above)" or to option labels without consequences.

#### 07-phase-gates-must-summarize-outcome

A phase-gate question (continue, re-run, add a comment) MUST summarize what the phase produced, any open risks or deferred items, and what each gate option will cause next. The summary SHOULD stay under 80 words or 5 bullets.

#### 08-requests-for-more-context-must-be-re-explained

When the human answers with a request for clarification (e.g. "explain better") instead of choosing, the agent MUST re-ask the same question with expanded context, such as concrete file references, examples, or impact, and MUST NOT repeat the original wording. The re-asked question MAY use up to twice the caps of rule 11.

#### 09-write-confirmations-extend-adapter-rules

Approval questions for external-system writes MUST follow [`agentme-edr-policy-127-external-system-adapter-skills.04-human-in-the-loop-before-mutations`](../application/127-external-system-adapter-skills.md#04-human-in-the-loop-before-mutations) and MUST also apply rules 03, 06, and 11 of this policy.

#### 10-skills-must-embed-and-test-the-checklist

A skill with HITL questions MUST embed rules 01, 03, 05-08, and 11 as a checklist in its instructions. Its `SKILL.test.md` (per [`agentme-edr-017`](017-skill-testing.md)) MUST contain at least one assertion verifying that a decision question has a context line, option consequences, and a "(recommended)" prefix, and at least one assertion verifying that question-UI fields carry that content per rule 06.

#### 11-questions-must-follow-compact-template

Every decision question MUST use the template below and MUST stay under 140 words in total (title, context, and all options):

```text
Q<n>: <title>
<context>
- A: (recommended) <option>. <consequences>.
- B: <option>. <consequences>.
```

Each part SHOULD respect its cap:

| Part | Cap |
|---|---|
| Title | under 15 words |
| Context | under 25 words |
| Options | 2-4 per question |
| Each option, with its consequences | under 25 words |

When one option is preferable, the agent SHOULD prefix it with "(recommended)" right after its letter; a separate recommendation line or reason is not needed. The human MUST still make the decision; a recommendation MUST NOT be applied without the human's answer.

### Example

Disallowed:

> Choose which option? A or B?

Allowed:

> **Q1: How long should a login session last?**
> `userstory-004.md` AC3 says sessions last 30 days, but `auth-spec.md` section 2.1 limits tokens to 24h with MFA.
> - A: 30 days, update the spec. Better UX; weakens MFA; needs security sign-off.
> - B: 24h limit, change AC3. Keeps security; users log in daily.
> - C: (recommended) 30 days on trusted devices only. Keeps MFA; about 3 extra days of work.

The same question in `vscode_askQuestions` fields (rule 06). Every part fits, so no chat copy is needed:

| Field | Content |
|---|---|
| header | Q1 session length |
| question | Q1: How long should a login session last? |
| message | `userstory-004.md` AC3 says sessions last 30 days, but `auth-spec.md` section 2.1 limits tokens to 24h with MFA. |
| option A label / description | A: 30 days, update the spec / Better UX; weakens MFA; needs security sign-off |
| option B label / description | B: 24h limit, change AC3 / Keeps security; users log in daily |
| option C label / description | C: (recommended) 30 days on trusted devices only / Keeps MFA; about 3 extra days of work |

## References

- [`agentme-edr-017`](017-skill-testing.md) - Skill testing
- [`agentme-edr-127`](../application/127-external-system-adapter-skills.md) - External system adapter skills
