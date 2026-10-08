# Interview chart

One chart per invited candidate (unrounded Overall above 5.0), written in Phase 11 of [SKILL.md](../SKILL.md) as `<run>/<candidate-slug>/interview-chart.md`. It is the single sheet the interviewer holds during the interview. Its purpose is to help the interviewer gather the best possible perception of the person: who they really are, and whether they can fill the role. It is not a verdict. A human decides.

## Sources

Build the chart only from:

- the candidate's row in the report: Overall, Base, Credibility, Rationale, Notes, Scenario notes;
- the candidate's redacted markdown files `<run>/.work/md/<candidate-slug>-*.md`;
- the report sections Inputs, Criteria and `Interview aspects`.

Never read the original documents in `<run>/<candidate-slug>/` for the chart, because they still contain protected attributes and photos. Write the chart in the language of the human's request.

## Template

Caps are written as `<N words`: stay below the number. Replace every `<...>` with real content and delete none of the sections.

```markdown
# Interview chart: <Name> (<candidate-slug>)

> Interviewer use only. Confidential; delete with the run folder when hiring ends.
> Flags are topics to explore, not conclusions. Use open questions.

Role: <role> | Overall <x.x> | Base <x.x> | Credibility <x.x>

## Story line
- <years> <education, role or experience> (<20 words)
(fewer than 10 bullets, oldest first)

## Summary
<notes, flags and scores in one paragraph (<50 words)>

## Points
- [+] <strong point> (<source>) (<15 words)
- [-] <weak point> (<source>) (<15 words)
- [?] <doubtful point> (<source>) (<15 words)
(at most 12 bullets in total)

## Questions
1. [<class>] <question> (<20 words)
   - Background: <what in the CV prompts it> (<15 words)
   - Intent: <what the answer tells you> (<15 words)
(at most 7 questions)

## Interview assessment
| Aspect | What to listen for | Score (1-10) | Notes |
|---|---|---|---|
| <aspect 1> | <from the report> | | |
(exactly the 5 aspects of the report, in the same order)
```

## Rules

1. **Header.** Both quoted lines are mandatory and unchanged. The role line repeats the numbers stored in the report, never recomputed.
2. **Story line.**
   - Career-centred: education, then roles and notable experiences in date order, at most 9 bullets, each under 20 words.
   - Merge short or similar stages to stay within the cap.
   - Use only job-relevant facts: employer, role, dates, scope, education. Never birth year, age, nationality, family or marital status, religion, health, or photos.
   - Do not list employment gaps.
3. **Summary.** One paragraph under 50 words that states the overall impression, the main flags and the scores (Overall, Base, Credibility, the weakest and strongest aspect). It follows the report Rationale and must not contradict it.
4. **Points.**
   - One combined list, at most 12 bullets, each under 15 words, marked `[+]` strong, `[-]` weak, `[?]` doubtful (always inside brackets, because a bare `+` or `-` after the bullet dash renders as a nested bullet in markdown). A claim flagged `!` in the report is also a doubtful point: keep the `!` mark so the interviewer sees it was contradicted or impossible.
   - Reuse the wording and the source references of the report Notes. A point not in the Notes needs its own source reference, for example `(cv p2)`.
   - Order: strong, weak, doubtful. Keep every `!`, `?` and negative-scenario item before trimming other points.
5. **Questions.**
   - At most 7, under 20 words each, a free mix of the most relevant. No minimum per class.
   - Every question carries one class label: `experience`, `flagged`, `weak`, `strong` or `personality` (personality match with the role).
   - Every flagged `!` or `?` item and every scenario with a negative adjustment is covered by a question, as long as the cap allows; drop the least relevant questions first.
   - Questions are open, behavioural ("Tell me about a time...") and non-leading. They never accuse or imply that a claim is false.
   - Questions are job-related. Never ask about protected attributes: age, gender, origin, nationality, family plans or status, religion, health, disability, sexual orientation, political opinion.
   - Background: the specific CV fact that prompts the question, under 15 words, with its source.
   - Intent: what the answer helps to judge, under 15 words, for example "tests whether ownership held without a title".
6. **Interview assessment.**
   - The 5 aspects come from the report `## Interview aspects` table, with the same names, order and "what to listen for" text for every candidate of the opportunity. Never add, drop or reword them in a chart.
   - Score and Notes stay empty: the interviewer fills them during the interview, scoring 1 to 10.
7. **Existing chart.** Never overwrite an existing `interview-chart.md`. If it exists, only make sure the report links to it.
8. **Same-name candidates** are told apart by the slug (`-2`) in the title.

## Grounding checks before saving

- Every point, background and story bullet traces to the redacted markdown or the report row.
- Every cap holds: words per bullet, bullets per section, number of questions.
- Counterfactual: would each flag, doubtful point and question hold for a person with a different name, gender, age, origin or background? If not, reword or remove it.
- No protected attribute appears anywhere in the chart.
- Neutral wording: "claims X; conflicts with Y", never "lie", "fake" or "dishonest".

## Thin evidence

- A candidate with only a cover letter or a very short CV gets a shorter story line and fewer points; do not pad. Say so in the Summary ("thin evidence: cover letter only").
- Low Credibility (below 4.0) does not change the format. The flagged questions come first.
- Two CV versions: the story line follows the latest version; one `?` point notes the difference and one flagged question explores it.
- Documents in other languages: keep short quotes in the original language followed by a translation, and write everything else in the report language.

## Example

Synthetic data for a Business Analyst (AI) role at a bank, Ana Silva, Overall 8.2.

```markdown
# Interview chart: Ana Silva (ana-silva)

> Interviewer use only. Confidential; delete with the run folder when hiring ends.
> Flags are topics to explore, not conclusions. Use open questions.

Role: Business Analyst (AI) | Overall 8.2 | Base 7.6 | Credibility 8.2

## Story line
- 2012-2016 BSc Information Systems, University of Porto
- 2016-2019 Junior business analyst, retail bank; payment process specs
- 2019-2022 Business analyst, insurer; claims workflow redesign
- 2022-2026 AI business analyst, ExampleBank; LLM complaint triage
- 2024 Wrote evaluation criteria for the bank's LLM triage pilot

## Summary
Strong AI requirements craft with banking context and consistent claims. Stakeholder conflict handling is thin and BPMN is absent. Overall 8.2: Base 7.6, Credibility 8.2; weakest aspect is Stakeholder management at 6.5.

## Points
- [+] 3 years as AI business analyst at a bank (cv p1)
- [+] Wrote LLM evaluation criteria (cv p2)
- [+] Quantified outcomes in every role (cv p1-2)
- [-] No BPMN or process modelling mentioned (cv p1)
- [-] Conflicts escalated, no resolution shown (cv p1)
- [?] Claims to have led the pilot; team size unstated (cv p2)

## Questions
1. [strong] Walk me through how you defined success for the triage pilot.
   - Background: Wrote evaluation criteria for the LLM triage pilot (cv p2).
   - Intent: Tests depth of AI requirements work beyond the title.
2. [weak] Tell me about a stakeholder conflict you resolved without escalating.
   - Background: Conflicts escalated, no resolution shown (cv p1).
   - Intent: Shows whether conflict handling is a gap or only undocumented.
3. [flagged] What was your role and team size in the triage pilot?
   - Background: Says she led the pilot; team size not stated (cv p2).
   - Intent: Clarifies the real scope of ownership.
4. [experience] How do you document a process when BPMN is not used?
   - Background: No process modelling mentioned (cv p1).
   - Intent: Checks fit with the team's analysis practices.
5. [personality] What makes you decide to push back on a requirement?
   - Background: Moves between banking and insurance domains (cv p1).
   - Intent: Shows judgement and independence under pressure.

## Interview assessment
| Aspect | What to listen for | Score (1-10) | Notes |
|---|---|---|---|
| Ownership | Describes own decisions and results, not only the team's | | |
| Communication under pressure | Stays clear and calm when challenged | | |
| Learning curiosity | Names recent things learned and how | | |
| Collaboration style | Credits others; handles disagreement openly | | |
| Motivation for the role | Concrete reasons tied to this team and product | | |
```
