# Palette catalogue

Six calm palettes, each tied to an audience. Pick one by audience and content, then keep it for the whole design and for sibling designs in the same `.assets/` folder. Every palette has 3 colors (primary, accent, surface-tint) plus a text color. White (`#FFFFFF`) is the neutral card and canvas fill.

Contrast ratios are WCAG 2.1 relative-luminance ratios, computed once with a throwaway script. Recompute them with a throwaway script whenever a hex value changes, and do the same for custom or brand colors.

## How to use a palette

- Canvas background: white or the surface tint. Cards and boxes: white or the surface tint. Primary: main shapes, titles, connectors. Accent: the one thing to look at first (key step, result, warning). Text: all body text.
- Use the "label on accent" color shown for each palette; never put the other text color on the accent.
- Where an accent fill against the surface is below 3:1, give accent shapes a 2px outline in the primary or text color.
- Never use color alone: add a label, number or shape to every category.

## Catalogue

### Engineering (developers, architects, runbooks)
primary #1F4E8C | accent #B85309 | surface #E8EEF6 | text #1B2433 | label on accent: white
contrast: text/surface 13.4 | white/primary 8.3 | white/accent 4.9 | text/white 15.6 | accent/surface 4.2

### Executive (leadership, strategy, roadmaps)
primary #14284B | accent #C8962E | surface #EEF1F6 | text #14284B | label on accent: text
contrast: text/surface 12.9 | white/primary 14.6 | text/accent 5.5 | accent/surface 2.4 (outline accent shapes)

### Research (studies, findings, reports)
primary #2F6B55 | accent #B4472A | surface #EDF3EE | text #1F2D26 | label on accent: white
contrast: text/surface 12.8 | white/primary 6.3 | white/accent 5.4 | accent/surface 4.8

### Workshop (teams, onboarding, product)
primary #0B7378 | accent #C93F2C | surface #E4F3F2 | text #12302F | label on accent: white
contrast: text/surface 12.4 | white/primary 5.6 | white/accent 5.0 | accent/surface 4.3

### Data (analytics, metrics, evals)
primary #4338A8 | accent #E8A317 | surface #ECEBFA | text #1E1B4B | label on accent: text
contrast: text/surface 13.6 | white/primary 8.9 | text/accent 7.4 | accent/surface 1.8 (outline accent shapes)

### Operations (delivery, pipelines, incidents)
primary #2F3B45 | accent #1E7A43 | surface #ECEFF1 | text #1A2026 | label on accent: white
contrast: text/surface 14.2 | white/primary 11.5 | white/accent 5.4 | accent/surface 4.6

## Color-blind notes

- Research pairs a green primary with a rust accent, and Operations pairs a slate primary with a green accent: the pairs differ in lightness, but still add a label or shape to every category.
- Never encode a status only as red versus green. Add words ("ok", "failed") or distinct shapes.
- Executive and Data pair a dark primary with a gold accent: these stay distinguishable for the common color-vision types.

## Choosing by audience

| Audience or content | Palette | Why |
|---|---|---|
| Developers, architecture, runbooks | Engineering | Neutral and technical |
| Leadership, roadmap, strategy | Executive | Formal and confident |
| Studies, findings, reports | Research | Calm and trustworthy |
| Team onboarding, product, workshops | Workshop | Friendly and open |
| Analytics, metrics, evaluations | Data | Precise and distinct |
| Delivery, pipelines, incidents | Operations | Sober and operational |

## Custom and brand colors

- Keep the human's brand colors, and warn when a pair fails 4.5:1 (text) or 3:1 (meaningful shapes and lines).
- Fix the failing pair by changing the text color or the background color, never the brand color.
- Compute every custom ratio with a throwaway script in the OS temp dir, never in chat.
