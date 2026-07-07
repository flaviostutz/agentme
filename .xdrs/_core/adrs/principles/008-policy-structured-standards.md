---
name: _core-adr-policy-008-policy-structured-standards
description: Extends policy-standards with a numbered rule format for Policy documents that define strong policies or rules, or need individually referenceable items. Use when a Policy must expose explicit rule blocks that other documents or skills may cite by identifier.
apply-to: Policy documents requiring structured rule blocks
valid-from: 2025-01-01
---

# _core-adr-policy-008: Policy structured standards

## Context and Problem Statement

Some Policy documents define strong rules or constraints that must be individually referenceable by other documents, skills, or automated agents. The standard policy format from `_core-adr-policy-002` does not specify how such numbered rule blocks should be structured, titled, or cited. Without a consistent format, citations become ambiguous and tools cannot reliably locate referenced rules.

## Decision Outcome

**Numbered rule blocks with stable identifiers, normative language, and dot-notation citations**

Policies that define strong or frequently-cited rules MUST use a numbered rule block format. Each rule receives a stable two-digit identifier, a lowercase kebab-case title, and a body with at least one normative keyword. Citations MUST use dot-notation referencing the exact rule identifier.

### Details

#### 01-always-use-numbered-rules-for-strong-or-referenceable-policies

A Policy MUST use numbered rule blocks when it defines strong rules that must be stable and referenceable. Rules MUST NOT be added for cosmetic organization only. Policies without strong rule sets SHOULD follow `_core-adr-policy-002-policy-standards` instead.

#### 02-rule-numbering-must-be-stable

Rule numbers MUST NOT be reused within the same document. When a rule is removed, its number is permanently retired. Gaps MUST NOT be filled by renumbering remaining rules.

#### 03-rule-body-must-use-normative-language

Every rule body MUST contain at least one normative term (MUST, SHOULD, MAY, etc.) as defined in `_core-adr-policy-001`. Rule bodies without normative language MUST NOT be published.

#### 04-citations-must-use-exact-identifiers

Citations MUST use the exact dot-notation form: `policy-name.NN-short-rule-title-in-kebab-case`. Prose references such as "see rule 3" or "the third rule" MUST NOT be used.

#### 05-rule-title-must-be-all-lowercase

Rule titles MUST be all lowercase. Uppercase letters MUST NOT appear in rule titles, including normative keywords (e.g. `01-code-must-be-linted`, not `01-code-MUST-be-linted`).

#### 06-normative-keywords-must-not-use-emphasis-marks

Normative keywords in rule bodies MUST be written as plain text. Bold or italic markers around normative keywords MUST NOT be used.

#### 07-rule-title-should-include-normative-keyword-in-simple-cases

A rule title SHOULD include a normative keyword when the rule can be stated clearly in a short phrase. For complex rules, the title MAY omit normative language, provided the rule body contains it.

#### 08-rule-block-must-use-standard-syntax

Each rule MUST be written as a level-4 heading with a two-digit zero-padded sequence number followed by a kebab-case title, and a body paragraph:

```markdown
#### [NN]-[short-rule-title-in-kebab-case]
[Rule body using normative language per _core-adr-policy-001. Under 500 words.]
```

#### 09-citations-must-use-dot-notation

Citations MUST use dot-notation where `policy-name` matches the `name` frontmatter field and the rule identifier after the dot matches the heading text exactly:

```
policy-name.NN-short-rule-title-in-kebab-case
```

Examples:
- `_core-adr-policy-008-policy-structured-standards.01-always-use-numbered-rules-for-strong-or-referenceable-policies`
- `_local-bdr-policy-003-data-retention-policy.02-purge-schedule-for-pii`

## References

- [_core-adr-policy-001 - XDRS core](001-xdrs-core.md)
- [_core-adr-policy-002 - Policy standards](002-policy-standards.md)
