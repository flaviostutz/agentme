# agentkit-edr-003: JavaScript project tooling and structure

## Context and Problem Statement

JavaScript/TypeScript projects accumulate inconsistent tooling configurations, making onboarding, quality enforcement, and cross-project maintenance unnecessarily hard.

What tooling and project structure should JavaScript/TypeScript projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use pnpm, tsc, esbuild, eslint, and jest with a standard layout separating library code (`lib/`) from runnable usage examples (`examples/`), coordinated by root-level Makefiles.**

Clear, consistent tooling and layout enable fast onboarding, reliable CI pipelines, and a predictable developer experience across projects.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **pnpm** | Package manager — strict linking, workspace support, fast installs |
| **tsc** | TypeScript compilation — type checking, declaration generation |
| **esbuild** | Bundling — fast bundling for distribution or single-binary outputs |
| **eslint** | Linting — code style and quality enforcement |
| **jest** | Testing — unit and integration test runner |

All commands are run exclusively through Makefiles, not through `package.json` scripts.

#### ESLint configuration

Use `@stutzlab/eslint-config` as the base ESLint config for all projects.

Install it as a dev dependency:

```bash
pnpm add -D @stutzlab/eslint-config
```

`lib/eslint.config.js`:

```js
// ESLint 9 flat config format
import baseConfig from '@stutzlab/eslint-config';

export default [
  ...baseConfig,
  {
    languageOptions: {
      parserOptions: {
        project: [ './tsconfig.json' ],
        tsconfigRootDir: process.cwd(),
      },
    },
  },
];
```

#### Project structure

```
/                          # workspace root
├── Makefile               # delegates build/lint/test to /lib and /examples
├── README.md              # Quick Start first; used as npm registry page
├── lib/                   # the published npm package
│   ├── Makefile           # build, lint, test, publish targets
│   ├── package.json       # package manifest
│   ├── tsconfig.json      # TypeScript config
│   ├── jest.config.js     # Jest config
│   ├── eslint.config.js   # ESLint config (ESLint 9 flat config)
│   └── src/               # all TypeScript source files
│       ├── index.ts       # public API re-exports
│       └── *.test.ts      # test files co-located with source
└── examples/              # runnable usage examples
    ├── Makefile           # build + test all examples in sequence
    ├── usage-x/           # first example
    │   └── package.json
    └── usage-y/           # second example
        └── package.json
```

#### Root Makefile

Delegates every target to `/lib` then `/examples`:

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

#### lib/Makefile targets

| Target | Description |
|--------|-------------|
| `install` | `pnpm install --frozen-lockfile` |
| `build` | compile with `tsc`, strip test files from `dist/`, then `pnpm pack` for local use by examples |
| `build-module` | compile with `tsc` only (no pack) |
| `lint` | `pnpm exec eslint ./src` |
| `lint-fix` | `pnpm exec eslint ./src --fix` |
| `test` | `pnpm exec jest --verbose` |
| `test-watch` | `pnpm exec jest --watch` |
| `clean` | remove `node_modules/` and `dist/` |
| `all` | `build lint test` |
| `publish` | version-bump with `monotag`, then `npm publish --provenance` |

#### lib/package.json key fields

```json
{
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist/**", "package.json", "README.md"],
  "packageManager": "pnpm@8.x",
  "scripts": {}
}
```

`scripts` is intentionally empty — all commands are driven by the Makefile.

#### examples/Makefile

Each sub-folder under `examples/` is an independent package. The Makefile installs the locally built `.tgz` pack from `lib/dist/` so examples simulate real external usage:

```makefile
SHELL := /bin/bash
%:
	@echo "Unknown target: $@. Ignoring"

build: install
	@echo "Examples built"

install:
	pnpm add [package-name]@file:../lib/dist/[package-name]-0.0.1.tgz
	pnpm install

test:
	@echo "Running example tests..."
	cd usage-x && make test
	cd usage-y && make test

all: build test
```

#### README.md

Must start with a **Quick Start** section containing a minimal working code example. This is the first content rendered on the npm registry page.

```markdown
# package-name

Short one-line description.

## Quick Start

\`\`\`bash
pnpm add package-name
\`\`\`

\`\`\`typescript
import { myFunction } from 'package-name';
const result = myFunction('hello');
\`\`\`

## More sections...
```

### Related Skills

- [001-create-javascript-project](skills/001-create-javascript-project/SKILL.md) — scaffolds a new project following this structure

