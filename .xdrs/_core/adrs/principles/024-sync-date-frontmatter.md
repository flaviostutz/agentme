---
name: _core-adr-policy-024-sync-date-frontmatter
description: Defines the optional `sync-date` frontmatter field that records when an XDRS element was last verified, checked, reconciled or aligned with other entities, internal or external. Use when a document depends on information that degrades over time, when adding or updating `sync-date`, or when a mechanism needs a refresh hint.
apply-to: All XDRS elements (Policies, skills, articles, research, initiatives, scope indexes) and every tool, skill or agent that syncs them
valid-from: 2026-11-04
---

# _core-adr-policy-024: Sync date frontmatter

## Context and Problem Statement

Some XDRS elements hold content whose quality degrades over time unless it is periodically checked against other entities: other scopes, external sources, APIs, URLs, scripts or people. Version control records when a file changed, but not when its content was last verified, nor that a verification ended with a decision to change nothing.

How should an element declare when it was last checked or reconciled, so that humans, tools and agents can decide when a refresh is worth doing?

## Decision Outcome

**An optional, opt-in `sync-date` frontmatter field holding the date of the last sync**

The field is a refresh hint. It is not a status, not a change date, and carries no enforcement semantics.

### Details

#### 01-sync-date-meaning

`sync-date` MUST contain the ISO date (`YYYY-MM-DD`) on which the element content was last verified, checked, reconciled or aligned with one or more other entities. The other entity MAY be internal (another scope, element or review) or external (an API, URL, repository, script, skill or person). A sync that ended with no change, or with a deliberate decision to change nothing, still counts and MUST update the date.

#### 02-not-a-change-date

`sync-date` MUST NOT be used as a last-modified date or to record content changes, which are already available from version control. It MUST NOT be updated when the content was edited without any verification against another entity.

#### 03-opt-in

`sync-date` is OPTIONAL and MUST NOT be added by default. It MUST be added only when a compiled scope requires it (rule 07), or when the user or a skill explicitly requests it for a specific sync purpose.

#### 04-purpose-check

Before adding `sync-date`, the author or agent MUST identify the concrete sync process that will use it (for example a periodic review, a source re-sync, or a cross-scope reconciliation). When no such process exists, the field MUST NOT be added. An existing `sync-date` that no process uses SHOULD be removed.

#### 05-placement-and-format

The value MUST be an unquoted ISO date. Placement per element:

| Element | Placement |
|---|---|
| Policy, scope `index.md` | Top-level frontmatter field `sync-date` |
| Article, research, initiative | Top-level `sync-date` in an optional frontmatter block placed before the title line; the block MUST contain no other field |
| Skill (`SKILL.md`) | Nested field `metadata.sync-date`, keeping the top-level frontmatter compatible with the agentskills spec |

Slide presentations MUST NOT carry `sync-date`.

Example:

```yaml
---
sync-date: 2026-11-04
---
```

#### 06-who-updates

The date MUST be updated by whoever performs the sync (human, tool or agent), only after the sync completed. A failed or partial sync MUST NOT update it.

#### 07-compiled-scopes

In a scope declaring `scope-type: compiled`, `sync-date` MUST be present only in the scope `index.md`, never in individual Policies. Compilation tools and agents MUST set it to the current date at the end of every completed compilation or re-sync cycle, including cycles where no source content changed and no Policy was modified. It MUST NOT be updated when the cycle was skipped because every source was still within its re-sync period. Placing it only in the scope index avoids touching every Policy when nothing changed.

#### 08-consumers

Mechanisms that refresh or check content (compilation, reviews, scheduled syncs, scripts) SHOULD read `sync-date` as a hint to prioritize or skip refreshes, and MUST NOT treat a missing `sync-date` as an error. How old a date must be before a refresh is worthwhile is decided by each mechanism.

## References

- [_core-adr-policy-002 - Policy standards](002-policy-standards.md) - Policy frontmatter fields
- [_core-adr-policy-003 - Skill standards](003-skill-standards.md) - SKILL.md frontmatter and metadata
- [_core-adr-policy-019 - Compiled scope type](019-compiled-scope-type.md) - Compilation and re-sync process
