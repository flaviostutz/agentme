---
name: agentme-edr-policy-103-python-project-tooling-and-structure
description: Defines the standard Python project toolchain, layout, and Makefile workflow using Mise, uv, ruff, ty, pytest, and pip-audit. Use when scaffolding or reviewing Python projects.
apply-to: Python projects
valid-from: 2026-05-25
---

# agentme-edr-policy-103: Python project tooling and structure

## Context and Problem Statement

Python projects often drift into mixed dependency managers, duplicated configuration files, and ad hoc quality checks, which makes onboarding and CI pipelines inconsistent.

What tooling and project structure should Python projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Python and uv toolchain with `pyproject.toml`, `ruff`, `ty`, `pytest`, `pytest-cov`, `pip-audit`, and a layout that follows [agentme-edr-016](../principles/016-cross-language-module-structure.md): a module root under `lib/`, runnable consumer examples in sibling `examples/`, and standardized `dist/` and `.cache/` locations.**

A single dependency manager, isolated package internals under `lib/`, and a standard Makefile contract keep Python projects predictable for contributors and CI while keeping the repository root clean.

### Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Mandatory tool version management and command runner for Python, uv, and project CLIs |
| **uv** | Dependency management, lockfile management, virtualenv sync, build, publish |
| **pyproject.toml** | Single source of truth for package metadata and tool configuration |
| **ruff** | Formatting, import sorting, linting, and common code-quality checks |
| **ty** | Static type checking |
| **pytest** | Test runner |
| **pytest-cov** | Coverage reporting and threshold enforcement |
| **pip-audit** | Dependency CVE audit |

All routine commands MUST run through the project `Makefile`. MUST NOT call `uv`, `ruff`, `pytest`, or `ty` directly in docs, CI, or daily development workflows.

The repository root MUST define a `.mise.toml` that pins Python and uv. Contributors and CI MUST bootstrap with `make setup` or `mise install`, then invoke routine work with `make <target>`. Each Makefile recipe MUST execute the underlying tool through `mise exec -- <tool> ...`, following [agentme-edr-304](../platform/304-tool-execution-and-scripting.md). Using routine project CLI commands directly outside the Makefile contract is not allowed.

The root `.venv/` is the canonical environment location for both the library and all examples. Subdirectory commands MUST set `UV_PROJECT_ENVIRONMENT` to the workspace root `.venv/` instead of creating nested virtual environments.

All tool caches, incremental state files, and workspace-local outputs MUST be written under `.cache/`. Cache paths MUST be declared in the tool's own configuration file — MUST NOT be on the command line or as Makefile CLI flags — so the location is enforced regardless of how the tool is invoked. Configure the following in `lib/pyproject.toml`:

| Tool | Config section | Setting | Value |
|------|---------------|---------|-------|
| **Ruff** | `[tool.ruff]` | `cache-dir` | `".cache/ruff"` |
| **pytest** | `[tool.pytest.ini_options]` | `cache_dir` | `".cache/pytest"` |
| **coverage** | `[tool.coverage.run]` | `data_file` | `".cache/.coverage"` |
| **coverage HTML** | `[tool.coverage.html]` | `directory` | `".cache/coverage-html"` |
| **uv** | `[tool.uv]` in `lib/pyproject.toml` | `cache-dir` | `".cache/uv"` |

Tools MUST NOT write cache or state files to the project root, `src/`, `tests/`, or any directory outside `.cache/`. Passing cache paths as CLI flags or Makefile recipe-level env overrides instead of `pyproject.toml` settings is not allowed.

#### Project structure

```text
/
├── .mise.toml              # required; pins Python and uv
├── .gitignore              # MUST ignore .venv/, dist/, .cache/, __pycache__/
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
│   │       ├── adapters/       # I/O boundary layer (following agentme-edr-126)
│   │       │   ├── cli/        # inbound: CLI bootstrap and entry point
│   │       │   ├── http/       # inbound: HTTP server bootstrap
│   │       │   └── connectors/ # outbound: one folder per external resource
│   │       ├── app/            # core business logic
│   │       └── shared/         # infrastructure-agnostic utilities
│   ├── tests/
│   │   ├── conftest.py     # shared fixtures when needed
│   │   └── *_test.py       # e.g. hello_test.py (named after the tested file)
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

Use the `lib/src/` layout for import safety and packaging clarity. Keep tests under `lib/tests/` and shared test setup in `lib/tests/conftest.py`. Do not introduce `requirements.txt`, `setup.py`, `setup.cfg`, `tox.ini`, `ruff.toml`, or `ty.toml` by default; keep project metadata and tool configuration in `lib/pyproject.toml`.

Internal source code MUST be organized following [agentme-edr-126](126-pragmatic-hexagonal-architecture.md): `adapters/` (inbound and outbound I/O boundaries), `app/` (business logic), and `shared/` (infrastructure-agnostic utilities).

Libraries and shared utilities MUST include an `examples/` folder and wire example execution into the root `test` flow, following [agentme-edr-501](../governance/501-project-quality-standards.md). Each example directory is its own Python project with its own `pyproject.toml`, and examples MUST import the library as a consumer would rather than reaching back into `lib/src/` with relative imports. Local example verification MUST install the wheel built into `lib/dist/`; do not use editable or path-based dependencies back to `lib/`.

Python keeps unit tests under `lib/tests/` by default because that remains the more common and maintainable convention for typed/package-based projects than co-locating tests beside every source file. Integration tests belong in `lib/tests_integration/`, and benchmark harnesses belong in `lib/tests_benchmark/` when they are more than a single micro-benchmark helper.

#### `lib/pyproject.toml`

- Runtime dependencies belong in `[project.dependencies]`.
- Development-only tooling belongs in `[dependency-groups].dev`.
- Configure Ruff, ty, and Pytest in `lib/pyproject.toml` under their `tool.*` sections.
- Commit `lib/uv.lock` and keep it in sync with `lib/pyproject.toml`.
- Expose CLI entry points with `[project.scripts]` when the project provides commands.

When ty runs from `lib/`, it auto-discovers the virtual environment via the `VIRTUAL_ENV` environment variable or the `UV_PROJECT_ENVIRONMENT` export set in the Makefile. No additional venv configuration is required in `pyproject.toml`.

Ruff is the default formatter and linter. Do not add Black, isort, or Flake8 unless another XDR for that repository explicitly requires them.

All Python projects MUST configure the following sections in `lib/pyproject.toml`. The cache-related settings are mandatory per the `.cache/` policy above:

```toml
[tool.pytest.ini_options]
cache_dir = ".cache/pytest"
python_files = "*_test.py"

[tool.coverage.run]
data_file = ".cache/.coverage"

[tool.coverage.html]
directory = ".cache/coverage-html"

[tool.uv]
cache-dir = ".cache/uv"

[tool.ruff]
cache-dir = ".cache/ruff"
output-format = "grouped"
line-length = 120
target-version = "py311"
src = ["src", "tests", "tests_integration"]

[tool.ruff.format]
docstring-code-format = true
line-ending = "lf"

[tool.ruff.lint]
task-tags = ["TODO"]
select = ["ERA", "FAST", "ANN", "ASYNC", "S", "BLE", "FBT", "B", "A", "COM",
  "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FIX", "INT", "ISC", "ICN", "LOG", "G",
  "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SIM", "SLOT", "TID",
  "TC", "ARG", "PTH", "FLY", "I", "C90", "NPY", "PD", "N", "PERF", "E", "W",
  "D", "F", "PGH", "PL", "UP", "FURB", "RUF", "TRY"]
ignore = ["ANN002", "ANN003", "ANN401", "D100", "D101", "D102", "D103", "D104",
  "D105", "D106", "D107", "COM812", "D203", "D213", "D400", "D401", "D404", "D415", "FIX002"]

[tool.ruff.lint.pycodestyle]
ignore-overlong-task-comments = true
```

Adjust `target-version` to match the project's minimum supported Python version. The `cache-dir` keeps Ruff's cache under `.cache/ruff` alongside other tool caches. The `src` list MUST include every directory that contains importable Python code. The `select` list enables a broad set of rules covering style, correctness, performance, security, and documentation. The `ignore` list suppresses rules that are either too noisy or conflict with the chosen docstring style.

ty MUST run on every lint pass. The default rule set is the minimum baseline; projects may enable stricter rules as the codebase matures.

Pytest coverage MUST fail below 80% line and branch coverage, following [agentme-edr-122](122-unit-test-requirements.md).

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
| `lint` | `mise exec -- uv run --project . ruff format --check . && mise exec -- uv run --project . ruff check . && mise exec -- uv run --project . ty check && mise exec -- uv run --project . pip-audit`, with caches redirected into `.cache/` |
| `lint-fix` | `mise exec -- uv run --project . ruff format . && mise exec -- uv run --project . ruff check . --fix && mise exec -- uv run --project . ty check && mise exec -- uv run --project . pip-audit`, with caches redirected into `.cache/` |
| `test-unit` | `mise exec -- uv run --project . pytest --cov=src/<package_name> --cov-branch --cov-report=term-missing --cov-fail-under=80`, with pytest and coverage outputs stored under `.cache/` |
| `clean` | Remove `dist/` and `.cache/` inside `lib/` |
| `all` | `build lint test-unit` |
| `update-lockfile` | `mise exec -- uv lock --project . --upgrade` |
| `run` | `mise exec -- uv run --project . python -m <package_name>` or the project CLI entry point |
| `dev` | Same as `run`, optionally with repository-specific dev defaults |
| `publish` | `mise exec -- uv publish --project .` after versioning and packaging are complete |

The root `Makefile` MUST remain the only contract for CI and contributors, in line with [agentme-edr-303](../platform/303-common-targets.md).

## Considered Options

* (REJECTED) **Mixed Python tooling** - Separate tools and config files such as `pip`, `requirements.txt`, `setup.cfg`, `flake8`, and `mypy`.
  * Reason: Increases cognitive load, duplicates configuration, and weakens the standard command surface across projects.
* (CHOSEN) **uv + `lib/` package layout + Ruff/ty/Pytest toolchain** - One dependency manager, package internals isolated under `lib/`, consumer examples under `examples/`, and one root Makefile contract.
  * Reason: Keeps packaging, dependency locking, static analysis, security auditing, and test execution consistent while aligning Python repositories with the established JavaScript layout.

## References

- [agentme-edr-122](122-unit-test-requirements.md) - Coverage and unit-test baseline
- [agentme-edr-501](../governance/501-project-quality-standards.md) - Examples and quality requirements
- [agentme-edr-303](../platform/303-common-targets.md) - Standard Makefile target names
- [005-create-python-project](skills/005-create-python-project/SKILL.md) - Scaffold a project following this EDR
