---
skill: create-javascript-project
skill-version: "1.1.0"
---

## Test Scenarios

### Scenario 1: Create a new TypeScript library, happy path

**Trigger / Input**

"Create a new TypeScript library project called `retry-client`."

**Expected Behaviour**

1. Phase 1 gathers or infers the package name (`retry-client`), description, author, and Node.js
   version (default `24`).
2. Phase 2 creates the root `Makefile` (delegating to `lib/` then `examples/`), `.mise.toml`, and
   `.gitignore` ignoring `node_modules/`, `dist/`, and `.cache/`.
3. Phase 3 creates `lib/src/index.ts`, `lib/src/index.test.ts`, `lib/Makefile`, `lib/package.json`
   (without `"type": "module"`), `lib/tsconfig.json`, `lib/jest.config.js`, and
   `lib/eslint.config.mjs` pointing `parserOptions.project` at `tsconfig.json`.
4. Phase 4 creates `examples/Makefile` and `examples/usage-basic/` consuming the packed tarball
   from `lib/dist/`.
5. Phase 5 creates the workspace `README.md` and `lib/README.md` with Quick Start first.
6. Phase 6 verifies the Phase 6 checklist, including that `lib/src/index.ts` exports at least one
   symbol and all `[package-name]` placeholders are replaced with `retry-client`.

**Assertions**

- [ ] Output creates a root `Makefile` that delegates every target to `lib/` and then `examples/`.
- [ ] Output creates `lib/eslint.config.mjs` with `parserOptions.project` set to
      `['./tsconfig.json']` and no duplicated closing syntax.
- [ ] Output keeps `lib/package.json` without `"type": "module"` while using `eslint.config.mjs` as
      the ESLint entry point.
- [ ] Output replaces every `[package-name]` placeholder with `retry-client` across the generated
      files.

### Scenario 2: CLI tool request adds a bin entry and bundling step

**Trigger / Input**

"Scaffold a JavaScript CLI tool called `snap-cli`."

**Expected Behaviour**

Per the Edge Cases entry for CLI tools, the skill adds a `"bin"` field to `lib/package.json`
pointing at the built output, creates `lib/src/main.ts` as the CLI entry point, and adds an
esbuild bundling step to `lib/Makefile` rather than relying on the plain `tsc` build alone.

**Assertions**

- [ ] Output adds a `"bin"` field to `lib/package.json` referencing the built CLI entry point.
- [ ] Output creates `lib/src/main.ts` as the CLI entry point and adds an esbuild bundle step to
      `lib/Makefile`.

### Scenario 3: "No examples needed" removes the examples delegation cleanly

**Trigger / Input**

"Create a TypeScript library called `token-cache` but skip the examples project."

**Expected Behaviour**

Per the Edge Cases entry for omitting examples, the skill does not create the `examples/`
directory and removes the `examples` delegation step from the root `Makefile`, while still
creating the full `lib/` structure and root `README.md`.

**Assertions**

- [ ] Output does not create an `examples/` directory.
- [ ] Output's root `Makefile` does not include a delegation step to `examples/`.
