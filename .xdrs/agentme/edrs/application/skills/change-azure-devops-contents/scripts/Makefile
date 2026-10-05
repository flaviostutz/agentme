# Module Makefile for the skill scripts (agentme-edr-005, agentme-edr-101)
SHELL := /bin/bash
MISE := mise exec --
CACHE_DIR := .cache

.PHONY: install lint lint-fix test clean

install:
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents/scripts: $@"
	$(MISE) pnpm install --frozen-lockfile --config.dedupe-peer-dependents=false

lint: install
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents/scripts: $@"
	@mkdir -p $(CACHE_DIR)/eslint $(CACHE_DIR)/tsc
	$(MISE) pnpm exec tsc --noEmit --incremental --tsBuildInfoFile $(CACHE_DIR)/tsc/tsconfig.tsbuildinfo
	$(MISE) pnpm exec eslint ./src --max-warnings 0 --cache --cache-location $(CACHE_DIR)/eslint/.eslintcache

lint-fix: install
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents/scripts: $@"
	@mkdir -p $(CACHE_DIR)/eslint
	$(MISE) pnpm exec eslint ./src --fix --cache --cache-location $(CACHE_DIR)/eslint/.eslintcache

test: install
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents/scripts: $@"
	$(MISE) pnpm exec jest --verbose --coverage

clean:
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents/scripts: $@"
	rm -rf node_modules .cache
