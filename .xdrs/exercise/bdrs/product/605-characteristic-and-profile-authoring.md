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

**A characteristic has an id, name, description and one domain; a profile has an id, name, description, reference and a list of characteristics.**

### Details

#### 01-characteristic-fields

A Characteristic MUST have `id` (snake_case, at most 7 words), `name` (required, at most 14 words), `description` (required, at most 39 words) and `domain` (one value from `exercise-adr-policy-201.02-domain-is-a-fixed-list`). These limits are checked by `exercise-edr-policy-102`.

#### 02-characteristic-description-is-the-reference

The description MUST state what the Characteristic means in daily experience. It is the reference used for dry-runs when authoring Questions (`exercise-bdr-policy-604.09-dry-run-before-accept`).

#### 03-specializations

A specialization MUST be a separate Characteristic whose id starts with the id of the broader one when it exists (for example `repetitive_movement_motor_soothing`) and whose description states what makes it more specific. It MUST NOT link to its parent (`exercise-adr-policy-201.04-specializations-are-independent-characteristics`).

#### 04-profile-fields

A Profile MUST have `id` (snake_case, at most 3 words), `name` (at most 9 words), `description` (at most 29 words), `reference` (at most 29 words: a URL or citation) and `characteristics` (a list of Characteristic ids).

#### 05-membership-is-a-claim

A Characteristic's membership in a Profile is a claim and MUST come from the Profile's `reference` or another cited source. Unverified memberships MUST be listed in the review notes of the change that adds them. A Characteristic MAY belong to many Profiles.

#### 06-profile-without-weights

Profiles MUST NOT define weights or thresholds. A more specific Characteristic adds more evidence to a Profile by being listed in it. Because `weighted_score` weights a Characteristic by how few Profiles list it (`exercise-edr-policy-101.10-weighted-profile-score`), adding or removing a membership changes the weights of that Characteristic in every Profile.

## References

- [exercise-adr-policy-201 - Domain model](../../adrs/data/201-domain-model.md)
- [exercise-bdr-policy-604 - Question authoring](604-question-authoring.md)
- [exercise-edr-policy-102 - Registry lint](../../edrs/application/102-registry-lint.md)
