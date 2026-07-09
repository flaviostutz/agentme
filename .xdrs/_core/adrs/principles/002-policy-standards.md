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

**Structured policies with a MANDATORY template, applicability metadata, and clear conflict rules**

Policy documents are the authoritative source of truth for their scope, type, and subject. They MUST be concise, template-compliant, and clear about applicability so that humans and AI agents can reliably determine whether and how to apply any decision.

### Details

- Policies MUST contain a clear decision about a certain problem or situation. Avoid being too verbose and focus on explaining clearly the context and the decision. Avoid adding contents that are not original. If you have other references that are important to understand the document, add links and references. Sources MUST be cited.
- Policies are the central artifact of the framework and the authoritative source of truth for their scope, type, and subject.
- Policy documents MUST include a YAML frontmatter block at the very beginning of the file. The supported fields are:

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1-64 characters. Lowercase letters, numbers, hyphens, and leading underscores only. MUST NOT end with a hyphen. MUST NOT contain consecutive hyphens. MUST match the document identifier from the heading: `[scope]-[type]-policy-[number]-[short-title]`. |
| `description` | Yes | 1-1024 characters. Describes what this decision is about and when to use it. SHOULD include keywords that help agents identify when to apply it. |
| `apply-to` | Yes | Short description of contexts this decision is applicable to. Keep it under 40 words. Use `All scopes` when the decision applies broadly. Examples: `Only frontend code`, `JavaScript projects`, `All scopes`. |
| `valid-from` | Yes | ISO date (`YYYY-MM-DD`) indicating from when this decision MUST be enforced. Before this date it SHOULD be used everywhere possible, but compliance is not enforced during reviews until after this date. Defaults to the date the Policy was created. When updating an existing Policy whose `valid-from` date has already passed, preserve the original date—it MUST NOT be updated to the current date. The historical date shows when the policy was originally enabled and is important for understanding policy evolution. |
| `license` | No | SPDX license expression (e.g. `MIT`, `Apache-2.0`, `CC-BY-4.0`). Indicates the license under which the document content is shared. If omitted, the license is governed by the repository or package defaults. |
| `metadata` | No | Arbitrary key-value map for additional properties not defined by this spec. |
| `freeze-reference` | No | Boolean (`true` or `false`, defaults to `false`). When `true`, the policy MUST NOT be renamed, renumbered, or moved because external parties reference it by its current identity (path, number, name, heading). Reference-identity issues are intentionally exempt. See rule [`01-freeze-reference-exemption`](#01-freeze-reference-exemption). |

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
- All documents present in the collection are considered active. There is no status field. When a decision is no longer relevant, valid or active, it MUST be removed from the collection. Historical versions are available via versioned packages or git history.
- Before using, enforcing, or citing a Policy as a current rule, humans and AI agents MUST decide whether the decision is applicable for the current case.
  - Check `valid-from:` first. If a date is present and has not yet been reached, the decision SHOULD be adopted for new implementations but is not enforced during reviews.
  - Check `apply-to:` next to determine whether the decision fits the current codebase, system, workflow, or audience.
  - Check the decision context and implementation details last to determine any additional boundaries, exceptions, or qualifiers that metadata alone cannot express.
- Research documents MAY be added under the same subject to capture the exploration, findings, and proposals that backed a decision. Research is useful during elaboration, discussion, and updates of Policies, but the Policy document remains the source of truth.
- **Policy Id:** [scope]-[type]-policy-[number] (numbers are scoped per type+scope combination and MUST NOT be reused within that combination; MUST be lowercase)
  - Types in IDs: `adr-policy`, `bdr-policy`, `edr-policy`
  - Policy numbers MUST follow the subject-based block ranges defined in [`_core-adr-policy-017`](017-policy-numbering-ranges.md). Each subject has a reserved 100-number block; use the lowest available number within the block for the chosen subject. Use the overflow range (901–999) only when the subject's block is exhausted.
  - Numbering gaps are expected and MUST NOT be filled, as gaps may represent deleted policies whose numbers MUST NOT be reused.
- Policies MUST be concise and reference other Policies to avoid duplication.
- Policies MUST NOT contain duplicated content: the same rule or information MUST NOT appear more than once in the document, whether stated identically or rephrased. Consolidate into a single authoritative statement and reference it where needed.
- Policies MUST NOT contain conflicting content: all rules and statements within the same document MUST be consistent with each other.
- The `### Details` section SHOULD state relevant boundaries or exceptions and what a reader SHOULD do or avoid in common cases. Use the frontmatter fields `apply-to` and `valid-from` as the first-pass filter for applicability, then keep nuanced boundaries in the decision text.
- Use concise rules, examples, `Allowed` / `Disallowed` lists or checklists with required items to help the reader apply the decision correctly. Keep them short and decision-specific.
- Policies MUST NOT include historical change notes or descriptions of what changed from a previous version. State only the current rule that MUST be followed. Historical context is available via git history or versioned packages.
- The `valid-from` field MUST NOT be updated automatically when a Policy is changed. It reflects the original enforcement date and MUST remain unchanged throughout the Policy's lifetime. Only update it intentionally when explicitly changing the enforcement start date as a deliberate decision.
- When a policy covers elements that could be confused with each other, include explicit disambiguation statements clarifying the distinction before stating the rules for each.
- A "why" explanation for a policy rule MAY only be included if it is brief, non-obvious, relevant to the reader, and not longer than the rule itself.
- Rules MUST focus on what is required or forbidden. Explanations of why a rule exists belong in a Research document, not in the Policy itself. Link to the relevant research when the rationale is important for adoption.
- Each policy rule and rule block MUST be unambiguous: it MUST be possible to clearly follow, check, and discuss it without requiring additional interpretation.
- When the decision defines strong policies or rules that SHOULD be stated explicitly as stable rule blocks, or when other documents, skills, or agents need to cite those rules individually by identifier, the Policy MUST follow the extension [_core-adr-policy-008 - Policy structured standards](008-policy-structured-standards.md) instead of using plain bullet lists for those rules.
- Conflict handling applies to Policy documents:
  - For cross-scope overrides, document the decision conflict in the Policy `## Conflicts` section of the Policy that overrides another scope.
  - **Within-scope conflicts:** Policies within the same type+scope MUST NOT conflict. If two Policies appear to conflict, one SHOULD be updated, removed, or the conflict resolved through a new Policy.
- When research exists for a decision, the Policy SHOULD mention the related research documents after the `## Considered Options` list.
- MUST NOT use emojis in contents.
- File names MUST be lowercase.
- Any non-Markdown files referenced by a Policy (schemas, JSON examples, images, diagrams, binaries, or any other data files) SHOULD be used only when they are materially necessary and MUST live in `[xdrs-root]/[scope]/[type]/[subject]/.assets/`.
- Avoid using lengthy instructions on the Policy. If there are long and detailed instructions related to the Policy, or instructions that are outside the decision, create another file with a guide. If the guide is small, keep it in the Policy itself.
- Policies SHOULD be under 1300 words long as a rule of thumb.
  - This is important to make them focused on a clear decision
  - Exceptions can reach under 2600 words (templates, more elaborate decision implementations etc)
- MUST use `_local` scope if the user doesn't explicitly indicate a specific scope while creating a policy or skill.

#### 01-freeze-reference-exemption

When a policy's frontmatter includes `freeze-reference: true`, the policy MUST NOT be renamed, renumbered, or moved because external parties reference it by its current identity. The policy's reference identity is its full addressable path and canonical identifier: scope location, type folder, subject folder, number, filename, frontmatter `name` field, and document heading identifier. All checks and reviews that would require changing the reference identity MUST be ignored unless the owner explicitly requests them to be fixed. Specifically, the following checks are exempt:

- Invalid subject folder (scope, subject, or type placement does not match allowed values)
- Numbering range mismatch (number outside the reserved block for the subject per [`_core-adr-policy-017`](017-policy-numbering-ranges.md))
- Document heading format mismatch (heading does not start with the expected `# scope-type-policy-number:` prefix)
- Frontmatter `name` field mismatch (name does not match the expected identifier derived from the file path)

Content-level checks that do not affect the policy's reference (required sections, word count, emojis, broken outgoing links, structured rule block format, normative language) remain enforced. The `valid-from` date is not taken into consideration when evaluating whether `freeze-reference` applies.

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
- [_core-adr-policy-008 - Policy structured standards](008-policy-structured-standards.md) - Extension for Policies that expose individually referenceable rules
