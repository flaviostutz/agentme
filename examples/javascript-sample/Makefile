SHELL := /bin/bash
MISE := mise exec --

.PHONY: all build lint test clean publish setup

all: build lint test

build:
	@echo ''
	@echo '>>> Running /lib:build...'
	@$(MISE) $(MAKE) -C lib build
	@echo ''
	@echo '>>> Running /examples:build...'
	@STAGE=dev $(MISE) $(MAKE) -C examples build

lint:
	@echo ''
	@echo '>>> Running /lib:lint...'
	@$(MISE) $(MAKE) -C lib lint

test:
	@echo ''
	@echo '>>> Running /lib:test...'
	@$(MISE) $(MAKE) -C lib test
	@echo ''
	@echo '>>> Running /examples:test...'
	@STAGE=dev $(MISE) $(MAKE) -C examples test

clean:
	@echo ''
	@echo '>>> Running /lib:clean...'
	@$(MISE) $(MAKE) -C lib clean
	@echo ''
	@echo '>>> Running /examples:clean...'
	@STAGE=dev $(MISE) $(MAKE) -C examples clean
	@rm -rf .cache

publish:
	@$(MISE) $(MAKE) -C lib publish

setup:
	mise install
