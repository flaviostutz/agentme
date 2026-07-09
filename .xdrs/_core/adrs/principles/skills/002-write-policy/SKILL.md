---
name: 002-write-policy
description: >
  Creates a new Policy interactively: selects type, scope, subject, and writes a focused, conflict-checked policy document.
  Activate this skill when the user asks to create, add, or write a new Policy (ADR, BDR, or EDR).
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured Policy by following the standards in `_core-adr-policy-001`, consulting `policy-standards` for every core element definition, researching existing policies for conflicts, checking redundancy across related artifacts, and iterating until the document is concise, decision-focused, and clear about when the decision should be used.

## Instructions

### Phase 0: Prerequisites Gate — MUST complete before writing

Identify the target scope from the user's request; use `_local` if none is specified. Read the scope's `index.md` frontmatter and perform ALL of the following checks. If ANY check fails, output a FAIL result immediately and do not proceed:

- **Follows scopes:** If the scope declares `follows:` entries (e.g., `follows: myarea-core, shared-standards`), verify that each listed scope directory exists in the workspace AND contains an accessible `index.md` (e.g., `.xdrs/[scope-name]/index.md`). If any listed scope is missing or unreadable, output: `FAIL — Cannot proceed: scope \`[scope-name]\` is listed in \`follows\` but its policies are not present in the workspace. Install it before authoring documents in this scope, as the governance constraints cannot be verified.`
- **Scope-local core policy:** Check whether a `-core` policy file exists for the target scope (i.e., a file ending in `{scope-name}-core.md` inside the scope's `[type]/principles/` directory). If the scope's `index.md` references or implies a local core standard and that file is absent or unreadable, output: `FAIL — Cannot proceed: the local core policy \`{scope-name}-core.md\` is referenced for scope \`[scope-name]\` but could not be found. Without it, the document cannot be authored in full compliance with the scope's governance.`
- **Rationale:** Authoring a document without all mandatory governance layers loaded risks producing content that silently violates scope policies. Every governance layer declared by the scope MUST be present before writing begins.

### Phase 1: Understand the Decision

1. Read the XDRS root `index.md` (default: `.xdrs/index.md`) to discover all active scopes and their canonical indexes.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full to internalize structure rules, mandatory language, and the XDRS framework elements.
3. Read `.xdrs/_core/adrs/principles/002-policy-standards.md` in full to internalize the Policy template and document writing rules.
4. Treat `001-xdrs-core` as the canonical source for all core XDRS element definitions (type, scope, subject, numbering, placement). Treat `002-policy-standards` as the canonical source for how to write and structure the document itself.
5. Ask the user (or infer from context) the topic of the decision. Do NOT proceed to Phase 2 without a clear topic.
   - Ask one focused clarifying question at a time. Wait for the answer before asking the next question.
   - Each answer may reveal new ambiguities; ask follow-up questions as needed until the topic, intent, and scope are unambiguous.
   - Stop asking and proceed only when the decision topic is fully understood.

### Phase 2: Select Type, Scope, and Subject

Consult `001-xdrs-core` while making each choice in this phase. The summaries below are orientation only; when any detail matters, the standard decides.

**Type** — choose exactly one based on the nature of the decision:
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure

**Scope** — use `_local` unless the user explicitly names another scope.
- If the user names a scope other than `_local`, check the workspace root `.filedist.lock` file. If any file under `.xdrs/[scope]/` appears in `.filedist.lock`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Subject** — MUST read `_core-adr-policy-016` ([016-policy-subjects.md](../../016-policy-subjects.md)) in full before choosing. That document defines all allowed subjects per type with full descriptions, examples, and disambiguation tiebreakers. Do not rely on summaries or prior knowledge of the subject list — always read the policy and select the subject that best matches the decision topic according to its definitions.

When type, scope, or subject cannot be confidently inferred, ask the user a clarifying question before proceeding. Ask one question at a time and wait for the answer; follow up if the response introduces new ambiguity.

**Policy ID** — format: `[scope]-[type]-[next available number]`
- Read `_core-adr-policy-017` ([017-policy-numbering-ranges.md](../../017-policy-numbering-ranges.md)) to identify the 100-number block reserved for the chosen subject (e.g. `principles` → 001–100, `application` → 101–200).
- Scan `.xdrs/[scope]/[type]/[subject]/` for all existing numbers within that block and use the lowest number in the block that has not yet been assigned.
- Use the overflow range (901–999) only when all 100 slots in the subject's block are exhausted, taking the next available number there.
- Never reuse numbers from deleted Policies.

### Phase 3: Choose the Title

Choose a title that clearly states the question this Policy answers, not the answer itself. The title should let a reader know at a glance what decision scope this record covers.

- Good: "Package manager for Node.js projects", "Phone marketing procedures", "Integration patterns for systems connectivity"
- Avoid: "Use pnpm", "We chose pnpm", or overly vague titles like "Tooling decisions"

### Phase 4: Research Related Policies

1. Read all existing Policies relevant to the topic across all scopes listed in the Policy root `index.md`.
2. Evaluate Policy metadata before treating any decision as a current constraint. All documents present in the collection are considered active. `valid-from:` determines the convergence date for adoption, `apply-to:` determines whether it fits the current topic, and the decision text defines any remaining boundaries. Treat out-of-window or out-of-scope Policies as background only when assessing overlaps and conflicts.
3. Identify decisions that already address the topic (full or partial overlap).
4. Note decisions that might conflict with the intended outcome.
5. Read related `researches/` documents when they exist, especially if they contain constraints, findings, or option tradeoffs that should influence the decision.
6. Collect Policy IDs and file paths for cross-references.

### Phase 5: Check Redundancy Across Related Artifacts

1. Review the related Policies, research documents, skills, articles, and guides connected to the same decision thread.
2. Identify content that is repeated across those files, especially decision statements, applicability boundaries, mandatory rules, and rationale.
3. Prioritize the final decision, core boundaries, and short key instructions in the Policy itself.
4. When another document already explains details well, link to it instead of re-explaining the same content in full.
5. Copy only short instructions or key excerpts when they materially help a reader apply the decision without leaving the Policy.
6. Avoid repeating the same decision text across multiple related documents whenever a link or short reference is enough.

### Phase 6: Write the First Draft

Use the mandatory template from `002-policy-standards`:

**Check if the decision requires a structured set of rules:**
If the decision defines strong rules or policies that must be stated explicitly, or if other documents, skills, or agents have a clear need to reference individual rules, you MUST apply the structured rule format from `_core-adr-policy-008-policy-structured-standards`. This means:
  - Place each rule as a numbered heading block inside `### Details`.
  - Use the format:
    #### [NN]-[short-descriptive-title-in-kebab-case]
    [Rule body with mandatory/advisory language.]
  - Ensure each rule is uniquely numbered (two digits, zero-padded) and never reuse numbers if a rule is removed.
  - Other documents must cite rules using the canonical dot-notation: `[policy-name].[NN-short-descriptive-title-in-kebab-case]`.

**Example of a structured set of rules:**

```markdown
### Details

#### 01-data-must-be-encrypted-at-rest
All user data must be encrypted at rest using AES-256 or stronger algorithms.

#### 02-access-logs-must-be-retained
Access logs must be retained for at least 90 days and reviewed monthly for suspicious activity.

#### 03-external-integrations-should-be-reviewed
All external integrations should be reviewed annually for compliance with current security standards.
```

Refer to `_core-adr-policy-008-policy-structured-standards` for full requirements and citation syntax.

```
---
name: [scope]-[type]-[number]-[short-title]
description: [What this decision is about and when to use it]
apply-to: [Required. Contexts this decision applies to, under 40 words. Use "All scopes" when broadly applicable.]
valid-from: [Required. ISO date YYYY-MM-DD. Defaults to today's date when not specified by the user.]
---

# [scope]-[type]-[number]: [Short Title]

## Context and Problem Statement
[background, who is impacted, and the explicit question being answered - under 40 words]

## Decision Outcome

**[Chosen Option Title]**
[One sentence: what is the decision - under 30 words]

### Details
[Rules, applicability boundaries, concise examples, and optional do/don't guidance — under 1300 words]

## Considered Options (only if the user explicitly indicated multiple options)

## Conflicts (mandatory if conflicts found in Phase 3)

## References (optional)
```

Mandatory rules to apply while drafting:
- Always include frontmatter `apply-to:`. Use `All scopes` when the decision applies broadly, or a more specific description when the decision is narrowly scoped.
- Always include frontmatter `valid-from:`. Use today's date in `YYYY-MM-DD` format when the user does not specify a date.
- Keep `apply-to:` under 40 words and use `valid-from:` only with `YYYY-MM-DD` ISO format.
- When frontmatter metadata is present, write it so a reader can decide whether the Policy should be used for the current case without guessing. `valid-from:` sets a convergence date for adoption, `apply-to:` narrows the contexts where the decision applies, and the decision text defines any remaining boundaries.
- Use mandatory language ("must", "always", "never") only for hard requirements; use advisory language ("should", "recommended") for guidance.
- Do not duplicate content already in referenced Policies — link instead.
- Keep the decision itself authoritative in the Policy. Supporting artifacts may elaborate, but they should not restate the full decision when a short reference is enough.
- Make clear when the decision applies and any important exception boundaries.
- Keep exploratory option analysis in a related Research document when it would distract from the final decision text.
- Prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams), or ASCII art for simple structure, flow, layout, or relationship indications.
- If the Policy genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- No emojis. Lowercase filenames.
- Target under 1300 words total; under 2600 words for complex decisions.

### Phase 7: Review the Draft

Check every item before finalizing:

1. **Length**: Is it under 1300 words? Trim verbose explanations. Move detailed skills to a separate file and link.
2. **Frontmatter**: Are `apply-to:` and `valid-from:` both present? `apply-to:` must describe the applicable context (use `All scopes` when broadly applicable). `valid-from:` must be set (use today's date if the user did not specify one).
3. **Normative language**: Does every normative requirement in the Details and Decision Outcome sections use uppercase BCP 14 keywords per `_core-adr-policy-001`? Replace any lowercase `must`/`should`/`may` that express requirements, prohibitions, or permissions with MUST/MUST NOT, SHOULD/SHOULD NOT, or MAY/OPTIONAL respectively. Lowercase forms are only acceptable in Context sections, question statements, or when used with their ordinary English meaning.
3. **Originality**: Does every sentence add value that cannot be found in a generic web search? Remove obvious advice. Keep only the project-specific decision.
4. **Clarity**: Is the chosen option unambiguous? Is the "why" clear in one reading?
5. **Redundancy**: Is the Policy the primary source for the decision itself, with related documents linked instead of duplicated wherever possible?
6. **Conflicts section**: Is it present and filled if Phase 3 found any conflicts?
7. **Index entries**: Will the new Policy be added to `[scope]/[type]/index.md` and the Policy root `index.md`?
8. **Meta-policy compliance**: Check the target scope's `index.md` for a `follows` frontmatter field. `_core` Policies always apply to all scopes. If `follows` lists additional core scope names (e.g., `follows: [myarea-core]`), verify that each listed scope directory exists in the workspace (e.g., `.xdrs/[scope-name]/index.md`). If any listed scope is missing, STOP immediately and tell the user: "Scope `[scope-name]` is listed in `follows` but not found in the workspace. Install it before proceeding." Once all `follows` scopes are confirmed present, verify the document satisfies all requirements from those Policies. Scopes are applied in order; last-listed scope in `follows` takes precedence when the same topic is covered by multiple scopes.
   - **Scope-type standards:** Read the target scope's `scope-type`. Search the `[type]/principles/` directories of all `core`-type scopes for a file ending in `{scope-type}-scope-type.md`. Apply its rules as requirements for the new Policy. Resolve any `NN-parent-scope-type` rule transitively. See `_core-adr-policy-010` rules 15 and 17.
   - **Scope-local standards:** Search the target scope's own `[type]/principles/` for a file ending in `{scope-name}-core.md`. If found, apply its rules as requirements; they override scope-type standards on conflict. See `_core-adr-policy-010` rules 16 and 17.

If any check fails, revise and re-run this phase before proceeding.

### Phase 8: Write Files

1. Create the Policy file at `[xdrs-root]/[scope]/[type]/[subject]/[number]-[short-title].md` (default root: `.xdrs/`).
2. Add an entry to `[xdrs-root]/[scope]/[type]/index.md` (create the file if it does not exist).
3. Add or verify the scope entry in the Policy root `index.md`.
4. If significant research was produced or already exists, link it from the Policy `## Considered Options` section.
5. If concise rules, examples, or do/don't bullets help readers apply the decision correctly, add them inside `### Details` without turning the Policy into a long procedure.
6. Evaluate whether the scope index at `[xdrs-root]/[scope]/index.md` should be updated to reflect the new content. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-policy-001`.

### Phase 9: Verify Package structure with Lint

1. Run the CLI lint utility from the repository root:
   ```
   npx -y xdrs-core@latest lint
   ```
2. Fix all reported errors before considering the task complete.
3. Review warnings; fix straightforward ones and note intentional deviations explicitly.

### Constraints

- MUST follow the Policy template from `002-policy-standards` exactly.
- MUST consult `001-xdrs-core` as the canonical source for element definitions (type, scope, subject, ID, numbering, naming, placement) and `002-policy-standards` for document writing rules and template.
- MUST NOT add personal opinions or general best-practice content not tied to a decision.
- MUST NOT create a Policy that duplicates a decision already captured in another Policy — extend or reference instead.
- MUST prefer links and short references over repeating the same decision content across related documents.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist.lock`).

## References

- [_core-adr-policy-001 - XDRS core](../../001-xdrs-core.md)
- [_core-adr-policy-002 - Policy standards](../../002-policy-standards.md)
- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)
