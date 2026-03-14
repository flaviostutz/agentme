# agentkit-edr-008: Common development script names

## Context and Problem Statement

Software projects use a wide variety of commands and tooling to perform the same fundamental tasks — building, testing, linting, and deploying. This diversity is amplified across language ecosystems, meaning developers must re-learn project-specific conventions every time they switch contexts. CI pipelines suffer from the same fragmentation, each one requiring bespoke scripts.

What standard set of command names and conventions should projects adopt so that any developer or CI pipeline can immediately operate on any project without needing to read documentation first?

## Decision Outcome

**Every project must expose its development actions using a defined set of standardized script names, grouped by lifecycle phase. These names apply regardless of the script runner used — Makefile, npm scripts, shell scripts, or any other tool — so that `build`, `test`, `lint`, and related commands work predictably across all projects and languages.**

Standardizing script names removes the cognitive overhead of learning per-project conventions, makes CI pipelines reusable across projects, and gives new developers an immediately operational entry point. The names are the contract; the underlying runner is an implementation detail.

### Implementation Details

#### 1. Every project MUST have a root-level entry point exposing the standard script names

The project root must contain a single authoritative entry point — a `Makefile`, `package.json` scripts section, a shell wrapper, or equivalent — that exposes the standard target names defined in rule 2. Developers and CI pipelines must invoke actions through this entry point exclusively, never by calling underlying tools directly.

**Preferred runner: Makefile.** A `Makefile` is the default recommended choice because it is language-agnostic, universally available, and provides a consistent invocation syntax (`make <target>`) across all ecosystems.

**Alternative runners** are acceptable when a Makefile is not practical for the project's ecosystem:

| Runner | Invocation example | When appropriate |
|--------|--------------------|------------------|
| Makefile | `make build` | Default; recommended for all projects |
| npm scripts | `npm run build` | Pure Node.js/frontend projects without a Makefile |
| Shell script | `./dev.sh build` | Projects where `make` is unavailable or impractical |
| Other (Taskfile, just, etc.) | `task build` | When agreed upon at the project or org level |

Whichever runner is chosen, the **target names** defined in rule 2 must be used unchanged. The runner is an implementation detail; the names are the shared contract.

*Why:* A single entry point means developers and CI pipelines use near-identical commands regardless of the underlying language or tooling. Any tooling change is then contained to the entry-point file and does not require updating CI pipelines or developer documentation.

---

#### 2. Standard script groups and names

Scripts are organized into five lifecycle groups. Projects must use these names regardless of the script runner in use. Extensions are allowed (see rule 4) but the core names must not be repurposed.

##### Developer group

| Script | Purpose |
|--------|---------|
| `setup` | Install any tools required on the developer machine (e.g., nvm, brew, python, golang). Typically run once per project checkout. In CI, tooling is usually pre-provisioned via runner images or workflow steps instead. |
| `all` | Alias that runs `build`, `lint`, and `test` in sequence. Must be the default target (i.e., running `make` or the runner with no arguments invokes `all`). Used by developers as a fast pre-push check to verify the software meets minimum quality standards in one command. |
| `clean` | Remove all temporary or generated files created during build, lint, or test (e.g., `node_modules`, virtual environments, compiled binaries, generated files). Used both locally and in CI for a clean slate. |
| `start` | Run the software locally for development (e.g., start a Node.js API server, open a Jupyter notebook, launch a React dev server). |
| `update-lockfile` | Update the dependency lockfile to reflect the latest resolved versions of all dependencies. |

##### Build group

| Script | Purpose |
|--------|---------|
| `build` | Install dependencies, compile, and package the software. The full `install → compile → package` workflow. |
| `install` | Download and install all project dependencies. Assumes the language runtime is already available (installed via `setup`). |
| `compile` | Compile source files into binaries or transpiled output. Assumes dependencies are already installed. |
| `package` | Assemble a distributable package from compiled files and other resources. Use the `VERSION` environment variable to set the package version explicitly. |

##### Lint group

| Script | Purpose |
|--------|---------|
| `lint` | Run code style checks, formatting validation, code smell detection, dependency security scans, and project structure checks. |
| `lint-fix` | Automatically fix linting and formatting issues where possible. |

##### Test group

| Script | Purpose |
|--------|---------|
| `test` | Run the full test suite. Normally delegates to `test-unit` and `test-integration`. |
| `test-unit` | Run unit tests only. |
| `test-integration` | Run integration and end-to-end tests only. |

##### Release group

| Script | Purpose |
|--------|---------|
| `release` | Determine the next version (e.g., via semantic versioning and git tags), generate changelogs and release notes, tag the repository, and create a release artifact. Normally invokes `docgen`. |
| `docgen` | Generate documentation (API docs, static sites, changelogs, example outputs). |
| `publish` | Upload the versioned package to the appropriate registry (npm, PyPI, DockerHub, GitHub Releases, blob storage, etc.). Depends on `release` and `package` having been run first. |
| `deploy` | Provision the software on a running environment. Use the `STAGE` environment variable to select the target environment (e.g., `STAGE=dev make deploy`). |
| `undeploy` | Deactivate or remove the software from an environment. Use the `STAGE` environment variable in the same way as `deploy`. Useful for tearing down ephemeral PR environments. |

---

#### 3. Standard environment variables

Two environment variables have defined semantics and must be used consistently.

| Variable | Purpose |
|----------|---------|
| `STAGE` | Identifies the runtime environment. Format: `[prefix][-variant]`. Common prefixes: `dev`, `tst`, `acc`, `prd`. Examples: `dev`, `dev-pr123`, `tst`, `prd-blue`. May be required by any target that is environment-aware (build, lint, deploy, etc.). |
| `VERSION` | Sets the explicit version used during packaging and deployment. Used when there is no automatic version-tagging utility, or to override it. |

---

#### 4. Extending scripts with prefixes

Projects may add custom scripts beyond the standard set. Custom scripts must be named by prefixing a standard script name with a descriptive qualifier, keeping the naming intuitive and consistent with the group it belongs to.

**Examples:**

```
build-dev         # prepare a build specifically for STAGE=dev
test-smoke        # run a fast subset of unit tests on critical paths
test-examples     # run the examples/ folder as integration tests
publish-npm       # publish to the npm registry specifically
publish-docker    # publish a Docker image
start-debugger    # launch the software with a visual debugger attached
deploy-infra      # deploy only the infrastructure layer
```

The prefix convention ensures developers can infer the purpose of any script without documentation.

---

#### 5. Monorepo usage

In a monorepo, each module has its own `Makefile` with its own `build`, `lint`, `test`, and `deploy` targets scoped to that module. Parent-level Makefiles (at the application or repo root) delegate to module Makefiles in sequence.

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

**Reference:** See [agentkit-edr-005](005-monorepo-structure.md) for the full monorepo layout convention.

---

#### 6. Quick-reference — commands a developer can always rely on

Any project following this EDR supports the following actions. Examples show Makefile syntax; substitute your project's runner (e.g., `npm run build`, `./dev.sh build`) if a Makefile is not used.

```sh
# install required development tools
make setup

# build the software (install deps, compile, package)
make build

# run all tests (unit + integration)
make test

# check code style, formatting, and security findings
make lint

# auto-fix lint/formatting issues
make lint-fix

# run the software locally
make start

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

**Equivalent examples for npm scripts and shell:**

```sh
# npm scripts (package.json)
npm run build
npm run test
npm run lint
STAGE=dev npm run deploy

# shell wrapper
./dev.sh build
./dev.sh test
STAGE=dev ./dev.sh deploy
```

## Considered Options

* (REJECTED) **Language-native entry points only** - Use `npm run`, `python -m`, `go run` etc. directly as the standard without a unifying name convention
  * Reason: Ties CI pipelines and developer muscle memory to language-specific tooling; breaks the abstraction when the underlying tool changes; target names vary per ecosystem

* (CHOSEN) **Standardized script names, runner-agnostic** - A common, language-agnostic command vocabulary that must be used regardless of whether the runner is a Makefile, npm scripts, a shell wrapper, or another tool; with Makefile as the preferred default
  * Reason: Separating the names (the contract) from the runner (the implementation) gives every developer and CI pipeline a predictable interface while allowing each project to choose the most practical runner for its ecosystem.
