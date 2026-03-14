# _local-bdr-001: agentkit product purpose and consumer model

## Context and Problem Statement

agentkit is an npm package that distributes opinionated XDRs and speckit agent skills to other
projects. Without a clear statement of its product purpose and how consumers are expected to use
it, contributors may add artifacts that dilute the product focus or break the consumption model.

What is agentkit's product purpose, who are its consumers, and how do they integrate it?

## Decision Outcome

**agentkit is a curated distribution package of XDRs and AI agent skills, consumed by other
projects via npmdata preset extraction.**

Consumers install agentkit as an npm dependency and run preset extraction to populate their own
repository with a curated set of XDRs and speckit agent files. The product value is the curation:
only well-reviewed, non-conflicting, immediately usable artifacts are shipped.

### Implementation Details

**Product scope**

agentkit ships two kinds of artifacts:

1. **XDRs** (in `.xdrs/agentkit/`) — opinionated engineering and architectural decision records
   covering coding best practices, tooling, testing, project structure, and CI/CD pipelines.
   These are intended for other teams to adopt as their own decision baseline.

2. **speckit agent files** (in `.github/agents/`, `.github/prompts/`, `.specify/`) — a complete
   AI-assisted software development workflow for VS Code Copilot. Includes agent definitions,
   prompt files, memory templates, and Bash scripts for managing feature specs and plans.

**Consumer workflow**

1. Consumer adds `agentkit` as an npm devDependency.
2. Consumer runs `pnpm exec agentkit extract --output . --presets <preset>` to populate their
   repository.
3. Consumer commits the extracted files; agentkit manages updates via the `.npmdata` marker.

**Preset model**

| Preset | Contents |
|--------|----------|
| `basic` | agentkit XDRs + `xdrs-core` baseline ADRs + `AGENTS.md` |
| `speckit` | speckit agent/prompt files + `.specify/` templates + VS Code settings |
| (none) | all of the above combined |

**Business rules**

- Only artifacts that are self-contained and conflict-free MUST be included in a preset.
- Preset membership is a public contract: changing which files belong to a preset is a breaking
  change for consumers who depend on that preset.
- The `_local` scope in agentkit's own `.xdrs/` is NOT shipped; it is for internal use only.
- agentkit MUST NOT take a runtime dependency on the consumer's codebase. It is a static
  distribution package only.

## References

- [_local-adr-001 - Project basics](../../adrs/principles/001-project-basics.md)
- [_local-adr-002 - XDR scope guidelines](../../adrs/principles/002-xdr-scope-guidelines.md)
- [agentkit-edr-003 - JavaScript project tooling](../../../agentkit/edrs/application/003-javascript-project-tooling.md)
