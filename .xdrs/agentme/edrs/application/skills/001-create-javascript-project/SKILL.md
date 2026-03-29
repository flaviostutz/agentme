---
name: 001-create-javascript-project
description: >
  Scaffolds the initial boilerplate structure for a JavaScript/TypeScript library project following
  the standard tooling and layout defined in _core-edr-003. Activate this skill when the user
  asks to create, scaffold, or initialize a new JavaScript or TypeScript library project, npm
  package, or similar project structure.
metadata:
  author: flaviostutz
  version: "1.0"
compatibility: JavaScript/TypeScript, Node.js 18+
---

## Overview

Creates a complete JavaScript/TypeScript library project from scratch. The layout separates
library source (`lib/`) from runnable usage examples (`examples/`), coordinated by root-level
Makefiles. Boilerplate is derived from the [filedist](https://github.com/flaviostutz/filedist)
project.

Related EDR: [agentme-edr-003](../../003-javascript-project-tooling.md)

## Instructions

### Phase 1: Gather information

1. Ask for (or infer from context):
   - **Package name** (npm-compatible, e.g. `my-lib`)
   - **Short description** (one sentence)
   - **Author** name or GitHub username
   - **Node.js version** (default: `24`)
   - **GitHub repo URL** (optional, for `package.json` fields)
2. Confirm the target directory (default: current workspace root).

---

### Phase 2: Create root files

**`./Makefile`**

Delegates every make target to `/lib` then `/examples` in sequence:

```makefile
SHELL := /bin/bash
%:
	@echo ''
	@echo '>>> Running /lib:$@...'
	@cd lib && make $@
	@echo ''
	@echo '>>> Running /examples:$@...'
	@cd examples && STAGE=dev make $@

publish:
	cd lib && make publish

prepare:
	@echo "Run 'nvm use; corepack enable'"
```

**`./.nvmrc`**

```
24
```
(Replace `24` with the chosen Node.js version.)

**`./.gitignore`**

```
node_modules/
dist/
*.tgz
.filedist
```

---

### Phase 3: Create `lib/`

**`lib/src/index.ts`** — public API entry point:

```typescript
export const hello = (name: string): string => {
  return `Hello, ${name}!`;
};
```

**`lib/src/index.test.ts`** — co-located unit test:

```typescript
import { hello } from './index';

describe('hello', () => {
  it('should return a greeting', () => {
    expect(hello('world')).toBe('Hello, world!');
  });
});
```

**`lib/Makefile`**:

```makefile
SHELL := /bin/bash

build: install
	@rm -rf dist
	pnpm exec tsc --outDir dist
	@-find ./dist \( -regex '.*\.test\..*' -o -regex '.*__tests.*' \) -exec rm -rf {} \; 2> /dev/null
	@# Create pack for use by examples to simulate real external usage
	pnpm pack --pack-destination dist

build-module: install
	@rm -rf dist
	pnpm exec tsc --outDir dist
	@-find ./dist \( -regex '.*\.test\..*' -o -regex '.*__tests.*' \) -exec rm -rf {} \; 2> /dev/null

lint:
	pnpm exec eslint ./src --ext .ts

lint-fix:
	pnpm exec eslint . --ext .ts --fix

test-watch:
	pnpm exec jest --watch

test:
	pnpm exec jest --verbose

clean:
	rm -rf node_modules
	rm -rf dist

all: build lint test

install:
	pnpm install --frozen-lockfile --config.dedupe-peer-dependents=false

publish:
	npx -y monotag@1.26.0 current --bump-action=latest --prefix=
	@VERSION=$$(node -p "require('./package.json').version"); \
	if echo "$$VERSION" | grep -q '-'; then \
		TAG=$$(echo "$$VERSION" | sed 's/[0-9]*\.[0-9]*\.[0-9]*-\([a-zA-Z][a-zA-Z0-9]*\).*/\1/'); \
		echo "Prerelease version $$VERSION detected, publishing with --tag $$TAG"; \
		npm publish --no-git-checks --provenance --tag "$$TAG"; \
	else \
		npm publish --no-git-checks --provenance; \
	fi
```

**`lib/package.json`** (replace `[package-name]`, `[description]`, `[author]`, `[owner]`, `[repo]`):

```json
{
  "name": "[package-name]",
  "version": "0.0.1",
  "description": "[description]",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist/**",
    "package.json",
    "README.md"
  ],
  "packageManager": "pnpm@8.9.0",
  "scripts": {},
  "repository": {
    "type": "git",
    "url": "git+https://github.com/[owner]/[repo].git"
  },
  "author": "[author]",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/[owner]/[repo]/issues"
  },
  "homepage": "https://github.com/[owner]/[repo]#readme",
  "devDependencies": {
    "@babel/preset-typescript": "^7.21.0",
    "@stutzlab/eslint-config": "^3.2.1",
    "@tsconfig/node24": "^24.0.0",
    "@types/jest": "^29.5.0",
    "esbuild": "^0.20.0",
    "eslint": "^8.57.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.3.0"
  }
}
```

**`lib/tsconfig.json`**:

```json
{
  "extends": "@tsconfig/node24/tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

**`lib/jest.config.js`**:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.test.ts'],
};
```

**`lib/eslint.config.js`** (ESLint 9 flat config format):

```js
import baseConfig from '@stutzlab/eslint-config';

export default [
  ...baseConfig,
  {
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.json'],
        tsconfigRootDir: process.cwd(),
      },
    },
  },
];
```

---

### Phase 4: Create `examples/`

**`examples/Makefile`** (replace `[package-name]`):

```makefile
SHELL := /bin/bash
%:
	@echo "Unknown target: $@. Ignoring"

build: install
	@echo "Examples built"

install:
	# Replace the lib dependency with the locally built pack
	pnpm add [package-name]@file:../lib/dist/[package-name]-0.0.1.tgz
	pnpm install

test:
	@echo "Running example tests..."
	cd usage-basic && node index.js

all: build test
```

**`examples/usage-basic/package.json`** (replace `[package-name]`):

```json
{
  "name": "usage-basic",
  "version": "1.0.0",
  "description": "Basic usage example for [package-name]",
  "type": "module",
  "scripts": {},
  "dependencies": {
    "[package-name]": "file:../../lib/dist/[package-name]-0.0.1.tgz"
  }
}
```

**`examples/usage-basic/index.js`**:

```javascript
import { hello } from '[package-name]';

const result = hello('world');
console.log(result);
// expected output: Hello, world!
```

---

### Phase 5: Create `README.md`

Quick Start must appear at the top — it is rendered first on the npm registry page.

```markdown
# [package-name]

[description]

## Quick Start

\`\`\`bash
pnpm add [package-name]
\`\`\`

\`\`\`typescript
import { hello } from '[package-name]';

const greeting = hello('world');
console.log(greeting); // Hello, world!
\`\`\`

## Installation

\`\`\`bash
npm install [package-name]
# or
pnpm add [package-name]
\`\`\`

## Examples

See the [examples/](examples/) folder for complete runnable examples.

## License

MIT
```

---

### Phase 6: Verify

Review all created files and confirm:

- [ ] Root `Makefile` delegates to both `lib/` and `examples/`
- [ ] `lib/src/index.ts` exports at least one symbol
- [ ] `lib/src/index.test.ts` has at least one passing test
- [ ] `lib/package.json` has `main`, `types`, and `files` set correctly
- [ ] `README.md` starts with Quick Start containing a code example
- [ ] All `[package-name]` placeholders are replaced with the actual name
- [ ] Structure matches the layout in [_core-edr-003](../../003-javascript-project-tooling.md)

## Examples

**User:** "Create a new TypeScript library project called `retry-client`"

**Agent action:** Gathers: name=`retry-client`, default Node.js 24, then creates:
- `./Makefile`, `./.nvmrc`, `./.gitignore`
- `lib/src/index.ts`, `lib/src/index.test.ts`, `lib/Makefile`, `lib/package.json`, `lib/tsconfig.json`, `lib/jest.config.js`, `lib/eslint.config.js`
- `examples/Makefile`, `examples/usage-basic/package.json`, `examples/usage-basic/index.js`
- `README.md` (Quick Start first)

All `[package-name]` replaced with `retry-client`.

## Edge Cases

- **Existing files** — skip creation; adapt references to the existing structure
- **Different Node.js version** — update `.nvmrc` and `tsconfig.json` `extends` (e.g. `@tsconfig/node22`)
- **CLI tool** — add `"bin": "dist/main.js"` to `package.json` and create `lib/src/main.ts` as the CLI entry point; add `esbuild` bundle target in `lib/Makefile`
- **No examples needed** — omit the `examples/` directory; remove the `examples` delegation from root `Makefile`
- **Binary bundling (Lambda/browser)** — add an esbuild step to `lib/Makefile`: `pnpm exec esbuild src/main.ts --bundle --platform=node --outfile=dist/bundle.js`
