# _core-article-001: XDRs Overview

## Overview

This article introduces XDRs (Decision Records), explains their purpose and design, and guides
teams through adopting, extending, and distributing them. It is an entry point for anyone new to
the framework and links out to the authoritative Decision Records for full details.

## Content

### What are XDRs?

XDRs are structured Markdown documents that capture decisions made by teams. Three types exist:

- **ADR (Architectural Decision Record)** — architectural and technical decisions: system context,
  integration patterns, overarching corporate practices.
- **BDR (Business Decision Record)** — business process, product strategy, compliance, and
  operational decisions.
- **EDR (Engineering Decision Record)** — engineering implementation details: library choices,
  tooling standards, coding practices.

Collectively they are called XDRs. See [_core-adr-001](../001-xdr-standards.md) for the full
definition and mandatory template.

### Objective

As organizations grow, decisions accumulate across teams and domains. Without a consistent
structure, AI agents cannot reliably locate the right decision for a given context, and humans
struggle to maintain hundreds of documents. XDRs solve both problems by defining:

- A predictable folder hierarchy that any agent can navigate.
- Small, focused files (target under 100 lines) that are fast for LLMs to read.
- Scope and subject grouping that limits the search space.
- A root index as a single discovery entry point.

### How it works

Every XDR lives at a fixed path:

```
.xdrs/[scope]/[type]/[subject]/[number]-[short-title].md
```

**Scopes** represent ownership domains (e.g. `_core`, `business-x`, `team-43`). `_local` is
reserved for project-specific decisions that must not be shared externally; it always sits last
in `.xdrs/index.md` so its decisions override all others.

**Types** are `adrs`, `bdrs`, or `edrs`.

**Subjects** constrain the domain further (e.g. `principles`, `application`, `devops`, `finance`).
See [_core-adr-001](../001-xdr-standards.md) for the full allowed subject list per type.

**IDs** follow the pattern `[scope]-[type abbrev]-[number]`, e.g. `_core-adr-001`. Numbers are
never reused. Gaps in the sequence indicate deleted records.

Each scope+type has a canonical `index.md` that lists all XDRs with short descriptions. A root
`.xdrs/index.md` points to all canonical indexes and defines scope precedence (later scopes
override earlier ones).

Skills — step-by-step procedural instructions for humans and AI agents — live in `[subject]/skills/` sub-directories and are
distributed alongside the XDRs they implement. A skill may start as a human-only procedure and evolve toward partial or full
AI automation over time, without needing to be restructured. See [_core-adr-003](../003-skill-standards.md).

Articles — like this document — are synthetic views that combine XDRs and Skills for a specific
topic. They never replace the Decision Records as source of truth. See
[_core-adr-004](../004-article-standards.md).

### Why it is implemented this way

Key design choices and their rationale:

- **Scoped folders over a flat list** — flat lists become unmanageable at scale; scopes give
  clear ownership and allow selective adoption.
- **Small focused files** — LLMs have limited context windows; small files make token budgets
  predictable and keep decisions unambiguous.
- **Canonical indexes** — agents read the index first to narrow the set of relevant files, rather
  than scanning every document.
- **npm distribution** — versioned packages let teams adopt specific decision sets at a specific
  version without being forced to take all changes at once.
- **Skills co-located with XDRs** — keeping procedural guidance next to the decisions it
  implements reduces drift and makes discovery straightforward for humans and agents alike.
  Because skills span a spectrum from fully manual to fully automated, co-location also
  makes it easy to see when a human procedure is ready to be promoted to an agent workflow.

### Getting started

1. Create or open a project workspace.
2. Run `npx xdrs-core` in the workspace root. This installs:
   - `AGENTS.md` — instructs AI agents to always consult XDRs.
   - `AGENTS.local.md` — project-specific agent instructions (editable).
   - `.xdrs/index.md` — root index (editable, `keepExisting` mode).
   - `_core` XDRs and skills under `.xdrs/_core/`.
3. Start a conversation with your AI agent:
   > Create an ADR about our decision to use Python for AI projects.

### Guidelines

Follow [_core-adr-001](../001-xdr-standards.md) strictly. Key rules:

- Use **mandatory language** (`must`, `never`, `required`) for non-negotiable rules and
  **advisory language** (`should`, `recommended`) for guidance.
- Keep XDRs under 100 lines. Move procedural detail to a co-located Skill.
- Always update the scope+type index and the root index after adding or changing an XDR.
- Use `_local` scope when a decision is project-specific and must not be shared.
- Never reuse a number once it has been assigned, even if the XDR is deleted.

### How to extend

- **New scope** — create `.xdrs/[scope]/[type]/index.md` and add it to `.xdrs/index.md`.
- **New subject** — create the subject folder under the existing scope+type path. Add an
  allowed subject or use `principles` if none fits (propose a new subject via a `_core` ADR).
- **New skill** — add a `skills/[number]-[skill-name]/SKILL.md` inside the relevant subject
  folder, following [_core-adr-003](../003-skill-standards.md).
- **New article** — add an `articles/[number]-[short-title].md` inside the relevant subject
  folder, following [_core-adr-004](../004-article-standards.md).

### Using XDRs in your own project

1. **Install** — add the scope package as a dependency and run `npx xdrs-core extract` (or
   `pnpm exec xdrs-core extract`) to unpack XDR files into `.xdrs/` in your workspace.
2. **Pins and upgrades** — update the npm dependency version to pull in the latest decisions
   for a scope. The `filedist` mechanism tracks managed files in `.filedist` and keeps
   `AGENTS.local.md` and `.xdrs/index.md` in `keepExisting` mode so local edits are preserved.
3. **Multi-scope** — list multiple scope packages as dependencies. Edit `.xdrs/index.md` to
   add each scope's canonical index link; place more specific scopes below broader ones.
4. **Verify** — run `npx xdrs-core check` to confirm all managed files are in sync with the
   installed packages.
5. **Distribute your own scope** — pack `.xdrs/[scope]/` with `pnpm pack` and publish to an
   npm registry (public or internal). Pin a tag for prerelease versions.

## References

- [_core-adr-001](../001-xdr-standards.md) - XDR standards and mandatory template
- [_core-adr-003](../003-skill-standards.md) - Skill standards and co-location rules
- [_core-adr-004](../004-article-standards.md) - Article standards
- [001-lint skill](../skills/001-lint/SKILL.md) - Linting code against XDRs
- [002-write-xdr skill](../skills/002-write-xdr/SKILL.md) - Writing a new XDR
- [003-write-skill skill](../skills/003-write-skill/SKILL.md) - Writing a new skill
