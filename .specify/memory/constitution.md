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

### II. Preset Integrity (NON-NEGOTIABLE)

agentme distributes files to consumer projects via named presets (`basic`, `speckit`). Each
preset MUST be independently coherent, non-overlapping, and verified on every build.

- A preset MUST contain all files a consumer needs and nothing more.
- Presets MUST NOT share extraction sets unless the consumer explicitly requests multiple presets.
- The `examples/` folder MUST assert the exact file presence/absence for each preset combination
  after every `make build`.
- Adding a file to a preset or changing selector patterns is a public API change and requires a
  version bump (MINOR or MAJOR depending on impact).

### III. Consumer-First API Discipline

XDRs, skills, and preset file sets are a public API consumed by external projects. Changes MUST
respect semantic versioning.

- MAJOR: removing or renaming a preset, removing or restructuring an XDR that external consumers
  reference, or any change that requires consumer-side migration.
- MINOR: adding a new preset, adding XDRs or skills, adding files to an existing preset.
- PATCH: wording, clarifications, typo fixes inside XDRs or skills that carry no structural change.
- Breaking changes MUST be documented in the release notes and in the relevant XDR's `Conflicts`
  or `Implementation Details` section before merging.

### IV. Self-Contained Artifacts

Every XDR and skill MUST work without any implicit context outside itself.

- XDRs MUST be under 100 lines (hard limit 200 for templates and elaborate decisions).
- Skills MUST be under 500 lines; lengthy reference material goes in `references/`.
- Internal cross-references MUST use relative file paths; no absolute or external URLs without
  explanation.
- A consumer reading an XDR or skill for the first time MUST be able to follow it without
  accessing other systems.

### V. Simplicity and Verified Quality

The simplest solution that passes all tests is always preferred. Quality gates are non-negotiable.

- `make test` MUST pass before any release; failures block publish.
- Linting MUST be clean (`make lint-fix`) before merging.
- Files MUST NOT exceed 400 lines (test files excepted).
- No feature scope creep: implement only what the current spec requires.
- Avoid adding error handling, fallbacks, or abstractions for hypothetical future scenarios.

## Quality Requirements

- `make test` in `examples/` MUST verify all preset extraction scenarios end-to-end.
- XDRs produced during a feature MUST be reviewed for non-conflict before merging.
- All XDR indexes (`_local`, `agentme`, `_core`) MUST be updated before a PR is merged.
- New presets or selector changes MUST include updated test assertions in the examples Makefile.

## Development Workflow

1. Before starting a feature: check existing XDRs for applicable decisions.
2. During specifying (`speckit.specify`): capture business requirements as BDRs in `_local`.
3. During planning (`speckit.plan`): update or create ADRs and EDRs in `_local` that reflect
   architectural and engineering decisions made during the planning phase.
4. During implementation: follow XDRs; create new `_local` XDRs for decisions not yet captured.
5. After implementation: delete feature specs and plans; XDRs remain permanently.
6. Runtime guidance: see `.xdrs/index.md` and all linked scope indexes.

## Governance

This constitution supersedes all other development practices within this repository. Amendments
require:
1. A version bump following semantic versioning rules stated in Principle III.
2. An updated `LAST_AMENDED_DATE` in this file.
3. A review of all five principles for continued non-conflict.
4. An updated Sync Impact Report (HTML comment at the top of this file).

All PRs MUST include a "Constitution Check" section confirming compliance with all five principles.
Complexity MUST be justified; if a solution requires deviation from a principle, that deviation
MUST be documented in a new or updated XDR in `_local`.

**Version**: 1.0.0 | **Ratified**: 2026-03-14 | **Last Amended**: 2026-03-14
