---
name: exercise-bdr-policy-602-response-scales
description: Defines the 5-point scales shown to the user and the internal values they map to. Use when building the answer input, converting answers or writing route thresholds.
apply-to: Answer input, answer storage and route thresholds of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-bdr-policy-602: Response scales

## Context and Problem Statement

Users answer on a familiar scale, but the engine computes with simple numeric ranges. Both must be defined once. Five choices are used instead of seven because the Question flow is long and adaptive: simulated respondents showed almost no precision loss from 7 to 5 points (profile score correlation with the true value 0.978 against 0.976, margin 0.072 against 0.077), while fewer choices are quicker to decide on and have clearer labels. Real answers MUST confirm this (`exercise-edr-policy-101.13-recalibrate-with-real-answers`).

Question: Which choices does the user see and which values does the engine store?

## Decision Outcome

**5-point choices with a neutral middle in the user experience; internally agreement is -1..1 and frequency is 0..1, evenly spaced and rounded to 2 decimals.**

### Details

#### 01-agreement-scale

An `agreement` Question MUST offer 5 choices, mapped in order to -1, -0.5, 0, 0.5, 1: strongly disagree, disagree, neutral, agree, strongly agree.

#### 02-frequency-scale

A `frequency` Question MUST offer 5 choices, mapped in order to 0, 0.25, 0.5, 0.75, 1: never, rarely, sometimes, often, always.

#### 03-internal-values-only

The 5-point scale MUST exist only in the user experience. Storage, scoring, routes and thresholds MUST use the internal values.

#### 04-skip-is-always-available

Every Question MUST offer a skip choice that stores null. Skip MUST NOT be presented as a point on the scale.

#### 05-thresholds-use-internal-values

Route thresholds MUST use values of the Question's own range (agreement -1..1, frequency 0..1) and MUST be one of the values of its scale (`01-agreement-scale`, `02-frequency-scale`). Comparisons MUST use the stored 2-decimal value.

## References

- [exercise-adr-policy-201 - Domain model](../../adrs/data/201-domain-model.md)
- [exercise-edr-policy-101 - Measurement formulas](../../edrs/application/101-measurement-formulas.md)
