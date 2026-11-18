---
name: exercise-bdr-policy-605-characteristic-and-profile-authoring
description: Defines how characteristics and profiles are written and related in the exercise registries. Use when adding or changing a characteristic or a profile.
apply-to: All Characteristics and Profiles in the exercise registries
valid-from: 2026-11-17
---

# exercise-bdr-policy-605: Characteristic and profile authoring

## Context and Problem Statement

Questions are weighted against characteristics, and results are grouped by profiles. Both registries need predictable fields and meanings.

Question: What must a characteristic and a profile contain?

## Decision Outcome

**A characteristic has an id, name, description, one domain and a source; a profile has an id, name, description, reference, a list of characteristics and optional comments.**

### Details

#### 01-characteristic-fields

A Characteristic MUST have `id` (snake_case, at most 7 words), `name` (required, at most 14 words), `description` (required, at most 39 words), `domain` (one value from `exercise-adr-policy-201.02-domain-is-a-fixed-list`) and `source` (required, at most 19 words, see `07-characteristic-source`). These limits are checked by `exercise-edr-policy-102`.

#### 02-characteristic-description-is-the-reference

The description MUST state what the Characteristic means in daily experience. It is the reference used for dry-runs when authoring Questions (`exercise-bdr-policy-604.09-dry-run-before-accept`).

#### 03-specializations

A specialization MUST be a separate Characteristic whose id starts with the id of the broader one when it exists (for example `repetitive_movement_motor_soothing`) and whose description states what makes it more specific. It MUST NOT link to its parent (`exercise-adr-policy-201.04-specializations-are-independent-characteristics`).

#### 04-profile-fields

A Profile MUST have `id` (snake_case, at most 3 words), `name` (at most 9 words), `description` (at most 29 words), `reference` (at most 29 words: a URL or citation), `characteristics` (a list of Characteristic ids) and, when `08-profile-comments` applies, `comments` (at most 49 words).

#### 05-membership-is-a-claim

A Characteristic's membership in a Profile is a claim and MUST come from the Profile's `reference` or another cited source. Unverified memberships MUST be listed in the review notes of the change that adds them. A Characteristic MAY belong to many Profiles.

#### 06-profile-without-weights

Profiles MUST NOT define weights or thresholds. A more specific Characteristic adds more evidence to a Profile by being listed in it. Because `weighted_score` weights a Characteristic by how few Profiles list it (`exercise-edr-policy-101.10-weighted-profile-score`), adding or removing a membership changes the weights of that Characteristic in every Profile.

#### 07-characteristic-source

The `source` of a Characteristic MUST say in at most 19 words where the concept was inspired, absorbed, adapted or used directly, starting with "Inspired by", "Absorbed from", "Adapted from" or "Used from". It SHOULD cite the most scientific source found that names or organises the concept (authors, year, journal and pages, or an instrument and item numbers). When no such source is found it MUST be exactly "no reference". A cited source MUST be checked for existence and bibliographic data, and MUST be worded as inspiration when it does not prove the Characteristic. A `source` MUST NOT claim that a Profile contains the Characteristic (`05-membership-is-a-claim`).

#### 08-profile-comments

When the paper or instrument behind a Profile (`reference`, `exercise-adr-policy-203`) could not be fully implemented in the bank, the Profile MUST carry `comments` of at most 49 words saying what was left out or changed, for example scoring, cut-offs, time windows, rating dimensions, subscales or items that were reworded or merged. When a Profile has no instrument behind it, `comments` MUST say so. A Profile whose source was implemented in full MAY omit `comments`. Comments describe the implementation only; they MUST NOT claim that a Profile contains a Characteristic (`05-membership-is-a-claim`).

## References

- [exercise-adr-policy-201 - Domain model](../../adrs/data/201-domain-model.md)
- [exercise-adr-policy-203 - Reference instruments](../../adrs/data/203-reference-instruments.md)
- [exercise-bdr-policy-604 - Question authoring](604-question-authoring.md)
- [exercise-edr-policy-102 - Registry lint](../../edrs/application/102-registry-lint.md)
