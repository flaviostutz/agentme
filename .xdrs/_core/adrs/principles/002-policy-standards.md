---
name: _core-adr-policy-002-policy-standards
description: Defines how Policy documents (the core Policy document type) should be written, including template, frontmatter, applicability fields, and conflict handling. Use when writing or reviewing any Policy, rules, contraints or a specific decision document.
apply-to: All Policy documents
valid-from: 2025-01-01
---

# _core-adr-policy-002: Policy standards

## Context and Problem Statement

Policy framework elements (types, scopes, subjects, folder structure) are defined in `_core-adr-policy-001`. Once a policy's structural placement is clear, how should the document itself be written to remain authoritative, concise, and consistently structured?

## Decision Outcome

**Structured policies with a mandatory template, applicability metadata, and clear conflict rules**

Policy documents are the authoritative source of truth for their scope, type, and subject. They must be concise, template-compliant, and clear about applicability so that humans and AI agents can reliably determine whether and how to apply any decision.

### Details

- Policies MUST contain a clear decision about a certain problem or situation. Avoid being too verbose and focus on explaining clearly the context and the decision. Avoid adding contents that are not original. If you have other references that are important to understand the document, add links and references. Always cite sources.
- Policies are the central artifact of the framework and the authoritative source of truth for their scope, type, and subject.
- Policy documents MUST include a YAML frontmatter block at the very beginning of the file. The supported fields are:

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1-64 characters. Lowercase letters, numbers, hyphens, and leading underscores only. Must not end with a hyphen. Must not contain consecutive hyphens. Must match the document identifier from the heading: `[scope]-[type]-policy-[number]-[short-title]`. |
| `description` | Yes | 1-1024 characters. Describes what this decision is about and when to use it. Should include keywords that help agents identify when to apply it. |
| `apply-to` | Yes | Short description of contexts this decision is applicable to. Keep it under 40 words. Use `All scopes` when the decision applies broadly. Examples: `Only frontend code`, `JavaScript projects`, `All scopes`. |
| `valid-from` | Yes | ISO date (`YYYY-MM-DD`) indicating from when this decision must be enforced. Before this date it should be used everywhere possible, but compliance is not enforced during reviews until after this date. Defaults to the date the Policy was created. |
| `license` | No | SPDX license expression (e.g. `MIT`, `Apache-2.0`, `CC-BY-4.0`). Indicates the license under which the document content is shared. If omitted, the license is governed by the repository or package defaults. |
| `metadata` | No | Arbitrary key-value map for additional properties not defined by this spec. |

  - Minimal example:
    ```yaml
    ---
    name: _core-adr-policy-002-policy-standards
    description: Defines how Policy documents should be written. Use when writing or reviewing any Policy.
    apply-to: All scopes
    valid-from: 2026-05-21
    ---
    ```
  - Example with optional fields:
    ```yaml
    ---
    name: _core-adr-policy-002-policy-standards
    description: Defines how Policy documents should be written. Use when writing or reviewing any Policy.
    apply-to: All Policy scopes
    valid-from: 2026-06-01
    metadata:
      author: example-org
    ---
    ```
- All documents present in the collection are considered active. There is no status field. When a decision is no longer relevant, valid or active, it must be removed from the collection. Historical versions are available via versioned packages or git history.
- Before using, enforcing, or citing a Policy as a current rule, humans and AI agents MUST decide whether the decision is applicable for the current case.
  - Check `valid-from:` first. If a date is present and has not yet been reached, the decision SHOULD be adopted for new implementations but is not enforced during reviews.
  - Check `apply-to:` next to determine whether the decision fits the current codebase, system, workflow, or audience.
  - Check the decision context and implementation details last to determine any additional boundaries, exceptions, or qualifiers that metadata alone cannot express.
- Research documents MAY be added under the same subject to capture the exploration, findings, and proposals that backed a decision. Research is useful during elaboration, discussion, and updates of Policies, but the Policy document remains the source of truth.
- **Policy Id:** [scope]-[type]-policy-[number] (numbers are scoped per type+scope combination and must not be reused within that combination; always use lowercase)
  - Types in IDs: `adr-policy`, `bdr-policy`, `edr-policy`
  - Define the next number of a Policy by checking what is the highest number present in the type+scope. Don't fill numbering gaps, as they might be old deleted Policies and we should never reuse numbers of different documents/decisions. Numbering gaps are expected.
- Policies MUST be concise and reference other Policies to avoid duplication.
- The `### Details` section SHOULD state relevant boundaries or exceptions and what a reader should do or avoid in common cases. Use the frontmatter fields `apply-to` and `valid-from` as the first-pass filter for applicability, then keep nuanced boundaries in the decision text.
- Use concise rules, examples, `Allowed` / `Disallowed` lists or checklists with required items to help the reader apply the decision correctly. Keep them short and decision-specific.
- When the decision defines strong policies or rules that should be stated explicitly as stable rule blocks, or when other documents, skills, or agents need to cite those rules individually by identifier, the Policy MUST follow the extension [_core-adr-policy-008 - Policy standards - structured](008-xdr-standards-structured.md) instead of using plain bullet lists for those rules.
- Conflict handling applies to Policy documents:
  - For cross-scope overrides, document the decision conflict in the Policy `## Conflicts` section of the Policy that overrides another scope.
  - **Within-scope conflicts:** Policies within the same type+scope must not conflict. If two Policies appear to conflict, one should be updated, removed, or the conflict resolved through a new Policy.
- When research exists for a decision, the Policy SHOULD mention the related research documents after the `## Considered Options` list.
- Never use emojis in contents.
- Always use file names with lowercase.
- Any non-Markdown files referenced by a Policy (schemas, JSON examples, images, diagrams, binaries, or any other data files) SHOULD be used only when they are materially necessary and MUST live in `[xdrs-root]/[scope]/[type]/[subject]/.assets/`.
- Avoid using lengthy instructions on the Policy. If there are long and detailed instructions related to the Policy, or instructions that are outside the decision, create another file with a guide. If the guide is small, keep it in the Policy itself.
- Policies should be under 1300 words long as a rule of thumb.
  - This is important to make them focused on a clear decision
  - Exceptions can reach under 2600 words (templates, more elaborate decision implementations etc)
- ALWAYS use `_local` scope if the user doesn't explicitly indicate a specific scope while creating a policy or skill.

**Policy template**

All Policies MUST follow this template

```markdown
---
name: [scope]-[type]-policy-[number]-[short-title]
description: [What this decision is about and when to use it]
apply-to: [Required. Contexts this decision applies to, under 40 words. Use "All scopes" when broadly applicable.]
valid-from: [Required. ISO date YYYY-MM-DD from when enforcement begins. Defaults to creation date.]
license: [Optional. SPDX license expression]
metadata:
  [optional-key]: [optional-value]
---

# [scope]-[type]-policy-[number]: [Short Title]

## Context and Problem Statement

[Describe the context, background, or need that led to this decision.
What is the problem we are trying to solve? Who is being impacted? (<40 words)

Question: In the end, state explicitly the question that needs to be answered. E.g: "Which platform should I use when implementing an AI agent?"]

## Decision Outcome

**[Chosen Option Title]**
[Very short description of what is the decision, aligned with the titles on the Considered Options section]

[Short description of implementation details for the chosen path]

### Details

[Optional section with implementation specifics, applicability boundaries, rules, concise examples, or do/don't guidance. This is the answer to the question in the "Context and Problem Statement". (<1300 words)]

## Considered Options 
[this section is present ONLY if the user explicitely indicated that there were multiple options to choose from while making this decision or have a backing research document]

[Related research, if any]
- [Research document title](researches/001-example.md) - Brief description of what it informed

## Conflicts

[If this Policy has conflicts with other scopes, this section is MANDATORY and needs to have an explanation why the conflict is accepted]

* Conflict with [Policy id] (e.g.: business-x-adr-policy-001)
  * Summary: Brief description of the conflict
  * Reason to accept: Brief description of why it was decided to accept this conflict, possibly overriding or diverging from the other decision/scopes

## References

[optional section]
[useful links related to this implementation]
[links to the discussion (PRs, meetings etc)]
[links to related skills]
```

**Examples:**
- Frontmatter examples:
  - `valid-from: 2026-03-01`
  - `apply-to: JavaScript projects`

**Policy ID Examples:**
- `business-x-adr-policy-001` (not `ADR-business-x-001` or `business-x-adr-1`)
- `business-x-edr-policy-042` (not `EDR-BUSINESS-X-042`)
- `business-x-bdr-policy-007`

## References

- [_core-adr-policy-001 - Policies core](001-xdrs-core.md) - Framework elements: types, scopes, subjects, folder structure
- [001-review skill](skills/001-review/SKILL.md) - Skill for reviewing code changes against Policies
- [002-write-policy skill](skills/002-write-policy/SKILL.md) - Skill for creating a new Policy following this standard
- [_core-adr-policy-003 - Skill standards](003-skill-standards.md)
- [_core-adr-policy-004 - Article standards](004-article-standards.md)
- [_core-adr-policy-006 - Research standards](006-research-standards.md)
- [_core-adr-policy-008 - Policy standards - structured](008-xdr-standards-structured.md) - Extension for Policies that expose individually referenceable rules
