SHELL := /bin/bash
MISE := mise exec --
BUILD := dist/build
CLIS := aat-normalize aat-ground aat-ledger aat-validate aat-answers aat-research aat-stats

.PHONY: build lint test clean

build: clean
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions: $@"
	mkdir -p $(BUILD)/scripts
	cp -R SKILL.md references $(BUILD)/
	cp scripts/pyproject.toml $(BUILD)/scripts/
	cp -R scripts/src $(BUILD)/scripts/src
	find $(BUILD) \( -name __pycache__ -o -name '*_mock.py' \) -prune -exec rm -rf {} +
	cd $(BUILD) && zip -rq ../analyse-account-transactions.zip .

lint:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions: $@"
	$(MAKE) -C scripts lint

test: build
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions: $@"
	$(MAKE) -C scripts test
	for c in $(CLIS); do $(MISE) uvx --from $(BUILD)/scripts $$c --help > /dev/null || exit 1; done

clean:
	@echo ">>> .xdrs/_local/bdrs/finance/skills/analyse-account-transactions: $@"
	rm -rf dist
	$(MAKE) -C scripts clean
