---
name: 151-write-user-story
description: 'Write, refine, elaborate, study or develop the contents of a user story used to create a unit of work for an agile team. Use when you need to write, refine, clarify requirements, ask follow-up questions, cover edge cases, and split large requests into vertical slices so they are clear, complete, and ready for implementation.'
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Turns a vague request or rough draft into an implementation-ready user story by asking targeted follow-up questions, resolving all ambiguities, and producing a thin vertical slice or a clean set of split slices.

Activate when:
- The request is vague, incomplete, or internally inconsistent.
- The acceptance criteria are missing or too shallow.
- The change may affect multiple parts of a system and needs a vertical-slice check.
- A requirement needs to be refined into a clear, testable story.

## Instructions

### Core Rules

- Start from the user input that exists today. Do not assume missing details are acceptable.
- Ask targeted follow-up questions until no material ambiguity remains.
- **HARD GATE: Do not output any story or acceptance criteria while any open decision, unresolved assumption, or ambiguous rule exists — even if the input looks detailed. Embedding an unresolved decision in the output (e.g. "rule X or Y — to be decided") is forbidden; resolve it through questions first.**
- A detailed or well-structured input does NOT exempt you from the question loop. Treat apparent completeness as a signal to look harder for hidden ambiguities.
- Analyze all affected parts of the system together before deciding whether the story is small enough.
- If the request is too large, output only the split implementation-ready stories.
- Split by independently valuable end-to-end slices, not by technical layers.
- Produce exactly one recommended result: one final story when feasible, otherwise the final split stories.

### Steps

1. **Classify the input.**
   Decide whether the input is a vague request, partial draft, or near-complete story. Restate the current understanding in a few lines before asking questions.

2. **Identify missing information.** Focus on missing or contradictory items first.

   | Area | Questions to resolve |
   |---|---|
   | Problem and value | What problem is being solved? Who benefits? What user or business value should exist after the change? |
   | Scope | What behavior is explicitly in scope? What is explicitly out of scope? What should remain unchanged? |
   | Requirements | What must the system do? What inputs, outputs, or contracts matter? What constraints shape the solution? |
   | Flow and interactions | What is the main end-to-end flow? Which actors, systems, or interfaces are involved? Are there state transitions or lifecycle rules? |
   | Edge cases | What unusual but valid scenarios must work? What invalid inputs or error paths must be handled? What happens on retries, duplicates, partial failure, or missing data? |
   | Dependencies | What upstream or downstream systems affect the change? Are there required approvals, sequencing, or external decisions? Does any migration, rollout, or compatibility concern exist? |

3. **Ask follow-up questions one by one using interactive inputs.**
   - **Always use the `vscode_askQuestions` tool** to ask questions interactively when it is available. Never dump questions as plain text if the tool is available.
   - Ask **one question at a time** (or at most 4–5 tightly related questions in a single call). Do not batch many unrelated questions together.
   - Use `options` in each question whenever the answer space is bounded (yes/no, a known set of choices). Use free-form text only when the answer is truly open-ended.
   - After each answer, evaluate whether new ambiguities surfaced before asking the next question.
   - Prefer concrete questions over broad prompts such as "anything else?"
   - Keep looping until all areas in the table above are complete enough for autonomous implementation.
   - **Do not proceed to step 4 until all questions are answered. If you find yourself wanting to write "or X" / "TBD" / "to be documented" anywhere in the output, that is a sign you skipped a question that should have been asked here.**

4. **Check consistency across the whole change.**
   - Look for contradictions between goal, scope, and acceptance criteria.
   - Cross-check the evolving story against any context already provided by the user.
   - If workspace docs or code are relevant, inspect them to confirm terminology, constraints, and affected parts.
   - Verify: requirements don't contradict each other; acceptance criteria prove the requirements; terminology is consistent; no assumptions remain unresolved.

5. **Review each scope item individually.**
   For every item listed under **Scope**, loop through these four checks before moving on:

   | Check | What to look for |
   |---|---|
   | Completeness | Is the item fully described? Are the inputs, outputs, triggers, and expected behavior clear enough for autonomous implementation without guessing? |
   | Edge cases | Does this specific item have unusual paths — errors, empty states, boundary values, retries, or concurrency — not yet captured in the Edge Cases section? Add any found. |
   | Technical constraints consequences | Does this item imply or conflict with an existing technical constraint (e.g. API contract, data model, performance budget, auth model, third-party limitation)? Flag any constraint that must be honored or must be added to Technical Constraints. |
   | Missing attachments | Would a screenshot, mockup, flow diagram, or reference document make this item unambiguous to implement? If so, ask for it explicitly before proceeding. |

   - Do **not** move to step 6 while any scope item fails a check.
   - If a check reveals a new gap, return to step 3 and ask the follow-up question.

6. **Decide whether the work fits in one story and enforce vertical slices.**
   - **Vertical slice requirement:** every story must deliver a complete, working feature — partial implementations (backend only, UI shell only, data model only) are only allowed if the developer explicitly says so and the feature is complex enough to justify it. Each story must close the loop from user action to user-visible outcome.
   - Keep one story only if it is a thin, independently valuable slice.
   - **Split when:** the request bundles multiple user outcomes or major workflows; different parts would each require substantial analysis; or acceptance criteria would become broad, vague, or hard to verify as one story.
   - When splitting, each story must still be a vertical slice, add incremental releasable value on top of the previous one, and be independently shippable.

7. **Produce the final result** using the output template below.
   - If one story is feasible, output one refined story. If the work is too large, output only the split stories using the same template.
   - Acceptance criteria must be a plain checklist.

### Output Template

```
## Title
[required — max 10 words, outcome-focused, e.g. "Add fraud-check endpoint for payment processing"]

## User Story
[required — max 50 words]
As a [role], I want to [action], so that [benefit].

## Scope
[required — max 200 words. List features, behaviors, screens, or services in scope with key characteristics and points of attention.]
- [feature or behavior — characteristic / point of attention]

## Edge Cases
[optional — max 50 words. Known edge cases and how each should be handled.]
- [edge case — expected handling]

## Out of Scope
[optional — max 30 words. What will not be touched; deferred to later or handled elsewhere.]
- [out-of-scope item]

## Technical Constraints
[optional — max 30 words. Rules, technologies, or standards that must be followed.]
- [constraint]

## Acceptance Criteria
[required — max 50 words. Verifiable checklist confirming the story is done.]
- [ ] [verifiable outcome]

## Attachments
[highly desirable — screenshots, mockups, or diagrams illustrating the feature.]
- [attachment]
```

### Completion Criteria

Do not stop the question loop until all of the following are true:

- Problem and intended user value are clear; scope and non-goals are explicit.
- Story description, scope, edge cases, and technical constraints are sufficient for autonomous implementation.
- Edge cases, failure modes, dependencies, and assumptions are known.
- Acceptance criteria match the requirements and are verifiable.
- Story is consistent with available context, with no contradictions or unresolved assumptions.
- Result is either one thin vertical slice or a clean set of split slices, each delivering complete releasable value on its own.

## Examples

**Input:** "Add a search bar to the product page."

**Clarifying questions asked:** Who performs the search? What data is searched? Should results filter the current page or navigate elsewhere? What happens on no results?

**Output:** A refined story scoped to keyword search on product name and description, filtering the current product list in place, with an empty-state message when no results match, and no pagination changes in scope.

## Edge Cases

- Input already contains detailed acceptance criteria: do not skip the question loop; look harder for hidden ambiguities in scope boundaries and edge cases.
- User refuses to answer a clarifying question: note it as an unresolved assumption and do not produce output until it is resolved.
- Request spans multiple independent user outcomes: always split into separate vertical-slice stories rather than merging into one broad story.
