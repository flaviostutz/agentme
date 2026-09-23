---
skill: refine-plan-mode
skill-version: "3.4.0"
---

## Test Scenarios

### Scenario 1: New feature implementation

**Trigger / Input**

"Add pagination to the user listing endpoint."

**Expected Behaviour**

The skill activates plan mode immediately. Before writing any code or editing any file, it: (1) states the goal and scope in Phase 1; (2) runs Phase 2 (Requirements Qualification) — restates understanding, scans the 6 areas for missing information, loops asking follow-up questions until convergence, then runs the scope item 3-check review; (3) per the Phase navigation rule, loops on each dependency or context item in Phase 3 (Research, Dependencies, and Draft Plan) until it converges before moving to the next; (4) runs iterative consistency checks in Phase 4, each round asking 1–5 questions across one or more checks (a–i), applying the Phase navigation rule convergence signal to stop; (5) generates a diagram and 2–3 sample paginated-response examples in Phase 5 and loops until the human explicitly confirms them; (6) analyzes all 9 challenge angles in Phase 6 applying the Phase navigation rule per angle; (7) verifies the Phase 7 Pre-Execution Readiness checklist before approving execution.

**Simulated Human Responses**
1. "Yes, goal and scope match exactly."
2. "Route handler conventions look correct. Database query pattern is right."
3. "No contradictions. The approach covers the edge cases."
4. "Confirmed — no new issues."
5. "The diagram and examples match my mental model."
6. "Everything in scope as requested. No security concerns."
7. "Success means all list responses include a `next` cursor and respect `limit`. Side effects are acceptable."
8. "The caching layer is the most fragile assumption. The approach is otherwise sound."
9. "All five scenarios work. Output is internally consistent."

**Assertions**

- [ ] Skill does not write or edit any file before Phase 7 is complete.
- [ ] Skill runs Phase 2 (Requirements Qualification) before Phase 3: restates understanding, scans 6 areas, loops asking follow-up questions, and runs scope item 3-check review.
- [ ] Each human interaction round across all phases contains 1–5 questions grouped together.
- [ ] Skill applies the Phase navigation rule convergence signal rather than a fixed round cap.
- [ ] Skill generates a diagram in Phase 5 (Visual and Example Consistency Validation) and loops until the human explicitly confirms it.
- [ ] Skill shows 2–3 textual examples of the paginated response in Phase 5 alongside the diagram.
- [ ] Confirmed examples appear in a Quality Verification Strategy "Confirmed examples" sub-list, each with an acceptance test case.
- [ ] All 9 challenge angles in Phase 6 are analyzed; related angles may share a round.
- [ ] Phase 7 Pre-Execution Readiness checklist is verified before execution is approved.

### Scenario 2: Well-structured input still triggers full Phase 2 Requirements Qualification

**Trigger / Input**

"Add a `/health` endpoint to the API server that returns HTTP 200 with `{status: 'ok'}` and the current UTC timestamp."

**Expected Behaviour**

Despite the input being detailed and well-structured, the skill runs Phase 2 (Requirements Qualification) in full. It restates the current understanding, scans all 6 areas for missing information, and asks follow-up questions. At minimum it asks: who the consumer of the endpoint is, whether authentication is required, what the expected response content-type is, and whether any existing health-check infrastructure must be integrated. After convergence on Step 3, it runs the scope item 3-check review.

**Simulated Human Responses**
1. "Consumer is the load balancer. No auth required. Content-type JSON. No existing health-check infrastructure."
2. "No edge cases beyond what was asked. No conflicting constraints."

**Assertions**

- [ ] Skill does not skip Phase 2 (Requirements Qualification) because the input appears complete.
- [ ] Skill scans all 6 areas in Phase 2 Step 2 regardless of input detail level.
- [ ] Skill runs the scope item 3-check review in Phase 2 Step 4.
- [ ] Skill applies the Phase navigation rule convergence signal before advancing to Phase 3.

### Scenario 3: Overconfident agent wants to skip planning

**Trigger / Input**

"I already know exactly how to implement this caching layer — let's skip planning and just implement it."

**Expected Behaviour**

The skill explicitly states that agent confidence is not a substitute for consistency checks and proceeds with all 7 phases regardless of the expressed certainty level.

**Assertions**

- [ ] Skill does not skip any phase because the agent expressed confidence.
- [ ] Skill explicitly states the Questioning rule: confidence does not replace consistency checks.
- [ ] Phase 1 is still executed — goal and scope are stated; Phase 2 (Requirements Qualification) is run to qualify requirements.

### Scenario 4: Agent resolves a subjective output design decision without asking the human

**Trigger / Input**

During angle 10 (output scenario dry runs), a scenario reveals that documentation can be structured in two ways — a single long document or a set of short quick-reference cards. The agent picks the single long document and proceeds to angle 11 without asking.

**Expected Behaviour**

The skill flags this as a violation of the Questioning rule and the HITL requirement. Subjective output design decisions must be surfaced to the human as a clarifying question — the agent must not resolve them unilaterally. The skill pauses, presents the two options, and asks the human to decide before continuing.

**Assertions**

- [ ] Skill does not proceed past a subjective design decision without asking the human.
- [ ] Skill explicitly frames the question as a clarifying question, not a confirmation request.
- [ ] Skill waits for the human's answer before continuing to the next angle.
- [ ] Violation is noted if the agent attempted to self-resolve a subjective decision.
- [ ] Skill gives the question a short title and a context line naming where the choice arose (the angle and plan section).
- [ ] Skill describes each option (single long document vs. quick-reference cards) with its consequences and prefixes one with "(recommended)".
- [ ] Skill maps the title, context, and options to the `vscode_askQuestions` fields, or places the full question in a chat message before the call when a part exceeds the field limit.

### Scenario 5: Feature split — deferred parts saved to TODO.md per agentme-edr-001

**Trigger / Input**

"Build a complete admin dashboard: user management, billing management, and audit log viewer."

**Expected Behaviour**

Phase 2 Step 4 surfaces roughly 24 distinct in-scope items across the three subsystems. Phase 2 Step 5 judges the request too large — it spans 3 qualitatively different concerns (user management, billing, audit) each needing independent data-model and UI design, and exceeds the ~20-item threshold — and proposes a 3-way split. The human accepts the split and picks "User management" as Part 1. Phases 1–7 run on User management only; the other two parts are recorded in the Deferred Features list. At Phase 7, the skill presents a brief one-line-per-item Deferred Features summary, then uses `vscode_askQuestions` offering "Save to TODO.md" as the recommended option. The human picks it. The skill creates (or appends to) `TODO.md` at the workspace root and appends one `agentme-edr-001` entry per deferred part (Billing management, Audit log viewer), each with its own `## N- Title (date)` heading, `status: open`, a `prompt` merging that part's Objective/Scope/Context captured so far plus a suggested resume prompt, and `deferred reason` set to the split rationale.

**Simulated Human Responses**
1. "Accept split — start planning User management"
2. "Save to TODO.md"

**Assertions**

- [ ] Skill proposes a 3-way split with a brief rationale for each part's boundary, justified by at least two of the Phase 2 Step 5 size criteria.
- [ ] Only the chosen part (User management) is planned through Phases 1–7; the other two parts are not further elaborated beyond the deferred entry.
- [ ] Phase 7 presents a Deferred Features summary as brief one-line bullets before asking where to save.
- [ ] `vscode_askQuestions` offers "Save to TODO.md" as the recommended option.
- [ ] TODO.md is created (or appended to) at the workspace root following the `agentme-edr-001` entry format (no `### Group:`/`#### ` headings).
- [ ] Each deferred part gets its own numbered entry with `status: open` and a `prompt` merging Objective, Scope, and Context captured so far.
- [ ] Each entry's `deferred reason` records the split rationale.

### Scenario 6: Final plan artifact contains no process narrative

**Trigger / Input**

A user runs the full refine-plan-mode workflow across multiple rounds — including at least one re-run of a phase gate (e.g., "Re-run Phase 4: Consistency Checks — deeper pass") and one Phase 2 Step 5 scope split with a deferred part — before reaching Phase 7 and confirming "Hand off to implementation".

**Expected Behaviour**

Throughout every phase, the plan document is maintained as a single continuously-edited artifact per the Artifact rule. When Phase 4 is re-run, the consistency-check findings from the first pass are merged or replaced in place — not appended as a second "round 2" narrative block. When a decision is revisited, the earlier entry is edited, not left beside a newer contradicting one. The final plan handed off at Phase 7 follows the structure in SKILL.md's Final Plan Artifact Template section: Title/TL;DR, Steps, Relevant files, Quality Verification Strategy (including Unverified References), Decisions, Further Considerations — with no additional top-level sections such as a session log, round-by-round history, or Q&A transcript.

**Simulated Human Responses**
1. "Accept split — start planning [Part 1 name]" (Phase 2 Step 5 scope split)
2. "Re-run Phase 4: Consistency Checks — deeper pass"
3. "Continue to Phase 5 — Visual and Example Consistency Validation" (after the re-run converges)
4. "Hand off to implementation" (Phase 7 final gate)

**Assertions**

- [ ] The final plan document contains no section narrating the planning process itself (e.g. "Round 1", "Round 2", phase-gate Q&A transcripts, a session status log).
- [ ] No decision or section appears twice with one marked as superseding the other — reversed decisions are edited in place.
- [ ] The final plan's top-level sections match SKILL.md's Final Plan Artifact Template section exactly, with zero additional top-level sections.
- [ ] Todo-list tracking used during the workflow (per the Task tracking rule) does not appear inside the final plan document.
- [ ] The Deferred Features entry from the Phase 2 Step 5 split appears only in `TODO.md` (per `agentme-edr-001`), not duplicated inside the main plan body.
