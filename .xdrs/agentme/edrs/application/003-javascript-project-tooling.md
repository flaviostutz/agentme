---
name: agentme-edr-003-javascript-project-tooling-and-structure
description: Defines the standard JavaScript and TypeScript project toolchain and layout using Mise, pnpm, TypeScript, ESLint, Jest, and Makefiles. Use when scaffolding or reviewing JavaScript projects.
---

# agentme-edr-003: JavaScript project tooling and structure

## Context and Problem Statement

JavaScript/TypeScript projects accumulate inconsistent tooling configurations, making onboarding, quality enforcement, and cross-project maintenance unnecessarily hard.

What tooling and project structure should JavaScript/TypeScript projects follow to ensure consistency, quality, and ease of development?

## Decision Outcome

**Use a Mise-managed Node.js and pnpm toolchain together with pnpm, tsc, esbuild, eslint, and jest in a standard layout separating library code (`lib/`) from runnable usage examples (`examples/`), coordinated by root-level Makefiles.**

Clear, consistent tooling and layout enable fast onboarding, reliable CI pipelines, and a predictable developer experience across projects.

### Implementation Details

#### Tooling

| Tool | Purpose |
|------|---------|
| **Mise** | Tool version management for Node.js, pnpm, and project CLIs |
| **pnpm** | Package manager — strict linking, workspace support, fast installs |
| **tsc** | TypeScript compilation — type checking, declaration generation |
| **esbuild** | Bundling — fast bundling for distribution or single-binary outputs |
| **eslint** | Linting — code style and quality enforcement |
| **jest** | Testing — unit and integration test runner |

All commands are run exclusively through Makefiles, not through `package.json` scripts. The repository root must define a `.mise.toml` that pins at least Node.js and pnpm, and Makefile targets must run through `mise exec --` or an activated Mise shell.

#### ESLint

Use `lib/eslint.config.mjs` as the ESLint entry point and configure it with `@stutzlab/eslint-config` plus `FlatCompat` from `@eslint/eslintrc`. Keep `package.json` in CommonJS mode without adding `"type": "module"`.

In flat-config mode, Makefile lint targets MUST NOT use `--ext`; file matching is defined in `eslint.config.mjs` instead. The flat config MUST declare TypeScript file globs such as `src/**/*.ts` and point `parserOptions.project` to `./tsconfig.json`.

#### TypeScript and Jest

Use a single `lib/tsconfig.json` for both build and type-aware linting. Keep co-located `*.test.ts` files included in that config so ESLint can resolve them through `parserOptions.project`, and rely on the Makefile cleanup step to remove compiled test artifacts from `dist/` after `tsc` runs.

When `tsconfig.json` extends `@tsconfig/node24/tsconfig.json`, the default `module` is `nodenext`. `ts-jest` still runs in CommonJS mode by default, so `lib/jest.config.js` MUST configure the `ts-jest` transform with an inline `tsconfig` override that sets `module: 'commonjs'`. Do not use the deprecated `globals['ts-jest']` configuration style.

#### Project structure

```
/                          # workspace root
├── .mise.toml             # pinned Node.js and pnpm versions
├── Makefile               # delegates build/lint/test to /lib and /examples
├── README.md              # Quick Start first; used as npm registry page
├── lib/                   # the published npm package
│   ├── Makefile           # build, lint, test, publish targets
│   ├── package.json       # package manifest
│   ├── tsconfig.json      # TypeScript config for build and linting
│   ├── jest.config.js     # Jest config
│   ├── eslint.config.mjs  # ESLint config (ESLint 9 flat config)
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

The root `Makefile` delegates every target to `/lib` then `/examples` in sequence and is expected to execute module commands inside the repository's Mise-managed environment.

The commands below assume they are invoked through `mise exec -- make <target>` or from an activated Mise shell.

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

- `"main"`: `dist/index.js`
- `"types"`: `dist/index.d.ts`
- `"files"`: `["dist/**", "package.json", "README.md"]`
- `"scripts"`: empty — all commands are driven by the Makefile

#### examples/

Each sub-folder under `examples/` is an independent package. The Makefile installs the locally built `.tgz` pack from `lib/dist/` so examples simulate real external usage.

The examples folder MUST exist for any libraries and utilities that are published or have more than 500 lines of code

### Related Skills

- [001-create-javascript-project](skills/001-create-javascript-project/SKILL.md) — scaffolds a new project following this structure

