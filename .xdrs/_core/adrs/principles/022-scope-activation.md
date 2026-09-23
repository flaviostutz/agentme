---
name: _core-adr-policy-022-scope-activation
description: Defines how installed scopes are listed in the root index, how consumers activate, narrow, or disable them with activation tags, and when a scope becomes read-only because a dependency is missing, disabled, or invalid.
apply-to: All XDRS workspaces, scope authors, consumers, tools, and agents
valid-from: 2026-07-20
---

# _core-adr-policy-022: Scope activation

## Context and Problem Statement

Packages install scope folders into a workspace, but nothing guaranteed that every installed scope was listed in the root `index.md`. Scopes that were meant to be reused only through `extends:` were hidden from the root index, so agents could not discover them, and consumers had no way to switch off a scope they installed but did not want to apply. When a scope depended on another scope that was absent, the result was either a hard lint error or silent misbehaviour.

How does a consumer control which installed scopes apply globally, which apply only through `extends:`, and which are ignored, while keeping every scope discoverable?

## Decision Outcome

**Every installed scope is listed once in the root index; the consumer controls activation with an inline activation tag next to the scope link, and the scope author declares intent with an `extends-only` frontmatter field that lint checks for coherence.**

Policies of listed scopes apply globally by default. An activation tag narrows a scope to `extends-only` or turns it off with `disabled`. Agents rely only on the tags. Scopes whose dependencies are missing, disabled, or invalid become read-only.

### Details

#### 01-root-index-completeness

Every scope folder under the XDRS root that contains an `index.md`, including scopes installed from external packages, MUST be linked exactly once from the root `index.md`. The `_local` scope MUST NOT be linked (see `_core-adr-policy-001`). A scope folder with no link, or a scope linked more than once, is a lint error. Links that resolve to the same scope index (e.g. `./x/index.md` and `x/index.md`) count as the same link. Links inside fenced code blocks are ignored.

#### 02-global-applicability

Policies of a listed scope without an activation tag MUST be applied globally, narrowed by the scope `apply-to` and each policy `apply-to`. Meta-policies (local meta-policies, scope-type definition policies) and all content of core-type scopes are never applied globally; they govern authoring only (see `_core-adr-policy-010` Sections B and C). `_core` always applies globally.

#### 03-activation-tag-syntax

An activation tag is an inline code span placed immediately after a scope link on the same line, optionally separated by spaces or tabs, for example a link to `payments-ref/index.md` followed by `` `extends-only` ``. Allowed values are `extends-only` and `disabled`, lowercase only. A scope link line MUST NOT contain any other inline code: an unknown value, a second tag, or inline code placed elsewhere on the line is a lint error. A tag on the next line is not a tag. `_core` MUST NOT be tagged.

#### 04-extends-only

Policies of a scope tagged `extends-only` MUST be applied only through the `extends:` chain of an active scope (untagged, including read-only scopes, or `_local`). Reach is transitive: if A extends B and B extends C, both B and C apply to A. The root index position of a tagged scope never matters for conflict resolution; `extends:` precedence applies (see `_core-adr-policy-010.33-extends-content-precedence`). Skills, articles, research, and initiatives of the scope remain usable. Tools SHOULD warn when no active scope reaches an `extends-only` scope; reach only through a `disabled` scope does not count.

#### 05-disabled

All content of a scope tagged `disabled` MUST be ignored by agents: its policies, skills, articles, research, and initiatives are not applied, and nothing is inherited from it through `extends:` or `follows:`. The scope is still linted and MAY be edited. Skills of a disabled scope that are symlinked into `.agents/skills` (see `_core-adr-policy-018`) stay loaded by tools and MUST be removed by the consumer.

#### 06-read-only-dependencies

A scope MUST be treated as READ-ONLY when a scope it follows or extends, or the scope that defines one of its scope types (including parent types), is missing, disabled, or invalid, or when it is an external scope and its own `index.md` is invalid. Content in a READ-ONLY scope MUST NOT be added, changed, or removed. For local scopes, missing dependencies and invalid indexes remain lint errors (see `_core-adr-policy-010.32-extends-mandatory-presence`); a disabled dependency only makes the scope read-only. Tools MUST report each cause and how to fix it, citing this rule.

#### 07-extends-only-field

A scope author MAY declare `extends-only: true` or `extends-only: false` in the scope index frontmatter. Only unquoted lowercase `true` and `false` are valid. An invalid value is a lint error in a local scope; in an external scope it makes the scope read-only and the value is treated as absent. `extends-only` (field `true` or tag) on `_core`, `_local`, or a core-type scope is a lint error. Coherence: when the field is `true`, the root index link MUST carry the tag `extends-only` or `disabled`; when the field is `false` or absent, the consumer MAY add either tag (narrowing), and MUST NOT widen a scope beyond what the author declared. The field is a lint aid only.

#### 08-agent-resolution

Agents MUST decide activation only from the root index tags, never from the `extends-only` field:

1. Skip scopes tagged `disabled`.
2. Apply scopes tagged `extends-only` only through the `extends:` chain of an active scope.
3. Apply all other listed scopes per rule 02.
4. Never edit READ-ONLY scopes (rule 06).

#### 09-root-index-ownership

The root `index.md` is owned by the consumer. Packages that ship a root index SHOULD install it without overwriting an existing file, so activation tags survive reinstalls. When any activation tag is used, the root index MUST contain this exact legend line: "Scopes tagged `disabled` MUST be ignored; `extends-only` scopes apply only via extends (see _core-adr-policy-022)".

## References

- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md) — root index and scope index frontmatter
- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) — `extends:` (Section D) and root index ordering (Section E)
- [_core-adr-policy-011 - core scope type](011-core-scope-type.md) — core-type scopes and read-only companions
