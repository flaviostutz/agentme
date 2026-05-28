---
name: agentme-edr-policy-003-javascript-project-tooling-and-structure
description: Defines the standard JavaScript and TypeScript project toolchain and layout using Mise, pnpm, TypeScript, ESLint, Jest, and Makefiles. Use when scaffolding or reviewing JavaScript projects.
apply-to: JavaScript and TypeScript projects
valid-from: 2026-05-25
---

# agentme-edr-policy-003: JavaScript project tooling and structure

## Context and Problem Statement

JavaScript/TypeScript projects accumulate inconsistent tooling configurations, making onboarding, quality enforcement, and cross-project maintenance unnecessarily hard.

What tooling and project structure should JavaScript/TypeScript projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Node.js and pnpm toolchain together with pnpm, tsc, esbuild, eslint, and jest in a module-root layout that follows [agentme-edr-016](../principles/016-cross-language-module-structure.md), with runnable usage examples in sibling `examples/` folders and Makefiles as the only entry points.**

Clear, consistent tooling and layout enable fast onboarding, reliable CI pipelines, and a predictable developer experience across projects.

### Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Mandatory tool version management and command runner for Node.js, pnpm, and project CLIs |
| **pnpm** | Package manager — strict linking, workspace support, fast installs |
| **tsc** | TypeScript compilation — type checking, declaration generation |
| **esbuild** | Bundling — fast bundling for distribution or single-binary outputs |
| **eslint** | Linting — code style and quality enforcement |
| **jest** | Testing — unit and integration test runner |

All commands are run exclusively through Makefiles, not through `package.json` scripts. The repository root MUST define a `.mise.toml` that pins at least Node.js and pnpm. Contributors and CI MUST bootstrap with `make setup` or `mise install`, then invoke routine work with `make <target>`. Each Makefile recipe MUST execute the underlying tool through `mise exec -- <tool> ...`, following [agentme-edr-017](../devops/017-tool-execution-and-scripting.md). Calling project tools directly in docs, CI, or daily workflows instead of `make <target>` is not allowed.

#### ESLint

Use `lib/eslint.config.mjs` as the ESLint entry point and configure it with `@stutzlab/eslint-config` plus `FlatCompat` from `@eslint/eslintrc`. Keep `package.json` in CommonJS mode without adding `"type": "module"`.

In flat-config mode, Makefile lint targets MUST NOT use `--ext`; file matching is defined in `eslint.config.mjs` instead. The flat config MUST declare TypeScript file globs such as `src/**/*.ts` and point `parserOptions.project` to `./tsconfig.json`.

#### TypeScript and Jest

Use a single `lib/tsconfig.json` for both build and type-aware linting. Keep co-located `*.test.ts` files included in that config so ESLint can resolve them through `parserOptions.project`, and rely on the Makefile cleanup step to remove compiled test artifacts from `dist/` after `tsc` runs.

When `tsconfig.json` extends `@tsconfig/node24/tsconfig.json`, the default `module` is `nodenext`. `ts-jest` still runs in CommonJS mode by default, so `lib/jest.config.js` MUST configure the `ts-jest` transform with an inline `tsconfig` override that sets `module: 'commonjs'`. Do not use the deprecated `globals['ts-jest']` configuration style.

#### Coverage

Jest must enforce 80% line and branch coverage, following [agentme-edr-004](../principles/004-unit-test-requirements.md). Configure thresholds in `lib/jest.config.js`:

```js
coverageThreshold: {
  global: {
    lines: 80,
    branches: 80,
  },
},
coverageProvider: 'v8',
coverageDirectory: '.cache/coverage',
```

Builds that miss the threshold must not be merged.

#### Project structure

```
/                          # workspace root or parent aggregation root
├── .mise.toml             # pinned Node.js and pnpm versions
├── .gitignore             # MUST ignore dist/ and .cache/
├── Makefile               # delegates build/lint/test to /lib and /examples
├── README.md              # workspace overview and quickstart
├── lib/                   # one JavaScript/TypeScript module root
│   ├── Makefile           # build, lint, test, publish targets
│   ├── README.md          # package README used for publishing
│   ├── package.json       # package manifest
│   ├── tsconfig.json      # TypeScript config for build and linting
│   ├── jest.config.js     # Jest config
│   ├── eslint.config.mjs  # ESLint config (ESLint 9 flat config)
│   ├── .cache/            # eslint, jest, tsc incremental state, coverage
│   ├── dist/              # compiled files and packed .tgz artifacts
│   └── src/               # all TypeScript source files
│       ├── index.ts       # public API re-exports from app/
│       ├── adapters/      # I/O boundary layer (following agentme-edr-021)
│       │   ├── cli/       # inbound: CLI bootstrap and entry point
│       │   ├── http/      # inbound: HTTP server bootstrap and handlers
│       │   └── connectors/ # outbound: one folder per external resource
│       ├── app/           # core business logic
│       │   └── *.test.ts  # test files co-located with source
│       └── shared/        # infrastructure-agnostic utilities
├── examples/              # runnable usage examples outside the module root
│   ├── Makefile           # build + test all examples in sequence
│   ├── usage-x/           # first example
│   │   └── package.json
│   └── usage-y/           # second example
│       └── package.json
├── tests_integration/     # optional cross-example or cross-module integration tests
└── tests_benchmark/       # optional benchmark harnesses
```

The root `Makefile` delegates every target to `/lib` then `/examples` in sequence. Parent Makefiles should call child Makefiles directly, and each module Makefile is responsible for running its actual tool commands through `mise exec --`.

Internal source code MUST be organized following [agentme-edr-021](021-pragmatic-hexagonal-architecture.md): `adapters/` (inbound and outbound I/O boundaries), `app/` (business logic), and `shared/` (infrastructure-agnostic utilities). The public API entry point (`index.ts`) re-exports from `app/`.

When a repository contains multiple JavaScript/TypeScript packages, each package MUST live in its own module folder such as `lib/my-package/` or `services/my-service/`, each with its own `Makefile`, `README.md`, `dist/`, and `.cache/`.

All tool caches, incremental state files, and workspace-local config outputs MUST be written under `.cache/`. This applies to every tool without exception. Cache and state paths MUST be declared in the tool's own configuration file — never on the command line — so that the location is enforced regardless of how the tool is invoked:

| Tool | Config file | Setting | Value |
|------|------------|---------|-------|
| **Jest** | `jest.config.js` | `cacheDirectory` | `.cache/jest` |
| **ESLint** | `eslint.config.mjs` | `cache: true, cacheLocation: '.cache/eslint'` | (set in config object) |
| **TypeScript** | `tsconfig.json` | `tsBuildInfoFile` | `.cache/tsbuildinfo` |
| **Jest coverage** | `jest.config.js` | `coverageDirectory` | `.cache/coverage` |

No tool MUST write cache or state files to the project root, `src/`, or any other directory outside `.cache/`. Passing cache paths as Makefile or CLI flags instead of config-file settings is not allowed.

Contributors and CI MUST invoke the commands below as `make <target>`. The Makefile recipes themselves MUST call the underlying tools through `mise exec -- <tool> ...`.

#### lib/Makefile targets

| Target | Description |
|--------|-------------|
| `install` | `mise exec -- pnpm install --frozen-lockfile` |
| `build` | `mise exec -- pnpm exec tsc ...`, strip test files from `dist/`, then `mise exec -- pnpm pack` for local use by examples |
| `build-module` | `mise exec -- pnpm exec tsc ...` only (no pack) |
| `lint` | `mise exec -- pnpm exec eslint ./src` |
| `lint-fix` | `mise exec -- pnpm exec eslint ./src --fix` |
| `test` | `mise exec -- pnpm exec jest --verbose --coverage` |
| `test-watch` | `mise exec -- pnpm exec jest --watch` |
| `clean` | remove `node_modules/`, `dist/`, and `.cache/` |
| `all` | `build lint test` |
| `publish` | `mise exec -- npx -y monotag ...`, then `mise exec -- npm publish --provenance` |

#### lib/package.json key fields

- `"main"`: `dist/index.js`
- `"types"`: `dist/index.d.ts`
- `"files"`: `["dist/**", "package.json", "README.md"]`
- `"scripts"`: empty by default. If reverse compatibility requires scripts, each script must be a direct one-line delegation to one Makefile target.

#### examples/

Each sub-folder under `examples/` is an independent package. The Makefile installs the locally built `.tgz` pack from `lib/dist/` so examples simulate real external usage.

Examples MUST remain outside the module root and MUST consume the package through the packed artifact in `dist/`, never through `../src` imports or other direct source links.

Module-specific integration tests that are not just runnable examples belong in `lib/tests_integration/` or a sibling `tests_integration/` when they cover multiple modules.

Benchmarks belong in `lib/tests_benchmark/` when they require dedicated harnesses; simple micro-benchmarks may stay co-located only if the local testing stack makes that idiomatic.

The examples folder MUST exist for any libraries and utilities that are published or have more than 500 lines of code

## References

- [agentme-edr-004](../principles/004-unit-test-requirements.md) — Coverage and unit-test baseline
- [agentme-edr-021](021-pragmatic-hexagonal-architecture.md) — Internal adapter/application layer separation for applications
- [001-create-javascript-project](skills/001-create-javascript-project/SKILL.md) — scaffolds a new project following this structure

