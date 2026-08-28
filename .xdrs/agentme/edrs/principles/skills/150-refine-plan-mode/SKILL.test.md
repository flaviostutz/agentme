---
skill: 150-refine-plan-mode
skill-version: "2.7"
---

## Test Scenarios

### Scenario 1: New feature implementation

**Trigger / Input**

"Add pagination to the user listing endpoint."

**Expected Behaviour**

The skill activates plan mode immediately. Before writing any code or editing any file, it: (1) states the goal and scope in Phase 1; (2) runs Phase 2 (Requirements Qualification) — restates understanding, scans the 6 areas for missing information, loops asking follow-up questions until convergence, then runs the scope item 3-check review; (3) per the Phase navigation rule, loops on each dependency or context item in Phase 3 (Research, Dependencies, and Draft Plan) until it converges before moving to the next; (4) runs iterative consistency checks in Phase 4, each round asking 1–5 questions across one or more checks (a–i), applying the Phase navigation rule convergence signal to stop; (5) generates a diagram in Phase 5 and loops until the human explicitly confirms it; (6) analyzes all 18 challenge angles in Phase 6 applying the Phase navigation rule per angle; (7) verifies the Phase 7 Pre-Execution Readiness checklist before approving execution.

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

- [ ] Skill does not write or edit any file before Phase 7 is complete.
- [ ] Skill runs Phase 2 (Requirements Qualification) before Phase 3: restates understanding, scans 6 areas, loops asking follow-up questions, and runs scope item 3-check review.
- [ ] Each human interaction round across all phases contains 1–5 questions grouped together.
- [ ] Skill applies the Phase navigation rule convergence signal rather than a fixed round cap.
- [ ] Skill generates a diagram in Phase 5 (Visual Consistency Validation) and loops until the human explicitly confirms it.
- [ ] All 18 challenge angles in Phase 6 are analyzed; related angles may share a round.
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
