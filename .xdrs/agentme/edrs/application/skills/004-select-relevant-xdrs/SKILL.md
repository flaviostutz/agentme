---
name: 004-select-relevant-xdrs
description: >
   Analyzes a client repository, extracts the full agentme XDR set, and excludes the records that do
   not fit the project's structure and workflow needs. Activate this skill when the user asks to
   choose relevant agentme XDRs automatically, install the right XDR set for an existing project, or
   bootstrap agentme guidance into a repository without manually deciding which records to keep.
metadata:
  author: flaviostutz
  version: "1.0"
compatibility: Node.js 18+
---

## Overview

Installs the full agentme XDR set for a repository through the published CLI, then removes only the
records that clearly do not fit the target project by passing explicit `--exclude` flags during
extraction.

## Instructions

### Phase 1: Discover the available extractable artifacts

1. Discover how the current published package exposes extraction. Prefer the package CLI help,
   installed package metadata, and the agentme README so you know how to invoke:
   - the full XDR extraction path with `extract --all`
   - any optional workflow artifacts
2. Build an explicit inventory of the shipped agentme XDR files so exclusions can be chosen by
   stable path.
3. If the runtime environment cannot enumerate the shipped XDRs directly, fall back to the package
   metadata or repository documentation and continue with that published inventory.
4. If the fallback still cannot identify the shipped XDRs, stop and report that automatic
   selection is blocked because the package does not expose enough metadata in the current
   environment.

### Phase 2: Analyze the current project

1. Inspect the repository root and identify:
   - primary languages (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, etc.)
   - project shape (single package, monorepo, library, application, CLI, service)
   - frameworks and tooling (`next.config.*`, `vite.config.*`, `jest.config.*`, `.mise.toml`,
     `docker-compose.*`, CI workflows, Makefiles)
   - existing agent workflow files (`.xdrs/`, `AGENTS.md`, `.github/agents/`, `.github/prompts/`)
2. Determine whether the repository already has:
   - XDR-driven guidance in `.xdrs/`
   - local conventions that would make a preset redundant or conflicting
3. Summarize the project in a short decision note before selecting exclusions:
   - what the project is
   - which languages and frameworks are present
4. From that analysis, build a candidate list of XDRs that are obviously out of scope for the
   repository. Only include exclusions when the mismatch is concrete, for example:
   - language-specific XDRs for languages not used in the repository
   - monorepo structure guidance for a clear single-package repository
   - service/runtime/deployment guidance for a pure library with no deployed application surface
5. Do not exclude baseline or broadly applicable guidance just because the project is small or
   simple. Exclusions must remove only XDRs that would clearly mislead the repository.

### Phase 3: Select exclusions

1. Start from the full shipped agentme XDR set as the default installation target.
2. Reduce that set only by excluding the XDRs that clearly do not fit the repository. Use
   path-stable identifiers so the extraction command is auditable, for example:
   - `.xdrs/agentme/edrs/application/010-golang-project-tooling.md` for non-Go projects
   - `.xdrs/agentme/edrs/platform/005-monorepo-structure.md` for non-monorepos
   - `.xdrs/agentme/edrs/operations/011-service-health-check-endpoint.md` for projects without
     a long-running service surface
3. If the repository does not want agentme XDRs, stop and explain why instead of forcing an
   installation.
4. State the final decision with:
   - whether full XDR extraction will run
   - the final exclude list with one-line rationale per excluded XDR

### Phase 4: Install the selected presets

1. Build an ordered exclude list for the irrelevant XDRs selected in Phase 3.
2. Run full XDR extraction first, using `--all`, and append one `--exclude` flag per XDR:

   ```sh
   npx -y agentme extract --output . --all --exclude <xdr-path> --exclude <xdr-path>
   ```

3. If the user wants a pinned dependency instead of one-off extraction, prefer:

   ```sh
   pnpm add -D agentme
   pnpm exec agentme extract --output . --all --exclude <xdr-path> --exclude <xdr-path>
   ```

4. After extraction, verify that the expected XDR files now exist:
   - `.xdrs/index.md`, `.xdrs/agentme/`, `AGENTS.md`
5. Also verify that each excluded XDR path is absent from the extracted output.
6. Report whether full XDR extraction ran, which XDRs were excluded with `--exclude`, and the
   paths that were added or updated.

### Phase 5: Handle conflicts and repeat runs

1. If the repository already contains extracted agentme files, treat the operation as an update, not
   a fresh bootstrap.
2. Do not delete unrelated local files to make a preset fit.
3. If extracted files conflict with existing local decisions, tell the user which areas now need a
   local `_local` XDR override or manual merge.
4. When rerunning the skill after repository changes, recompute the exclude list instead of
   reusing stale exclusions from a previous run.
5. When rerunning the skill after repository changes, repeat the analysis instead of assuming the
   previous workflow-artifact decision is still correct.

## Examples

Input: "Install the right agentme XDR presets for this Node.js library"
- Inventory the shipped agentme XDR files
- Analyze the repository and detect a JavaScript library with Makefiles
- Exclude `.xdrs/agentme/edrs/application/010-golang-project-tooling.md` and `.xdrs/agentme/edrs/operations/011-service-health-check-endpoint.md`
- Run `npx -y agentme extract --output . --all --exclude .xdrs/agentme/edrs/application/010-golang-project-tooling.md --exclude .xdrs/agentme/edrs/operations/011-service-health-check-endpoint.md`

Input: "Set up agentme for this repo"
- Inventory the shipped agentme XDR files
- Detect `.xdrs/`, `.github/agents/`, and `.github/prompts/`
- Choose full XDR extraction
- Exclude only the XDRs that are concretely irrelevant for the repository shape
- Run `npx -y agentme extract --output . --all --exclude <irrelevant-xdr-path>`

## Edge Cases

- If the CLI cannot directly list the shipped XDRs, use the package's published metadata or README
   as a fallback instead of failing immediately.
- If the repository already has `.xdrs/`, install or update the XDR set.
- If a candidate exclusion is debatable, keep the XDR. The skill should exclude only records that
   clearly do not make sense for the project.
- If preset extraction would overwrite locally customized agent files, warn the user and describe the
  likely merge points.
- If the repository is a spike or intentionally minimal experiment, still prefer the smallest preset
   set of workflow artifacts and avoid adding scaffolding that the project will not use.

## References

- [agentme README](../../../../../../README.md)
- [agentme-edr-003 - JavaScript project tooling and structure](../../003-javascript-project-tooling.md)
- [agentme-edr-005 - Monorepo structure](../../../platform/005-monorepo-structure.md)
- [agentme-edr-007 - Project quality standards](../../../governance/007-project-quality-standards.md)
- [agentme-edr-008 - Common development script names](../../../platform/008-common-targets.md)
- [_core-adr-003 - Skill standards](../../../../../_core/adrs/principles/003-skill-standards.md)