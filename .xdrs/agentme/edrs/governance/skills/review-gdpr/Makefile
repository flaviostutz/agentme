SHELL := /bin/bash
MISE := mise exec --
TSX := npx -y tsx@4.23.15
SKILL := review-gdpr

# Bundling dependencies per _core-adr-policy-021 (skill-bundling): skills activated in prose (none).
DEPS :=
BUILD := dist/build

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/agentme/edrs/governance/skills/$(SKILL): $@"
	mkdir -p $(BUILD)/scripts
	cp SKILL.md $(BUILD)/
	@if [ -d references ]; then cp -R references $(BUILD)/; fi
	find scripts -maxdepth 1 -name '*.ts' ! -name '*.test.ts' ! -name '*_mock.ts' -exec cp {} $(BUILD)/scripts/ \;
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
	cd $(BUILD) && zip -rq ../$(SKILL).zip .

lint:
	@echo ">>> .xdrs/agentme/edrs/governance/skills/$(SKILL): $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/agentme/edrs/governance/skills/$(SKILL): $@"
	$(MAKE) -C scripts test
	@$(MISE) $(TSX) $(BUILD)/scripts/review-gdpr.ts > /dev/null 2>&1; rc=$$?; \
		if [ $$rc -ne 2 ]; then echo "bundled runner: expected exit 2, got $$rc"; exit 1; fi

clean:
	@echo ">>> .xdrs/agentme/edrs/governance/skills/$(SKILL): $@"
	rm -rf dist
	$(MAKE) -C scripts clean
