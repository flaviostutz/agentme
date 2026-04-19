---
name: agentme-edr-017-tool-execution-and-scripting
description: Defines how Makefiles, CI pipelines, and optional wrapper scripts execute project commands. Use when designing project automation or command entry points.
---

# agentme-edr-017: Tool execution and scripting

## Context and Problem Statement

Projects often hide build, lint, and test behavior behind multiple scripting layers, making it hard for developers and CI pipelines to see what actually runs.

How should projects execute development commands so the command surface stays predictable and the underlying operations stay obvious?

## Decision Outcome

**Use Makefiles as the only authoritative command entry point, with targets named by [agentme-edr-008](008-common-targets.md) and implemented with `mise exec --` before the real tool command.**

This keeps local development and CI aligned, reduces indirection, and lets contributors understand project behavior by reading one command surface.

### Implementation Details

- Every project MUST use a root `Makefile` as the authoritative entry point for developer and pipeline commands.
- The target names in that `Makefile` MUST follow [agentme-edr-008](008-common-targets.md).
- CI pipelines MUST run `make <target>` from the relevant root instead of calling language-specific scripts such as `npm run`, `pnpm run`, shell wrappers, or secondary task runners.
- A Makefile target MUST execute the real operation through `mise exec --` before invoking the tool itself, so it always uses the version pinned in `.mise.toml`. Avoid intermediate script layers that hide the actual command.
- Every Makefile target MUST start by echoing a concise summary of the target and folder or context, using fewer than 10 words. When delegating to another Makefile, echo the child path and delegated target before invoking it.
- Direct delegation to another Makefile is allowed when traversing repo, app, or module boundaries, for example `$(MAKE) -C lib build`.
- Calling the actual tool binary through its native executable launcher is allowed when that is the direct command under `mise exec --`, for example `mise exec -- pnpm exec eslint ./src`, `mise exec -- uv run pyright`, `mise exec -- go test`, or `mise exec -- npx -y monotag`.
- Makefile targets MUST use `mise exec --` consistently before routine tool commands and MUST NOT call `npm run`, `pnpm run`, `yarn run`, `just`, `task`, or similar abstraction layers for routine project commands.
- Tool installation and environment preparation MUST be handled explicitly in developer setup instructions and CI workflow steps, using ecosystem-specific installation steps such as `actions/setup-node`, `actions/setup-go`, `astral-sh/setup-uv`, system package managers, or pinned install commands such as `mise install`.
- `package.json` scripts are optional and MAY exist only as direct reverse-compatibility aliases to one Make target, for example `"test": "make test"`. They MUST stay one-to-one and add no extra orchestration.
- README examples, contributing guides, and pipeline snippets SHOULD show `make <target>` as the primary way to operate the project.

Allowed:

- `make lint` running `mise exec -- pnpm exec eslint ./src`
- `make test` running `mise exec -- go test ./...`
- `make build` running `mise exec -- uv build --project . --out-dir dist`
- Root Makefile delegating to module Makefiles with `$(MAKE) -C <module> <target>`
- A target beginning with `echo ">>> ./lib: lint"`

Disallowed:

- `make lint` running `pnpm run lint`
- `make test` running `mise exec -- make test`
- `make lint` running `pnpm exec eslint ./src` without `mise exec --`
- CI running `npm run build` when the project already defines `make build`
- `package.json` scripts that chain multiple operations instead of forwarding to one Make target

## Considered Options

* (REJECTED) **Runner-agnostic command entry points** - Allow Makefiles, package-manager scripts, shell wrappers, and task runners as equivalent project entry points.
  * Reason: Preserves multiple abstraction layers and weakens the guarantee that developers and CI execute the same visible commands.
* (CHOSEN) **Makefile-first Mise-managed execution** - Standardize on Makefiles for entry points and require targets to run the underlying commands through `mise exec --`.
  * Reason: Keeps the command surface small, readable, and consistent across languages while ensuring the pinned tool versions from `.mise.toml` are always used.

## References

- [agentme-edr-005](005-monorepo-structure.md) - Monorepo layout and Makefile hierarchy
- [agentme-edr-006](006-github-pipelines.md) - CI/CD workflows should call Make targets
- [agentme-edr-008](008-common-targets.md) - Standard target names
- [agentme-edr-003](../application/003-javascript-project-tooling.md) - JavaScript tooling commands inside Makefiles
- [agentme-edr-010](../application/010-golang-project-tooling.md) - Go tooling commands inside Makefiles
- [agentme-edr-014](../application/014-python-project-tooling.md) - Python tooling commands inside Makefiles