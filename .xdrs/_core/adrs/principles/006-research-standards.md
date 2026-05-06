---
name: _core-adr-006-research-standards
description: Defines research document standards including IMRAD structure and traceability to XDRs. Use when creating or reviewing research documents.
---

# _core-adr-006: Research standards

## Context and Problem Statement

Teams often need more space than an XDR allows to evaluate constraints, explore options, and record findings before or after a decision changes. When that material is scattered across PR comments, docs, and chat, the reasoning behind a decision becomes hard to recover or update.

Question: How should research documents be structured and organized so they communicate an investigated problem, evidence, and conclusions clearly, while remaining traceable from related XDRs?

## Decision Outcome

**IMRAD-based subject-level research documents co-located with XDRs**

Research documents are Markdown files placed inside a subject folder alongside decision records. They use an IMRAD-inspired paper structure adapted to company needs so teams can communicate investigated problems, methods, findings, and conclusions clearly, combine experienced professional judgment with good-enough evidence, preserve reproducibility where it matters, and revisit the work when technology, constraints, or facts change.

### Details

- Research is evidence and exploration, not the adopted decision. When a research document and an XDR disagree, the XDR takes precedence.
- `Research` is the artifact name. `researches/` is only the folder name used alongside `skills/` and `articles/`.
- Research documents MUST live under `researches/` inside the relevant subject folder:
  `.xdrs/[scope]/[type]/[subject]/researches/[number]-[short-title].md`
- The `[subject]` component MUST be one of the allowed subjects for the chosen type. The required list of allowed subjects per type is defined in `_core-adr-001`.
- Research documents SHOULD stay focused on one investigated problem, comparison, or hypothesis.
- Research documents MUST state clearly what problem or question is being investigated, the relevant system or domain context, and why the subject matters in practice.
- Research documents MUST follow this section order: `Abstract`, `Introduction`, `Methods`, `Results`, `Discussion`, `Conclusion`, `References`.
- Research uses a company-adapted IMRAD structure. It MAY include informed professional judgment and experience-based observations, but claims that affect the conclusion MUST have enough evidence to be teachable, reviewable, and useful to other colleagues.
- Research does not require full academic statistical rigor. Use good-enough evidence that supports the conclusion without demanding exhaustive proof.
- Research documents MUST read as standalone technical papers for readers who do not know the XDR process.
- Mentions of future ADRs, decision lifecycle, repository process, or artifact management SHOULD be avoided in the body unless they are materially necessary to understand the research question.
- Traceability to related XDRs, skills, articles, discussions, and external sources SHOULD live primarily in `## References` and surrounding indexes rather than in the body narrative.
- Research documents MUST describe the methods, tools, sources, and conditions with enough detail that an experienced professional could at least minimally reproduce the important parts of the study, especially the aspects that materially affected the conclusion.
- The short title portion after the research id MUST stay under 20 words.
- `## Abstract` MUST be a single paragraph under 200 words summarizing the goal, methods, results, and conclusion. It SHOULD let a quick technical reader understand the question, method, main result, and takeaway.
- `## Introduction` MUST define the problem, context, constraints, known facts, experiences, gaps, assumptions, and objectives. It SHOULD prefer plain Markdown, bullet points, tables, or ASCII art for simple explanations, and SHOULD use external visuals only when they are materially necessary to improve understanding. It MUST stay under 700 words and MUST end with `Question: [central question]?`.
- `## Methods` MUST explain how the study was conducted, including design, tools, data sources, and test conditions, with a reproducibility goal. It MUST stay under 1200 words.
- `## Results` MUST present findings, data, trends, quantitative results, produced code, and option comparisons when relevant. It SHOULD prefer tables, bullet lists, or ASCII art for simple comparisons, and SHOULD use external figures only when they are materially necessary. Keep interpretation to a minimum. It MUST stay under 1800 words.
- When different options for the same problem are being analyzed, `## Results` SHOULD include comparison tables and explicit pros and cons for each option so the trade-offs are directly inspectable.
- `## Discussion` MUST interpret the results, explain significance, trade-offs, performance considerations, limitations, and implications for technical readers. It MUST stay under 1000 words.
- `## Conclusion` MUST summarize the main findings, practical takeaway, applicability boundaries, and important open questions. It MUST stay under 400 words.
- `## References` MUST list all cited literature, websites, tutorials, documentation, discussions, or related artifacts.
- In general, research SHOULD roughly follow the proportion `Introduction : Methods : Results : Discussion ≈ 3 : 5 : 6 : 4`.
- Be strict about the goal of each section. Avoid duplicating the same material across sections and prefer clarity over rhetorical flourishes.
- Research documents SHOULD stay under 5000 words total. They MAY exceed that only when the `## Introduction` explicitly states that the study will be lengthy because a very detailed analysis is required.
- Research documents SHOULD link in `## References` to the XDRs, skills, articles, discussions, and external references relevant to the subject or that later cite the work.
- A 1:1 relationship between one research document and one decision will likely be common in practice, but it is not required.
- One research document MAY also be referenced by multiple XDRs, including a mix of ADRs, BDRs, and EDRs, when the same investigation remains relevant across several decisions.
- Images and other local resource files referenced by a research document SHOULD be used only when they are materially necessary and MUST live in `researches/.assets/` next to the research files.
- Research file names MUST be lowercase. Never use emojis.
- A research document MAY exist before the related XDR is written, or remain after the XDR changes, as long as its status and references stay clear.

**Folder layout**

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        researches/
          [number]-[short-title].md
          .assets/
```

Examples:
- `.xdrs/_local/adrs/principles/researches/001-research-and-decision-lifecycle.md`
- `.xdrs/business-x/adrs/platform/researches/003-api-gateway-options.md`
- `.xdrs/_local/edrs/application/researches/002-model-serving-constraints.md`

**Research numbering**

- Each research document has a number unique within its `scope/type/subject/researches/` namespace.
- Determine the next number by checking the highest number already present in that namespace.
- Never reuse numbers of deleted research documents. Gaps are expected.

**Research template**

All research documents MUST follow this template:

```markdown
# [scope]-research-[number]: [Short Title]

## Abstract

[Single paragraph summarizing the goal, methods, results, and conclusion. Goal: let a quick technical reader understand the question, method, main result, and takeaway. Under 200 words.]

## Introduction

[Describe the problem, context, constraints, known facts, experiences, gaps, assumptions, and objectives.
Prefer bullets, tables, or ASCII art for simple explanations. Use external visuals only when they are materially necessary. Goal: explain the investigated problem, operating context, constraints, and why the subject matters. Under 700 words.]

Question: [Central question of the research]?

## Methods

[Explain how the study was conducted, including design, tools, data sources, and test conditions.
Include enough detail for an experienced professional to reproduce the relevant parts. Goal: make the important parts of the study reproducible. Under 1200 words.]

## Results

[Report findings, data, trends, quantitative results, code artifacts, and option comparisons.
Prefer tables, bullets, or ASCII art for simple comparisons. Use external figures only when they are materially necessary. If multiple options solve the same problem, add comparison tables and explicit pros and cons for each option. Focus on raw findings, not interpretation. Goal: present the raw findings with minimal interpretation. Under 1800 words.]

## Discussion

[Interpret the results, explain significance, trade-offs, performance considerations, limitations, and implications. Goal: interpret the findings for technical readers. Keep this section technically engaged and under 1000 words.]

## Conclusion

[Summarize the main findings, practical takeaway, applicability boundaries, and important open questions. Goal: summarize the main findings and what they mean in practice. Under 400 words.]

## References

[A list of all cited literature, websites, tutorials, documentation, discussions, and related artifacts. Goal: make all cited sources and supporting artifacts traceable.]

- [Related XDR or artifact](relative/path.md) - Why it matters
- [Another related XDR if this research informed multiple decisions](relative/path.md) - Why it matters
```

## Considered Options

- Related research: `001-research-and-decision-lifecycle` (workspace-local research)

* (REJECTED) **Inline long-form analysis inside the XDR** - Put all research and decision text in one file.
  * Reason: Makes XDRs too long, mixes evidence with the adopted rule set, and hurts fast retrieval by humans and AI agents.
* (CHOSEN) **IMRAD-based subject-level research beside XDRs** - Keep exploratory material beside the decisions, skills, and articles it informs, using an IMRAD-inspired structure adapted to company work.
  * Reason: Preserves lifecycle context, keeps the XDR concise, gives readers a predictable structure, and raises evidence quality without demanding full academic rigor.

## References

- [_core-adr-001 - XDRs core](001-xdrs-core.md)
- [_core-adr-003 - Skill standards](003-skill-standards.md)
- [_core-adr-004 - Article standards](004-article-standards.md)
- [005-write-research skill](skills/005-write-research/SKILL.md) - Step-by-step instructions for creating a research document