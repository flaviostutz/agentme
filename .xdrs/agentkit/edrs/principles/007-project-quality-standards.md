# agentkit-edr-007: Project quality standards

## Context and Problem Statement

Without a baseline quality bar, projects within the same organization can diverge significantly in documentation completeness, test coverage, linting discipline, and structural clarity. New developers encounter confusion, quality regressions slip through, and standards drift over time.

What minimum quality standards must every project in the organization meet to ensure it is understandable, maintainable, and consistently verifiable?

## Decision Outcome

**Every project must meet six minimum quality standards: a Getting Started section in its README, unit tests that run on every release, compliance with workspace XDRs, active linting enforcement, a structure that is clear to new developers, and — for libraries and utilities — a runnable examples folder that is verified on every test run.**

These standards form a non-negotiable baseline. Individual projects may raise the bar further but must never fall below it.

### Implementation Details

#### 1. README MUST have a Getting Started section at the top

The `README.md` file **must** include a **Getting Started** section as the first section after the project title and optional one-line description. It must show the minimal steps required to install and use the project.

*Why:* The README is the first artifact a developer reads. An immediate, working example dramatically shortens the time-to-productivity and signals that the project is actively maintained.

**Required content in Getting Started:**
- Installation or setup command(s)
- At least one usage example (code snippet, CLI command, or API call) that a new developer can copy and run

**Required README structure:**

```markdown
# Project Name

One-line description of what the project does.

## Getting Started

```sh
npm install my-package
```

```ts
import { myFunction } from "my-package";
myFunction({ input: "value" });
```

## Other sections...
```

**Checklist:**
- [ ] `Getting Started` is the first `##`-level section in the README
- [ ] At least one runnable code or CLI snippet is present
- [ ] The snippet reflects the current public API (kept in sync with implementation)

---

#### 2. Unit tests MUST run on every release

Every project **must** have a unit test suite that is automatically executed as part of the release pipeline. Releases that fail the test suite **must not** be published or deployed.

*Why:* Tests only provide value if they are run. Gating releases on test results prevents regressions from reaching production and enforces accountability for code quality.

**Requirements:**
- A `make test` (or equivalent Makefile target) must exist and run the full unit test suite
- The CI/CD pipeline must invoke the test target before the publish/deploy step
- Test failures must block the release — they must never be skipped or overridden silently

**Reference:** See also [agentkit-edr-004](004-unit-test-requirements.md) for detailed unit test quality requirements (assertion rules, coverage thresholds, mock discipline).

---

#### 3. The project MUST comply with all applicable workspace XDRs

Every project **must** follow all XDRs that apply to its scope, as defined in [.xdrs/index.md](../../../../index.md). No implementation decision may knowingly contradict an applicable XDR without a documented override in a project-local XDR.

*Why:* XDRs encode organizational decisions. Ignoring them without documentation undermines consistency, makes cross-team collaboration harder, and erodes the value of the decision record system.

**Requirements:**
- Before starting any significant implementation, review the applicable XDRs
- If an XDR conflicts with a project's needs, create a `_local` XDR that documents the deviation and the reason
- AI coding agents must follow the instruction hierarchy defined in [_general-edr-001](../../_general/edrs/principles/001-coding-agent-behavior.md)

---

#### 4. The project MUST have linting enforcing code style, formatting, and best practices

Every project **must** have a linter configured and actively enforced. Linting must cover at minimum: code style, formatting, and language-specific best practices. Lint failures **must** block CI builds.

*Why:* Manual code review is insufficient for style and formatting consistency. Automated linting catches entire classes of issues instantly and removes subjective debate from code review.

**Requirements:**
- A `make lint` target must exist and run the linter with zero-warning tolerance (warnings treated as errors)
- A `make lint-fix` target should auto-fix fixable issues
- The linter must be configured via a checked-in config file (e.g., `.eslintrc.js`, `pyproject.toml`, `.golangci.yml`)
- CI must run `make lint` before merging or releasing

**Reference:** See [agentkit-edr-003](003-javascript-project-tooling.md) for JavaScript-specific tooling configuration.

---

#### 5. The project structure MUST be easily understood by new developers

The project's directory and file layout **must** be self-explanatory to a developer who has never worked on it before. Structure alone should make it obvious where to find source code, tests, configuration, and examples.

*Why:* A confusing structure increases onboarding time, causes files to be placed in wrong locations, and makes maintenance harder. A well-organized project respects contributors' time.

**Requirements:**
- Directory names must reflect their purpose (e.g., `src/`, `lib/`, `tests/`, `examples/`, `docs/`)
- The root README must describe the top-level directory layout if it is non-obvious
- There must be a clear separation between: source code, test files, configuration files, and runnable examples
- Test files must be co-located with or clearly associated with the source files they cover
- There must be no orphaned or unexplained directories or files at the project root

**Example of a clear top-level layout (TypeScript project):**

```
/
├── README.md          # project overview and Getting Started
├── Makefile           # single entry point for build, lint, test
├── lib/               # published library source and tests
│   └── src/
│       ├── index.ts
│       └── *.test.ts
└── examples/          # runnable usage examples
    └── basic-usage/
```

**Checklist:**
- [ ] A new developer can identify the entry point of the project within 60 seconds
- [ ] Source code, tests, and configuration are in clearly named directories
- [ ] The README describes the layout if top-level structure is non-obvious
- [ ] No unexplained files or directories exist at the project root

---

#### 6. Libraries and utilities MUST have a runnable examples folder verified on every test run

When the project is a **library** (published to a package registry) or a **utility** (a shared tool consumed by other projects), it **must** include an `examples/` directory at the project root. Each subdirectory under `examples/` represents a distinct usage scenario and must be independently runnable via its own `Makefile`.

The examples must be executed as part of the test suite so that they serve as living integration tests — ensuring the public API stays functional and the README snippets stay accurate.

*Why:* Unit tests verify internal logic but cannot catch breakage of the public API as seen by a real consumer. Runnable examples validate the full install-and-use path and are the fastest way for new developers to understand what the library actually does in practice.

**Requirements:**
- An `examples/` directory must exist at the project root with at least one subdirectory per major usage scenario
- Each example subdirectory must contain a `Makefile` with at minimum a `run` target that installs dependencies and executes the example
- The root `Makefile` must have a target (e.g., `make test-examples` or included in `make test`) that runs all examples in sequence
- Example execution must be part of the CI pipeline and must block releases on failure
- Example code must import and use the library as an external consumer would (not via relative `../src` imports) — this validates the published package interface

**Directory layout:**

```
/
├── Makefile              # includes: make test → runs lib tests + examples
├── lib/                  # library source
│   └── src/
└── examples/
    ├── Makefile          # runs all example subdirectories in sequence
    ├── basic-usage/      # scenario: simplest possible usage
    │   ├── Makefile      # targets: run
    │   └── main.ts
    └── advanced-usage/   # scenario: more complex configuration
        ├── Makefile      # targets: run
        └── main.ts
```

**Root Makefile integration example:**

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

**Checklist:**
- [ ] `examples/` directory exists with at least one scenario subdirectory
- [ ] Each scenario has a `Makefile` with a `run` target
- [ ] Examples install and consume the library as an external package, not via relative path imports
- [ ] `make test` (or equivalent) in the root runs all examples
- [ ] Example failures block CI and releases
- [ ] Each example scenario is named to reflect the use case it demonstrates

## Considered Options

* (REJECTED) **Heavy prescriptive standards** - Mandate every tool, directory name, and documentation section with exact templates
  * Reason: Over-specification creates friction for legitimate project-specific needs and becomes hard to maintain as technology evolves

* (CHOSEN) **Minimal, outcome-focused standards** - Define the five non-negotiable outcomes every project must achieve, letting implementation details vary by language/framework
  * Reason: Ensures consistency on the outcomes that matter most while preserving flexibility in how teams achieve them
