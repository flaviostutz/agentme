# agentme-edr-014: Python project tooling and structure

## Context and Problem Statement

Python projects often drift into mixed dependency managers, duplicated configuration files, and ad hoc quality checks, which makes onboarding and CI pipelines inconsistent.

What tooling and project structure should Python projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a uv-managed Python project with `pyproject.toml`, `ruff`, `pyright`, `pytest`, `pytest-cov`, `pip-audit`, and a Makefile as the only development entry point.**

A single dependency manager, one canonical config file, and standard targets keep Python projects predictable for contributors and CI.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **uv** | Dependency management, lockfile management, virtualenv sync, build, publish |
| **pyproject.toml** | Single source of truth for package metadata and tool configuration |
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

Use the `src/` layout for import safety and packaging clarity. Keep tests under `tests/` and shared test setup in `tests/conftest.py`. Do not introduce `requirements.txt`, `setup.py`, `setup.cfg`, `tox.ini`, `ruff.toml`, or `pyrightconfig.json` by default; keep project metadata and tool configuration in `pyproject.toml`.

Libraries and shared utilities must include an `examples/` folder and wire example execution into the root `test` flow, following [agentme-edr-007](../principles/007-project-quality-standards.md).

#### `pyproject.toml`

- Runtime dependencies belong in `[project.dependencies]`.
- Development-only tooling belongs in `[dependency-groups].dev`.
- Configure Ruff, Pyright, and Pytest in `pyproject.toml` under their `tool.*` sections.
- Commit `uv.lock` and keep it in sync with `pyproject.toml`.
- Expose CLI entry points with `[project.scripts]` when the project provides commands.

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
* (CHOSEN) **uv + `pyproject.toml` + Ruff/Pyright/Pytest toolchain** - One dependency manager, one config file, and one Makefile entry point.
  * Reason: Keeps packaging, dependency locking, static analysis, security auditing, and test execution consistent.

## References

- [agentme-edr-004](../principles/004-unit-test-requirements.md) - Coverage and unit-test baseline
- [agentme-edr-007](../principles/007-project-quality-standards.md) - Examples and quality requirements
- [agentme-edr-008](../devops/008-common-targets.md) - Standard Makefile target names
- [005-create-python-project](skills/005-create-python-project/SKILL.md) - Scaffold a project following this EDR
