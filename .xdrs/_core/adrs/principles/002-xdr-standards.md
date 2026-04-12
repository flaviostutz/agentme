# _core-adr-002: XDR standards

## Context and Problem Statement

XDR framework elements (types, scopes, subjects, folder structure) are defined in `_core-adr-001`. Once a decision record's structural placement is clear, how should the document itself be written to remain authoritative, concise, and consistently structured?

## Decision Outcome

**Structured decision records with a mandatory template, applicability metadata, and clear conflict rules**

XDR documents are the authoritative policy for their scope, type, and subject. They must be concise, template-compliant, and clear about applicability so that humans and AI agents can reliably determine whether and how to apply any decision.

### Implementation Details

- XDRs MUST contain a clear decision about a certain problem or situation. Avoid being too verbose and focus on explaining clearly the context and the decision. Avoid adding contents that are not original. If you have other references that are important to understand the document, add links and references. Always cite sources.
- XDRs are the central artifact of the framework and the authoritative policy for their scope, type, and subject. Supporting artifacts may explain, justify, or operationalize the decision (like articles, researches and skills), but they do not replace it.
- XDRs MAY include a `## Metadata` section, but only when at least one supported metadata field is present. When used, `## Metadata` MUST appear immediately before `## Context and Problem Statement`.
- Supported XDR metadata fields are:
  - `Valid:` Optional. Defines a convergence date after which the decision is expected to be fully adopted. Use ISO date format: `from YYYY-MM-DD`. New implementations SHOULD adopt the decision immediately, but compliance is not enforced during reviews until the convergence date.
  - `Applied to:` Optional. A short description of the contexts in which the decision is applicable. Keep it under 40 words. If omitted, the decision should be interpreted as applying to all logically applicable elements according to the decision text itself. Examples: `Only frontend code`, `JavaScript projects`, `Performance-sensitive codebases`
- All documents present in the collection are considered active. There is no status field. When a decision is no longer relevant, valid or active, it must be removed from the collection. Historical versions are available via versioned packages or git history.
- Before using, enforcing, or citing an XDR as a current rule, humans and AI agents MUST decide whether the decision is applicable for the current case.
  - Check `Valid:` first. If a convergence date is present and has not yet been reached, the decision SHOULD be adopted for new implementations but is not enforced during reviews.
  - Check `Applied to:` next to determine whether the decision fits the current codebase, system, workflow, or audience.
  - Check the decision context and implementation details last to determine any additional boundaries, exceptions, or qualifiers that metadata alone cannot express.
- Research documents MAY be added under the same subject to capture the exploration, findings, and proposals that backed a decision. Research is useful during elaboration, discussion, and updates of XDRs, but the XDR document remains the source of truth.
- **XDR Id:** [scope]-[type]-[xdr number] (numbers are scoped per type+scope combination and must not be reused within that combination; always use lowercase)
  - Types in IDs: `adr`, `bdr`, `edr`
  - Define the next number of an XDR by checking what is the highest number present in the type+scope. Don't fill numbering gaps, as they might be old deleted XDRs and we should never reuse numbers of different documents/decisions. Numbering gaps are expected.
- Decisions MUST be concise and reference other XDRs to avoid duplication.
- The `### Implementation Details` section SHOULD state relevant boundaries or exceptions and what a reader should do or avoid in common cases. Use `## Metadata` as the first-pass filter for applicability, then keep nuanced boundaries in the decision text.
- Use concise rules, examples, `Allowed` / `Disallowed` lists or checklists with required items to help the reader apply the decision correctly. Keep them short and decision-specific.
- Conflict handling applies to XDR documents:
  - For cross-scope overrides, document the decision conflict in the XDR `## Conflicts` section of the XDR that overrides another scope.
  - **Within-scope conflicts:** XDRs within the same type+scope must not conflict. If two XDRs appear to conflict, one should be updated, removed, or the conflict resolved through a new XDR.
- When research exists for a decision, the XDR SHOULD mention the related research documents after the `## Considered Options` list.
- Never use emojis in contents.
- Always use file names with lowercase.
- Avoid using lengthy instructions on the XDR. If there are long and detailed instructions related to the XDR, or instructions that are outside the decision, create another file with a guide. If the guide is small, keep it in the XDR itself.
- XDRs should be under 1300 words long as a rule of thumb.
  - This is important to make them focused on a clear decision
  - Exceptions can reach under 2600 words (templates, more elaborate decision implementations etc)
- ALWAYS use `_local` scope if the user doesn't explicitly indicate a specific scope while creating an xdr or skill.

**XDR template**

All XDRs MUST follow this template

```markdown
# [scope]-[type]-[number]: [Short Title]

## Metadata

[Optional section. Omit the entire section when none of `Valid:` or `Applied to:` is defined. Readers decide whether to use the XDR by checking `Valid:` first, then `Applied to:`, and finally the decision text itself.]
Valid: [Optional. Use `from YYYY-MM-DD` to set a convergence date for adoption]
Applied to: [Optional short applicability scope, under 40 words]

## Context and Problem Statement

[Describe the context, background, or need that led to this decision.
What is the problem we are trying to solve? Who is being impacted? (<40 words)

Question: In the end, state explicitly the question that needs to be answered. E.g: "Which platform should I use when implementing an AI agent?"]

## Decision Outcome

**[Chosen Option Title]**
[Very short description of what is the decision, aligned with the titles on the Considered Options section]

[Short description of implementation details for the chosen path]

### Implementation Details

[Optional section with implementation specifics, applicability boundaries, rules, concise examples, or do/don't guidance. This is the answer to the question in the "Context and Problem Statement". (<1300 words)]

[Related research, if any]
- [Research document title](researches/001-example.md) - Brief description of what it informed

## Conflicts

[If this XDR has conflicts with other scopes, this section is MANDATORY and needs to have an explanation why the conflict is accepted]

* Conflict with [XDR id] (e.g.: adr-business-x-001)
  * Summary: Brief description of the conflict
  * Reason to accept: Brief description of why it was decided to accept this conflict, possibly overriding or diverging from the other decision/scopes

## References

[optional section]
[useful links related to this implementation]
[links to the discussion (PRs, meetings etc)]
[links to related skills]
```

**Examples:**
- Metadata examples:
  - `Valid: from 2026-03-01`
  - `Applied to: JavaScript projects`

**XDR ID Examples:**
- `business-x-adr-001` (not `ADR-business-x-001` or `business-x-adr-1`)
- `business-x-edr-042` (not `EDR-BUSINESS-X-042`)
- `business-x-bdr-007`

## References

- [_core-adr-001 - XDRs core](001-xdrs-core.md) - Framework elements: types, scopes, subjects, folder structure
- [001-lint skill](skills/001-lint/SKILL.md) - Skill for reviewing code changes against XDRs
- [002-write-xdr skill](skills/002-write-xdr/SKILL.md) - Skill for creating a new XDR following this standard
- [_core-adr-003 - Skill standards](003-skill-standards.md)
- [_core-adr-004 - Article standards](004-article-standards.md)
- [_core-adr-006 - Research standards](006-research-standards.md)
