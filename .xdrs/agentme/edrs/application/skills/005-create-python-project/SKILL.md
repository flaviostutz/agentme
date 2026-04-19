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

Creates a complete Python project from scratch using `uv`, `pyproject.toml`, Ruff, Pyright,
Pytest, and Makefiles. The default layout keeps the library self-contained under `lib/`, uses a
shared root `.venv/`, and places runnable consumer projects under `examples/`.

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
ROOT_DIR := $(abspath .)
export UV_PROJECT_ENVIRONMENT := $(ROOT_DIR)/.venv

all: build lint test

install:
	$(MAKE) -C lib install

build:
	$(MAKE) -C lib build

lint:
	$(MAKE) -C lib lint

lint-fix:
	$(MAKE) -C lib lint-fix

test: test-unit test-examples

test-unit:
	$(MAKE) -C lib test-unit

test-examples: build
	@for dir in examples/*; do \
		if [ -f "$$dir/pyproject.toml" ]; then \
			echo ">>> Running $$dir"; \
			UV_PROJECT_ENVIRONMENT="$(UV_PROJECT_ENVIRONMENT)" uv sync --project "$$dir" --frozen || exit 1; \
			UV_PROJECT_ENVIRONMENT="$(UV_PROJECT_ENVIRONMENT)" uv run --project "$$dir" python main.py || exit 1; \
		fi; \
	done

clean:
	$(MAKE) -C lib clean
	rm -rf .venv
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

The root `Makefile` keeps the repository clean by delegating package work to `lib/` and treating each example directory as an independent consumer project.

If the repository already uses Mise, wrap the delegated commands with `mise exec --` and pin both Python and uv in `.mise.toml`.

**`./.gitignore`**

```gitignore
.venv/
lib/dist/
lib/.pytest_cache/
lib/.ruff_cache/
lib/.coverage
lib/htmlcov/
__pycache__/
*.pyc
```

**`./README.md`**

Keep this README focused on the repository or workspace. Put Getting Started near the top.

````markdown
# [package-name]

[description]

## Getting Started

```sh
make test
```

The published package lives in `lib/` and runnable consumer examples live in `examples/`.
````

### Phase 3: Create `lib/`

`lib/` contains everything the library needs: source, tests, package metadata, lockfile, build
artifacts, and library-specific Makefile targets.

**`lib/Makefile`**

```makefile
SHELL := /bin/bash
ROOT_DIR := $(abspath ..)
export UV_PROJECT_ENVIRONMENT := $(ROOT_DIR)/.venv

PACKAGE_NAME ?= your_package

all: build lint test-unit

install:
	uv sync --project . --frozen --all-extras --dev

build: install
	rm -rf dist
	uv build --project . --out-dir dist

lint: install
	uv run --project . ruff format --check .
	uv run --project . ruff check .
	uv run --project . pyright
	uv run --project . pip-audit

lint-fix: install
	uv run --project . ruff format .
	uv run --project . ruff check . --fix
	uv run --project . pyright
	uv run --project . pip-audit

test-unit: install
	uv run --project . pytest --cov=src/$(PACKAGE_NAME) --cov-branch --cov-report=term-missing --cov-fail-under=80

run: install
	uv run --project . python -m $(PACKAGE_NAME)

dev: run

update-lockfile:
	uv lock --project . --upgrade

clean:
	rm -rf dist .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

**`lib/pyproject.toml`**

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

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.pyright]
include = ["src", "tests"]
venvPath = ".."
venv = ".venv"
typeCheckingMode = "standard"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

Use `lib/pyproject.toml` as the single configuration file for the package. Do not add
`requirements.txt`, `setup.py`, `setup.cfg`, `ruff.toml`, or `pyrightconfig.json` by default.

**`lib/README.md`**

This README is the published package README referenced by `lib/pyproject.toml`.

````markdown
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
````

### Phase 4: Create the package and tests inside `lib/`

Create this baseline structure.

**`lib/src/[package_name]/__init__.py`**

```python
from .core import hello

__all__ = ["hello"]
```

**`lib/src/[package_name]/core.py`**

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

**`lib/src/[package_name]/__main__.py`**

Use this only for CLI-oriented projects.

```python
from .core import hello


def main() -> None:
    print(hello("world"))


if __name__ == "__main__":
    main()
```

**`lib/tests/test_core.py`**

```python
from [package_name].core import hello


def test_hello() -> None:
    assert hello("world") == "Hello, world!"
```

If two or more test files need shared fixtures, create `lib/tests/conftest.py` and move shared setup there.

### Phase 5: Create examples for libraries and utilities

If the project is a library or shared utility, add an `examples/` directory with one subdirectory per runnable consumer example. Each example must be its own Python project.

**`examples/basic-usage/pyproject.toml`**

```toml
[project]
name = "basic-usage"
version = "0.0.0"
requires-python = ">=[python-version]"
dependencies = ["[package-name]"]

[tool.uv.sources]
[package-name] = { path = "../../lib", editable = false }
```

This keeps each example independent while still consuming the local library package.

**`examples/basic-usage/main.py`**

```python
from [package_name] import hello


print(hello("world"))
```

Examples must import the package as a consumer would. Avoid relative imports back into `lib/src/`.

### Phase 6: Verify

After creating the files:

1. Run `make install`.
2. Run `make lint-fix`.
3. Run `make test`.
4. Run `make build`.
5. Fix all failures before finishing.

## Examples

**Input:** "Create a Python library called `event_tools`"
- Create `Makefile`, `README.md`, `lib/pyproject.toml`, `lib/Makefile`, `lib/src/event_tools/`, `lib/tests/`, and `examples/`
- Configure `uv`, Ruff, Pyright, Pytest, `pytest-cov`, and `pip-audit`
- Verify with `make lint-fix`, `make test`, and `make build`

**Input:** "Scaffold a Python CLI package"
- Add `lib/src/<package_name>/__main__.py`
- Add `[project.scripts]` in `lib/pyproject.toml` when the command name must differ from the module name
- Keep the same Makefile and quality checks

## Edge Cases

- If the repository already has a root `.mise.toml`, pin Python and uv there instead of assuming host-installed tools.
- If the project is fewer than 100 lines and explicitly marked as a spike or experiment, examples and linting may be skipped only when another applicable XDR allows it.
- If an example needs extra dependencies, keep them in that example's `pyproject.toml`; do not move them into `lib/pyproject.toml` unless the library truly needs them.
- If the user asks for an app with framework-specific needs such as FastAPI or Django, keep this baseline and add the framework config on top instead of replacing it.

## References

- [agentme-edr-014](../../014-python-project-tooling.md)
- [_core-adr-003 - Skill standards](../../../../../_core/adrs/principles/003-skill-standards.md)
