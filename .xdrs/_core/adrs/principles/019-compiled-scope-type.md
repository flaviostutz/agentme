---
name: _core-adr-policy-019-compiled-scope-type
description: Defines the `compiled` scope type — scopes whose policies are compiled strictly from external authoritative sources (web pages, git repositories, or local folders). All content must trace back to source; no invented content is permitted. The type may be combined with other scope types. Use when declaring a compiled-type scope, authoring content in a compiled scope, or configuring the compilation process.
apply-to: All XDRS scope authors declaring compiled-type scopes; tools or agents compiling or reviewing compiled scopes
valid-from: 2026-08-03
---

# _core-adr-policy-019: compiled scope type

## Context and Problem Statement

Some XDRS scopes exist to provide structured policy representations of external authoritative sources — industry standards, regulatory frameworks, vendor documentation, or reference materials published on the web, in git repositories, or in local folders. The content of these scopes must remain strictly faithful to the source: editorial additions, invented rules, and inferences beyond what the source states are not permitted.

These scopes differ structurally from `reference`, `platform`, and `standard` scopes: they are defined by a systematic compilation process, require source traceability in every policy, and must document any inconsistencies found in the source rather than silently correcting them.

How should a scope that exists solely as a compiled representation of external sources be identified and governed?

## Decision Outcome

**Declare `scope-type: compiled` for any scope whose policies are compiled directly from one or more external sources, where all content must trace back to the source and no invention is permitted.**

### Details

#### 01-scope-type-name

The scope type defined by this policy is `compiled`. A scope MUST declare it by setting `scope-type: compiled` in its `index.md` YAML frontmatter. The `compiled` type MAY be combined with one or more other scope types using a comma-separated list (e.g., `scope-type: compiled, reference`).

#### 02-when-to-use

Use `scope-type: compiled` when the scope holds policies that are directly compiled from external authoritative sources and where the primary governance constraint is source fidelity, not editorial judgment. Examples include:

- Policies compiled from industry standards (e.g., OWASP Top 10, NIST guidelines, ISO 27001 controls).
- Policies compiled from vendor documentation, product specifications, or API contracts.
- Policies compiled from regulatory texts, compliance frameworks, or legal documents.
- Policies compiled from internal reference documents published in another repository or folder.

`scope-type: compiled` MUST NOT be used for scopes that contain policies authored from scratch, derived from general knowledge, or editorially synthesised without a direct external source.

#### 03-naming-convention

`compiled`-type scopes have no required naming pattern. Any valid scope name MAY be used. When `compiled` is combined with another type (e.g., `scope-type: compiled, reference`), the naming convention of the non-`compiled` type MUST apply.

#### 04-structured-format-required

All policies in a `compiled` scope MUST use the structured policy format defined in `_core-adr-policy-008`. Every claim or rule originating from the source MUST be expressed as an individually referenceable numbered rule block.

#### 05-source-traceability

Every policy claim, rule body, and normative statement in a `compiled` scope MUST be traceable to at least one external source. Content MUST NOT be invented, inferred beyond what the source states, or filled in to cover gaps. Where the source is ambiguous or contradictory, the ambiguity or contradiction MUST be transcribed faithfully and documented as an inconsistency per rule 08.

XDRS structural frontmatter fields (`name`, `description`, `apply-to`, `valid-from`) are explicitly exempt from this rule. These fields are generated from source text by the compilation process and are not considered invented content.

#### 06-source-types

Sources for a compiled scope MAY be specified as:

- A web URL pointing to a publicly accessible page or document.
- A git repository URL (e.g., `git@github.com:org/repo.git` or `https://github.com/org/repo.git`) pointing to a repository containing the source content.
- A local folder path relative to the workspace root.

When multiple source entries point to the same content (e.g., a web page and its git mirror), all MAY be listed so that the compilation process can use whichever source is accessible. The preference order for fetching is: git URL first, then local folder, then web URL.

#### 07-compilation-meta-policy

Before any compilation begins, at least one local meta-policy file named `NNN-core.md` MUST exist in a `[type]/principles/` directory of the target scope (e.g., `adrs/principles/001-core.md`). Compilation tools and agents MUST scan all type folders (`adrs`, `bdrs`, `edrs`) for such meta-policy files; each meta-policy governs compilation for its own type folder.

The meta-policy MUST contain the following sections:

- `## Sources` — one bullet per source using the format `- [web] https://...`, `- [git] git@...`, or `- [local] ./path`. Each source entry MAY include an inline description after the URL.
- `## Selectors` — describes which portions of the fetched source to include or exclude, expressed as document sections, filename patterns, topics, or other criteria.

The meta-policy MAY also contain:

- `## Fetch Procedures` — special instructions for fetching the source (authentication, crawl depth, pagination, format conversion, etc.).
- `## Compilation Notes` — guidance on how to structure or categorise the compiled content.
- `## Review Notes` — guidance for reviewers verifying compiled content against the source.

#### 08-inconsistencies-policy

If the source contains inconsistencies, contradictions, errors, or gaps that cannot be faithfully transcribed as a valid policy, the compiled scope MUST document them in a dedicated policy file at `[type]/principles/NNN-inconsistencies-from-source.md`. Each inconsistency MUST reference the source file path and the affected compiled policy. Inconsistencies MUST NOT be silently corrected, omitted, or worked around.

#### 09-ordering

There is no fixed position for `compiled`-type scopes in the root `index.md`. When `compiled` is combined with another type, the ordering convention of the non-`compiled` type governs placement. When declared standalone, a `compiled` scope MAY appear at any position before `_local`.

#### 10-source-section

Every compiled policy MUST include a `## Source` section placed after the `## References` section (or after `## Decision Outcome` when no `## References` section is present). The section MUST list the relative file path(s) of the source document(s) used to produce the policy as plain text. Paths MUST NOT be written as markdown links, because the source files exist only inside a temporary local directory that is created during the compilation or review process.

Example:

```
## Source

- source-1/standards/owasp-top-10-2021/A01-broken-access-control.md
- source-2/docs/security-controls.html
```

#### 11-compilation-notes

Rule bodies in compiled policies SHOULD include `**compilation-note:**` inline markers when the mapping from source to rule is not obvious — for example: indirect references, conclusions drawn from multiple source sections, or interpretations that required judgment. Direct literal transcriptions of a single source statement do not require a marker. Review and update processes MUST consult these notes and re-fetch the source before making changes to compiled rules.

Example:

```
#### 03-access-control-must-enforce-least-privilege

All access control implementations MUST enforce the principle of least privilege.
**compilation-note:** derived from OWASP A01:2021 "How to Prevent", bullet 3 — "Deny by default".
```

## References

- [_core-adr-policy-008 - Policy structured standards](008-policy-structured-standards.md) — numbered rule format required for all policies in compiled scopes
- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — scope-type definition convention and local meta-policy mechanism
- [_core-adr-policy-002 - Policy standards](002-policy-standards.md) — policy document format and frontmatter requirements
- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md) — scope structure and `scope-type` field definition
