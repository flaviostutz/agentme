---
name: _core-adr-policy-009-presentation-standards
description: Defines how Marp slide presentations are structured, named, placed, and linked within XDRS projects. Use when creating, reviewing, or linting slide decks that support XDRS documents.
apply-to: Marp slide presentations in XDRS projects
valid-from: 2025-01-01
---

# _core-adr-policy-009: Presentation standards

## Context and Problem Statement

Teams often need slide presentations to communicate decisions, research findings, plans, or article content to different audiences. Without a standard, slides drift from the authoritative documents, use inconsistent formats, and become disconnected from the policies they support.

How should slide presentations be structured, placed, and maintained within the XDRS framework so they remain consistent, discoverable, and always traceable to the documents they support?

## Decision Outcome

**Marp Markdown slides co-located in `.assets/` next to the parent document**

Presentations are Markdown files in Marp format, stored in the `.assets/` folder of the document they support, with bidirectional links and strict naming conventions.

### Details

- Slides are supporting media for XDRS documents. They MUST NOT exist as standalone artifacts without a parent decision, research, article, or plan.
- Slides MUST use the [Marp](https://marp.app/) Markdown format with a minimal YAML frontmatter block at the beginning of the file:
  ```
  ---
  marp: true
  ---
  ```
  Additional Marp configuration keys (e.g. `theme`, `paginate`, `header`, `footer`) MAY be added when needed, but `marp: true` MUST be the first frontmatter key.
- Slide files MUST be placed in the `.assets/` folder next to the element they relate to, following the `.assets/` placement rules defined in `_core-adr-policy-001`.
- The parent document MUST contain a link to the slide file. The slide file MUST contain a link back to the parent document at the end of the presentation.
- Slide files MUST use the same base name as the parent file, suffixed with `-slides`. When multiple slide sets exist for the same parent, append a context indicator after `-slides` (e.g. `-slides-overview`, `-slides-executive`).
  - Example: parent `003-naming-conventions.md` produces `003-naming-conventions-slides.md` or `003-naming-conventions-slides-overview.md`.
- Slide file names MUST NOT exceed 64 characters (including the `.md` extension).
- Slide file names MUST be lowercase.
- When slides refer to content from multiple decisions, plans, or research documents, an article explaining the combined view MUST be written first. The slides then support that article, not the individual documents directly.
- Slides SHOULD contain minimal text. Prefer Mermaid diagrams, short bullet points, ASCII art, key short statements, and tables. Use longer text only when the exact wording MUST be evaluated by the audience (policies, texts under discussion, controls).
- Slides SHOULD follow a clean, linear storytelling structure (context, problem, solution, actions). Follow the structure of the underlying document, extracting the most important points and stressing central questions, answers, doubts, decisions, and risks.
- Define the central message or objective of the presentation before creating the slides. If the objective is unclear or there are multiple possible paths, ask the user before proceeding.
- The target audience MUST be identified (executives, engineers, specialists, control). If the audience is not clear from the underlying document, ask before creating the slides. Include audience info in the file name when multiple audiences exist (e.g. `005-rail-standards-slides-executive.md`).
- Keep presentations under 30 slides. Create separate slide sets for different views or audiences when needed.
- Slides MUST NOT replace policies or related document contents. When the underlying document changes, the associated slides MUST be reviewed and updated to stay consistent.
- MUST NOT use emojis in slide content.
- File names MUST be lowercase.

## References

- [_core-adr-policy-001 - XDRs core](001-xdrs-core.md) - Framework structure and `.assets/` placement rules
- [_core-adr-policy-002 - Policy standards](002-policy-standards.md) - Policy document writing rules
- [_core-adr-policy-004 - Article standards](004-article-standards.md) - Article standards for multi-document views
- [007-write-presentation skill](skills/007-write-presentation/SKILL.md) - Skill for creating slide presentations
- [Marp](https://marp.app/) - Markdown Presentation Ecosystem
