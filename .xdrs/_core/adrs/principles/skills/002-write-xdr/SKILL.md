---
name: 002-write-xdr
description: >
  Creates a new XDR (Decision Record) interactively: selects type, scope, subject, and writes a focused, conflict-checked decision document.
  Activate this skill when the user asks to create, add, or write a new XDR, ADR, BDR, or EDR.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured XDR by following the standards in `_core-adr-001`, consulting `xdr-standards` for every core element definition, researching existing records for conflicts, checking redundancy across related artifacts, and iterating until the document is concise, decision-focused, and clear about when the decision should be used.

## Instructions

### Phase 1: Understand the Decision

1. Read the XDR root `index.md` (default: `.xdrs/index.md`) to discover all active scopes and their canonical indexes.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full to internalize structure rules, mandatory language, and the XDR framework elements.
3. Read `.xdrs/_core/adrs/principles/002-xdr-standards.md` in full to internalize the XDR template and document writing rules.
4. Treat `001-xdrs-core` as the canonical source for all core XDR element definitions (type, scope, subject, numbering, placement). Treat `002-xdr-standards` as the canonical source for how to write and structure the document itself.
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
- If the user names a scope other than `_local`, check the workspace root `.filedist` file. If any file under `.xdrs/[scope]/` appears in `.filedist`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Subject** — pick one from the allowed list for the chosen type (from `001-xdrs-core`):
- ADR: `principles`, `application`, `data`, `integration`, `platform`, `controls`, `operations`
- BDR: `principles`, `marketing`, `product`, `controls`, `operations`, `organization`, `finance`, `sustainability`
- EDR: `principles`, `application`, `infra`, `observability`, `devops`, `governance`

When type, scope, or subject cannot be confidently inferred, ask the user a clarifying question before proceeding. Ask one question at a time and wait for the answer; follow up if the response introduces new ambiguity.

**XDR ID** — format: `[scope]-[type]-[next available number]`
- Scan `.xdrs/[scope]/[type]/` for the highest existing number in that scope+type and increment by 1.
- Never reuse numbers from deleted XDRs.

### Phase 3: Choose the Title

Choose a title that clearly states the question this XDR answers, not the answer itself. The title should let a reader know at a glance what decision scope this record covers.

- Good: "Package manager for Node.js projects", "Phone marketing procedures", "Integration patterns for systems connectivity"
- Avoid: "Use pnpm", "We chose pnpm", or overly vague titles like "Tooling decisions"

### Phase 4: Research Related XDRs

1. Read all existing XDRs relevant to the topic across all scopes listed in the XDR root `index.md`.
2. Evaluate XDR metadata before treating any decision as a current constraint. All documents present in the collection are considered active. `validFrom:` determines the convergence date for adoption, `applyTo:` determines whether it fits the current topic, and the decision text defines any remaining boundaries. Treat out-of-window or out-of-scope XDRs as background only when assessing overlaps and conflicts.
3. Identify decisions that already address the topic (full or partial overlap).
4. Note decisions that might conflict with the intended outcome.
5. Read related `researches/` documents when they exist, especially if they contain constraints, findings, or option tradeoffs that should influence the decision.
6. Collect XDR IDs and file paths for cross-references.

### Phase 5: Check Redundancy Across Related Artifacts

1. Review the related XDRs, research documents, skills, articles, and guides connected to the same decision thread.
2. Identify content that is repeated across those files, especially decision statements, applicability boundaries, mandatory rules, and rationale.
3. Prioritize the final decision, core boundaries, and short key instructions in the XDR itself.
4. When another document already explains details well, link to it instead of re-explaining the same content in full.
5. Copy only short instructions or key excerpts when they materially help a reader apply the decision without leaving the XDR.
6. Avoid repeating the same decision text across multiple related documents whenever a link or short reference is enough.

### Phase 6: Write the First Draft

Use the mandatory template from `002-xdr-standards`:

**Check if the decision requires a structured set of rules:**
If the decision defines strong rules or policies that must be stated explicitly, or if other documents, skills, or agents have a clear need to reference individual rules, you MUST apply the structured rule format from `_core-adr-008-xdr-standards-structured`. This means:
  - Place each rule as a numbered heading block inside `### Details`.
  - Use the format:
    #### [NN]-[short-descriptive-title-in-kebab-case]
    [Rule body with mandatory/advisory language.]
  - Ensure each rule is uniquely numbered (two digits, zero-padded) and never reuse numbers if a rule is removed.
  - Other documents must cite rules using the canonical dot-notation: `[xdr-name].[NN-short-descriptive-title-in-kebab-case]`.

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

Refer to `_core-adr-008-xdr-standards-structured` for full requirements and citation syntax.

```
---
name: [scope]-[type]-[number]-[short-title]
description: [What this decision is about and when to use it]
applyTo: [Optional. Contexts this decision applies to, under 40 words]
validFrom: [Optional. ISO date YYYY-MM-DD from when enforcement begins]
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
- Include frontmatter `applyTo:` only when it adds value by narrowing the decision scope; omit it when the decision applies broadly.
- Include frontmatter `validFrom:` only when there is a specific future enforcement date; omit it when the decision is immediately effective.
- Keep `applyTo:` under 40 words and use `validFrom:` only with `YYYY-MM-DD` ISO format.
- When frontmatter metadata is present, write it so a reader can decide whether the XDR should be used for the current case without guessing. `validFrom:` sets a convergence date for adoption, `applyTo:` narrows the contexts where the decision applies, and the decision text defines any remaining boundaries.
- Use mandatory language ("must", "always", "never") only for hard requirements; use advisory language ("should", "recommended") for guidance.
- Do not duplicate content already in referenced XDRs — link instead.
- Keep the decision itself authoritative in the XDR. Supporting artifacts may elaborate, but they should not restate the full decision when a short reference is enough.
- Make clear when the decision applies and any important exception boundaries.
- Keep exploratory option analysis in a related Research document when it would distract from the final decision text.
- Prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams), or ASCII art for simple structure, flow, layout, or relationship indications.
- If the XDR genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- No emojis. Lowercase filenames.
- Target under 1300 words total; under 2600 words for complex decisions.

### Phase 7: Review the Draft

Check every item before finalizing:

1. **Length**: Is it under 1300 words? Trim verbose explanations. Move detailed skills to a separate file and link.
2. **Frontmatter**: Are `applyTo:` and `validFrom:` present only when they add value, omitted entirely when not needed, and specific enough for a reader to decide whether the XDR is currently valid and applicable?
3. **Originality**: Does every sentence add value that cannot be found in a generic web search? Remove obvious advice. Keep only the project-specific decision.
4. **Clarity**: Is the chosen option unambiguous? Is the "why" clear in one reading?
5. **Redundancy**: Is the XDR the primary source for the decision itself, with related documents linked instead of duplicated wherever possible?
6. **Conflicts section**: Is it present and filled if Phase 3 found any conflicts?
7. **Index entries**: Will the new XDR be added to `[scope]/[type]/index.md` and the XDR root `index.md`?

If any check fails, revise and re-run this phase before proceeding.

### Phase 8: Write Files

1. Create the XDR file at `[xdrs-root]/[scope]/[type]/[subject]/[number]-[short-title].md` (default root: `.xdrs/`).
2. Add an entry to `[xdrs-root]/[scope]/[type]/index.md` (create the file if it does not exist).
3. Add or verify the scope entry in the XDR root `index.md`.
4. If significant research was produced or already exists, link it from the XDR `## Considered Options` section.
5. If concise rules, examples, or do/don't bullets help readers apply the decision correctly, add them inside `### Details` without turning the XDR into a long procedure.
6. Evaluate whether the scope index at `[xdrs-root]/[scope]/index.md` should be updated to reflect the new content. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-001`.

### Phase 9: Verify Package structure with Lint

1. Run the CLI lint utility from the repository root:
   ```
   npx -y xdrs-core lint .
   ```
2. Fix all reported errors before considering the task complete.
3. Review warnings; fix straightforward ones and note intentional deviations explicitly.

### Constraints

- MUST follow the XDR template from `002-xdr-standards` exactly.
- MUST consult `001-xdrs-core` as the canonical source for element definitions (type, scope, subject, ID, numbering, naming, placement) and `002-xdr-standards` for document writing rules and template.
- MUST NOT add personal opinions or general best-practice content not tied to a decision.
- MUST NOT create an XDR that duplicates a decision already captured in another XDR — extend or reference instead.
- MUST prefer links and short references over repeating the same decision content across related documents.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist`).

## References

- [_core-adr-001 - XDRs core](../../001-xdrs-core.md)
- [_core-adr-002 - XDR standards](../../002-xdr-standards.md)
- [_core-adr-003 - Skill standards](../../003-skill-standards.md)
