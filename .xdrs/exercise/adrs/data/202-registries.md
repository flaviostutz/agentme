---
name: exercise-adr-policy-202-registries
description: Defines the JSON registries, schemas and configuration that hold the exercise catalogue and where they live. Use when adding or reading characteristics, profiles, questions or configuration values.
apply-to: All registries and implementations of the exercise questionnaire system
valid-from: 2026-11-17
---

# exercise-adr-policy-202: Registries

## Context and Problem Statement

The catalogue of characteristics, profiles and questions is data that changes much more often than the rules around it. It must still be the single source of truth during implementation.

Question: Where does the catalogue live and what shape does it have?

## Decision Outcome

**JSON registries and JSON Schemas in the `.assets/` folder next to this policy; rules stay in Policies, data stays in the registries.**

### Details

#### 01-registry-location

All registries MUST live in `.xdrs/exercise/adrs/data/.assets/`:
- `characteristics.json`: array of Characteristics.
- `profiles.json`: array of Profiles.
- `questions/<domain>.json`: one array of Questions per Domain, where the file name is the derived Domain of the Questions it holds (`exercise-adr-policy-201.07-question-domain-is-derived`).
- `config.json`: engine and measurement thresholds.
- `schemas/`: one JSON Schema per registry (`characteristic`, `profile`, `question`, `config`).
- `<instrument-id>/`: reference instruments, which are not registries and are defined in `exercise-adr-policy-203`.

#### 02-registries-hold-data-not-rules

Registry files MUST contain data only. A rule MUST NOT exist only in a registry or a schema; each structural rule in a schema MUST also be stated in a Policy (`exercise-adr-policy-201`, `exercise-bdr-policy-604`, `exercise-bdr-policy-605`). Every schema property MUST carry a `description` that explains what the field means in plain language; descriptions are explanatory only and, when they differ from a Policy, the Policy prevails.

#### 03-ids-are-unique-and-stable

Characteristic, Profile and Question ids MUST be unique within their registry. An id MUST NOT be reused for a different meaning.

#### 04-references-must-resolve

Every Characteristic id in a Profile or a Question, and every `add` target in a Question route, MUST exist in its registry. The automated checks are defined in `exercise-edr-policy-102`.

#### 05-config-keys

`config.json` MUST contain exactly these keys, with the initial values shown. Their use is defined in `exercise-edr-policy-101`.

| Key | Initial value |
|---|---|
| `margin_stop` | 0.25 |
| `uncertainty_giveup` | 0.5 |
| `giveup_min_asked` | 2 |
| `min_answered` | 3 |
| `stability_window` | 2 |
| `stability_delta` | 0.25 |
| `balancing_min_score` | 0.3 |
| `evidence_sd` | 0.35 |
| `profile_measured_ratio` | 0.7 |
| `profile_settled_ratio` | 0.6 |
| `profile_margin_stop` | 0.12 |
| `quality_min_characteristics` | 10 |
| `quality_margin_max` | 0.55 |
| `quality_keying_max` | 0.6 |
| `quality_spread_min` | 0.2 |
| `quality_flat_max_mean` | 0.15 |

#### 06-catalogue-status-is-draft

The registry content is a draft and has no scientific validation. Content MUST NOT be presented to end users as validated until a review records that validation.

#### 08-change-config-with-dry-run

A value in `05-config-keys` MUST be changed together with a new simulated test run (`exercise-edr-policy-103-question-bank-testing`) that checks session length, bias and discrimination between Profiles. A Profile with few Characteristics MAY override `profile_margin_stop` with its own `margin_stop` (`exercise-bdr-policy-605.04-profile-fields`); the override SHOULD be revisited when the test run reports it.

## References

- [exercise-adr-policy-201 - Domain model](201-domain-model.md)
- [exercise-adr-policy-203 - Reference instruments](203-reference-instruments.md)
- [exercise-edr-policy-102 - Registry lint](../../edrs/application/102-registry-lint.md)
- Registries: [config.json](.assets/config.json), [characteristics.json](.assets/characteristics.json), [profiles.json](.assets/profiles.json)
- Question files: [adaptation_environment.json](.assets/questions/adaptation_environment.json), [attention.json](.assets/questions/attention.json), [emotional_experience.json](.assets/questions/emotional_experience.json), [executive_function.json](.assets/questions/executive_function.json), [interests_learning.json](.assets/questions/interests_learning.json), [sensory_processing.json](.assets/questions/sensory_processing.json), [social_communication.json](.assets/questions/social_communication.json), [thinking_patterns.json](.assets/questions/thinking_patterns.json)
- Schemas: [characteristic.schema.json](.assets/schemas/characteristic.schema.json), [config.schema.json](.assets/schemas/config.schema.json), [profile.schema.json](.assets/schemas/profile.schema.json), [question.schema.json](.assets/schemas/question.schema.json)
