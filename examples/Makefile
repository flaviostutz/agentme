SHELL := /bin/bash

clean:
	@rm -rf output node_modules

test: build

# Fix for recursive presets issue: add "presets": ["speckit"] to the selector of the speckit entries in package.json. This forwards the preset filter to agentkit's nested sets, preventing the xdrs-core basic set from being extracted recursively.

    # basic preset checks
	pnpm exec agentkit extract --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test ! -e output/.github/agents/speckit.analyze.agent.md
	pnpm exec agentkit check --output ./output --presets basic

	# speckit preset checks
	rm -rf output
	pnpm exec agentkit extract --output ./output --presets speckit
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test ! -e output/AGENTS.md
	test ! -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	pnpm exec agentkit check --output ./output --presets speckit

	# install all agentkit presets
	pnpm exec agentkit extract --output ./output
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test -e output/AGENTS.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	pnpm exec agentkit check --output ./output

	# AUTOMATIC CLEANUP OF PREVIOUSLY EXTRACTED PRESETS
	rm -rf output
    # basic preset checks
	pnpm exec agentkit extract --output ./output --presets basic
	test -e output/AGENTS.md
	test -e output/.xdrs/index.md
	test -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	test ! -e output/.github/agents/speckit.analyze.agent.md
	pnpm exec agentkit check --output ./output --presets basic

	# speckit preset checks (should remove the previous files from basic preset)
	pnpm exec agentkit extract --output ./output --presets speckit
	test -e output/.github/agents/speckit.analyze.agent.md
	test -e output/.specify/memory/constitution.md
	test ! -e output/AGENTS.md
	test ! -e output/.xdrs/_core/adrs/principles/001-xdr-standards.md
	pnpm exec agentkit check --output ./output --presets speckit

	# present because of previous extractions (it's not managed)
	test -e output/.xdrs/index.md


build: clean install

install:
	make -C .. build
	# replace the dependency with the local package
	pnpm add agentkit@file:../dist/agentkit-0.0.1.tgz
	pnpm install

