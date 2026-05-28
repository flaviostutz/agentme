---
name: agentme-edr-skill-005-create-python-project
description: >
  Scaffolds the initial boilerplate structure for a Python project following the standard tooling
  and layout defined in agentme-edr-014. Activate this skill when the user asks to create,
  scaffold, or initialize a new Python package, CLI, or similar project structure.
metadata:
  author: flaviostutz
  version: "1.0"
compatibility: Python 3.12+
---

## Overview

Creates a complete Python project from scratch using Mise, `uv`, `pyproject.toml`, Ruff,
ty, Pytest, and Makefiles. The layout keeps the package self-contained under `lib/`,
organizes internal code following [agentme-edr-021](../../021-pragmatic-hexagonal-architecture.md)
(`adapters/`, `app/`, `shared/`), uses a shared root `.venv/`, redirects persistent caches into
`.cache/`, and places runnable consumer projects under the sibling `examples/` folder.

Related EDRs: [agentme-edr-014](../../014-python-project-tooling.md), [agentme-edr-016](../../../principles/016-cross-language-module-structure.md), [agentme-edr-021](../../021-pragmatic-hexagonal-architecture.md)

## Instructions

### Phase 1: Gather information

Ask for or infer from context:

- **Package name** - Python distribution/import name, e.g. `my_tool`
- **Short description** - one sentence
- **Author** name or GitHub username
- **Python version** - default `3.13`
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
__pycache__/
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
	$(MISE) uv run --project . ty check
	$(MISE) uv run --project . pip-audit

lint-fix: install
	$(MISE) uv run --project . ruff format .
	$(MISE) uv run --project . ruff check . --fix
	$(MISE) uv run --project . ty check
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
  "ty>=0.1.0",
  "pytest>=8.4.0",
  "pytest-cov>=6.1.0",
  "ruff>=0.11.0",
]

[build-system]
requires = ["hatchling>=1.27.0"]
build-backend = "hatchling.build"

[tool.ruff]
cache-dir = ".cache/ruff"
output-format = "grouped"
line-length = 120
target-version = "py313"
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

[tool.ty]
src = ["src", "tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "*_test.py"
addopts = "-q"
```

Use `lib/pyproject.toml` as the single configuration file for the package. Do not add
`requirements.txt`, `setup.py`, `setup.cfg`, `ruff.toml`, or `ty.toml` by default.

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

Create this baseline structure following [agentme-edr-021](../../021-pragmatic-hexagonal-architecture.md).

**`lib/src/[package_name]/__init__.py`**

```python
from .app.hello import hello

__all__ = ["hello"]
```

**`lib/src/[package_name]/app/__init__.py`**

```python
```

**`lib/src/[package_name]/app/hello.py`**

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

**`lib/src/[package_name]/adapters/__init__.py`**

```python
```

**`lib/src/[package_name]/adapters/cli/__init__.py`**

```python
from [package_name].app.hello import hello


def main() -> None:
    print(hello("world"))


if __name__ == "__main__":
    main()
```

**`lib/src/[package_name]/shared/__init__.py`**

```python
```

Create empty `adapters/connectors/` directory with a `.gitkeep` for outbound adapters.

**`lib/tests/hello_test.py`**

```python
from [package_name].app.hello import hello


def test_hello() -> None:
    assert hello("world") == "Hello, world!"
```

If two or more test files need shared fixtures, create `lib/tests/conftest.py` and move shared setup there.

If the module needs slower end-to-end coverage, place those tests in `lib/tests_integration/`. Put dedicated benchmark harnesses in `lib/tests_benchmark/`.

### Phase 5: Create examples

Add an `examples/` directory with one subdirectory per runnable consumer example. Each example must be its own Python project.

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

**Input:** "Create a Python project called `event_tools`"
- Create `Makefile`, `README.md`, `lib/pyproject.toml`, `lib/Makefile`, `lib/src/event_tools/`, `lib/tests/`, and `examples/`
- Scaffold `adapters/`, `app/`, `shared/` directories inside `lib/src/event_tools/`
- Add `lib/README.md`, `.cache/` handling, and install examples from the built wheel in `lib/dist/`
- Configure `uv`, Ruff, ty, Pytest, `pytest-cov`, and `pip-audit`
- Verify with `make lint-fix`, `make test`, and `make build`

**Input:** "Scaffold a Python CLI package"
- Add CLI entry point in `lib/src/<package_name>/adapters/cli/__init__.py`
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
