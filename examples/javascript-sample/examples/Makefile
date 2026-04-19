SHELL := /bin/bash

.PHONY: all build install test clean

all: build test

build: install
	@echo "Examples built"

install:
	@if [ ! -f ../lib/dist/javascript-sample-0.0.1.tgz ]; then \
		echo "Missing packaged artifact. Building lib first..."; \
		$(MAKE) -C ../lib build; \
	fi
	@$(MAKE) -C usage-basic install

test: install
	@echo "Running example tests..."
	@$(MAKE) -C usage-basic run

clean:
	@$(MAKE) -C usage-basic clean
