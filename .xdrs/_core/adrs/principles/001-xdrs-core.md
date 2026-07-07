---
name: _core-adr-policy-001-xdrs-core
description: Defines the core XDRS framework including types (ADR, BDR, EDR), folder structure, scopes, subjects, and index requirements. Use when structuring or navigating policies.
apply-to: All XDRS scopes and document types
valid-from: 2025-01-01
---

# _core-adr-policy-001: XDRs core

## Context and Problem Statement

We need a consistent way to capture decisions that scales across scopes and subjects, remains easy to navigate, and works well with AI agents.

How should XDRS be structured and organized across types, teams, and scopes?

## Decision Outcome

**Scoped + typed + subject folders**

Provides clear ownership by scope, predictable navigation, and reusable decisions that work well with AI agents by keeping files small and focused.

### Details

A standard Decision Record normally combines several concerns in the same document: a reason (why, options considered), a policy (rules, what is the decision), a plan (consequences, when it will be implemented), a how-to (step-by-step how-to procedure), and a view on a topic. The XDRS framework separates these concerns into different document types: Policies as the source of truth for the core of the decision, Research for reasoning and evidence, Plans for implementation approach, Skills for execution procedures, and Articles for topic overviews. Supporting artifacts MAY explain, justify, or operationalize the policy, but they do not replace it. The compilation process of a raw Decision Record is to distribute it into those different documents and create links between them. You can also use the framework standalone, generating these elements individually directly during the writing process.

Policies can be of different kinds, depending on the nature of the decision:
- BDR (Business Decision Record): Captures business process, product features, procedures and strategic decisions. Examples: business rules, product policies, customer service, business workflow, control frameworks for regulators for finance, product procedures and manuals, KYC requirements, business requirements in general
- ADR (Architectural Decision Record): Wider architectural and technical decisions. Examples: how big topics relate to each other, system contexts, overview without realy deciding on details, integration patterns, overarching topics, corporate wide practices, corporate systems, external and internal partners etc
- EDR (Engineering Decision Record): captures engineering details about how to implement things. Examples: specific tools and libraries selection, framework usage, best practices on coding, testing, quality, project structure, pipelines etc

#### General framework standards

- The main document type in the collection of XDRS is the Policy document, which contains the core of a decision, contraints, rules and what SHOULD be followed. Other documents are normally related to this policy and MUST NOT go against its contents.
- All documents in the framework SHOULD be removed when they are no longer necessary. The latest version of the collection MUST represent the active set of documents. Historical versions are available via versioned packages or git history. There is no status field on documents; if a document is present, it is considered active and valid. This keeps the document base clean and avoids confusion about which documents are current. REJECT any indication in the Decisions that contradicts this rule to avoid confusion and complexity.
- Make it clear if an instruction is mandatory or advisory.
  - Policy documents MUST use BCP 14 (RFC 2119 / RFC 8174) keywords when expressing normative requirements
    - Use **MUST** / **MUST NOT** for absolute requirements or prohibitions.
    - Use **SHOULD** / **SHOULD NOT** for strong recommendations where valid exceptions exist but MUST be justified.
    - Use **MAY** / **OPTIONAL** for truly optional choices.
    - Avoid overusing normative keywords; reserve them for rules that genuinely require unambiguous compliance or optionality.
    - Uppercase statements are ALWAYS enforced.
    - When those words are in lowercase, they have the normal meanings in english, but are not necessarily enforced. Use only when not defining normative statements in a statement. e.g.: "This policy defines when you should use something"
  - Expressions like "must", "always", "never", "required", "mandatory" SHOULD be written in the MUST/MUST NOT format
  - Expressions like: "should", "recommended", "advised", "preferably" SHOULD be written in the SHOULD/SHOULD NOT format
  - Expressions like: "possibly", "optionally" SHOULD be written in MAY/OPTIONAL format
- The XDRS root folder is the folder that contains the root `index.md`. The default root folder name is `.xdrs/`. Any folder name is valid as long as it contains an `index.md`. When `.xdrs/` is used, tools and agents discover it automatically by looking for `.xdrs/index.md` relative to the workspace root. When a different folder name is used, it MUST be passed explicitly to tools (e.g., `xdrs-core lint my-decisions/`).
- MUST use the following folder structure for Policy documents:
  `[xdrs-root]/[scope]/[type]/[subject]/[number]-[short-title].md`
  where `[xdrs-root]` is the XDRS root folder (default: `.xdrs/`).
- MUST ignore symlinks paths. MUST NOT create or update documents inside symlinked folders.
- **Files listed in `.filedist.lock` are external XDRs.** A file whose path appears in the workspace root `.filedist.lock` file was distributed from an external source repository. It MUST NOT be modified locally. To change it, submit the change to the source repository and re-extract the updated package. The `.filedist.lock` format is one entry per line: `<relative-path>|<package>|<version>`. A scope is considered external when any of its files appear in `.filedist.lock`, and tools (such as `xdrs-core lint`) will skip external scopes by default. The `.filedist.lock` file can also be used to detect which files changed when bumping an external scope to a newer version: compare the version field in `.filedist.lock` entries before and after the upgrade and diff the affected paths to understand what decisions were added, updated, or removed.
- Optional supporting artifacts under the same subject:
  - `[xdrs-root]/[scope]/[type]/[subject]/researches/[number]-[short-title].md`
  - `[xdrs-root]/[scope]/[type]/[subject]/skills/[number]-[skill-name]/SKILL.md`
  - `[xdrs-root]/[scope]/[type]/[subject]/articles/[number]-[short-title].md`
  - `[xdrs-root]/[scope]/[type]/[subject]/plans/[number]-[short-title].md`
- Research, skills, and articles are part of the framework, but each has its own concept-specific standards in dedicated Policies. This Policy defines the shared framework baseline; `_core-adr-policy-002` defines the Policy document writing standard.
  - `_core-adr-policy-002` defines Policy standards (document writing)
  - `_core-adr-policy-003` defines skill standards
  - `_core-adr-policy-004` defines article standards
  - `_core-adr-policy-006` defines research standards
  - `_core-adr-policy-007` defines plan standards
- For simple structures, flows, layout, or relationship indications, documents SHOULD prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams) or ASCII art instead of external assets.
- Any non-Markdown supporting files referenced by a document (schemas, JSON examples, images, diagrams, binaries, or any other data files) SHOULD be used only when they are materially necessary to preserve clarity, fidelity, or evidence. When used, they MUST live in a sibling `.assets/` folder next to the document.
  - Policies in the subject root use `[xdrs-root]/[scope]/[type]/[subject]/.assets/`
  - Articles use `[xdrs-root]/[scope]/[type]/[subject]/articles/.assets/`
  - Research uses `[xdrs-root]/[scope]/[type]/[subject]/researches/.assets/`
  - Skills use `[xdrs-root]/[scope]/[type]/[subject]/skills/[number]-[skill-name]/.assets/`
- **Scopes:** 
  - Short name that defines a group or a package of XDRS
  - examples: `business-x`, `business-y`, `team-43`, `_core`
  - `_local` is a reserved scope for XDRS elements created locally to a specific project or repository. XDRS elements in `_local` MUST NOT be shared with or propagated to other contexts. This scope MUST be placed in the lowest position in the root `index.md` so that its decisions override or extend any decisions from higher-positioned scopes. Shared root `index.md` files MUST NOT include an explicit link to `_local`, because `_local` remains workspace-local and is not distributed with shared packages. Readers, tools, and agents SHOULD still try the default workspace-local path `_local/index.md` when it exists, even without a root-index link. Documents in non-`_local` scopes MUST NOT link to any document inside `_local`; documents inside `_local` MAY link to other documents inside `_local`.
  - **Types:** `adrs`, `bdrs`, `edrs`
  - there can exist sufixes to the standard scope names (e.g: `business-x-mobileapp`, `business-y-servicedesk`)
  - The `-core` suffix designates a scope as the meta governance layer for a domain. See `_core-adr-policy-011` for the `core` scope type definition.
  - **Scope types:** Every scope MUST declare its type via a `scope-type` field in its `index.md` YAML frontmatter. A `scope-type` value is valid when a `{scope-type}-scope-type` policy exists in the `principles` subject of any `core`-type scope in the workspace. Custom scope-type names MUST NOT start with `_`. The five built-in scope types and their definitions are:
    - `core` — see [`_core-adr-policy-011`](011-core-scope-type.md)
    - `reference` — see [`_core-adr-policy-012`](012-reference-scope-type.md)
    - `platform` — see [`_core-adr-policy-013`](013-platform-scope-type.md)
    - `standard` — see [`_core-adr-policy-014`](014-standard-scope-type.md)
    - `_local` — see [`_core-adr-policy-015`](015-local-scope-type.md)
  - Scope name suffixes are unlimited and MAY be used in any scope type.
  - When writing or generating a new XDRS root `index.md`, use the following default ordering (scopes listed later override earlier ones): `core → reference → platform → standard → _local`. Custom-type scopes SHOULD be placed in the `standard` position.
  - **Scope index frontmatter fields:** Every scope's `index.md` MUST include the following YAML frontmatter. Fields match the Policy frontmatter standard (`_core-adr-policy-002`) in purpose, adjusted for scope-level semantics:
    - `name` (required): The scope identifier, MUST exactly match the scope directory name (e.g., `myteam`, `cloud-platform-aws`). Used by tools to verify scope identity.
    - `description` (required): Short overview of what this scope covers and who the intended audience is. Used by AI agents for discovery and relevance matching. Max 40 words.
    - `scope-type` (required): Scope classification type. MUST match a `{scope-type}-scope-type` policy in any `core`-type scope's `principles/` directory. See `_core-adr-policy-010` for the full governance convention and `_core-adr-policy-011`, `012`–`015` for built-in type definitions.
    - `apply-to` (required): Declares in which contexts — teams, systems, codebases, or environments — the decisions in this scope are relevant. Max 30 words.
    - `valid-from` (required): ISO date (YYYY-MM-DD) from which this scope became active.
    - `metadata` (optional): Arbitrary key-value map for additional scope metadata.
    - `follows` (optional): Core scope names whose Policies apply as mandatory conventions to this scope, beyond `_core`. Last-listed takes precedence on conflicts (e.g., `follows: myarea-core, shared-standards`).
    - `related-scopes` (optional): Scope names of parent, sibling, or child scopes. Use when structural links help verify policy correctness across related scopes.
- **Subjects:** MUST be one of the following depending on the type of the Policy. Use the subject to indicate the main concern of the decision.
  - **ADR subjects**
    - `principles`: Cross-cutting architecture and policy foundations.
      - Examples: architecture style, interoperability rules, long-term technology direction.
    - `application`: System and service design decisions at application level.
      - Examples: modularization strategy, service decomposition, app-level security flows.
    - `data`: Data architecture and information modeling choices.
      - Examples: canonical schemas, data ownership boundaries, retention strategies.
    - `integration`: Decisions about communication between internal/external systems.
      - Examples: sync vs async patterns, contract strategy, partner integration approach.
    - `platform`: Platform-level runtime and enabling capabilities.
      - Examples: cloud/runtime baseline, foundational services, platform tenancy approach.
    - `controls`: Architecture controls for risk, security, and compliance at a high level.
      - Examples: encryption baseline, auditability requirements, policy enforcement points.
    - `operations`: Operational architecture decisions.
      - Examples: incident model, resilience objectives, operational ownership boundaries.
  - **BDR subjects**
    - `principles`: Business principles and decision criteria that guide all business areas.
      - Examples: customer fairness rules, policy precedence, strategic guardrails.
    - `marketing`: Go-to-market, communication, and campaign policy decisions.
      - Examples: campaign approval rules, channel usage standards, positioning constraints.
    - `product`: Product behavior, lifecycle, and offering decisions.
      - Examples: feature rollout policy, packaging/tiers, product requirement governance.
    - `controls`: Business control framework decisions.
      - Examples: approval segregation, mandatory checks, exception handling policy.
    - `operations`: Day-to-day business process and procedure decisions.
      - Examples: support workflows, onboarding/offboarding procedures, SLA operations.
    - `organization`: Structure, roles, and responsibility model decisions.
      - Examples: decision rights, team topology, accountability boundaries.
    - `finance`: Financial and cost-control business decisions.
      - Examples: budgeting process, pricing governance, investment approval rules.
    - `sustainability`: Environmental and social responsibility policy decisions.
      - Examples: sustainability KPIs, reporting cadence, procurement sustainability criteria.
  - **EDR subjects**
    - `principles`: Engineering principles and non-functional quality defaults.
      - Examples: coding standards baseline, testing philosophy, secure-by-default engineering rules.
    - `application`: Code-level implementation patterns and application conventions.
      - Examples: framework patterns, layer organization, API implementation conventions.
    - `infra`: Infrastructure implementation and runtime operations details.
      - Examples: IaC patterns, environment provisioning, network/runtime hardening details.
    - `observability`: Telemetry, monitoring, alerting, and diagnostics implementation.
      - Examples: log/metric/tracing standards, alert routing policy, SLO measurement approach.
    - `devops`: Delivery pipeline, release automation, and developer workflow decisions.
      - Examples: CI/CD stages, branch strategy, release promotion gates.
    - `governance`: Engineering governance, risk controls, and compliance mechanics.
      - Examples: dependency governance, approval policies, mandatory quality checks.
- MUST NOT use emojis
- **Links:** Use relative paths for all links; MUST NOT use absolute paths starting with `/`.
- **Indexes**
  - Every document in the collection (Policies, skills, articles, research, and plans) MUST be reachable through the index chain: root index → scope index → type index → document. A document that exists on disk but is not linked from its canonical type index is considered an orphan and MUST be added to the index or removed.
  - Keep a canonical type index with all documents of a certain type+scope in `[xdrs-root]/[scope]/[type]/index.md`. The type index MUST link to every Policy, skill, article, research, and plan under that type+scope.
  - Canonical index requirements:
    - Organize XDRS documents by subject for easier navigation
    - Add a short description of what this scope is about (responsibilities, general worries, teams involved, link to discussion process, etc)
    - Add links to related scope indexes that this scope might override or be overridden by (scopes listed last override earlier ones on the same topic).
    - Each XDRS element entry MUST include a short description. SHOULD use an imperative statement or the question it answers (<15 words). Example: "Use this while planning a new feature", "What communication tone we use with our customers?"
  - Outside the scopes, keep a root index in `[xdrs-root]/index.md` that links to each scope index (`[xdrs-root]/[scope]/index.md`). Add the text "XDRS scopes listed last override the ones listed first". The root index MUST NOT link directly to type indexes; readers navigate from the scope index to the type indexes. Use the link text pattern `View scope [scope_name]` for each scope link (e.g. `[View scope myteam] linking to (myteam/index.md)`).
  - MUST verify if indexes are up to date after making changes
- **Scope index**
  - Each scope folder MUST maintain an `index.md` file at `[xdrs-root]/[scope]/index.md`.
  - The scope index is a short article (under 1000 words) that provides an overview of all XDRS contents within that scope. Follow article standards (`_core-adr-policy-004`) when writing this file.
  - The audience for the scope index are engineers, architects, or business analysts who want to check if the scope's contents are useful before diving into specific documents. Write a guided summary that helps them decide whether to explore further.
  - Focus on the most relevant content of the scope: what decisions are covered, what problems they address, and how the scope relates to other scopes.
  - At the end of the scope index, MUST add links to the canonical type indexes (`adrs/index.md`, `bdrs/index.md`, `edrs/index.md`) that exist within the scope.
  - Whenever the contents of a scope change (new Policies, skills, articles, research, or plans are added, updated, or removed), evaluate whether the scope index SHOULD be updated to reflect the newer contents.

**Folder structure examples** (using the default `.xdrs/` root):
- `.xdrs/business-x/edrs/devops/003-required-development-workflow.md`
- `.xdrs/business-x/adrs/controls/010-security-and-secrets-management.md`
- `.xdrs/_core/edrs/devops/001-multi-repo.md`

```text
subject/
|-- 001-policy.md
|-- .assets/
|-- articles/
|   |-- 001-article.md
|   `-- .assets/
|-- plans/
|   |-- 001-plan.md
|   `-- .assets/
|-- researches/
|   |-- 001-study.md
|   `-- .assets/
`-- skills/
    `-- 001-task/
        |-- SKILL.md
        `-- .assets/
```

## References

- [_core-adr-policy-002 - Policy standards](002-policy-standards.md) - Standards for writing individual Policy documents
- [_core-adr-policy-010 - Scope governance](010-scope-governance.md) - Scope-type definition convention, scope-local standards, and governance application model
- [_core-adr-policy-011 - core scope type](011-core-scope-type.md) - Defines the `core` scope type and meta-governance scope conventions
- [001-review skill](skills/001-review/SKILL.md) - Skill for reviewing code changes against Policies
- [002-write-policy skill](skills/002-write-policy/SKILL.md) - Skill for creating a new Policy following this standard
- [_core-adr-policy-003 - Skill standards](003-skill-standards.md)
- [_core-adr-policy-004 - Article standards](004-article-standards.md)
- [_core-adr-policy-006 - Research standards](006-research-standards.md)
- [_core-adr-policy-007 - Plan standards](007-plan-standards.md)
