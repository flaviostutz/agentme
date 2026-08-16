---
name: plan-mode-consistency
description: >
  MANDATORY for ANY planning activity. Read and follow this skill in full whenever the user asks
  to plan, design, propose, outline, draft, brainstorm, architect, or think through anything —
  software features, systems, research, documents, processes, or any other task — before execution
  begins. This skill defines the required pre-execution structured workflow. It MUST be read from
  the XDRS repository even when not directly exposed in the .agents skills folder. Activate in
  full mode for non-trivial tasks and in abbreviated mode (Phases 3–5 collapsed, Phase 4 marked
  not applicable) for trivial single-step tasks.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Ensures that every plan is deeply validated through iterative consistency checks, visual externalization, and multi-angle challenges before execution starts. The skill is not designed to make human work easier — its purpose is to identify precisely where human experience, feeling, and domain knowledge are irreplaceable, and to demand that input before moving forward.

**No-assumption rule**: The agent performs all analysis autonomously. Surface findings as questions only when they are dubious, non-obvious, risky, or require subjective judgment — obvious and deterministic findings must be stated and the agent must continue without pausing. For findings with major impact on downstream users or consumers (breaking changes, behavior regressions, removals), do not ask — emit a prominently formatted **⚠️ SEVERE WARNING** with a clear description of the impact and continue. Do not defer questions to the end of a check, round, or phase — raise them as soon as they arise. The human is the oracle for domain knowledge, intent, and subjective decisions; the agent is the oracle for everything deterministic.

**Task tracking rule**: Use the todo list tool throughout this entire skill. Before starting each phase, create a todo for it and mark it in-progress. Mark it completed immediately when done. For Phase 3 (consistency checks), create a todo for each check (a–g) at the start of each round and mark them individually. For Phase 5 (challenge angles), create a todo for each of the 11 angles before beginning Phase 5 and mark each completed after the human responds to any question raised, or immediately if no question was raised for that angle. An angle todo MUST NOT be marked complete if a subjective decision was resolved without asking the human — if this is detected, flag it as a HITL violation, re-open the todo, surface the decision to the human as a clarifying question, and only mark it complete after the human responds. This ensures no check, round, or angle is silently skipped and no subjective decision is self-resolved.

## Instructions

### Phase 1: Activate Plan Mode

1. Switch to plan mode. Do not write, edit, or execute anything until the plan is fully validated through Phase 6.
2. State the goal in one sentence: what problem is being solved and what the expected outcome is.
3. State the scope boundaries explicitly: what is included and what is explicitly excluded.
4. Ask the human: "Does this goal statement and scope match your intent? Is anything missing or wrong?" Wait for the answer and incorporate it before continuing.

### Phase 2: Research, Dependencies, and Draft Plan

1. Research the existing context: relevant files, prior decisions, established conventions, and analogous patterns already in place.
2. For each contextual input, constraint, or dependency found (existing files, prior decisions, external systems, in-progress work by others), surface non-obvious, risky, or subjective items to the human and ask only when needed. Proceed without asking for obvious or deterministic context items. Only pause for the next item if a question was actually raised.
3. Draft a plan with ordered steps, items to create or modify, and a verification step at the end.
4. Present the draft and ask: "Does this match your intent? What am I missing?" Wait for the answer before continuing.

### Phase 3: Iterative Consistency Checks

**Trivial tasks**: Run exactly one abbreviated round covering only checks (a), (e), and (f). Skip the remaining checks and mark them as not applicable. Proceed directly to Phase 4 after the single round.

**Non-trivial tasks**: Run a minimum of 3 rounds, targeting approximately 10. For each check within a round, ask the human only for findings that are dubious, relevant, subjective, or risky — state obvious findings and continue to the next check without pausing.

Each round runs the following checks in order:

- **(a) Internal consistency**: Are there contradictions between steps? Do the scope boundaries align with the implementation steps?
- **(b) Dry run**: Walk through the plan with the most complex realistic scenario. Where does it break or leave gaps?
- **(c) Component consistency**: Do all elements of the plan work together as a coherent whole? Are there missing connections between parts?
- **(d) XDR alignment**: Does this plan align with the relevant XDRs governing this area? Have the right policies been consulted?
- **(e) Feasibility**: Is each step actually achievable given the current context, constraints, and available resources?
- **(f) Completeness**: Is anything missing that would leave the task half-done or the outcome broken for its consumer?
- **(g) Scope creep check**: Has the plan grown beyond the original request? Flag any additions and ask the human to confirm or reject each one explicitly before continuing.

**Convergence signals** (non-trivial tasks only): Stop running rounds when the last 2 consecutive rounds produce only single-sentence answers with no new issues surfaced. Do not stop on a round count alone — stop when the checks genuinely have nothing left to surface.

### Phase 4: Visual Consistency Validation

**Trivial tasks**: Mark this phase as **not applicable** and state this explicitly before moving to Phase 5. Do not skip silently.

**Non-trivial tasks**:
1. Choose the diagram type that best externalizes this plan's structure:
   - **Flowchart** — step-by-step decision flows and process branches
   - **Concept map** — ideas, relationships, and conceptual structure
   - **Dependency graph** — components and their dependencies
   - **Sequence diagram** — call flows, API interactions, and temporal order
   - **State diagram** — lifecycle states and transitions
   - **Activity diagram** — business workflows with parallel paths
   - **Entity diagram** — data models and relationships
   2. Generate the diagram.
   3. Ask the human: "Does this diagram match your mental model of the solution?" Wait for the answer.
   4. If the diagram reveals gaps or inconsistencies not yet surfaced, return to Phase 3 before continuing.

### Phase 5: Challenge from 11 Distinct Angles

Each angle is a separate analysis step. Run the angle and present findings. Wait for human input only if a question was raised — for obvious or factual findings, state them and proceed immediately. For findings with major impact on users, emit a **⚠️ SEVERE WARNING** and continue without asking. Never batch multiple questions from different angles into a single prompt. Ask clarifying questions whenever findings are ambiguous, subjective, risky, or very relevant — do not resolve those points unilaterally.

#### Plan quality angles

**1. Prompt faithfulness**
Go back to the original request word by word. Is every part of the request covered? Is anything included in the plan that was not asked for? Identify gaps and additions explicitly.

**2. Local context consistency**
Does the plan account for existing files, decisions, and constraints already in place? Does it contradict anything already established in the codebase, repository, or context?

**3. Goal achievability**
Walk the end state step by step: if every step in the plan is executed exactly as written, does the desired outcome actually result? State the end state explicitly. Ask the human to confirm only if there is genuine doubt about whether the outcome matches their expectation.

**4. Ambiguity scan**
Is any step or decision in the plan interpretable in more than one way? Every ambiguity is a future mistake. List all ambiguous points and ask the human to resolve each one.

**5. Pre-mortem**
Assume the plan is executed and fails to reach the goal. What was the most likely reason? Identify the plan's most fragile assumption or weakest step.

**6. Security and privacy scan**
Does the plan or its output expose sensitive information, create privacy risks, or introduce misuse vectors? This applies to any task type: documentation, code, processes, data handling, communications. If findings are present and require a subjective decision to resolve, ask the human. For clear and obvious mitigations, state them and continue.

**7. Success criteria and falsifiability**
How will we know this plan succeeded or failed? Are the success criteria concrete enough to be measurable and observable? If they are vague, the outcome cannot be evaluated. If the criteria are already clear and measurable, state the assessment and continue. Ask the human only when criteria are vague or require their input to sharpen.

**8. Second-order effects**
What changes as a side effect of executing this plan beyond the intended outcome? Does solving this problem create a new problem elsewhere — in adjacent systems, files, processes, or stakeholders? List the side effects. Ask the human whether they are acceptable only when the effects are non-obvious or the decision is subjective.

**9. Steelman the opposition**
What is the strongest case against this approach? What would a well-informed critic say about this plan? Present the strongest objection. Ask the human to respond if the objection raises a genuine risk or requires a subjective decision — otherwise state the counter-argument and continue.

#### Output quality angles

**10. Output scenario dry runs**
Simulate 5 realistic usage scenarios of the expected output by its actual consumer. For each scenario, ask: "Does the output serve its consumer in this situation?" Use scenarios that cover typical use, edge cases, and at least one adversarial or failure case.

Examples of scenario framing:
- If the output is operator documentation: "A worker needs to reset the machine at 2 AM — will they find the procedure in under 2 minutes?"
- If the output is an API: "A developer calling this endpoint with a malformed payload — what happens?"
- If the output is a business process: "An employee following this process on their first day — will they complete it without asking for help?"

Whenever a scenario reveals ambiguity or requires a subjective judgment, stop and ask the human a clarifying question. Do not resolve subjective decisions unilaterally.

**11. Output internal consistency**
Check that the planned output is internally consistent: no contradictions between parts, no gaps between sections, all elements serve the same goal. Run approximately 3 rounds until answers converge to single sentences with no new issues surfaced.

### Phase 6: Pre-Execution Readiness

Before approving execution, verify ALL items in the checklist below. If any item cannot be checked, return to the relevant phase and resolve it first. For trivial tasks, mark non-applicable items explicitly as **N/A** rather than leaving them unchecked or omitting them.

- [ ] Consistency rounds converged (convergence signals met — last 2 rounds produced only single-sentence answers with no new issues) *(trivial tasks: single abbreviated round completed)*
- [ ] All 11 challenge angles completed with human input received for every ambiguity and subjective decision *(trivial tasks: single abbreviated round — mark remaining angles N/A)*
- [ ] Diagram generated and confirmed by the human *(trivial tasks: N/A — mark explicitly)*
- [ ] No unresolved human questions outstanding
- [ ] Scope confirmed by the human with no silent expansions
- [ ] Any irreversible or high-impact steps have a mitigation or fallback noted *(trivial tasks: N/A if no irreversible steps)*

Only proceed to execution when every item is checked or explicitly marked N/A. Do not start execution to escape planning discomfort — only start when confidence is genuine and all items are verified.

---

## Anti-Patterns

Avoid these common failure modes:

- **Planning theater**: running rounds without real critical thinking. The quality of questioning matters more than the count of rounds. Rounds that confirm the plan against itself add false confidence — checks must challenge assumptions, not validate them.
- **Scope creep silence**: the plan grows beyond the original request without the human noticing. Every addition must be flagged explicitly.
- **Agent self-validation**: the agent answers its own questions on subjective, domain, or intent-based decisions and proceeds without asking the human. The human is the oracle for domain knowledge, intent, and subjective decisions — the agent must not self-resolve those unilaterally.
- **Confidence as a proxy for correctness**: an agent expressing certainty does not mean the plan is correct. Run all checks regardless of how confident the agent sounds.

## Re-Plan Triggers

Stop execution and return to Phase 1 if any of the following occur:

- A discovered assumption underlying the plan is wrong.
- The scope has expanded by more than approximately 20% beyond the original request.
- Two consecutive execution steps fail unexpectedly and the root cause points to a planning gap.

## Examples

**Input**: "Add a rate-limiting feature to the API."

- Phase 1: Goal stated as "rate-limit all POST endpoints to 100 req/min per user; internal service calls excluded." Human confirms.
- Phase 2: Discovers existing middleware and an in-progress PR touching the same path. Human asked about each before drafting.
- Phase 3: Round 1 — check (a) finds the plan references a `RateLimiter` class not yet decided on; human asked to clarify. Round 5 — all checks return trivial answers; convergence reached.
- Phase 4: Sequence diagram generated. Human confirms it matches their model.
- Phase 5: Angle 8 (second-order effects) reveals that rate-limiting breaks an existing test suite that sends rapid sequential requests; human decides to add a test bypass header. Angle 9 (steelman) surfaces that Redis dependency adds operational complexity; human accepts the trade-off.
- Phase 6: All items checked. Execution approved.

**Input**: "Write operator documentation for the conveyor belt system."

- Phase 5, angle 10 (output dry runs): Scenario 1 — "An operator needs to restart the belt after an emergency stop at midnight." The draft plan has no emergency stop section; human asked whether to add it. Scenario 3 — "Operator reading on a mobile phone." Human asked whether a condensed quick-reference card is needed alongside the full manual.

## Edge Cases

- **Trivial changes** (typo fixes, single-line formatting): Phases 3–5 may be shortened to a single abbreviated round. Phase 4 (diagram) may be skipped, but MUST be explicitly noted as not applicable in the task tracking todo with a brief reason (e.g., "Phase 4: N/A — trivial single-step change"). Phase 6 checklist still applies — mark non-applicable items explicitly.
- **Agent that insists it knows the answer**: Do not skip any phase because the agent expresses confidence. Confidence is not a substitute for consistency checks.
- **Diagram cannot be generated**: Describe the flow in a plain-language walkthrough step by step. The intent of Phase 4 is to externalize the plan's structure — the medium is secondary.
- **Scope change discovered mid-planning**: If Phase 3 or Phase 5 reveals that the scope must change significantly, restart from Phase 2 with the revised scope. Do not patch the plan incrementally without a full re-check.
- **Human is unavailable for a step**: Note the unanswered question explicitly in the plan. Do not proceed past that point until the human responds.

## References

- [`agentme-edr-012`](../../012-continuous-xdr-enrichment.md) — Continuous XDR enrichment policy
- [`agentme-edr-501`](../../../governance/501-project-quality-standards.md) — Project quality standards
- [`agentme-edr-017`](../../017-skill-testing.md) — Skill testing mandate
