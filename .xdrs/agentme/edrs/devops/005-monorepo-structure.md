---
name: agentme-edr-005-monorepo-structure
description: Defines the standard monorepo layout, naming, and build conventions using shared areas, Mise, and Makefiles. Use when creating or reviewing monorepos.
---

# agentme-edr-005: Monorepo structure

## Context and Problem Statement

Without a defined monorepo layout, teams independently organize projects in ways that are inconsistent, hard to navigate, and difficult to build uniformly. Shared code gets duplicated, tooling varies per project, and onboarding new contributors is slow because there is no standard entry point or build convention.

What monorepo structure, naming conventions, tooling, and build standards should be followed to keep multiple projects cohesive, discoverable, and easy to build?

## Decision Outcome

**Adopt a standardized monorepo layout with top-level application folders that aggregate independent module roots, shared parent-level example and test areas, Mise-managed tooling, and Makefiles at every level.**

For step-by-step scaffolding instructions see [skill 002-monorepo-setup](skills/002-monorepo-setup/SKILL.md).
Module folder responsibilities, artifact locations, and test-folder conventions follow [agentme-edr-016](../principles/016-cross-language-module-structure.md).

### Implementation Details

#### 01-top-level-directory-layout

```
/
├── .cache/               # Optional shared cache for repo-level tooling
├── shared/               # Resources shared across ALL applications
│   ├── libs/             # Reusable libraries consumed by applications
│   └── scripts/          # Build/CI/dev scripts used across applications
│
├── <application>/        # One folder per application or project
│   ├── README.md         # REQUIRED
│   ├── Makefile          # REQUIRED
│   ├── <module>/         # One folder per buildable/publishable module
│   │   ├── Makefile      # REQUIRED
│   │   ├── README.md     # REQUIRED
│   │   ├── dist/         # REQUIRED when the module publishes/builds artifacts
│   │   └── .cache/       # REQUIRED when caches are not shared above
│   ├── examples/         # Optional sibling consumer examples for modules in this app
│   ├── tests_integration/# Optional cross-module integration tests for this app
│   ├── tests_benchmark/  # Optional cross-module benchmarks for this app
│   └── shared/           # Resources shared by modules within THIS application
│
├── Makefile              # Root Makefile coordinating all areas
├── .gitignore            # MUST ignore dist/ and .cache/
├── README.md             # REQUIRED — onboarding and quickstart guide
└── .mise.toml            # Mise tool version configuration
```

#### 02-application-folders

- Represent a cohesive unit with its own lifecycle (e.g., `mymobileapp`, `graph-visualizer`).
- **MUST** depend only on resources in `/shared/`. Direct cross-application dependencies are forbidden; use published artifacts (container images, published libraries) instead.
- **MUST** contain a `README.md` with: purpose, architecture overview, how to build, and how to run.
- **MAY** contain `examples/`, `tests_integration/`, and `tests_benchmark/` when those artifacts apply to multiple modules inside the application.

*Why:* Isolating applications prevents implicit coupling and makes the `shared/` boundary explicit and intentional.

#### 03-module-folders

- A module is a subfolder inside an application that is independently compilable and produces a build artifact.
- May depend on sibling modules within the same application or on `/shared/` resources.
- **MUST NOT** depend on modules from other applications.
- **MUST** contain its own `Makefile`, `README.md`, and language/tooling configuration.
- **MUST** keep build outputs under `dist/` and persistent caches under `.cache/`, following [agentme-edr-016](../principles/016-cross-language-module-structure.md).
- **MUST NOT** keep consumer examples inside the module folder; those belong in a sibling `examples/` folder at the nearest parent aggregation root.

#### 04-naming-conventions

- All folder and file names **MUST** be **lowercase**.
- Use hyphens (`-`) to separate words (e.g., `data-loader`, `graph-visualizer`).
- Avoid abbreviations unless universally understood in the domain (e.g., `cli`, `api`).

#### 05-makefiles-at-every-level

A `Makefile` **MUST** be present at the repository root, in every application folder, and in every module folder.

All Makefiles **MUST** use the shared target vocabulary from [agentme-edr-008](008-common-targets.md).

Repository, application, and module Makefiles **MUST** define at minimum: `all`, `build`, `lint`, `test`, and `clean`.

Module Makefiles **SHOULD** also provide `lint-fix` and `install` when the underlying tooling supports them.

The root `Makefile` **MUST** also define a `setup` target that guides a new contributor to prepare their machine.
The root `setup` target **MUST** run `mise install` and any small repository bootstrap required before routine targets work.

*Why:* Makefiles provide a universal, stack-agnostic entry point regardless of programming language.

#### 06-mise-for-tooling-management

- [Mise](https://mise.jdx.dev/) **MUST** be used to pin all tool versions (compilers, runtimes, CLI tools).
- A `.mise.toml` **MUST** exist at the repository root.
- Every language runtime or CLI referenced by any module `Makefile`, CI workflow, or README command **MUST** be pinned in `.mise.toml`.
- Contributors and CI run `make setup` after cloning or checkout; this target must call `mise install`.
- Agents and contributors **MUST** check `.mise.toml` before using a system-installed compiler, runtime, or CLI.
- When `.mise.toml` exists, all build, test, lint, and code-generation commands **MUST** run through `make <target>`, and the Makefile recipes **MUST** execute the underlying tools via `mise exec -- <command>`, following [agentme-edr-017](017-tool-execution-and-scripting.md).
- If a required tool is missing, the first remediation step **MUST** be to update `.mise.toml` or run `mise install`, not to install ad-hoc global tools with language-specific installers such as `go install`, `npm install -g`, `pip install --user`, or `cargo install`.
- Root and module `Makefile` targets **MUST** work when invoked as plain `make <target>` after `make setup`.

*Why:* Eliminates "works on my machine" build failures by ensuring identical tool versions across all environments.

#### 07-root-readme

The root `README.md` **MUST** include: overview, machine setup, quickstart, and a repository map.

#### 08-root-gitignore

The repository root **MUST** ignore `dist/` and `.cache/` so module artifacts and tool caches are never committed accidentally.

#### 09-git-tagging-and-artifact-versioning

All releases **MUST** be tagged using the format `<module-name>/<semver>` (e.g., `graphvisualizer/renderer/1.0.0`, `shared/libs/mylib/2.1.0`).

`<module-name>` is preferably the path-like identifier of the module being released. A custom name is allowed but the folder name is strongly preferred.

*Why:* Namespacing tags by module prevents collisions and makes it easy to filter release history when multiple modules release independently.

---

#### 11-summary-of-requirements

| Requirement | Scope | Mandatory |
|---|---|---|
| Lowercase folder/file names | All | Yes |
| `README.md` per application | Application folders | Yes |
| `README.md` per module | Module folders | Yes |
| `Makefile` with `all`, `build`, `lint`, `test`, `clean` | Root, applications, modules | Yes |
| Root `Makefile` with `setup` target | Repository root | Yes |
| Root `README.md` with setup + quickstart | Repository root | Yes |
| Ignore `dist/` and `.cache/` | Repository root | Yes |
| Mise `.mise.toml` at root | Repository root | Yes |
| Applications depend only on `/shared/` | Application folders | Yes |
| Modules depend only on siblings or `/shared/` | Module folders | Yes |
| Module outputs live in `dist/` | Module folders | Yes |
| Persistent caches live in `.cache/` | Repo or module folders | Yes |
| Git tags follow `<module-name>/<semver>` format | All modules | Yes |
