---
name: agentme-core-adr-policy-002-policy-numbering
description: Specializes the xdrs-core numbering standard for agentme EDR application policies, mapping topic-group blocks within the 101–200 number range. Use when assigning a number to a new agentme EDR application policy to determine which topic-group block it belongs to.
apply-to: agentme scope contributors assigning numbers to new policies
valid-from: 2026-07-09
---

# agentme-core-adr-policy-002: agentme policy numbering

## Context and Problem Statement

[`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) reserves the 101–200 block for the `application` subject in ADR and EDR policies. Without further sub-division, agentme EDR application policies in that block are assigned sequentially as they are created, mixing unrelated topics. This makes it hard to discover all policies on a given topic and leaves no room to insert related policies near each other as a subject area grows.

How should the agentme EDR 101–200 number block be partitioned into topic groups so that related policies cluster together and each topic group has room to grow?

## Decision Outcome

**The agentme EDR 101–200 number block is divided into topic-group ranges. A new agentme EDR application policy MUST be assigned a number from the matching topic-group range when one is defined, subject to the constraints of [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md). When no range fits, standard xdrs-core sequential numbering within the 101–200 block applies.**

### Details

#### 01-edr-application-topic-group-ranges

New agentme EDR `application` policies MUST be assigned a number from the topic-group range whose description best matches the policy's subject. The following topic-group ranges are defined within the 101–200 EDR application block. Ranges are non-overlapping and by default all numbering conventions from xdrs-core MUST apply.

| Range | Topic group | Examples of policies that belong here |
|-------|-------------|---------------------------------------|
| 101–120 | Language and framework standards | Project tooling for JS, Go, Python; CLI standards; module structure |
| 121–140 | Design and architecture | Hexagonal architecture; abstraction practices; cross-cutting design patterns |
| 141–150 | AI development | LLM calls, agents, workflows, naming conventions, XDRS knowledge layer |
| 151–160 | AI evaluation and testing | Eval folder structure, dataset usage, test types, eval scripts, reports |
| 161–200 | Unreserved | Use when no existing range fits, or when an existing range has no available slots |

#### 02-range-assignment

When creating a new agentme EDR `application` policy:

1. Identify the topic-group range whose description best matches the policy subject using the table in rule `01`.
2. MUST scan the EDR application index to find the next unoccupied number in that range.
3. If the range is fully occupied, MUST use the unreserved block (161–200) and add a comment in the index noting the overflow reason.
4. If the unreserved block is also exhausted, MUST follow the overflow rules in [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) (use 901–999).
5. If no range fits at all, MUST add a new range to rule `01` following the same format before assigning the number.

#### 03-range-boundaries

Numbers at range boundaries (e.g., 120, 140, 150, 160, 200) are ordinary policy numbers — they carry no special meaning and MAY be assigned to policies. The boundary values in rule `01` are inclusive on both ends.

## References

- [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) — Policy numbering ranges: subject-based 100-number block ranges and overflow rules
