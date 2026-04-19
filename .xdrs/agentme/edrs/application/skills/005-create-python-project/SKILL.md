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

Creates a complete Python project from scratch using Mise, `uv`, `pyproject.toml`, Ruff,
Pyright, Pytest, and Makefiles. The default layout keeps the library self-contained under `lib/`,
uses a shared root `.venv/`, redirects persistent caches into `.cache/`, and places runnable
consumer projects under the sibling `examples/` folder.

Related EDRs: [agentme-edr-014](../../014-python-project-tooling.md), [agentme-edr-016](../../../principles/016-cross-language-module-structure.md)

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

**`./.mise.toml`**

```toml
[tools]
python = "3.13"
uv = "latest"
```

Replace `3.13` with the chosen Python version and pin any additional project CLIs used by the project here.

**`./Makefile`**

```makefile
SHELL := /bin/bash
MISE := mise exec --
ROOT_DIR := $(abspath .)
export UV_PROJECT_ENVIRONMENT := $(ROOT_DIR)/.venv
export UV_CACHE_DIR := $(ROOT_DIR)/.cache/uv

all: build lint test

setup:
	mise install
	$(MAKE) install

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
			UV_PROJECT_ENVIRONMENT="$(UV_PROJECT_ENVIRONMENT)" UV_CACHE_DIR="$(UV_CACHE_DIR)" $(MISE) uv sync --project "$$dir" --frozen || exit 1; \
			UV_PROJECT_ENVIRONMENT="$(UV_PROJECT_ENVIRONMENT)" UV_CACHE_DIR="$(UV_CACHE_DIR)" $(MISE) uv pip install --python "$(UV_PROJECT_ENVIRONMENT)/bin/python" lib/dist/*.whl || exit 1; \
			UV_PROJECT_ENVIRONMENT="$(UV_PROJECT_ENVIRONMENT)" UV_CACHE_DIR="$(UV_CACHE_DIR)" $(MISE) uv run --project "$$dir" python main.py || exit 1; \
		fi; \
	done

clean:
	$(MAKE) -C lib clean
	rm -rf .cache
	rm -rf .venv
```

The root `Makefile` keeps the repository clean by delegating package work to `lib/` and treating each example directory as an independent consumer project. Child Makefiles own the actual `mise exec -- <tool>` calls.

**`./.gitignore`**

```gitignore
.venv/
dist/
.cache/
```

**`./README.md`**

Keep this README focused on the repository or workspace. Put Getting Started near the top.

````markdown
# [package-name]

[description]

## Getting Started

```sh
make setup
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
MISE := mise exec --
ROOT_DIR := $(abspath ..)
export UV_PROJECT_ENVIRONMENT := $(ROOT_DIR)/.venv
export UV_CACHE_DIR := $(ROOT_DIR)/.cache/uv
export RUFF_CACHE_DIR := $(abspath .cache/ruff)
export PYTHONPYCACHEPREFIX := $(abspath .cache/pycache)
export COVERAGE_FILE := $(abspath .cache/coverage)

PACKAGE_NAME ?= your_package

all: build lint test-unit

install:
	$(MISE) uv sync --project . --frozen --all-extras --dev

build: install
	rm -rf dist
	$(MISE) uv build --project . --out-dir dist

lint: install
	$(MISE) uv run --project . ruff format --check .
	$(MISE) uv run --project . ruff check .
	$(MISE) uv run --project . pyright
	$(MISE) uv run --project . pip-audit

lint-fix: install
	$(MISE) uv run --project . ruff format .
	$(MISE) uv run --project . ruff check . --fix
	$(MISE) uv run --project . pyright
	$(MISE) uv run --project . pip-audit

test-unit: install
	$(MISE) uv run --project . pytest -o cache_dir=.cache/pytest --cov=src/$(PACKAGE_NAME) --cov-branch --cov-report=term-missing --cov-report=html:.cache/htmlcov --cov-fail-under=80

run: install
	$(MISE) uv run --project . python -m $(PACKAGE_NAME)

dev: run

update-lockfile:
	$(MISE) uv lock --project . --upgrade

clean:
	rm -rf dist .cache
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
make setup
make test
```

```python
from [package-name] import hello

print(hello("world"))
```

## Development

```sh
make build
make lint
make test
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

If the module needs slower end-to-end coverage, place those tests in `lib/tests_integration/`. Put dedicated benchmark harnesses in `lib/tests_benchmark/`.

### Phase 5: Create examples for libraries and utilities

If the project is a library or shared utility, add an `examples/` directory with one subdirectory per runnable consumer example. Each example must be its own Python project.

**`examples/basic-usage/pyproject.toml`**

```toml
[project]
name = "basic-usage"
version = "0.0.0"
requires-python = ">=[python-version]"
dependencies = []
```

The root `test-examples` target installs the wheel built into `lib/dist/` before running each
example. Do not point examples back to `../../lib` or `lib/src/`.

**`examples/basic-usage/main.py`**

```python
from [package_name] import hello


print(hello("world"))
```

Examples must import the package as a consumer would. Avoid relative imports back into `lib/src/`.

### Phase 6: Verify

After creating the files:

1. Run `make setup`.
2. Run `make install`.
3. Run `make lint-fix`.
4. Run `make test`.
5. Run `make build`.
6. Fix all failures before finishing.

## Examples

**Input:** "Create a Python library called `event_tools`"
- Create `Makefile`, `README.md`, `lib/pyproject.toml`, `lib/Makefile`, `lib/src/event_tools/`, `lib/tests/`, and `examples/`
- Add `lib/README.md`, `.cache/` handling, and install examples from the built wheel in `lib/dist/`
- Configure `uv`, Ruff, Pyright, Pytest, `pytest-cov`, and `pip-audit`
- Verify with `make lint-fix`, `make test`, and `make build`

**Input:** "Scaffold a Python CLI package"
- Add `lib/src/<package_name>/__main__.py`
- Add `[project.scripts]` in `lib/pyproject.toml` when the command name must differ from the module name
- Keep the same Makefile and quality checks

## Edge Cases

- Pin Python and uv in the root `.mise.toml`; do not assume host-installed tools.
- If the project is fewer than 100 lines and explicitly marked as a spike or experiment, examples and linting may be skipped only when another applicable XDR allows it.
- If an example needs extra dependencies, keep them in that example's `pyproject.toml`; do not move them into `lib/pyproject.toml` unless the library truly needs them.
- If the user asks for an app with framework-specific needs such as FastAPI or Django, keep this baseline and add the framework config on top instead of replacing it.

## References

- [agentme-edr-014](../../014-python-project-tooling.md)
- [_core-adr-003 - Skill standards](../../../../../_core/adrs/principles/003-skill-standards.md)
