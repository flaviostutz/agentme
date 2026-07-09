---
name: _core-adr-policy-017-policy-numbering-ranges
description: Defines numeric block ranges per subject for policy numbering. Use when assigning a number to a new policy to ensure the number reflects the policy's subject.
apply-to: All XDRS scopes and policy numbers
valid-from: 2026-07-09
---

# _core-adr-policy-017: Policy numbering ranges

## Context and Problem Statement

As a scope grows across multiple subjects, doing only sequential numbering alone gives no indication of the subject, making browsing harder and independent authoring more prone to gaps that could have been intentional range separators.

How should policy numbers be allocated so that related policies are naturally grouped and the subject is visible from the number alone?

## Decision Outcome

**Reserve fixed 100-number blocks per subject, with an upper overflow range for exhausted blocks**

Allocating one 100-number block per subject groups related policies in any sequential listing, makes subject membership visible from the number alone, and provides a clear path when a block runs out.

### Details

#### 01-numbering-blocks-per-subject

Policies within a scope+type MUST be assigned numbers within the block reserved for their subject according to the table below. Each block covers exactly 100 numbers. Subjects that are not valid for a given type leave their block empty and unused.

| Block    | Subject       | Types              |
|----------|---------------|--------------------|
| 001–100  | `principles`  | ADR, BDR, EDR      |
| 101–200  | `application` | ADR, EDR           |
| 201–300  | `data`        | ADR, EDR           |
| 301–400  | `platform`    | ADR, EDR           |
| 401–500  | `operations`  | ADR, BDR, EDR      |
| 501–600  | `governance`  | ADR, BDR, EDR      |
| 601–700  | `product`     | BDR                |
| 701–800  | `finance`     | BDR                |
| 801–900  | *(reserved)*  | future subjects    |
| 901–999  | overflow      | see rule 03        |

#### 02-next-available-number-within-block

The subject block rules in rule 01 apply to all policies, including existing ones. Any policy whose number falls outside its subject's reserved block MUST be renumbered to the lowest available number within the correct block. Authors assigning a number to a new policy MUST use the lowest available number within the subject's reserved block. Numbers from deleted policies MUST NOT be reused. Authors MUST NOT assign a number outside the subject's block unless that block is fully exhausted (see rule 03).

#### 03-overflow-range

When all 100 slots in a subject's block are exhausted, new policies for that subject MUST be placed in the overflow range (901–999), taking the next available number. The policy's subject folder governs placement; the number alone does not determine the subject for overflow policies.

#### 04-policy-numbers-must-comply

A policy's number MUST comply with the subject block rules in rule 01. Any policy with a non-compliant number MUST be renumbered to the correct block unless `freeze-reference: true` is set in the policy's frontmatter (see rule 06). Renumbering MUST update the filename, the `name` frontmatter field, the document heading, and all references to the old number in indexes, links, and citations.

#### 05-reserved-gap-must-not-be-assigned

Numbers in the reserved gap (801–900) MUST NOT be assigned to any policy. They are reserved for future subject additions defined by a future update to this policy.

#### 06-freeze-reference-exemption

When `freeze-reference: true` is set in a policy's frontmatter, numbering range compliance checks for that policy MUST be treated as exempt. The full exemption semantics are defined in [`_core-adr-policy-002-policy-standards.01-freeze-reference-exemption`](002-policy-standards.md).

## References

- [`_core-adr-policy-001`](001-xdrs-core.md) — XDRS core framework: numbering and folder structure
- [`_core-adr-policy-002`](002-policy-standards.md) — Policy standards: freeze-reference exemption semantics
- [`_core-adr-policy-016`](016-policy-subjects.md) — Policy subjects: allowed subjects and taxonomy per type
