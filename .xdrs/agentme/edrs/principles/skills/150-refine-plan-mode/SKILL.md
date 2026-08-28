---
name: 150-refine-plan-mode
description: >
  MANDATORY for ANY planning activity. Read and follow this skill in full whenever the user asks
  to plan, design, propose, outline, draft, brainstorm, architect, or think through anything —
  software features, systems, research, documents, processes, or any other task — before execution
  begins. This skill defines the required pre-execution structured workflow. It MUST be read from
  the XDRS repository even when not directly exposed in the .agents skills folder.
metadata:
  author: flaviostutz
  version: "1.1"
---

## Overview

Ensures that every plan is deeply validated through iterative consistency checks, visual externalization, and multi-angle challenges before execution starts. The skill is not designed to make human work easier — its purpose is to identify precisely where human experience, feeling, and domain knowledge are irreplaceable, and to demand that input before moving forward.

**Questioning rule**: Ask questions about all findings proactively — skip only trivially obvious ones with no decision weight. Use `vscode_askQuestions` when available; ask at most 4–5 tightly related questions per call. Before each new round, explicitly state what territory has not yet been explored and will be the focus of this round (in structured phases such as Phase 3 or Phase 5, state which predefined check or angle you are covering next) — do not re-ask questions already addressed in previous rounds. Never self-resolve a choice point, and never produce output, plan sections, or decisions while any open decision, unresolved assumption, or ambiguity remains — embed nothing as 'or X / TBD / to be decided' — resolve through questions first. For findings with major impact on downstream users or consumers (breaking changes, behavior regressions, removals), do not ask — emit a prominently formatted **SEVERE WARNING** with a clear description of the impact and continue.

**Task tracking rule**: Use the todo list tool throughout this entire skill. Before starting each phase, create a todo for it and mark it in-progress. Mark it completed immediately when done. For Phase 3 (consistency checks), create a todo for each check (a–i) before beginning Phase 3 and mark each completed when that check individually converges. For Phase 5 (challenge angles), create a todo for each of the 17 angles before beginning Phase 5 and mark each completed after the human responds to any question raised, or immediately if no question was raised for that angle. An angle todo MUST NOT be marked complete if any decision was self-resolved without asking the human (per the Questioning rule) — if this is detected, flag it as a HITL violation, re-open the todo, surface the decision to the human as a clarifying question, and only mark it complete after the human responds. This ensures no check, round, or angle is silently skipped and no decision is self-resolved.

**Phase navigation rule**: Governs loop control, convergence, and phase transitions across all phases:
- **Loop**: within each phase, loop asking questions until convergence or Skip. Convergence means the last 2 consecutive rounds produced only single-sentence answers with no new issues surfaced — do not stop on a round count alone; stop only when checks genuinely have nothing left to surface. Explicit human confirmation that the phase output is correct also counts as convergence.
- **Checklist gate**: after convergence, verify any completion checklist — if items are unmet, ask those specifically (targeted questions, not a full loop restart) before advancing.
- **Skip**: when the human invokes Skip, stop the loop, record all open items as named Deferred Risks (visible in the plan, carried forward), suspend the hard gate for those items, and advance immediately.
- **Backtracking**: when any finding touches goals, scope, requirements, or assumptions from an earlier phase, explain to the human which phase is affected and why, and re-run that phase's loop focused on the new information; backtracking overrides any prior skip; Phase 1 concerns re-route to Phase 1.5 Step 1.

## Instructions

### Phase 1: Activate Plan Mode

1. Switch to plan mode. Do not write, edit, or execute anything until the plan is fully validated through Phase 6.
2. State the goal in one sentence: what problem is being solved and what the expected outcome is.
3. State the scope boundaries explicitly: what is included and what is explicitly excluded.

### Phase 1.5: Requirements Qualification

### Step 1 — Restate the request
Restate current understanding in 2-3 lines. A well-structured or detailed input does NOT exempt you from running all steps — always proceed through the full phase top-down.

### Step 2 — Identify missing information
Scan across 6 areas:

| Area | Questions to resolve |
|---|---|
| Problem and value | What problem is being solved? Who benefits? What value should exist after the change? |
| Scope | What behavior is in scope? What is out? What stays unchanged? |
| Requirements | What must the system do? What inputs, outputs, or constraints matter? |
| Flow and interactions | What is the main flow? Which actors, systems, or interfaces are involved? |
| Edge cases | What unusual but valid scenarios must work? What error paths must be handled? |
| Dependencies | What upstream/downstream systems affect this? Are there required approvals or sequencing? |

### Step 3 — Ask follow-up questions
Loop asking questions across the 6 areas. After each answer, evaluate whether new ambiguities surfaced in areas not yet explored before continuing. Apply the Phase navigation rule — loop until convergence, then proceed to Step 4.

### Step 4 — Scope item review (separate pass after Step 3 converges)
For every in-scope item, run these three checks. For each check, ask questions about findings — only skip trivially obvious ones. Apply the Phase navigation rule — loop until all items pass.

| Check | What to look for |
|---|---|
| Completeness | Inputs, outputs, triggers, expected behavior clear enough for autonomous implementation? |
| Edge cases | Unusual paths not yet captured? Add any found. |
| Technical constraints | Item implies or conflicts with existing technical constraint? |

### Completion criteria for Phase 1.5
Do not proceed to Phase 2 until all are true:
- [ ] Problem, intended value, and beneficiary unambiguous.
- [ ] Scope boundaries explicit (in / out / unchanged).
- [ ] Requirements, flow, edge cases, dependencies known or explicitly deferred.
- [ ] Every in-scope item passes 3-check review with no open findings.

### Phase 2: Research, Dependencies, and Draft Plan

1. Research the existing context: relevant files, prior decisions, established conventions, and analogous patterns already in place.
2. For each contextual input, constraint, or dependency found (existing files, prior decisions, external systems, in-progress work by others), ask questions about all non-trivial items. For each dependency or context item, apply the Phase navigation rule: loop asking questions until that item converges before moving to the next. Only skip asking for trivially obvious or deterministic context items with no decision weight.
3. Draft a plan with ordered steps, items to create or modify, and a verification step at the end. The plan MUST include two dedicated sections:
   - **Quality Verification Strategy**: (a) existing checks that must continue to pass; (b) new checks required for the task — for code: unit tests, integration tests, linting, type checking, dead code detection, security/dependency audit, schema/contract validation; for documents, analyses, and policies: proofreading, fact-checking, citation and link validation, policy compliance review, peer review, readability check; (c) exact executable steps or commands for each check; (d) what each check verifies. A plan without this section is incomplete.
   - **Unverified References**: any resource referenced in the plan but not verified during planning must be listed here as *"unverified — must verify before use"* with a concrete first-step verification. For code: file paths, function names, CLIs, library APIs (e.g., `which cmd`, `npm list pkg`). For documents and analyses: statistics, quotes, cited studies, named organizations or people, URLs, legal or regulatory references. This section is the primary defense against fabricated claims surfacing only at execution time.
4. Present the draft and ask: "Does this match your intent? What am I missing? What verification checks exist today, and what new checks will confirm the key outcomes of this plan?" Wait for the answer before continuing. Apply Phase navigation rule: loop re-presenting the updated draft until the human explicitly confirms no gaps remain.

### Phase 3: Iterative Consistency Checks

Run checks (a–i) sequentially. For each check: formulate 2–3 questions targeted at that check in the context of the current plan, attempt to answer by reasoning through evidence — this is not self-resolving. For anything unresolved or subjective, ask the human per the Questioning rule. Loop on each check until it fully converges before moving to the next check. Convergence for a check = last 2 consecutive exchanges on that check produced only single-sentence answers with no new issues surfaced (per Phase navigation rule).

Checks to run in order:

- **(a) Internal consistency**: Are there contradictions between steps? Do the scope boundaries align with the implementation steps?
- **(b) Dry run**: Walk through the plan with the most complex realistic scenario. Where does it break or leave gaps? During the dry run, execute all verification checks that already exist and are applicable to the context. Failing checks and missing coverage for planned changes are blockers — surface them immediately.
- **(c) Component consistency**: Do all elements of the plan work together as a coherent whole? Are there missing connections between parts?
- **(d) XDR alignment**: Does this plan align with the relevant XDRs governing this area? Have the right policies been consulted?
- **(e) Feasibility**: Is each step actually achievable given the current context, constraints, and available resources?
- **(f) Completeness**: Is anything missing that would leave the task half-done or the outcome broken for its consumer?
- **(g) Scope creep check**: Has the plan grown beyond the original request? Flag any additions and ask the human to confirm or reject each one explicitly before continuing. For large plans (more than approximately 10 steps), verify that each step traces to a requirement, user request, or policy — untraceable steps must be explicitly confirmed by the human.
- **(h) Verification coverage and executability**: Are verification checks defined for each changed or new outcome, with exact executable steps or commands? Do they cover the applicable strategies for the context — for code: unit tests, integration tests, linting, type checking, dead code detection, security audit, schema/contract validation; for documents and analyses: proofreading, fact-checking, link and citation validation, policy compliance review, peer review, readability check? Can a reviewer independently confirm correctness by executing them without setup friction?
- **(i) Unverified claims audit**: Scan the plan for any factual claim, reference, or resource that the agent did not verify with a tool call or direct inspection — for code: file paths, function names, CLIs, library APIs; for documents and analyses: cited statistics, quoted sources, URLs, named people or organizations, legal references. Either verify each one immediately (preferred) or add it to the Unverified References section with a mandatory first-step verification before use. This check MUST NOT be skipped even when the agent is confident.

**Human prompt examples** — these are effective ways to drive a round:

- `"Check for more features I would probably need but that are not part of the plan. Ask questions."`
- `"What happens if the file doesn't exist? Ask questions."`
- `"Dry run if I send a file with 10GB in size"`
- `"What happens if we have 10 million files?"`
- `"Explore if all types of input would work with this utility"`
- `"Is the plan doing everything we asked in the beginning?"`
- `"How are you making sure those things are implemented correctly?"`
- `"Verify all references in the plan. Ask questions."`
- `"Check for edge cases we didn't discuss yet. Ask questions."`
- `"Check for consistency and ask questions"`
- `"Show me a diagram explaining the overall feature structure"`
- `"Explain to me what this utility does"`
- `"How could I distribute this utility?"`

### Phase 4: Visual Consistency Validation

1. Choose the diagram type that best externalizes this plan's structure:
   - **Flowchart** — step-by-step decision flows and process branches
   - **Concept map** — ideas, relationships, and conceptual structure
   - **Dependency graph** — components and their dependencies
   - **Sequence diagram** — call flows, API interactions, and temporal order
   - **State diagram** — lifecycle states and transitions
   - **Activity diagram** — business workflows with parallel paths
   - **Entity diagram** — data models and relationships
   2. Generate the diagram.
   3. Ask the human: "Does this diagram match your mental model of the solution?" Wait for the answer. Apply Phase navigation rule: loop regenerating and re-presenting the diagram until the human explicitly confirms it matches their mental model.
   4. If the diagram reveals gaps or inconsistencies not yet surfaced, return to Phase 3 before continuing.

### Phase 5: Challenge from 17 Distinct Angles

Each angle is an analysis step. Run the angle and present findings. Batch questions from related angles into a single round when findings are related — batching questions is permitted, skipping analysis is not. Ask questions about findings. Only skip asking when a finding is trivially obvious and carries no decision weight. For findings with major impact on users, emit a **SEVERE WARNING** and continue without asking. Apply Phase navigation rule to each angle: ask questions about findings proactively; loop on that angle's findings until no new questions surface before marking the angle complete. Do not resolve choice points unilaterally — apply the Questioning rule.

#### Plan quality angles

**1. Prompt faithfulness**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Go back to the original request word by word. Is every part of the request covered? Is anything included in the plan that was not asked for? Identify gaps and additions explicitly.

**2. Local context consistency**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Does the plan account for existing files, decisions, and constraints already in place? Does it contradict anything already established in the codebase, repository, or context?

**3. Goal achievability**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Walk the end state step by step: if every step in the plan is executed exactly as written, does the desired outcome actually result? State the end state explicitly. Ask the human to confirm the end state and whether it matches their expectation.

**4. Ambiguity scan**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Is any step or decision in the plan interpretable in more than one way? Every ambiguity is a future mistake. List all ambiguous points and ask the human to resolve each one.

**5. Pre-mortem**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Assume the plan is executed and fails to reach the goal. What was the most likely reason? Identify the plan's most fragile assumption or weakest step. Specifically check whether any referenced resources, facts, tools, files, or capabilities are fabricated or assumed without verification — this is a common single-point failure mode regardless of task type.

**6. Security and privacy scan**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Does the plan or its output expose sensitive information, create privacy risks, or introduce misuse vectors? This applies to any task type: documentation, code, processes, data handling, communications. Ask the human about any non-trivial findings. For trivially obvious mitigations with no decision weight, state them and continue.

**7. Success criteria and falsifiability**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Verification checks are the primary falsifiability mechanism. A plan without defined, executable verification has unverifiable success criteria — treat this as a blocking gap. How will we know this plan succeeded or failed? Are the success criteria concrete enough to be measurable and observable? If they are vague, the outcome cannot be evaluated. Ask the human to validate the success criteria and confirm they are concrete and measurable.

**8. Second-order effects**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
What changes as a side effect of executing this plan beyond the intended outcome? Does solving this problem create a new problem elsewhere — in adjacent systems, files, processes, or stakeholders? List the side effects. Ask the human whether the side effects are acceptable.

**9. Steelman the opposition**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
What is the strongest case against this approach? What would a well-informed critic say about this plan? Present the strongest objection. Ask the human to respond to the objection.

#### Output quality angles

**10. Output scenario dry runs**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Simulate 5 realistic usage scenarios of the expected output by its actual consumer. For each scenario, ask: "Does the output serve its consumer in this situation?" Use scenarios that cover typical use, edge cases, and at least one adversarial or failure case.

Examples of scenario framing:
- If the output is operator documentation: "A worker needs to reset the machine at 2 AM — will they find the procedure in under 2 minutes?"
- If the output is an API: "A developer calling this endpoint with a malformed payload — what happens?"
- If the output is a business process: "An employee following this process on their first day — will they complete it without asking for help?"

Whenever a scenario reveals ambiguity or requires a subjective judgment, stop and ask the human a clarifying question. Do not resolve subjective decisions unilaterally.

**11. Output internal consistency**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Check that the planned output is internally consistent: no contradictions between parts, no gaps between sections, all elements serve the same goal. Apply Phase navigation rule.

**12. Input coverage dry run**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Simulate 50 different inputs against the produced element with the goal of discovering edge cases, security issues, and unresolved discussion points not yet surfaced in earlier phases. The 50 inputs are a breadth-forcing tool — not a pass/fail test. What counts as an "input" depends on the task type: for code/systems — function arguments, API payloads, config values; for documents/policies/processes — reader queries, usage scenarios, edge-case interpretations. Inputs must span typical, edge, boundary, invalid, adversarial, and combined cases. For each, ask: does this reveal a new edge case, security risk, or ambiguity not already addressed? Surface all findings as questions to the human per the Questioning rule.

**13. Stress and failure conditions**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Simulate 20 different stress or failure situations that could occur while the product/output is being used or running, with the goal of discovering resilience gaps, missing recovery paths, and unhandled failure modes not yet surfaced. The 20 situations are a breadth-forcing tool — not a pass/fail test. What counts as a "stress situation" depends on the task type: for code/systems — infrastructure failures (e.g., database down mid-transaction, third-party API unavailable), user-side disruptions (e.g., device freezes mid-task, session timeout, connectivity loss), environmental degradation (e.g., slow under load, corrupt data mid-process), combined/cascading failures; for documents/policies/processes — reader under time pressure, document misread during a crisis, policy applied by someone who skips sections, ambiguous instruction followed incorrectly under stress. Human factors apply to all types (e.g., user gets bored and abandons a long or confusing flow). For each situation, ask: does this expose a gap in error handling, recovery, communication, or resilience? Surface all findings as questions to the human per the Questioning rule.

#### Discussion and improvement angles

**14. Alternative approaches**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Enumerate 2–3 meaningfully different ways the goal could be achieved. For each alternative, describe the approach in 1–2 lines and compare it against the current plan on at least: implementation effort, reversibility, risk, and fit with existing context. The goal is to surface whether the current plan is the right approach or just the first one considered. Ask the human: which tradeoffs matter most, and does the current approach still win? If an alternative is clearly superior in the context, flag it prominently and ask the human to reconsider.

**15. Stakeholder perspective tour**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Walk through the plan from the perspective of 3–5 distinct stakeholders who are not the primary requester — e.g., maintainer, ops/support team, end user, affected third party, security reviewer, first-time reader. For each stakeholder, ask: what would they find problematic, missing, or unclear in this plan? This is not about their usage scenarios (covered by angle 10) but about their critique of the plan itself. Surface all findings as questions to the human per the Questioning rule.

**16. Simplification check**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Review the plan for anything that could be cut, simplified, or deferred without losing essential value. For each candidate: what is it, why might it be unnecessary, and what is the risk of removing it? This is not the same as scope-creep detection (angle 1, which checks for additions) — this angle actively proposes reductions. Ask the human to confirm or reject each simplification candidate explicitly.

**17. Observability and failure recovery**
**Challenge questions:** Formulate 3–5 questions that could challenge the current plan from this angle, grounded in the current plan and broader context (codebase, prior decisions). Reason through each, surfacing evidence — not self-resolving. Bring unresolved or subjective questions to the human per the Questioning rule. Then run the analysis below.
Ask: if the output fails or behaves incorrectly while in use, will anyone know, and can it be corrected? What counts as "observability" depends on the task type: for code/systems — are there logs, metrics, alerts, health checks, debug tooling, and a rollback path? For documents/policies/processes — is it known where and by whom the document is being used? Is there a way to detect misapplication or misinterpretation? Is it clear how to report an issue with the document, and how corrections reach all consumers? If none of these mechanisms are planned, ask the human whether they are needed. If the output is a prototype or throwaway artifact with no ongoing use, this angle may be explicitly marked N/A.

### Phase 6: Pre-Execution Readiness

Before approving execution, verify ALL items in the checklist below. If any item cannot be checked, return to the relevant phase and resolve it first.

- [ ] Consistency rounds converged (convergence signals met — last 2 rounds produced only single-sentence answers with no new issues) (per Phase navigation rule)
- [ ] All 17 challenge angles completed with human input received for every ambiguity and subjective decision
- [ ] Diagram generated and confirmed by the human
- [ ] No unresolved human questions outstanding
- [ ] Scope confirmed by the human with no silent expansions
- [ ] Any irreversible or high-impact steps have a mitigation or fallback noted
- [ ] Quality Verification Strategy defined in the plan with exact executable steps for all applicable check types (code: unit tests, integration tests, linting, static analysis; documents/analyses: fact-checking, link and citation validation, peer review, etc.)
- [ ] Verification checks executed during dry run and results reviewed — failures and coverage gaps resolved
- [ ] All high-risk unverified references (code or factual) listed in the Unverified References section with explicit first-step verification in the execution plan

Only proceed to execution when every item is checked or explicitly marked N/A. Do not start execution to escape planning discomfort — only start when confidence is genuine and all items are verified.

---

## Anti-Patterns

Avoid these common failure modes:

- **Planning theater**: running rounds without real critical thinking. Asking many questions is correct behavior — the anti-pattern is asking hollow, self-validating questions, not asking frequently. Rounds that confirm the plan against itself add false confidence — checks must challenge assumptions, not validate them.
- **Scope creep silence**: the plan grows beyond the original request without the human noticing. Every addition must be flagged explicitly.
- **Agent self-validation**: the agent answers its own questions on subjective, domain, or intent-based decisions and proceeds without asking the human. The human is the oracle for domain knowledge, intent, and subjective decisions — the agent must not self-resolve those unilaterally.
- **Confidence as a proxy for correctness**: an agent expressing certainty does not mean the plan is correct. Run all checks regardless of how confident the agent sounds.
- **Treating unverified references as facts**: the agent references files, CLIs, statistics, library APIs, quoted sources, or named organizations without a tool call or direct inspection to confirm they exist. All high-risk references must be verified immediately or explicitly listed in the Unverified References section with a mandatory first-step check before use.

## Re-Plan Triggers

Stop execution and return to Phase 1 if any of the following occur:

- A discovered assumption underlying the plan is wrong.
- The scope has expanded by more than approximately 20% beyond the original request.
- Two consecutive execution steps fail unexpectedly and the root cause points to a planning gap.

## Examples

**Input**: "Add a rate-limiting feature to the API."

- Phase 1: Goal stated as "rate-limit all POST endpoints to 100 req/min per user; internal service calls excluded."
- Phase 1.5: Requirements qualification — problem and value confirmed; scope boundaries explicit; human asked whether internal service calls need a separate bypass mechanism (edge case); all in-scope items pass 3-check review.
- Phase 2: Discovers existing middleware and an in-progress PR touching the same path. Human asked about each before drafting.
- Phase 3: Round 1 — check (a) finds the plan references a `RateLimiter` class not yet decided on; human asked to clarify. Round 5 — all checks return trivial answers; convergence reached.
- Phase 4: Sequence diagram generated. Human confirms it matches their model.
- Phase 5: Angle 8 (second-order effects) reveals that rate-limiting breaks an existing test suite that sends rapid sequential requests; human decides to add a test bypass header. Angle 9 (steelman) surfaces that Redis dependency adds operational complexity; human accepts the trade-off.
- Phase 6: All items checked. Execution approved.

**Input**: "Write operator documentation for the conveyor belt system."

- Phase 5, angle 10 (output dry runs): Scenario 1 — "An operator needs to restart the belt after an emergency stop at midnight." The draft plan has no emergency stop section; human asked whether to add it. Scenario 3 — "Operator reading on a mobile phone." Human asked whether a condensed quick-reference card is needed alongside the full manual.

**Input**: "Add input validation to the user registration endpoint."

- Phase 2: Quality Verification Strategy lists: unit tests for each validation rule (Jest), integration test for the full registration flow, ESLint + TypeScript tsc. Unverified References lists: `zod` library — unverified; verification step: `npm list zod`.
- Phase 3, check (i): agent scans plan and finds `zod` schema API usage not confirmed — added to Unverified References. Check (h): unit tests cover each validation rule with exact command `npm test -- --testPathPattern=registration`.
- Phase 6: Quality Verification Strategy checked; `zod` listed as unverified with first-step `npm list zod` before any schema code is written.

## Edge Cases

- **Agent that insists it knows the answer**: Do not skip any phase because the agent expresses confidence. Confidence is not a substitute for consistency checks.
- **Diagram cannot be generated**: Describe the flow in a plain-language walkthrough step by step. The intent of Phase 4 is to externalize the plan's structure — the medium is secondary.
- **Scope change discovered mid-planning**: If Phase 3 or Phase 5 reveals that the scope must change significantly, restart from Phase 2 with the revised scope. Do not patch the plan incrementally without a full re-check.
- **Human is unavailable for a step**: Note the unanswered question explicitly in the plan. Do not proceed past that point until the human responds.

## References

- [`agentme-edr-012`](../../012-continuous-xdr-enrichment.md) — Continuous XDR enrichment policy
- [`agentme-edr-501`](../../../governance/501-project-quality-standards.md) — Project quality standards
- [`agentme-edr-017`](../../017-skill-testing.md) — Skill testing mandate
