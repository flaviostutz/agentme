---
name: _core-adr-policy-004-article-standards
description: Defines article document standards for synthesizing and linking Policies, research, and skills. Use when creating or reviewing articles.
---

# _core-adr-policy-004: Article standards

## Context and Problem Statement

As the number of Policies, Research documents, and Skills grows, navigating and understanding related decisions across subjects and types becomes difficult. Without a structured format for synthetic documentation, teams create ad-hoc documents that drift from the actual decisions and supporting evidence over time.

How should articles be structured and organized to provide useful views over Policies, Research, and Skills without replacing them as the source of truth?

## Decision Outcome

**Subject-level synthetic documents co-located with Policies**

Articles are Markdown documents placed inside a subject folder alongside policies. Placing articles within a subject keeps them close to the decisions, research, and skills they reference.

### Details

- Articles are views, not decisions. They summarize and synthesize content from Policies, Research, and Skills but are NOT the source of truth. When there is a conflict between an article and a Policy, the Policy takes precedence.
- Articles are not limited to synthesizing Policies. They may also document application features, APIs, general project information, reference tables, diagrams, FAQs and other elements useful to their intended audience.
- Articles must reference the Policies, Research documents, and Skills they synthesize. Never duplicate decision content; link back to the authoritative sources.
- Articles may serve as indexes, combining related artifacts on a specific topic into a single navigable document.
- In more complex cases, an article may be an index of links to other articles, grouping related documentation into a single entry point that guides readers across a set of related topics.
- When an article tells readers which decisions to follow, it SHOULD check `valid-from:` first to determine the convergence date, `apply-to:` second to determine context fit, and the decision text itself last. All documents present in the collection are considered active; articles must not present out-of-window or out-of-scope Policies as current rules for the discussed context.
- Articles must remain consistent with the Policies, Research documents, and Skills they reference. When a referenced artifact changes, the article must be reviewed and updated.
- Place an article in the subject folder that best matches its topic using the required list of subjects per type defined in `_core-adr-policy-001`. If an article spans more than one subject, place it in `principles`.
- For simple structure, flow, layout, or relationship indications, articles SHOULD prefer plain Markdown, tables, or ASCII art instead of external assets.
- Any non-Markdown files referenced by an article (schemas, JSON examples, images, diagrams, binaries, or any other data files) SHOULD be used only when they are materially necessary and MUST live in `articles/.assets/` next to the article files.
- Sub-directories inside this `.assets/` folder are allowed only when it already has more than 10 files. Otherwise, keep files flat.
- Always use lowercase file names.
- Never use emojis in article content.
- Articles should be kept under 5000 words. Move or point to detailed contents referenced in Policy decisions, researches, plans or skills.

**Folder layout**

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        articles/
          [number]-[short-title].md
          .assets/
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
# [scope]-[type]-article-[number]: [Short Title]

## Overview

[Brief description of what this article covers and its intended audience. (<40 words)]

## Content

[Synthetic text combining and explaining the topic. Use links to Policies, Research, and Skills
when referencing an information from those documents.]

## References

- [Policy id or Skill name](relative/path/to/file.md) - Brief description of relevance
```

## Considered Options

* (REJECTED) **Separate documentation repository** - Removes drift risk but decouples docs from decisions.
  * Reason: Increases maintenance burden and makes it easy for articles to go stale relative to the Policies they reference.
* (CHOSEN) **Subject-level articles folder co-located with Policies** - Keeps articles alongside the policies and skills they reference, with `principles` as the fallback for cross-subject articles.
  * Reason: Easy to discover, consistent with where skills are placed, and clearly distinct from the policies themselves.

## References

- [_core-adr-policy-001 - Policies core](001-xdrs-core.md)
- [_core-adr-policy-003 - Skill standards](003-skill-standards.md)
- [_core-adr-policy-006 - Research standards](006-research-standards.md)
- [004-write-article skill](skills/004-write-article/SKILL.md) - Step-by-step instructions for creating a new article
