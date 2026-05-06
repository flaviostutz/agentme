---
name: agentme-edr-007-project-quality-standards
description: Defines minimum project quality standards for README onboarding, testing, linting, XDR compliance, and runnable examples. Use when scaffolding or reviewing projects.
---

# agentme-edr-007: Project quality standards

## Context and Problem Statement

Without a baseline quality bar, projects within the same organization can diverge significantly in documentation completeness, test coverage, linting discipline, and structural clarity. New developers encounter confusion, quality regressions slip through, and standards drift over time.

What minimum quality standards must every project in the organization meet to ensure it is understandable, maintainable, and consistently verifiable?

## Decision Outcome

Every project must meet six minimum quality standards: a Getting Started section in its README, unit tests that run on every release, compliance with workspace XDRs, active linting enforcement, a structure that is clear to new developers, and — for libraries and utilities — a runnable examples folder verified on every test run.

These standards form a non-negotiable baseline. Individual projects may raise the bar but must never fall below it.

### Implementation Details

#### 01-readme-must-have-getting-started

`README.md` must include a **Getting Started** section in the first 20 lines with the minimal steps to install and use the project.

**Required content:**
- Installation or setup command(s)
- At least one runnable usage example (code snippet, CLI command, or API call)

**Required README structure:**

```markdown
# Project Name

One-line description.

## Getting Started

```sh
npm install my-package
```

```ts
import { myFunction } from "my-package";
myFunction({ input: "value" });
```
```

---

#### 02-unit-tests-must-run-on-every-release

A unit test suite must run automatically before every release. Failing tests must block the release — no silent skips or overrides.

**Requirements:**
- A `make test` target must exist and run the full suite
- CI/CD must invoke it before publish/deploy
- Test failures block the release

**Exception:** Projects with fewer than 100 lines of code, or whose `README.md` prominently marks them as a **Spike** or **Experiment**, are exempt from this requirement. Such projects must never be deployed to production.

**Reference:** [agentme-edr-004](004-unit-test-requirements.md) for detailed unit test requirements.

---

#### 03-project-must-comply-with-xdrs

All XDRs that apply to the project's scope (as listed in [.xdrs/index.md](../../../index.md)) must be followed. A deviation requires a project-local XDR documenting the override.

**Requirements:**
- Review applicable XDRs before any significant implementation
- If an XDR conflicts with project needs, create a `_local` XDR documenting the deviation

---

#### 04-project-must-have-linting

Projects larger than 10 files or 200 lines of code must have a linter configured and actively enforced. Lint failures block CI builds.

**Requirements:**
- `make lint` runs the linter with zero-warning tolerance
- `make lint-fix` auto-fixes fixable issues
- Linter config is checked in (e.g., `.eslintrc.js`, `pyproject.toml`, `.golangci.yml`)
- CI runs `make lint` before merging or releasing

**Exception:** Projects with fewer than 100 lines of code, or whose `README.md` prominently marks them as a **Spike** or **Experiment**, are exempt from this requirement. Such projects must never be deployed to production.

**Reference:** [agentme-edr-003](../application/003-javascript-project-tooling.md) for JavaScript-specific tooling.

---

#### 05-project-structure-must-be-clear

Directory and file layout must be self-explanatory: source code, tests, configuration, and examples must be clearly separated and named.

**Requirements:**
- Directory names must reflect their purpose (`src/`, `lib/`, `tests/`, `examples/`, `docs/`)
- README must describe the top-level layout if non-obvious
- No orphaned or unexplained directories or files at the project root

**Example layout (TypeScript project):**

```
/
├── README.md
├── Makefile
├── lib/
│   └── src/
│       ├── index.ts
│       └── *.test.ts
└── examples/
    └── basic-usage/
```

---

#### 06-libraries-must-have-runnable-examples

Projects that are libraries or shared utilities must include an `examples/` directory. Each subdirectory represents a usage scenario and must be independently runnable. Examples are executed as part of `make test`.

**Requirements:**
- `examples/` must contain at least one subdirectory per major usage scenario
- Each scenario subdirectory must have a `Makefile` with a `run` target
- Examples must import the library as an external consumer (not via relative `../src` imports)
- `make test` in the root must run all examples; failures block CI and releases

**Directory layout:**

```
/
├── Makefile
├── lib/src/
└── examples/
    ├── Makefile
    ├── basic-usage/
    │   ├── Makefile      # targets: run
    │   └── main.ts
    └── advanced-usage/
        ├── Makefile      # targets: run
        └── main.ts
```

**Root Makefile:**

```makefile
test: test-unit test-examples

test-unit:
	$(MAKE) -C lib test

test-examples:
	$(MAKE) -C examples
```

**Examples Makefile:**

```makefile
all:
	$(MAKE) -C basic-usage run
	$(MAKE) -C advanced-usage run
```
