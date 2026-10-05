SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build
CLIS := pm

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/_local/bdrs/finance/skills/manage-investment-portfolio: $@"
	mkdir -p $(BUILD)/scripts
	cp -R SKILL.md references $(BUILD)/
	cp scripts/pyproject.toml $(BUILD)/scripts/
	cp -R scripts/src $(BUILD)/scripts/src
	find $(BUILD) \( -name __pycache__ -o -name '*_mock.py' \) -prune -exec rm -rf {} +
	cd $(BUILD) && zip -rq ../manage-investment-portfolio.zip .

lint:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/manage-investment-portfolio: $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/_local/bdrs/finance/skills/manage-investment-portfolio: $@"
	$(MAKE) -C scripts test
	for c in $(CLIS); do $(MISE) uvx --from $(BUILD)/scripts $$c --help > /dev/null || exit 1; done

clean:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/manage-investment-portfolio: $@"
	rm -rf dist
	$(MAKE) -C scripts clean
