---
name: _core-adr-policy-010-scope-governance
description: Defines how scope types and scope-local standards are declared and applied. Covers how to author a custom scope-type policy, how to define scope-local content standards, and how all governance mechanisms (scope-type, follows, scope-local) interact with their precedence chain. Use when defining a new scope type, setting local standards for a scope, or understanding how governance is applied when adding content to a scope.
apply-to: All XDRS scopes, core scopes defining scope types, and tools/agents processing scope content
valid-from: 2026-07-01
---

# _core-adr-policy-010: Scope governance

## Context and Problem Statement

XDRS provides three mechanisms that govern what content belongs in a scope and how it should be structured:

1. **Scope-type standards**: a policy in a `core`-type scope that defines the rules for all scopes of that type.
2. **`follows:` declarations**: a scope explicitly declares that it follows the standards of a named `core`-type scope.
3. **Scope-local standards**: a policy inside a scope that defines content rules specific to that one scope.

## Decision Outcome

**Define scope types as policies, local meta-policies as `core`-named policies in `principles/`, and a clear precedence chain for governance application.**

All scope types — both the five built-in types and any custom types — are defined using the same convention: a `{scope-type}-scope-type` policy in a `core`-type scope. Scope-local standards (called _local meta-policies_) are optional policies whose filename title starts with `core` and which are placed in the `principles` subject of the scope. Multiple local meta-policy files are allowed, each distinguished by an optional qualifier. Tools and agents apply all applicable standards in a defined order.

> **Choosing between a local meta-policy and a `-core` sibling scope**: use a local meta-policy when the standards apply only to one scope. Use a `-core` sibling scope (see `_core-adr-policy-011`) when the governance needs to be shared or governs a family of scopes.

### Details

**Section A — Scope-type definition standards**

#### 01-def-must-live-in-core-scope

A scope-type definition policy MUST be placed in a `core`-type scope (i.e., a scope whose `index.md` declares `scope-type: core`).

#### 02-def-naming

The policy `name` field MUST end with `{scope-type}-scope-type` (e.g., `security-scope-type`, `business-area-scope-type`). The policy file MUST follow the standard numbered filename convention `NNN-{scope-type}-scope-type.md` and MUST be placed in the `principles` subject of any decision type folder within the `core`-type scope (e.g., `_core/adrs/principles/011-core-scope-type.md`).

Note: this naming applies to the **policy name** only, not to any scope directory name. It is distinct from the `-core` scope-name suffix convention defined in `_core-adr-policy-011`.

#### 03-def-companion-files

A scope-type definition MAY be split across multiple policy files. The primary file MUST follow rule 02 above. Each additional companion file MUST be named `NNN-{scope-type}-scope-type-{qualifier}.md` (e.g., `012-business-area-scope-type-writing-style.md`), where `{qualifier}` is a short lowercase kebab-case descriptor. All companion files MUST be placed in the **same** `[type]/principles/` directory as the primary file within the same scope. A companion file MUST NOT exist without a corresponding primary file in the same scope and type folder. Tools and agents MUST apply all companion files for a scope-type as additional mandatory conventions alongside the primary.

#### 04-def-required-content

A scope-type definition policy MUST define:

- The scope type name (the value that instances declare in their `scope-type:` field).
- When to use this scope type and what kinds of scopes SHOULD declare it.

#### 05-def-preferred-content

A scope-type definition policy SHOULD define:

- Naming conventions for scope instances of this type.
- What content SHOULD be placed in scopes of this type.
- What content SHOULD NOT be placed in scopes of this type.
- Special instructions on how to organise or write content in scopes of this type.

#### 06-def-instance-declaration

A scope that is an instance of one or more scope types MUST declare `scope-type` in its `index.md` frontmatter. Two formats are valid:

- **Single type**: `scope-type: business-area`
- **Multiple types** (comma-separated): `scope-type: compiled, internal-docs, auditable`

When multiple scope types are declared, all rules from all declared types (and their parent chains) apply simultaneously to documents in the scope. A document MUST satisfy the requirements of every applicable type. When two types define a rule with the same rule number but different content, the conflict MUST be declared in a `## Conflicts` section of the overriding scope-type policy (see Section C rule 26-conflict-declarations). An undeclared conflict makes a document impossible to satisfy and MUST be resolved before authoring begins.

#### 07-def-multi-type-validation

A comma-separated `scope-type` list MUST NOT have empty elements. Each element MUST satisfy the same constraints as a single `scope-type` value (rules 08 and 10). Duplicate values within the same list are NOT allowed.

#### 08-def-no-underscore-prefix

Custom scope-type names MUST NOT start with `_`. The `_` prefix is reserved for built-in scope types defined in `_core` (currently only `_local`).

#### 09-def-parent-scope-type

A scope-type definition policy MAY declare a parent scope type by including a rule titled `NN-parent-scope-type` in its `### Details` section. The body of that rule MUST reference the parent scope-type name in backticks (e.g., "Instances of this scope type inherit all rules from the `standard` scope type."). This rule MUST appear only in the **primary** file (rule 02), not in a companion file (rule 03). Tools and agents MUST resolve the full parent chain transitively. Child scope-type standards override parent standards on any conflict.

#### 10-def-valid-iff-policy-exists

A `scope-type` value in a scope `index.md` is valid if and only if a policy file whose name ends with `{scope-type}-scope-type` exists in the `principles` subject of any `core`-type scope in the workspace. Tools (such as `xdrs-core lint`) MUST enforce this for every element when `scope-type` is an array.

When a scope declares a `scope-type` but any corresponding `{scope-type}-scope-type.md` policy is absent from the workspace, the scope MUST be treated as READ-ONLY: content MUST NOT be added, changed, removed, or reviewed. Tools MUST surface the read-only status and MUST NOT apply changes until the scope-type governance is installed.

#### 11-def-scope-type-must-be-structured

All `{scope-type}-scope-type.md` policies (primary and companion files) MUST follow the structured format defined in `_core-adr-policy-008`: the policy MUST contain a `### Details` section and at least one `#### NN-rulename` rule block within it. This makes individual scope-type rules machine-readable, individually citable, and detectable for conflict analysis. Tools MUST enforce this and report an error using code `_core-adr-policy-010-scope-governance.11-def-scope-type-must-be-structured`.

#### 12-def-core-scope-policies-must-be-structured

All policy files in a `core`-type scope (a scope whose `index.md` declares `scope-type: core`) MUST follow the structured format defined in `_core-adr-policy-008` (see rule 11). This requirement applies to ALL policies in the scope, not only scope-type definitions or local meta-policies. The `_core` scope itself is exempt from this requirement until its existing policies are migrated. Tools MUST enforce this for all non-exempt core-type scopes and report an error using code `_core-adr-policy-010-scope-governance.12-def-core-scope-policies-must-be-structured`.

---

**Section B — Local meta-policies**

#### 13-local-naming

The word `core` as a hyphen-delimited segment in a policy filename title is reserved for local meta-policies. A local meta-policy is identified by its filename title starting with `core`: either `NNN-core.md` (primary, no qualifier) or `NNN-core-{qualifier}.md` (companion, where `{qualifier}` is a short lowercase kebab-case descriptor). A policy filename title MUST NOT use `core` as a word segment unless it is a valid local meta-policy (see rule 14). Scope-type definition files (`NNN-{scope-type}-scope-type.md`) are exempt from this restriction even when their title begins with `core`.

#### 14-local-placement

Local meta-policy files MUST be placed in the `principles` subject of any type folder within the scope they govern (e.g., `my-team/adrs/principles/001-core.md`). They apply implicitly to that scope — no declaration in `index.md` is required. Local meta-policies MUST NOT be placed in any other subject folder; a file whose title starts with `core` in a non-`principles` subject is a lint error.

#### 15-local-primary-required

A companion local meta-policy (`NNN-core-{qualifier}.md`) MUST NOT exist in a type folder unless a primary local meta-policy (`NNN-core.md`) also exists in the **same** type folder. Tools MUST enforce this constraint.

#### 16-local-unique-qualifier

Each qualifier (including the blank qualifier of the primary) MUST be unique across all type folders within the same scope. For example, a scope MUST NOT have both `adrs/principles/001-core.md` and `bdrs/principles/001-core.md` — the blank qualifier would appear twice.

#### 17-local-optional

Creating a local meta-policy is optional. It SHOULD be created when a scope has specific structural, authoring, or content constraints that differ from `_core` defaults or the scope's declared scope-type standards.

#### 18-local-content

A local meta-policy SHOULD define the same kinds of instructions as a scope-type definition policy (rules 04–05 above): naming conventions for content in the scope, allowed content, forbidden content, and organisation rules. These instructions apply only to policy documents authored in this one scope; they do not govern non-policy artifacts (skills, articles, plans, research).

#### 19-local-must-be-structured

All local meta-policy files (`NNN-core.md` and `NNN-core-{qualifier}.md`) MUST follow the structured format defined in `_core-adr-policy-008` (see rule 11). Tools MUST enforce this and report an error using code `_core-adr-policy-010-scope-governance.19-local-must-be-structured`.

#### 20-local-mandatory-when-present

When one or more local meta-policies exist in a scope, tools and agents MUST load and apply ALL of them as mandatory conventions when authoring or reviewing **policy documents** in that scope. If any found local meta-policy file is unreadable, tools MUST halt and report an error before proceeding.

---

**Section C — Governance application and precedence**

#### 21-application-follows

Tools and agents MUST apply the policies of all scopes listed in a scope's `follows:` frontmatter as mandatory conventions, in addition to `_core`. When the same topic is addressed by multiple `follows:` scopes, the last-listed scope MUST take precedence on conflicts.

#### 22-application-scope-type

When adding or reviewing content in a scope, tools and agents MUST:

1. Read the scope's `scope-type` from its `index.md`. Normalise to a list: split on commas and trim whitespace.
2. For each declared type in list order, resolve its full ancestor chain:
   a. Search `[type]/principles/` directories of all `core`-type scopes for the `{scope-type}-scope-type.md` primary file.
   b. If found, load the primary and all companion files (`{scope-type}-scope-type-{qualifier}.md`) from the **same directory**, in alphabetical qualifier order.
   c. If the primary contains a rule titled `NN-parent-scope-type`, extract the parent type name and repeat steps a–c. Detect and stop on cycles.
3. Concatenate all resolved ancestor chains in declaration order to form a flat list (e.g., `scope-type: [reference, platform]` where `reference → standard`, `platform → core`: `[standard, reference, core, platform]`).
4. Deduplicate keeping the **first occurrence** of each type.
5. Apply all policies from the deduplicated list as mandatory conventions. Later entries override earlier entries on same rule number conflicts (see rule 26-conflict-declarations).

#### 23-application-local

When adding or reviewing **policy documents** in a scope, tools and agents MUST:

1. Search the scope's own `[type]/principles/` directories for all files whose filename title starts with `core` (i.e., `NNN-core.md` or `NNN-core-{qualifier}.md`), excluding scope-type definition files whose title ends with `-scope-type`.
2. If any are found, read and apply ALL of them as mandatory conventions. If a found file is unreadable, halt with an error before proceeding.
3. If none are found, continue without error — absence of local meta-policies is valid.

#### 24-precedence

When multiple governance layers define a rule with the same rule number, the later entry in the following ordered chain takes precedence (lowest to highest):

1. All scope-types in the deduplicated ancestor chain (rule 22), in chain order — earlier entries are overridden by later entries.
2. `follows:` scope policies (applied in `follows:` list order; last-listed scope wins among themselves).
3. Local meta-policies (`NNN-core.md` and companions in alphabetical qualifier order).

All of the above are subordinate to `_core` structural rules, which MUST NOT be overridden.

#### 25-ordering-custom-types

Custom-type scopes SHOULD be placed in the `standard` position in the root `index.md` ordering (i.e., after `platform` scopes and before `_local`).

#### 26-conflict-declarations

When a policy (scope-type definition, local meta-policy, or companion) overrides a rule defined by a lower-precedence policy in the governance chain, the overriding policy MUST include a `## Conflicts` section that declares:

- The rule number and short identifier being overridden (e.g., `#### NN-rulename`).
- The policy file where the original rule is defined.
- A short explanation of why the override is required for this scope or type.

A `## Conflicts` section MAY also document cross-scope-type incompatibilities for informational purposes. Tools and agents MUST detect undeclared conflicts at review time and surface them as errors. Semantic conflict detection is the responsibility of the authoring agent, not the lint tool.

## References

- [_core-adr-policy-011 - core scope type](011-core-scope-type.md) — defines the `core` scope type and when to use a `-core` sibling scope vs. a scope-local policy
- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md) — scope structure, `follows:` and `extends:` field definitions, scope index frontmatter fields

---

**Section D — Scope extends**

#### 27-extends-declaration

A scope MAY declare an `extends:` field in its `index.md` YAML frontmatter. The value MUST be a single scope name or a comma-separated list (YAML list format also valid). The field causes all **policy documents** (decision records only — skills, articles, research, and plans are NOT inherited) from the listed scopes to be treated as if authored in the extending scope. Valid for all scope types.

#### 28-extends-disjoint

The `extends:` field and the `follows:` field MUST reference disjoint sets of scope names. The same scope MUST NOT appear in both fields. Tools MUST enforce this and report an error using code `_core-adr-policy-010.28-extends-disjoint`.

#### 29-extends-reserved-scopes

A scope `extends:` declaration MUST NOT reference the reserved scope names `_local` or `_core` by name. `_local` is workspace-only and non-distributable; `_core` policies are always applied implicitly to every scope and extending them would be redundant. Tools MUST enforce this and report an error using code `_core-adr-policy-010.29-extends-reserved-scopes`.

#### 30-extends-no-self

A scope `extends:` declaration MUST NOT reference the declaring scope itself. Tools MUST enforce this and report an error using code `_core-adr-policy-010.30-extends-no-self`.

#### 31-extends-no-cycle

`extends:` declarations MUST NOT form circular chains (e.g., scope A extends B, B extends A). Tools MUST detect such cycles across the full workspace and report an error using code `_core-adr-policy-010.31-extends-no-cycle`, identifying the cycle.

#### 32-extends-mandatory-presence

Every scope listed in a scope's `extends:` field MUST exist in the workspace with an accessible `index.md`. If any referenced scope is absent or its `index.md` cannot be read, all READ, WRITE, and REVIEW operations on the extending scope MUST fail immediately. Tools MUST surface a clear message naming the missing scope and citing code `_core-adr-policy-010.32-extends-mandatory-presence`.

#### 33-extends-content-precedence

When loading the effective policy set for a scope, tools and agents MUST resolve the full `extends:` chain depth-first and apply the following content precedence (lowest to highest):

1. Transitively extended scopes, in depth-first order, deduplicated keeping first occurrence. For A extends [B, C] where B itself extends [D]: resolved order is D < B < C.
2. The extending scope's own policy documents (always take highest precedence and override all inherited policies).

Deduplication: if the same scope name appears more than once in the depth-first traversal, keep only the first occurrence. When a scope's policy overrides an inherited policy on the same topic, the overriding policy MUST include a `## Conflicts` section (see rule 34).

Note: the `extends:` content-precedence chain is independent of Section C rule 24. `extends:` determines which policy documents are in scope; rule 24 determines which authoring rules apply.

#### 34-extends-conflict-declaration

When an extending scope's own policy addresses the same topic as a policy in an extended scope, or when two extended scopes address the same topic differently, the higher-precedence policy MUST include a `## Conflicts` section that:

- Names the conflicting policy (scope and policy ID) being overridden or superseded.
- Explains why the override or difference exists.

An undeclared semantic conflict between policies from the `extends:` chain MUST be surfaced as an error during review (see `_core-adr-policy-010.34-extends-conflict-declaration`).

#### 35-extends-index

Scopes referenced only via `extends:` chains and not linked in the root `index.md` are **exempt** from the "root index must link all scopes" requirement. These scopes form the building-block layer; the root index lists only entry scopes. If a scope is both referenced via `extends:` AND linked in the root index, tools SHOULD warn of ambiguous dual precedence (the root index ordering governs for consumers that do not interpret `extends:` declarations), using warning code `_core-adr-policy-010.35-extends-index`.
