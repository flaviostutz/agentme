---
name: agentme-edr-008-common-development-script-names
description: Defines standard Makefile target names and the mandatory tool-execution flow using Mise. Use when designing build, lint, test, and release entry points.
---

# agentme-edr-008: Common development script names

## Context and Problem Statement

Software projects use a wide variety of commands and tooling to perform the same fundamental tasks — building, testing, linting, and deploying. This diversity is amplified across language ecosystems, meaning developers must re-learn project-specific conventions every time they switch contexts. CI pipelines suffer from the same fragmentation, each one requiring bespoke scripts.

What standard set of Makefile target names and execution rules should projects adopt so that any developer or CI pipeline can immediately operate on any project without needing to read documentation first?

## Decision Outcome

**Every project must expose its development actions through a root `Makefile` using a defined set of standardized target names. Target implementation and tool-execution rules follow [agentme-edr-017](017-tool-execution-and-scripting.md), which requires `mise exec --` before routine tool commands.**

Standardizing both the target names and the execution chain removes per-project guesswork, makes CI pipelines reusable, and keeps tooling behavior visible in one place.

### Implementation Details

#### 01-every-project-must-have-root-makefile

The project root must contain a single authoritative `Makefile` that exposes the standard target names defined in rule 3. Developers and CI pipelines must invoke routine actions through this `Makefile`, never by calling underlying tools directly in documentation, CI, or daily workflow commands.

`make <target>` is the shared contract across projects and languages.

- The root `Makefile` must be the entry point for both developers and pipelines.
- The root `Makefile` must expose at minimum the common targets defined in this XDR.
- Reverse-compatibility wrappers are allowed when an ecosystem expects them, but they must stay trivial.
	- Allowed: `package.json` script `"test": "make test"`
	- Not allowed: `make test` -> `npm run test` -> tool command
- Project logic must not live in npm scripts, Mise tasks, shell wrappers, or other secondary runners when the same logic belongs in the `Makefile`.

*Why:* The project entry point must stay language-agnostic and obvious. A developer should be able to inspect the `Makefile` and immediately see which real tool commands will run.

#### 02-makefile-recipes-must-use-mise

After a checkout, the shared execution flow is:

```text
make <target>
	-> Makefile recipe
		-> mise exec -- <tool> [tool arguments]
			-> explicit tool command
```

- The `setup` target must run `mise install` and any small project-specific bootstrap needed before normal targets work.
- Routine targets such as `build`, `lint`, `test`, `run`, and `publish` must be invoked as `make <target>` by both contributors and CI.
- Each Makefile recipe must call the real underlying command through `mise exec --`, following [agentme-edr-017](017-tool-execution-and-scripting.md).
- Makefile recipes must not add extra script layers such as `npm run`, `pnpm run`, `yarn run`, `mise run`, `mise tasks`, or shell aliases when those layers only forward to another command.
- Calling the actual tool is allowed even when that tool itself launches another program as part of its normal interface.
	- Allowed: `mise exec -- pnpm exec eslint ./src`
	- Allowed: `mise exec -- go test -cover ./...`
	- Allowed: `mise exec -- uv run --project . pytest`
	- Disallowed: `pnpm run lint`
	- Disallowed: `pnpm exec eslint ./src`
	- Disallowed: `mise run lint`
	- Disallowed: `make lint` implemented as `./scripts/lint.sh` when the shell script only forwards to one visible tool command

*Why:* This keeps the execution path inspectable, avoids hidden logic spread across multiple scripting systems, and makes CI behave the same way as local development.

---

#### 03-standard-target-groups-and-names

Targets are organized into five lifecycle groups. Projects must use these names unchanged. Extensions are allowed (see rule 5) but the core names must not be repurposed.

##### Developer group

| Target | Purpose |
|--------|---------|
| `setup` | Run `mise install` and any small project bootstrap needed before normal targets work. This is the first command after checkout. |
| `all` | Alias that runs `build`, `lint`, and `test` in sequence. Must be the default target (i.e., running `make` or the runner with no arguments invokes `all`). Used by developers as a fast pre-push check to verify the software meets minimum quality standards in one command. |
| `clean` | Remove all temporary or generated files created during build, lint, or test (e.g., `node_modules`, virtual environments, compiled binaries, generated files). Used both locally and in CI for a clean slate. |
| `dev` | Run the software locally for development (e.g., start a Node.js API server, open a Jupyter notebook, launch a React dev server). May have debugging tools, verbose logging, or hot reloading features enabled. |
| `run` | Run the software in production mode (e.g., start a compiled binary, launch a production server). No debugging or development-only features should be enabled. |
| `update-lockfile` | Update the dependency lockfile to reflect the latest resolved versions of all dependencies. |

##### Build group

| Target | Purpose |
|--------|---------|
| `build` | Install dependencies, compile, and package the software. The full `install → compile → package` workflow. |
| `install` | Download and install all project dependencies. Assumes the language runtime is already available (installed via `setup`). |
| `compile` | Compile source files into binaries or transpiled output. Assumes dependencies are already installed. |
| `package` | Assemble a distributable package from compiled files and other resources. Use the `VERSION` environment variable to set the package version explicitly. |
| `bump` | Automatically upgrade dependencies to the latest version that satisfies the semver range declared in the dependency manifest (e.g., `package.json`, `go.mod`, `pyproject.toml`). Does not widen or change the declared range — only resolves to the highest compatible version within it. After bumping, updates the lockfile and stages the changes. Useful for routine dependency maintenance without risking breaking semver contracts. |

##### Lint group

| Target | Purpose |
|--------|---------|
| `lint` | Run **all static quality checks** outside of tests. This MUST include: code formatting validation, code style enforcement, code smell detection, static analysis, dependency audits for known CVEs, security vulnerability scans (e.g., SAST), and project/configuration structure checks. All checks must be non-destructive (read-only); fixes are handled by `lint-fix`. |
| `lint-fix` | Automatically fix linting and formatting issues where possible. || `lint-format` | *(Optional)* Check code formatting only (e.g., Prettier, gofmt, Black). |
##### Test group

| Target | Purpose |
|--------|---------|
| `test` | Run **all tests** required for the project. This MUST include unit tests (with coverage enforcement — the build MUST fail if coverage thresholds are not met) and integration/end-to-end tests. Normally delegates to `test-unit` and `test-integration` in sequence. |
| `test-unit` | Run unit tests only, including coverage report generation and coverage threshold enforcement. |
| `test-integration` | *(Optional)* Run integration and end-to-end tests only. Projects without integration tests may omit this target. |
| `test-smoke` | *(Optional)* Run a fast, minimal subset of tests to verify the software is basically functional. Useful as a post-deploy health check. |

##### Release group

| Target | Purpose |
|--------|---------|
| `release` | Determine the next version (e.g., via semantic versioning and git tags), generate changelogs and release notes, tag the repository, and create a release artifact. Normally invokes `docgen`. |
| `docgen` | Generate documentation (API docs, static sites, changelogs, example outputs). |
| `publish` | Upload the versioned package to the appropriate registry (npm, PyPI, DockerHub, GitHub Releases, blob storage, etc.). Depends on `release` and `package` having been run first. |
| `deploy` | Provision the software on a running environment. Use the `STAGE` environment variable to select the target environment (e.g., `STAGE=dev make deploy`). |
| `undeploy` | Deactivate or remove the software from an environment. Use the `STAGE` environment variable in the same way as `deploy`. Useful for tearing down ephemeral PR environments. |

---

#### 04-standard-environment-variables

Two environment variables have defined semantics and must be used consistently.

| Variable | Purpose |
|----------|---------|
| `STAGE` | Identifies the runtime environment. Format: `[prefix][-variant]`. Common prefixes: `dev`, `tst`, `acc`, `prd`. Examples: `dev`, `dev-pr123`, `tst`, `prd-blue`. May be required by any target that is environment-aware (build, lint, deploy, etc.). |
| `VERSION` | Sets the explicit version used during packaging and deployment. Used when there is no automatic version-tagging utility, or to override it. |

---

#### 05-extending-targets-with-prefixes

Projects may add custom targets beyond the standard set. Custom targets must be named by prefixing a standard target name with a descriptive qualifier, keeping the naming intuitive and consistent with the group it belongs to.

**Examples:**

```
build-dev         # prepare a build specifically for STAGE=dev
build-docker      # build a Docker image with the application
test-smoke        # run a fast subset of unit tests on critical paths
test-examples     # run the examples/ folder as integration tests
publish-npm       # publish to the npm registry specifically
publish-docker    # publish a Docker image
run-docker        # run the application inside a Docker container
start-debugger    # launch the software with a visual debugger attached
deploy-infra      # deploy only the infrastructure layer
```

The prefix convention ensures developers can infer the purpose of any target without documentation.

---

#### 06-monorepo-usage

In a monorepo, each module has its own `Makefile` with its own `build`, `lint`, `test`, and `deploy` targets scoped to that module. Parent-level Makefiles (at the application or repo root) delegate to child Makefiles in sequence. The parent Makefile should call `$(MAKE) -C <child> <target>` directly, while each child `Makefile` runs its actual tool commands through `mise exec --`.

```makefile
# root Makefile — delegates to all modules
build:
	$(MAKE) -C module-a build
	$(MAKE) -C module-b build

test:
	$(MAKE) -C module-a test
	$(MAKE) -C module-b test
```

A developer can run `make test` at the repo root to test everything, or `cd module-a && make test` to test a single module. Both must work.

**Reference:** See [agentme-edr-005](005-monorepo-structure.md) for the full monorepo layout convention.

---

#### 07-quick-reference

Any project following this EDR supports the following actions through the root `Makefile`.

```sh
# install the pinned toolchain and project bootstrap
make setup

# build the software (install deps, compile, package)
make build

# run all tests (unit + integration)
make test

# check code formatting, style, code smells, CVE audits, security scans, and project structure
make lint

# auto-fix lint/formatting issues
make lint-fix

# run the software in dev mode (may have hot reload, debug tools enabled, verbose logging etc)
make dev

# run the software in production mode
make run

# generate next version, changelogs, and tag the repo; then package
make release package

# publish the release to a registry (e.g., npm, PyPI)
make publish

# deploy to the dev environment
STAGE=dev make deploy

# remove all temporary/generated files
make clean

# run build + lint + test in one shot (pre-push check)
make all
```

## Considered Options

* (REJECTED) **Language-native entry points only** - Use `npm run`, `python -m`, `go run`, and similar tool-specific commands directly as the standard surface
  * Reason: Ties CI pipelines and developer muscle memory to language-specific tooling; breaks the abstraction when the underlying tool changes; target names vary per ecosystem

* (REJECTED) **Runner-agnostic targets with multiple primary runners** - Keep the target names standard but allow Makefile, npm scripts, shell wrappers, or other runners as equivalent first-class entry points
	* Reason: Preserves naming consistency but still spreads behavior across multiple scripting systems, which hides the real command path and weakens CI standardization.

* (CHOSEN) **Standardized Makefile targets with Mise-managed explicit tool execution** - Use `make <target>` as the only routine entry point, keep target names standard, and run the actual underlying tool commands through `mise exec --`
	* Reason: This keeps names, execution flow, and tool versions equally predictable while avoiding script indirection.

## References

- [agentme-edr-005](005-monorepo-structure.md) - Monorepo layout and delegation structure
- [agentme-edr-017](017-tool-execution-and-scripting.md) - Tool-execution rules for Makefile targets and CI
