SHELL := /bin/bash
BUILD := dist/build
PYTEST_FLAGS := -q -p no:cacheprovider
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	find scripts -maxdepth 1 -name '*.py' ! -name '*_test.py' -exec cp {} $(BUILD)/scripts/ \;
	cd $(BUILD) && zip -rq ../analyse-cvs.zip .

lint:
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	uvx ruff check --no-cache --line-length 120 scripts

test: build
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	uv run --no-project --with pytest pytest $(PYTEST_FLAGS) scripts
	$(BUILD)/scripts/stage.py --help > /dev/null
	$(BUILD)/scripts/redact.py --help > /dev/null
	$(BUILD)/scripts/organise.py --help > /dev/null

clean:
	rm -rf dist
