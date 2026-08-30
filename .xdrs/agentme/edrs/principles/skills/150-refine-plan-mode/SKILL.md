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
  version: "2.8"
---

## Overview

Ensures that every plan is deeply validated through iterative consistency checks, visual externalization, and multi-angle challenges before execution starts. The skill is not designed to make human work easier — its purpose is to identify precisely where human experience, feeling, and domain knowledge are irreplaceable, and to demand that input before moving forward.

**Questioning rule**: Ask questions about all findings proactively — skip only trivially obvious ones with no decision weight. Use `vscode_askQuestions` when available; ask at most 4–5 tightly related questions per call. Before each new round, explicitly state what territory has not yet been explored and will be the focus of this round (in structured phases such as Phase 4 or Phase 6, state which predefined check or angle you are covering next) — do not re-ask questions already addressed in previous rounds. Never self-resolve a choice point, and never produce output, plan sections, or decisions while any open decision, unresolved assumption, or ambiguity remains — embed nothing as 'or X / TBD / to be decided' — resolve through questions first. For findings with major impact on downstream users or consumers (breaking changes, behavior regressions, removals), do not ask — emit a prominently formatted **SEVERE WARNING** with a clear description of the impact and continue.

**Task tracking rule**: Use the todo list tool throughout this entire skill. Before starting each phase, create a todo for it and mark it in-progress. Mark it completed immediately when done. For Phase 4 (consistency checks), create a todo for each check (a–i) before beginning Phase 4 and mark each completed when that check individually converges. For Phase 6 (challenge angles), create a todo for each of the 9 angles before beginning Phase 6 and mark each completed after the human responds to any question raised, or immediately if no question was raised for that angle. An angle todo MUST NOT be marked complete if any decision was self-resolved without asking the human (per the Questioning rule) — if this is detected, flag it as a HITL violation, re-open the todo, surface the decision to the human as a clarifying question, and only mark it complete after the human responds. This ensures no check, round, or angle is silently skipped and no decision is self-resolved.

**Phase navigation rule**: Governs loop control, convergence, and phase transitions across all phases:
- **Loop**: within each phase, loop asking questions until convergence or Skip. Convergence means the last 2 consecutive rounds produced only single-sentence answers with no new issues surfaced — do not stop on a round count alone; stop only when checks genuinely have nothing left to surface. Explicit human confirmation that the phase output is correct also counts as convergence.
- **Checklist gate**: after convergence, verify any completion checklist — if items are unmet, ask those specifically (targeted questions, not a full loop restart) before advancing.
- **Skip**: when the human invokes Skip, stop the loop, record all open items as named Deferred Risks (visible in the plan, carried forward), suspend the hard gate for those items, and advance immediately.
- **Backtracking**: when any finding touches goals, scope, requirements, or assumptions from an earlier phase, explain to the human which phase is affected and why, and re-run that phase's loop focused on the new information; backtracking overrides any prior skip; Phase 1 concerns re-route to Phase 2 Step 1.

**Phase gate UI rule**: At every point where the skill requires human confirmation before advancing to the next phase — any instruction that says "Wait for the answer before continuing" or requires the human to confirm convergence — use `vscode_askQuestions` to present the gate. Always include a clearly labeled recommended option such as "Continue to Phase N — [phase name]" and allow free text so the human can provide corrections, ask follow-up questions, or redirect instead. Do not present a text prompt alone and wait for freeform input — the human must always have a visible, labeled UI option to advance.

## Instructions

### Phase 1: Activate Plan Mode

1. Switch to plan mode. Do not write, edit, or execute anything until the plan is fully validated through Phase 7.
2. State the goal in one sentence: what problem is being solved and what the expected outcome is.
3. State the scope boundaries explicitly: what is included and what is explicitly excluded.

### Phase 2: Requirements Qualification

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

### Completion criteria for Phase 2
Do not proceed to Step 5 until all are true:
- [ ] Problem, intended value, and beneficiary unambiguous.
- [ ] Scope boundaries explicit (in / out / unchanged).
- [ ] Requirements, flow, edge cases, dependencies known or explicitly deferred.
- [ ] Every in-scope item passes 3-check review with no open findings.

### Step 5 — Scope size evaluation
Assess whether the feature as currently scoped is suitable for a single focused planning and implementation run. A feature is likely too large if two or more of the following are true (a single criterion alone is not sufficient):
- More than approximately 10 distinct subsystems, components, or modules are affected.
- More than approximately 20 distinct in-scope items resulted from Step 4.
- The work spans 3 or more qualitatively different concerns each requiring substantial independent design effort (e.g., a new data model, a new public API surface, and a new CLI — all non-trivial).
- Multiple independent stakeholder groups or deployment environments are involved in distinct, non-overlapping ways.

If the feature qualifies as too large, propose a split into 2–4 coherent parts where each part is independently releasable or testable. Present the proposed split with a brief rationale for each part's boundary. Use `vscode_askQuestions` with:
- **"Accept split — start planning [Part 1 name]"** (recommended) — restart from Phase 1 with the narrower scope of the selected part; record all deferred parts in a **Deferred Features** list in the plan so they can be tracked for future runs.
- **"Keep original scope — continue"** — proceed without splitting; note the human explicitly accepted the larger scope.
- Free text to adjust the proposed part boundaries before deciding.

If the human accepts the split, restart the entire planning process from Phase 1 with the new narrower scope. The deferred parts are preserved in the Deferred Features list and will be surfaced again at the Phase 7 handoff gate.

Present a brief feature summary — a short bullet list of what will be built or changed, written in plain language the requester can validate at a glance. Then use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
   - **"Continue to Phase 3 — Research and Draft Plan"** (recommended when scope is clear and agreed) — proceed with research and drafting.
   - **"Re-run Phase 2: Requirements Qualification — deeper pass"** — repeat all steps with fresh eyes, prioritising areas not yet fully explored, then re-present this gate.
   - **"Add a comment or correction"** (open box) — re-run Phase 2 in full, treating the comment as additional context and constraints, then re-present this gate.

### Phase 3: Research, Dependencies, and Draft Plan

1. Research the existing context: relevant files, prior decisions, established conventions, and analogous patterns already in place.
2. For each contextual input, constraint, or dependency found (existing files, prior decisions, external systems, in-progress work by others), ask questions about all non-trivial items. For each dependency or context item, apply the Phase navigation rule: loop asking questions until that item converges before moving to the next. Only skip asking for trivially obvious or deterministic context items with no decision weight.
3. Draft a plan with ordered steps, items to create or modify, and a verification step at the end. The plan MUST include a dedicated phase for test generation and execution whenever applicable — this phase must appear as an explicit step in the ordered plan, not only in the verification section. It must specify: (a) what tests to create or extend (unit, integration, end-to-end, or manual); (b) the exact commands or manual steps to run them; (c) the expected outcome for each. Examples: "Generate unit tests for X and run `npm test` — expect all pass", "Run integration tests with `make test-integration` — verify no regressions", "Manually open the generated document and verify sections Y and Z look correct". If no automated or manual tests apply, explicitly state why and mark the phase N/A. The plan MUST also include two dedicated sections:
   - **Quality Verification Strategy**: (a) existing checks that must continue to pass; (b) new checks required for the task — for code: unit tests, integration tests, linting, type checking, dead code detection, security/dependency audit, schema/contract validation; for documents, analyses, and policies: proofreading, fact-checking, citation and link validation, policy compliance review, peer review, readability check; (c) exact executable steps or commands for each check; (d) what each check verifies. A plan without this section is incomplete.
   - **Unverified References**: any resource referenced in the plan but not verified during planning must be listed here as *"unverified — must verify before use"* with a concrete first-step verification. For code: file paths, function names, CLIs, library APIs (e.g., `which cmd`, `npm list pkg`). For documents and analyses: statistics, quotes, cited studies, named organizations or people, URLs, legal or regulatory references. This section is the primary defense against fabricated claims surfacing only at execution time.
4. Present the draft and use `vscode_askQuestions` (per Phase gate UI rule) to ask: "Does this draft match your intent? What verification checks exist today, and what new checks will confirm the key outcomes?" Present at least these options:
   - **"Continue to Phase 4 — Consistency Checks"** (recommended when no gaps remain) — advance.
   - **"Re-run Phase 3: Research, Dependencies & Draft Plan — explore deeper"** — repeat the research and drafting pass looking for context, dependencies, or constraints not yet surfaced, then re-present the gate.
   - **"Add a comment or correction"** (open box) — re-run Phase 3 in full, treating the comment as additional context and constraints, then re-present this gate.
   Wait for the answer before continuing.

### Phase 4: Iterative Consistency Checks

Run checks (a–i) sequentially. For each check: formulate 2–3 questions targeted at that check in the context of the current plan, attempt to answer by reasoning through evidence — this is not self-resolving. For anything unresolved or subjective, ask the human per the Questioning rule. Loop on each check until it fully converges before moving to the next check. Convergence for a check = last 2 consecutive exchanges on that check produced only single-sentence answers with no new issues surfaced (per Phase navigation rule).

Checks to run in order:

- **(a) Internal consistency**: Are there contradictions between steps? Do the scope boundaries align with the implementation steps?
- **(b) Dry run**: Walk through the plan with the most complex realistic scenario. Where does it break or leave gaps? During the dry run, execute all verification checks that already exist and are applicable to the context. Failing checks and missing coverage for planned changes are blockers — surface them immediately.
- **(c) Component consistency**: Do all elements of the plan work together as a coherent whole? Are there missing connections between parts?
- **(d) XDRS alignment**: Does this plan align with the relevant XDRS governing this area? Have the right policies been consulted?
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

After all checks (a–i) converge, use `vscode_askQuestions` (per Phase gate UI rule) to present the Phase 4 gate with at least these options:
- **"Continue to Phase 5 — Visual Consistency Validation"** (recommended when all checks have converged) — advance.
- **"Re-run Phase 4: Consistency Checks — deeper pass"** — restart all checks (a–i) with fresh eyes, prioritising angles and scenarios not yet explored, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 4 in full, treating the comment as additional context and constraints, then re-present this gate.

### Phase 5: Visual Consistency Validation

1. **Assess the plan's visual complexity** and select 1–5 diagram perspectives to generate. Use the following scale:
   - **1 diagram** — narrow, single-concern plan (one flow, one component, one decision path).
   - **2–3 diagrams** — moderate complexity: multiple interacting components, non-trivial flows, or a mix of structural and behavioral concerns.
   - **4–5 diagrams** — high complexity: multiple subsystems, multiple actor types, significant state or lifecycle concerns, or a plan that proved hard to reason about in Phases 3–4.

   For each perspective needed, choose the diagram type that best externalizes that aspect:
   - **Flowchart** — step-by-step decision flows and process branches
   - **Concept map** — ideas, relationships, and conceptual structure
   - **Dependency graph** — components and their dependencies
   - **Sequence diagram** — call flows, API interactions, and temporal order
   - **State diagram** — lifecycle states and transitions
   - **Activity diagram** — business workflows with parallel paths
   - **Entity diagram** — data models and relationships

   Do not repeat diagram types unless a second instance covers a meaningfully different scope or actor. Label each diagram with the perspective it externalizes (e.g. "Component dependencies", "Registration flow", "Session lifecycle").

2. **Generate all selected diagrams** in sequence, each with a one-line description of what it is meant to reveal.

3. Use `vscode_askQuestions` (per Phase gate UI rule) to ask: "Do these diagrams match your mental model of the solution? Is any important perspective missing?" Present at least these options:
   - **"Continue to Phase 6 — 9 Challenge Angles"** (recommended when the diagrams match) — advance.
   - **"Re-run Phase 5: Visual Consistency Validation — add or replace a diagram"** — add a missing perspective or replace one with a different type, then re-present this gate.
   - **"Add a comment or correction"** (open box) — re-run Phase 5 in full, treating the comment as additional context and constraints, then re-present this gate.

4. If any diagram reveals gaps or inconsistencies not yet surfaced, return to Phase 4 before continuing.

### Phase 6: Challenge from 9 Distinct Angles

Each angle is an analysis step. **For each angle:** formulate 5–10 challenge questions grounded in the current plan and broader context (codebase, prior decisions); reason through each surfacing evidence — not self-resolving; bring unresolved or subjective questions to the human per the Questioning rule; then run the angle's analysis. Run the angle and present findings. Batch questions from related angles into a single round when findings are related — batching questions is permitted, skipping analysis is not. Ask questions about findings. Only skip asking when a finding is trivially obvious and carries no decision weight. For findings with major impact on users, emit a **SEVERE WARNING** and continue without asking. Apply Phase navigation rule to each angle: ask questions about findings proactively; loop on that angle's findings until no new questions surface before marking the angle complete. Do not resolve choice points unilaterally — apply the Questioning rule.

**Scenario-to-test rule**: Across all angles — especially angles 5 (scenario runs), 6 (input coverage), and 7 (stress/failure) — continuously collect scenarios into the plan's Quality Verification Strategy as named test cases. Capture a scenario from each of the following categories whenever one is encountered during investigation:

| Category | When to add |
|---|---|
| **Gap** | Scenario reveals behaviour not yet covered by existing tests |
| **Challenging** | Hardest to reason about, required the most conditions to align, or exposed the deepest assumptions |
| **Happy flow** | The primary success path a typical user will follow; must always pass |
| **Complex flow** | Multi-step or multi-condition path that exercises several components together |
| **Edge case** | Valid but unusual input or state at the boundary of defined behaviour |
| **Model doubt** | Any case where the agent was uncertain whether the implementation would handle it correctly — add it regardless of outcome |
| **Regression** | A scenario that passed during planning but could silently break after future changes to the plan |
| **Adversarial / invalid** | Deliberately malformed, hostile, or out-of-contract input |
| **Smoke** | Minimal "does it work at all" check for the primary function — derived from feasibility analysis (Phase 4e) |
| **Integration** | Components connect and communicate correctly — derived from component consistency analysis (Phase 4c) |
| **Policy / contract compliance** | Behaviour matches a declared policy, interface contract, or external API shape — derived from XDRS alignment (Phase 4d) and unverified claims (Phase 4i) |
| **Assumption** | A planning assumption that must hold true at runtime — derived from pre-mortem analysis (angle 3) and unverified references |
| **Security** | No sensitive data exposed, no attack surface created, no OWASP violation — derived from security scan (angle 3) |
| **Side-effect / isolation** | Executing this feature leaves adjacent systems, files, and state unaffected — derived from second-order effects analysis (angle 4) |
| **Observability** | Failures and error states are detectable, logged, and produce actionable messages — derived from observability analysis (angle 9) |
| **Acceptance** | The originally requested feature or outcome is demonstrably delivered end-to-end — derived from faithfulness (angle 1), goal achievability (angle 2), and success criteria (angle 4) |

Name each test case as `<descriptive action or scenario> (<category>)` so the purpose is immediately readable after implementation without needing to look up the planning notes. The descriptive part should name the concrete scenario; the category in parentheses identifies why it was captured. Examples: `"Validate BOM-prefixed file (edge case)"`, `"glob pattern [invalid throws (adversarial/invalid)"`, `"10 000 files processed synchronously (stress)"`, `"CLI exits 0 when all files valid (acceptance)"`, `"readFileSync EACCES returns invalid result (integration)"`. Optionally append the source angle in brackets for full traceability: `"BOM-prefixed file (edge case) [12-22]"`. Show a sample of the most revealing scenarios as brief inline callouts during the analysis to make the depth of analysis visible without producing a wall of text.

#### Plan quality angles

**1. Prompt faithfulness**
Does the plan account for existing files, decisions, and constraints already in place? Does it contradict anything already established in the codebase, repository, or context?

**2. Goal achievability**
Is any step or decision in the plan interpretable in more than one way? Every ambiguity is a future mistake. List all ambiguous points and ask the human to resolve each one.

**3. Pre-mortem**
Does the plan or its output expose sensitive information, create privacy risks, or introduce misuse vectors? This applies to any task type: documentation, code, processes, data handling, communications. Ask the human about any non-trivial findings. For trivially obvious mitigations with no decision weight, state them and continue.

**4. Success criteria and falsifiability**
What changes as a side effect of executing this plan beyond the intended outcome? Does solving this problem create a new problem elsewhere — in adjacent systems, files, processes, or stakeholders? List the side effects. Ask the human whether the side effects are acceptable.

**5. Steelman the opposition**
Simulate 10 realistic usage scenarios of the expected output by its actual consumer. For each scenario, ask: "Does the output serve its consumer in this situation?" Use scenarios that cover typical use, edge cases, and at least two adversarial or failure cases.

Examples of scenario framing:
- If the output is operator documentation: "A worker needs to reset the machine at 2 AM — will they find the procedure in under 2 minutes?"
- If the output is an API: "A developer calling this endpoint with a malformed payload — what happens?"
- If the output is a business process: "An employee following this process on their first day — will they complete it without asking for help?"

Whenever a scenario reveals ambiguity or requires a subjective judgment, stop and ask the human a clarifying question. Do not resolve subjective decisions unilaterally.

**6. Output internal consistency**
Simulate 50–200 different inputs against the produced element with the goal of discovering edge cases, security issues, and unresolved discussion points not yet surfaced in earlier phases. Scale toward 200 when the feature has high input diversity (many argument types, branches, modes, or configuration axes) — use the lower end only for narrow, single-path features. These inputs are a breadth-forcing tool — not a pass/fail test. What counts as an "input" depends on the task type: for code/systems — function arguments, API payloads, config values; for documents/policies/processes — reader queries, usage scenarios, edge-case interpretations. Inputs must span typical, edge, boundary, invalid, adversarial, and combined cases. Add more inputs for each distinct branch or configuration axis the plan introduces — the more divergent paths exist in the logic, the more inputs are needed to cover them. For each, ask: does this reveal a new edge case, security risk, or ambiguity not already addressed? Surface all findings as questions to the human per the Questioning rule.

**7. Stress and failure conditions**
Enumerate 2–3 meaningfully different ways the goal could be achieved. For each alternative, describe the approach in 1–2 lines and compare it against the current plan on at least: implementation effort, reversibility, risk, and fit with existing context. The goal is to surface whether the current plan is the right approach or just the first one considered. Ask the human: which tradeoffs matter most, and does the current approach still win? If an alternative is clearly superior in the context, flag it prominently and ask the human to reconsider.

**8. Stakeholder perspective tour**
Review the plan for anything that could be cut, simplified, or deferred without losing essential value. For each candidate: what is it, why might it be unnecessary, and what is the risk of removing it? This is not the same as scope-creep detection (angle 1, which checks for additions) — this angle actively proposes reductions. Ask the human to confirm or reject each simplification candidate explicitly.

**9. Observability and failure recovery**
Ask: will someone who did not build this be able to understand, change, and extend it safely 6 months from now? For code: are responsibilities clearly separated, is there excessive coupling, are there undocumented assumptions baked into the implementation, are naming and structure consistent with the codebase conventions? For documents and policies: is the content organized so that a future editor can update one section without inadvertently invalidating another? Is the vocabulary stable and defined, or does it rely on context that may not survive contributor turnover? For processes: are the steps atomic and independently verifiable, or do they depend on unstated tribal knowledge? Identify the parts of the plan most likely to become a maintenance burden and ask the human whether the trade-off is acceptable.

After all 9 angles are complete, use `vscode_askQuestions` (per Phase gate UI rule) to present the Phase 6 gate with at least these options:
- **"Continue to Phase 7 — Pre-Execution Readiness"** (recommended when all angles are complete and no open questions remain) — advance.
- **"Re-run Phase 6: 9 Challenge Angles — deeper pass"** — repeat all 9 angles with fresh challenge questions, prioritising scenarios and inputs not yet explored, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 6 in full, treating the comment as additional context and constraints, then re-present this gate.

### Phase 7: Pre-Execution Readiness

Before approving execution, verify ALL items in the checklist below. If any item cannot be checked, return to the relevant phase and resolve it first.

- [ ] Consistency rounds converged (convergence signals met — last 2 rounds produced only single-sentence answers with no new issues) (per Phase navigation rule)
- [ ] All 9 challenge angles completed with human input received for every ambiguity and subjective decision
- [ ] Diagram generated and confirmed by the human
- [ ] No unresolved human questions outstanding
- [ ] Scope confirmed by the human with no silent expansions
- [ ] Any irreversible or high-impact steps have a mitigation or fallback noted
- [ ] Quality Verification Strategy defined in the plan with exact executable steps for all applicable check types (code: unit tests, integration tests, linting, static analysis; documents/analyses: fact-checking, link and citation validation, peer review, etc.)
- [ ] A dedicated test generation and execution phase is present in the ordered plan steps (or explicitly marked N/A with a reason)
- [ ] Verification checks executed during dry run and results reviewed — failures and coverage gaps resolved
- [ ] All high-risk unverified references (code or factual) listed in the Unverified References section with explicit first-step verification in the execution plan
- [ ] All scenarios from any phase or angle that revealed gaps, raised model doubt, or qualified for any category in the Scenario-to-test table have been added as named test cases to the plan's Quality Verification Strategy

Once all items are checked or explicitly marked N/A, present a **brief scenario summary** — a short bulleted list of the most significant scenarios discovered across all phases (aim for 5–10 entries), each showing: the angle or check that surfaced it, what it revealed, and what test case was added to the plan. This makes the depth of analysis visible before handoff.

If any features were placed in the **Deferred Features** list during Phase 2 Step 5 (scope split) or explicitly excluded from scope at any point, present a **Deferred Features summary** — a bulleted list of each deferred part with a one-line description of what it covers and why it was deferred. Then use `vscode_askQuestions` with:
- **"Save to BACKLOG.md"** (recommended) — append the list under a `## Deferred Features` heading in `BACKLOG.md` at the workspace root (create the file if it does not exist), so the user can plan future implementation runs from it.
- **"Save to a different file"** (open box) — human specifies the file path; append there instead.
- **"Skip — do not save"** — proceed without saving.
This step is skipped if no features were deferred.

Before the final gate, add a step to the implementation plan to produce a concise feature documentation file. Use `vscode_askQuestions` to ask:
- **"Save to README.md"** (recommended) — append the documentation to `README.md` in the feature’s directory (create if absent).
- **"Save to a different file"** (open box) — human specifies the file path.
- **"Skip — do not save"** — proceed without saving.

If the human chooses to save, the implementation plan must include a dedicated step to write the file. The content must be brief and practical — not exhaustive prose — covering only what is most useful for someone revisiting the feature later:
- One-paragraph description of what the feature does and why it exists.
- The diagram generated in Phase 5 (the one the human confirmed).
- Key design decisions that are non-obvious (3–6 bullet points max).
- A short summary of the main API or usage (CLI flags, HTTP endpoints, or equivalent).
- Links to relevant policies or EDRs consulted.

Then use `vscode_askQuestions` (per Phase gate UI rule) to present the final gate with at least these options:
- **"Hand off to implementation"** (recommended when all checklist items pass) — confirm the plan is ready and signal execution can begin.
- **"Re-run all phases again with different challenges"** — restart from Phase 1 using the current plan as context, generating fresh scenarios, stress tests, and challenge angles to stress-test the plan further before committing to implementation.
- Free text for any other concern or question.

Do not start execution to escape planning discomfort — only start when confidence is genuine and all items are verified.

**Test execution rule**: After implementation is complete, all tests defined in the Quality Verification Strategy must be run before the work is considered done:
- **Automated tests** (unit tests, integration tests, linting, type checking, coverage): run them directly using the exact commands defined in the plan. If any fail, fix the issue and re-run before proceeding.
- **Manual tests**: for each manual test step in the plan, guide the human explicitly — state what command to run or action to take, what to look at, and what the expected output or behaviour is. Wait for the human to confirm the result before moving to the next step. If the result doesn’t match, treat it as a failure and investigate before continuing.
- Do not mark the work done until every test — automated and manual — has a confirmed passing result.

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
- Phase 2: Requirements qualification — problem and value confirmed; scope boundaries explicit; human asked whether internal service calls need a separate bypass mechanism (edge case); all in-scope items pass 3-check review.
- Phase 3: Discovers existing middleware and an in-progress PR touching the same path. Human asked about each before drafting.
- Phase 4: Round 1 — check (a) finds the plan references a `RateLimiter` class not yet decided on; human asked to clarify. Round 5 — all checks return trivial answers; convergence reached.
- Phase 5: Sequence diagram generated. Human confirms it matches their model.
- Phase 6: Angle 4 (second-order effects) reveals that rate-limiting breaks an existing test suite that sends rapid sequential requests; human decides to add a test bypass header. Angle 5 (steelman) surfaces that Redis dependency adds operational complexity; human accepts the trade-off.
- Phase 7: All items checked. Execution approved.

**Input**: "Write operator documentation for the conveyor belt system."

- Phase 6, angle 5 (steelman): Scenario 1 — "An operator needs to restart the belt after an emergency stop at midnight." The draft plan has no emergency stop section; human asked whether to add it. Scenario 3 — "Operator reading on a mobile phone." Human asked whether a condensed quick-reference card is needed alongside the full manual.

**Input**: "Add input validation to the user registration endpoint."

- Phase 3: Quality Verification Strategy lists: unit tests for each validation rule (Jest), integration test for the full registration flow, ESLint + TypeScript tsc. Unverified References lists: `zod` library — unverified; verification step: `npm list zod`.
- Phase 4, check (i): agent scans plan and finds `zod` schema API usage not confirmed — added to Unverified References. Check (h): unit tests cover each validation rule with exact command `npm test -- --testPathPattern=registration`.
- Phase 7: Quality Verification Strategy checked; `zod` listed as unverified with first-step `npm list zod` before any schema code is written.

## Edge Cases

- **Agent that insists it knows the answer**: Do not skip any phase because the agent expresses confidence. Confidence is not a substitute for consistency checks.
- **Diagram cannot be generated**: Describe the flow in a plain-language walkthrough step by step. The intent of Phase 5 is to externalize the plan's structure — the medium is secondary.
- **Scope change discovered mid-planning**: If Phase 4 or Phase 6 reveals that the scope must change significantly, restart from Phase 3 with the revised scope. Do not patch the plan incrementally without a full re-check.
- **Human is unavailable for a step**: Note the unanswered question explicitly in the plan. Do not proceed past that point until the human responds.

## References

- [`agentme-edr-012`](../../012-continuous-xdr-enrichment.md) — Continuous XDR enrichment policy
- [`agentme-edr-501`](../../../governance/501-project-quality-standards.md) — Project quality standards
- [`agentme-edr-017`](../../017-skill-testing.md) — Skill testing mandate
