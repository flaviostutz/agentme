# _core-adr-004: Article standards

## Context and Problem Statement

As the number of XDRs and Skills grows, navigating and understanding related decisions across subjects and types becomes difficult. Without a structured format for synthetic documentation, teams create ad-hoc documents that drift from the actual decisions over time.

How should articles be structured and organized to provide useful views over XDRs and Skills without replacing them as the source of truth?

## Decision Outcome

**Subject-level synthetic documents co-located with XDRs**

Articles are Markdown documents placed inside a subject folder alongside decision records. Placing articles within a subject keeps them close to the decisions and skills they reference.

### Implementation Details

- Articles are views, not decisions. They summarize and synthesize content from XDRs and Skills but are NOT the source of truth. When there is a conflict between an article and a Decision Record, the Decision Record takes precedence.
- Articles must reference the XDRs and Skills they synthesize. Never duplicate decision content; link back to the authoritative sources.
- Articles may serve as indexes, combining related DRs and Skills on a specific topic into a single navigable document.
- Articles must remain consistent with the XDRs and Skills they reference. When a referenced XDR or Skill changes, the article must be reviewed and updated.
- Place an article in the subject folder that best matches its topic. If an article spans more than one subject, place it in `principles`.
- Always use lowercase file names.
- Never use emojis in article content.
- Articles should be kept under 150 lines. Move detailed content to referenced XDRs or Skills.

**Folder layout**

```
.xdrs/[scope]/[type]/[subject]/
  articles/
    [number]-[short-title].md
```

Examples:
- `.xdrs/_local/adrs/principles/articles/001-onboarding-guide.md`
- `.xdrs/business-x/bdrs/product/articles/002-checkout-flow-overview.md`
- `.xdrs/business-x/bdrs/principles/articles/003-cross-domain-overview.md`  ← spans multiple subjects

**Article numbering**

- Each article has a number unique within its `scope/type/subject/articles/` namespace.
- Determine the next number by checking the highest number already present in that namespace.
- Never reuse numbers of deleted articles. Gaps in the sequence are expected and allowed.

**Article template**

All articles MUST follow this template:

```markdown
# [scope]-article-[number]: [Short Title]

## Overview

[Brief description of what this article covers and its intended audience. (<3 lines)]

## Content

[Synthetic text combining and explaining the topic. Use links to Decision Records and Skills
when referencing an information from those documents.]

## References

- [XDR id or Skill name](relative/path/to/file.md) - Brief description of relevance
```

## Considered Options

* (REJECTED) **Inline summaries inside XDR index files** - Keeps everything in one place but clutters the navigation indexes.
  * Reason: Index files should remain lean navigation aids; mixing synthesis into them hurts readability and makes updates harder.
* (REJECTED) **Separate documentation repository** - Removes drift risk but decouples docs from decisions.
  * Reason: Increases maintenance burden and makes it easy for articles to go stale relative to the XDRs they reference.
* (CHOSEN) **Subject-level articles folder co-located with XDRs** - Keeps articles alongside the decision records and skills they reference, with `principles` as the fallback for cross-subject articles.
  * Reason: Easy to discover, consistent with where skills are placed, and clearly distinct from the decision records themselves.

## References

- [_core-adr-001 - XDR standards](001-xdr-standards.md)
- [_core-adr-003 - Skill standards](003-skill-standards.md)
- [004-write-article skill](skills/004-write-article/SKILL.md) - Step-by-step instructions for creating a new article
