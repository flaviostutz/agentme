---
name: agentme-bdr-policy-001-company-organizational-levels
description: Defines the Group, Company, and Business Unit taxonomy used to describe how organisations are structured. Use when referencing org levels, structuring teams, or assigning OKR ownership.
apply-to: All contexts that reference company organizational structure
valid-from: 2026-08-30
---

# agentme-bdr-policy-001: Company organizational levels

## Context and Problem Statement

Policies for teams, OKRs, and product structures reference organisational levels — Group, Company, and Business Unit — without a shared definition. Without a common taxonomy, documents use these terms inconsistently, leading to ambiguity about who sets which goals, who owns which teams, and how accountability flows.

How should the organisational hierarchy above the product team be defined so that all agentme policies can reference it consistently?

## Decision Outcome

**A three-level taxonomy — Group, Company, and Business Unit — with an optional product team layer below**

### Details

#### 01-group-definition

A Group is the parent entity that owns or controls one or more Companies.

- A Group MUST own or fund at least one Company.
- The Group layer is OPTIONAL. A standalone Company with no parent entity operates without a Group.
- Groups typically hold consolidated financial and governance responsibility across their Companies but do not operate products directly.

#### 02-company-definition

A Company is a legal entity that operates independently within its jurisdiction.

- A Company MUST be a registered legal entity with its own compliance and legal obligations.
- A Company MAY exist without a parent Group.
- A Company MAY contain one or more Business Units, or operate as a single undivided entity.
- Strategic OKRs MAY be set at the Company level when the Company operates without Business Units.

#### 03-business-unit-definition

A Business Unit (BU) is an internal division of a Company that operates with a distinct product portfolio, market focus, or organisational boundary.

- A Business Unit is NOT a separate legal entity. It shares the legal, financial, and compliance structure of its parent Company.
- The Business Unit layer is OPTIONAL. A Company with a single undivided focus operates without Business Units.
- A Business Unit MUST have clearly defined scope boundaries and ownership so that OKRs, teams, and accountability are unambiguous.
- Strategic and Tactical OKRs MAY be set at the Business Unit level.

#### 04-product-teams-inside-business-units

Product teams are cross-functional execution units that sit inside a Business Unit (or directly inside a Company when no Business Unit layer exists).

- A product team MUST be accountable for a defined product scope — an API, a business process, or a platform consumed by others.
- Product teams implement Tactical OKR work through epics, sprints, and kanban flows. They do NOT set Tactical OKRs; Tactical OKRs are set at the Group, Company, or Business Unit level.
- Product teams MAY define Operational OKRs for day-to-day execution tracking. See `agentme-bdr-002` for the full OKR framework.
- Org-level and cross-team role definitions — including Product Manager, Principal Engineer, and Solution Architect — are in `agentme-bdr-402`. Team-level and specialist role definitions are in `agentme-bdr-404`.

## References

- [`agentme-bdr-002`](002-okr-framework.md) — OKR framework: Strategic, Tactical, and Operational OKR definitions
- [`agentme-bdr-402`](../operations/402-digital-product-roles.md) — Digital product roles (org & cross-team): PM, Principal Engineer, and Solution Architect definitions
- [`agentme-bdr-404`](../operations/404-team-roles-and-specialists.md) — Digital product roles (team & specialists): PO, PjM, BA, AI BA, AI Lead, AI Engineer, Tech Lead, engineers, and specialists
