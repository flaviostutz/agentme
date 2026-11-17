---
name: exercise-edr-policy-102-registry-lint
description: Defines the automated checks run over the exercise registries and where they run. Use when changing registry files, schemas or the lint script, or wiring checks into the build.
apply-to: The exercise registries, their schemas and the repository lint target
valid-from: 2026-11-17
---

# exercise-edr-policy-102: Registry lint

## Context and Problem Statement

The registries are written by hand and by agents. Structural mistakes (wrong ids, broken routes) are cheap to detect automatically and expensive to find in use.

Question: Which checks are automated, and which stay as review?

## Decision Outcome

**JSON Schema for structure plus a small node script for references and graph checks, run by the repository `lint` target; semantic rules stay in review.**

### Details

#### 01-script-and-schemas

The checks MUST be implemented by [lint-registries.js](.assets/lint-registries.js), which validates the registries in `exercise-adr-policy-202.01-registry-location` against the schemas in `adrs/data/.assets/schemas/` and runs the checks below.

#### 02-schema-checks

Schemas MUST check required fields, enums, id patterns, the word limits from `exercise-bdr-policy-604.01-field-limits` and `exercise-bdr-policy-605`, weights in -1..1 and not 0, and the `config.json` keys. Every schema property MUST have a `description`, and the script MUST fail when one is missing (`exercise-adr-policy-202.02`).

#### 03-reference-checks

The script MUST fail on: duplicate ids; Characteristic ids in Profiles or Questions that do not exist; route targets that do not exist; a Question file whose name differs from the derived Domain of its Questions; route thresholds outside the Question's answer range.

#### 04-graph-checks

The script MUST fail on a route from a Question to itself and on a route cycle. It MUST warn, not fail, on a Question that is not `discovery` and is not reachable from a `discovery` Question through routes, because refill can still reach it (`exercise-adr-policy-101.05-refill-from-bank`).

#### 05-coverage-warnings

The script MUST warn on: a Characteristic with no Question; a Characteristic that no Profile lists; a Characteristic listed in a Profile that is not the main Characteristic (highest absolute weight) of any `discovery` Question (`exercise-bdr-policy-604.07-stage-types`).

#### 06-run-in-lint

The repository `lint` target MUST run the script and fail when it exits non-zero.

#### 07-semantic-checks-stay-in-review

Dry-runs, internal consistency (Cronbach's alpha), contradictions between Questions and source consistency (`exercise-bdr-policy-604.06-source`, `exercise-bdr-policy-604.09-dry-run-before-accept`, `exercise-bdr-policy-604.12-internal-consistency`) MUST be checked by review, not by the script.

#### 08-rationale-from-dry-runs

The description check and the discovery coverage warning exist because dry-runs (`exercise-edr-policy-101.12-rationale-from-dry-runs`) exposed two silent problems: the meaning of schema fields and config keys could not be read from the data, and Profile Characteristics without a discovery Question were reached late. The coverage check MUST remain a warning because the bank still works through routes and refill.

## References

- [exercise-adr-policy-202 - Registries](../../adrs/data/202-registries.md)
- [exercise-bdr-policy-604 - Question authoring](../../bdrs/product/604-question-authoring.md)
- [exercise-bdr-policy-605 - Characteristic and profile authoring](../../bdrs/product/605-characteristic-and-profile-authoring.md)
