# Critique checklist

How to test a rendered SVG against [`agentme-edr-018`](../../../018-svg-visual-design-standards.md). Each test names the policy rule by id and the way to check it; the policy keeps the requirement text. Run the tests on the full render and on the squint render (about 280px wide).

## Tests by rule

| Rule | How to test |
|---|---|
| `02-canvas-and-ratio` | Read `viewBox` and the background rect; compare with A4 landscape or portrait; check margins of 40px or more |
| `03-content-density` | Count primary elements; above about 12, raise a split or simplification proposal |
| `04-readable-type-sizes` | List every `font-size`; find text below 14px that is not a minor annotation; look for empty space that could hold larger type; count distinct sizes (4 or fewer) |
| `05-contrast` | Squint render: the strongest element is clear and unique; text and shape contrast ratios computed by throwaway script when not from the catalogue |
| `06-alignment` | Compare x and y coordinates of boxes in the same row or column; every offset is a multiple of 8 and equal within a group |
| `07-repetition` | List shape, radius, stroke width, weight and color per element role; equal roles use equal values |
| `08-proximity-and-whitespace` | Gaps inside a group are smaller than gaps between groups; no element touches another or an edge |
| `09-color-palette` | Count distinct non-neutral colors (3 or 4); every category has a label or shape too; no gradients, shadows or transparency |
| `10-typography` | One font-family stack; hierarchy through weight and size only |
| `11-visual-hierarchy-and-flow` | Say which element is seen first, second, last; reading order is left to right, top to bottom; connectors are orthogonal; the title states the conclusion |
| `12-minimalism-and-labels` | Labels of about 6 words or fewer; no legend where direct labels fit; remove-half pass: remove each candidate element and check whether the message survives |
| `13-squint-and-reading-tests` | View the squint render: primary element, groups and reading path remain visible; trace the path from start to end |
| `14-chart-data-integrity` | Each value traces to the supplied data; axes and units are labeled; bars start at zero |
| `15-accessibility-and-hygiene` | `role="img"`, `<title>`, `<desc>` present; no `<script>`, `<animate>`, `href` to external files, `foreignObject`, `<image>` with raster data, metadata or absolute paths; special characters are escaped |

## Render checks (every pass)

- No text is clipped, overlapping another text or running outside its shape.
- No glyph is missing (empty squares or fallback fonts).
- Arrowheads attach to their shapes and connectors do not cross text.
- The render matches the canvas size declared in the brief.

## Severity

- **must-fix**: readability, contrast below thresholds, overlap, clipping, a missing glyph, a wrong or misleading message, a broken reading path, a hygiene violation (script, external reference).
- **polish**: a small alignment offset on non-adjacent elements, slightly uneven spacing, optional hierarchy refinements.

A pass is clean when it has no must-fix finding.

## Finding format

One finding per line pair, each under 25 words:

```
[must-fix] Alignment: boxes "Plan" and "Build" differ by 6px on the y axis.
Fix: snap both to the 8px grid at y=240.
```

Use `[polish]` for polish findings. Write findings to `critique.md` in the run folder, one section per pass (`## Pass N`).

## Test report (Gate 3)

A report under 120 words with: passes run, whether the stop rule was met, rule ids tested, the contrast pairs checked, open polish findings, and any must-fix finding still open after pass 5.

## Mermaid and draw.io

Apply the same tests through the format's own levers (theme variables, `classDef`, layout direction, node text length, shape styles). When no renderer is available, review the source for the testable rules and ask the human to view the result.
