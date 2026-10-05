SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build
TSX := npx -y tsx@4.23.15

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	cd scripts && find src -name '*.ts' ! -name '*.test.ts' ! -name '*_mock.ts' -exec sh -c 'mkdir -p ../$(BUILD)/scripts/$$(dirname {}) && cp {} ../$(BUILD)/scripts/{}' \;
	cd $(BUILD) && zip -rq ../open-browser-playwright.zip .

lint:
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	$(MAKE) -C scripts test
	@$(MISE) $(TSX) $(BUILD)/scripts/src/adapters/cli/open-browser.ts > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 64 ]; then echo "bundled runner: expected exit 64, got $$rc"; exit 1; fi

clean:
	@echo ">>> .xdrs/agentme/edrs/application/skills/open-browser-playwright: $@"
	rm -rf dist
	$(MAKE) -C scripts clean
