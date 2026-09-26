SHELL := /bin/bash
MISE := mise exec --

# Bundling dependencies per _core-adr-policy-021 (skill-bundling): skills activated in prose.
DEPS := ../get-github-contents
BUILD := dist/build

.PHONY: build test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-github-contents: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	find scripts -maxdepth 1 -name '*.js' ! -name '*.test.js' -exec cp {} $(BUILD)/scripts/ \;
	@for d in $(DEPS); do \
		name=$$(basename $$d); \
		mkdir -p $(BUILD)/dist/$$name; \
		if [ -f $$d/Makefile ]; then \
			$(MAKE) -C $$d build; \
			cp -R $$d/dist/build/. $(BUILD)/dist/$$name/; \
		else \
			cp $$d/SKILL.md $(BUILD)/dist/$$name/; \
		fi; \
		sed -i.bak "s#$$d/SKILL.md#dist/$$name/SKILL.md#g" $(BUILD)/SKILL.md && rm -f $(BUILD)/SKILL.md.bak; \
	done
	cd $(BUILD) && zip -rq ../change-github-contents.zip .

test: build
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-github-contents: $@"
	$(MISE) node --test --experimental-test-coverage --test-coverage-include=scripts/github-lib.js --test-coverage-lines=80 --test-coverage-branches=80 scripts/*.test.js
	@echo '[]' | $(MISE) node $(BUILD)/scripts/pr-comment-reply.js > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 0 ]; then echo "bundled runner: expected exit 0, got $$rc"; exit 1; fi

clean:
	rm -rf dist
