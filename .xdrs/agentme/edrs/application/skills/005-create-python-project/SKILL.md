---
name: 005-create-python-project
description: >
  Scaffolds the initial boilerplate structure for a Python library or CLI project following the
  standard tooling and layout defined in agentme-edr-014. Activate this skill when the user asks
  to create, scaffold, or initialize a new Python package, CLI, library, or similar project
  structure.
metadata:
  author: flaviostutz
  version: "1.0"
compatibility: Python 3.12+
---

## Overview

Creates a complete Python project from scratch using `uv`, `pyproject.toml`, `ruff.toml`, Ruff, Pyright,
Pytest, and Makefiles. The default layout uses `src/<package_name>/`, `tests/`, and `examples/`
for libraries and shared utilities.

Related EDR: [agentme-edr-014](../../014-python-project-tooling.md)

## Instructions

### Phase 1: Gather information

Ask for or infer from context:

- **Package name** - Python distribution/import name, e.g. `my_tool`
- **Short description** - one sentence
- **Author** name or GitHub username
- **Python version** - default `3.13`
- **Project kind** - `library` or `cli`
- **Primary entry point** - first module or command name to scaffold
- **GitHub repo URL** - optional, for project metadata
- **Confirm target directory** - default: current workspace root

### Phase 2: Create root files

Create these files first.

**`./Makefile`**

```makefile
SHELL := /bin/bash

PACKAGE_NAME ?= your_package
MISE := mise exec --

all: build lint test

install:
	uv sync --frozen --all-extras --dev

build: install
	uv build

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run pyright
	uv run pip-audit

lint-fix:
	uv run ruff format .
	uv run ruff check . --fix
	uv run pyright
	uv run pip-audit

test: test-unit test-examples

test-unit:
	uv run pytest --cov=src/$(PACKAGE_NAME) --cov-branch --cov-report=term-missing --cov-fail-under=80

test-examples:
	@if [ -d examples ]; then $(MAKE) -C examples test PACKAGE_NAME=$(PACKAGE_NAME); else echo "No examples/ directory. Skipping"; fi

run:
	uv run python -m $(PACKAGE_NAME)

dev: run

update-lockfile:
	uv lock --upgrade

clean:
	rm -rf .venv dist .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

If the repository already uses Mise, adapt the commands to `$(MISE) uv ...` and pin both Python and uv in `.mise.toml`.

**`./pyproject.toml`**

Replace placeholders such as `[package-name]`, `[description]`, `[author]`, and `[python-version]`.

```toml
[project]
name = "[package-name]"
version = "0.0.1"
description = "[description]"
readme = "README.md"
requires-python = ">=[python-version]"
dependencies = []

[[project.authors]]
name = "[author]"

[project.optional-dependencies]
dev = []

[dependency-groups]
dev = [
  "pip-audit>=2.9.0",
  "pyright>=1.1.400",
  "pytest>=8.4.0",
  "pytest-cov>=6.1.0",
  "ruff>=0.11.0",
]

[build-system]
requires = ["hatchling>=1.27.0"]
build-backend = "hatchling.build"

[tool.pyright]
include = ["src", "tests"]
venvPath = "."
venv = ".venv"
typeCheckingMode = "standard"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

Use `pyproject.toml` for package metadata, Pyright, and Pytest configuration. Do not add
`requirements.txt`, `setup.py`, `setup.cfg`, or `pyrightconfig.json` by default.

**`./ruff.toml`**

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

**`./.gitignore`**

```gitignore
.venv/
dist/
build/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
__pycache__/
*.pyc
```

**`./README.md`**

Put Getting Started near the top.

```markdown
# [package-name]

[description]

## Getting Started

```sh
uv sync --dev
make test
```

```python
from [package-name] import hello

print(hello("world"))
```
```

### Phase 3: Create the package and tests

Create this baseline structure.

**`src/[package_name]/__init__.py`**

```python
from .core import hello

__all__ = ["hello"]
```

**`src/[package_name]/core.py`**

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

**`src/[package_name]/__main__.py`**

Use this only for CLI-oriented projects.

```python
from .core import hello


def main() -> None:
    print(hello("world"))


if __name__ == "__main__":
    main()
```

**`tests/test_core.py`**

```python
from [package_name].core import hello


def test_hello() -> None:
    assert hello("world") == "Hello, world!"
```

If two or more test files need shared fixtures, create `tests/conftest.py` and move shared setup there.

### Phase 4: Create examples for libraries and utilities

If the project is a library or shared utility, add an `examples/` directory and execute it from the root `test` target.

**`examples/Makefile`**

```makefile
test:
	$(MAKE) -C basic-usage run PACKAGE_NAME=$(PACKAGE_NAME)
```

**`examples/basic-usage/Makefile`**

```makefile
run:
	uv run python main.py
```

**`examples/basic-usage/main.py`**

```python
from [package_name] import hello


print(hello("world"))
```

Examples must import the built package as a consumer would. Avoid relative imports back into `src/`.

### Phase 5: Verify

After creating the files:

1. Run `uv lock`.
2. Run `make lint-fix`.
3. Run `make test`.
4. Run `make build`.
5. Fix all failures before finishing.

## Examples

**Input:** "Create a Python library called `event_tools`"
- Create `pyproject.toml`, `Makefile`, `src/event_tools/`, `tests/`, and `examples/`
- Configure `uv`, Ruff, Pyright, Pytest, `pytest-cov`, and `pip-audit`
- Verify with `make lint-fix`, `make test`, and `make build`

**Input:** "Scaffold a Python CLI package"
- Add `src/<package_name>/__main__.py`
- Add `[project.scripts]` in `pyproject.toml` when the command name must differ from the module name
- Keep the same Makefile and quality checks

## Edge Cases

- If the repository already has a root `.mise.toml`, pin Python and uv there instead of assuming host-installed tools.
- If the project is fewer than 100 lines and explicitly marked as a spike or experiment, examples and linting may be skipped only when another applicable XDR allows it.
- If the user asks for an app with framework-specific needs such as FastAPI or Django, keep this baseline and add the framework config on top instead of replacing it.

## References

- [agentme-edr-014](../../014-python-project-tooling.md)
- [_core-adr-003 - Skill standards](../../../../../_core/adrs/principles/003-skill-standards.md)
