---
name: exercise-bdr-policy-601-purpose-and-guardrails
description: Defines the purpose of the exercise questionnaire system and the non-diagnostic limits it must keep. Use when designing wording, results or features that describe a user in terms of profiles or characteristics.
apply-to: All user-facing content and behaviour of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-bdr-policy-601: Purpose and guardrails

## Context and Problem Statement

The system asks personal questions and groups the answers into profiles. Without clear limits it can be read as a diagnostic tool, which it is not.

Question: What is the system for, and what must it never do?

## Decision Outcome

**A self-reflection aid that asks questions, identifies and details characteristics and groups findings into profiles; it never diagnoses and always reports its uncertainty.**

### Details

#### 01-purpose

The system MUST help a person reflect on their own characteristics by: asking questions to identify characteristics, detailing some of them with follow-up questions and organising the findings into profiles, so the person can continue with their own self-recognition and, if they wish, a professional.

#### 02-no-diagnosis

The system MUST NOT diagnose, label the user as having a condition, or state or imply that a profile is "a match" in a clinical sense.

#### 03-no-probabilities

The system MUST NOT show probabilities, likelihoods or percentages that suggest a chance of a condition.

#### 04-neutral-language

Wording MUST be neutral and tentative, for example "Your answers suggest...". It MUST NOT use alarming, judgemental or certain language.

#### 05-report-uncertainty-and-limits

Results MUST show how confident they are and MUST state that the questions are a draft self-reflection aid, not a validated instrument (`exercise-adr-policy-202.06-catalogue-status-is-draft`).

#### 06-no-neurotypicality-model

The system MUST NOT model a "neurotypical" reference profile. Characteristics and Profiles describe differences only.

#### 07-user-control

Every question MUST be skippable and the user MAY stop at any time without losing the results so far.

## References

- [exercise-bdr-policy-603 - Results presentation](603-results-presentation.md)
- [exercise-adr-policy-202 - Registries](../../adrs/data/202-registries.md)
