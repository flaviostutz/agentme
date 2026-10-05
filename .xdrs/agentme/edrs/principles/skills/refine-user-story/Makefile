SHELL := /bin/bash

# Bundling dependencies per _core-adr-policy-021 (skill-bundling): contents skills
# activated at runtime that must be resolvable from a standalone distribution.
DEPS := ../../../application/skills/get-github-contents ../../../application/skills/change-github-contents ../../../application/skills/get-azure-devops-contents ../../../application/skills/change-azure-devops-contents ../../../application/skills/get-web-contents
BUILD := dist/build

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/principles/skills/refine-user-story: $@"
	mkdir -p $(BUILD)
	cp SKILL.md $(BUILD)/
	cp -R references $(BUILD)/references
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
	cd $(BUILD) && zip -rq ../refine-user-story.zip .

lint:
	@echo ">>> .xdrs/agentme/edrs/principles/skills/refine-user-story: $@"

test: build
	@echo ">>> .xdrs/agentme/edrs/principles/skills/refine-user-story: $@"
	@for name in get-github-contents change-github-contents get-azure-devops-contents change-azure-devops-contents get-web-contents; do \
		grep -q "dist/$$name/SKILL.md" $(BUILD)/SKILL.md || { echo "bundled link for $$name missing"; exit 1; }; \
		[ -f $(BUILD)/dist/$$name/SKILL.md ] || { echo "bundled $$name missing"; exit 1; }; \
	done

clean:
	@echo ">>> .xdrs/agentme/edrs/principles/skills/refine-user-story: $@"
	rm -rf dist
