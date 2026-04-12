SHELL := /bin/bash
%:
	@echo "Unknown target: $@. Ignoring"

build: install
	@echo "Examples built"

install:
	# Replace the lib dependency with the locally built pack
	pnpm add javascript-sample@file:../lib/dist/javascript-sample-0.0.1.tgz
	pnpm install

test:
	@echo "Running example tests..."
	cd usage-basic && node index.js

all: build test
