---
name: exercise-bdr-policy-602-response-scales
description: Defines the 7-point scales shown to the user and the internal values they map to. Use when building the answer input, converting answers or writing route thresholds.
apply-to: Answer input, answer storage and route thresholds of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-bdr-policy-602: Response scales

## Context and Problem Statement

Users answer on a familiar scale, but the engine computes with simple numeric ranges. Both must be defined once.

Question: Which choices does the user see and which values does the engine store?

## Decision Outcome

**7-point choices with a neutral middle in the user experience; internally agreement is -1..1 and frequency is 0..1, evenly spaced and rounded to 2 decimals.**

### Details

#### 01-agreement-scale

An `agreement` Question MUST offer 7 choices, mapped in order to -1, -0.67, -0.33, 0, 0.33, 0.67, 1: strongly disagree, disagree, somewhat disagree, neutral, somewhat agree, agree, strongly agree.

#### 02-frequency-scale

A `frequency` Question MUST offer 7 choices, mapped in order to 0, 0.17, 0.33, 0.5, 0.67, 0.83, 1: never, very rarely, rarely, sometimes, often, very often, always.

#### 03-internal-values-only

The 7-point scale MUST exist only in the user experience. Storage, scoring, routes and thresholds MUST use the internal values.

#### 04-skip-is-always-available

Every Question MUST offer a skip choice that stores null. Skip MUST NOT be presented as a point on the scale.

#### 05-thresholds-use-internal-values

Route thresholds MUST use values of the Question's own range (agreement -1..1, frequency 0..1). Comparisons MUST use the stored 2-decimal value.

## References

- [exercise-adr-policy-201 - Domain model](../../adrs/data/201-domain-model.md)
- [exercise-edr-policy-101 - Measurement formulas](../../edrs/application/101-measurement-formulas.md)
