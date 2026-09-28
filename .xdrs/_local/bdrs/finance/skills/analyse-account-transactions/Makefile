SHELL := /bin/bash
BUILD := dist/build
PYTEST_FLAGS := -q -p no:cacheprovider
export PYTHONDONTWRITEBYTECODE := 1
export COVERAGE_FILE := dist/.coverage

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-transactions: $@"
	mkdir -p $(BUILD)/scripts/institutions
	cp -R SKILL.md references $(BUILD)/
	find scripts -maxdepth 1 -name '*.py' ! -name '*_test.py' ! -name conftest.py -exec cp {} $(BUILD)/scripts/ \;
	find scripts/institutions -maxdepth 1 -name '*.py' ! -name '*_test.py' -exec cp {} $(BUILD)/scripts/institutions/ \;
	cd $(BUILD) && zip -rq ../analyse-transactions.zip .

lint:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-transactions: $@"
	uvx ruff check --no-cache --line-length 120 scripts

test: build
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-transactions: $@"
	uv run --no-project --with pytest --with pytest-cov --with 'pdfplumber>=0.11' --with 'openpyxl>=3.1' \
		pytest $(PYTEST_FLAGS) --cov=scripts --cov-report=term-missing --cov-fail-under=80 scripts
	for s in normalize ground ledger validate answers research stats; do \
		$(BUILD)/scripts/$$s.py --help > /dev/null || exit 1; \
	done

clean:
	rm -rf dist
