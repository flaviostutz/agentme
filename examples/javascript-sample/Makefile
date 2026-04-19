SHELL := /bin/bash
MISE := mise exec --

.PHONY: all build lint test clean publish setup

all: build lint test

build:
	@echo ''
	@echo '>>> Running /lib:build...'
	@$(MAKE) -C lib build
	@echo ''
	@echo '>>> Running /examples:build...'
	@STAGE=dev $(MAKE) -C examples build

lint:
	@echo ''
	@echo '>>> Running /lib:lint...'
	@$(MAKE) -C lib lint

test:
	@echo ''
	@echo '>>> Running /lib:test...'
	@$(MAKE) -C lib test
	@echo ''
	@echo '>>> Running /examples:test...'
	@STAGE=dev $(MAKE) -C examples test

clean:
	@echo ''
	@echo '>>> Running /lib:clean...'
	@$(MAKE) -C lib clean
	@echo ''
	@echo '>>> Running /examples:clean...'
	@STAGE=dev $(MAKE) -C examples clean
	@rm -rf .cache

publish:
	@$(MAKE) -C lib publish

setup:
	mise install
