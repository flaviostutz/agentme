---
skill: plan-mode-refine
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: New feature implementation

**Trigger / Input**

"Add pagination to the user listing endpoint."

**Expected Behaviour**

The skill activates plan mode immediately. Before writing any code or editing any file, it: (1) states the goal and scope and asks the human to confirm; (2) batches related dependency questions into rounds of 1–5 questions each; (3) runs iterative consistency checks drawing from the global 30-round budget, each round asking 1–5 questions across one or more checks (a–g), stopping when two consecutive rounds surface no new questions; (4) generates a diagram and asks the human to confirm it; (5) analyzes all 11 challenge angles, batching related questions from multiple angles into rounds of 1–5 questions; (6) verifies the Phase 6 checklist before approving execution.

**Simulated Human Responses**
1. "Yes, goal and scope match exactly."
2. "Route handler conventions look correct. Database query pattern is right."
3. "No contradictions. The approach covers the edge cases."
4. "Confirmed — no new issues."
5. "The diagram matches my mental model."
6. "Everything in scope as requested. No security concerns."
7. "Success means all list responses include a `next` cursor and respect `limit`. Side effects are acceptable."
8. "The caching layer is the most fragile assumption. The approach is otherwise sound."
9. "All five scenarios work. Output is internally consistent."

**Assertions**

- [ ] Skill does not write or edit any file before Phase 6 is complete.
- [ ] Skill asks the human to confirm the goal and scope in Phase 1 before proceeding.
- [ ] Each human interaction round across all phases contains 1–5 questions grouped together.
- [ ] Total number of human interaction rounds across all phases does not exceed 30.
- [ ] Skill stops asking rounds when two consecutive rounds surface no new questions.
- [ ] Skill generates a diagram in Phase 4 and asks the human to confirm it.
- [ ] All 11 challenge angles are analyzed; related angles may share a round.
- [ ] Phase 6 checklist is verified before execution is approved.

### Scenario 2: Trivial change

**Trigger / Input**

"Fix the typo 'authentification' → 'authentication' in the README."

**Expected Behaviour**

The skill acknowledges this as a trivial single-step change. Phases 3–5 are abbreviated to a single round. Phase 4 (diagram) is marked as not applicable. Phase 6 checklist is still performed with non-applicable items explicitly marked.

**Assertions**

- [ ] Skill does not run multiple iterative consistency rounds for a trivial change.
- [ ] Skill explicitly marks Phase 4 as not applicable rather than skipping it silently.
- [ ] Phase 6 checklist is still performed before execution.
- [ ] Non-applicable checklist items are explicitly noted as such.

### Scenario 3: Overconfident agent wants to skip planning

**Trigger / Input**

"I already know exactly how to implement this caching layer — let's skip planning and just implement it."

**Expected Behaviour**

The skill explicitly states that agent confidence is not a substitute for consistency checks and proceeds with all 6 phases regardless of the expressed certainty level.

**Assertions**

- [ ] Skill does not skip any phase because the agent expressed confidence.
- [ ] Skill explicitly states the no-assumption rule: confidence does not replace consistency checks.
- [ ] Phase 1 is still executed — goal and scope are stated and confirmed with the human.

### Scenario 4: Agent resolves a subjective output design decision without asking the human

**Trigger / Input**

During angle 10 (output scenario dry runs), a scenario reveals that documentation can be structured in two ways — a single long document or a set of short quick-reference cards. The agent picks the single long document and proceeds to angle 11 without asking.

**Expected Behaviour**

The skill flags this as a violation of the no-assumption rule and the HITL requirement. Subjective output design decisions must be surfaced to the human as a clarifying question — the agent must not resolve them unilaterally. The skill pauses, presents the two options, and asks the human to decide before continuing.

**Assertions**

- [ ] Skill does not proceed past a subjective design decision without asking the human.
- [ ] Skill explicitly frames the question as a clarifying question, not a confirmation request.
- [ ] Skill waits for the human's answer before continuing to the next angle.
- [ ] Violation is noted if the agent attempted to self-resolve a subjective decision.
