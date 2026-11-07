---
name: agentme-edr-policy-152-ai-test-types-taxonomy
description: Maps stable AI eval labels to the objective-based catalogue, distinguishes AI Accuracy from code correctness, and defines golden dataset entries, statistical-method guidance, mocking constraints and component scopes. Use when designing AI evaluation or selecting datasets and scoring methods.
apply-to: AI projects (LLM, Agent, or Workflow tier) implementing AI-specific test types beyond generic code-level unit/integration tests
valid-from: 2026-07-05
---

# agentme-edr-policy-152: AI test types taxonomy

## Context and Problem Statement

AI components need test types beyond generic unit/integration tests (safety, fairness, groundedness, functional accuracy, etc.). Which test types should be named, and how should their datasets and eval tooling work?

## Decision Outcome

**Specialize the objective-based taxonomy of agentme-edr-503 for AI evaluation, retaining a shared golden dataset envelope filtered by `test_types`.**

The catalogue defines what a test assesses; this policy defines how AI eval labels map to it. Golden datasets, scoring methods and mocking constraints specialize execution rather than defining universal test objectives.

### Details

#### 01-golden-dataset-concept

Projects MUST use a golden dataset — all eval case entries used to test an AI component, each labeled with `test_types` (rule `04`). Consumed by [agentme-edr-153](153-ai-eval-script.md) and stored at `evals/<component>/eval-<name>/golden_dataset/` per [agentme-edr-201](../data/201-ml-dataset-structure.md) rule `04`.

#### 02-golden-dataset-entry-envelope

Every golden dataset entry (a JSON file in `golden_dataset/data/`) MUST have this shape, in addition to any project-specific fields:

```json
{
  "$schema": "../dataset.schema.json",
  "test_types": ["functional"],
  "input": "...",
  "expected_output": "...",
  "mock_fixtures": {
    "system_y": [{"123": {"name": "Flavio"}}, {"456": {"name": "Andrew"}}]
  }
}
```

- `test_types` — array, values MUST come from rule `04`'s enum, MUST contain at least one value. An entry MAY carry more than one value additively (e.g. `["functional", "smoke"]`) — no test type excludes another.
- `input` — the prompt string or input parameters (Prompt tier), or input attributes object (Agent/Workflow tier) passed to the component.
- `expected_output` — fields used to score the entry. MUST be `null` when `test_types` contains only `["bias", "repeatability"]` (Schema Rule C); MUST be non-null when any other type is also present (Schema Rule B). When `bias` and `fairness` are combined, used by fairness scoring and IGNORED for bias scoring.
- `mock_fixtures` — optional object; keys identify adapters to mock (SHOULD match `adapters/connectors/<name>`), values are any valid JSON. When present, eval.py MUST configure each mock BEFORE invoking the component, using fresh instances per entry. `mock_fixtures` MUST NOT include LLM adapter keys — LLM calls MUST be real (rule `03`).
- `human_review` — optional boolean; when `true`, requires manual verification IN ADDITION to automated scoring. NOT a test type — can be applied to any entry at any stage.
- `human_instructions` — optional string; MUST be present when `human_review: true` (Schema Rule D). Manual-verification instructions for the reviewer; does not participate in automated scoring.
- `group` — optional string; thematic label for filtering (e.g. `"simple"`, `"edge_cases"`). Used by the `--groups` CLI argument of [agentme-edr-153](153-ai-eval-script.md). Values MUST NOT contain commas.
- `bias_group` — optional string or integer; MUST be present when `test_types` includes `bias` (Schema Rule A). All entries sharing the same value represent the same scenario varying only in EU Charter/GDPR Art.9 protected attributes. Fairness-only entries MUST NOT carry `bias_group`.
- `dataset.schema.json` MUST require `test_types`, `input`, and `expected_output`; `group`, `bias_group`, and `mock_fixtures` MUST be optional. `expected_output` type MUST allow `null`. Four `allOf/if-then` rules MUST enforce: (A) `bias_group` required when `bias` in `test_types`; (B) `expected_output` non-null when any non-exempted type present; (C) `expected_output` null when only `bias`/`repeatability` types present; (D) `human_instructions` required when `human_review: true`. See [agentme-edr-201](../data/201-ml-dataset-structure.md) rule `04`.

#### 03-mocks-allowed-values

The following values describe mocking constraints for AI eval execution and code-level scopes:

| Value | Meaning |
|---|---|
| `mocks allowed` | Fully offline; fakes may replace every dependency including the LLM. Used only for code-level unit tests. |
| `mocks disallowed` | No mocking of any dependency — all real external systems required. Used for integration tests. |
| `mocks disallowed for LLM calls` | **The LLM call MUST be real; all other external dependencies MAY be mocked via `mock_fixtures`.** `mock_fixtures` keys MUST NOT reference LLM adapters. Standard for all golden-dataset eval test types (see rule `08`). |

#### 04-test-types-enum

A golden dataset entry's `test_types` array MUST only use these values: `safety`, `adversarial`, `fairness`, `bias`, `robustness`, `explainability`, `groundedness`, `functional`, `prompt`, `smoke`, `repeatability`. These are stable execution labels: `functional` maps to Accuracy and `prompt` to Regression protection, not new enum values `accuracy` or `regression`. Unit and integration are code-level scopes outside this enum, with no golden dataset entries. A/B experimentation serves Live outcome validation: see [agentme-edr-157](157-ai-a-b-testing.md). Performance remains outside this enum: see [agentme-edr-158](158-ai-performance-testing.md). `human` is NOT a test type — use the `human_review` boolean and `human_instructions` fields instead (rule `02`).

#### 05-test-type-taxonomy

AI execution labels MUST map to the objectives in [agentme-edr-policy-503-test-groups-and-release-flow.07-every-test-type-has-one-main-group](../governance/503-test-groups-and-release-flow.md#07-every-test-type-has-one-main-group), which owns the definitions, AI affinity and primary groups. This table supplies AI-specific applicability, value and method examples, not a second universal catalogue. All eleven eval labels use the golden-dataset mocking constraint of rule `08`.

| `test_types` label | Objective type | AI use / value | Method example | Priority (1-5) |
|---|---|---|---|---|
| `safety` | Safety | User-facing content/actions; avoids harmful or policy-violating behavior | Harmful-input policy rubric | 5 |
| `adversarial` | Adversarial resistance | Tool and agent loops; exposes control-bypass paths | Injection/jailbreak scenarios, unsafe-tool-use checks | 5 |
| `fairness` | Fairness | Segment decisions; exposes business-policy gaps | Independent segment scenarios scored inline; [156](156-ai-eval-fairness-bias.md) | 4 |
| `bias` | Bias / non-discrimination | Decisions/rankings; exposes protected-attribute influence | Paired `bias_group` output comparisons; [156](156-ai-eval-fairness-bias.md) | 3 |
| `robustness` | Robustness | Variable input; checks graceful behavior | Typo, empty and out-of-distribution cases | 3 |
| `explainability` | Explainability | Justified decisions; gives users and auditors checkable rationale | Faithfulness rubric against outcome/evidence | 2 |
| `groundedness` | Groundedness | Retrieval-based answers; detects unsupported claims | Compare claims with retrieved context | 4 |
| `repeatability` | Repeatability | Decision-critical stochastic output; detects sampling sensitivity | Repeated semantic comparison; [155](155-ai-eval-repeatability.md) | 3 |
| `functional` | Accuracy | Task-quality evidence before release; detects model/provider/prompt degradation | Representative golden cases and task-appropriate scoring; rule `12` | 5 |
| `smoke` | Smoke | Cheap early warning before fuller evals | A small critical golden-case subset | 4 |
| `prompt` | Regression protection | Prompt/model changes; protects required behavior | Replay cases across versions | 3 |

Code-level unit and integration testing remain scopes with their existing mocking constraints (rule `03`), not additional eval labels. Unit testing provides cheap offline logic checks (priority 5); integration testing checks real system wiring (priority 2). Performance (priority 3) uses its own module/dataset under [158](158-ai-performance-testing.md); its real-LLM default and allowed mocking exception remain there.

**Human review modifier:** `human_review: true` is NOT a test type and does NOT appear in this table (rule `02`).

#### 06-priority-and-relevance-are-descriptive-only

Priority and applicability/value guidance in rule `05` MUST NOT be treated as mandating which test types a project implements. [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09` remains the only tier-level testing requirement. Once a project chooses to implement a test type, [agentme-edr-153](153-ai-eval-script.md) rule `01`'s failing-threshold behavior applies; the specific threshold is a project/business decision.

#### 07-smoke-is-distinct-from-test-smoke

The `smoke` eval type (`eval-smoke` Makefile target) MUST NOT be conflated with [agentme-edr-303](../platform/303-common-targets.md)'s `test-smoke` code-level target. Both MAY coexist.

#### 08-eval-mocking-constraint

For every golden-dataset eval test type: **the LLM call MUST be real; all other external dependencies MUST be mocked via `mock_fixtures`.** `mock_fixtures` keys MUST NOT reference LLM adapters. This applies equally to entries with `human_review: true`. Code-level unit tests are the correct place for fully offline, LLM-mocked testing.

#### 09-repeatability-vs-reproducibility

| Property | Definition | What varies | Measured by |
|---|---|---|---|
| **Repeatability** | Output stability across N invocations at non-zero temperature | Model sampling variance | `repeatability` test type per [agentme-edr-155](155-ai-eval-repeatability.md) |
| **Reproducibility** | Deterministic output at temperature = 0 with fixed seed | Nothing — any variance is a config bug | Not a golden-dataset type; verified via config, documented in [agentme-edr-305](../platform/305-environment-variable-configuration.md) |

A component may satisfy reproducibility yet still need repeatability tests for its production configuration (temperature > 0). The `repeatability` test type MUST NOT be applied to components with intentionally diverse output.

#### 10-test-scope-levels

Test types can be applied at three distinct scopes, matching the AI component tiers defined in [agentme-edr-141](141-ai-llm-development-standards.md):

| Scope | Description | Example eval target |
|---|---|---|
| **Workflow tier** | End-to-end, black-box test of a full LangGraph workflow | The complete document-review workflow: input document → final approval decision |
| **Agent tier** | Test of a specific deepagents agent or LangGraph node in isolation | The CRM-lookup agent node: input query → retrieved contact record |
| **LLM tier** | Test of a single prompt-response exchange | The classification prompt: input text → category label |

**Each tier requires fully independent evals and golden datasets** scoped per component (not shared across tiers), because input structure, expected output, and relevant test types differ across tiers.

**Workflow-first strategy:** Testing SHOULD start at the Workflow tier (one black-box eval covers the whole stack) and drill down to the Agent or LLM tier only for critical, complex (multi-step tool use) or hard-to-debug nodes or prompts.

All `test_types` values apply at all three tiers. Some have natural tier affinity (guidance, not restrictions):

| Test type | Natural tier affinity | Rationale |
|---|---|---|
| `prompt` | LLM tier, Agent tier | Prompt regression is most directly actionable at the level where the prompt template lives |
| `groundedness` | Agent tier (RAG node) | RAG retrieval happens at a specific node; groundedness is most precisely measured there |
| `adversarial` | Agent tier | Tool-invocation loops are the primary attack surface for injection and jailbreaks |

**Unit tests across tiers:** Apply at all three tiers with different mock setups (see [agentme-edr-141](141-ai-llm-development-standards.md) rule `04`, [agentme-edr-143](143-ai-agents-quality-standards.md) rule `04`, [agentme-edr-144](144-ai-workflow-development-standards.md) rule `10`).

#### 11-test-quality-progression

The following progression distinguishes code-level scopes from objective types and guides implementation priority and tech debt ordering.

This ordering is orthogonal to the Priority column in rule `05` and does NOT override it.

All edges are SHOULD relationships — advisory guidance for prioritization and tech debt conversations. They MUST NOT be treated as hard enforcement gates.

```
[code-level] Unit Test
    └──> [code-level] Integration Test
              └──> Smoke
                    └──> Accuracy / Regression protection
                              ├──> Safety
                              ├──> Adversarial resistance
                              ├──> Groundedness
                              ├──> Explainability
                              ├──> Robustness
                              ├──> Fairness
                              ├──> Performance
                              └──> Repeatability
                                        └──> Bias
```

**Rationale per dependency:**

| Dependency | Rationale |
|---|---|
| Unit / Integration → Smoke | Code correctness is a prerequisite; a component that crashes or errors will produce meaningless eval signal |
| Smoke → Accuracy / Regression protection | Smoke validates the critical subset; running full evals on a fundamentally broken component wastes LLM cost |
| Accuracy / Regression protection → Safety, Adversarial resistance, Groundedness, Explainability, Robustness, Fairness | A broken baseline produces unreliable responsible-AI signals |
| Accuracy / Regression protection → Repeatability | A working baseline makes variance results interpretable |
| Accuracy / Regression protection → Performance | Load results need a working baseline |
| Repeatability → Bias | Bias scoring compares outputs across protected-attribute groups; if not repeatable, output differences may reflect sampling variance rather than protected-attribute influence |

**Fairness does NOT depend on Repeatability.** Fairness entries are per-entry LLM-as-judge tests, unaffected by cross-invocation variance.

**`human_review: true` is NOT part of this progression** — it is a per-entry modifier applicable at any stage.

#### 12-accuracy-needs-statistical-evidence

Accuracy MUST be distinguished from Functional correctness and Repeatability. Code-path, schema and contract assertions do not establish how reliably stochastic model outputs satisfy task-quality criteria across representative inputs. A model can be consistently wrong or give different equally correct answers. The stable `functional` label, `eval-functional` target and `report-functional.md` name refer to Accuracy; their interfaces and scoring contracts remain unchanged.

Accuracy evaluation design SHOULD document:

- intended population, representative sampling and important scenario slices, including rare/high-impact cases; distinguish targeted challenge sets from prevalence estimates;
- dependable expected outcomes or rubrics that allow valid alternative answers;
- scoring-method suitability: exact assertions for objective fields, task rubrics or semantic comparison for open responses, with judge agreement checked against trusted reviewed examples; follow [151](151-ai-eval-standards.md) for LLM-judge output contracts;
- stochastic configuration and how output variation affects the conclusion; repeated sampling can help but does not replace coverage of distinct inputs;
- project-specific sample-sufficiency rationale and acceptance thresholds, using the confidence intervals and convergence reporting of [154](154-ai-eval-report-format.md).

A large dataset alone does not establish representativeness. Repeated trials on a few inputs are not independent coverage of more scenarios; estimates SHOULD state their sampling limitations. There is no universal minimum sample count or new repeated-call loop here; [153](153-ai-eval-script.md) and [155](155-ai-eval-repeatability.md) retain their execution rules.

## References

- [agentme-edr-201](../data/201-ml-dataset-structure.md) — Golden dataset file layout and schema-lint validation
- [agentme-edr-151](151-ai-eval-standards.md) — Eval folder structure and LLM-as-judge scoring contract
- [agentme-edr-153](153-ai-eval-script.md) — Eval script: `--type` filtering, entry-first loop, threshold enforcement
- [agentme-edr-154](154-ai-eval-report-format.md) — Eval report format per test type
- [agentme-edr-155](155-ai-eval-repeatability.md) — Repeatability scoring constants, metrics, and run cadence
- [agentme-edr-126](126-pragmatic-hexagonal-architecture.md) — `_mock` file naming for mock adapters
- [agentme-edr-501](../governance/501-project-quality-standards.md) — Tier-level testing requirements
- [agentme-edr-503](../governance/503-test-groups-and-release-flow.md) — Test groups
- [agentme-edr-303](../platform/303-common-targets.md) — `eval-<qualifier>` Makefile convention
- [agentme-edr-305](../platform/305-environment-variable-configuration.md) — Environment-configuration conventions
- [agentme-edr-141](141-ai-llm-development-standards.md) — LLM tier definition and mocking utilities
- [agentme-edr-122](122-unit-test-requirements.md) — Unit test requirements
- [agentme-edr-156](156-ai-eval-fairness-bias.md) — Fairness/bias eval loop, scoring, and metrics
- [agentme-edr-158](158-ai-performance-testing.md) — AI performance testing
