---
name: agentme-edr-003-javascript-project-tooling-and-structure
description: Defines the standard JavaScript and TypeScript project toolchain and layout using Mise, pnpm, TypeScript, ESLint, Jest, and Makefiles. Use when scaffolding or reviewing JavaScript projects.
---

# agentme-edr-003: JavaScript project tooling and structure

## Context and Problem Statement

JavaScript/TypeScript projects accumulate inconsistent tooling configurations, making onboarding, quality enforcement, and cross-project maintenance unnecessarily hard.

What tooling and project structure should JavaScript/TypeScript projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Node.js and pnpm toolchain together with pnpm, tsc, esbuild, eslint, and jest in a module-root layout that follows [agentme-edr-016](../principles/016-cross-language-module-structure.md), with runnable usage examples in sibling `examples/` folders and Makefiles as the only entry points.**

Clear, consistent tooling and layout enable fast onboarding, reliable CI pipelines, and a predictable developer experience across projects.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Mandatory tool version management and command runner for Node.js, pnpm, and project CLIs |
| **pnpm** | Package manager — strict linking, workspace support, fast installs |
| **tsc** | TypeScript compilation — type checking, declaration generation |
| **esbuild** | Bundling — fast bundling for distribution or single-binary outputs |
| **eslint** | Linting — code style and quality enforcement |
| **jest** | Testing — unit and integration test runner |

All commands are run exclusively through Makefiles, not through `package.json` scripts. The repository root MUST define a `.mise.toml` that pins at least Node.js and pnpm. Contributors and CI MUST install the base toolchain with `mise install` and run routine Makefile targets through `mise exec -- make <target>` or from an activated Mise shell. Using host-installed `node`, `pnpm`, or other project CLIs directly for routine project work is not allowed.

#### ESLint

Use `lib/eslint.config.mjs` as the ESLint entry point and configure it with `@stutzlab/eslint-config` plus `FlatCompat` from `@eslint/eslintrc`. Keep `package.json` in CommonJS mode without adding `"type": "module"`.

In flat-config mode, Makefile lint targets MUST NOT use `--ext`; file matching is defined in `eslint.config.mjs` instead. The flat config MUST declare TypeScript file globs such as `src/**/*.ts` and point `parserOptions.project` to `./tsconfig.json`.

#### TypeScript and Jest

Use a single `lib/tsconfig.json` for both build and type-aware linting. Keep co-located `*.test.ts` files included in that config so ESLint can resolve them through `parserOptions.project`, and rely on the Makefile cleanup step to remove compiled test artifacts from `dist/` after `tsc` runs.

When `tsconfig.json` extends `@tsconfig/node24/tsconfig.json`, the default `module` is `nodenext`. `ts-jest` still runs in CommonJS mode by default, so `lib/jest.config.js` MUST configure the `ts-jest` transform with an inline `tsconfig` override that sets `module: 'commonjs'`. Do not use the deprecated `globals['ts-jest']` configuration style.

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
│       ├── index.ts       # public API re-exports
│       └── *.test.ts      # test files co-located with source
├── examples/              # runnable usage examples outside the module root
│   ├── Makefile           # build + test all examples in sequence
│   ├── usage-x/           # first example
│   │   └── package.json
│   └── usage-y/           # second example
│       └── package.json
├── tests_integration/     # optional cross-example or cross-module integration tests
└── tests_benchmark/       # optional benchmark harnesses
```

The root `Makefile` delegates every target to `/lib` then `/examples` in sequence and is expected to execute module commands inside the repository's Mise-managed environment.

When a repository contains multiple JavaScript/TypeScript packages, each package MUST live in its own module folder such as `lib/my-package/` or `services/my-service/`, each with its own `Makefile`, `README.md`, `dist/`, and `.cache/`.

Persistent caches MUST live under `.cache/`. Recommended locations are Jest `cacheDirectory`, ESLint `--cache-location`, TypeScript `tsBuildInfoFile`, and coverage outputs.

The commands below MUST be invoked through `mise exec -- make <target>` or from an activated Mise shell.

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
| `clean` | remove `node_modules/`, `dist/`, and `.cache/` |
| `all` | `build lint test` |
| `publish` | version-bump with `monotag`, then `npm publish --provenance` |

#### lib/package.json key fields

- `"main"`: `dist/index.js`
- `"types"`: `dist/index.d.ts`
- `"files"`: `["dist/**", "package.json", "README.md"]`
- `"scripts"`: empty — all commands are driven by the Makefile

#### examples/

Each sub-folder under `examples/` is an independent package. The Makefile installs the locally built `.tgz` pack from `lib/dist/` so examples simulate real external usage.

Examples MUST remain outside the module root and MUST consume the package through the packed artifact in `dist/`, never through `../src` imports or other direct source links.

Module-specific integration tests that are not just runnable examples belong in `lib/tests_integration/` or a sibling `tests_integration/` when they cover multiple modules.

Benchmarks belong in `lib/tests_benchmark/` when they require dedicated harnesses; simple micro-benchmarks may stay co-located only if the local testing stack makes that idiomatic.

The examples folder MUST exist for any libraries and utilities that are published or have more than 500 lines of code

### Related Skills

- [001-create-javascript-project](skills/001-create-javascript-project/SKILL.md) — scaffolds a new project following this structure

