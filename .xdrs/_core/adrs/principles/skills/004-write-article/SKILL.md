---
name: 004-write-article
description: >
  Creates a new article document following XDR article standards: selects scope, type, subject, and number;
  then writes a focused synthetic text that combines and links multiple XDRs and Skills around a topic.
  Activate this skill when the user asks to create, add, or write a new article, guide, or overview document
  within an XDR project.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a well-structured article by following `_core-adr-004`, researching the XDRs and
Skills to synthesize, and producing a concise document that serves as a navigable view without duplicating
decision content.

## Instructions

### Phase 1: Understand the Article Goal

1. Read `.xdrs/_core/adrs/principles/004-article-standards.md` in full to internalize the template,
   placement rules, numbering rules, and the constraint that articles are views, not decisions.
2. Identify the topic and intended audience from user input or context. Do NOT proceed without a clear
   topic.

### Phase 2: Select Scope, Type, and Subject

**Scope** — use `_local` unless the user explicitly names another scope.

**Type** — match the type of the XDRs the article primarily synthesizes (`adrs`, `bdrs`, or `edrs`).
If the topic spans multiple types, use `adrs`.

**Subject** — pick the subject that best matches the article's topic (see `004-article-standards`).
If the article spans more than one subject, place it in `principles`.

### Phase 3: Assign a Number and Name

1. List `.xdrs/[scope]/[type]/[subject]/articles/` (create the folder if it does not exist).
2. Find the highest existing article number in that namespace and increment by 1. Never reuse numbers.
3. Choose a short lowercase kebab-case title that describes the topic clearly.
   - Good: `onboarding-guide`, `checkout-flow-overview`, `api-design-principles`
   - Avoid: `summary`, `notes`, `misc`

### Phase 4: Research XDRs and Skills to Synthesize

1. Read all XDRs and Skills relevant to the article topic across all scopes listed in `.xdrs/index.md`.
2. Identify the key points a reader needs to understand the topic end-to-end.
3. Collect XDR IDs and file paths for cross-references. Never copy decision text verbatim; link to it.

### Phase 5: Write the Article

Use the mandatory template from `004-article-standards`:

```
# [scope]-article-[number]: [Short Title]

## Overview

[Brief description of what this article covers and its intended audience. Under 3 lines.]

## Content

[Synthetic text combining and explaining the topic. Use links to Decision Records and Skills
when referencing information from those documents. Keep under 150 lines total.]

## References

- [XDR id or Skill name](relative/path/to/file.md) - Brief description of relevance
```

Rules to apply while drafting:

- Write for the stated audience; avoid jargon unexplained elsewhere.
- Every factual claim must link back to the authoritative XDR or Skill.
- Never reproduce decision text verbatim; summarize and link.
- Keep the article under 150 lines; move detailed content to XDRs or Skills.
- Use lowercase file names. Never use emojis.
- If a conflict exists between the article and a Decision Record, note it and defer to the XDR.

### Phase 6: Place and Register

1. Save the file at `.xdrs/[scope]/[type]/[subject]/articles/[number]-[short-title].md`.
2. Add a link to the article in the canonical index for that scope+type (`.xdrs/[scope]/[type]/index.md`).
3. Add back-references in the XDRs and Skills that the article synthesizes, under their `## References`
   section.

## Examples

**Input:** "Write an article about how skills work in this project."

**Expected actions:**
1. Read `004-article-standards.md`.
2. Topic: how skills work. Audience: developers new to the project.
3. Scope: `_local`, type: `adrs`, subject: `principles`.
4. Scan `.xdrs/_local/adrs/principles/articles/` — no articles exist → number is `001`.
5. Research `_core-adr-003` and all existing skill SKILL.md files.
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
- **Article would exceed 150 lines** — move detailed content to a new Skills or XDR and link back.
