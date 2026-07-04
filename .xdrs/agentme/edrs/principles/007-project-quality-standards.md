---
name: agentme-edr-policy-007-project-quality-standards
description: Defines minimum project quality standards for README onboarding, testing (unit, integration, and AI-tier evals), linting, XDR compliance, and runnable examples. Use when scaffolding or reviewing projects.
apply-to: All projects
valid-from: 2026-05-25
---

# agentme-edr-policy-007: Project quality standards

## Context and Problem Statement

Without a baseline quality bar, projects within the same organization can diverge significantly in documentation completeness, test coverage, linting discipline, and structural clarity. New developers encounter confusion, quality regressions slip through, and standards drift over time.

What minimum quality standards must every project in the organization meet to ensure it is understandable, maintainable, and consistently verifiable?

## Decision Outcome

Every project must meet the minimum quality standards: a Getting Started section in its README, unit tests that run on every release, compliance with workspace XDRs, active linting enforcement, a structure that is clear to new developers, and — for libraries and utilities — a runnable examples folder verified on every test run. Integration tests are advised but not required. Projects with statistical models must have evaluation targets with performance thresholds.

These standards form a non-negotiable baseline. Individual projects may raise the bar but must never fall below it.

### Details

#### 01-readme-must-have-getting-started

`README.md` must include a **Getting Started** section in the first 20 lines with the minimal steps to install and use the project.

**Required content:**
- Installation or setup command(s)
- At least one runnable usage example (code snippet, CLI command, or API call)

**Required README structure:**

````markdown
# Project Name

One-line description.

## Getting Started

```sh
npm install my-package
```

```ts
import { myFunction } from "my-package";
myFunction({ input: "value" });
```
````

---

#### 02-unit-tests-must-run-on-every-release

A unit test suite must run automatically before every release. Failing tests must block the release — no silent skips or overrides.

**Requirements:**
- A `make test` target must exist and run the full suite
- CI/CD must invoke it before publish/deploy
- Test failures block the release

**Exception:** Projects with fewer than 100 lines of code, or whose `README.md` prominently marks them as a **Spike** or **Experiment**, are exempt from this requirement. Such projects must never be deployed to production.

**Reference:** [agentme-edr-004](004-unit-test-requirements.md) for detailed unit test requirements.

---

#### 03-project-must-comply-with-xdrs

All XDRs that apply to the project's scope (as listed in [.xdrs/index.md](../../../index.md)) must be followed. A deviation requires a project-local XDR documenting the override.

**Requirements:**
- Review applicable XDRs before any significant implementation
- If an XDR conflicts with project needs, create a `_local` XDR documenting the deviation

---

#### 04-project-must-have-linting

Projects larger than 10 files or 200 lines of code must have a linter configured and actively enforced. Lint failures block CI builds.

**Requirements:**
- `make lint` runs the linter with zero-warning tolerance
- `make lint-fix` auto-fixes fixable issues
- Linter config is checked in (e.g., `.eslintrc.js`, `pyproject.toml`, `.golangci.yml`)
- CI runs `make lint` before merging or releasing

**Exception:** Projects with fewer than 100 lines of code, or whose `README.md` prominently marks them as a **Spike** or **Experiment**, are exempt from this requirement. Such projects must never be deployed to production.

**Reference:** [agentme-edr-003](../application/003-javascript-project-tooling.md) for JavaScript-specific tooling.

---

#### 05-project-structure-must-be-clear

Directory and file layout must be self-explanatory: source code, tests, configuration, and examples must be clearly separated and named.

**Requirements:**
- Directory names must reflect their purpose (`src/`, `lib/`, `tests/`, `examples/`, `docs/`)
- README must describe the top-level layout if non-obvious
- No orphaned or unexplained directories or files at the project root

**Example layout (TypeScript project):**

```
/
├── README.md
├── Makefile
├── lib/
│   └── src/
│       ├── index.ts
│       └── *.test.ts
└── examples/
    └── basic-usage/
```

---

#### 06-libraries-must-have-runnable-examples

Projects that are libraries or shared utilities must include an `examples/` directory. Each subdirectory represents a usage scenario and must be independently runnable. Examples that are "offline" (require no external credentials, no running servers, no paid APIs, and no environment-specific configuration outside the repository) must be executed as part of `make test`. Examples that depend on external entities may be left out of `make test`.

**Requirements:**
- `examples/` must contain at least one subdirectory per major usage scenario
- Each scenario subdirectory must have a `Makefile` with a `run` target
- Examples must import the library as an external consumer (not via relative `../src` imports)
- `make test` in the root must run all offline examples; failures block CI and releases
- Examples that depend on external entities must not be included in `make test`

**Directory layout:**

```
/
├── Makefile
├── lib/src/
└── examples/
    ├── Makefile
    ├── basic-usage/
    │   ├── Makefile      # targets: run
    │   └── main.ts
    └── advanced-usage/
        ├── Makefile      # targets: run
        └── main.ts
```

**Root Makefile:**

```makefile
# test-examples runs the examples offline (no external services) → include in test
test: test-unit test-examples

test-unit:
	$(MAKE) -C lib test

test-examples:
	$(MAKE) -C examples
```

If examples require live services or credentials, remove `test-examples` from the `test` dependency list and keep it as a standalone named target only. See [agentme-edr-008](../devops/008-common-targets.md) rule 08 for the full offline/online decision table.

**Examples Makefile:**

```makefile
all:
	$(MAKE) -C basic-usage run
	$(MAKE) -C advanced-usage run
```

---

#### 07-statistical-models-must-have-eval-targets

Projects that contain statistical models (e.g., ML models, LLM-based evaluators, classifiers, ranking systems, or any component whose output quality is measured probabilistically) must define measurable performance thresholds and verify them automatically.

**Requirements:**
- A `make eval` target must exist and execute all performance evaluations
- Each evaluation must have a **documented minimum performance threshold** (e.g., accuracy ≥ 0.85, F1 ≥ 0.80, BLEU ≥ 0.70)
- Thresholds must be declared explicitly in the project (e.g., in a config file, `Makefile` variable, or documented in `README.md`)
- `make eval` must **exit with a non-zero status** (fail) if:
  - The evaluation cannot be executed (missing data, environment errors, model load failures)
  - Any metric falls below its defined minimum threshold
- CI/CD must invoke `make eval` before releasing any version that changes model weights, prompts, or evaluation logic

**Threshold declaration example (Makefile):**

```makefile
EVAL_MIN_ACCURACY := 0.85
EVAL_MIN_F1       := 0.80

eval:
	python eval.py \
	  --min-accuracy $(EVAL_MIN_ACCURACY) \
	  --min-f1 $(EVAL_MIN_F1) \
	  || (echo "Evaluation failed: metrics below threshold"; exit 1)
```

---

#### 08-integration-tests-are-advised

Integration tests verify end-to-end system behavior with real external dependencies (databases, APIs, message queues, file systems, cloud services). While not required, integration tests are strongly advised for projects that interact with external systems.

**When to implement integration tests:**

- The project makes calls to external APIs or services
- The project reads from or writes to databases
- The project integrates with third-party systems (payment processors, authentication providers, etc.)
- The project's behavior depends on the interaction between multiple components or services
- Unit tests alone cannot adequately verify system integration points

**Integration test guidelines (when implemented):**

- SHOULD verify end-to-end execution with real external dependencies or containerized equivalents (e.g., postgres in Docker, localstack for AWS services)
- SHOULD use pass/fail assertions to validate expected behavior and error handling
- SHOULD be isolated from unit tests to allow independent execution
- Files SHOULD be named with a clear integration test suffix (e.g., `<name>_integration_test.py`, `<name>.integration.test.ts`)
- MAY be run less frequently than unit tests (e.g., nightly, before releases) to manage execution time and external dependency costs
- MAY use smaller or cheaper configurations of external services when available (e.g., smaller database instances, development-tier API keys)

**Makefile target:**

When integration tests exist, provide a dedicated `make test-integration` target:

```makefile
test: test-unit

test-unit:
	# Run fast offline unit tests
	pytest lib/src/

test-integration:
	# Run integration tests with real dependencies
	pytest lib/src/ -m integration
```

Projects are not required to implement integration tests, but when present, they SHOULD follow these conventions for consistency across the codebase.

---

#### 09-ai-project-testing-requirements

AI projects are classified into three tiers — LLM, Agent, and Workflow — defined in [agentme-edr-018](../application/018-ai-llm-development-standards.md). Testing requirements differ per tier:

| Tier | Unit tests | Evals | Integration tests |
|---|---|---|---|
| **LLM** ([agentme-edr-018](../application/018-ai-llm-development-standards.md)) | Not required | Not required; SHOULD be used when critical prompts are in use to measure accuracy and detect model drift | Not required |
| **Agent** ([agentme-edr-019](../application/019-ai-agents-development-standards.md)) | Not required | Not required; MAY be used | Not required |
| **Workflow** ([agentme-edr-021](../application/021-ai-workflow-development-standards.md)) | **Required** — see below | **Required** before every release; failed evals block release | Advised |

**Workflow unit test requirements:**

- MUST use mocked LLM providers. See [agentme-edr-018](../application/018-ai-llm-development-standards.md) rule `04-unit-test-mocking` for the mocking pattern.
- MUST run offline with no external dependencies per [agentme-edr-004](004-unit-test-requirements.md) rule `02-must-run-offline`.
- MUST achieve 80% code coverage per [agentme-edr-004](004-unit-test-requirements.md) rule `03-must-maintain-80-percent-coverage`.
- MUST test workflow routing logic, conditional edges, state transformations, and error handling.
- MUST achieve **80% coverage of LangGraph graph edges and branches**: every conditional edge MUST have test cases covering each possible branch, and every node→node transition MUST be exercised by at least one test.
- Files MUST be named `<name>_test.py` and placed alongside the source file per [agentme-edr-004](004-unit-test-requirements.md) rule `04-must-place-test-files-alongside-source`.

**Workflow eval requirements:**

- Evals MUST be executed before every release.
- Accuracy below project-defined thresholds MUST block the release. Thresholds MUST be documented in the eval Makefile or README.
- Evals MUST run against real LLM providers (not mocks) to capture model drift.
- For eval folder structure and script requirements, see [agentme-edr-028](../application/028-ai-eval-standards.md).
- For the taxonomy of AI test types (safety, responsible-AI, quality-eval, prompt, code-level) and the golden dataset entry format, see [agentme-edr-030](../application/030-ai-test-types-taxonomy.md).
