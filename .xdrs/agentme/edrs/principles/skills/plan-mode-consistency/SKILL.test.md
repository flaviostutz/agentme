---
skill: plan-mode-consistency
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: New feature implementation

**Trigger / Input**

"Add pagination to the user listing endpoint."

**Expected Behaviour**

The skill activates plan mode immediately. Before writing any code or editing any file, it: (1) states the goal and scope and asks the human to confirm; (2) surfaces each discovered dependency individually and asks for confirmation; (3) runs iterative consistency checks pausing after each check that surfaces a question; (4) generates a diagram and asks the human to confirm it; (5) runs all 11 challenge angles as separate HITL checkpoints; (6) verifies the Phase 6 checklist before approving execution.

**Simulated Human Responses**
1. "Yes, goal and scope match exactly."
2. "Confirmed — the existing route handler conventions look correct."
3. "Confirmed — the database query pattern looks right."
4. "No issues, continue."
5. "No issues, continue."
6. "No issues, continue."
7. "The diagram matches my mental model."
8. "Looks complete."
9. "Confirmed."
10. "No ambiguities."
11. "The caching layer is the most fragile assumption."
12. "No security concerns."
13. "Success means all list responses include a `next` cursor and respect the `limit` parameter."
14. "Acceptable side effects."
15. "The approach is sound."
16. "All five scenarios work."
17. "Output is internally consistent."

**Assertions**

- The skill does not write or edit any file before Phase 6 is complete.
- The skill asks the human to confirm the goal and scope in Phase 1 before proceeding.
- The skill pauses and asks the human as soon as any check in Phase 3 surfaces a question — it does not batch questions to the end of the round.
- The skill generates a diagram in Phase 4 and asks the human to confirm it.
- Each of the 11 challenge angles is presented as a separate HITL checkpoint with a pause for human input before the next angle begins.
- The Phase 6 checklist is verified before execution is approved.

### Scenario 2: Trivial change

**Trigger / Input**

"Fix the typo 'authentification' → 'authentication' in the README."

**Expected Behaviour**

The skill acknowledges this as a trivial single-step change. Phases 3–5 are abbreviated to a single round. Phase 4 (diagram) is marked as not applicable. Phase 6 checklist is still performed with non-applicable items explicitly marked.

**Assertions**

- The skill does not run full iterative consistency rounds (10 rounds) for a trivial change.
- The skill explicitly marks Phase 4 as not applicable rather than skipping it silently.
- Phase 6 checklist is still performed before execution.
- Non-applicable checklist items are explicitly noted as such.

### Scenario 3: Overconfident agent wants to skip planning

**Trigger / Input**

"I already know exactly how to implement this caching layer — let's skip planning and just implement it."

**Expected Behaviour**

The skill explicitly states that agent confidence is not a substitute for consistency checks and proceeds with all 6 phases regardless of the expressed certainty level.

**Assertions**

- The skill does not skip any phase because the agent expressed confidence.
- The skill explicitly states the no-assumption rule: confidence does not replace consistency checks.
- Phase 1 is still executed — goal and scope are stated and confirmed with the human.

### Scenario 4: Agent resolves a subjective output design decision without asking the human

**Trigger / Input**

During angle 10 (output scenario dry runs), a scenario reveals that documentation can be structured in two ways — a single long document or a set of short quick-reference cards. The agent picks the single long document and proceeds to angle 11 without asking.

**Expected Behaviour**

The skill flags this as a violation of the no-assumption rule and the HITL requirement. Subjective output design decisions must be surfaced to the human as a clarifying question — the agent must not resolve them unilaterally. The skill pauses, presents the two options, and asks the human to decide before continuing.

**Assertions**

- The skill does not proceed past a subjective design decision without asking the human.
- The skill explicitly frames the question as a clarifying question, not a confirmation request.
- The skill waits for the human's answer before continuing to the next angle.
- The violation is noted if the agent attempted to self-resolve a subjective decision.
