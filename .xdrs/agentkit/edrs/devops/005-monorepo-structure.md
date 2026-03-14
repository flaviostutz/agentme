# agentkit-edr-005: Monorepo structure

## Context and Problem Statement

Without a defined monorepo layout, teams independently organize projects in ways that are inconsistent, hard to navigate, and difficult to build uniformly. Shared code gets duplicated, tooling varies per project, and onboarding new contributors is slow because there is no standard entry point or build convention.

What monorepo structure, naming conventions, tooling, and build standards should be followed to keep multiple projects cohesive, discoverable, and easy to build?

## Decision Outcome

**Adopt a standardized monorepo layout with top-level application folders, a shared library area, Mise-managed tooling, and Makefiles at every level so any contributor can build, lint, and test any part of the monorepo with a single, predictable command.**

For step-by-step scaffolding instructions see [skill 002-monorepo-setup](skills/002-monorepo-setup/SKILL.md).

### Policies

#### 1. Top-level directory layout

```
/
├── shared/               # Resources shared across ALL applications
│   ├── libs/             # Reusable libraries consumed by applications
│   └── scripts/          # Build/CI/dev scripts used across applications
│
├── <application>/        # One folder per application or project
│   ├── README.md         # REQUIRED
│   ├── <module>/         # One folder per compilable module
│   └── shared/           # Resources shared by modules within THIS application
│
├── Makefile              # Root Makefile coordinating all areas
├── README.md             # REQUIRED — onboarding and quickstart guide
└── .mise.toml            # Mise tool version configuration
```

#### 2. Application folders

- Represent a cohesive unit with its own lifecycle (e.g., `mymobileapp`, `graph-visualizer`).
- **MUST** depend only on resources in `/shared/`. Direct cross-application dependencies are forbidden; use published artifacts (container images, published libraries) instead.
- **MUST** contain a `README.md` with: purpose, architecture overview, how to build, and how to run.

*Why:* Isolating applications prevents implicit coupling and makes the `shared/` boundary explicit and intentional.

#### 3. Module folders

- A module is a subfolder inside an application that is independently compilable and produces a build artifact.
- May depend on sibling modules within the same application or on `/shared/` resources.
- **MUST NOT** depend on modules from other applications.

#### 4. Naming conventions

- All folder and file names **MUST** be **lowercase**.
- Use hyphens (`-`) to separate words (e.g., `data-loader`, `graph-visualizer`).
- Avoid abbreviations unless universally understood in the domain (e.g., `cli`, `api`).

#### 5. Makefiles at every level

A `Makefile` **MUST** be present at the repository root, in every application folder, and in every module folder.

Each Makefile **MUST** define at minimum: `build`, `lint`, and `test` targets.

The root `Makefile` **MUST** also define a `setup` target that guides a new contributor to prepare their machine.

*Why:* Makefiles provide a universal, stack-agnostic entry point regardless of programming language.

#### 6. Mise for tooling management

- [Mise](https://mise.jdx.dev/) **MUST** be used to pin all tool versions (compilers, runtimes, CLI tools).
- A `.mise.toml` **MUST** exist at the repository root.
- Contributors run `mise install` once after cloning.

*Why:* Eliminates "works on my machine" build failures by ensuring identical tool versions across all environments.

#### 7. Root README

The root `README.md` **MUST** include: overview, machine setup, quickstart, and a repository map.

#### 8. Git tagging and artifact versioning

All releases **MUST** be tagged using the format `<module-name>/<semver>` (e.g., `graphvisualizer/renderer/1.0.0`, `shared/libs/mylib/2.1.0`).

`<module-name>` is preferably the path-like identifier of the module being released. A custom name is allowed but the folder name is strongly preferred.

*Why:* Namespacing tags by module prevents collisions and makes it easy to filter release history when multiple modules release independently.

---

#### 11. Summary of requirements

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
| Git tags follow `<module-name>/<semver>` format | All modules | Yes |
