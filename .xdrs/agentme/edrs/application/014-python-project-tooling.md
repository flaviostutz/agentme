---
name: agentme-edr-014-python-project-tooling
description: Defines the standard Python project toolchain, layout, and Makefile workflow using uv, ruff, pyright, pytest, and pip-audit. Use when scaffolding or reviewing Python projects.
---

# agentme-edr-014: Python project tooling and structure

## Context and Problem Statement

Python projects often drift into mixed dependency managers, duplicated configuration files, and ad hoc quality checks, which makes onboarding and CI pipelines inconsistent.

What tooling and project structure should Python projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a uv-managed Python project with `pyproject.toml`, `ruff.toml`, `ruff`, `pyright`, `pytest`, `pytest-cov`, `pip-audit`, and a Makefile as the only development entry point.**

A single dependency manager, a canonical package config, a shared Ruff baseline, and standard targets keep Python projects predictable for contributors and CI.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **uv** | Dependency management, lockfile management, virtualenv sync, build, publish |
| **pyproject.toml** | Single source of truth for package metadata and non-Ruff tool configuration |
| **ruff.toml** | Canonical Ruff formatting and lint configuration |
| **ruff** | Formatting, import sorting, linting, and common code-quality checks |
| **pyright** | Static type checking |
| **pytest** | Test runner |
| **pytest-cov** | Coverage reporting and threshold enforcement |
| **pip-audit** | Dependency CVE audit |

All routine commands must run through the project `Makefile`, never by calling `uv`, `ruff`, `pytest`, or `pyright` directly in docs, CI, or daily development workflows.

When the repository defines a root `.mise.toml`, Python and uv must be pinned there and commands should run through `mise exec --` or an activated Mise shell.

#### Project structure

```text
/
├── .mise.toml              # optional but required when the repo uses Mise
├── Makefile                # single entry point for build/lint/test/run tasks
├── pyproject.toml          # package metadata + tool config
├── ruff.toml               # Ruff formatting + lint configuration
├── uv.lock                 # committed lockfile
├── README.md               # Getting Started near the top
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── __main__.py     # when the project exposes a CLI
│       └── ...
├── tests/
│   ├── conftest.py         # shared fixtures when needed
│   └── test_*.py
└── examples/               # required for libraries and shared utilities
    ├── Makefile
    └── basic-usage/
```

Use the `src/` layout for import safety and packaging clarity. Keep tests under `tests/` and shared test setup in `tests/conftest.py`. Do not introduce `requirements.txt`, `setup.py`, `setup.cfg`, `tox.ini`, or `pyrightconfig.json` by default. Keep package metadata, Pyright, and Pytest configuration in `pyproject.toml`, and keep Ruff configuration in `ruff.toml`.

Libraries and shared utilities must include an `examples/` folder and wire example execution into the root `test` flow, following [agentme-edr-007](../principles/007-project-quality-standards.md).

#### `pyproject.toml`

- Runtime dependencies belong in `[project.dependencies]`.
- Development-only tooling belongs in `[dependency-groups].dev`.
- Configure Pyright and Pytest in `pyproject.toml` under their `tool.*` sections.
- Configure Ruff in `ruff.toml` using the shared baseline below.
- Commit `uv.lock` and keep it in sync with `pyproject.toml`.
- Expose CLI entry points with `[project.scripts]` when the project provides commands.

#### `ruff.toml`

Use this Ruff baseline unless another applicable XDR overrides it.

```toml
cache-dir = ".ruff_cache"
output-format = "grouped"

line-length = 120
src = [".", "apps/*/services/*/src", "src/"]

[format]
docstring-code-format = true
line-ending = "lf"

[lint.pycodestyle]
ignore-overlong-task-comments = true # To allow longer TODO comments without raising E501

[lint]
task-tags = ["TODO"] # https://stackoverflow.com/a/79035357

select = ["ERA", "FAST", "ANN", "ASYNC", "S", "BLE", "FBT", "B", "A", "COM",
  "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FIX", "INT", "ISC", "ICN", "LOG", "G",
  "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SIM", "SLOT", "TID",
  "TC", "ARG", "PTH", "FLY", "I", "C90", "NPY", "PD", "N", "PERF", "E", "W",
  "D", "F", "PGH", "PL", "UP", "FURB", "RUF", "TRY"]
ignore = ["ANN002", "ANN003", "ANN401", "D100", "D101", "D102", "D103", "D104",
  "D105", "D106", "D107", "COM812", "D203", "D213", "D400", "D401", "D404", "D415", "FIX002"]


[lint.flake8-tidy-imports]
# Ban relative imports beyond immediate module
ban-relative-imports = "parents"

[lint.per-file-ignores]
"*/test_*.py" = ["S101", "ANN201", "ANN001", "PLR0913"]
"*/tests/*.py" = ["S101", "ANN201", "ANN001", "PLR0913", "INP001", "B017", "PT011"]
"scripts/*.py" = ["T20", "BLE001"]  # Allow prints in scripts
"*/tests/*" = ["INP001", "SLF001", "PLR2004"]
```

Ruff is the default formatter and linter. Do not add Black, isort, or Flake8 unless another XDR for that repository explicitly requires them.

Pyright must run on every lint pass. `typeCheckingMode = "standard"` is the minimum baseline; projects may raise this to `strict` when the codebase is ready.

Pytest coverage must fail below 80% line and branch coverage, following [agentme-edr-004](../principles/004-unit-test-requirements.md).

#### Makefile targets

The commands below assume invocation through `mise exec -- make <target>` when the repository uses Mise, or plain `make <target>` inside an activated project environment.

| Target | Description |
|--------|-------------|
| `install` | `uv sync --frozen --all-extras --dev` |
| `build` | `uv sync --frozen --all-extras --dev && uv build` |
| `lint` | `uv run ruff format --check . && uv run ruff check . && uv run pyright && uv run pip-audit` |
| `lint-fix` | `uv run ruff format . && uv run ruff check . --fix && uv run pyright && uv run pip-audit` |
| `test-unit` | `uv run pytest --cov=src/<package_name> --cov-branch --cov-report=term-missing --cov-fail-under=80` |
| `test-examples` | Run `examples/` through its own `Makefile` when the project is a library/utility |
| `test` | Run `test-unit`, then `test-examples` when applicable |
| `clean` | Remove `.venv/`, `dist/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/` |
| `all` | `build lint test` |
| `update-lockfile` | `uv lock --upgrade` |
| `run` | `uv run python -m <package_name>` or the project CLI entry point |
| `dev` | Same as `run`, optionally with repository-specific dev defaults |
| `publish` | `uv publish` after versioning and packaging are complete |

The root `Makefile` must remain the only contract for CI and contributors, in line with [agentme-edr-008](../devops/008-common-targets.md).

## Considered Options

* (REJECTED) **Mixed Python tooling** - Separate tools and config files such as `pip`, `requirements.txt`, `setup.cfg`, `flake8`, and `mypy`.
  * Reason: Increases cognitive load, duplicates configuration, and weakens the standard command surface across projects.
* (CHOSEN) **uv + `pyproject.toml` + `ruff.toml` + Ruff/Pyright/Pytest toolchain** - One dependency manager, a canonical package config, a shared Ruff baseline, and one Makefile entry point.
  * Reason: Keeps packaging, dependency locking, code style, static analysis, security auditing, and test execution consistent.

## References

- [agentme-edr-004](../principles/004-unit-test-requirements.md) - Coverage and unit-test baseline
- [agentme-edr-007](../principles/007-project-quality-standards.md) - Examples and quality requirements
- [agentme-edr-008](../devops/008-common-targets.md) - Standard Makefile target names
- [005-create-python-project](skills/005-create-python-project/SKILL.md) - Scaffold a project following this EDR
