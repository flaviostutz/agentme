---
skill: create-python-project
skill-version: "1.1.0"
---

## Test Scenarios

### Scenario 1: Create a new Python package, happy path

**Trigger / Input**

"Create a Python project called `event_tools`."

**Expected Behaviour**

1. Phase 1 gathers or infers package name (`event_tools`), description, author, Python version
   (default `3.13`), and primary entry point.
2. Phase 2 creates root `.mise.toml`, root `Makefile` (exporting `UV_PROJECT_ENVIRONMENT`/
   `UV_CACHE_DIR`, delegating `build`/`lint`/`test` to `lib/`, and running each `examples/*`
   project against the built wheel), root `.gitignore` ignoring `.venv/`, `dist/`, `.cache/`, and
   `__pycache__/`, and root `README.md` with Getting Started (`make setup` / `make test`) near the
   top.
3. Phase 3 creates `lib/Makefile`, `lib/pyproject.toml` (Ruff, ty, pytest-cov, pip-audit
   configured), and `lib/README.md` with Quick Start first.
4. Phase 4 creates `lib/src/event_tools/` with `app/`, `adapters/`, `shared/` following the
   hexagonal layout, plus `lib/tests/hello_test.py`.
5. Phase 5 creates `examples/basic-usage/` as an independent consumer project that imports
   `event_tools` rather than importing from `lib/src/`.
6. Phase 6 runs `make setup`, `make install`, `make lint-fix`, `make test`, and `make build`, and
   fixes any failures before finishing.

**Assertions**

- [ ] Output creates `lib/src/event_tools/app/`, `lib/src/event_tools/adapters/`, and
      `lib/src/event_tools/shared/` following the hexagonal layout.
- [ ] Output configures `lib/pyproject.toml` with Ruff, ty, pytest-cov, and pip-audit, and does
      not add a separate `requirements.txt`, `setup.py`, `ruff.toml`, or `ty.toml`.
- [ ] Output creates `examples/basic-usage/` as its own project that imports the `event_tools`
      package rather than reaching into `lib/src/` with a relative import.
- [ ] Output reports running `make lint-fix`, `make test`, and `make build` and fixes any
      failures before declaring completion.

### Scenario 2: CLI package request adds an entry point, not a new baseline

**Trigger / Input**

"Scaffold a Python CLI package called `net_probe` with a command named `probe`."

**Expected Behaviour**

Per Phase 4 and the skill's own CLI example, the skill keeps the same baseline Makefile and
quality checks and adds the CLI entry point in `lib/src/net_probe/adapters/cli/__init__.py`,
adding `[project.scripts]` to `lib/pyproject.toml` only because the command name (`probe`)
differs from the module name (`net_probe`).

**Assertions**

- [ ] Output places the CLI entry point in `lib/src/net_probe/adapters/cli/__init__.py`, not in
      `app/` or at the package root.
- [ ] Output adds a `[project.scripts]` entry in `lib/pyproject.toml` mapping `probe` to the CLI
      entry point.

### Scenario 3: Example-only dependency stays in the example, not in lib/

**Trigger / Input**

"Add an example under `examples/` that calls a public HTTP API and therefore needs the `httpx`
library. The core `event_tools` package itself does not need `httpx`."

**Expected Behaviour**

Per the Edge Cases entry on example dependencies, the skill adds `httpx` to that example's own
`pyproject.toml` and does not add it to `lib/pyproject.toml`, since the library itself has no
need for it.

**Assertions**

- [ ] Output adds `httpx` only to the example's own `pyproject.toml`.
- [ ] Output does not add `httpx` to `lib/pyproject.toml`.
