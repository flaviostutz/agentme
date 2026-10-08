SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	cp scripts/pyproject.toml $(BUILD)/scripts/
	cp -R scripts/src $(BUILD)/scripts/src
	find $(BUILD) -name __pycache__ -prune -exec rm -rf {} +
	cd $(BUILD) && zip -rq ../analyse-cvs.zip .

lint:
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	$(MAKE) -C scripts test
	$(MISE) uvx --from $(BUILD)/scripts cvs-stage --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-redact --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-organise --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-slug --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-score --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-check --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-rank --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-sources --help > /dev/null
	$(MISE) uvx --from $(BUILD)/scripts cvs-publish --help > /dev/null

clean:
	@echo ">>> .xdrs/agentme/bdrs/operations/skills/analyse-cvs: $@"
	rm -rf dist
	$(MAKE) -C scripts clean
