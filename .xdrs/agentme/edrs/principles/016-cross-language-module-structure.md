---
name: agentme-edr-016-cross-language-module-structure
description: Defines the baseline module-root structure, artifact locations, cache placement, README expectations, examples layout, and test folder conventions across languages. Use when creating or reviewing buildable modules.
---

# agentme-edr-016: Cross-language module structure

## Context and Problem Statement

The language-specific tooling EDRs currently describe similar module layouts in different ways, which causes drift in example placement, cache folders, README expectations, and test organization.

What baseline structure rules must every buildable module follow regardless of language?

## Decision Outcome

**Standardize every buildable module around its own folder root, with `dist/`, `.cache/`, sibling consumer examples, a module README, and predictable test locations.**

Language-specific EDRs may add ecosystem details, but they must not redefine these baseline folder responsibilities.

### Implementation Details

#### 01-module-must-own-folder-root

A module is the smallest independently buildable, testable, or publishable unit. It MUST live in its own folder and that folder MUST contain:

- a `Makefile` following [agentme-edr-008](../devops/008-common-targets.md)
- a `README.md` for the module itself
- all configuration files required to build, lint, test, package, or publish that module
- its generated `dist/` directory when the module produces distributable artifacts
- a module-local `.cache/` when tool caches are not intentionally shared with a parent aggregation root

Example module root:

```text
<module>/
├── Makefile
├── README.md
├── dist/
├── .cache/
└── ... language-specific sources and config ...
```

#### 02-parent-folders-are-aggregation-roots

Parent folders such as a repository root, an application folder, or `lib/` may aggregate multiple modules. They may also hold shared consumer examples or multi-module test harnesses.

They MUST keep the public aggregation obvious: deleting an aggregation folder should remove a coherent API surface or entry-point area, not scatter unrelated internal implementation across the repository.

Recommended aggregation pattern:

```text
<parent>/
├── <module-a>/
├── <module-b>/
├── examples/
├── tests_integration/
└── tests_benchmark/
```

#### 03-build-outputs-must-go-to-dist

Distributable outputs such as packages, wheels, archives, generated binaries, or packed example inputs MUST be written under the module's `dist/` folder.

`dist/` MUST be gitignored.

#### 04-persistent-caches-must-live-under-cache

Tool-generated caches and disposable machine-local state MUST be redirected into the nearest intended `.cache/` folder, either at monorepo level or module level.

Examples include:

- linter caches
- test runner caches
- transpiler incremental state
- formatter caches
- dependency-manager caches when local caching is desired

If a tool cannot natively choose its cache path, the module `Makefile` MUST wrap or clean that tool so persistent cache files do not remain scattered outside `.cache/` after standard targets run.

`.cache/` MUST be gitignored.

#### 05-consumer-examples-must-sit-outside-module

Examples that demonstrate how to consume a library or reusable module MUST live in a sibling `examples/` folder under the nearest aggregation root, not inside the module folder itself.

Examples MUST exercise the module through its public distribution surface:

- use the package built into `dist/` when the ecosystem supports local packaged artifacts
- otherwise use the public module path or equivalent consumer-facing import surface, never relative source-file imports or direct references to internal implementation paths

Example:

```text
lib/
└── mymodule/

examples/
└── using-mymodule/
```

#### 06-module-readme-must-explain-usage-and-development

Each module MUST contain a `README.md` that shows how to use the module as a consumer.

The end of the README MUST also include short developer instructions for that module, covering at least the standard build, lint, and test entry points.

Repository-level READMEs may describe the workspace, but they do not replace the module README.

#### 07-tests-use-predictable-locations

Unit tests SHOULD be co-located with the file they exercise when that is idiomatic and common for the language.

When co-location is uncommon or awkward for the ecosystem, unit tests SHOULD live under `<module>/tests/`.

Integration tests MUST live in one of these locations:

- `<module>/tests_integration/` when they cover one module
- `<parent>/tests_integration/` when they cover multiple sibling modules

Benchmark tests MUST live in one of these locations:

- co-located with the source when the language has a first-class benchmark convention there
- `<module>/tests_benchmark/` for module-specific harnesses or datasets
- `<parent>/tests_benchmark/` when they cover multiple sibling modules

#### 08-module-makefiles-must-expose-shared-targets

Every module `Makefile` MUST expose the common target names from [agentme-edr-008](../devops/008-common-targets.md). At minimum, modules MUST provide `build`, `lint`, and `test`, and SHOULD also provide `all`, `clean`, and `lint-fix` when meaningful.

## References

- [agentme-edr-005](../devops/005-monorepo-structure.md) - Monorepo aggregation and delegation rules
- [agentme-edr-008](../devops/008-common-targets.md) - Shared Makefile target names