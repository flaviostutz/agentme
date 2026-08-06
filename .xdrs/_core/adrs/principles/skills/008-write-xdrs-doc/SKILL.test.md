---
skill: 008-write-xdrs-doc
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Routes a policy creation request to 002-write-policy

**Trigger / Input**
You are an agent with the `008-write-xdrs-doc` skill loaded. The XDRS workspace is present with all scopes accessible. The user says:

"Write a policy about how functions must be named in our codebase."

**Expected Behaviour**
1. Skill infers document type as **Policy** from keywords "write a policy".
2. Skill runs the prerequisites gate for the target scope.
3. Skill reads `.xdrs/_core/adrs/principles/skills/002-write-policy/SKILL.md` in full.
4. Skill reads `_core-adr-policy-016` (allowed subjects) and `_core-adr-policy-017` (numbering ranges).
5. Skill follows all phases of `002-write-policy` from Phase 0 onward.

**Assertions**
- [ ] Skill reads `002-write-policy/SKILL.md` before producing any output.
- [ ] Skill reads both `_core-adr-policy-016` and `_core-adr-policy-017`.
- [ ] Skill executes Phase 0 (scope placement) of `002-write-policy`.
- [ ] Skill does NOT skip directly to producing the policy document without going through `002-write-policy` phases.

### Scenario 2: Routes a skill creation request to 003-write-skill

**Trigger / Input**
You are an agent with the `008-write-xdrs-doc` skill loaded. The user says:

"Create an agent skill that helps debug failing CI pipelines."

**Expected Behaviour**
1. Skill infers document type as **Skill** from keywords "agent skill".
2. Skill runs the prerequisites gate.
3. Skill reads `.xdrs/_core/adrs/principles/skills/003-write-skill/SKILL.md` in full.
4. Skill follows all phases of `003-write-skill` including Phase 0 (scope placement) and Phase 5.5 (SKILL.test.md).

**Assertions**
- [ ] Skill reads `003-write-skill/SKILL.md` before producing output.
- [ ] Skill executes Phase 0 (scope placement) of `003-write-skill`.
- [ ] Skill does NOT create the skill document without running through `003-write-skill` phases.

### Scenario 3: Asks a clarifying question when type is ambiguous

**Trigger / Input**
You are an agent with the `008-write-xdrs-doc` skill loaded. The user says:

"I want to document the deployment process."

**Expected Behaviour**
1. Skill cannot confidently infer whether this is a Policy, Plan, Article, or Research document.
2. Skill asks exactly one focused clarifying question listing the valid document types.
3. Skill does NOT proceed to load any target skill until the user answers.

**Assertions**
- [ ] Skill outputs a question asking the user to specify the document type.
- [ ] The question lists at least the options: Policy, Skill, Research, Plan, Article, Presentation.
- [ ] Skill does NOT create or route to any document-type skill before receiving the answer.

### Scenario 4: Rejects an unknown document type

**Trigger / Input**
You are an agent with the `008-write-xdrs-doc` skill loaded. The user says:

"Create a changelog for version 2.0."

The user then clarifies: "The document type is 'Changelog'."

**Expected Behaviour**
1. Skill recognizes "Changelog" is not in the routing table.
2. Skill informs the user that this document type is not supported.
3. Skill does NOT attempt to route to any skill or create any document.

**Assertions**
- [ ] Skill does NOT create any document or route to a skill.
- [ ] Output informs the user that "Changelog" is not a supported XDRS document type.
- [ ] Output lists the valid types from the routing table.
