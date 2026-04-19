SHELL := /bin/bash

.PHONY: all build lint test clean publish setup

all: build lint test

build:
	@echo '>>> ./examples/javascript-sample/lib: $@'
	@$(MAKE) -C lib build
	@echo '>>> ./examples/javascript-sample/examples: $@'
	@STAGE=dev $(MAKE) -C examples build

lint:
	@echo '>>> ./examples/javascript-sample/lib: $@'
	@$(MAKE) -C lib lint

test:
	@echo '>>> ./examples/javascript-sample/lib: $@'
	@$(MAKE) -C lib test
	@echo '>>> ./examples/javascript-sample/examples: $@'
	@STAGE=dev $(MAKE) -C examples test

clean:
	@echo '>>> ./examples/javascript-sample/lib: $@'
	@$(MAKE) -C lib clean
	@echo '>>> ./examples/javascript-sample/examples: $@'
	@STAGE=dev $(MAKE) -C examples clean
	@rm -rf .cache

publish:
	@echo '>>> ./examples/javascript-sample/lib: $@'
	@$(MAKE) -C lib publish

setup:
	@echo '>>> ./examples/javascript-sample: $@'
	mise install
