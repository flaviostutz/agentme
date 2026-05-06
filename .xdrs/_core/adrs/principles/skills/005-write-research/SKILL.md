---
name: 005-write-research
description: >
  Creates a new research document following XDR research standards: selects scope, type, subject, and number;
  then writes an IMRAD-based study with enough evidence and method detail to stand on its own as a technical paper.
  Activate this skill when the user asks to create, add, or write a research document that backs a decision.
metadata:
  author: flaviostutz
  version: "1.4"
---

## Overview

Guides the creation of a well-structured research document by following `_core-adr-006`, consulting `xdr-standards` for every core element definition, checking related XDRs and existing research to avoid duplication, and producing an IMRAD-based study that reads as a standalone technical paper. Treat each section goal in the research template as an acceptance criterion, not as optional wording. Do not assume missing direction, evidence, or intended follow-up; ask the user explicitly before proceeding when those points are not already concrete.

This skill is interactive by design. Ask clarifying questions to the user at each phase where direction, evidence, or scope is unclear. Ask sequentially — one focused set of questions at a time — and wait for the user's answers before advancing to the next phase. Never front-load all questions at once if not all are yet relevant.

## Instructions

### Phase 1: Understand the Research Goal

1. Read `.xdrs/_core/adrs/principles/006-research-standards.md` in full to internalize the folder layout, numbering rules, and mandatory template.
2. Read `.xdrs/_core/adrs/principles/001-xdrs-core.md` in full before defining the research document's core elements. Treat it as the canonical source for how to choose and write type, scope, subject, numbering expectations, naming constraints, and folder placement.
3. Ask the user to confirm the intended direction of the research before planning the document: what decision, question, or option space the study should support, what boundaries or exclusions apply, and what kind of outcome they expect. Wait for the answers before proceeding.
4. Ask the user what evidence already exists and what evidence-gathering methods are acceptable if the current evidence is incomplete. Do not invent facts, sources, or confidence that the user did not provide. Wait for the answers before proceeding.
5. Ask the user what the proposed next step is after the research, such as writing a new XDR, updating an existing XDR, informing a discussion, or documenting trade-offs for later. Use that answer to shape the framing without turning the research into the final decision. Wait for the answers before proceeding.
6. Identify the problem or question being explored, the relevant system or domain context, the likely technical audience, and why the subject matters in practice.
7. Internalize the goal of each required section before drafting: `Abstract` gives a quick technical reader the question, method, main result, and takeaway, `Introduction` frames the investigated problem and context, `Methods` makes the important parts reproducible, `Results` records raw findings with minimal interpretation, `Discussion` interprets the findings, `Conclusion` summarizes the practical takeaway and boundaries, and `References` makes sources traceable.
8. Collect the main constraints, known facts, important experiences, gaps, and assumptions that belong in the introduction.
9. Do NOT proceed without a clear problem statement, a central question, explicit user direction, an understood next step, and at least one credible source of evidence or a method for generating it. If any of these are ambiguous, use `vscode_askQuestions` to ask the user instead of assuming. After receiving answers, evaluate whether any response introduces new ambiguity and, if so, ask a follow-up set of questions before proceeding.

### Phase 2: Select Scope, Type, Subject, and Number

If the answers from Phase 1 leave scope, type, or subject ambiguous, use `vscode_askQuestions` to present the candidate options with a brief rationale for each and ask the user to confirm the selection before proceeding. If the user's answer raises a related uncertainty, ask a follow-up question to resolve it before locking the selection.

Consult `001-xdrs-core` while making each choice in this phase. The summaries below are orientation only; when any detail matters, the standard decides.

**Scope** — use `_local` unless the user explicitly names another scope.
- If the user names a scope other than `_local`, check the workspace root `.filedist` file. If any file under `.xdrs/[scope]/` appears in `.filedist`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

**Type** — match the type of decision this research supports (`adrs`, `bdrs`, or `edrs`). Use the same rules as `002-write-xdr` Phase 2:
- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure, pipelines

**Subject** — pick the most specific subject that matches the problem domain (required list per type is in `_core-adr-001`).

**Research number** — scan `.xdrs/[scope]/[type]/[subject]/researches/` for the highest existing number and increment by 1. Never reuse numbers from deleted research documents.

### Phase 3: Research Existing Artifacts

1. Read relevant XDRs across all scopes listed in the XDR root `index.md`.
2. Evaluate XDR metadata before treating any decision as current context. All documents present in the collection are considered active. `validFrom:` determines the convergence date for adoption, `applyTo:` determines whether the decision fits the intended task context, and the decision text defines any remaining boundaries. Keep out-of-window or out-of-scope XDRs as background only.
3. Read existing research documents in the same or overlapping subjects to avoid duplicating the same study.
4. Read related skills or articles if they contain context, implementation limits, or terminology that must be reflected.
5. Collect links that should appear in the final `## References` section.

### Phase 4: Create the Skeleton and Frame the Study

1. Create the final section skeleton in the research file before running the study: `Abstract`, `Introduction`, `Methods`, `Results`, `Discussion`, `Conclusion`, `References`.
2. Write a one-line note under each section heading capturing that section's goal before filling in the content so the draft stays disciplined.
3. Draft `## Introduction` early so the problem, scope, constraints, assumptions, and central question are fixed before evidence collection expands. If the central research question is still unclear after Phase 1, use `vscode_askQuestions` to confirm it in a single focused question before drafting the introduction. If the answer reveals further ambiguity, ask one more targeted follow-up before proceeding.
4. Draft `## Methods` before or while executing the study so tools, data sources, and conditions are captured while they are still precise. If the study design is uncertain, use `vscode_askQuestions` to clarify which methods or data sources are applicable before committing to a design. Follow up if the answer leaves the design still unclear.
5. Treat `## Abstract` as a late-stage summary. Do not try to finalize it yet.
6. Keep process framing out of the body. If related ADRs or repository context matter, push that traceability to `## References` unless it is essential to the technical question itself.

### Phase 5: Capture Evidence as the Study Runs

If at any point during evidence collection a significant gap appears, an assumption cannot be verified, or a new branch of the question emerges, pause and use `vscode_askQuestions` to ask the user a focused question before continuing. If the answer resolves one gap but reveals another, ask a follow-up question immediately. Do not proceed past a critical gap by guessing.

1. As experiments, comparisons, code spikes, interviews, benchmarks, or document reviews happen, append the concrete findings to `## Results` continuously.
2. Prefer capturing tables, bullet points, numbers, code outputs, and option comparisons while the evidence is fresh.
3. If multiple options solve the same problem, add a comparison table and explicit pros and cons for each option in `## Results` so the trade-offs are directly inspectable.
4. Update `## Methods` whenever the actual study design changes so the final document remains reproducible.
5. Keep interpretation out of `## Results`; record observations first and save meaning-making for `## Discussion`.

### Phase 6: Synthesize After Results Stabilize

If the results contain competing interpretations or the intended audience for the conclusions is unclear, use `vscode_askQuestions` to ask the user a focused question before writing the discussion. Keep the question specific to a single open point. If the answer raises a further interpretive uncertainty, ask one targeted follow-up before writing.

1. Write `## Discussion` only after the important findings are visible in `## Results`.
2. Use `## Discussion` to interpret significance, trade-offs, limitations, implications, and performance considerations for technical readers.
3. Write `## Conclusion` after the discussion so it reflects the actual findings, practical takeaway, applicability boundaries, and open questions.
4. Write `## Abstract` last so it accurately summarizes the final goal, methods, results, and conclusion for quick technical readers.

### Phase 7: Write the Research Document

Use the mandatory template from `006-research-standards`:

```markdown
# [scope]-research-[number]: [Short Title]

## Abstract

[Single paragraph summarizing the goal, methods, results, and conclusion. Goal: let a quick technical reader understand the question, method, main result, and takeaway. Under 200 words.]

## Introduction

[Describe the problem, context, constraints, known facts, experiences, gaps, assumptions, and objectives.
Use visuals, bullets, graphs, or diagrams when helpful. Goal: explain the investigated problem, operating context, constraints, and why the subject matters. Under 700 words.]

Question: [Central question of the research]?

## Methods

[Explain how the study was conducted, including design, tools, data sources, and test conditions.
Include enough detail for an experienced professional to reproduce the relevant parts. Goal: make the important parts of the study reproducible. Under 1200 words.]

## Results

[Report findings, data, trends, quantitative results, code artifacts, and option comparisons.
Use figures, tables, or bullets when useful. If multiple options solve the same problem, add comparison tables and explicit pros and cons for each option. Focus on raw findings, not interpretation. Goal: present the raw findings with minimal interpretation. Under 1800 words.]

## Discussion

[Interpret the results, explain significance, trade-offs, performance considerations, limitations, and implications. Goal: interpret the findings for technical readers. Keep this section technically engaged and under 1000 words.]

## Conclusion

[Summarize the main findings, practical takeaway, applicability boundaries, and important open questions. Goal: summarize the main findings and what they mean in practice. Under 400 words.]

## References

[A list of all cited literature, websites, tutorials, documentation, discussions, and related artifacts. Goal: make all cited sources and supporting artifacts traceable.]

- [Related XDR or artifact](relative/path.md) - Why it matters
- [Another related XDR if this research informed multiple decisions](relative/path.md) - Why it matters
```

Rules:
- Treat the goal sentence of each section as a hard check on what belongs in that section.
- Focus on exploring and evidencing the problem space; do not turn the document into the final decision.
- Write as a standalone technical paper for readers who do not know the XDR process.
- Keep mentions of future ADRs, decision lifecycle, repository process, or artifact management out of the body unless they are materially necessary to understand the research question.
- Keep traceability to related XDRs, skills, articles, discussions, and external sources primarily in `## References`.
- Use good-enough evidence. Experienced professional judgment is allowed, but the conclusions still need support that other colleagues can inspect and learn from.
- Ensure the methods and test conditions are reproducible enough for an experienced professional to rerun or evolve the critical parts later.
- Prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams), bullet points, or ASCII art for simple explanations and comparisons, especially in the introduction and results.
- If the research genuinely needs local images or supporting files, store them in `.xdrs/[scope]/[type]/[subject]/researches/.assets/` and link them using a same-folder relative path (e.g., `.assets/image.png`).
- Use relative paths for all links; never use absolute paths starting with `/`.
- Keep section word limits within the standard and keep the document under 5000 words total unless the introduction explicitly states that a very detailed analysis is required.

### Phase 8: Check Section Goals

Before the final review, verify each section against its specific goal:

1. **Abstract goal**: Does it let a quick technical reader understand the question, method, main result, and takeaway, in one paragraph and under 200 words?
2. **Introduction goal**: Does it explain the investigated problem and context, stay within scope, and end with `Question: ...?`?
3. **Methods goal**: Could an experienced professional reproduce the important parts that materially affect the conclusion?
4. **Results goal**: Are the findings concrete and minimally interpreted, with comparisons and pros/cons when multiple options exist?
5. **Discussion goal**: Does it interpret the findings rather than repeat the results?
6. **Conclusion goal**: Does it summarize the main findings, practical takeaway, applicability boundaries, and open questions without introducing new evidence?
7. **References goal**: Are cited sources and related artifacts traceable, including related XDRs, skills, articles, and research where relevant?

If any section fails its goal, revise that section before continuing.

### Phase 9: Check Word Counts and Ratios

Before the final review, run a word-count pass over the draft and verify that the main body roughly follows the standard proportion `Introduction : Methods : Results : Discussion ≈ 3 : 5 : 6 : 4`.

1. Count words by top-level `##` section after stripping Markdown syntax so lists, tables, and links count as prose rather than punctuation.
2. Compare only `Introduction`, `Methods`, `Results`, and `Discussion` for the ratio check.
3. Use these target shares of the main body: `Introduction = 16.7%`, `Methods = 27.8%`, `Results = 33.3%`, `Discussion = 22.2%`.
4. Treat any section as out of ratio when its share differs by more than 25% from its target share, unless the `## Introduction` explicitly justifies a very detailed or intentionally unbalanced analysis.
5. If the ratio check fails, rebalance the draft before final review instead of accepting the imbalance silently.
6. Use this Python script when you need a fast deterministic check:

```python
from pathlib import Path
import re

path = Path(".xdrs/[scope]/[type]/[subject]/researches/[number]-[short-title].md")
text = path.read_text(encoding="utf-8")

sections = {}
current = None
for line in text.splitlines():
  if line.startswith("## "):
    current = line[3:].strip()
    sections[current] = []
    continue
  if line.startswith("# "):
    continue
  if current is not None:
    sections[current].append(line)


def count_words(markdown: str) -> int:
  cleaned = markdown
  cleaned = re.sub(r"^\|(?:\s*[-:]+\s*\|)+\s*$", " ", cleaned, flags=re.M)
  cleaned = re.sub(r"```[\s\S]*?```", " ", cleaned)
  cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
  cleaned = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", cleaned)
  cleaned = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cleaned)
  cleaned = re.sub(r"^#+\s+", "", cleaned, flags=re.M)
  cleaned = re.sub(r"[|*_>#-]", " ", cleaned)
  cleaned = re.sub(r"[^\w'’]+", " ", cleaned, flags=re.UNICODE)
  words = cleaned.strip().split()
  return len(words)


targets = {
  "Introduction": 3,
  "Methods": 5,
  "Results": 6,
  "Discussion": 4,
}

counts = {name: count_words("\n".join(lines)) for name, lines in sections.items()}
total_words = sum(counts.values())
body_total = sum(counts.get(name, 0) for name in targets)
target_weight_total = sum(targets.values())

print(f"TOTAL\t{total_words}")
for name, count in counts.items():
  print(f"{name}\t{count}")

print("\nRATIO CHECK")
for name, weight in targets.items():
  actual_share = counts.get(name, 0) / body_total if body_total else 0
  target_share = weight / target_weight_total
  delta = ((actual_share - target_share) / target_share) if target_share else 0
  status = "OK" if abs(delta) <= 0.25 else "REVISE"
  print(
    f"{name}: actual={actual_share:.1%} target={target_share:.1%} delta={delta:+.1%} {status}"
  )
```

### Phase 10: Review the Draft

Before writing files, verify:

1. **Problem clarity**: Is the research question explicit?
2. **Section discipline**: Does each section contain the right kind of content with minimal duplication?
3. **Method quality**: Could an experienced professional reproduce or extend the important parts of the study from the methods section?
4. **Evidence quality**: Are the results concrete enough to support the discussion and conclusion?
5. **Standalone focus**: Does the text read as a technical paper rather than commentary about future ADRs, repository process, or artifact management?
6. **Ratio fit**: Does the document stay within section word limits and pass the Python ratio check, or does the introduction explicitly justify the deviation?
7. **References**: Are all related XDRs, research docs, skills, articles, and external sources linked when relevant?

If any check fails, revise before continuing.

### Phase 11: Write Files

1. Create the research file at `.xdrs/[scope]/[type]/[subject]/researches/[number]-[short-title].md`.
2. Add an entry to `.xdrs/[scope]/[type]/index.md`.
3. Add back-references from the related XDR, article, or skill when the relationship is important for discovery.
4. Evaluate whether the scope index at `.xdrs/[scope]/index.md` should be updated to reflect the new research. If the scope index does not exist, create it following article standards and the scope index rules in `_core-adr-001`.

## Examples

**Input**: "Create research comparing package distribution options for our XDR scopes"

**Expected actions:**
1. Read `006-research-standards.md`.
2. Choose type `adrs` and subject `principles`.
3. Scan `.xdrs/_local/adrs/principles/researches/` for the next number.
4. Read related XDRs about packaging and versioning.
5. Write an IMRAD-based research document comparing options such as npm package, git submodule, and copy-paste distribution, with the comparison grounded in methods and results.
6. Add references to the resulting XDR if a decision is later created.

## Edge Cases

- If the user is really asking for a final decision, write an XDR instead of research.
- If only one viable option exists, still explain what was evaluated, what was ruled out, or what constraints removed the alternatives.
- If the document grows too large, split independent problem threads into separate research files unless the introduction explicitly justifies a longer study.
- If the supported decision does not exist yet, reference the decision topic or planned XDR title in the introduction and conclusion.
- If the user's direction, evidence base, or intended next step is vague, ask follow-up questions and wait for clarification instead of choosing a path yourself.

## References

- [_core-adr-006 - Research standards](../../006-research-standards.md)
- [_core-adr-001 - XDRs core](../../001-xdrs-core.md)
- [002-write-xdr skill](../002-write-xdr/SKILL.md)

## Constraints

- MUST consult `001-xdrs-core` as the canonical source for every core element definition, especially type, scope, subject, numbering, naming, and placement.
- MUST follow the research template and section-goal rules from `006-research-standards`.
- MUST keep scope `_local` unless the user explicitly states otherwise.
- MUST NOT create documents in external scopes (scopes whose files appear in the workspace root `.filedist`).
- MUST keep the document as research rather than turning it into a final decision.
ing it into a final decision.
