# XDRS Scope and Type Selection

This module is shared across XDRS writing skills. Read and apply these instructions when selecting scope and type for a new document.

---

## Scope

The scope was determined and confirmed in Phase 0 (scope placement analysis). Carry it forward. As a final safety check, verify the scope is not external:

- Check the workspace root `.filedist.lock` file. If any file under `.xdrs/[scope]/` appears in `.filedist.lock`, the scope is external and new documents MUST NOT be created there. Inform the user and ask them to choose a non-external scope.

## Type

Choose exactly one based on the nature of the decision:

- **BDR**: business process, product policy, strategic rule, operational procedure
- **ADR**: system context, integration pattern, overarching architectural choice
- **EDR**: specific tool/library, coding practice, testing strategy, project structure, pipelines

When type cannot be confidently inferred, ask the user a clarifying question before proceeding. Ask one question at a time and wait for the answer.

## Subject

MUST read `_core-adr-policy-016` (`.xdrs/_core/adrs/principles/016-policy-subjects.md`) in full before choosing. That document defines all allowed subjects per type with full descriptions, examples, and disambiguation tiebreakers. Do not rely on summaries or prior knowledge — always read the policy and select the subject that best matches the topic according to its definitions.
