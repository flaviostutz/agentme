---
name: _core-adr-policy-020-media-and-asset-standards
description: Defines the preferred order for representing visual information and the rules for non-Markdown assets across all XDRS document types. Use when choosing a diagram format or referencing any non-Markdown file in any XDRS document.
apply-to: All XDRS document types
valid-from: 2026-08-06
---

# _core-adr-policy-020: Media and asset standards

## Context and Problem Statement

Rules for diagram format preference and non-Markdown asset handling are scattered across multiple policies (001, 002, 003, 004, 006, 007) and all write-\* skills. The same asset placement and diagram preference rules appear independently in each document-type policy, creating duplication that `_core-adr-policy-002` itself prohibits, and inconsistency when the rules diverge.

Question: What is the canonical preference order for representing visual information in XDRS documents, and where must non-Markdown files be stored?

## Decision Outcome

**Markdown-first preference order: Markdown → ASCII → Mermaid → draw.io → SVG → PNG**

All diagram format preferences and non-Markdown asset rules are defined here as individually citable rule blocks. Individual document-type policies and skills reference this policy instead of repeating these rules.

### Details

#### 01-prefer-markdown
Markdown structures MUST be the first choice for any layout, tabular data, list, heading hierarchy, or simple relationship that can be expressed adequately as plain text. Plain Markdown tables, bullet lists, headings, and code blocks MUST be used before reaching for any external visual format.

#### 02-ascii-for-simple
ASCII art MAY be used for very simple spatial layouts or shapes where plain Markdown structures cannot adequately convey the diagram. ASCII art SHOULD be limited to cases that are trivial to write and maintain as plain text; anything requiring visual complexity SHOULD use Mermaid instead.

#### 03-mermaid-for-complex
Mermaid.js SHOULD be used for diagrams that require explicit visual representation: flows, sequences, state machines, entity relationships, class diagrams, and activity diagrams. Mermaid is preferred over draw.io when it can adequately express the needed diagram.

#### 04-drawio-when-mermaid-insufficient
draw.io SHOULD be used when Mermaid cannot adequately express the needed diagram — for example, custom visual layouts, freehand annotations, or combined view types that Mermaid does not support natively. draw.io diagrams MUST be saved as `.drawio` files in the sibling `.assets/` folder and referenced directly from the Markdown document.

#### 05-svg-for-custom-vector
Plain SVG MAY be used instead of draw.io when greater visual freedom is needed than draw.io provides, or when the diagram originates from tooling other than draw.io. SVG files MUST be stored in the sibling `.assets/` folder.

#### 06-png-as-last-resort
PNG (or other raster formats) MAY be used only when no vector or text-based format can adequately represent the content — for example, screenshots or photographs. PNG files MUST be stored in the sibling `.assets/` folder.

#### 07-assets-no-policy-content
Asset files MUST NOT contain policy content. Diagrams and images do not carry mandatory or advisory language — they cannot express MUST, SHOULD, or MAY obligations with the precision that prose requires. Assets MAY be used only to support the understanding of policy already stated in Markdown text; a visual that merely illustrates what the prose already says is acceptable, but any rule or constraint that exists only inside an asset file is invisible to policy and has no normative force. When in doubt, keep the content in Markdown.

#### 08-assets-materially-necessary
Non-Markdown files (images, diagrams, schemas, JSON examples, binaries, or any other data files) SHOULD be referenced only when they are materially necessary to preserve clarity, fidelity, or evidence. Assets that duplicate information already expressible in Markdown SHOULD NOT be added.

#### 09-assets-placement
Non-Markdown files MUST live in the sibling `.assets/` folder next to the referencing document. The canonical per-document-type `.assets/` paths are defined in `_core-adr-policy-001`.

## References

- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md) - Per-document-type `.assets/` canonical paths
- [_core-adr-policy-008 - Policy structured standards](008-policy-structured-standards.md) - Structured rule block format used in this policy
