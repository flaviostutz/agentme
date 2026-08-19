---
skill: 151-write-user-story
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Vague request refined into a single story

**Trigger / Input**
You are an agent with the `151-write-user-story` skill loaded. The user says:

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
You are an agent with the `151-write-user-story` skill loaded. The user says:

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

### Scenario 3: Request too large — split into vertical slices

**Trigger / Input**
You are an agent with the `151-write-user-story` skill loaded. The user says:

"Build a complete user authentication system: registration with email/password, login, password reset via email, and social login with Google."

**Expected Behaviour**
1. Skill classifies the input as too large (bundles multiple independent user outcomes).
2. Skill asks targeted questions to understand each flow's requirements.
3. After questions are resolved, skill determines the work cannot fit in one story.
4. Skill splits the request into independently shippable vertical-slice stories (e.g. registration, login, password reset, social login as separate stories).
5. Each split story uses the output template and delivers a complete end-to-end user-visible outcome.
6. Skill does NOT produce a single merged story.

**Simulated Human Responses**
1. "Registration: email + password only. Password min 8 chars, at least one digit. Email must be verified before the user can log in."
2. "Login: email + password. No magic links. Session token valid for 7 days. Invalidated on logout."
3. "Password reset: send a time-limited link to the registered email. Link expires after 1 hour. User sets a new password via the link."
4. "Google social login: OAuth 2.0. If the Google email matches an existing account, link them. Otherwise create a new account."
5. "Error handling: show a user-friendly message for invalid credentials, expired links, and OAuth failures. No silent failures."
6. "No rate limiting, CAPTCHA, or 2FA in scope for now. Each flow ships independently."

**Assertions**
- [ ] Output contains multiple stories, each using the full output template.
- [ ] Each story is independently shippable and delivers a complete end-to-end user-visible outcome.
- [ ] No story is a technical-layer-only slice (e.g. "implement the auth database schema" alone is not acceptable).
