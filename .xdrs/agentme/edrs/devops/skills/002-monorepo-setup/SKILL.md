---
name: 002-monorepo-setup
description: >
  Step-by-step instructions for setting up and scaffolding a new monorepo following the standard
  layout, naming conventions, Makefiles, Mise tooling, and README requirements defined in
  agentme-edr-005. Activate this skill when the user asks to create, initialize, or set up a
  monorepo, add a new application or module to an existing monorepo, or verify that a monorepo
  complies with the standard structure.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Creates or extends a monorepo that follows the standard layout from [agentme-edr-005](../../005-monorepo-structure.md):
top-level application folders, independent module roots, sibling example and multi-module test
areas, Mise-managed tooling, and Makefiles at every level so any contributor can build, lint, and
test any part of the monorepo with a single, predictable command.

Related EDRs: [agentme-edr-005](../../005-monorepo-structure.md), [agentme-edr-013](../../../governance/013-contributing-guide-requirements.md), [agentme-edr-016](../../../principles/016-cross-language-module-structure.md)

## Instructions

### Phase 1: Gather information

1. Ask for (or infer from context):
   - **Applications** — names and short descriptions of the top-level applications to scaffold.
   - **Modules** — modules inside each application (e.g., `renderer`, `dataloader`, `cli`).
   - **Primary language(s)** — Go, Python, TypeScript, etc., to choose the right build commands.
   - **Tool versions** — versions to pin in `.mise.toml` (compilers, runtimes, CLI tools).
2. Confirm the target directory (default: current workspace root).

---

### Phase 2: Create root-level files

#### `.mise.toml`

Pin all required tool versions. Example for a Go + Node.js monorepo:

```toml
[tools]
go = "1.22"
node = "24"
golangci-lint = "1.57"
```

#### Root `Makefile`

Coordinates `build`, `lint`, and `test` across all applications. Also exposes a `setup` target.

```makefile
.PHONY: all build lint test clean setup

APPS := <app1> <app2>   # replace with actual application names

all: build lint test

build:
	$(foreach app,$(APPS),$(MAKE) -C $(app) build &&) true

lint:
	$(foreach app,$(APPS),$(MAKE) -C $(app) lint &&) true

test:
	$(foreach app,$(APPS),$(MAKE) -C $(app) test &&) true

clean:
   $(foreach app,$(APPS),$(MAKE) -C $(app) clean &&) true
   rm -rf .cache

setup:
	@echo "Install Mise: https://mise.jdx.dev/getting-started.html"
	@echo "Then run: mise install"
	@echo "See README.md for full setup instructions."
```

#### Root `.gitignore`

Must ignore shared artifact and cache folders:

```gitignore
dist/
.cache/
```

#### Root `README.md`

Must include four sections:

```markdown
# <Monorepo Name>

## Overview
<What this monorepo contains and its high-level structure.>

## Machine setup
1. Install [Mise](https://mise.jdx.dev/getting-started.html).
2. Clone the repository and run `mise install`.
3. <Any OS-level prerequisites.>

## Quickstart
<Instructions to run at least one project locally as a concrete working example.>

## Repository map
| Folder              | Description                        |
|---------------------|------------------------------------|
| `shared/`           | Libraries and scripts shared across all apps |
| `<app1>/`           | <Short description of app1>        |
| `<app2>/`           | <Short description of app2>        |
```

#### Root `CONTRIBUTING.md`

Must explain the contribution workflow in a short, explicit way.

```markdown
# Contributing

## Bugs
Report bugs in GitHub issues with steps to reproduce, expected behavior, and actual behavior.

## Features
Discuss feature ideas in an issue before opening a pull request so scope and approach can be agreed first.

## Pull requests
Submit fixes and features through pull requests from feature branches targeting `main`.

## Review etiquette
Use [Conventional Comments](https://conventionalcomments.org/) in review feedback.

## Keep changes focused
Keep pull requests small and focused enough that review and discussion stay efficient.
```

---

### Phase 3: Create the `shared/` area

```
shared/
├── libs/       # Reusable libraries consumed by applications
└── scripts/    # Build/CI/dev scripts used across applications
```

Create these folders; populate only if shared content already exists.

---

### Phase 4: Scaffold each application

For each application:

1. **Create the application folder** using lowercase, hyphen-separated names (e.g., `graph-visualizer`).

2. **Create `<app>/README.md`** with the four required sections:

   ```markdown
   # <Application Name>

   ## Purpose
   <What this application does and why it exists.>

   ## Architecture overview
   | Module        | Description                        |
   |---------------|------------------------------------|
   | `<module1>/`  | <What it does and what it produces>|

   ## How to build
   Run `make build` from this folder or from the repository root.

   ## How to run
   <Minimal working example.>
   ```

3. **Create `<app>/Makefile`** that delegates to each module:

   ```makefile
   .PHONY: all build lint test clean

   MODULES := <module1> <module2>   # replace with actual module names

   all: build lint test

   build:
   	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) build &&) true

   lint:
   	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) lint &&) true

   test:
   	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) test &&) true

   clean:
   	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) clean &&) true
   	rm -rf .cache
   ```

4. **Create `<app>/shared/`** — leave empty if no cross-module shared code exists yet.

5. **Create sibling aggregation folders when needed**: `<app>/examples/`, `<app>/tests_integration/`, and `<app>/tests_benchmark/` for artifacts that apply to multiple modules.

---

### Phase 5: Scaffold each module

For each module inside an application:

1. **Create the module folder** using lowercase, hyphen-separated names (e.g., `data-loader`).

2. **Create `<app>/<module>/README.md`** with consumer usage first and short developer commands at the end.

3. **Create `<app>/<module>/Makefile`** with the common targets, adapted to the module's language. Redirect persistent caches into `.cache/` and write distributable artifacts to `dist/`.

   **Go:**
   ```makefile
   .PHONY: all build lint test clean

   all: build lint test

   build:
   mise exec -- go build ./...

   lint:
   mise exec -- golangci-lint run ./...

   test:
   mise exec -- go test ./... -cover

   clean:
	rm -rf dist .cache
   ```

   **Node.js / TypeScript:**
   ```makefile
   .PHONY: all build lint test clean

   all: build lint test

   build:
   mise exec -- pnpm exec tsc --project tsconfig.json

   lint:
   mise exec -- pnpm exec eslint ./src

   test:
   mise exec -- pnpm exec jest --verbose

   clean:
	rm -rf dist .cache
   ```

   **Python:**
   ```makefile
   .PHONY: all build lint test clean

   all: build lint test

   build:
   mise exec -- uv build --project . --out-dir dist

   lint:
   mise exec -- uv run --project . ruff check .

   test:
   mise exec -- uv run --project . pytest

   clean:
	rm -rf dist .cache
   ```

4. **Add source files** appropriate to the language, placing them inside the module folder.

5. **Place module-specific integration tests and benchmarks predictably**: `<module>/tests_integration/` and `<module>/tests_benchmark/` when they are not co-located by language convention.

---

### Phase 6: Verify and report

After scaffolding, run the following checks and fix any issues:

- `make build` at the repository root succeeds.
- `make lint` at the repository root passes.
- `make test` at the repository root passes.
- All folder and file names are lowercase and use hyphens.
- The root `.gitignore` ignores `dist/` and `.cache/`.
- A `CONTRIBUTING.md` exists at the repository root and covers bugs, feature discussions, pull requests, Conventional Comments, and small focused changes.
- Every application folder has a `README.md` covering all four required sections.
- Every module folder has a `README.md`, `Makefile`, `dist/` location, and `.cache/` strategy.
- A `.mise.toml` exists at the repository root with all required tool versions pinned.

---

## Examples

### Example: adding a new `pcb-devices` application with a `firmware` module (Go)

```
pcb-devices/
├── README.md
├── Makefile
├── examples/
├── shared/
└── firmware/
   ├── README.md
    └── Makefile
```

`pcb-devices/Makefile`:
```makefile
.PHONY: build lint test
MODULES := firmware
build:
	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) build &&) true
lint:
	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) lint &&) true
test:
	$(foreach mod,$(MODULES),$(MAKE) -C $(mod) test &&) true
```

`pcb-devices/firmware/Makefile`:
```makefile
.PHONY: build lint test
build:
	go build ./...
lint:
	golangci-lint run ./...
test:
	go test ./... -cover
```

---

## Edge Cases

- **Cross-application dependency requested:** Refuse and suggest publishing the shared code as a library in `shared/libs/` instead.
- **Module with no compilable output (e.g., pure scripts):** Still create the Makefile; `build` can be a no-op (`@true`) but the target must exist.
- **Language not listed above:** Mirror the pattern — `build` produces an artifact, `lint` runs static analysis, `test` runs tests. Adapt commands to the actual toolchain.
- **Existing files:** Never overwrite existing `README.md`, `CONTRIBUTING.md`, or `Makefile` files without user confirmation. Diff and propose additions instead.
