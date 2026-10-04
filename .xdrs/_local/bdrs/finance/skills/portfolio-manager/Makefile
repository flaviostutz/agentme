SHELL := /bin/bash
BUILD := dist/build
PYTEST_FLAGS := -q -p no:cacheprovider -W ignore::DeprecationWarning
export PYTHONDONTWRITEBYTECODE := 1
export COVERAGE_FILE := dist/.coverage

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/_local/bdrs/finance/skills/portfolio-manager: $@"
	mkdir -p $(BUILD)/scripts/institutions
	cp -R SKILL.md references $(BUILD)/
	find scripts -maxdepth 1 -name '*.py' ! -name '*_test.py' ! -name conftest.py -exec cp {} $(BUILD)/scripts/ \;
	find scripts/institutions -maxdepth 1 -name '*.py' ! -name '*_test.py' -exec cp {} $(BUILD)/scripts/institutions/ \;
	cd $(BUILD) && zip -rq ../portfolio-manager.zip .

lint:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/portfolio-manager: $@"
	cd scripts && uvx ruff check --no-cache --line-length 120 .

test: build
	@echo ">>> .xdrs/_local/bdrs/finance/skills/portfolio-manager: $@"
	uv run --no-project --with pytest --with pytest-cov --with pymupdf --with pyyaml \
		pytest $(PYTEST_FLAGS) --cov=scripts --cov-report=term-missing --cov-fail-under=80 scripts
	uv run --no-project --with pymupdf --with pyyaml python $(BUILD)/scripts/pm.py --help > /dev/null

clean:
	rm -rf dist
