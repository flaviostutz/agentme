---
name: 151-refine-user-story
description: >
  Refine, elaborate, study or develop the contents of a user story used to create a unit of work
  for an agile team. Use when you need to write, refine, clarify requirements, ask follow-up
  questions, cover edge cases, and split large requests into vertical slices so they are clear,
  complete, and ready for implementation.
metadata:
  author: flaviostutz
  version: "4.0"
---

## Overview

Turns a vague request or rough draft into an implementation-ready user story by running a structured 9-phase refinement process: establishing plan context and gathering external information to ground the analysis (Phase 1), analysing the request and qualifying requirements with a scope size check (Phase 2), researching existing context and drafting a story skeleton (Phase 3), checking consistency and scope completeness (Phase 4), validating visually with a user journey diagram (Phase 5), challenging from 9 user-perspective angles (Phase 6), challenging from 8 implementer-perspective angles (Phase 7), producing a final ready-to-implement story with a readiness checklist (Phase 8), and running a final readiness double-check (Phase 9).

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

**Phase navigation rule**: Governs loop control, convergence, and phase transitions across all phases:
- **Loop**: within each phase, loop asking questions until convergence or Skip. Convergence means the last 2 consecutive rounds produced only single-sentence answers with no new issues surfaced — do not stop on a round count alone; stop only when checks genuinely have nothing left to surface. Explicit human confirmation that the phase output is correct also counts as convergence.
- **Checklist gate**: after convergence, verify any completion checklist — if items are unmet, ask those specifically (targeted questions, not a full loop restart) before advancing.
- **Skip**: when the human invokes Skip, stop the loop, record all open items as named Deferred Risks (visible in the story, carried forward), suspend the hard gate for those items, and advance immediately.
- **Backtracking**: when any finding touches goals, scope, requirements, or assumptions from an earlier phase, explain to the human which phase is affected and why, and re-run that phase's loop focused on the new information; backtracking overrides any prior skip; concerns about the initial request understanding re-route to Phase 2 Step 1 (Classify and restate).

**Phase gate UI rule**: At every point where the skill requires human confirmation before advancing to the next phase — any instruction that says "Wait for the answer before continuing" or requires the human to confirm convergence — use `vscode_askQuestions` to present the gate. Always include a clearly labeled recommended option such as "Continue to Phase N — [phase name]" and allow free text so the human can provide corrections, ask follow-up questions, or redirect instead. Do not present a text prompt alone and wait for freeform input — the human must always have a visible, labeled UI option to advance.

**Context Probe rule**: In every phase, whenever you encounter a gap, uncertainty, or ambiguity that external documentation, specifications, URLs, screenshots, or other artifacts could resolve — ask the user proactively. Tie the ask to the specific gap identified (e.g. *"I need to understand how the current deletion confirmation works — do you have a design spec or screenshot?"*). Never ask generically ("do you have any docs?"). The user can always skip; skipped probes are recorded as "Context: not provided for [topic]" and do **not** count as unresolved decisions under the Hard Gate. Do not re-probe gaps already covered by the Context Summary from Phase 1.

---

### Phase 1: Plan Document Context & Context Enrichment

Before beginning refinement, determine the working context and where output will be saved.

**Inline reference — Epic / Feature / User Story structure** (self-contained; no external policy file required to run this skill):
- **Epic** — A plan document at `[scope]/bdrs/operations/plans/NNN-epic-slug.md`. Represents a group of features toward a well-defined objective (1–12 months). Heading: `# [scope]-bdr-plan-NNN: [Epic Title]`.
- **Feature** — A `### Milestone N: [Feature Name]` section inside the epic plan. One Milestone per Feature. Duration: 2 weeks – 6 months.
- **User Story** — A key task inside a Milestone, always as a link: `- [Brief description]{.assets/userstory-NNN-slug.md}`. Pending stories append ` — pending` to the link text and have `**Status:** to-be-refined` in the file. Refined stories have the full title. Duration: < 2 weeks; stories exceeding this MUST be split.
- **User story detail file** — `.assets/userstory-NNN-slug.md` inside the epic plan's `.assets/` folder. NNN restarts at 001 per epic. Filenames always lowercase.

**Step 1 — Detect XDRS scope**

Scan the workspace for a `.xdrs/` directory. Proceed to Step 2a, 2b, or 2c based on what is found.

**Step 2a — Plan document explicitly provided or referenced:**
1. Parse all `### Milestone` sections (Features) and collect all task entries that link to `.assets/userstory-*.md` files.
2. For each linked file, read it and check for `**Status:** to-be-refined`. Collect only those as pending stories.
3. Use `vscode_askQuestions` to list all pending stories (by their link text and file name) plus a "New story — I will describe it" option.
4. If the user picks a pending story:
   - Read the placeholder file. Extract the NNN and slug from its `**Story ID:**` line. Carry any notes, context, or related-story links from the placeholder into Phase 1 Step 3 (Context Enrichment) as starting context.
   - Use the placeholder's title and notes as the subject for Phase 2.
5. If the user picks "New story", ask which Milestone to place it in; offer to add the Milestone if it does not exist. The slug and NNN for the new story are assigned in Phase 8.

**Step 2b — XDRS scope found but no plan document provided:**
1. Search for files matching `*/bdrs/operations/plans/*-epic-*.md`.
2. Use `vscode_askQuestions` to ask the user to: pick an existing epic plan, create a new epic plan, or start fresh (no plan context).
3. If an existing plan is picked, proceed as Step 2a.
4. If **create a new epic plan** is chosen, run a guided Q&A using `vscode_askQuestions` to collect: Epic Title, one-sentence objective, Expected end date (YYYY-MM-DD), and name of the first Feature/Milestone. Then:
   - Derive the epic slug by kebab-casing the title, keeping at most 7 words.
   - Determine the epic NNN by scanning `[scope]/bdrs/operations/plans/` for existing plan files and using the next available number (start at 001).
   - Create the file at `.xdrs/[scope]/bdrs/operations/plans/NNN-epic-slug.md` with the required `_core-adr-policy-007` sections:
     ```markdown
     # [scope]-bdr-plan-NNN: [Epic Title]

     ## Executive Summary
     [To be completed.]

     ## Context and Problem Statement
     [one-sentence objective collected above]

     ## Proposed Solution
     [To be completed.]

     Expected end date: YYYY-MM-DD

     ## Milestones

     ### Milestone 1: [First Feature Name]
     Owner: TBD
     Due date: TBD

     **Key tasks:**
     ```
   - Proceed as Step 2a (the new plan is now the active plan context, Milestone 1 is the target).
5. If "start fresh" is chosen, continue to Phase 1 Step 3 (Context Enrichment) with no active plan context; Phase 8 will handle deferred stories.

**Step 2c — No XDRS scope found:**
Skip Phase 1 Steps 1–2. Proceed directly to Phase 1 Step 3 (Context Enrichment). Phase 8 will ask where to save output.

**Step 3 — Context Enrichment**

Before beginning analysis, gather factual context about the system, process, or domain the story touches. This step runs for all Phase 1 paths (2a, 2b, 2c).

1. **Quick request analysis** *(internal — not surfaced verbatim to the user)*: read the story request and perform a rapid 3–5 bullet read to identify: domain/system type (CRM, e-commerce, auth, internal tool, etc.); key entities mentioned (contacts, leads, orders, users…); type of operation (CRUD, integration, notification, UI change…); any named systems, teams, or technologies. Used solely to generate targeted questions; NOT the full Phase 2 analysis.

2. **Auto-discovery**: scan the workspace for signals — source code folders, documentation files (`.md`, `.pdf`, `.txt`), XDRS decisions, prior user stories (`.assets/userstory-*.md`), README files, API specs, test files, diagrams. Summarize findings in 3–5 bullet points (do not dump raw content). Include any notes or context carried forward from Step 2a/2b placeholder files.

3. **Generate targeted context questions** derived from the quick analysis and auto-discovery. Questions must be specific — derived from what the request implies, not generic boilerplate:
   - **Domain-specific probes** (examples: *"This looks like a CRM — is it? Can you point me to the Leads screen documentation or any existing specs?"* / *"Do you have screenshots, mockups, or a recording of the current flow?"* / *"Is there an existing implementation to reference? If so, point me to the relevant folder or file."*)
   - **Business intent / artifact probes** (examples: *"What business outcome is expected from this change? Are there OKR or KR documents that describe the goal?"* / *"Were there any user interviews or stakeholder discussions about this need? A transcript or notes would help."*)
   - ≤5 questions per `vscode_askQuestions` call; freeform answers preferred; use `options` only for bounded choices.

4. After answers, auto-read any provided files/URLs and summarize them (factual only, each item labeled with its source). If the answers surface new questions that external info could address, generate a new targeted round and loop. Apply the Phase navigation rule (convergence = last 2 consecutive rounds produced no new actionable information).

5. Present the convergence gate via `vscode_askQuestions`:
   - **"Context is sufficient — continue to Phase 2"** *(recommended when meaningful context has been gathered)*
   - **"Add more context"** (free text) — record and loop back to step 4
   - **"Skip — no additional context available"** — record `Context: none available` and proceed

6. Compile the **Context Summary**: a labeled bullet list of all gathered information, each item attributed to its source (e.g. `**Source:** workspace/README.md — describes the existing Contact entity model`). Carry this summary into all subsequent phases.

**Hard constraint**: never invent or synthesize context from the story description alone. If nothing was found and the user skips, record `Context: none available.`

---

**Plan context record:** note the active plan file path (or none), the target Milestone name, and the Context Summary from Step 3; carry these into Phase 8.

---

### Phase 2: Request Analysis & Requirements Qualification

#### Step 1 — Classify and restate

1. Announce that you are activating the refine-user-story skill. State the story goal in one sentence: what the user wants to accomplish and what value it should deliver.
2. **Classify the input.** Decide whether the input is a vague request, partial draft, or near-complete story. State the classification explicitly.
3. **Restate current understanding** in 2–3 lines, drawing on the Context Summary from Phase 1 when present.

#### Step 2 — Requirements loop

Loop asking questions across the 6 areas below until convergence. Apply the Phase navigation rule. A detailed or well-structured input does NOT exempt you from the question loop — treat apparent completeness as a signal to look harder for hidden ambiguities.

**Apply Context Probe rule** throughout this step: whenever a gap in any area could be resolved by an external document, spec, URL, screenshot, or artifact not yet in the Context Summary, ask for it specifically.

| Area | Questions to resolve |
|---|---|
| Problem and value | What problem is being solved? Who benefits? What user or business value should exist after the change? |
| Scope | What behavior is explicitly in scope? What is explicitly out of scope? What should remain unchanged? |
| Requirements | What must the system do? What inputs, outputs, or contracts matter? What constraints shape the solution? |
| Flow and interactions | What is the main end-to-end flow? Which actors, systems, or interfaces are involved? Are there state transitions or lifecycle rules? |
| Edge cases | What unusual but valid scenarios must work? What invalid inputs or error paths must be handled? What happens on retries, duplicates, partial failure, or missing data? |
| Dependencies | What upstream or downstream systems affect the change? Are there required approvals, sequencing, or external decisions? Does any migration, rollout, or compatibility concern exist? Is there a real named person — a domain expert, business owner, or decision maker — who can be contacted during implementation if questions arise? (Capture name and role only when they are an actual known person; never fabricate a contact.) |

**Interface and integration scan** (apply Context Probe rule here): before closing Step 2, explicitly check for: external APIs invoked (endpoints, HTTP methods, request/response payloads, authentication, behavior); input/output data (field names, types, formats, valid values, meanings, constraints); documentation links (specs, API references, runbooks); contact names and roles (owners of external systems or business rules); process rules or business logic tied to the story. For any missing detail, ask targeted questions or apply the Context Probe rule to request external sources.

Do not proceed to Step 3 while any open decision, unresolved assumption, or ambiguous rule exists. If you find yourself wanting to write "or X" / "TBD" / "to be documented" anywhere, that is a sign you skipped a question.

#### Step 3 — Scope size evaluation

Assess whether the request as currently scoped is suitable for a single focused story. A request is likely too large if two or more of the following are true (a single criterion alone is not sufficient):
- More than approximately 10 distinct scope items resulted from questioning.
- Multiple independent user outcomes each of which stands alone as releasable value.
- Three or more qualitatively different user flows each requiring substantial independent analysis.
- Multiple distinct actor groups experiencing the feature in non-overlapping ways.

If too large, propose a split into 2–4 vertical slices where each slice delivers independent end-to-end releasable value. Present the proposed split with a brief rationale for each slice's boundary. Use `vscode_askQuestions` with:
- **"Accept split — start refining [Slice 1 name]"** (recommended) — restart from Phase 2 with the narrower scope; record all deferred slices in a **Deferred Stories** list so they can be tracked for future runs.
- **"Keep original scope — continue"** — proceed without splitting; note the human explicitly accepted the larger scope.
- Free text to adjust the proposed slice boundaries before deciding.

If the human accepts the split, restart the entire process from Phase 2 with the new narrower scope.

#### Step 4 — Feature summary and phase gate

Present a brief feature summary — a short bullet list of what will be built or changed, written in plain language the requester can validate at a glance.

Then use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
- **"Continue to Phase 3 — Context & Story Draft"** (recommended when requirements are clear and agreed)
- **"Re-run Phase 2 — deeper pass"** — repeat all steps with fresh eyes, prioritising areas not yet fully explored, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 2 in full treating the comment as additional context, then re-present this gate.

---

### Phase 3: Context & Story Draft

1. **Build on the Context Summary** from Phase 1 Step 3. Do not re-scan the workspace for what is already captured there; instead focus on story-specific patterns, prior decisions, analogous implementations, and established conventions not yet covered in the Context Summary. Apply the Context Probe rule: if this deeper pass surfaces a partial or missing artifact (a referenced doc that was not provided, a prior story that links to an external spec), ask for it specifically. Apply the Phase navigation rule.
2. **Draft a story skeleton** — a rough but structured version of the output template — incorporating context found. The skeleton must include at minimum: Title, User Story, Scope, and Acceptance Criteria as first drafts (not final).
3. Present the draft skeleton and use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
   - **"Continue to Phase 4 — Consistency & Scope Review"** (recommended when the draft matches intent)
   - **"Re-run Phase 3 — explore deeper"** — repeat the research pass looking for context, decisions, or constraints not yet surfaced, then re-present this gate.
   - **"Add a comment or correction"** (open box) — re-run Phase 3 treating the comment as additional context, then re-present this gate.
4. If the draft reveals gaps or contradictions, return to Phase 2 before continuing.

---

### Phase 4: Consistency & Scope Review

#### Step 1 — Consistency check

Look for contradictions between goal, scope, and acceptance criteria:
- Cross-check the evolving story against any context provided by the user.
- If workspace docs or code are relevant, inspect them to confirm terminology, constraints, and affected parts.
- Verify: requirements don't contradict each other; acceptance criteria prove the requirements; terminology is consistent; no assumptions remain unresolved.

Ask questions about all findings. Apply the Phase navigation rule.

#### Step 2 — Scope item review

For every item listed under **Scope**, loop through these five checks before moving on:

| Check | What to look for |
|---|---|
| Completeness | Is the item fully described? Are inputs, outputs, triggers, and expected behavior clear enough for autonomous implementation without guessing? |
| Edge cases | Does this item have unusual paths — errors, empty states, boundary values, retries, or concurrency — not yet captured? Add any found. |
| Technical constraints | Does this item imply or conflict with an existing technical constraint (e.g. API contract, data model, performance budget, auth model)? Flag any that must be honored. |
| Missing attachments | Would a screenshot, mockup, flow diagram, or reference document make this item unambiguous? If so, apply the Context Probe rule and ask for it explicitly before proceeding. |
| Detailed Specs | Did refinement surface any external APIs, data contracts, documentation links, or contact names relevant to this item? If yes, are they fully recorded? If anything is missing, ask targeted questions. If none apply, note it explicitly so the N/A can be recorded in the output. |

Do **not** advance while any scope item fails a check. If a check reveals a new gap, return to Phase 2 and ask the follow-up question.

After all checks converge, use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
- **"Continue to Phase 5 — Visual Validation"** (recommended when all items pass all checks)
- **"Re-run Phase 4 — deeper pass"** — repeat all consistency and scope checks with fresh eyes, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 4 treating the comment as additional context, then re-present this gate.

---

### Phase 5: Visual Validation

1. **Choose a diagram type** that best externalizes the user journey for this story:
   - **Flowchart** — step-by-step user decision flows and happy / error paths
   - **Sequence diagram** — interactions between user and system over time
   - **State diagram** — lifecycle states and transitions visible to the user
   - **Activity diagram** — parallel user and system activities

2. **Generate the diagram.** The diagram must show at minimum: the actor, the trigger, the main steps, the outcome, and at least one error or edge path.

3. Use `vscode_askQuestions` (per Phase gate UI rule) to ask: "Does this diagram match your mental model of the user journey?" Present at least these options:
   - **"Continue to Phase 6 — User-Perspective Challenge"** (recommended when the diagram matches)
   - **"Re-run Phase 5 — try a different diagram type"** — choose a different type or regenerate with a different framing, then re-present this gate.
   - **"Add a comment or correction"** (open box) — re-run Phase 5 treating the comment as additional context, then re-present this gate.

4. If the diagram reveals gaps or inconsistencies not yet surfaced, return to Phase 4 before continuing.
5. **Save the confirmed diagram.** Write the Mermaid source to `.assets/userstory-NNN-slug-journey.md` inside the plan's `.assets/` folder (when a plan doc is active) or to `userstory-journey.md` at the workspace root otherwise. Record this path to include as a diagram attachment in `## Attachments` when Phase 8 writes the story file.

---

### Phase 6: User-Perspective Challenge

For each angle, apply the following protocol. The Phase navigation rule (convergence, Skip, Backtracking) governs loop control on top of this protocol.

1. Generate 10–20 specific questions about that angle **in the context of this story** (grounded in what has been gathered, not generic).
2. Attempt to answer each question from the current story contents.
3. For every question that cannot be answered, is unanswered, or reveals a gap or inconsistency: elaborate the finding and ask the user via `vscode_askQuestions`.
4. Apply the Context Probe rule: if any gap could be resolved by an external spec, interview transcript, design doc, or other artifact, ask for it specifically.
5. Only mark the angle complete when all questions are answered or explicitly deferred as named risks.
6. Do not resolve choice points unilaterally.

**1. User journey completeness**
Does the story cover the full user journey from trigger to completion, including what happens immediately after? Identify any step the user must take that is not covered by the story.

**2. Pain point alignment**
Does solving this actually address the real underlying pain, or does it address only a surface symptom? What is the root cause the user is experiencing, and does the story eliminate it?

**3. Emotional experience**
How does the user feel at each touchpoint in the journey — when initiating, waiting, receiving feedback, encountering errors? Are frustration, confusion, or delight anticipated and addressed?

**4. Mental model match**
Does the interaction described in the story match how users naturally expect the system to behave? Where will users be surprised, confused, or forced to adapt their mental model?

**5. Value clarity and timing**
Is the value the user receives immediate and perceivable, or is it delayed or indirect? Will users understand why this feature helps them, or does its value require explanation?

**6. Accessibility and inclusion**
Can users with different abilities (visual, motor, cognitive), language backgrounds, device types, or technical literacy levels complete this story's user journey successfully?

**7. Edge user scenarios**
How are these user profiles served: a first-time user unfamiliar with the feature; a power user who already knows what they want; a user trying to recover from an error; a user under time pressure? Are all adequately served?

**8. Trust and safety**
Are there data privacy, error recovery, or safety implications from the user's perspective? Will users trust the system's behavior during this interaction, especially for error states and data handling?

**9. Learnability**
Can a new user complete this story's scenario without reading documentation? What is the first-use experience? Are there onboarding moments, tooltips, or self-describing UI elements needed?

After all 9 angles converge, use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
- **"Continue to Phase 7 — Implementer-Perspective Challenge"** (recommended when all angles have converged and no open questions remain)
- **"Re-run Phase 6 — deeper pass"** — repeat all angles with fresh challenge questions, prioritising angles not yet fully explored, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 6 treating the comment as additional context, then re-present this gate.

---

### Phase 7: Implementer-Perspective Challenge

For each angle, apply the following protocol. The Phase navigation rule (convergence, Skip, Backtracking) governs loop control on top of this protocol.

1. Generate 10–20 specific questions about that angle **in the context of this story** (grounded in what has been gathered, not generic).
2. Attempt to answer each question from the current story contents.
3. For every question that cannot be answered, is unanswered, or reveals a gap or inconsistency: elaborate the finding and ask the user via `vscode_askQuestions`.
4. Apply the Context Probe rule: if any gap could be resolved by an external spec, API reference, interface contract, or other artifact, ask for it specifically.
5. Only mark the angle complete when all questions are answered or explicitly deferred as named risks.
6. Do not resolve choice points unilaterally.

**1. Verifiable acceptance criteria**
Can every acceptance criterion be independently tested by a developer without ambiguity? Is "done" unambiguous for each item, with no subjective interpretation required? Are criteria specific enough to write automated tests against?

**2. Error and edge paths**
Are all failure modes, invalid inputs, retries, empty states, and boundary values explicitly handled? Does the story cover what happens when things go wrong — not only the happy path? Are error responses and recovery flows described?

**3. Blocking dependencies & startability**
Is any external team decision, environment access, infrastructure change, or third-party system onboarding required before work can start? Is it clear when this story can be picked up — are there ordering constraints relative to other stories, milestones, or external events? All blocking items must be either resolved or explicitly deferred as named risks with the expected resolution date or condition.

**4. Functional dependencies**
What external APIs, systems, services, or teams does this story depend on to function — not necessarily blocking start, but required for the feature to work? For each: is the integration contract (endpoints, auth, data format, SLAs, contact) documented? Are there known risks, rate limits, reliability concerns, or ownership questions that the implementer needs to know?

**5. Non-functional requirements**
Are performance, scalability, availability, and accessibility expectations stated? If none apply, is that explicitly noted? (Mark N/A if not applicable.) Any measurable NFR discovered here (e.g. "response time < 2s", "supports 50 concurrent users") MUST also appear as a verifiable item in `## Acceptance Criteria` — recording it only in `## Constraints` is not sufficient.

**6. Security implications**
Are authentication model, authorization rules, sensitive data handling, and input validation concerns identified and addressed? Are any known threat vectors or compliance constraints noted? (Mark N/A if not applicable.)

**7. Independent releasability**
Can this story be deployed to production without requiring another story to be completed first? If a hard coupling exists, is it explicitly stated and justified?

**8. Implementer dry run**
Simulate an engineer receiving this story cold — no prior context, no verbal briefing. Walk through their experience step by step: reading the title and user story, scanning the scope, reading the acceptance criteria, checking the detailed specs, looking at external system references, identifying where to start. At each step ask: would they get stuck? Would they need to ask a question? Would they make a wrong assumption? Flag every point where the story is insufficient to let them start and make progress without outside help. This is the final integration check: if any of angles 1–7 left gaps, they will surface here.

After all 8 angles converge, use `vscode_askQuestions` (per Phase gate UI rule) with at least these options:
- **"Continue to Phase 8 — Story Output & Readiness"** (recommended when all angles have converged and no open questions remain)
- **"Re-run Phase 7 — deeper pass"** — repeat all angles with fresh challenge questions, prioritising angles not yet fully explored, then re-present this gate.
- **"Add a comment or correction"** (open box) — re-run Phase 7 treating the comment as additional context, then re-present this gate.

---

### Phase 8: Story Output & Readiness

Before producing the final story, verify ALL items in the checklist below. If any item cannot be checked, return to the relevant phase and resolve it first.

- [ ] Problem, intended user value, and beneficiary unambiguous.
- [ ] Scope boundaries explicit (in / out / unchanged).
- [ ] Requirements, flow, edge cases, dependencies known or explicitly deferred as named Deferred Risks.
- [ ] Every in-scope item passes the 5-check review (completeness, edge cases, technical constraints, attachments, detailed specs) with no open findings.
- [ ] No contradictions between goal, scope, and acceptance criteria.
- [ ] Story is either one thin vertical slice or a clean set of split slices, each delivering complete releasable value.
- [ ] All 9 user-perspective challenge angles (Phase 6) and all 8 implementer-perspective angles (Phase 7) completed with human input received for every ambiguity and subjective decision.
- [ ] Diagram generated and confirmed by the human.
- [ ] No unresolved human questions outstanding.
- [ ] For every in-scope item where integration or interface details exist: `## Detailed Specs` is populated or explicitly marked N/A; the story contains enough detail to begin architecture or implementation without further business clarification.

Once all items are checked or explicitly marked N/A, **produce the final result** using the output template below.
- If one story is feasible, output one refined story.
- If the work is too large, output only the split stories using the same template.
- Acceptance criteria must be a plain checklist.

If any stories or features were placed in the **Deferred Stories** list during Phase 2 Step 3 (scope split), or any items were recorded as named **Deferred Risks** during a Skip, present a **Deferred Items summary** — a bulleted list of each deferred item with a one-line description of what it covers and why it was deferred.

**When an XDRS plan doc is active** (Phase 1 selected or created a plan): skip this prompt entirely. Deferred slices are handled as placeholder files with task links in the plan doc by the Plan document integration section below.

**When no XDRS plan doc is active**: use `vscode_askQuestions` with:
- **"Save to BACKLOG.md"** (recommended) — append the list under a `## Deferred Stories` heading in `BACKLOG.md` at the workspace root (create the file if it does not exist), so the items can be planned for future refinement runs.
- **"Save to a different file"** (open box) — human specifies the file path; append there instead.
- **"Skip — do not save"** — proceed without saving.

This step is skipped if no stories were deferred and no Deferred Risks were recorded.

### Plan document integration

After producing the final story output, persist it according to the active plan context from Phase 1.

**When an XDRS plan doc is active (Phase 1 selected or created a plan):**
1. Determine the NNN and slug for the story detail file:
   - **Placeholder story** (Phase 1 picked a pending story): extract the NNN and slug from the placeholder file's `**Story ID:**` line. Reuse them for the refined file.
   - **New story** (Phase 1 chose "New story" or a new epic was created): use the next available NNN in the plan's `.assets/` folder (list existing `userstory-NNN-*.md` files, increment the highest; start at 001 if empty). Derive the slug by kebab-casing the refined `## Title`, keeping at most 7 words, e.g. `save-payment-method-future-checkouts`.
2. Write the refined story as `.assets/userstory-NNN-slug.md` inside the plan's `.assets/` folder using the output template, including the `**Story ID:** userstory-NNN-slug` line at the top (no `**Status:**` line — absence of the status field indicates a refined story).
3. In the plan doc, update the task entry link text in the active Milestone: change `[Brief description — pending]` to `[Refined Story Title]` (keep the same `.assets/userstory-NNN-slug.md` path). For new stories, insert a new task entry `- [Refined Story Title]{.assets/userstory-NNN-slug.md}`.
4. When splitting: for each non-chosen slice, create a placeholder file at `.assets/userstory-NNN-slug.md` containing:
   - `**Story ID:** userstory-NNN-slug`
   - `**Status:** to-be-refined`
   - A `## Title` with the preliminary description of the slice.
   - A `## Notes from intake` section with any relevant context captured in this session: split rationale, relationship to the current story, any API or business details already known.
   - A `## Related` section linking to the current story being refined.
   Assign NNNs sequentially after the highest existing one in `.assets/` (the current story's file already written by step 2 counts as existing). Insert a task entry `- [Slice description — pending]{.assets/userstory-NNN-slug.md}` in the same Milestone (or a new Milestone if the split reveals a distinct Feature). Do NOT offer BACKLOG.md for deferred slices.
5. Add a back-link to the epic plan at the bottom of the story detail file: `**Epic plan:** [NNN-epic-slug.md]{../NNN-epic-slug.md}` (the `../` resolves from `.assets/` up to `plans/`).

**When no XDRS plan doc is active ("start fresh" or no XDRS scope):**
- Ask the user where to save the refined story (default: `userstory-NNN-slug.md` at workspace root).
- If split/deferred stories exist, use `vscode_askQuestions` to ask whether to add them to an existing epic plan, create a new epic plan, or save to `BACKLOG.md`. Apply the chosen action.

### Output Template

```
**Story ID:** userstory-NNN-slug

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

## Constraints
[optional — max 30 words. Any rule, technology, regulatory, or business constraint that must be respected.]
- [constraint]

## Detailed Specs
[Required when any API, integration, or data detail was discovered. Mark N/A if none.
 A story lacking sufficient detail here is not ready for implementation.]
- [External API / integration: endpoint, method, payload, auth, behavior]
- [Data field: type, format, valid values, meaning, constraints]
- [Doc link: URL or file path — what it covers]
- [Contact: name/role — what they own or can clarify]
- [Process rule or business constraint not captured in Constraints above]

## Acceptance Criteria
[required — max 50 words. Verifiable checklist confirming the story is done.]
- [ ] [verifiable outcome]

## Attachments
[highly desirable — screenshots, mockups, or diagrams illustrating the feature.]
- [attachment]

**Epic plan:** [NNN-epic-slug.md](../NNN-epic-slug.md)
*(omit when no XDRS plan doc is active)*
```

---

### Phase 9: Final Readiness & Size Re-Validation

Run two sequential checks. For any item in Check A not met in the final output, ask targeted questions and update the story before moving to Check B.

#### Check A — Readiness double-check

Verify all 14 items against the final story output:

**Story-level (6 items):**
1. **Vertical completeness** — story covers everything needed for end-to-end implementation; no half-slices that silently assume separate parallel work.
2. **Size** — one person can develop it in roughly 2–3 days.
3. **Engineering-ready detail** — sufficient for architecture and engineering detailing without further business clarification.
4. **External systems** — all external systems documented with APIs, endpoints, data fields, formats, constraints, and known concerns.
5. **User context** — user perspective present: what the user will do with this feature in their context, including concrete usage examples.
6. **Scope boundary** — explicit statement of what is included and what is not included in this implementation.

**Implementer double-check (mirrors Phase 7 angles 1–8):**
7. **Verifiable acceptance criteria** — every criterion independently testable; "done" is unambiguous.
8. **Error and edge paths** — failure modes, invalid inputs, empty states, and boundary values explicitly handled beyond the happy path.
9. **Blocking dependencies & startability** — all blocking items resolved or deferred; ordering constraints and startability conditions are explicit.
10. **Functional dependencies** — all external APIs, systems, services, and teams documented with integration contracts; known risks and reliability concerns noted.
11. **Non-functional requirements** — performance, availability, and accessibility expectations stated or explicitly N/A.
12. **Security implications** — auth model, data handling, and input validation addressed or explicitly N/A.
13. **Independent releasability** — can ship without waiting for another story; any hard coupling explicitly stated.
14. **Implementer dry run passed** — a cold engineer can read the story, understand where to start, and make progress without getting stuck or making wrong assumptions.
15. **Definition of Done** — ask whether the team has a DoD; if so, confirm that its implicit criteria (e.g. code reviewed, tests passing, deployed to staging) are either satisfied by the story's scope or explicitly noted as out of scope.

#### Check B — Size re-evaluation

Apply the same 4 criteria from Phase 2 Step 3. If two or more are met, the story is still too large.

- **Passes** → use `vscode_askQuestions` to confirm the skill is complete and the story is ready.
- **Too large** → propose 2–4 vertical slices with rationale. Use `vscode_askQuestions` with:
  - **"Accept split — start refining [Slice 1 name]"** (recommended) — restart from Phase 2 with the narrower scope; Phase 1 context is preserved; deferred slices follow Phase 2 Step 3 rules.
  - Free text to adjust the proposed slice boundaries before deciding.

---

## Examples

**Input:** "Add a search bar to the product page."

**Clarifying questions asked:** Who performs the search? What data is searched? Should results filter the current page or navigate elsewhere? What happens on no results?

**Output:** A refined story scoped to keyword search on product name and description, filtering the current product list in place, with an empty-state message when no results match, and no pagination changes in scope.

**Phase 6 example (angle 3 — Emotional experience):** "When search returns no results, the user may feel confused or assume the product doesn't exist. The story needs an empty-state message that reassures the user and offers a next action." → Question asked: "Should the empty state suggest alternative search terms or link to a 'browse all products' view?"

## Edge Cases

- **Input already contains detailed acceptance criteria**: do not skip the question loop; look harder for hidden ambiguities in scope boundaries and edge cases.
- **User refuses to answer a clarifying question**: note it as an unresolved assumption and do not produce output until it is resolved.
- **Request spans multiple independent user outcomes**: always split into separate vertical-slice stories rather than merging into one broad story.
- **Diagram cannot be generated**: describe the user journey in a plain-language step-by-step walkthrough. The intent of Phase 5 is to externalize the journey — the medium is secondary.

## References

- [`agentme-edr-012`](../../012-continuous-xdr-enrichment.md) — Continuous XDR enrichment policy
- [`agentme-edr-017`](../../017-skill-testing.md) — Skill testing mandate
- [`agentme-bdr-401`](../../../../bdrs/operations/401-epic-feature-story-planning.md) — Epic/feature/user story planning structure (policy source for the inline reference in Phase 1)
