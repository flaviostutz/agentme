# _core ADRs Index

Decisions about how the XDRS framework itself works: structure, standards, document types, versioning, and supporting artifacts. Owned by the platform team. Propose changes via pull request.

## Principles

Foundational standards, principles, and guidelines.

- [_core-adr-policy-001](principles/001-xdrs-core.md) - **XDRS core** — Types, scopes, subjects, folder structure, and indexes for the XDRS framework
- [_core-adr-policy-002](principles/002-policy-standards.md) - **Policy standards** — How to write individual Policy documents: template, metadata, ID, lifecycle rules
- [_core-adr-policy-003](principles/003-skill-standards.md) - **Skill standards** — How to author and organize reusable skill packages within XDRS projects
- [_core-adr-policy-004](principles/004-article-standards.md) - **Article standards** — How to write synthetic views combining Policies, research, and skills
- [_core-adr-policy-005](principles/005-semantic-versioning-for-xdrs-packages.md) - **Semantic versioning for XDRS packages** — How to version XDRS packages to communicate upgrade impact
- [_core-adr-policy-006](principles/006-research-standards.md) - **Research standards** — How to structure research documents backing Policy decisions
- [_core-adr-policy-007](principles/007-plan-standards.md) - **Plan standards** — How to structure ephemeral execution plans that implement decisions
- [_core-adr-policy-008](principles/008-policy-structured-standards.md) - **Policy structured standards** — How to expose individually referenceable numbered rules inside a Policy when external citation by identifier is required
- [_core-adr-policy-009](principles/009-presentation-standards.md) - **Presentation standards** — How to structure Marp slide presentations that support XDRS documents
- [_core-adr-policy-010](principles/010-scope-governance.md) - **Scope governance** — How to define custom scope types, scope-local standards, and how all governance mechanisms apply with their precedence chain
- [_core-adr-policy-011](principles/011-core-scope-type.md) - **core scope type** — Defines the `core` scope type: meta-governance scopes that hold writing standards, templates, and process guidance for a domain
- [_core-adr-policy-012](principles/012-reference-scope-type.md) - **reference scope type** — Defines the `reference` scope type: blueprints and standards meant to be copied or adapted
- [_core-adr-policy-013](principles/013-platform-scope-type.md) - **platform scope type** — Defines the `platform` scope type: live services or operational areas consumable directly
- [_core-adr-policy-014](principles/014-standard-scope-type.md) - **standard scope type** — Defines the `standard` scope type: the default for business areas, products, and teams
- [_core-adr-policy-015](principles/015-local-scope-type.md) - **_local scope type** — Defines the `_local` scope type: reserved for workspace-local decisions that must never be distributed
- [_core-adr-policy-016](principles/016-policy-subjects.md) - **Policy Subjects** — Allowed subjects per type (ADR/BDR/EDR), descriptions, examples, and disambiguation tiebreakers
- [_core-adr-policy-017](principles/017-policy-numbering-ranges.md) - **Policy numbering ranges** — Subject-based 100-number block ranges for policy numbering and the freeze-reference exemption
- [_core-adr-policy-018](principles/018-external-path-symlinks.md) - **External path symlinks** — How to make XDRS files accessible from paths outside the .xdrs/ root using symlinks

## Skills

Step-by-step procedural guides for humans and AI agents.

- [001-review](principles/skills/001-review/SKILL.md) - **Review** — review code and files against Policies
- [002-write-policy](principles/skills/002-write-policy/SKILL.md) - **Write Policy** — create a new Policy document
- [003-write-skill](principles/skills/003-write-skill/SKILL.md) - **Write Skill** — create a new skill package
- [004-write-article](principles/skills/004-write-article/SKILL.md) - **Write Article** — create a new article document
- [005-write-research](principles/skills/005-write-research/SKILL.md) - **Write Research** — create a new research document
- [006-write-plan](principles/skills/006-write-plan/SKILL.md) - **Write Plan** — create a new plan document
- [007-write-presentation](principles/skills/007-write-presentation/SKILL.md) - **Write Presentation** — create Marp slide presentations for XDRS documents
- [008-write-xdrs-doc](principles/skills/008-write-xdrs-doc/SKILL.md) - **Write XDRS Doc** — router skill; infers document type and delegates to the appropriate authoring skill

## Articles

Synthetic views combining Policies, Research, and Skills around a specific topic.

- [_core-adr-article-001](principles/articles/001-xdrs-overview.md) - **XDRS Overview** (objective, structure, getting started, guidelines, extension, usage)
