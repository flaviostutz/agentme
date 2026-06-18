SHELL := /bin/bash
MISE := mise exec --

clean:
	@echo ">>> ./examples: $@"
	@rm -rf output node_modules

test: build
	@echo ">>> ./examples: $@"

	# core preset checks
	$(MISE) pnpm exec agentme install --output ./output --presets core
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/002-policy-standards.md
	test -e output/.xdrs/agentme/edrs/application/skills/004-select-relevant-xdrs/SKILL.md
	test ! -e output/.xdrs/agentme/edrs/principles/002-coding-best-practices.md
	$(MISE) pnpm exec agentme check --output ./output --presets core

	# basic preset checks
	rm -rf output
	$(MISE) pnpm exec agentme install --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/002-policy-standards.md
	$(MISE) pnpm exec agentme check --output ./output --presets basic

	# install all agentme presets
	$(MISE) pnpm exec agentme install --output ./output
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/002-policy-standards.md
	$(MISE) pnpm exec agentme check --output ./output

	# AUTOMATIC CLEANUP OF PREVIOUSLY EXTRACTED PRESETS
	rm -rf output
	# basic preset checks
	$(MISE) pnpm exec agentme install --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/002-policy-standards.md
	$(MISE) pnpm exec agentme check --output ./output --presets basic

	# core preset checks (should remove the previous managed files from basic preset)
	$(MISE) pnpm exec agentme install --output ./output --presets core
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/002-policy-standards.md
	test -e output/.xdrs/agentme/edrs/application/skills/004-select-relevant-xdrs/SKILL.md
	test ! -e output/.xdrs/agentme/edrs/principles/002-coding-best-practices.md
	$(MISE) pnpm exec agentme check --output ./output --presets core

	# present because of previous extractions (it's not managed)
	test -e output/.xdrs/index.md


build: clean install
	@echo ">>> ./examples: $@"

install:
	@echo ">>> ..: build"
	$(MAKE) -C .. build
	# replace the dependency with the local package
	@echo ">>> ./examples: $@"
	$(MISE) pnpm add agentme@file:../dist/agentme-0.0.1.tgz
	$(MISE) pnpm install

