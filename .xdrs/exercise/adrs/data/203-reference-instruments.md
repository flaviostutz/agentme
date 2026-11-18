---
name: exercise-adr-policy-203-reference-instruments
description: Defines where published screening instruments used as sources for the question bank are stored, which Profile each one relates to, and how new instruments are merged. Use when adding an instrument, tracing a question to its source item or reviewing citations.
apply-to: All reference instruments stored under the exercise registries and the Questions and Characteristics derived from them
valid-from: 2026-11-18
---

# exercise-adr-policy-203: Reference instruments

## Context and Problem Statement

Published instruments (questionnaires and checklists) inspire Characteristics and Questions. Without the original items kept next to the bank, nobody can check what was adapted or which items are still uncovered.

Question: Where are instruments kept and how are they linked to the bank?

## Decision Outcome

**One folder per instrument in `.assets/`, each linked to one Profile and mapping every item to bank Questions; the engine MUST NOT read instruments, which are analysis material.**

### Details

#### 01-instrument-location

Each instrument MUST live in its own folder `.xdrs/exercise/adrs/data/.assets/<instrument-id>/`, where `<instrument-id>` is lowercase with hyphens. The folder MUST contain:
- `README.md`: citation, download URL, related Profile, licence notes and how the items map to the bank.
- `<instrument-id>.json`: all items with their number, text and scoring direction or subscale.
- `<instrument-id>-bank-map.json`: for each item, the Question ids that cover it and a `match` of `new`, `close` or `equivalent`.
- The original download, when the publisher allows keeping a copy.

#### 02-instrument-catalogue

Every instrument MUST be listed here with the Profile it relates to. An instrument MUST relate to one Profile; its README MUST name that Profile.

| Instrument | Items | Related Profile | Folder |
|---|---|---|---|
| AQ-50, Adult Autism Spectrum Quotient | 50 | `autism` | [aq-50/](.assets/aq-50/README.md) |
| ASRS-v1.1, Adult ADHD Self-Report Scale symptom checklist | 18 | `adhd` | [asrs-v1.1/](.assets/asrs-v1.1/README.md) |
| ARHQ, Adult Reading History Questionnaire | 23 | `dyslexia` | [arhq/](.assets/arhq/README.md) |
| OCI-R, Obsessive-Compulsive Inventory-Revised | 18 | `ocd` | [oci-r/](.assets/oci-r/README.md) |

#### 03-every-item-is-traceable

Every item MUST appear in the bank map. A `new` item MUST have at least one Question whose `source` cites the instrument and item number, for example "ASRS-v1.1 item 10 (reworded)" (`exercise-bdr-policy-604.06-source`). A `close` or `equivalent` item MUST point to the existing Question that covers it.

#### 04-items-are-reworded

A Question derived from an item MUST be reworded to follow `exercise-bdr-policy-604` and MUST NOT copy the item text, scale or scoring. Instrument scores MUST NOT be reproduced by the engine.

#### 05-instruments-are-not-read-by-the-engine

The engine and the registry lint MUST NOT read the instrument folders. Instruments are analysis material; the bank is the only source for sessions.

#### 06-licence-is-checked-before-reuse

The README MUST record what the publisher states about use. When no terms are stated, the README MUST say so. A licence check MUST happen before any commercial use of the derived wording.

#### 07-adding-an-instrument

A new instrument MUST be added in one change that:
1. Downloads the instrument and stores the items as in `01-instrument-location`.
2. Maps every item to existing Questions or to new ones, and adds new Characteristics when no existing one fits.
3. Sets the `source` of each new Characteristic (`exercise-bdr-policy-605.07-characteristic-source`) and of each new Question.
4. Adds the new Characteristics to the related Profile, updates its `reference` and lists the unverified memberships in the review notes (`exercise-bdr-policy-605.05-membership-is-a-claim`), and records in its `comments` what could not be implemented (`exercise-bdr-policy-605.08-profile-comments`).
5. Adds a row to `02-instrument-catalogue`.
6. Runs the registry lint and a dry-run (`exercise-bdr-policy-604.09-dry-run-before-accept`).

#### 08-new-characteristics-stay-in-one-profile

A Characteristic created from an instrument MUST be listed only in the Profile the instrument relates to, unless a cited source supports another Profile.

## References

- [exercise-adr-policy-201 - Domain model](201-domain-model.md)
- [exercise-adr-policy-202 - Registries](202-registries.md)
- [exercise-bdr-policy-604 - Question authoring](../../bdrs/product/604-question-authoring.md)
- [exercise-bdr-policy-605 - Characteristic and profile authoring](../../bdrs/product/605-characteristic-and-profile-authoring.md)
- AQ-50 (autism): [README](.assets/aq-50/README.md), [items](.assets/aq-50/aq-50.json), [bank map](.assets/aq-50/aq-50-bank-map.json)
- ASRS-v1.1 (adhd): [README](.assets/asrs-v1.1/README.md), [items](.assets/asrs-v1.1/asrs-v1.1.json), [bank map](.assets/asrs-v1.1/asrs-v1.1-bank-map.json)
- ARHQ (dyslexia): [README](.assets/arhq/README.md), [items](.assets/arhq/arhq.json), [bank map](.assets/arhq/arhq-bank-map.json)
- OCI-R (ocd): [README](.assets/oci-r/README.md), [items](.assets/oci-r/oci-r.json), [bank map](.assets/oci-r/oci-r-bank-map.json)
