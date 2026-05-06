---
name: agentme-edr-014-python-project-tooling-and-structure
description: Defines the standard Python project toolchain, layout, and Makefile workflow using Mise, uv, ruff, pyright, pytest, and pip-audit. Use when scaffolding or reviewing Python projects.
---

# agentme-edr-014: Python project tooling and structure

## Context and Problem Statement

Python projects often drift into mixed dependency managers, duplicated configuration files, and ad hoc quality checks, which makes onboarding and CI pipelines inconsistent.

What tooling and project structure should Python projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Python and uv toolchain with `pyproject.toml`, `ruff`, `pyright`, `pytest`, `pytest-cov`, `pip-audit`, and a layout that follows [agentme-edr-016](../principles/016-cross-language-module-structure.md): a module root under `lib/`, runnable consumer examples in sibling `examples/`, and standardized `dist/` and `.cache/` locations.**

A single dependency manager, isolated package internals under `lib/`, and a standard Makefile contract keep Python projects predictable for contributors and CI while keeping the repository root clean.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Mandatory tool version management and command runner for Python, uv, and project CLIs |
| **uv** | Dependency management, lockfile management, virtualenv sync, build, publish |
| **pyproject.toml** | Single source of truth for package metadata and tool configuration |
| **ruff** | Formatting, import sorting, linting, and common code-quality checks |
| **pyright** | Static type checking |
| **pytest** | Test runner |
| **pytest-cov** | Coverage reporting and threshold enforcement |
| **pip-audit** | Dependency CVE audit |

All routine commands must run through the project `Makefile`, never by calling `uv`, `ruff`, `pytest`, or `pyright` directly in docs, CI, or daily development workflows.

The repository root MUST define a `.mise.toml` that pins Python and uv. Contributors and CI MUST bootstrap with `make setup` or `mise install`, then invoke routine work with `make <target>`. Each Makefile recipe MUST execute the underlying tool through `mise exec -- <tool> ...`, following [agentme-edr-017](../devops/017-tool-execution-and-scripting.md). Using routine project CLI commands directly outside the Makefile contract is not allowed.

The root `.venv/` is the canonical environment location for both the library and all examples. Subdirectory commands must set `UV_PROJECT_ENVIRONMENT` to the workspace root `.venv/` instead of creating nested virtual environments.

Persistent caches must live under `.cache/`, preferably the module `lib/.cache/` plus a shared root `.cache/uv/` when uv cache sharing is desired.

#### Project structure

```text
/
├── .mise.toml              # required; pins Python and uv
├── .gitignore
├── .cache/                 # optional shared uv cache at repo level
├── .venv/                  # shared uv environment for lib/ and examples/
├── Makefile                # root entry point; delegates to lib/ and runs examples/
├── README.md               # workspace/repository overview
├── lib/                    # everything the published library needs
│   ├── Makefile            # build, lint, test, publish targets for the library
│   ├── pyproject.toml      # package metadata + tool config
│   ├── uv.lock             # committed lockfile for the library
│   ├── README.md           # package README used for publishing
│   ├── .cache/             # pytest, Ruff, coverage, Python bytecode cache
│   ├── src/
│   │   └── <package_name>/
│   │       ├── __init__.py
│   │       ├── __main__.py # when the project exposes a CLI
│   │       └── ...
│   ├── tests/
│   │   ├── conftest.py     # shared fixtures when needed
│   │   └── test_*.py
│   ├── tests_integration/  # optional integration tests for this module
│   ├── tests_benchmark/    # optional benchmark harnesses and datasets
│   └── dist/               # wheels / sdists built from lib/
└── examples/               # independent consumer projects
    ├── example1/
    │   ├── pyproject.toml
    │   └── main.py
    └── example2/
        ├── pyproject.toml
        └── main.py
```

Keep the repository root clean: source code, tests, distribution artifacts, and package metadata live under `lib/`, while the root contains only orchestration and repository-level files.

Use the `lib/src/` layout for import safety and packaging clarity. Keep tests under `lib/tests/` and shared test setup in `lib/tests/conftest.py`. Do not introduce `requirements.txt`, `setup.py`, `setup.cfg`, `tox.ini`, `ruff.toml`, or `pyrightconfig.json` by default; keep project metadata and tool configuration in `lib/pyproject.toml`.

Libraries and shared utilities must include an `examples/` folder and wire example execution into the root `test` flow, following [agentme-edr-007](../principles/007-project-quality-standards.md). Each example directory is its own Python project with its own `pyproject.toml`, and examples must import the library as a consumer would rather than reaching back into `lib/src/` with relative imports. Local example verification must install the wheel built into `lib/dist/`; do not use editable or path-based dependencies back to `lib/`.

Python keeps unit tests under `lib/tests/` by default because that remains the more common and maintainable convention for typed/package-based projects than co-locating tests beside every source file. Integration tests belong in `lib/tests_integration/`, and benchmark harnesses belong in `lib/tests_benchmark/` when they are more than a single micro-benchmark helper.

#### `lib/pyproject.toml`

- Runtime dependencies belong in `[project.dependencies]`.
- Development-only tooling belongs in `[dependency-groups].dev`.
- Configure Ruff, Pyright, and Pytest in `lib/pyproject.toml` under their `tool.*` sections.
- Commit `lib/uv.lock` and keep it in sync with `lib/pyproject.toml`.
- Expose CLI entry points with `[project.scripts]` when the project provides commands.

When Pyright runs from `lib/`, configure it to discover the shared root virtual environment, for example with `venvPath = ".."` and `venv = ".venv"`.

Ruff is the default formatter and linter. Do not add Black, isort, or Flake8 unless another XDR for that repository explicitly requires them.

Pyright must run on every lint pass. `typeCheckingMode = "standard"` is the minimum baseline; projects may raise this to `strict` when the codebase is ready.

Pytest coverage must fail below 80% line and branch coverage, following [agentme-edr-004](../principles/004-unit-test-requirements.md).

#### Makefile targets

Contributors and CI MUST invoke the commands below as `make <target>`. The Makefile recipes themselves MUST call the underlying tools through `mise exec -- <tool> ...`.

#### Root `Makefile`

The root `Makefile` is the only contract for CI and contributors. It delegates library work to `lib/` and runs each example project in `examples/` against the shared root `.venv/`.

| Target | Description |
|--------|-------------|
| `setup` | Run `mise install`, then `lib/install` to create or update the shared root `.venv/` |
| `install` | Run `lib/install` to create or update the shared root `.venv/` |
| `build` | Run `lib/build` |
| `lint` | Run `lib/lint` |
| `lint-fix` | Run `lib/lint-fix` |
| `test-unit` | Run `lib/test-unit` |
| `test-examples` | For each `examples/*/pyproject.toml`, sync and run the example serially against the shared root `.venv/` |
| `test` | Run `test-unit`, then `test-examples` when applicable |
| `clean` | Remove the shared root `.venv/`, root `.cache/`, and delegate cleanup to `lib/` |
| `all` | `build lint test` |

#### `lib/Makefile`

| Target | Description |
|--------|-------------|
| `install` | `mise exec -- uv sync --project . --frozen --all-extras --dev` using the shared root `.venv/` |
| `build` | `mise exec -- uv sync --project . --frozen --all-extras --dev && mise exec -- uv build --project . --out-dir dist` |
| `lint` | `mise exec -- uv run --project . ruff format --check . && mise exec -- uv run --project . ruff check . && mise exec -- uv run --project . pyright && mise exec -- uv run --project . pip-audit`, with caches redirected into `.cache/` |
| `lint-fix` | `mise exec -- uv run --project . ruff format . && mise exec -- uv run --project . ruff check . --fix && mise exec -- uv run --project . pyright && mise exec -- uv run --project . pip-audit`, with caches redirected into `.cache/` |
| `test-unit` | `mise exec -- uv run --project . pytest --cov=src/<package_name> --cov-branch --cov-report=term-missing --cov-fail-under=80`, with pytest and coverage outputs stored under `.cache/` |
| `clean` | Remove `dist/` and `.cache/` inside `lib/` |
| `all` | `build lint test-unit` |
| `update-lockfile` | `mise exec -- uv lock --project . --upgrade` |
| `run` | `mise exec -- uv run --project . python -m <package_name>` or the project CLI entry point |
| `dev` | Same as `run`, optionally with repository-specific dev defaults |
| `publish` | `mise exec -- uv publish --project .` after versioning and packaging are complete |

The root `Makefile` must remain the only contract for CI and contributors, in line with [agentme-edr-008](../devops/008-common-targets.md).

## Considered Options

* (REJECTED) **Mixed Python tooling** - Separate tools and config files such as `pip`, `requirements.txt`, `setup.cfg`, `flake8`, and `mypy`.
  * Reason: Increases cognitive load, duplicates configuration, and weakens the standard command surface across projects.
* (CHOSEN) **uv + `lib/` package layout + Ruff/Pyright/Pytest toolchain** - One dependency manager, package internals isolated under `lib/`, consumer examples under `examples/`, and one root Makefile contract.
  * Reason: Keeps packaging, dependency locking, static analysis, security auditing, and test execution consistent while aligning Python repositories with the established JavaScript layout.

## References

- [agentme-edr-004](../principles/004-unit-test-requirements.md) - Coverage and unit-test baseline
- [agentme-edr-007](../principles/007-project-quality-standards.md) - Examples and quality requirements
- [agentme-edr-008](../devops/008-common-targets.md) - Standard Makefile target names
- [005-create-python-project](skills/005-create-python-project/SKILL.md) - Scaffold a project following this EDR
