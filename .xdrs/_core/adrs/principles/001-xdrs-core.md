---
name: _core-adr-001-xdrs-core
description: Defines the core XDR framework including types (ADR, BDR, EDR), folder structure, scopes, subjects, and index requirements. Use when structuring or navigating decision records.
---

# _core-adr-001: XDRs core

## Context and Problem Statement

We need a consistent way to capture decisions that scales across scopes and subjects, remains easy to navigate, and works well with AI agents.

How should XDRs be structured and organized across types, teams, and scopes?

## Decision Outcome

**Scoped + typed + subject folders**

Provides clear ownership by scope, predictable navigation, and reusable decisions that work well with AI agents by keeping files small and focused.

### Details

Decision Records can be of different kinds, depending on the nature of the decision:
- BDR (Business Decision Record): Captures business process, product features, procedures and strategic decisions. Examples: business rules, product policies, customer service, business workflow, control frameworks for regulators for finance, product procedures and manuals, KYC requirements, business requirements in general
- ADR (Architectural Decision Record): Wider architectural and technical decisions. Examples: how big topics relate to each other, system contexts, overview without realy deciding on details, integration patterns, overarching topics, corporate wide practices, corporate systems, external and internal partners etc
- EDR (Engineering Decision Record): captures engineering details about how to implement things. Examples: specific tools and libraries selection, framework usage, best practices on coding, testing, quality, project structure, pipelines etc

Collectively, these are referred to as XDRs.

#### General framework standards

- The main document type in the collection of XDRs is the XDR document, which contains a decision. Other documents are normally related to this decision and shouldn't go against its contents.
- All documents in the framework should be removed when they are no longer necessary. The latest version of the collection always represents the active set of documents. Historical versions are available via versioned packages or git history. There is no status field on documents; if a document is present, it is considered active and valid. This keeps the document base clean and avoids confusion about which documents are current. REJECT any indication in the Decisions that contradicts this rule to avoid confusion and complexity.
- Make it clear if an instruction is mandatory or advisory.
  - Mandatory language: "must", "always", "never", "required", "mandatory"
  - Advisory language: "should", "recommended", "advised", "preferably", "possibly", "optionally"
- The XDR root folder is the folder that contains the root `index.md`. The default root folder name is `.xdrs/`. Any folder name is valid as long as it contains an `index.md`. When `.xdrs/` is used, tools and agents discover it automatically by looking for `.xdrs/index.md` relative to the workspace root. When a different folder name is used, it must be passed explicitly to tools (e.g., `xdrs-core lint my-decisions/`).
- ALWAYS use the following folder structure for XDR documents:
  `[xdrs-root]/[scope]/[type]/[subject]/[number]-[short-title].md`
  where `[xdrs-root]` is the XDR root folder (default: `.xdrs/`).
- ALWAYS ignore symlinks paths. NEVER create or update documents inside symlinked folders.
- **Files listed in `.filedist` are external XDRs.** A file whose path appears in the workspace root `.filedist` file was distributed from an external source repository. It must NEVER be modified locally. To change it, submit the change to the source repository and re-extract the updated package. The `.filedist` format is one entry per line: `<relative-path>|<package>|<version>`. A scope is considered external when any of its files appear in `.filedist`, and tools (such as `xdrs-core lint`) will skip external scopes by default. The `.filedist` file can also be used to detect which files changed when bumping an external scope to a newer version: compare the version field in `.filedist` entries before and after the upgrade and diff the affected paths to understand what decisions were added, updated, or removed.
- Optional supporting artifacts under the same subject:
  - `[xdrs-root]/[scope]/[type]/[subject]/researches/[number]-[short-title].md`
  - `[xdrs-root]/[scope]/[type]/[subject]/skills/[number]-[skill-name]/SKILL.md`
  - `[xdrs-root]/[scope]/[type]/[subject]/articles/[number]-[short-title].md`
  - `[xdrs-root]/[scope]/[type]/[subject]/plans/[number]-[short-title].md`
- Research, skills, and articles are part of the framework, but each has its own concept-specific standards in dedicated XDRs. This XDR defines the shared framework baseline; `_core-adr-002` defines the XDR document writing standard.
  - `_core-adr-002` defines XDR standards (document writing)
  - `_core-adr-003` defines skill standards
  - `_core-adr-004` defines article standards
  - `_core-adr-006` defines research standards
  - `_core-adr-007` defines plan standards
- For simple structures, flows, layout, or relationship indications, documents SHOULD prefer plain Markdown, tables, Mermaid.js (sequence, state, activity, entity diagrams) or ASCII art instead of external assets.
- Images and other supporting files SHOULD be used only when they are materially necessary to preserve clarity, fidelity, or evidence. When used, they MUST live in a sibling `.assets/` folder next to the document.
  - XDRs in the subject root use `[xdrs-root]/[scope]/[type]/[subject]/.assets/`
  - Articles use `[xdrs-root]/[scope]/[type]/[subject]/articles/.assets/`
  - Research uses `[xdrs-root]/[scope]/[type]/[subject]/researches/.assets/`
  - Skills use `[xdrs-root]/[scope]/[type]/[subject]/skills/[number]-[skill-name]/.assets/`
- **Scopes:** 
  - Short name that defines a group or a package of xdrs
  - examples: `business-x`, `business-y`, `team-43`, `_core`
  - `_local` is a reserved scope for XDRs created locally to a specific project or repository. XDRs in `_local` must not be shared with or propagated to other contexts. This scope must always be placed in the lowest position in the root `index.md` so that its decisions override or extend any decisions from all higher-positioned scopes. Shared root `index.md` files MUST NOT link `_local` canonical type indexes because `_local` stays workspace-local and is not distributed with shared packages. Readers, tools, and agents SHOULD still try to discover existing workspace-local `_local` canonical indexes by default, even when the shared root index does not link them. Documents in non-`_local` scopes MUST NEVER link to any document inside the `_local` scope, because `_local` is workspace-only and such links would break in any consumer workspace. Documents inside `_local` MAY link to other documents inside `_local`.
  - **Types:** `adrs`, `bdrs`, `edrs`
  - there can exist sufixes to the standard scope names (e.g: `business-x-mobileapp`, `business-y-servicedesk`)
- **Subjects:** MUST be one of the following depending on the type of the XDR. Use the subject to indicate the main concern of the decision.
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
- Never use emojis
- **Links:** Use relative paths for all links; never use absolute paths starting with `/`.
- **Indexes**
  - Every document in the collection (XDRs, skills, articles, research, and plans) must be reachable through the index chain: root index → scope index → type index → document. A document that exists on disk but is not linked from its canonical type index is considered an orphan and must be added to the index or removed.
  - Keep a canonical type index with all documents of a certain type+scope in `[xdrs-root]/[scope]/[type]/index.md`. The type index must link to every XDR, skill, article, research, and plan under that type+scope.
  - Canonical index requirements:
    - Organize XDR documents by subject for easier navigation
    - Add a short description of what this scope is about (responsibilities, general worries, teams involved, link to discussion process, etc)
    - Add a list of other scope indexes that this scope might be related to (only add scopes that might be overridden). E.g: "business-x-mobileapp" scope could refer to "business-x" and "sensitive-data" scopes in its index list. XDRs in scopes listed last override XDRs in scopes listed first when addressing the same topic.
    - Each XDR element entry in the index MUST include a short description of its content, preferably with an imperative statement or the question it answers, when possible (<15 words). Example: "Use this while planning a new feature", "What communication tone we use with our customers?", "PNPM vs Yarn comparison study"
  - Outside the scopes, keep a root index in `[xdrs-root]/index.md` that links to each scope index (`[xdrs-root]/[scope]/index.md`). Add the text "XDRs in scopes listed last override the ones listed first". The root index must not link directly to type indexes; readers navigate from the scope index to the type indexes. Use the link text pattern `View scope [scope_name]` for each scope link (e.g. `[View scope myteam] linking to (myteam/index.md)`).
  - Always verify if indexes are up to date after making changes
- **Scope index**
  - Each scope folder must maintain an `index.md` file at `[xdrs-root]/[scope]/index.md`.
  - The scope index is a short article (under 1000 words) that provides an overview of all XDR contents within that scope. Follow article standards (`_core-adr-004`) when writing this file.
  - The audience for the scope index are engineers, architects, or business analysts who want to check if the scope's contents are useful for them before diving into the specific documents. Write a guided summary that helps them decide whether to explore further.
  - Focus on the most relevant content of the scope: what decisions are covered, what problems they address, and how the scope relates to other scopes.
  - At the end of the scope index, always add links to the canonical type indexes (`adrs/index.md`, `bdrs/index.md`, `edrs/index.md`) that exist within the scope.
  - Whenever the contents of a scope change (new XDRs, skills, articles, research, or plans are added, updated, or removed), evaluate whether the scope index should be updated to reflect the newer contents.

**Folder structure examples** (using the default `.xdrs/` root):
- `.xdrs/business-x/edrs/devops/003-required-development-workflow.md`
- `.xdrs/business-x/adrs/controls/010-security-and-secrets-management.md`
- `.xdrs/_core/edrs/devops/001-multi-repo.md`

```text
subject/
|-- 001-xdr.md
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

- [_core-adr-002 - XDR standards](002-xdr-standards.md) - Standards for writing individual XDR decision documents
- [001-lint skill](skills/001-lint/SKILL.md) - Skill for reviewing code changes against XDRs
- [002-write-xdr skill](skills/002-write-xdr/SKILL.md) - Skill for creating a new XDR following this standard
- [_core-adr-003 - Skill standards](003-skill-standards.md)
- [_core-adr-004 - Article standards](004-article-standards.md)
- [_core-adr-006 - Research standards](006-research-standards.md)
- [_core-adr-007 - Plan standards](007-plan-standards.md)
