SHELL := /bin/bash

.PHONY: all build install test clean

all: build test

build: install
	@echo ">>> ./examples/javascript-sample/examples: $@"

install:
	@echo ">>> ./examples/javascript-sample/examples: $@"
	@if [ ! -f ../lib/dist/javascript-sample-0.0.1.tgz ]; then \
		echo ">>> ../lib: build"; \
		$(MAKE) -C ../lib build; \
	fi
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: install"
	@$(MAKE) -C usage-basic install

test: install
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: run"
	@$(MAKE) -C usage-basic run

clean:
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: clean"
	@$(MAKE) -C usage-basic clean
