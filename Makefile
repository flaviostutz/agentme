MISE := mise exec --

all: build lint test

build: install
	$(MISE) pnpm pack --pack-destination=./dist

lint:
	$(MISE) pnpm exec xdrs-core lint .

lint-fix:
	$(MISE) pnpm exec xdrs-core lint .

test: build
	$(MISE) $(MAKE) -C examples test

clean:
	rm -rf dist node_modules
	$(MAKE) -C examples clean

setup:
	mise install

install:
	mise install
	$(MISE) pnpm install

publish:
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
	@echo "Bumping xdrs core..."
	mise install
	$(MISE) pnpm add filedist@latest

	# we don't directly publish those files, but the project uses it itself
	$(MISE) pnpm add xdrs-core@latest
	$(MISE) pnpm exec xdrs-core extract
# 	pnpm exec filedist extract --packages git://github.com/flaviostutz/xdrs-core.git
