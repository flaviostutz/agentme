# Style families

Four styles, each a recipe of shape, stroke, fill and type. Combine one style with one palette from [palette-catalogue.md](palette-catalogue.md). All use the stack `Helvetica, Arial, sans-serif` and the type scale below, on a 1123x794 (or 794x1123) canvas. Scale the numbers for other canvases.

## Type scale (all styles)

| Role | Size | Weight |
|---|---|---|
| Title (action title) | 30-36px | 700 |
| Subtitle or section | 18-20px | 400 |
| Central label | 20-24px | 700 |
| Body label | 15-17px | 400 or 600 |
| Annotation | 12-13px | 400 |

## clean-blocks

- Shapes: rectangles with radius 8, no stroke, solid fills (primary for main steps, accent for the key step, white on a tinted background for the rest).
- Connectors: 2px primary lines with small solid arrowheads, orthogonal.
- Background: white or surface tint.
- Best for: process flows, architecture overviews, engineering and operations audiences.
- Avoid: more than one accent element per canvas.

## outline-blueprint

- Shapes: white fill, 2px primary stroke, radius 4; the accent only as a thicker 3px stroke or a small marker.
- Connectors: 2px primary lines, square corners.
- Background: surface tint with an optional 1px grid in a slightly darker solid tint (no transparency).
- Best for: technical systems, interfaces, data models.
- Avoid: dense text inside boxes; outline shapes carry less visual weight, so use bigger type.

## soft-cards

- Shapes: cards with radius 16 on a surface tint, a 1px border in a darker tint, and a 6px accent tab or number badge on top.
- Connectors: 2px primary lines.
- Background: white.
- Best for: onboarding, team and product overviews, comparisons of 3-6 items.
- Avoid: nested cards; keep one level.

## editorial

- Shapes: few boxes. Large title (36px), a thin 2px primary rule under it, numbered markers (circles, 28px) instead of boxes, generous whitespace.
- Connectors: only where flow matters, 2px.
- Background: white.
- Best for: article covers, executive summaries, storytelling and timelines.
- Avoid: more than about 8 primary elements.

## Choosing a style

| Content | Style |
|---|---|
| Process or flow | clean-blocks |
| System, interfaces, data model | outline-blueprint |
| Comparison, team, onboarding | soft-cards |
| Story, timeline, cover | editorial |

Reuse the style of sibling SVGs in the same `.assets/` folder unless the human asks for variety.
