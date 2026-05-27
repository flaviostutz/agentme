---
name: _core-adr-policy-008-policy-standards-structured
description: Extends policy-standards with a numbered rule format for Policy documents that define strong policies or rules, or need individually referenceable items. Use when a Policy must expose explicit rule blocks that other documents or skills may cite by identifier.
apply-to: Policy documents requiring structured rule blocks
valid-from: 2025-01-01
---

# _core-adr-policy-008: Policy standards - structured

## Context and Problem Statement

Some Policy documents define multiple strong policies or rules that must be stated explicitly so they can be applied consistently. In other cases, documents, skills, or agents need to refer to one specific rule without copying its content. Without a standard format, prose references like "see the third bullet in Details" are fragile and ambiguous.

Question: How should a Policy document expose strong or individually referenceable rules or policies so they stay explicit, stable, and easy to cite?

## Decision Outcome

**Numbered rule blocks inside Details with a canonical citation syntax**

When a Policy document defines strong rules or policies that must be stated explicitly, or when documents and skills need to cite individual rules precisely, each rule must be placed inside `### Details` as a numbered heading block. Referencing documents and skills must cite rules using the canonical dot-notation identifier.

### Details

Use this format when the decision defines strong rules or policies that must be stated explicitly as stable rule blocks, or when there is a clear need for external documents, skills, or agents to reference specific items inside a Policy without duplicating the full policy text. Standard Policies that do not define strong rule sets and do not need item-level citation should follow `_core-adr-policy-002-policy-standards` without adding numbered rule headings.

#### Rule block format

Each numbered rule must be written as:

```markdown
#### [NN]-[short-rule-title-in-mandatory-advisory-language-in-kebab-case-<12-words]
[Body using mandatory or advisory language as defined in _core-adr-policy-001. State the requirement and the situations in which it must or should be followed. Under 500 words.]
```

Where `NN` is a two-digit zero-padded sequence number (e.g. `01`, `02`, `12`). Numbers must be unique within the document and must never be reused after a rule is removed. The short descriptive title must be in kebab-case (lowercase words separated by hyphens, no spaces or uppercase letters) and express the rule summary contents (e.g.: "43-code-must-be-linted", "12-use-standard-file-structure", "02-log-all-errors-to-mlflow")

Rule bodies must use the mandatory or advisory language terms defined in `_core-adr-policy-001`:

- Mandatory: "must", "always", "never", "required", "mandatory"
- Advisory: "should", "recommended", "advised", "preferably", "possibly", "optionally"

#### Citation syntax

When another document or skill cites a specific rule, it must use the following dot-notation:

```
policy-name.NN-short-rule-title-in-kebab-case
```

Examples:

- `_core-adr-policy-008-policy-standards-structured.01-always-use-numbered-rules-for-strong-or-referenceable-policies`
- `_local-bdr-policy-003-data-retention-policy.02-purge-schedule-for-pii`

The `policy-name` must match the `name` field in the frontmatter of the source document exactly. The rule identifier after the dot must match the heading text exactly, including the two-digit prefix.

#### 01-always-use-numbered-rules-for-strong-or-referenceable-policies

Numbered rule blocks must be added to a Policy when the decision defines strong rules or policies that must be stated explicitly as stable items, or when there is a clear need for other documents, skills, or agents to cite individual rules by identifier. Adding numbered rules only for cosmetic organization is not recommended. Standard Policy documents that do not define strong rule sets and are not expected to be cited at the rule level should follow `_core-adr-policy-002-policy-standards` without this structured format.

#### 02-rule-numbering-must-be-stable

Rule numbers must never be reused within the same document. When a rule is removed, its number becomes permanently retired for that document. Gaps in the sequence are expected and must not be filled by renumbering remaining rules, as existing citations depend on number stability.

#### 03-rule-body-must-use-normative-language

Every rule body must contain at least one mandatory or advisory language term as defined in `_core-adr-policy-001`. Rule bodies without normative language must not be published, as they fail to communicate whether compliance is required or recommended.

#### 04-citations-must-use-exact-identifiers

Documents and skills that cite a rule must use the exact dot-notation form: `policy-name.NN-short-rule-title-in-kebab-case`. Prose paraphrases such as "see rule 3" or "the third rule in that Policy" must not be used as citations, because they are ambiguous and break when rules are reordered or reworded.

## Considered Options

* (REJECTED) **Free-form prose rules with section anchors** — Use markdown heading anchors as citation targets.
  * Reason: Anchors are fragile across editors, rendering tools, and refactors. They do not enforce a stable numbering contract and break silently when headings are reworded.
* (CHOSEN) **Numbered rule blocks inside Details** — Prefix each rule heading with a two-digit sequence number and use dot-notation for citations.
  * Reason: Minimal addition to the existing Policy template, stable identifiers independent of heading text, and fully compatible with `_core-adr-policy-002-policy-standards`.

## References

- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md)
- [_core-adr-policy-002 - Policy standards](002-policy-standards.md)
