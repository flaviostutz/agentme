SHELL := /bin/bash
MISE := mise exec --

clean:
	@rm -rf output node_modules

test: build

# Fix for recursive presets issue: add "presets": ["speckit"] to the selector of the speckit entries in package.json. This forwards the preset filter to agentme's nested sets, preventing the xdrs-core basic set from being extracted recursively.

	# core preset checks
	$(MISE) pnpm exec agentme extract --output ./output --presets core
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test -e output/.xdrs/agentme/edrs/application/skills/004-select-relevant-xdrs/SKILL.md
	test ! -e output/.xdrs/agentme/edrs/principles/002-coding-best-practices.md
	test ! -e output/.github/agents/speckit.analyze.agent.md
	$(MISE) pnpm exec agentme check --output ./output --presets core

	# basic preset checks
	rm -rf output
	$(MISE) pnpm exec agentme extract --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test ! -e output/.github/agents/speckit.analyze.agent.md
	$(MISE) pnpm exec agentme check --output ./output --presets basic

	# speckit preset checks
	rm -rf output
	$(MISE) pnpm exec agentme extract --output ./output --presets speckit
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test ! -e output/AGENTS.md
	test ! -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	$(MISE) pnpm exec agentme check --output ./output --presets speckit

	# install all agentme presets
	$(MISE) pnpm exec agentme extract --output ./output
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	$(MISE) pnpm exec agentme check --output ./output

	# AUTOMATIC CLEANUP OF PREVIOUSLY EXTRACTED PRESETS
	rm -rf output
	# basic preset checks
	$(MISE) pnpm exec agentme extract --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test ! -e output/.github/agents/speckit.analyze.agent.md
	$(MISE) pnpm exec agentme check --output ./output --presets basic

	# core preset checks (should remove the previous managed files from basic preset)
	$(MISE) pnpm exec agentme extract --output ./output --presets core
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test -e output/.xdrs/agentme/edrs/application/skills/004-select-relevant-xdrs/SKILL.md
	test ! -e output/.xdrs/agentme/edrs/principles/002-coding-best-practices.md
	$(MISE) pnpm exec agentme check --output ./output --presets core

	# present because of previous extractions (it's not managed)
	test -e output/.xdrs/index.md

	# speckit preset checks (should remove the previous files from basic preset)
	$(MISE) pnpm exec agentme extract --output ./output --presets speckit
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test ! -e output/AGENTS.md
	test ! -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	$(MISE) pnpm exec agentme check --output ./output --presets speckit

	# present because of previous extractions (it's not managed)
	test -e output/.xdrs/index.md


build: clean install

install:
	$(MAKE) -C .. build
	# replace the dependency with the local package
	$(MISE) pnpm add agentme@file:../dist/agentme-0.0.1.tgz
	$(MISE) pnpm install

