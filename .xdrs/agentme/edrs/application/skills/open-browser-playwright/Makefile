SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build

.PHONY: build test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	find scripts -maxdepth 1 -name '*.js' ! -name '*.test.js' -exec cp {} $(BUILD)/scripts/ \;
	cd $(BUILD) && zip -rq ../open-browser-playwright.zip .

test: build
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	$(MISE) node --test --experimental-test-coverage --test-coverage-include=scripts/open-browser-lib.js --test-coverage-lines=80 --test-coverage-branches=80 scripts/*.test.js
	@$(MISE) node $(BUILD)/scripts/open-browser.js > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 64 ]; then echo "bundled runner: expected exit 64, got $$rc"; exit 1; fi

clean:
	rm -rf dist
