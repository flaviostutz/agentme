SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build

.PHONY: build test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/application/skills/get-azure-devops-contents: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	find scripts -maxdepth 1 -name '*.js' ! -name '*.test.js' -exec cp {} $(BUILD)/scripts/ \;
	cd $(BUILD) && zip -rq ../get-azure-devops-contents.zip .

test: build
	@echo ">>> .xdrs/agentme/edrs/application/skills/get-azure-devops-contents: $@"
	$(MISE) node --test --experimental-test-coverage --test-coverage-include=scripts/azure-devops-lib.js --test-coverage-lines=80 --test-coverage-branches=80 scripts/*.test.js
	@$(MISE) node $(BUILD)/scripts/pr-comments-list.js > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 2 ]; then echo "bundled runner: expected exit 2, got $$rc"; exit 1; fi

clean:
	rm -rf dist
