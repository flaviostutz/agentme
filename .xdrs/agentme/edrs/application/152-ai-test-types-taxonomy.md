---
name: agentme-edr-policy-152-ai-test-types-taxonomy
description: Names AI test types with objective, mocking constraint, and relevance; defines the golden dataset entry envelope for agentme-edr-151's eval tooling; covers three test scopes (Workflow/Agent/LLM) and a quality-progression DAG. Use when deciding which test types to implement, authoring a golden dataset entry, or selecting a test tier.
apply-to: AI projects (LLM, Agent, or Workflow tier) implementing AI-specific test types beyond generic code-level unit/integration tests
valid-from: 2026-07-05
---

# agentme-edr-policy-152: AI test types taxonomy

## Context and Problem Statement

AI components need test types beyond generic unit/integration tests (safety, fairness, groundedness, functional accuracy, etc.). Which test types should be named, and how should their datasets and eval tooling work?

## Decision Outcome

**Adopt a named taxonomy of AI test types plus a shared "golden dataset" entry envelope that agentme-edr-151's eval tooling filters by `test_types`.**

Each test type is named with its objective, mocking constraint, applicability, and relevance; every golden dataset entry is labeled with the test types it applies to.

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

The taxonomy in rule `05` rates each test type using one of three values under the `Mock Constraint` column:

| Value | Meaning |
|---|---|
| `mocks allowed` | Fully offline; fakes may replace every dependency including the LLM. Used only for code-level unit tests. |
| `mocks disallowed` | No mocking of any dependency — all real external systems required. Used for integration tests. |
| `mocks disallowed for LLM calls` | **The LLM call MUST be real; all other external dependencies MAY be mocked via `mock_fixtures`.** `mock_fixtures` keys MUST NOT reference LLM adapters. Standard for all golden-dataset eval test types (see rule `08`). |

#### 04-test-types-enum

A golden dataset entry's `test_types` array MUST only use these values: `safety`, `adversarial`, `fairness`, `bias`, `robustness`, `explainability`, `groundedness`, `functional`, `prompt`, `smoke`, `repeatability`. Unit test and Integration test are NOT in this enum — they are code-level only with no golden dataset entries. `human` is NOT a test type — use the `human_review` boolean and `human_instructions` fields instead (rule `02`).

#### 05-test-type-taxonomy

Test types MUST be selected from this taxonomy. Each test type is named with its group, objective, mocking constraint, applicability, and relevance:

| Test Type Name | `test_types` value | Test Objective | Mock Constraint | When to Apply | Relevance – Business | Relevance – Development Team | Priority (1-5) | Examples |
|---|---|---|---|---|---|---|---|---|
| Safety/content eval | `safety` | Detect harmful, biased, or policy-violating output | mocks disallowed for LLM calls | Any user-facing release | Avoids reputational harm; acceptable-use compliance | Automated content gate before merge/release | 5 | Self-harm input → output flagged; hate-speech prompt → policy-violation score above threshold |
| Adversarial/red-team test | `adversarial` | Probe for prompt injection, jailbreaks, unsafe tool use | mocks disallowed for LLM calls | System exposes tool-invocation or agent loops | Reduces security-incident/breach liability | Finds exploitable tool-loop paths before attackers do | 5 | Prompt injection → detected; crafted input triggering unauthorized tool call → blocked |
| Fairness test | `fairness` | Verify the system handles diverse non-protected groups correctly per business policies. Each entry is an independent policy scenario scored inline via LLM-as-judge against `expected_output`. `bias_group` MUST NOT be present on fairness-only entries. See [agentme-edr-156](156-ai-eval-fairness-bias.md). | mocks disallowed for LLM calls | System makes decisions that may unconsciously exclude population segments; before releases affecting access to services | Detects unconscious policy gaps before they become regulatory or reputational issues | Stress-tests the model against edge-case group scenarios | 4 | Rural farmer loan with farm land as collateral → `{"decision": "approved"}`; self-employed applicant at student credit union → `{"decision": "declined"}` |
| Bias test | `bias` | Certify that EU Charter/GDPR Art.9 protected attributes do NOT influence outcomes. Entries sharing the same `bias_group` vary only in protected attributes; outputs are compared across the group. `expected_output` IGNORED for bias scoring (null on bias-only entries). See [agentme-edr-156](156-ai-eval-fairness-bias.md). | mocks disallowed for LLM calls | Any system producing decisions, rankings, or recommendations; when training data or prompts may encode historical disparities | Lowers legal/regulatory exposure (EU AI Act, GDPR); protects against discriminatory outcomes | Catches protected-attribute influence from training data or prompts | 3 | Same loan with male/female/non-binary names → same approval decision; same resume with different ethnic-background names → same shortlisting outcome |
| Robustness test | `robustness` | Verify stable behavior under noisy/out-of-distribution input | mocks disallowed for LLM calls | Inputs come from untrusted/variable sources | Protects reliability/SLAs | Confirms graceful degradation, guides input validation | 3 | Typo-laden query ("Whta is teh status of ordr 123?") → same intent extracted as clean input; empty string input → graceful error, no crash |
| Explainability test | `explainability` | Verify output is justifiable with a faithful rationale | mocks disallowed for LLM calls | Output must be justified to users/auditors/regulators | Required for auditability; builds user trust | Gives rationale trace for debugging wrong answers | 2 | Recommendation output includes a cited source paragraph; the rationale field semantically supports the conclusion rather than contradicting it |
| Groundedness (RAG) eval | `groundedness` | Verify the answer is supported by retrieved context | mocks disallowed for LLM calls | System uses retrieval-augmented generation | Avoids confidently-wrong answers reaching customers | Pinpoints retrieval/prompt bugs | 4 | Answer "The policy expires on 2025-01-01" is verbatim in retrieved document; no date mentioned in context → answer must not invent one |
| Repeatability test | `repeatability` | Verify output stability across N repeated invocations under fixed configuration | mocks disallowed for LLM calls | Non-deterministic components (temperature > 0) in decision-critical flows | Protects against silently flaky behavior; supports consistency SLAs | Detects prompt/agent designs too sensitive to sampling noise | 3 | Same query 10× at temp=0.7 → semantic similarity ≥ 0.85; same agent task 5× → consistent tool selection |
| Functional eval (golden-dataset accuracy / LLM-as-judge) | `functional` | Measure output correctness against the golden dataset | mocks disallowed for LLM calls | Required before every Workflow release ([agentme-edr-501](../governance/501-project-quality-standards.md) rule `09`); advised elsewhere | Auditable evidence of business correctness before release | Detects regressions from model/provider/prompt changes | 5 | Invoice summary output matches expected `{"total": 450, "currency": "USD"}` within LLM-as-judge rubric; entity extraction returns all required fields |
| Smoke test | `smoke` | Fast pass/fail check on a small, critical subset before running fuller suites | mocks disallowed for LLM calls | Every commit/PR, before functional/responsible-AI evals run | Cheap early warning before slower evals run | Fast, cheap feedback loop | 4 | 3 critical golden entries (happy-path, empty-input, large-input) all pass before CI proceeds to full functional eval |
| Prompt regression test | `prompt` | Detect behavior change when a prompt or model version changes | mocks disallowed for LLM calls | Whenever a prompt template or model version changes | Prevents shipping a worse experience via a "small" tweak | Fast check on every prompt edit | 3 | Prompt v2 vs v1 on 20 entries: output diff reviewed; key fields present in ≥ 95% of v2 responses |
| Integration test | n/a — code-level only (see rule `04`) | Verify real interaction with external systems | mocks disallowed | Component depends on external systems | Reduces production outages from integration mismatches | Catches wiring bugs unit tests can't see | 2 | Agent calls real CRM API and receives a populated contact record; embedding service returns a vector of the expected dimension |
| Unit test (offline, mocked) | n/a — code-level only (see rule `04`) | Verify deterministic logic in isolation, offline | mocks allowed | Required for Workflow tier every commit ([agentme-edr-501](../governance/501-project-quality-standards.md) rule `09`) | Lowest-cost point to catch defects | Fastest, fully offline feedback on every commit | 5 | `extract_date("next Monday")` returns ISO string; `FakeListChatModel` returns canned JSON and parser handles it correctly |

**Human review modifier:** `human_review: true` is NOT a test type and does NOT appear in this table. It adds a manual review layer on top of automated scoring for any entry at any stage.

#### 06-priority-and-relevance-are-descriptive-only

Priority, Relevance, and When to Apply in rule `05` MUST NOT be treated as mandating which test types a project must implement. [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09` remains the only tier-level testing requirement. Once a project chooses to implement a test type, [agentme-edr-153](153-ai-eval-script.md) rule `01`'s failing-threshold behavior applies; the specific threshold is a project/business decision.

#### 07-smoke-is-distinct-from-test-smoke

The `smoke` eval type (`eval-smoke` Makefile target) MUST NOT be conflated with [agentme-edr-303](../platform/303-common-targets.md)'s `test-smoke` code-level target. Both MAY coexist.

#### 08-eval-mocking-constraint

For every golden-dataset eval test type: **the LLM call MUST be real; all other external dependencies MUST be mocked via `mock_fixtures`.** `mock_fixtures` keys MUST NOT reference LLM adapters. This applies equally to entries with `human_review: true`. Code-level unit tests are the correct place for fully offline, LLM-mocked testing.

#### 09-repeatability-vs-reproducibility

| Property | Definition | What varies | Measured by |
|---|---|---|---|
| **Repeatability** | Output stability across N invocations at non-zero temperature | Model sampling variance | `repeatability` test type per [agentme-edr-155](155-ai-eval-repeatability.md) |
| **Reproducibility** | Deterministic output at temperature = 0 with fixed seed | Nothing — any variance is a config bug | Not a golden-dataset type; verified via config, documented in [agentme-edr-305](../platform/305-environment-variable-configuration.md) |

A component may satisfy reproducibility (temperature = 0) yet still need repeatability tests for its production configuration (temperature > 0). The `repeatability` test type MUST NOT be applied to components with intentionally diverse output — variance is correct behavior there.

#### 10-test-scope-levels

Test types can be applied at three distinct scopes, matching the AI component tiers defined in [agentme-edr-141](141-ai-llm-development-standards.md):

| Scope | Description | Example eval target |
|---|---|---|
| **Workflow tier** | End-to-end, black-box test of a full LangGraph workflow | The complete document-review workflow: input document → final approval decision |
| **Agent tier** | Test of a specific deepagents agent or LangGraph node in isolation | The CRM-lookup agent node: input query → retrieved contact record |
| **LLM tier** | Test of a single prompt-response exchange | The classification prompt: input text → category label |

**Each tier requires fully independent evals and golden datasets** scoped per component (not shared across tiers). Input structure, expected output, and relevant test types differ substantially across tiers. Eval folders, golden datasets, and `eval.py` scripts MUST be scoped per component.

**Workflow-first strategy:** Testing SHOULD begin at the Workflow tier (highest cost-benefit: a single black-box eval covers the entire component stack). Drilling down to the Agent or LLM tier SHOULD only be done when a node or prompt is critical (high impact), complex (multi-step tool use), or difficult to debug at the workflow level.

All `test_types` values apply at all three tiers. Some have natural tier affinity (guidance, not restrictions):

| Test type | Natural tier affinity | Rationale |
|---|---|---|
| `prompt` | LLM tier, Agent tier | Prompt regression is most directly actionable at the level where the prompt template lives |
| `groundedness` | Agent tier (RAG node) | RAG retrieval happens at a specific node; groundedness is most precisely measured there |
| `adversarial` | Agent tier | Tool-invocation loops are the primary attack surface for injection and jailbreaks |

**Unit tests across tiers:** Apply at all three tiers with different mock setups (see [agentme-edr-141](141-ai-llm-development-standards.md) rule `04`, [agentme-edr-143](143-ai-agents-quality-standards.md) rule `04`, [agentme-edr-144](144-ai-workflow-development-standards.md) rule `10`).

#### 11-test-quality-progression

The test types form a **quality-progression DAG** that guides implementation priority and tech debt ordering — primarily for deciding which test types to implement first for the best quality signal.

This ordering is orthogonal to the Priority column in rule `05` (standalone business importance) and does NOT override it.

All edges are SHOULD relationships — advisory guidance for prioritization and tech debt conversations. They MUST NOT be treated as hard enforcement gates.

```
[code-level] Unit Test
    └──> [code-level] Integration Test
              └──> Smoke
                    └──> Functional / Prompt
                              ├──> Safety
                              ├──> Adversarial
                              ├──> Groundedness
                              ├──> Explainability
                              ├──> Robustness
                              ├──> Fairness
                              └──> Repeatability
                                        └──> Bias
```

**Rationale per dependency:**

| Dependency | Rationale |
|---|---|
| Unit / Integration → Smoke | Code correctness is a prerequisite; a component that crashes or errors will produce meaningless eval signal |
| Smoke → Functional / Prompt | Smoke validates the critical subset; running full evals on a fundamentally broken component wastes LLM cost |
| Functional / Prompt → Safety, Adversarial, Groundedness, Explainability, Robustness, Fairness | A functionally broken component produces unreliable responsible-AI signals — a working baseline is required |
| Functional / Prompt → Repeatability | Measuring output variance is only meaningful when the component produces correct outputs under normal conditions |
| Repeatability → Bias | Bias scoring compares outputs across protected-attribute groups; if not repeatable, output differences may reflect sampling variance rather than protected-attribute influence |

**Fairness does NOT depend on Repeatability.** Fairness entries are per-entry LLM-as-judge tests, unaffected by cross-invocation variance.

**`human_review: true` is NOT part of this progression** — it is a per-entry modifier applicable at any stage.

## References

- [agentme-edr-201](../data/201-ml-dataset-structure.md) — Golden dataset file layout and schema-lint validation
- [agentme-edr-151](151-ai-eval-standards.md) — Eval folder structure and LLM-as-judge scoring contract
- [agentme-edr-153](153-ai-eval-script.md) — Eval script: `--type` filtering, entry-first loop, threshold enforcement
- [agentme-edr-154](154-ai-eval-report-format.md) — Eval report format per test type
- [agentme-edr-155](155-ai-eval-repeatability.md) — Repeatability scoring constants, metrics, and run cadence
- [agentme-edr-126](126-pragmatic-hexagonal-architecture.md) — `_mock` file naming for mock adapters
- [agentme-edr-501](../governance/501-project-quality-standards.md) — Tier-level testing requirements
- [agentme-edr-303](../platform/303-common-targets.md) — `eval-<qualifier>` Makefile convention
- [agentme-edr-305](../platform/305-environment-variable-configuration.md) — Environment-configuration conventions
- [agentme-edr-141](141-ai-llm-development-standards.md) — LLM tier definition and mocking utilities
- [agentme-edr-122](122-unit-test-requirements.md) — Unit test requirements
- [agentme-edr-156](156-ai-eval-fairness-bias.md) — Fairness/bias eval loop, scoring, and metrics
