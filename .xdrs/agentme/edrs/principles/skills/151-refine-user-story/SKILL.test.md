---
skill: 151-refine-user-story
skill-version: "2.0"
---

## Test Scenarios

### Scenario 1: Vague request refined into a single story

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user says:

"We need to add notifications to the app."

**Expected Behaviour**
1. Skill classifies the input as vague and restates the current understanding before asking questions.
2. Skill asks targeted follow-up questions covering problem/value, scope, requirements, flow, edge cases, and dependencies — one group at a time using `vscode_askQuestions` when available.
3. Skill does NOT produce any story or acceptance criteria while ambiguities remain open.
4. After all questions are answered and no ambiguity remains, skill performs a consistency check across goal, scope, and acceptance criteria.
5. Skill reviews each scope item for completeness, edge cases, technical constraint consequences, and missing attachments.
6. Skill decides whether the work fits in one story; if so, produces one refined story using the output template.
7. Output contains all required sections: Title, User Story, Scope, Acceptance Criteria.

**Simulated Human Responses**
1. "Registered users receive notifications. Events that trigger them: a new direct message, a mention in a comment, or a status change on an item they own."
2. "In-app only (bell icon with a badge counter). No email or push for now."
3. "Users can mark individual notifications as read or mark all as read. Unread count shown in the header."
4. "No notifications for system or admin events. Notifications are scoped to the current user only."
5. "If the user is offline the notification is stored and shown when they next open the app. No real-time delivery guarantee needed yet."
6. "No limit on stored notifications per user for now. No deletion UI required."

**Assertions**
- [ ] Skill asks at least one question about who receives notifications and what triggers them before producing any output.
- [ ] Skill does not output a story while any area in the identification table (problem, scope, requirements, flow, edge cases, dependencies) has an open question.
- [ ] Final output follows the output template with Title (max 10 words), User Story (As a … I want … so that …), Scope, and Acceptance Criteria sections.
- [ ] Acceptance criteria items are verifiable and start with a checkbox `- [ ]`.

---

### Scenario 2: User refuses to answer a clarifying question

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user says:

"Add export to PDF for the reports page."

The skill asks: "Should the export include all report data or only the currently filtered view?" The user replies: "I don't know, just decide."

**Expected Behaviour**
1. Skill classifies the input and identifies the filtering scope as an open decision.
2. Skill asks the clarifying question about export scope.
3. When the user refuses to answer, skill notes the item as an unresolved assumption.
4. Skill does NOT produce a story or acceptance criteria while the assumption is unresolved.
5. Skill explicitly communicates that it cannot proceed until the assumption is resolved, and re-asks or rephrases the question.

**Assertions**
- [ ] Skill does not produce a story, acceptance criteria, or output template while the filtering scope is unresolved.
- [ ] Skill explicitly states that the unresolved assumption blocks output and asks the user to resolve it.

---

### Scenario 3: Request too large — split into vertical slices, one refined, rest deferred

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user says:

"Build a complete user authentication system: registration with email/password, login, password reset via email, and social login with Google."

**Expected Behaviour**
1. Phase 0 finds no XDRS scope and skips to Phase 1.
2. Skill classifies the input as too large (bundles multiple independent user outcomes).
3. Skill asks targeted questions to understand each flow's requirements.
4. After questions are resolved, skill determines the work cannot fit in one story and proposes splitting into 4 vertical slices: registration, login, password reset, social login.
5. Skill presents `vscode_askQuestions` with "Accept split — start refining Registration" (recommended) plus options to adjust boundaries or keep the original scope.
6. User accepts the split and picks "Registration" as the first slice to refine.
7. Skill restarts from Phase 1 with the narrower registration scope. The remaining 3 slices are recorded as Deferred Stories.
8. Phases 1–7 run on the registration slice only. At Phase 7, a Deferred Items summary lists the 3 remaining slices.
9. Because no plan doc is active, skill presents `vscode_askQuestions` asking where to save the deferred slices; user picks BACKLOG.md.
10. Skill outputs one fully refined story (registration) and appends the 3 deferred slices to BACKLOG.md.

**Simulated Human Responses**
1. "Registration: email + password only. Password min 8 chars, at least one digit. Email must be verified before the user can log in."
2. "Login: email + password. No magic links. Session token valid for 7 days. Invalidated on logout."
3. "Password reset: send a time-limited link to the registered email. Link expires after 1 hour. User sets a new password via the link."
4. "Google social login: OAuth 2.0. If the Google email matches an existing account, link them. Otherwise create a new account."
5. "Error handling: show a user-friendly message for invalid credentials, expired links, and OAuth failures. No silent failures."
6. "No rate limiting, CAPTCHA, or 2FA in scope for now. Each flow ships independently."

**Assertions**
- [ ] Phase 0 is skipped (no XDRS scope found).
- [ ] Skill proposes a split at Phase 2 with rationale for each slice boundary.
- [ ] Skill uses `vscode_askQuestions` to present the split options, not plain text.
- [ ] After the user accepts, skill restarts Phase 1 for the chosen slice (registration) only.
- [ ] Final output contains exactly one fully refined story (the chosen slice), using the full output template.
- [ ] The three deferred slices appear in a Deferred Items summary at Phase 7, each with a one-line description.
- [ ] Skill does NOT produce a single merged story covering all four flows.
- [ ] The chosen slice's story is independently shippable and delivers a complete end-to-end user-visible outcome.
- [ ] No slice is a technical-layer-only story (e.g. "implement the auth database schema" alone is not acceptable).

---

### Scenario 4: Phase gate re-run — user requests deeper pass on Phase 4

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The skill has completed Phase 4 (Consistency & Scope Review) and presents the phase gate. The user selects:

"Re-run Phase 4 — deeper pass"

**Expected Behaviour**
1. Skill does NOT advance to Phase 5 — it restarts Phase 4 Step 1 (consistency check) and Phase 4 Step 2 (scope item review) with fresh eyes.
2. During the deeper pass, skill surfaces at least one finding not raised in the first run (e.g. a new edge case or a scope item with an unresolved constraint).
3. Skill asks a question about the new finding using `vscode_askQuestions`.
4. After the human responds, Phase 4 converges again and the gate is re-presented.
5. Skill re-presents the Phase 4 gate with "Continue to Phase 5 — Visual Validation" as the recommended option.

**Simulated Human Responses**
1. (Re-run Phase 4 selected at gate)
2. "The empty state message should appear only after a 300 ms delay to avoid a flash on fast networks."

**Assertions**
- [ ] Skill re-runs Phase 4 (does not skip to Phase 5) when the human selects re-run.
- [ ] Skill surfaces at least one new finding during the deeper pass.
- [ ] Skill asks a question about the new finding before re-presenting the gate.
- [ ] The Phase 4 gate is re-presented after the human responds.
- [ ] Skill does not advance to Phase 5 until the gate is explicitly confirmed with "Continue".

---

### Scenario 5: Phase 6 user-perspective challenge surfaces a missing journey step

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The story being refined is:

"Add a CSV export button to the reports page so registered users can download the current view."

Phases 1–5 are complete. The skill is running Phase 6, angle 1 (User journey completeness).

**Expected Behaviour**
1. During angle 1 analysis, skill identifies that the story does not specify what the user sees while the export is being prepared — there is no loading state or download confirmation described.
2. Skill presents this as a finding and asks: "What should the user see while the export is being prepared — an immediate download, a loading indicator, or a background task with a notification? What feedback confirms the download completed?"
3. Human answers the question.
4. Skill incorporates the answer into the story scope and continues to angles 2–9.
5. Skill does NOT produce the final story until Phase 7 is complete and the readiness checklist passes.

**Simulated Human Responses**
1. "Show a spinner while generating. When ready, auto-download the file and show a success toast: 'Your CSV is ready'."

**Assertions**
- [ ] Skill runs Phase 6 analysis before producing any output.
- [ ] Skill surfaces the missing loading state and download confirmation as a finding during angle 1 (User journey completeness).
- [ ] Skill asks at least one question about the finding using `vscode_askQuestions` before moving to angle 2.
- [ ] After the human responds, the answer is reflected in the story scope (loading spinner + success toast added).
- [ ] Skill does not skip to Phase 7 while any angle has open questions.

---

### Scenario 6: Plan document with pending placeholder stories — user picks one to refine

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The user references an epic plan document at `.xdrs/_local/bdrs/operations/plans/001-epic-improve-checkout.md`. The plan contains:

```
### Milestone 1: Payment Speed
**Key tasks:**
- [Reduce payment steps — pending](.assets/userstory-001-reduce-payment-steps.md)
- [Save payment method — pending](.assets/userstory-002-save-payment-method.md)

### Milestone 2: Error Recovery
**Key tasks:**
- [Retry failed payment — pending](.assets/userstory-001-retry-failed-payment.md)
```

Each `.assets/userstory-*.md` file contains `**Status:** to-be-refined` plus any preliminary notes captured when the story was created.

**Expected Behaviour**
1. Skill activates Phase 0, detects the plan document, and parses all Milestone key tasks.
2. Skill reads each linked `.assets/userstory-*.md` file and checks for `**Status:** to-be-refined`. Identifies all three as pending.
3. Skill presents a `vscode_askQuestions` list of the three pending stories plus a "New story" option.
4. User picks the "Reduce payment steps" story from Milestone 1.
5. Skill reads the placeholder file — extracts NNN (001) and slug (`reduce-payment-steps`) from its `**Story ID:**` line; carries any notes into Phase 1 as starting context.
6. Skill proceeds to Phase 1 using the placeholder's title and notes as the subject.
7. After Phase 7, skill overwrites `.assets/userstory-001-reduce-payment-steps.md` with the fully refined content (no `**Status:**` line).
8. Skill updates the task entry link text in Milestone 1 to `- [Reduce payment steps at checkout](.assets/userstory-001-reduce-payment-steps.md)`.

**Assertions**
- [ ] Phase 0 detects pending stories by reading file content (`**Status:** to-be-refined`), not by task entry name format.
- [ ] All three pending stories are listed before Phase 1 begins.
- [ ] NNN and slug are extracted from the placeholder file's `**Story ID:**` line, not from the task entry text.
- [ ] After Phase 7, the story detail file is overwritten with the refined content and no `**Status:**` field.
- [ ] The Milestone 1 task entry link text is updated to the refined story title; the file path stays the same.
- [ ] Skill does NOT offer "Save to BACKLOG.md" for deferred items while a plan doc is active.

---

### Scenario 7: Refined story output writes asset file and updates plan Milestone link

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. Phase 0 has detected an active plan doc at `.xdrs/_local/bdrs/operations/plans/002-epic-onboarding.md` with Milestone 1: "First Login Experience". The user is refining a new story to be placed there.

After completing Phases 1–6, Phase 7 produces the final story: "Show personalised welcome screen on first login".

**Expected Behaviour**
1. Phase 7 determines the next NNN in the plan's `.assets/` folder (no existing userstory files → NNN = 001).
2. Skill writes `.assets/userstory-001-welcome-screen-first-login.md` using the output template sections: Title, User Story, Scope, Edge Cases, Out of Scope, Constraints, Detailed Specs, Acceptance Criteria, Attachments, plus a back-link to the epic plan.
3. Skill inserts `- [Show personalised welcome screen on first login](.assets/userstory-001-welcome-screen-first-login.md)` as a key task in Milestone 1 of the plan doc.

**Assertions**
- [ ] Story detail file is created at the correct path inside the plan's `.assets/` folder.
- [ ] File uses all required template sections including `## Constraints` and `## Detailed Specs`.
- [ ] File includes a back-link to the parent epic plan.
- [ ] The plan doc's Milestone 1 key tasks section contains a markdown link entry pointing to the new file.
- [ ] NNN is 001 (first story in this epic's `.assets/` folder).

---

### Scenario 8: No XDRS scope — skill asks where to save and defaults to workspace root

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user says:

"I need to refine a story: users should be able to reset their PIN via SMS."

**Expected Behaviour**
1. Phase 0 finds no XDRS scope and skips to Phase 1 immediately.
2. Skill runs all phases normally.
3. At Phase 7, after producing the final story, skill asks via `vscode_askQuestions` where to save the story file, defaulting to `userstory-001-reset-pin-via-sms.md` at the workspace root.
4. If the story is split, the deferred slices prompt offers: add to existing epic plan, create new epic plan, or save to `BACKLOG.md`.

**Assertions**
- [ ] Phase 0 does not block or present any plan-doc questions when no XDRS scope exists.
- [ ] Phase 7 asks for a save location with a clear default path.
- [ ] The story file is saved to the user-confirmed path.
- [ ] Split deferred stories trigger a destination choice (not silently written to BACKLOG.md).

---

### Scenario 9: Story lacking detailed specs is flagged and sent back for more refinement

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user is refining:

"Integrate with the payments provider so users can pay by card."

After Phase 2 Step 1, no API endpoints, no payload structures, no documentation links, and no contact names have been surfaced.

**Expected Behaviour**
1. Phase 2 Step 1 interface-and-integration scan identifies that no external API details are recorded despite the story clearly involving a payment provider integration.
2. Skill asks targeted questions: "What is the payment provider? Do you have an API reference or documentation link? What is the payment flow — which endpoints are called, in what order, with what payload?"
3. Human provides partial answers: "We use Stripe. Charge endpoint. Don't know the exact payload."
4. Skill asks follow-up: "Can you share the Stripe API documentation link or the name of someone who owns the Stripe integration?"
5. Phase 7 readiness checklist item for Detailed Specs fails until sufficient detail is provided (endpoint, payload shape, or doc link).

**Assertions**
- [ ] Phase 2 Step 1 explicitly surfaces the missing integration details before Step 2 is reached.
- [ ] Skill does not produce a final story while `## Detailed Specs` remains empty for a story involving an external API.
- [ ] Phase 7 checklist item for Detailed Specs is checked only after sufficient detail (at minimum a doc link or endpoint) is provided.
- [ ] Final output's `## Detailed Specs` section contains at least the Stripe API reference and the charge endpoint.

---

### Scenario 10: XDRS scope active, start fresh, story split — Phase 7 asks where to put deferred slices

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. Phase 0 detected an XDRS scope with two existing epic plans but the user chose "start fresh — no plan context". During Phase 2, the story is found to be too large and split into three slices. The user accepts the split and starts refining Slice 1.

**Expected Behaviour**
1. Phase 0 detects XDRS scope, presents epic plan list plus "Start fresh" option, user picks "Start fresh".
2. Phases 1–7 run normally for Slice 1.
3. At Phase 7, because the context is "start fresh" (no active plan doc), the two deferred slices trigger a `vscode_askQuestions` prompt: "Where should the deferred story slices go?" with options: add to an existing epic plan (lists found epics), create a new epic plan, or save to BACKLOG.md.
4. Skill applies the chosen action (e.g., creates placeholder files for the two deferred slices and inserts `- [Slice description — pending](.assets/userstory-NNN-slug.md)` task entries in the chosen epic plan, or appends descriptions to BACKLOG.md).

**Assertions**
- [ ] Phase 0 presents the XDRS epic plan list even in "start fresh" mode.
- [ ] Deferred slices do NOT go silently to BACKLOG.md when an XDRS scope is present.
- [ ] Phase 7 presents a `vscode_askQuestions` destination choice for deferred slices.
- [ ] If an epic plan is chosen, deferred slices are created as placeholder files and inserted as `- [description — pending](.assets/...)` link entries in the correct Milestone.

---

### Scenario 11: Very large story split into multiple slices — no XDRS scope — deferred slices saved to BACKLOG.md

**Trigger / Input**
You are an agent with the `151-refine-user-story` skill loaded. The workspace has no `.xdrs/` directory. The user says:

"I need to build the entire checkout flow: cart review, address selection, payment method entry, coupon validation, order summary, fraud check, payment processing, order confirmation email, and post-purchase upsell screen."

**Expected Behaviour**
1. Phase 0 finds no XDRS scope and skips to Phase 1 immediately.
2. Phase 1 classifies the input as a vague, massively oversized request covering 9+ distinct behaviours.
3. Phase 2 determines the story is far too large for a single story (estimated > 2 weeks). Skill proposes splitting into vertical slices, for example:
   - Slice 1: Review cart and confirm address
   - Slice 2: Enter and validate payment method
   - Slice 3: Apply coupon and show order summary
   - Slice 4: Fraud check and payment processing
   - Slice 5: Order confirmation email
   - Slice 6: Post-purchase upsell screen
4. Skill presents `vscode_askQuestions` asking which slice to refine first; user picks Slice 1.
5. Phases 1–7 run on Slice 1 only. The remaining 5 slices are tracked as Deferred Stories.
6. At Phase 7, because no plan doc is active, skill presents `vscode_askQuestions`:
   - **"Save deferred slices to BACKLOG.md"** (recommended)
   - **"Save to a different file"** (open box)
   - **"Skip — do not save"**
7. User picks "Save deferred slices to BACKLOG.md". Skill appends the 5 deferred slices under a `## Deferred Stories` heading in `BACKLOG.md` at the workspace root (creating the file if needed), each with a one-line description and split rationale.
8. Skill outputs the refined story for Slice 1 only.

**Assertions**
- [ ] Phase 0 is skipped entirely (no XDRS scope found).
- [ ] Skill explicitly states at Phase 2 that the request is too large and must be split.
- [ ] All identified slices are presented for user selection before any refinement begins.
- [ ] Only the user-selected slice (Slice 1) is refined through Phases 1–7.
- [ ] The remaining slices appear in a Deferred Items summary at Phase 7.
- [ ] `vscode_askQuestions` is used at Phase 7 to ask where to save deferred slices (not silently appended).
- [ ] BACKLOG.md is created (or appended to) at the workspace root with a `## Deferred Stories` section.
- [ ] Each deferred slice in BACKLOG.md has a one-line description and reason for deferral.
- [ ] The final output contains exactly one refined story (Slice 1), not all slices.
- [ ] Skill does NOT offer BACKLOG.md for deferred items from an active plan doc (this scenario has no plan doc — condition satisfied).
