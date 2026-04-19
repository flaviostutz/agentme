MISE := mise exec --

all: build lint test

build: install
	@echo ">>> .: $@"
	$(MISE) pnpm pack --pack-destination=./dist

lint:
	@echo ">>> .: $@"
	$(MISE) pnpm exec xdrs-core lint .

lint-fix:
	@echo ">>> .: $@"
	$(MISE) pnpm exec xdrs-core lint .

test: build
	@echo ">>> ./examples: $@"
	$(MAKE) -C examples test

clean:
	@echo ">>> .: $@"
	rm -rf dist node_modules
	@echo ">>> ./examples: $@"
	$(MAKE) -C examples clean

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

	# we don't directly publish those files, but the project uses it itself
	$(MISE) pnpm add xdrs-core@latest
	$(MISE) pnpm exec xdrs-core extract
# 	pnpm exec filedist extract --packages git:github.com/flaviostutz/xdrs-core.git
