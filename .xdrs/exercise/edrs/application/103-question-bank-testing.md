---
name: exercise-edr-policy-103-question-bank-testing
description: Defines the simulated-respondent tests that MUST run when the question bank, characteristics, profiles, config or engine change, with their thresholds. Use when changing any exercise registry or the engine, or reading a test report.
apply-to: The exercise registries, config.json, the engine formulas and the test-question-bank skill
valid-from: 2026-11-17
---

# exercise-edr-policy-103: Question bank testing

## Context and Problem Statement

Registry lint (`exercise-edr-policy-102-registry-lint`) finds structural mistakes only. Dry-runs, internal consistency and profile clashes were checked by hand with throwaway simulators, so they were run unevenly and their thresholds were not written down. Changing one Question, Characteristic or Profile can silently shift scores, alpha and the stopping behaviour of other Profiles.

Question: Which simulated tests MUST run after a change, and what makes them pass or fail?

## Decision Outcome

**One reusable skill, `test-question-bank`, runs four simulated-respondent tests (each Profile alone, all Profiles together, Cronbach's alpha, mixed stress) after every change to the bank or engine, with fixed thresholds.**

The tests aim at the Questions and Characteristics, not at the software.

### Details

#### 01-run-on-every-change

The [test-question-bank skill](skills/test-question-bank/SKILL.md) MUST be run, and its report reviewed, whenever a Question, Characteristic, Profile, `config.json` or the engine formulas (`exercise-edr-policy-101-measurement-formulas`) change, before the change is accepted. A FAIL MUST be fixed or the change rejected. A WARN MUST be fixed or justified in the review.

#### 02-respondent-source

Respondents MUST be simulated from the registries: each person has a true level per Profile (none 0, low 0.25, medium 0.5, high 0.75) or a pattern, and answers each Question from the weights of the Characteristics it lists, plus noise, skips, yes-saying and distortion. The tests check keying, weights, routes, arithmetic and measurement. They MUST NOT be presented as evidence of wording quality or of real-world validity; only real respondents can show that.

#### 03-each-profile-alone

For each Profile, the engine MUST be run with only that Profile in scope, with none, low, medium and high levels in equal shares. It MUST FAIL when the correlation between level and profile score is below 0.85 or fewer than 95% of people land within one level of the true one. It MUST WARN when fewer than 80% of sessions reach good enough, when a Characteristic is measured in fewer than 90% of sessions, or when its mean bias exceeds 0.15 in absolute value.

#### 04-all-profiles-together

People holding random levels of every Profile, plus about 5% holding none, MUST be run against the whole bank to find clashes from shared Characteristics. It MUST FAIL when the correlation of a Profile score with the true level is below 0.9. It MUST WARN when the mean absolute bias of a Profile exceeds 0.1, when more than 5% of people with a low true trait read high, or when a Characteristic bias exceeds 0.15.

#### 05-internal-consistency

Cronbach's alpha MUST be computed per Characteristic as defined in `exercise-bdr-policy-604.12-internal-consistency`, with every item presented to every person. Each Profile MUST have its own population where only that Profile varies, with answer noise x1.5 and 1000 people, and a Characteristic listed by several Profiles MUST be tested in each. It MUST FAIL when alpha is below 0.70. It MUST WARN when alpha is above 0.90, with fewer than 3 items, with fewer than 30 complete respondents, or when no Profile lists the Characteristic.

Simulated alpha mostly reflects the noise setting and the item count, so a HIGH result is a signal to review redundancy, not proof of it.

#### 06-mixed-stress

At least 500 people MUST be generated from: none, low, medium and high of each Profile alone and in combinations of two, three or all Profiles; one-domain pockets; patterns that match no Profile; and careless, distorted and invalid respondents. It MUST FAIL on a score that is not a number or is outside its range, and when the mean Profile score does not rise from low to medium to high. It MUST WARN when the strongest Profile is identified for fewer than 80% of honest people with a clear dominant Profile, when more than 10% of neurotypical people score 0.3 or more on some Profile, when the response quality check flags more than 10% of honest people or fewer than 50% of invalid respondents, or when the mean absolute error of honest people exceeds 0.15.

#### 07-report-and-reproducibility

The skill MUST write `report.md` and `results.json` to its run folder and MUST accept a seed so that a run can be reproduced. The thresholds in rules 03 to 06 MUST match `T` in [tests.js](skills/test-question-bank/scripts/tests.js); changing one MUST change the other.

#### 08-known-warnings

The `ocd` Profile has six Characteristics, so its margin is wider than that of the large Profiles and it reached good enough in only 62% of sessions with the default `profile_margin_stop` (0.12; median margin 0.114, 90th percentile 0.151). It carries `margin_stop` 0.15 (92% in the dry-run) as a provisional override. The skill MUST apply the Profile override when judging good enough and MUST report a WARN if the rate is still below the threshold, so the override is revisited when the OCD Characteristics or questions change.

## References

- [exercise-edr-policy-101 - Measurement formulas](101-measurement-formulas.md)
- [exercise-edr-policy-102 - Registry lint](102-registry-lint.md)
- [exercise-bdr-policy-604 - Question authoring](../../bdrs/product/604-question-authoring.md)
- [exercise-bdr-policy-605 - Characteristic and profile authoring](../../bdrs/product/605-characteristic-and-profile-authoring.md)
