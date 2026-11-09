---
name: agentme-edr-policy-018-svg-visual-design-standards
description: >
  Defines visual design standards for SVG assets (diagrams, infographics, charts, illustrations, icons, cover art) used in articles, READMEs and research: A4-like canvas, readable type, KARP principles, palette, layout, accessibility and a render-and-critique process. Use when creating, modifying or reviewing an SVG design or a Mermaid or draw.io visual made as a document asset.
apply-to: the agentme scope itself, and any scope that directly or transitively follows or extends agentme
valid-from: 2026-11-08
---

# agentme-edr-policy-018: svg visual design standards

## Context and Problem Statement

Generated SVG assets tend to be wide, crowded, small-fonted and visually uniform, so readers struggle to read them and authors cannot judge them objectively.

Which design rules and verification process must SVG visual assets follow?

## Decision Outcome

**Design SVG assets on an A4-like canvas with importance-proportional type, KARP principles and an audience-driven palette, and verify each one by rendering, viewing and critiquing it.**

### Details

#### 01-scope-and-precedence

These rules apply when an SVG design is created or materially modified, meaning layout, text or colors change beyond a typo fix. Existing SVGs are not required to be redrawn. A primary element is a box, node, chart mark or label group that carries meaning. Format order and the ban on images in Policies stay as in [`_core-adr-policy-020`](../../../_core/adrs/principles/020-media-and-asset-standards.md). Mermaid and draw.io visuals made as document assets MUST follow rules `02` to `18` through their own levers (theme, classes, layout direction) and MUST be rendered when a renderer exists.

#### 02-canvas-and-ratio

The canvas SHOULD be A4 landscape (`viewBox="0 0 1123 794"`) or A4 portrait (`0 0 794 1123`). A square MAY be used for symmetric content. Any other ratio, including wide strips, MUST be justified by a consumer constraint (for example 16:9 slides) stated in the brief. The SVG MUST declare a `viewBox` and an explicit light background rectangle. Icons and logos use the size the consumer needs. Margins SHOULD be at least 40px, and the content SHOULD use most of the canvas.

#### 03-content-density

A canvas SHOULD hold about 12 primary elements or fewer. Above that, the author MUST propose a split or simplification and the human decides.

#### 04-readable-type-sizes

Text SHOULD be sized in proportion to its importance. Central labels SHOULD be large, and body text SHOULD be about 14px or larger on an A4-like canvas. Minor annotations MAY be smaller. Titles SHOULD be 28 to 36px and central labels 20 to 24px. A design SHOULD use at most 4 font sizes, and unused space SHOULD be spent on larger type before shrinking text.

#### 05-contrast

Importance MUST be shown through differences in size, weight, color or position. Only one element, or a few, SHOULD be the strongest on the canvas. Text MUST have at least 4.5:1 contrast against its background, and meaningful shapes and lines at least 3:1 against theirs.

#### 06-alignment

Boxes, text and connectors MUST align to shared horizontal and vertical lines on an 8px grid. Misalignment of a few pixels MUST be treated as a defect.

#### 07-repetition

Equivalent elements MUST reuse the same shape, radius, stroke width, font weight and color. Different meaning MUST use a different, consistently applied style.

#### 08-proximity-and-whitespace

Related items MUST be placed closer to each other than to unrelated items, and distinct clusters MUST be separated by larger gaps. Whitespace SHOULD be generous and balanced, and no element SHOULD feel cramped.

#### 09-color-palette

A design MUST use 3 or 4 colors plus neutral text and surface colors, chosen from the audience and content type. Color MUST NOT be the only carrier of meaning, so pair it with a label, shape or position. Washed-out solid fills SHOULD be preferred over gradients, shadows and transparency. A brand color that fails contrast MUST be kept and flagged, and the failing pair MUST be fixed by changing the text or background color.

#### 10-typography

A design MUST use one sans-serif stack, `Helvetica, Arial, sans-serif` by default, and MUST create hierarchy with weight and size, not additional typefaces.

#### 11-visual-hierarchy-and-flow

The design MUST have a deliberate first, second and last look, with a predictable reading order (left to right and top to bottom) and clear directional cues. Lines SHOULD be orthogonal with consistent thickness, and diagonal lines SHOULD be avoided. The title SHOULD state the conclusion (an action title), not only the topic.

#### 12-minimalism-and-labels

Elements that do not serve the message, such as decoration and vendor stencils, MUST be removed. Labels SHOULD have about 6 words or fewer and SHOULD sit on or next to their element instead of in a legend. A remove-half pass SHOULD be applied: remove or merge elements until nothing can go without losing the message.

#### 13-squint-and-reading-tests

The author MUST render a second, small image (about 280px wide) and confirm that the primary element, the grouping and the reading path are still visible. The reading path MUST be traced from the start element to the last one without ambiguity.

#### 14-chart-data-integrity

Charts MUST use only values supplied by the human or a cited source, label axes and units, and start bar charts at zero.

#### 15-accessibility-and-hygiene

The SVG MUST have `role="img"`, a `<title>` and a `<desc>`, use editable text elements and escape XML special characters. It MUST NOT contain scripts, animation, external references, `foreignObject`, embedded raster images, tool metadata or absolute paths.

#### 16-audience-driven-variety

The palette and style MUST be proposed from the audience and content type, and a sibling SVG in the same `.assets/` folder SHOULD be reused as the visual reference. Designs SHOULD NOT repeat one look for every audience, but SHOULD stay calm and useful.

#### 17-ask-when-in-doubt

When audience, objective, content or style is unclear, the author MUST present options and let the human choose, following [`agentme-edr-003`](003-hitl-question-content.md). The human MUST approve the brief before drawing and the result before it is saved.

#### 18-render-and-critique-evidence

Each pass MUST render the SVG to an image and view it, then test it against rules `04` to `15`, and fix defects. Must-fix defects are readability, contrast, overlap, clipping and message errors. The loop MUST stop after two consecutive passes without must-fix defects, or after 5 passes with the remaining defects reported. Where no renderer is available, the human MUST view the file.

#### 19-skill

The skill [`create-svg-design`](skills/create-svg-design/SKILL.md) operationalizes these rules and SHOULD be used to create or review SVG designs.

## References

- [`_core-adr-policy-020`](../../../_core/adrs/principles/020-media-and-asset-standards.md) - media and asset standards
- [`agentme-edr-003`](003-hitl-question-content.md) - HITL question content
- [`create-svg-design`](skills/create-svg-design/SKILL.md) - skill that applies this policy
