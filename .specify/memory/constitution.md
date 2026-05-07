<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (MINOR: initial population of constitution)

Added sections:
  - Core Principles (I through V)
  - Quality Requirements
  - Development Workflow
  - Governance

Modified principles: N/A (first version)
Removed sections: N/A (first version)

Templates checked:
  - .specify/templates/plan-template.md    ✅ "Constitution Check" gate already present
  - .specify/templates/spec-template.md   ✅ no constitution-specific sections required
  - .specify/templates/tasks-template.md  ✅ generic task categories compatible

Related XDRs created:
  - .xdrs/_local/bdrs/index.md            ✅ created
  - .xdrs/_local/bdrs/principles/001-agentme-product-purpose.md  ✅ created

Follow-up TODOs: none
-->

# agentme Constitution

## Core Principles

### I. XDR-First Knowledge Base

Every design decision, product requirement, and engineering convention MUST be captured in an XDR
before it is acted on. Specs and plans produced by speckit are temporary work products and may be
deleted after a feature ships. XDRs are permanent and form the living knowledge base used for
vibe coding, onboarding, and future feature development.

- BDRs capture product purpose, business rules, and consumer workflows.
- ADRs capture architectural context and cross-cutting patterns.
- EDRs capture concrete engineering decisions: tooling, structure, practices.
- Every non-trivial implementation decision MUST have a corresponding XDR entry before the implementation task is marked complete. Create new XDRs if necessary.

### II. XDR as the Single Source of Truth for All Policies

All quality standards, business policies, architectural policies, and engineering policies that
specs, plans, and implementations must follow MUST be captured exclusively in XDRs. The
constitution does not restate those rules; it defers to them.

- Quality gates (testing, linting, coverage thresholds, file-size limits) → EDRs.
- Business rules, consumer workflows, versioning contracts → BDRs.
- Architectural patterns, cross-cutting concerns, dependency strategies → ADRs.
- If a policy is not in an XDR, it is not an enforceable policy. Write the XDR first.
- Agents and humans MUST consult the XDR index before starting any work and MUST follow every
  relevant XDR found there without exception.

## Development Workflow

1. Before starting a feature: check existing XDRs for applicable decisions.
2. During specifying (`speckit.specify`): capture business requirements as BDRs in `_local`.
   **After every `speckit.specify` run the agent MUST offer to run `speckit.clarify` (refine)
   before proceeding to planning. This is non-negotiable.**
3. During planning (`speckit.plan`): update or create ADRs and EDRs in `_local` that reflect
   architectural and engineering decisions made during the planning phase.
   **After every `speckit.plan` run the agent MUST propose running `speckit.checklist` to enrich
   the plan with domain-specific quality checks before generating tasks.**
4. During implementation: follow XDRs; create new `_local` XDRs for decisions not yet captured.
5. After implementation: delete feature specs and plans; XDRs remain permanently.
6. Runtime guidance: see `.xdrs/index.md` and all linked scope indexes.

## XDR Compliance Check (Mandatory at Every Stage)

Every Spec, Refinement (clarify), Plan, Checklist, and Implementation task MUST include an
explicit step that verifies compliance with the XDRs present in the repository:

1. Read `.xdrs/index.md` and all linked scope indexes (`_local`, `agentme`, `_core`).
2. Identify every XDR relevant to the work being performed.
3. Confirm that the artifact (spec, plan, task list, or code change) does not contradict any
   relevant XDR.
4. If a contradiction or gap is found: either update the artifact to comply, or create/update the
   relevant XDR to reflect the new decision before continuing.
5. Document the compliance check result in the artifact (e.g., a "XDR Compliance" section or
   comment) so reviewers can audit it.

No artifact may be considered complete without a passed XDR compliance check.

## Governance

This constitution supersedes all other development practices within this repository. Amendments
require:
1. A version bump following semantic versioning rules stated in the relevant BDR/ADR/EDR.
2. An updated `LAST_AMENDED_DATE` in this file.
3. A review of all principles for continued non-conflict.
4. An updated Sync Impact Report (HTML comment at the top of this file).

All PRs MUST include a "Constitution Check" section confirming compliance with all principles.
Complexity MUST be justified; if a solution requires deviation from a principle, that deviation
MUST be documented in a new or updated XDR in `_local`.

**Version**: 1.0.0 | **Ratified**: 2026-03-14 | **Last Amended**: 2026-03-14
