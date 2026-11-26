---
name: agentme-bdr-policy-407-phase-1-ideation
description: Defines phase 1 of the business and software lifecycle, Ideation - spikes, brainstorms, whiteboards, sandbox experiments and local prototypes - with its entry, activities, RACI, environment, XDRS outputs and exit gate. Use when exploring a new idea, problem or solution before scoping it.
apply-to: Every idea, problem or opportunity explored before a solution is scoped, including new changes to an existing business application
valid-from: 2026-11-26
---

# agentme-bdr-policy-407: Phase 1 - Ideation

## Context and Problem Statement

Ideas are explored in meetings, notebooks and prototypes that are lost or never connected to what is built later. Phase 1 of `agentme-bdr-004` must produce explorations that are cheap, isolated from the company and written down from the first brainstorm.

Question: What does the team do in phase 1, who is accountable, and what must exist when it ends?

## Decision Outcome

**Phase 1 explores cheaply in isolation and records everything in XDRS from the first brainstorm, ending when the Product Owner accepts that the idea is worth scoping**

### Details

#### 01-objective-and-entry

The objective is to learn whether an idea, problem or opportunity is worth scoping. The entry is any idea. No approval is needed to start, but the XDRS scope of the business application MUST be created at the first brainstorm per `agentme-bdr-415`.

#### 02-activities-and-outputs

Activities are spikes, brainstorms, whiteboard sessions, sandbox experiments and locally running prototypes. Outputs are research documents, hypotheses and their results, and standalone prototypes. A prototype MUST be placed in the `.assets/` folder of the XDRS document that explores it, when no cloud is involved, per `agentme-bdr-416`. Spikes and experiments MUST be marked as such and MUST NOT be deployed to production (`agentme-edr-501` rule 02).

#### 03-raci

The activities below MUST be performed with the accountability shown, using the abbreviations of `agentme-bdr-405`.

| Activity | PM | PO | PjM | EM | BA | AI BA | Solution Architect | Enterprise Architect | Business Owner | Tech Lead | AI Lead | Principal Engineer | Engineers | AI Engineer | DevOps/Infra Engineer | Specialists |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AI opportunity discovery | | | | | | A | | | | | | | | | | |
| Ideation, spikes, and sandbox prototypes | | A | | | | | C | C | | R | R | | | | | |

#### 04-environments-and-tests

Experiments run locally or in `sbx` (`agentme-adr-301` rule 02): no company data, no company credentials, owner and expiry date at creation. No test group applies. A prototype that touches company data or systems is no longer phase 1 and MUST restart in phase 5.

#### 05-xdrs-outputs

Findings MUST be written as XDRS research or initiative documents of the business application scope, and the first policies MAY be drafted as if final (`agentme-bdr-005`). Open questions and rejected options MUST be kept in the research document.

#### 06-exit-gate

The Product Owner MUST accept (`agentme-bdr-503` rule 01) that the idea is worth scoping, or drop it. A dropped idea keeps its research on the branch or is deleted per `agentme-bdr-415`. Loop-back: new findings in later phases return here only for the part that changed.

## References

- [`agentme-bdr-004`](../principles/004-business-and-software-lifecycle.md) - Lifecycle overview and phase definitions
- [`agentme-bdr-005`](../principles/005-xdrs-single-source-of-truth.md) - XDRS as the single source of truth
- [`agentme-bdr-405`](405-digital-product-roles-raci.md) - RACI rules and role abbreviations
- [`agentme-bdr-415`](415-solution-scope-lifecycle.md) - Creating the scope at the first brainstorm
- [`agentme-bdr-416`](416-solution-content-map.md) - Where prototypes and findings are placed
- [`agentme-bdr-503`](../governance/503-lifecycle-gate-approvals.md) - Phase exit approvers
- [`agentme-adr-301`](../../adrs/platform/301-computational-environments.md) - The `sbx` environment
- [`agentme-edr-501`](../../edrs/governance/501-project-quality-standards.md) - Spike and experiment exemption
