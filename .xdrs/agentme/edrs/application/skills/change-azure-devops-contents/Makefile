SHELL := /bin/bash
MISE := mise exec --
TSX := npx -y tsx@4.23.15

# Bundling dependencies per _core-adr-policy-021 (skill-bundling): skills activated in prose.
DEPS := ../get-azure-devops-contents
BUILD := dist/build

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents: $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	cd scripts && find src -name '*.ts' ! -name '*.test.ts' ! -name '*_mock.ts' -exec sh -c 'mkdir -p ../$(BUILD)/scripts/$$(dirname {}) && cp {} ../$(BUILD)/scripts/{}' \;
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
	cd $(BUILD) && zip -rq ../change-azure-devops-contents.zip .

lint:
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents: $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents: $@"
	$(MAKE) -C scripts test
	@echo '[]' | $(MISE) $(TSX) $(BUILD)/scripts/src/adapters/cli/pr-comment-reply.ts > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 0 ]; then echo "bundled runner: expected exit 0, got $$rc"; exit 1; fi

clean:
	@echo ">>> .xdrs/agentme/edrs/application/skills/change-azure-devops-contents: $@"
	rm -rf dist
	$(MAKE) -C scripts clean
