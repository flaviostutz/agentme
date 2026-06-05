---
name: _core-adr-skill-007-write-presentation
description: >
  Creates a Marp slide presentation for an existing XDRS document (policy, research, article, or plan).
  Activate this skill when the user asks to create slides, a presentation, or a slide deck for an XDRS document.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Guides the creation of a Marp Markdown slide presentation that supports an existing XDRS document. The skill ensures the slides follow presentation standards (`_core-adr-policy-009`), are correctly placed in the `.assets/` folder, and maintain bidirectional links with the parent document.

## Instructions

### Phase 1: Identify the Parent Document

1. Read `.xdrs/_core/adrs/principles/009-presentation-standards.md` in full to internalize all presentation rules.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` for `.assets/` placement rules and general framework structure.
3. Identify the parent document (policy, research, article, or plan) that the slides will support. The parent document must already exist. If no parent document exists, inform the user that slides cannot be standalone and suggest creating the parent document first.
4. If the user wants slides covering content from multiple documents, check whether an article already exists that synthesizes those documents. If not, suggest creating an article first (using the 004-write-article skill) and then creating slides for that article.

### Phase 2: Define the Presentation Scope

1. Read the parent document in full.
2. Define the central message or objective of the presentation. If the objective is ambiguous or there are multiple possible paths, ask the user before proceeding. Ask one question at a time.
3. Identify the target audience. Check the parent document for audience indicators. If unclear, ask the user. Common audiences:
   - **Executives**: high-level, strategic, outcome-focused
   - **Engineers**: technical depth, implementation details, trade-offs
   - **Specialists**: domain-specific depth, compliance, controls
   - **Control**: risk, compliance, audit, governance focus
4. Determine if multiple slide sets are needed for different audiences. If so, create separate files for each.

### Phase 3: Plan the Slide Structure

1. Extract the most important points from the parent document.
2. Organize slides following a linear storytelling structure:
   - **Context**: what is the situation, background, who is impacted
   - **Problem**: what needs to be decided, addressed, or understood
   - **Solution/Decision**: what was decided and why
   - **Actions/Next Steps**: what happens now, who is responsible
3. For each slide, identify the best format:
   - Mermaid diagrams for flows, relationships, architecture
   - Short bullet points for key decisions and trade-offs
   - Tables for comparisons, options, criteria
   - ASCII art for simple layouts or structures
   - Key short statements for emphasis
   - Longer text only when exact wording must be evaluated (policies, controls)
4. Keep the total under 30 slides. If more content is needed, plan separate slide sets.

### Phase 4: Determine the File Name

1. Take the parent document file name (without `.md` extension).
2. Append `-slides` for the primary set.
3. If multiple sets exist, append a context indicator: `-slides-overview`, `-slides-executive`, `-slides-technical`, etc.
4. Verify the final file name (including `.md`) is 64 characters or fewer. If it exceeds 64 characters, shorten the base name while keeping it recognizable.
5. Ensure the file name is entirely lowercase.

Examples:
- Parent: `003-naming-conventions.md` -> `003-naming-conventions-slides.md`
- Parent: `005-rail-standards.md` (executive audience) -> `005-rail-standards-slides-executive.md`
- Parent: `001-xdrs-overview.md` (article) -> `001-xdrs-overview-slides.md`

### Phase 5: Write the Slides

Create the Marp Markdown file with this structure:

```markdown
---
marp: true
---

# [Presentation Title]

[Subtitle or context line]
[Audience and date if relevant]

---

[Slide 2: Context/Background]

---

[Slide 3: Problem Statement]

---

[... additional slides ...]

---

# References

- [Parent document title](relative/path/to/parent.md)
- [Other related documents if applicable]
```

Rules:
- The first line of YAML frontmatter must be `marp: true`. Additional Marp keys (`theme`, `paginate`, `header`, `footer`) may be added after.
- Use `---` as the slide separator (standard Marp syntax).
- The last slide must contain links back to the parent document and any other related documents.
- Minimize text per slide. Prefer visual elements and short statements.
- Stress central questions, answers, doubts, decisions, and risks from the parent document.
- No emojis.
- Use relative paths for all links.
- Follow the audience-appropriate level of detail.

### Phase 6: Update the Parent Document

1. Add a link to the slide file in the parent document. Place it in the `## References` section or, for Policies, in the most appropriate section.
2. Use a descriptive link text such as "Presentation slides" pointing to the slide file in `.assets/`.

### Phase 7: Write Files

1. Create the slide file at the correct `.assets/` location:
   - Policies: `[xdrs-root]/[scope]/[type]/[subject]/.assets/[slide-file].md`
   - Articles: `[xdrs-root]/[scope]/[type]/[subject]/articles/.assets/[slide-file].md`
   - Research: `[xdrs-root]/[scope]/[type]/[subject]/researches/.assets/[slide-file].md`
   - Skills: `[xdrs-root]/[scope]/[type]/[subject]/skills/[number]-[skill-name]/.assets/[slide-file].md`
   - Plans: `[xdrs-root]/[scope]/[type]/[subject]/plans/.assets/[slide-file].md`
2. Update the parent document with the link to the slide file.
3. Verify that the slide file name is <= 64 characters and lowercase.

### Phase 8: Verify with Lint

1. Run the CLI lint utility from the repository root:
   ```
   npx -y xdrs-core@latest lint
   ```
2. Fix all reported errors before considering the task complete.

### Constraints

- MUST follow presentation standards from `_core-adr-policy-009` exactly.
- MUST NOT create slides without an existing parent document.
- MUST NOT create standalone slides that reference multiple documents without an article as the parent.
- MUST maintain bidirectional links between slides and parent document.
- MUST keep slide file names under 64 characters.
- MUST include `marp: true` in the slide frontmatter.
- MUST keep presentations under 30 slides.
- MUST ask the user about audience and objective when not clear from context.

## Examples

**Input**: "Create slides for our naming conventions decision"
- Locate the parent Policy (e.g. `003-naming-conventions.md`)
- Ask: "Who is the target audience for these slides?"
- Create: `.assets/003-naming-conventions-slides.md`
- Update: Add link in `003-naming-conventions.md`

**Input**: "Create an executive presentation covering our security and data decisions"
- Check if an article synthesizing security + data decisions exists
- If not, suggest creating the article first
- Create slides for the article, not the individual Policies

## Edge Cases

- If the parent document does not exist, do not create slides. Inform the user and suggest creating the parent first.
- If the slide file name would exceed 64 characters, shorten the base name while keeping it recognizable.
- If the content requires more than 30 slides, split into multiple slide sets with distinct audience or topic focus.
- If the parent document changes after slides are created, the slides must be reviewed and updated.

## References

- [_core-adr-policy-009 - Presentation standards](../../009-presentation-standards.md)
- [_core-adr-policy-001 - XDRS core](../../001-xdrs-core.md)
- [_core-adr-policy-004 - Article standards](../../004-article-standards.md)
- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)
