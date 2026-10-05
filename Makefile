MISE := mise exec --

# skill Makefiles of every scope except _core (agentme-edr-005)
SKILL_DIRS := $(patsubst %/Makefile,%,$(filter-out .xdrs/_core/%,$(wildcard .xdrs/*/*/*/skills/*/Makefile)))

all: build lint test

build: install
	@echo ">>> .: $@"
	$(MISE) npm pack --pack-destination=./dist

lint:
	@echo ">>> .: $@"
	$(MISE) pnpm exec xdrs-core lint .
	@$(MAKE) skills TARGET=lint

lint-fix:
	@echo ">>> .: $@"
	$(MISE) pnpm exec xdrs-core lint .

test: build
	@echo ">>> ./examples: $@"
	$(MAKE) -C examples test
	@$(MAKE) skills TARGET=test

clean:
	@echo ">>> .: $@"
	rm -rf dist node_modules
	@echo ">>> ./examples: $@"
	$(MAKE) -C examples clean
	@$(MAKE) skills TARGET=clean

# runs TARGET sequentially (never make -j) in every skill Makefile, stopping at the first failure
skills:
	@echo ">>> .: skills $(TARGET)"
	@for d in $(SKILL_DIRS); do \
		if grep -q "^$(TARGET):" $$d/Makefile; then $(MAKE) -C $$d $(TARGET) || exit 1; \
		else echo ">>> $$d: no $(TARGET) target, skipped"; fi; \
	done

setup:
	@echo ">>> .: $@"
	mise install

install:
	@echo ">>> .: $@"
	mise install
	$(MISE) pnpm install

publish:
	@echo ">>> .: $@"
	$(MISE) npx -y monotag@1.26.0 current --bump-action=latest --prefix=
	@VERSION=$$($(MISE) node -p "require('./package.json').version"); \
	if echo "$$VERSION" | grep -q '-'; then \
		TAG=$$(echo "$$VERSION" | sed 's/[0-9]*\.[0-9]*\.[0-9]*-\([a-zA-Z][a-zA-Z0-9]*\).*/\1/'); \
		echo "Prerelease version $$VERSION detected, publishing with --tag $$TAG to avoid it being 'latest'"; \
		$(MISE) npm publish --no-git-checks --tag "$$TAG"; \
	else \
		$(MISE) npm publish --no-git-checks; \
	fi

bump:
	@echo ">>> .: $@"
	mise install
	$(MISE) pnpm add filedist@latest

	# used for linting xdrs
	$(MISE) pnpm add xdrs-core@latest

	# we don't directly publish those files, but the project uses it itself
	$(MISE) pnpm exec filedist update

# 	copilot -p "check and fix agentme xdrs after xdrs-core bump"
