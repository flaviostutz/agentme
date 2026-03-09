# agentkit-edr-005: Monorepo structure

## Context and Problem Statement

Without a defined monorepo layout, teams independently organize projects in ways that are inconsistent, hard to navigate, and difficult to build uniformly. Shared code gets duplicated, tooling varies per project, and onboarding new contributors is slow because there is no standard entry point or build convention.

What monorepo structure, naming conventions, tooling, and build standards should be followed to keep multiple projects cohesive, discoverable, and easy to build?

## Decision Outcome

**Adopt a standardized monorepo layout with top-level application folders, a shared library area, Mise-managed tooling, and Makefiles at every level so any contributor can build, lint, and test any part of the monorepo with a single, predictable command.**

### Implementation Details

#### 1. Top-level directory layout

```
/
├── shared/               # Resources shared across ALL applications
│   ├── libs/             # Reusable libraries consumed by applications
│   └── scripts/          # Build/CI/dev scripts used across applications
│
├── <application>/        # One folder per application or project (see rule 2)
│   ├── README.md         # REQUIRED — describes the application (see rule 5)
│   ├── <module>/         # One folder per compilable module (see rule 3)
│   └── shared/           # Resources shared by modules within THIS application
│
├── Makefile              # Root Makefile coordinating all areas (see rule 6)
├── README.md             # REQUIRED — onboarding and quickstart guide (see rule 7)
└── .mise.toml            # Mise tool version configuration (see rule 8)
```

---

#### 2. Application folders

An **application** (also called a project) is a folder at the repository root that:

- Represents something large enough to have a "life of its own" — it aggregates many dependencies, modules, and concerns (e.g., `mymobileapp`, `graphvisualizer`, `pcbdevices`).
- **MUST** depend only on resources in `/shared/`. Direct cross-application dependencies are forbidden. Use published resources (such as publishing container images or libraries for that)
- **MUST** contain a `README.md` describing what the application is about.

*Why:* Keeping applications isolated prevents implicit coupling that makes large monorepos painful to refactor. The `shared/` boundary makes coupling explicit and intentional.

**Example layout:**

```
graphvisualizer/
├── README.md
├── shared/               # shared between graphvisualizer modules only
├── renderer/             # module: produces a build artifact
├── dataloader/           # module: produces a build artifact
└── cli/                  # module: produces a build artifact
```

---

#### 3. Module folders

A **module** is a subfolder inside an application that:

- Is independently compilable, or has its own `Makefile` that produces a build artifact from source files.
- May depend on sibling modules within the same application, or on `/shared/` resources.
- **MUST NOT** depend on modules from other applications.

*Why:* Module-level isolation enables incremental builds and clear ownership within an application.

---

#### 4. Naming conventions

- All folder and file names **MUST** be **lowercase**.
- Use hyphens (`-`) to separate words in folder names (e.g., `data-loader`, `graph-visualizer`).
- Avoid abbreviations unless they are universally understood in the domain (e.g., `cli`, `api`).

---

#### 5. Application README

Every application folder **MUST** contain a `README.md` that covers:

1. **Purpose** — what the application does and why it exists.
2. **Architecture overview** — list of modules and how they relate to each other.
3. **How to build** — point to the Makefile targets or prerequisite steps.
4. **How to run** — a minimal working example.

---

#### 6. Makefiles at every level

A `Makefile` **MUST** be present in:

- The repository root.
- Every application folder.
- Every module folder.

Each Makefile **MUST** define at minimum the following targets:

| Target  | Description                                                  |
|---------|--------------------------------------------------------------|
| `build` | Compile or package the module/application into an artifact.  |
| `lint`  | Run static analysis and formatting checks.                   |
| `test`  | Execute the test suite.                                      |

*Why:* Makefiles provide a universal, stack-agnostic entry point. A contributor working across Go, Python, and TypeScript modules can always type `make build` or `make test` without reading language-specific docs.

**Example module Makefile:**

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

#### 7. Root Makefile

The root `Makefile` **MUST**:

- Coordinate `build`, `lint`, and `test` targets across all applications and modules (typically by delegating to sub-makes).
- Include a **`setup`** target that either performs environment setup (installing tools, configuring secrets) or prints clear human-readable instructions so a new contributor can prepare their machine to work on the monorepo.

**Example root Makefile:**

```makefile
.PHONY: build lint test setup

APPS := graphvisualizer pcbdevices mymobileapp

build:
	$(foreach app,$(APPS),$(MAKE) -C $(app) build &&) true

lint:
	$(foreach app,$(APPS),$(MAKE) -C $(app) lint &&) true

test:
	$(foreach app,$(APPS),$(MAKE) -C $(app) test &&) true

setup:
	@echo "Install Mise: https://mise.jdx.dev/getting-started.html"
	@echo "Then run: mise install"
	@echo "See README.md for full setup instructions."
```

---

#### 8. Mise for tooling management

[Mise](https://mise.jdx.dev/) **MUST** be used to pin and manage the versions of all basic tooling required to build and work on the monorepo (compilers, runtimes, CLI tools, etc.).

- A `.mise.toml` file **MUST** exist at the repository root declaring all required tool versions.
- Contributors activate the environment by running `mise install` once after cloning.

*Why:* Mise ensures every contributor and CI environment uses the exact same tool versions, eliminating "works on my machine" build failures.

**Example `.mise.toml`:**

```toml
[tools]
node = "22.3.0"
python = "3.12.4"
go = "1.22.4"
```

---

#### 9. Root README

The root `README.md` **MUST** include:

1. **Overview** — what this monorepo contains and its high-level structure.
2. **Machine setup** — step-by-step instructions to prepare a development environment (install Mise, run `mise install`, any OS-level prerequisites).
3. **Quickstart** — instructions to run at least one project locally as a concrete working example.
4. **Repository map** — a brief description of each top-level application and the `shared/` area.

---

#### 10. Summary of requirements

| Requirement | Scope | Mandatory |
|---|---|---|
| Lowercase folder/file names | All | Yes |
| `README.md` per application | Application folders | Yes |
| `Makefile` with `build`, `lint`, `test` | All modules and applications | Yes |
| Root `Makefile` with `setup` target | Repository root | Yes |
| Root `README.md` with setup + quickstart | Repository root | Yes |
| Mise `.mise.toml` at root | Repository root | Yes |
| Applications depend only on `/shared/` | Application folders | Yes |
| Modules depend only on siblings or `/shared/` | Module folders | Yes |
