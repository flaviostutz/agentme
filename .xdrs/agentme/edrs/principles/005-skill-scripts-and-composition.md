---
name: agentme-edr-policy-005-skill-scripts-and-composition
description: Defines when a skill step must be a script instead of LLM work (calculations, bulk data, financial operations), how skill scripts are written, checked and bundled (native-first dependencies, ad hoc vs structured modules, Makefiles, root cascade) and how one skill may use another (prose activation only, no cross-skill script access). Use when writing or reviewing a skill that has scripts, steps that compute or generate data, or dependencies on another skill.
apply-to: All skills in the agentme scope and in any scope that directly or transitively follows or extends agentme
valid-from: 2026-10-04
---

# agentme-edr-policy-005: Skill scripts and composition

## Context and Problem Statement

LLM steps that compute, validate or generate data are slow, costly and unreliable, skill scripts often skip the repository's coding, linting and test practices, and skills that call each other's scripts break when renamed or bundled alone. Which skill steps must be scripts, how are scripts built and checked, and how may one skill use another?

## Decision Outcome

**Give the LLM judgement and orchestration and scripts every well-defined task, build scripts as ordinary modules with native-first dependencies, and compose skills through prose activation only**

Skill scripts follow the same coding, layering and Makefile policies as any other software. A skill uses another skill only by activating it in a prose step.

### Details

#### 01-activate-other-skills-in-prose

A skill that depends on another skill MUST activate it with an explicit prose step naming the skill and the goal, for example "Step 4: Run skill `get-github-contents` to list the PR comments." The step MAY pass inputs (URLs, JSON items, file paths) and MUST state which outputs it expects back. The activated skill's own confirmations, halt conditions and known issues apply unchanged.

A bundling-enabled skill MUST list every skill it activates in its `DEPS` per [_core-adr-policy-021](../../../_core/adrs/principles/021-skill-bundling.md).

#### 02-no-cross-skill-script-calls

A skill's scripts MUST NOT execute, `require`/`import`, or read another skill's scripts or files, including by relative path, and MUST NOT depend on another skill's folder layout. Helpers needed by two skills MUST be copied into each skill's own `scripts/` folder, containing only what that skill uses.

#### 03-no-shared-script-library

A shared script library across skills MUST NOT be used: a rename or partial distribution breaks every caller, and callers skip the owning skill's checks.

#### 04-native-first-ladder

Skill scripts, and every library or tool they need, MUST take the first rung of this ladder that works:

1. Language and standard library on the runtimes already provided by mise.
2. A tool fetched on demand with a pinned version (`npx -y <pkg>@<version>`, `uvx <pkg>==<version>`).
3. A library installed into `scripts/` (JS: `pnpm install --prod --frozen-lockfile --ignore-scripts`), only when rungs 1 and 2 cannot do the job. `SKILL.md` MUST then start with a preflight step that checks whether the dependency is present, asks the user once before installing it, and otherwise halts printing the install command.

The same native-first order MUST guide implementation choices, for example the exact-arithmetic ladder of [agentme-edr-105 rule `04`](../application/105-monetary-calculation-precision.md). A missing toolchain manager or CLI (`uv`, `gh`, `az`) MAY be installed environment-wide only after the user is told the exact command and agrees once; otherwise the skill halts printing it. Any other environment-wide install MUST NOT be requested.

#### 05-ad-hoc-or-structured-scripts

The scripts of a skill MUST be treated as **ad hoc** when they stay below the size threshold of [agentme-edr-126](../application/126-pragmatic-hexagonal-architecture.md) rule 07 (fewer than ~400 non-blank, non-test lines in total across `scripts/`, with a single I/O boundary) and as **structured** otherwise. No other threshold exists for skills.

#### 06-ad-hoc-scripts

Ad hoc scripts MAY skip layering only (flat files in `scripts/`). They MUST still:

- follow the coding practices in [agentme-edr-121](../application/121-coding-best-practices.md) to [agentme-edr-125](../application/125-coding-abstraction-practices.md)
- have unit tests with at least 80% coverage and a linter run with a pinned version and a config file kept in `scripts/`
- have a `scripts/Makefile` with `lint`, `test` and `clean` targets and a `scripts/README.md` per [agentme-edr-016](016-cross-language-module-structure.md)

The skill `get-github-contents` is the reference layout.

#### 07-structured-scripts

Structured scripts MUST use `scripts/` as the module root per [agentme-edr-016](016-cross-language-module-structure.md) and [agentme-edr-126](../application/126-pragmatic-hexagonal-architecture.md) (`scripts/src/adapters`, `app`, `shared`) and follow [agentme-edr-101](../application/101-javascript-project-tooling.md) (TypeScript) or [agentme-edr-103](../application/103-python-project-tooling.md) (Python), except build emit and package publishing steps. TypeScript entry points run without a build step: `npx -y tsx@<version> scripts/src/adapters/cli/<name>.ts`.

#### 08-skill-makefile-and-scripts-makefile

A skill that has `scripts/` MUST have a skill Makefile per [_core-adr-policy-021](../../../_core/adrs/principles/021-skill-bundling.md) that delegates `lint`, `test` and `clean` to `scripts/Makefile` (`make -C scripts <target>`); its `clean` MUST also remove `dist`. `scripts/Makefile` owns lint, tests and module build and MUST follow [agentme-edr-303](../platform/303-common-targets.md) and [agentme-edr-304](../platform/304-tool-execution-and-scripting.md).

The skill `build` MUST bundle along its `DEPS` (dependencies built first, then copied) and copy the production dependencies of the scripts module into the bundle (JS: a fresh production `node_modules` install). Python bundles MUST vendor pure-Python dependencies; skills with native dependencies use the rule 04 preflight. A bundle MUST need nothing beyond the runtime and `npx`/`uvx`. `dist`, `.cache` and `node_modules` of skills MUST NOT be committed or published.

#### 09-root-cascade

The repository root Makefile `lint`, `test` and `clean` MUST run the same target in every skill Makefile of every scope except `_core`, sequentially, stopping at the first failure while echoing the failing skill; `lint` runs where a skill Makefile defines it. These targets MUST NOT run in parallel (`make -j`) because builds delete and rebuild shared `dist` folders.

#### 10-script-first-division-of-labour

A skill MUST use the LLM for identifying inputs, reasoning, connecting concepts, deciding complex flows, judging and testing results, creating plans and coordinating tasks. A well-defined task (defined input, deterministic processing, defined output) SHOULD be a script, for example validation, parsing, sorting, counting, deriving names, filling templates from data and fetching. Scripts make the skill faster, cheaper to run, testable and trustworthy; the LLM keeps the reasoning and the adaptation to diverse contexts.

#### 11-mandatory-script-steps

The following steps MUST be performed by a script, never by the LLM in chat, even when they look trivial:

- calculations: arithmetic, scoring, aggregation, date math, rounding, unit and currency conversion
- bulk data: generating or transforming files, tables or lists of more than ~10 records, or any set of records the LLM would otherwise emit one by one from other data
- financial operations, which MUST also follow [agentme-edr-105](../application/105-monetary-calculation-precision.md)

#### 12-llm-input-script-output-contract

Judgement MUST enter a script as structured input (flags, JSON, report cells). The script MUST validate it (ranges, enums, formats), exit non-zero with a clear message on invalid input, and SHOULD support `--json` output. The LLM MUST use the script output as is and MUST NOT override or recompute it; a disagreement is reported to the user. Scripts that write files MUST be idempotent and confined to the skill's output folder.

#### 13-script-failure-and-missing-scripts

When a script for a rule 11 step fails or cannot run, the skill MUST halt and report the command and the error, and MUST NOT fall back to computing in chat. When no packaged script exists for a rule 11 step, the skill MUST write a script under `.work/scripts/` per [_core-adr-policy-003](../../../_core/adrs/principles/003-skill-standards.md), run it, state its path in the result, and SHOULD propose packaging it as a tested script.

#### 14-script-steps-are-tested

Packaged scripts MUST be covered by unit tests per rules 06 and 07. Every `SKILL.test.md` scenario that exercises a script-owned step MUST include an assertion that the skill runs the command for that step and does not compute it in chat, per [agentme-edr-017](017-skill-testing.md).

## References

- [agentme-edr-105](../application/105-monetary-calculation-precision.md) - exact arithmetic for money in scripts
- [agentme-edr-017](017-skill-testing.md) - script-use assertions in `SKILL.test.md`
- [agentme-edr-127](../application/127-external-system-adapter-skills.md) - external system contents skills built on this composition model
- [agentme-edr-126](../application/126-pragmatic-hexagonal-architecture.md) - layering and the size threshold
- [agentme-edr-101](../application/101-javascript-project-tooling.md) and [agentme-edr-103](../application/103-python-project-tooling.md) - language tooling
- [agentme-edr-121](../application/121-coding-best-practices.md) to [agentme-edr-125](../application/125-coding-abstraction-practices.md) - coding practices
- [agentme-edr-016](016-cross-language-module-structure.md) - module structure and README
- [agentme-edr-303](../platform/303-common-targets.md) and [agentme-edr-304](../platform/304-tool-execution-and-scripting.md) - Makefile targets and tool execution
- [_core-adr-policy-021](../../../_core/adrs/principles/021-skill-bundling.md) - skill bundling
- [_core-adr-policy-003](../../../_core/adrs/principles/003-skill-standards.md) - skill standards
