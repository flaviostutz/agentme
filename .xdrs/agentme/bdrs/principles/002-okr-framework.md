---
name: agentme-bdr-policy-002-okr-framework
description: Defines the Strategic, Tactical, and Operational OKR framework. Use when setting, reviewing, or connecting OKRs to org levels, teams, or epics.
apply-to: All contexts where OKRs are set, tracked, or referenced
valid-from: 2026-08-30
---

# agentme-bdr-policy-002: OKR framework

## Context and Problem Statement

Teams and Business Units set goals using OKRs (Objectives and Key Results), but without a defined framework the term is applied inconsistently — timeframes vary, ownership is blurry, and the connection between strategic intent and daily execution is lost.

How should OKRs be structured, owned, and connected across organisational levels so that strategy is traceable to execution?

## Decision Outcome

**A three-level OKR framework — Strategic, Tactical, and Operational — with defined ownership, timeframes, and connection rules**

### Details

#### 01-objective-characteristics

An Objective defines WHERE the organisation wants to go.

- Objectives MUST be qualitative, inspirational, and actionable — they state a desired direction, not a metric.
- Objectives MUST be time-bound: each Objective MUST have a deadline; the timeframe is defined per OKR level (see rules 04–06).
- Each Objective MUST have at least one Key Result.

#### 02-key-result-characteristics

A Key Result measures HOW FAR the Objective has been achieved.

- Key Results MUST be quantitative and outcome-focused — they measure results, not activities.
- Key Results SHOULD be set aggressively: a score of 0.7 out of 1.0 at cycle end is considered a strong result.
- Key Results MUST be independently verifiable by any team member without subjective interpretation.

#### 03-framework-characteristics

- **Transparent**: all OKRs at every level MUST be visible to all members of the organisation.
- **Bidirectional**: lower-level OKRs are informed by higher-level OKRs, and learnings from lower levels flow upward to inform the next cycle.
- **Frequent**: OKR progress MUST be reviewed at a cadence appropriate to each level (see rules 04–06).
- **Divorced from compensation**: OKR scores MUST NOT be used as direct inputs to performance reviews, bonuses, or compensation decisions. Using OKRs for compensation destroys the honesty required for accurate grading.

#### 04-strategic-okrs

Strategic OKRs define the long-term direction of the organisation.

- **Timeframe**: annual or multi-quarter cycles.
- **Owners**: Group, Company, or Business Unit level. See `agentme-bdr-001` for org level definitions.
- **Downstream coverage**: every Strategic OKR MUST have at least one Tactical OKR that contributes to it. A Strategic OKR with no downstream Tactical coverage MUST have the coverage gap explicitly documented as a conscious decision.

#### 05-tactical-okrs

Tactical OKRs translate strategic direction into quarterly execution goals.

- **Timeframe**: quarterly cycles.
- **Owners**: Group, Company, or Business Unit level only. Product teams do NOT set Tactical OKRs — they execute against them.
- **Strategic coverage**: all active Strategic OKRs MUST have at least one Tactical OKR contributing to them in each quarter. Undocumented gaps MUST be flagged for resolution.
- **Connection to epics**: Tactical OKRs connect directly to Epics. The relationship is many-to-many: one Tactical OKR MAY drive multiple Epics; one Epic MAY contribute to multiple Tactical OKRs. See `agentme-bdr-401` for the epic planning policy.

#### 06-operational-okrs

Operational OKRs track day-to-day execution and business-as-usual (BAU) stability.

- **Timeframe**: short-term cycles — day-to-day or weekly.
- **Owners**: product teams or individual contributors.
- **Tactical connection**: Operational OKRs SHOULD be connected to the unit's Tactical OKRs. An Operational OKR with no Tactical connection is allowed when the absence is a conscious and documented decision.
- **Epic connection**: Operational OKRs are NOT directly linked to epics. Epics connect to Tactical OKRs, not Operational OKRs.

## References

- [`agentme-bdr-001`](001-company-organizational-levels.md) — Company organisational levels: Group, Company, and Business Unit definitions
- [`agentme-bdr-401`](../operations/401-epic-feature-story-planning.md) — Epic / Feature / User Story planning: epic structure and OKR connection rule
