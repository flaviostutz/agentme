# Module Makefile for the skill scripts (agentme-edr-005)
SHELL := /bin/bash
MISE := mise exec --
ESLINT := eslint@10.12.0

.PHONY: lint test clean

lint:
	@echo ">>> .xdrs/agentme/edrs/principles/skills/resolve-pr-comments/scripts: $@"
	$(MISE) npx -y $(ESLINT) --cache --cache-location .cache/eslint/ --max-warnings 0 .

test:
	@echo ">>> .xdrs/agentme/edrs/principles/skills/resolve-pr-comments/scripts: $@"
	$(MISE) node --test --experimental-test-coverage --test-coverage-include=update-section.js --test-coverage-lines=80 --test-coverage-branches=80 *.test.js

clean:
	@echo ">>> .xdrs/agentme/edrs/principles/skills/resolve-pr-comments/scripts: $@"
	rm -rf .cache node_modules
