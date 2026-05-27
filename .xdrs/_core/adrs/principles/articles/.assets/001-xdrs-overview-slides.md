---
marp: true
paginate: true
---

# XDRS Framework

A structured system for capturing, organizing, and distributing architectural, business, and engineering decisions

---

## Context

Teams accumulate decisions across architecture, engineering, and business domains.

Without structure, decisions are:
- Buried in wikis, tickets, or chat threads
- Mixed with rationale, plans, and how-to guides
- Invisible to AI agents and future contributors

---

## Problem

A standard Decision Record combines too many concerns in one file:

| Concern | Job |
|---------|-----|
| Why we decided | Rationale / Research |
| What we decided | Policy (the rule) |
| How to implement it | Plan |
| How to apply it daily | Skill |
| Overview for readers | Article |

Mixing these makes decisions hard to search, update, and apply.

---

## Solution: Separate Artifact Types

XDRS splits the concerns into focused, linkable documents:

- **Policy** — the authoritative decision (ADR / BDR / EDR)
- **Research** — exploration, options, evidence
- **Skill** — step-by-step execution procedure
- **Article** — synthetic overview linking multiple artifacts
- **Plan** — ephemeral execution plan, deleted after implementation

---

## Policies — the Source of Truth

The central artifact. Answers a concrete question and records the adopted direction.

Three types:
- **ADR** — architectural and technical decisions
- **BDR** — business and operational decisions
- **EDR** — engineering implementation decisions

If Research and a Policy disagree, **the Policy wins**.

---

## Research

Captures exploration **before or around** a decision.

- Constraints, findings, options, pros, cons
- Supports elaboration and discussion — not a rule
- One Research document may inform multiple downstream Policies
- Lives beside the Policy in `researches/`

---

## Skills

Describe **how to execute** work under the constraints of a decision.

- Add procedural detail that Policies intentionally avoid
- Used by humans, AI agents, or both
- Task-based, end in a verifiable outcome
- Only mandatory when a Policy makes them mandatory

---

## Articles

Synthetic views that **explain a topic** across multiple Policies, Research, and Skills.

- Help readers understand the system without making new decisions
- Do not replace the source of truth
- Useful for onboarding and cross-cutting topics

---

## Plans

Describe a problem, proposed solution, and implementation approach.

- Clear start and end, well-defined scope
- **Ephemeral**: deleted after full implementation
- Lasting outputs are captured as Policies, Skills, or Articles

---

## How They Differ at a Glance

| Artifact | Central question |
|----------|-----------------|
| Policy | What did we decide? |
| Research | What did we learn while evaluating options? |
| Skill | How do we carry out work under this decision? |
| Article | How do these artifacts fit together for a reader? |
| Plan | What are we going to do, why, and how? |

---

## Lifecycle

```
Explore  →  Decide  →  Execute  →  Explain  →  Distribute
Research    Policy      Skill       Article     Scopes / Indexes
```

Research usually appears **before** a decision.
The Policy marks the **adopted outcome**.
Skills appear when the decision must be **executed repeatedly**.
Articles appear when the **ecosystem around the decision** needs explanation.

---

## Folder Structure

```
.xdrs/
  [scope]/
    [type]/          # adrs | bdrs | edrs
      [subject]/
        [N]-[title].md        ← Policy
        researches/
        skills/[N]-[name]/SKILL.md
        articles/
        plans/
        .assets/              ← slides, diagrams
```

- **Scope** — ownership domain (e.g. `_core`, `team-43`)
- **Type** — ADR / BDR / EDR
- **Subject** — topic category (e.g. `principles`, `application`)

---

## Scope Precedence

The root `.xdrs/index.md` lists all scope indexes.

Scopes listed **later override** those listed earlier.

```
_core         ← base rules (broadest)
my-platform   ← platform-specific overrides
_local        ← project-specific overrides (narrowest)
```

---

## Applying a Policy

Before treating a Policy as a rule, check in order:

1. **Valid** — is the policy active?
2. **Applied to** — does the current context match the scope?
3. **Decision text** — do the context and exceptions allow this case?

Only decisions that pass all three checks should be enforced.

---

## Getting Started

```bash
# 1. Install
npm install xdrs-core   # or pnpm add xdrs-core

# 2. Bootstrap
npx xdrs-core

# 3. Start writing with your AI agent
# "Create an ADR about our decision to use Python for AI projects."
```

This creates `AGENTS.md` and `.xdrs/index.md` with the `_core` scope pre-loaded.

---

## Extending XDRS

| Goal | Action |
|------|--------|
| New scope | Create `.xdrs/[scope]/[type]/index.md`, add to root index |
| New subject | Add subject folder under scope+type path |
| New research | Add `researches/[N]-[title].md` |
| New skill | Add `skills/[N]-[name]/SKILL.md` |
| Distribute a scope | Pack `.xdrs/[scope]/` and publish to an npm registry |

---

## Distributing Across Teams

- Pack `.xdrs/[scope]/` with `pnpm pack`
- Publish to public or internal npm registry
- Consumers install the package and run `npx xdrs-core extract`
- `filedist` tracks managed files; `_local` overrides are preserved
- Run `npx xdrs-core check` to verify files are in sync

---

# Summary

- XDRS separates concerns: Policy, Research, Skill, Article, Plan
- Policies are the source of truth; all other artifacts support them
- Scopes and indexes make decisions discoverable and overridable
- AI agents consult XDRS before every request via `AGENTS.md`

---

# References

- [XDRS Overview article](../001-xdrs-overview.md)
- [_core-adr-policy-001 - XDRS core](../../001-xdrs-core.md)
- [_core-adr-policy-002 - Policy standards](../../002-policy-standards.md)
- [_core-adr-policy-003 - Skill standards](../../003-skill-standards.md)
- [_core-adr-policy-004 - Article standards](../../004-article-standards.md)
- [_core-adr-policy-009 - Presentation standards](../../009-presentation-standards.md)
