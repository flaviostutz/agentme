---
name: agentme-bdr-policy-403-product-team-composition
description: Defines team composition models, squad structure, squad dynamics, and known structural gaps for Product Teams. Use when structuring or scaling a new or existing product team.
apply-to: All product teams and cross-team roles in the organisation
valid-from: 2026-08-18
---

# agentme-bdr-policy-403: Product team composition

## Context and Problem Statement

Product teams vary in scope and AI surface. Without a defined composition model, teams grow informally, leading to inconsistent structures, unclear coordination patterns, and unmanaged structural risks.

How should a product team be structured, and what known risks must teams manage proactively?

## Decision Outcome

**Two composition models (simple and complex) with defined squad structure, squad dynamics, and documented structural gaps with required mitigations**

### Details

#### 01-composition-model-selection

Teams MUST apply one of the two composition models defined in this policy — simple or complex — based on their product scope and AI surface. Teams MUST NOT operate with an undefined or informal structure.

![Team composition diagram](.assets/team-composition.svg)

#### 02-team-composition-simple

A team with a bounded product scope and limited AI surface MUST operate as a simple team with no internal squads.

| Role | Count | Notes |
|---|---|---|
| Product Owner | 1 | |
| Business Analyst or AI BA | 1 | |
| Tech Lead | 1 | |
| Engineer | 1–2 | Any sub-type from `agentme-bdr-404` (Backend, Frontend, DevOps/Infra, Full Stack) |
| AI Engineer (if AI work exists) | 0–1 | |

The Tech Lead MAY also contribute as an engineer in a simple team. The BA MUST work directly with the PO on requirements without squad separation.

#### 03-team-composition-complex

A team with a broad product scope or significant AI surface MUST operate with internal squads.

| Role | Count | Notes |
|---|---|---|
| Product Owner | 1 | Shared across all squads |
| Tech Lead | 1 | Shared across all squads |
| AI Lead | 1 | Shared across all squads |
| Squad | 3 | See squad composition below |

**Squad composition** (per squad):

| Role | Count | Notes |
|---|---|---|
| Business Analyst (BA or AI BA) | 1 | Ideally one per squad; may move |
| AI Engineer | 2 | |
| Engineer | 2 | Any sub-type from `agentme-bdr-404` (Backend, Frontend, DevOps/Infra, Full Stack) |
| Squad Lead | 1 | One of the engineers above, designated by soft skills |

Squads MUST NOT exceed 4 engineers (AI + Full Stack combined) to preserve cohesion and limit coordination overhead.

#### 04-squad-dynamics

**Squad stability**: Engineers assigned to a squad MUST remain stable over time. Squad membership changes MUST be deliberate and infrequent; frequent reassignment prevents team bonding and reduces squad effectiveness.

**BA and AI BA fluidity**: One BA or AI BA MUST be assigned to each squad, ideally working one sprint ahead on upcoming features. When squad needs shift — for example, when a squad moves from a non-AI phase to an AI-heavy phase — the BA and AI BA MAY exchange positions. Movement is self-organised between the BAs with PO awareness and is not restricted to sprint boundaries.

**Squad Lead**: Each squad MUST have a designated Squad Lead — one of its engineers (AI Engineer or Engineer) selected based on available soft skills. The Squad Lead is a formal role with the following responsibilities:
- Run squad ceremonies (standups, retrospectives)
- Shield the squad from unplanned external interruptions
- Make within-squad prioritisation calls when the PO or Tech Lead / AI Lead are unavailable

The Squad Lead MUST be identified at squad formation, not selected on-demand when a situation arises. The role does not change the engineer's technical responsibilities and does not carry a formal seniority change, but soft skills MUST be taken into account at the time of assignment.

**Cross-squad coordination**: Cross-squad dependencies within the same team MUST be the Project Manager (PjM)'s explicit responsibility. The PjM MUST proactively identify and resolve scheduling conflicts between squads.

**Tech Lead and AI Lead interaction**: The PO, Tech Lead, and AI Lead MUST connect to all squads. For integrated features spanning AI and non-AI components, the Tech Lead and AI Lead MUST co-own the technical design. The Tech Lead holds the tiebreaker on system boundaries and non-AI components; the AI Lead holds the tiebreaker on AI components.

#### 05-known-gaps-and-mitigations

Teams MUST be aware of the following structural gaps and MUST apply the recommended mitigations proactively.

| Gap | Risk | Mitigation |
|---|---|---|
| PO, Tech Lead, AI Lead spanning 3 squads | Bandwidth overload; leads become bottlenecks | Squad Lead MUST absorb daily unblocking and within-squad prioritisation; leads focus on design, mentoring, and cross-squad alignment |
| Principal Engineer covering all teams | Single point of knowledge for engineering standards | Architecture documentation MUST be kept current; Principal Engineer MUST actively pair with Tech Leads and AI Leads to distribute knowledge |
| No embedded UX/Design role | UI and interaction design absorbed informally by BA or PO | A UX Designer Specialist (see `agentme-bdr-404`) SHOULD be engaged for user-facing features with significant interaction design needs; otherwise bring in a contract designer |
| No Data Engineering / MLOps role | Data pipelines, feature stores, and model serving infrastructure absorbed by Engineers and AI Engineers | Teams MUST plan a dedicated hire when the AI surface grows beyond squad capacity |
| No embedded QA role | Test quality depends on individual engineer discipline with no gate owner | A Tester / QA Specialist (see `agentme-bdr-404`) SHOULD be engaged during high-complexity delivery phases; Tech Lead and AI Lead MUST own quality gates; acceptance criteria from BA and AI BA MUST include testable conditions |
| No Security / SecOps role | Security design and review absorbed by Tech Lead on top of architecture load | Teams MUST schedule an external security review cadence; Principal Engineer MUST maintain security standards in the engineering blueprint |
| BA squad fluidity | Knowledge transfer cost each time a BA moves | BAs MUST coordinate handoff timing to minimise disruption |
| Squad Lead selection uncertainty | Squads without a clear lead default to ambiguity in ceremonies and prioritisation | Squad Lead MUST be identified at squad formation; MUST NOT be left to emerge organically after work has started |
| Cross-squad dependency coordination | Without explicit ownership, cross-squad dependencies surface late and block delivery | Project Manager (PjM) MUST own cross-squad dependency tracking and resolution as part of their stakeholder-connecting mandate |

## References

- [`_core-adr-policy-016`](../../../_core/adrs/principles/016-policy-subjects.md) — Policy subjects: BDR operations subject definition
- [`_core-adr-policy-017`](../../../_core/adrs/principles/017-policy-numbering-ranges.md) — Policy numbering: BDR operations block 401–500
- [`agentme-bdr-402`](402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Principal Engineer, and Solution Architect definitions
- [`agentme-bdr-404`](404-team-roles-and-specialists.md) — Digital product roles (team & specialists): role definitions for all team-level roles and specialists referenced in this policy
