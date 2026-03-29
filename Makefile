all: build test

build: install
	pnpm pack --pack-destination=./dist

lint:
	@echo "No linting rules to check"

test: build
	make -C examples test

clean:
	rm -rf dist node_modules
	make -C examples clean

setup:
	mise install

install:
	pnpm install

publish:
	npx -y monotag@1.26.0 current --bump-action=latest --prefix=
	@VERSION=$$(node -p "require('./package.json').version"); \
	if echo "$$VERSION" | grep -q '-'; then \
		TAG=$$(echo "$$VERSION" | sed 's/[0-9]*\.[0-9]*\.[0-9]*-\([a-zA-Z][a-zA-Z0-9]*\).*/\1/'); \
		echo "Prerelease version $$VERSION detected, publishing with --tag $$TAG to avoid it being 'latest'"; \
		npm publish --no-git-checks --tag "$$TAG"; \
	else \
		npm publish --no-git-checks; \
	fi

bump:
	@echo "Bumping xdrs core..."
	pnpm add xdrs-core@latest
	pnpm add filedist@latest

	# we don't directly publish those files, but the project uses it itself
	pnpm exec xdrs-core extract
