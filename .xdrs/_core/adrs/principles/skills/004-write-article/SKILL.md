---
name: 004-write-article
description: >
   Creates a new article document following XDR article standards: selects scope, type, subject, and number; then writes a focused synthetic text that combines and links multiple XDRs, Research documents, and Skills around a topic. Activate this skill when the user asks to create, add, or write a new article, guide, or overview document within an XDR project.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured article by following `_core-adr-004`, consulting `xdr-standards` for every core element definition, researching the XDRs, Research documents, and Skills to synthesize, and producing a concise document that serves as a navigable view without duplicating decision content.

## Instructions

### Phase 0: Clarify Intent

Before reading any standards, ask the user clarifying questions to gather the information needed to proceed. Use the `vscode_askQuestions` tool with all questions in a single call.

Mandatory questions (ask only if not already provided by the user):
- **Topic**: What is the article about? (skip if the user already stated it)
- **Audience**: Who is the intended reader? (e.g., new developers, product managers, external contributors) MUST always be asked explicitly; never infer from context.
- **Scope**: Which XDR scope should contain the article? (default is `_local`; confirm or ask only if context is ambiguous)

Optional questions (ask only when genuinely unclear):
- **Type**: Should the article primarily synthesize ADRs, BDRs, or EDRs? Ask only when the topic spans multiple types.
- **Existing XDRs**: Are there specific Decision Records or Skills you want the article to reference or synthesize?

Do NOT proceed to Phase 1 until you have at minimum a clear **topic** and **audience**.

### Phase 1: Understand the Article Goal

1. Read `.xdrs/_core/adrs/principles/004-article-standards.md` in full to internalize the template,
   placement rules, numbering rules, and the constraint that articles are views, not decisions.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full before defining the article's core elements. Treat it as the canonical source for how to choose and write type, scope, subject, numbering, naming, and folder placement.
3. Confirm the topic and intended audience gathered in Phase 0. Do NOT proceed without a clear
   topic.

### Phase 2: Select Scope, Type, and Subject

Consult `001-xdrs-core` while making each choice in this phase. The summaries below are orientation only; when any detail is unclear, the standard decides.

**Scope** — use `_local` unless the user explicitly names another scope.
- If the user names a scope other than `_local`, check the workspace root `.filedist` file. If any file under `.xdrs/[scope]/` appears in `.filedist`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Type** — match the type of the XDRs the article primarily synthesizes (`adrs`, `bdrs`, or `edrs`).
If the topic spans multiple types, use `adrs`. Use the same rules as `002-write-xdr` Phase 2:
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure, pipelines

**Subject** — pick the subject that best matches the article's topic (required list per type is in `_core-adr-001`).
If the article spans more than one subject, place it in `principles`.

### Phase 3: Assign a Number and Name

1. List `.xdrs/[scope]/[type]/[subject]/articles/` (create the folder if it does not exist).
2. Find the highest existing article number in that namespace and increment by 1. Never reuse numbers.
3. Choose a short lowercase kebab-case title that describes the topic clearly.
   - Good: `onboarding-guide`, `checkout-flow-overview`, `api-design-principles`
   - Avoid: `summary`, `notes`, `misc`

### Phase 4: Research XDRs and Skills to Synthesize

1. Read all XDRs, Research documents, and Skills relevant to the article topic across all scopes listed in the XDR root `index.md`.
2. Evaluate XDR metadata before synthesizing guidance. All documents present in the collection are considered active. Use `validFrom:` to determine the convergence date for adoption, `applyTo:` to determine whether the decision fits the audience or context being discussed, and the decision text itself for any remaining applicability boundaries.
3. Identify the key points a reader needs to understand the topic end-to-end.
4. Collect XDR IDs and file paths for cross-references. Never copy decision text verbatim; link to it.

### Phase 5: Write the Article

Use the mandatory template from `004-article-standards`:

```
# [scope]-article-[number]: [Short Title]

## Overview

[Brief description of what this article covers and its intended audience. Under 40 words.]

## Content

[Synthetic text combining and explaining the topic. Use links to Decision Records, Research documents, and Skills
when referencing information from those documents. Keep under 1950 words total.]

## References

- [XDR id or Skill name](relative/path/to/file.md) - Brief description of relevance
```

Rules to apply while drafting:

- Write for the stated audience; avoid jargon unexplained elsewhere.
- Every factual claim must link back to the authoritative XDR or Skill.
- If the article advises readers what to do, clearly separate active/applicable XDRs from background, historical, or out-of-scope ones.
- Never reproduce decision text verbatim; summarize and link.
- Prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams), or ASCII art for simple structure, flow, layout, or relationship indications.
- If the article genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/articles/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- Keep the article under 1950 words; move detailed content to XDRs or Skills.
- Use lowercase file names. Never use emojis.
- If a conflict exists between the article and a Decision Record, note it and defer to the XDR.

### Phase 6: Place and Register

1. Save the file at `.xdrs/[scope]/[type]/[subject]/articles/[number]-[short-title].md`.
2. Add a link to the article in the canonical index for that scope+type (`.xdrs/[scope]/[type]/index.md`).
3. Add back-references in the XDRs, Research documents, and Skills that the article synthesizes, under their `## References`
   section.
4. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new article. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-001`.

## Examples

**Input:** "Write an article about how skills work in this project."

**Expected actions:**
1. Read `004-article-standards.md`.
2. Topic: how skills work. Audience: developers new to the project.
3. Scope: `_local`, type: `adrs`, subject: `principles`.
4. Scan `.xdrs/_local/adrs/principles/articles/` — no articles exist → number is `001`.
5. Research `_core-adr-003`, `_core-adr-006`, and the existing skill SKILL.md files.
6. Write `.xdrs/_local/adrs/principles/articles/001-skills-overview.md` following the template, linking
   to `_core-adr-003` and the individual skill files.
7. Update `.xdrs/_local/adrs/index.md` with a link to the new article.
8. Add a reference to the article in `_core-adr-003` under `## References`.

## Edge Cases

- **Article vs. XDR confusion** — if the user asks for a document that makes a decision, write an XDR
  (use the `002-write-xdr` skill), not an article.
- **Cross-subject topic** — place the article in `principles`, not in any single subject folder.
- **No existing articles folder** — create it; it is optional in the folder layout.
- **Conflicting information found** — note the conflict in the article and always defer to the XDR.
- **Article would exceed 1950 words** — move detailed content to a new Research, Skill, or XDR and link back.

## Constraints

- MUST consult `001-xdrs-core` as the canonical source for every core element definition, especially type, scope, subject, numbering, naming, and placement.
- MUST follow the article template and placement rules from `004-article-standards`.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist`).
- MUST defer to active and applicable XDRs when article synthesis conflicts with them.

## References

- [_core-adr-004 - Article standards](../../004-article-standards.md)
- [_core-adr-006 - Research standards](../../006-research-standards.md)
- [_core-adr-001 - XDRs core](../../001-xdrs-core.md)
