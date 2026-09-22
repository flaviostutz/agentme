SHELL := /bin/bash
MISE := mise exec --

# Bundling dependencies per _core-adr-policy-021 (skill-bundling): connector skills
# activated at runtime that must be resolvable from a standalone distribution.
DEPS := ../../../application/skills/github-connector ../../../application/skills/azure-devops-connector
BUILD := dist/build

.PHONY: build test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/principles/skills/resolve-pr-comments: $@"
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
	cd $(BUILD) && zip -rq ../resolve-pr-comments.zip .

test: build
	@echo ">>> .xdrs/agentme/edrs/principles/skills/resolve-pr-comments: $@"
	$(MISE) node --test scripts/*.test.js

clean:
	rm -rf dist
