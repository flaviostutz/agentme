# _local-adr-001: Project basics

## Context and Problem Statement

What is agentme's purpose and what quality bar must its XDRs and skills meet?

## Decision Outcome

**agentme is a curated library of XDRs and skills encoding best practices for AI coding agents**

agentme ships two kinds of artifacts: XDRs (ADR/BDR/EDR) that capture best practices and architectural decisions for coding, and skills that encode reusable procedures for AI coding agents. All artifacts are intended for consumption by external projects, so consistency and clarity are paramount.

### Implementation Details

**Product scope**

- XDRs cover best practices for coding: architectural decisions, engineering workflows, and tooling choices relevant to AI-assisted software development.
- Skills package reusable step-by-step procedures that AI coding agents can load and execute.
- Both artifacts must be self-contained, unambiguous, and immediately usable without additional context.

**Consistency requirements**

Because agentme XDRs and skills are used as a source of truth by other projects, consistency is paramount. Before adding or changing any XDR or skill:

1. Verify the content is clear and unambiguous on its own.
2. Verify it does not conflict with existing XDRs in the same or other scopes within agentme.
3. Explicitly document any accepted conflict in the XDR "Conflicts" section with justification.
4. Update all affected indexes.

**Consumer integration**

Projects that import agentme XDRs must add the `agentme` scope to their `.xdrs/index.md` above `_local`, so local overrides remain in effect.

## References

- [_general-adr-001 - XDR standards](../../../_general/adrs/principles/001-xdr-standards.md)
- [_general-adr-003 - Skill standards](../../../_general/adrs/principles/003-skill-standards.md)
