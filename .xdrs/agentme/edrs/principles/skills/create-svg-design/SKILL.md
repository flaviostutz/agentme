---
name: create-svg-design
description: >
  Creates or reviews an SVG graphic (diagram, infographic, chart, illustration, icon, cover art) used as an asset in an article, README, research or similar document. It gathers a short brief, proposes an audience-driven palette and style, draws the SVG on an A4-like canvas with large readable type, then renders it, views the render and critiques it against KARP and readability tests until it converges, with human gates. Activate when the user asks for a polished SVG, diagram image, graphic or visual asset, or asks to review or improve an existing SVG.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-11-08
---

## Overview

Produces SVG assets that are readable, calm and aesthetic by following [`agentme-edr-018`](../../018-svg-visual-design-standards.md) in a gated process: brief, palette and style proposal, optional layout concepts, build, render-and-critique loop with self-taken screenshots, final approval. The agent draws and tests; the human decides audience, message, style and whether the result is good enough. A second mode reviews and improves an existing SVG, Mermaid or draw.io visual with the same tests.

### Inputs

#### Required
- A request for a graphic, or the path of an existing visual to review
- What the graphic must show (content or source text)

#### Optional
- Target document's `.assets/` folder, audience, brand colors, named palette or style, consumer canvas constraint (e.g. 16:9)

### Outputs

#### Contents
- Approved SVG in the run folder (and its PNG render)
- Brief, critique log and test report in the run folder
- Test report shown in chat (<120 words)

#### Changes
- Approved SVG copied to the target document's sibling `.assets/` folder, only with human approval

### Halt Conditions
- Nothing to show was given, or the content stays unclear after clarification
- The target is a Policy document (propose an article instead)
- A gate has not been approved by the human
- The content cannot fit one canvas and the human declines a split or simplification

### User Interaction
- Gate 1: the brief (audience, message, content, canvas) with one proposed palette and style
- Gate 2 (only when the structure is ambiguous): 2-3 layout concepts
- Gate 3: the final render with the test report
- One question before installing the renderer package, when needed
- Every question follows [`agentme-edr-003`](../../003-hitl-question-content.md)

### Runtime Requirements
- Write access to `.tmp/create-svg-design/`
- An SVG renderer: `rsvg-convert` or `resvg`, or Node.js 22+ with `npm` (see Phase 4)
- An image-viewing capability for the agent; without it the human views each render (Phase 4)

## Instructions

Keep every question <140 words, every concept sketch <60 words, `brief.md` <150 words, every critique finding <25 words, the test report <120 words, every other intermediate message <100 words and the final summary <100 words. SVG `<title>` <12 words and `<desc>` <60 words. Use no emojis. Cite policy rules by id (for example `agentme-edr-018.06-alignment`).

### Work files

- Create one run folder `.tmp/create-svg-design/[run-name]/` per run (run name: lowercase letters, digits and hyphens, like `onboarding-flow`; append `-2`, `-3` if taken). Keep `brief.md`, `draft-N.svg`, `render-N.png`, `squint-N.png`, `critique.md` and the final `[name].svg` there. Never write files directly in `.tmp/create-svg-design/`.
- Put throwaway scripts (render, contrast, sampler fill) in an OS temp directory (`mktemp -d`) and delete it when the run ends, also on halt.
- End the final chat message with `results-path: .tmp/create-svg-design/[run-name]/`.
- Keep renders local; do not upload them to external services.

### Phase 1: Brief (Gate 1)

1. Create one todo per phase.
2. Identify the mode: create, or review and improve an existing visual. For review, read the file, then continue at Phase 4 with the existing file as `draft-0` (do not overwrite it; the improved copy is saved in the run folder).
3. If the target document is a Policy, halt and propose an article (`_core-adr-policy-020.10-no-images-in-policies`).
4. Confirm these inputs, asking only for what is unknown: audience, message (the one thing the reader should take away), content (elements, relationships, source text), canvas (A4 landscape by default, A4 portrait, square, or a consumer constraint with its reason).
5. When a target document exists, list the SVGs in its sibling `.assets/` folder. If some exist, propose reusing their palette and style, and read one to see which.
6. Pick one palette from [palette-catalogue.md](references/palette-catalogue.md) and one style from [style-families.md](references/style-families.md) by audience and content (`agentme-edr-018.16-audience-driven-variety`). Keep brand colors given by the human (see the catalogue section on custom colors). Prefer variety across a document set, but stay calm and useful.
7. Count the primary elements. Above about 12, propose a split into several graphics or a simplification, with 2 options and their consequences.
8. Write `brief.md` and ask the Gate 1 question: the brief in the context line, 2-3 options (proposed palette and style marked "(recommended)", an alternative, "Other"), and an offer to show a rendered sampler. When in doubt about style, content or objective, give the options instead of guessing (`agentme-edr-018.17-ask-when-in-doubt`).
9. Show a sampler only when asked (Phase 1a). Never start drawing before the human approves the brief.

#### Phase 1a: Sampler (on request)

Pick 3 candidate palettes from the catalogue. Copy [sampler-template.svg](.assets/sampler-template.svg) into the run folder, fill every `{{token}}` (`title`, `subtitle`, `style`, and `pN_name`, `pN_audience`, `pN_primary`, `pN_accent`, `pN_surface`, `pN_text`, `pN_onaccent` for N = 1..3) with a throwaway script, render it as in Phase 4, view it and show it to the human. Let the human pick by name.

### Phase 2: Layout concepts (Gate 2, optional)

Skip when the structure is obvious. Otherwise sketch 2-3 concepts (for example left-to-right flow, layered stack, hub and spoke) as ASCII, each <60 words with what it emphasizes, and ask which to use with a recommended option. Do not draw before the choice.

### Phase 3: Build the draft

1. Write `draft-1.svg` following [style-families.md](references/style-families.md) and the policy rules: `viewBox`, explicit light background rect, a `<title>`, a `<desc>` and `role="img"` on the root, one font stack, sizes from the type scale, an 8px grid, orthogonal connectors, consistent stroke, direct labels of about 6 words or fewer, an action title.
2. Use the whole canvas: margins of 40px or more, sizes proportional to importance, central labels large (`agentme-edr-018.04-readable-type-sizes`). Prefer enlarging type to leaving empty space.
3. Use catalogue colors with their listed "label on accent" color. For a custom or brand color pair, compute the WCAG 2.1 contrast with a throwaway script (relative luminance `0.2126R + 0.7152G + 0.0722B` on linearized channels, ratio `(L1 + 0.05) / (L2 + 0.05)`) and never in chat. Text needs 4.5:1 and meaningful shapes 3:1.
4. For a chart, use only values from the human or a cited source, label axes and units and start bars at zero (`agentme-edr-018.14-chart-data-integrity`).
5. Escape `&`, `<` and `>` in text. Do not add scripts, animation, external references, `foreignObject`, raster images, metadata or absolute paths.

### Phase 4: Render and critique loop

1. Render each draft to PNG at the canvas width (1123 for landscape, 794 for portrait) and a squint render about 280px wide. Use the first available renderer:
   - `rsvg-convert -w 1123 draft-N.svg -o render-N.png` or `resvg -w 1123 draft-N.svg render-N.png`
   - a throwaway Node script in the OS temp dir with the pinned package `@resvg/resvg-js@2.6.2` (ask the human once before running `npm install --prefix [tempdir] @resvg/resvg-js@2.6.2`); the script reads the SVG path, output path and width from `process.argv` and writes `new Resvg(svg, { fitTo: { mode: 'width', value: width }, font: { loadSystemFonts: true } }).render().asPng()`
   - the `open-browser-playwright` skill to screenshot the SVG
   - otherwise the human opens the SVG and reports what they see
2. View `render-N.png` and `squint-N.png` with the image-viewing capability. When the agent cannot view images, use the human-views path: the human views each render and answers the checklist questions, while the agent still checks the SVG source.
3. Critique the pass with [critique-checklist.md](references/critique-checklist.md): run the tests of every rule listed there and the render checks, and write findings to `critique.md` (`## Pass N`) in the finding format. Classify each finding as must-fix or polish.
4. Fix all must-fix findings and polish that is cheap, save as `draft-N+1.svg` and repeat.
5. Stop when two consecutive passes have no must-fix finding, or after 5 passes (`agentme-edr-018.18-render-and-critique-evidence`). After pass 5, keep the best draft and list the open findings.
6. Run the remove-half pass once before the stop and re-render if elements changed.

### Phase 5: Final approval (Gate 3)

1. Write the test report (<120 words) in `critique.md` and show it in chat with the path of the final render.
2. Ask: approve, adjust (free text), or try a different style or layout, with a recommended option. Loop back to Phase 3 or 4 on adjustments.
3. On approval, save the final SVG as `[name].svg` in the run folder. When a target document exists, copy it into the sibling `.assets/` folder with a lowercase kebab-case name; if that file already exists, ask before replacing it. Offer to add the Markdown image link to the document, with an alt text <20 words.
4. Delete the OS temp directory with the throwaway scripts. End with a summary <100 words and the `results-path:` line.

### Other formats

For Mermaid or draw.io sources, run the same tests through their levers (theme variables, `classDef`, direction, label length). Render when a renderer exists (`mmdc` for Mermaid); otherwise review the source and ask the human to view the result. Format choice stays per `_core-adr-policy-020`.

## Examples

Example prompts:
- "Create an SVG diagram of our release flow for the README."
- "Make a cover graphic for the research article about onboarding."
- "Review docs/.assets/pipeline.svg for readability and improve it."

Example Gate 1 question:

```
Context: I'm about to design a diagram for the onboarding README (audience: new team members).
Proceed with this palette and style?
 1. Workshop + soft cards (recommended): friendly, suits a team audience
 2. Different palette or style: I'll list alternatives or render a sampler
 3. Other: describe the audience and I'll adapt
```

## Edge Cases

- No target document: keep the SVG in the run folder only; the human moves it.
- Icons and logos: use the size the consumer needs; skip the A4 and density rules and keep contrast and hygiene.
- The human asks for something that breaks a rule (for example 8px body text everywhere): ask for the reason and offer a compliant alternative before drawing.
- The brand colors fail contrast: keep them, warn, and fix the failing pair through the text or background color.
- No renderer and no image viewing: review the source and ask the human to view; report what could not be tested.
- Existing SVGs in the repository with small fonts: leave them unless the human asks to modify them.
- Requests for photos or raster art: decline; SVG is vector only.

## Anti-Patterns

- **Mistake:** Drawing a wide strip with 9px labels to fit all the content.
  **Why it happens:** Fitting everything in one graphic feels more complete.
  **Instead:** Use the A4-like canvas, enlarge type by importance, and propose a split when there are more than about 12 primary elements.

- **Mistake:** Declaring the design good from the SVG source without viewing a render.
  **Why it happens:** The source looks correct and rendering takes an extra step.
  **Instead:** Render and view every pass, including the squint render, or hand the render to the human.

- **Mistake:** Reusing the same palette and style for every audience, or adding gradients and shadows to look rich.
  **Why it happens:** The first working look is the cheapest to copy.
  **Instead:** Choose from the catalogue by audience, keep solid washed-out fills, and ask when unsure.

- **Mistake:** Computing contrast ratios or screening colors in chat.
  **Why it happens:** The numbers seem easy to estimate.
  **Instead:** Use catalogue values or a throwaway script, per [`agentme-edr-005`](../../005-skill-scripts-and-composition.md).

- **Mistake:** Overwriting an existing `.assets/` file or the reviewed original.
  **Why it happens:** The improved version feels clearly better.
  **Instead:** Save to the run folder first and ask before replacing a file.

## References

- [agentme-edr-018 - SVG visual design standards](../../018-svg-visual-design-standards.md)
- [agentme-edr-003 - HITL question content](../../003-hitl-question-content.md)
- [agentme-edr-005 - Skill scripts and composition](../../005-skill-scripts-and-composition.md)
- [_core-adr-policy-020 - Media and asset standards](../../../../../_core/adrs/principles/020-media-and-asset-standards.md)
- [_core-adr-policy-023 - Skill runtime standards](../../../../../_core/adrs/principles/023-skill-runtime-standards.md)
