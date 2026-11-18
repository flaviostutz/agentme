---
name: exercise-bdr-policy-603-results-presentation
description: Defines what the user sees about their characteristics and profiles, while answering and at the end. Use when designing or reviewing the results screen or any text that reports scores.
apply-to: Results and progress views of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-bdr-policy-603: Results presentation

## Context and Problem Statement

Results are the part of the system that can mislead most. They must be understandable, honest about confidence and consistent with the measurement formulas.

Question: What must results show and what must they avoid?

## Decision Outcome

**Results show characteristic scores grouped by domain, profile scores and weighted scores with coverage and confidence, and the good-enough indicator, in neutral language.**

### Details

#### 01-available-any-time

Results MUST be available after any number of answers. The good-enough indicator (`exercise-edr-policy-101.08-good-enough`) MUST be shown, and the user MUST be able to keep answering after it turns true while confidence improves.

#### 02-characteristic-results

For every Characteristic with a non-null score, results MUST show its Domain, its score on the -1..1 scale (not as a percentage), its state (`open`, `settled`, `given_up`) and the Questions in Positive and Negative.

#### 03-profile-results

For every analysed Profile (`exercise-adr-policy-101.10-analysed-profiles`), results MUST show the score and the `weighted_score` (`exercise-edr-policy-101.10-weighted-profile-score`) on the -1..1 scale, each with its margin, the coverage and whether the Profile is well explored (`exercise-edr-policy-101.08-good-enough`). Results MUST explain `weighted_score` as the score that gives more weight to Characteristics that fewer Profiles share. A Profile with no evaluated Characteristic MUST be shown as "not enough answers". The margins MUST be described as the effect of answer noise only, not as a measure of validity.

#### 04-confidence-is-visible

Margin of error and unknown confidence MUST be visible next to every score. A score MUST NOT be shown without its confidence.

#### 05-guardrails-apply

All text MUST follow `exercise-bdr-policy-601`, including neutral wording and no probability language.

#### 06-follow-up-suggestions

Results MAY suggest what to explore next, such as reviewing the Characteristics with the highest scores or talking to a professional. Suggestions MUST NOT include diagnostic statements.

#### 07-response-quality-notice

When the response quality flag is raised (`exercise-edr-policy-101.11-response-quality`), results MUST keep showing every score and margin and MUST add a neutral notice that the answers look inconsistent, so the scores may not describe the person, and that answering again more carefully may help. The notice MUST NOT accuse the user of lying or carelessness and MUST NOT use diagnostic or probability language. The Profile MUST NOT be shown as well explored while the flag is raised. When the flag is not raised the notice MUST NOT be shown, and its absence MUST NOT be presented as proof that the answers are valid.

#### 08-choose-analysed-profiles

Before the first Question the user MUST be able to choose which Profiles to analyse, with every Profile selected by default, and MUST be able to add or remove Profiles at any moment of the session (`exercise-adr-policy-101.10-analysed-profiles`). The answers already given MUST be kept and MUST be explained as reused when a Profile is added again or later. Results MUST say which Profiles are being analysed and MUST NOT show scores as Profile results for Profiles that are not analysed; the user MUST NOT be told a Profile was "ruled out" because it is not analysed. The user MUST be told that the next questions change when the selection changes.

#### 10-score-precision-and-weighted-view

Results SHOULD NOT present a score as more exact than a conservative weighted mean whose margin captures answer noise only, and MUST NOT present the margin as evidence of validity. Results MUST show `score` and `weighted_score` side by side and MUST NOT replace one by the other, because shared Characteristics are real signal.

## References

- [exercise-bdr-policy-601 - Purpose and guardrails](601-purpose-and-guardrails.md)
- [exercise-edr-policy-101 - Measurement formulas](../../edrs/application/101-measurement-formulas.md)
