---
name: agentme-core-adr-policy-002-ai-edr-number-range
description: Defines the reserved EDR number ranges for the agentme scope, mapping number blocks to topic groups. Use when assigning a number to a new agentme EDR to determine which range it belongs to and whether a suitable slot is available.
apply-to: agentme scope contributors assigning numbers to new EDRs
valid-from: 2026-07-08
---

# agentme-core-adr-policy-002: EDR number ranges

## Context and Problem Statement

Without a numbering convention, agentme EDRs are assigned sequentially as they are created, mixing unrelated topics. This makes it hard to discover all policies on a given topic and leaves no room to insert related policies near each other as a subject area grows.

How should the agentme EDR number space be partitioned so that related policies cluster together and each topic group has room to grow?

## Decision Outcome

**The agentme EDR number space is divided into named ranges, each reserved for a specific topic group. A new EDR MUST be assigned a number from the range whose topic best matches the policy's subject.**

### Details

#### 01-reserved-ranges

A new agentme EDR MUST be assigned a number from the range whose topic best matches the policy's subject. The following ranges are defined. Ranges are non-overlapping and cover distinct topic groups.

| Range | Topic group | Examples of policies that belong here |
|-------|-------------|---------------------------------------|
| 001–019 | Language and framework standards | Project tooling for JS, Go, Python; CLI standards; module structure |
| 020–029 | Design and architecture | Hexagonal architecture; abstraction practices; cross-cutting design patterns |
| 040–049 | AI development | LLM calls, agents, workflows, naming conventions, XDRS knowledge layer |
| 050–059 | AI evaluation and testing | Eval folder structure, dataset formats, test types, eval scripts, reports |
| 060+ | Unreserved | Use when no existing range fits, or when an existing range has no available slots |

#### 02-range-assignment

When creating a new agentme EDR:

1. Identify the topic group whose description best matches the policy subject using the table in rule `01`.
2. MUST scan the relevant type index to find the next unoccupied number in that range.
3. If the range is fully occupied, MUST use the unreserved block (060+) and add a comment in the index noting the overflow reason.
4. If no range fits at all, MUST add a new range to rule `01` following the same format before assigning the number.

#### 03-range-boundaries

Numbers at range boundaries (e.g., 020, 040, 050, 060) are ordinary policy numbers — they carry no special meaning and MAY be assigned to policies. The boundary values in rule `01` are inclusive on both ends.
