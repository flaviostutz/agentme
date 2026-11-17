---
name: exercise-edr-policy-101-measurement-formulas
description: Defines how answers become evidence, characteristic scores, confidence states and profile results. Use when implementing or reviewing scoring, stopping logic or the good-enough indicator.
apply-to: The scoring and confidence code of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-edr-policy-101: Measurement formulas

## Context and Problem Statement

Every implementation must compute the same scores and confidence from the same answers, otherwise results cannot be compared or tested.

Question: Which formulas turn answers into scores, confidence states and profile results?

## Decision Outcome

**Evidence = weight x centred answer; a characteristic score is the weight-weighted mean of its non-null evidence in -1..1; confidence comes from non-response, the margin of error and score stability; a profile score is the mean of its characteristic scores, and `weighted_score` is a second profile score that counts Characteristics shared by fewer Profiles more.**

### Details

#### 01-evidence

For each asked Question and each `{id, weight}` in its `characteristics`, evidence for that Characteristic MUST be `weight x centred answer`. The centred answer is the stored answer for `agreement` Questions (-1..1) and `2 x answer - 1` for `frequency` Questions (0..1 becomes -1..1), so the neutral middle of both scales is 0 evidence. The result is in -1..1. When the Question was skipped, the evidence MUST be null. Questions that were never asked MUST NOT appear in the evidence list. Route thresholds keep using the stored answer (`exercise-bdr-policy-602.05-thresholds-use-internal-values`). Each non-null evidence entry MUST keep its weight, because the score and the margin use it as the strength of that entry (`02-characteristic-score`).

#### 02-characteristic-score

For the non-null evidence entries i of a Characteristic, with value `e_i` (the evidence) and weight `w_i`, Score MUST be `sum(e_i) / sum(|w_i|)`, kept in -1..1. Each entry therefore counts in proportion to `|w_i|`: a Question with a low weight on the Characteristic moves the score less than one with a high weight, and with equal weights the score is the plain mean. When there is no non-null evidence the score MUST be null. Scores MUST NOT be rescaled to 0..1.

#### 03-positive-and-negative

Positive MUST list the Questions whose evidence is above 0 and Negative those whose evidence is below 0. Evidence equal to 0 counts in the total and in neither list.

#### 04-uncertainty

Uncertainty MUST be `nulls / total`, where total is the count of evidence entries including nulls. It measures only non-response. With no entries it MUST be null.

#### 05-margin-of-error

With n non-null evidence entries, let `r_i = e_i / |w_i|` (the signed answer, in -1..1), `m` the Score, `V1 = sum(|w_i|)` and `V2 = sum(w_i^2)`. The weighted sample standard deviation MUST be `s = sqrt(sum(|w_i| x (r_i - m)^2) / (V1 - V2 / V1))`, the effective count `n_eff = V1^2 / V2`, and Margin of error MUST be `1.96 x s / sqrt(n_eff)`. With equal weights this is `1.96 x s / sqrt(n)` with s the sample standard deviation (n-1). Margin MUST be unknown, and treated as high, when n is below `min_answered` (`exercise-adr-policy-202.05-config-keys`).

#### 06-characteristic-state

The state of a Characteristic MUST be the first that applies:
1. `given_up` when the evidence list has at least `giveup_min_asked` entries (nulls included) and Uncertainty >= `uncertainty_giveup`.
2. `settled` when Margin is known, and either Margin <= `margin_stop` or the score is stable (`09-score-stability`), and the balancing condition holds: the absolute score is at most `balancing_min_score`, or at least one balancing Question carrying the Characteristic with a negative weight has been asked (answered or skipped), or the registry has no such Question.
3. `open` otherwise, including when there is no evidence entry at all.

The balancing condition keeps counter-evidence from being skipped when a Characteristic shows a clear signal. A Characteristic with a weak or neutral score does not need counter-evidence, and one that has no balancing Question in the bank is never blocked.

#### 07-profile-result

For a Profile, evaluated Characteristics are those with a non-null score. Profile score MUST be the mean of the evaluated scores in -1..1, with each Characteristic counted once per Profile. Profile coverage MUST be evaluated count / total count.

Profile margin MUST be `1.96 x sqrt(sum of se^2) / k`, where k is the evaluated count and `se` of a Characteristic is `s / sqrt(n_eff)` with s and n_eff as in `05-margin-of-error` when n >= `min_answered`, or `evidence_sd / sqrt(n)` otherwise. With no evaluated Characteristic the Profile margin MUST be unknown. This margin measures only answer noise, assumes independent errors between Characteristics and says nothing about whether the Profile is a valid measure; results MUST NOT present it as more than that (`exercise-bdr-policy-603`).

#### 08-good-enough

A Profile is well explored when all of these hold, counting over all Characteristics listed in the Profile, including those without evidence:
1. At least `profile_measured_ratio` of them have at least `min_answered` non-null evidence entries.
2. At least `profile_settled_ratio` of them are `settled` or `given_up`.
3. The Profile margin is known and <= `profile_margin_stop`.
4. The response quality flag (`11-response-quality`) is not raised.

Good enough MUST be true when at least one analysed Profile (`exercise-adr-policy-101.10-analysed-profiles`) has an evaluated Characteristic and every analysed Profile that has one is well explored. It is only an indicator: it MUST NOT end the session.

#### 09-score-stability

A Characteristic score MUST be treated as stable when it has more than `stability_window` non-null evidence entries and, for each of the last `stability_window` entries, the running weighted mean (`02-characteristic-score` applied to the non-null evidence up to and including that entry) differs from the current score by at most `stability_delta`. Stability lets a Characteristic settle when its answers are consistent even if the Margin is still above `margin_stop` because of few entries.

#### 10-weighted-profile-score

Besides the Profile score (`07-profile-result`), results MUST compute `weighted_score` for each analysed Profile, which counts Characteristics that belong to fewer Profiles more than shared ones. Let P be the number of analysed Profiles (`exercise-adr-policy-101.10-analysed-profiles`) and `k_c` the number of analysed Profiles that list Characteristic c. The profile weight of c MUST be `pw_c = (P - k_c + 1) / P`, so a Characteristic listed by one analysed Profile has weight 1 and one listed by every analysed Profile has weight `1 / P`; with a single analysed Profile every weight is 1 and `weighted_score` equals the Profile score. For the evaluated Characteristics c of the Profile with Characteristic score `s_c`:
- `weighted_score` MUST be `sum(pw_c x s_c) / sum(pw_c)`, in -1..1.
- `weighted_score` Margin MUST be `1.96 x sqrt(sum(pw_c^2 x se_c^2)) / sum(pw_c)`, with `se_c` as in `07-profile-result`.
- It MUST be null, and its margin unknown, when no Characteristic is evaluated.

The weight is derived from Profile membership in the registries and from the analysed Profiles at the time of calculation, so it changes when a Profile is added or removed. The Profile does not store it (`exercise-adr-policy-201.05-profile-is-a-flat-list`) and the Characteristic score is not affected. `weighted_score` does not replace the Profile score and MUST NOT be used by `08-good-enough`.

#### 11-response-quality

The engine MUST raise a response quality flag when at least `quality_min_characteristics` Characteristics have at least `min_answered` non-null evidence entries and any of these holds:
1. **Scattered:** the mean margin of those Characteristics is above `quality_margin_max`.
2. **Keying:** over the Characteristics that have both positive-weight and negative-weight non-null entries, the mean of the absolute difference between the mean `sign(weight) x centred answer` of the positive entries and the same mean of the negative entries is above `quality_keying_max`. Honest answers agree after the sign is applied; yes-saying, no-saying and random answers do not.
3. **Flat:** the population standard deviation of those Characteristic scores is below `quality_spread_min` and the absolute mean of those scores is at most `quality_flat_max_mean`.

The flag MUST NOT change any score or margin and MUST NOT end the session. It only means the answers do not look like one consistent person, so the Profile results MUST NOT be reported as well explored (`08-good-enough`) and the results MUST show a neutral notice (`exercise-bdr-policy-603`). It cannot detect consistent but inverted answers, masking or most extreme responding.

#### 12-rationale-from-dry-runs

These formulas were tuned by dry-running the engine (`exercise-adr-policy-101`) with simulated respondents on the draft registries: known severity per Profile, answer noise, 3% skips, 60-100 sessions per case. What each run showed:
- Uncentred frequency answers inflated scores (a neutral respondent scored +0.17), so evidence is centred (`01-evidence`).
- With a plain mean, low-weight secondary evidence pulled scores toward 0 (true severity 0.75 read 0.60, about -0.12 from weights alone), so the score and margin are weighted (`02-characteristic-score`, `05-margin-of-error`). Now 0.75 reads about 0.70 and 0.5 reads about 0.48.
- A `margin_stop` of 0.15 was unreachable with about 8 Questions per Characteristic, so `margin_stop` is 0.25 and score stability can settle a Characteristic (`06-characteristic-state`, `09-score-stability`).
- One skip could mean `given_up` and good enough after a single Question, so `given_up` needs `giveup_min_asked` entries.
- Requiring a balancing Question for every Characteristic kept sessions long (about 227 vs 183 Questions, same scores), so it is required only above `balancing_min_score`.
- A good aggregate Profile margin can hide uneven sampling, so a Profile is well explored only when enough of its Characteristics are measured and settled (`08-good-enough`).
- A weight-normalised per-Characteristic margin made no difference and was not adopted.
- Profiles share many Characteristics (15 of 28-30 for ADHD and autism, 12-14 for the others), so a Profile at none rose to about 0.35 when the other two were high. Specificity weights (`10-weighted-profile-score`) lowered that to about 0.24 and made the levels easier to tell apart (500 simulated respondents, same answers): the chance that a higher level scores above a lower one rose from 0.81 to 0.92 between none and low and from 0.85 to 0.92 between low and medium, and the share of respondents classified in the right level (cut points from the pooled level means) rose from 69% to 79%. The Profile score is kept because it also reflects the shared Characteristics; `weighted_score` has a larger margin (about 0.064 vs 0.058) because fewer Characteristics weigh fully.
- A stress test (1000 respondents in 21 archetypes: honest, distorted and invalid; seed 7) found that random, yes-saying, no-saying, midpoint and straight-line respondents were declared well explored in 0-100% of cases while their scores were meaningless (yes-sayers read about 0.55 on every Profile, random and midpoint respondents about 0). The margin looked fine because it only measures noise. Keying disagreement, mean margin and flat spread separated these respondents from honest ones (AUC near 1.0), so `11-response-quality` combines them. Thresholds are the 95th percentile (5th for spread) of honest respondents, except `quality_margin_max`, loosened from 0.50 to 0.55 to cut honest false alarms (7% to 4%) at the cost of random-answer detection (100% to 84%); at 0.60 fewer than half of random respondents were flagged. With the flag all five invalid archetypes were flagged in 100% of cases, flip-floppers 79%, fatigued respondents 56% and extreme responders 24%; honest false alarms were 7% (19% for neurotypical and 16% for one-domain profiles, because their answers really are scattered) and 6% on a second seed. Contrarians (consistent but inverted answers) and maskers were not detectable (0-6%) and remain a limit. At twice the answer noise 69% of honest respondents were flagged, which is the intended behaviour for very noisy answers, but shows the thresholds are only valid for the simulated noise.
- Balancing Questions (`exercise-bdr-policy-604.11-reverse-keyed-pairs`) were added so each Characteristic with six or more Questions has two reverse-keyed ones: yes-sayers fell from about 0.55 to about 0.47 per Profile, with sessions about 2 Questions longer on average and honest fidelity unchanged (bias -0.06, RMSE 0.12, correlation 0.95).
- A severe respondent (true 0.84) reads about 0.70 and about 0.78 at half the noise, so part of the compression comes from simulated answer clamping and quantisation. Calibrating the high end needs real answers.

The respondents are assumptions, not real people, and the margin captures only answer noise. The values in `exercise-adr-policy-202.05-config-keys` MUST be recalibrated with real answers before the results are treated as validated.

## References

- [exercise-adr-policy-101 - Question flow engine](../../adrs/application/101-question-flow-engine.md)
- [exercise-adr-policy-202 - Registries](../../adrs/data/202-registries.md)
- [exercise-bdr-policy-602 - Response scales](../../bdrs/product/602-response-scales.md)
