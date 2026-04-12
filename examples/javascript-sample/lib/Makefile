SHELL := /bin/bash
MISE := mise exec --

build: install
	@rm -rf dist
	$(MISE) pnpm exec tsc --outDir dist
	@-find ./dist \( -regex '.*\.test\..*' -o -regex '.*__tests.*' \) -exec rm -rf {} \; 2> /dev/null
	@# Create pack for use by examples to simulate real external usage
	$(MISE) pnpm pack --pack-destination dist

build-module: install
	@rm -rf dist
	$(MISE) pnpm exec tsc --outDir dist
	@-find ./dist \( -regex '.*\.test\..*' -o -regex '.*__tests.*' \) -exec rm -rf {} \; 2> /dev/null

lint:
	$(MISE) pnpm exec eslint ./src

lint-fix:
	$(MISE) pnpm exec eslint ./src --fix

test-watch:
	$(MISE) pnpm exec jest --watch

test:
	$(MISE) pnpm exec jest --verbose

clean:
	rm -rf node_modules
	rm -rf dist

all: build lint test

install:
	mise install
	$(MISE) pnpm install --frozen-lockfile --config.dedupe-peer-dependents=false

publish:
	$(MISE) npx -y monotag@1.26.0 current --bump-action=latest --prefix=
	@VERSION=$$($(MISE) node -p "require('./package.json').version"); \
	if echo "$$VERSION" | grep -q '-'; then \
		TAG=$$(echo "$$VERSION" | sed 's/[0-9]*\.[0-9]*\.[0-9]*-\([a-zA-Z][a-zA-Z0-9]*\).*/\1/'); \
		echo "Prerelease version $$VERSION detected, publishing with --tag $$TAG"; \
		$(MISE) npm publish --no-git-checks --provenance --tag "$$TAG"; \
	else \
		$(MISE) npm publish --no-git-checks --provenance; \
	fi
