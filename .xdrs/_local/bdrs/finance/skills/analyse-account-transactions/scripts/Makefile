# Module Makefile for the skill scripts (agentme-edr-005, agentme-edr-103)
SHELL := /bin/bash
MISE := mise exec --
export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.cache/venv
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: install lock lint lint-fix test clean

install:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	$(MISE) uv sync --frozen --dev

lock:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	$(MISE) uv lock

lint: install
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	$(MISE) uv run ruff format --check .
	$(MISE) uv run ruff check .
	$(MISE) uv run ty check
	$(MISE) uv run pip-audit --skip-editable

lint-fix: install
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	$(MISE) uv run ruff format .
	$(MISE) uv run ruff check . --fix

test: install
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	$(MISE) uv run pytest

clean:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions/scripts: $@"
	rm -rf .cache dist
