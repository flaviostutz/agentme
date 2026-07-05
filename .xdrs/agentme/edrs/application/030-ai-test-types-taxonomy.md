---
name: agentme-edr-policy-030-ai-test-types-taxonomy
description: Names AI-application test types (safety, responsible-AI, quality-eval, prompt, code-level) with their group, objective, mocking constraint, and relevance, and defines the shared "golden dataset" entry envelope that agentme-edr-028's eval tooling filters by test_types. Use when deciding which AI test types to implement or when authoring a golden dataset entry.
apply-to: AI projects (LLM, Agent, or Workflow tier) implementing AI-specific test types beyond generic code-level unit/integration tests
valid-from: 2026-07-05
---

# agentme-edr-policy-030: AI test types taxonomy

## Context and Problem Statement

AI components need test types beyond generic unit/integration tests (safety, fairness, groundedness, functional accuracy, etc.). Which test types should be named, and how should their datasets and eval tooling work?

## Decision Outcome

**Adopt a named taxonomy of AI test types plus a shared "golden dataset" entry envelope that agentme-edr-028's eval tooling filters by `test_types`.**

Each test type is named with its group, objective, mocking constraint, applicability, and relevance; every golden dataset entry is labeled with the test types it applies to.

### Details

#### 01-golden-dataset-concept

A **golden dataset** comprises all eval case entries used to test an AI component (LLM, Agent, or Workflow tier); each entry is labeled with the `test_types` (rule `04`) it applies to. It is the dataset consumed by [agentme-edr-028](028-ai-eval-standards.md) evals and stored as one JSON file per entry per [agentme-edr-024](024-ml-dataset-structure.md) rule `04`, at `evals/<component>/eval-<name>/golden_dataset/`.

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

- `test_types` — array, values MUST come from rule `04`'s enum, MUST contain at least one value. An entry MAY carry more than one value additively (e.g. `["functional", "smoke", "human"]`) — no test type excludes another.
- `input` — for Prompt-tier components, a raw prompt string or the prompt template's input parameters object; for Agent/Workflow-tier components, the input attributes object passed to the component.
- `expected_output` — the fields used to score the entry under each of its automated `test_types`: output attributes for an LLM-as-judge rubric, a target for vector-similarity scoring, or exact attribute values for strict comparison. When `human` is one of the entry's `test_types`, `expected_output` MUST additionally include a `human_test` string field with manual-verification instructions (e.g. `"check for ethical issues, verify record change in system X"`) — this supplements, and never replaces, the entry's automated scoring fields.
- `mock_fixtures` — optional object; keys identify the adapter or external system to mock (SHOULD match the connector folder name under `adapters/connectors/<name>` for readability, though not enforced), values are any valid JSON interpreted by the mock implementation. When present, eval.py MUST configure each named mock adapter with its fixture data BEFORE invoking the component for that entry; each entry MUST use fresh mock instances to prevent state from bleeding across entries. `mock_fixtures` applies to all `test_types` including `human` — the component is still invoked for human entries to capture `actual_output`. `mock_fixtures` MUST NOT include keys for LLM adapters: all golden dataset test types are rated `mocks disallowed for LLM calls` (rule `03`), so the LLM call MUST always be real; LLM provider mocking belongs exclusively to unit tests via [agentme-edr-018](018-ai-llm-development-standards.md) rule `04`. See [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) rule `10` for the `_mock` file naming and placement convention.
- The dataset's `dataset.schema.json` MUST require `test_types`, `input`, and `expected_output`, and SHOULD declare `mock_fixtures` as optional (`"type": "object", "additionalProperties": {}`), per [agentme-edr-024](024-ml-dataset-structure.md) rule `04`.

#### 03-mocks-allowed-values

The taxonomy in rule `05` rates each test type using one of three values:

| Value | Meaning |
|---|---|
| `mocks allowed` | Fully offline; fakes may replace every dependency (e.g. `FakeListChatModel` per [agentme-edr-018](018-ai-llm-development-standards.md) rule `04`). |
| `mocks disallowed` | No mocking of any dependency — real external systems required. |
| `mocks disallowed for LLM calls` | Tools and other external/dependency calls MAY be mocked; only the LLM call itself MUST be real for the test to be meaningful. |

#### 04-test-types-enum

A golden dataset entry's `test_types` array MUST only use these values: `safety`, `adversarial`, `fairness`, `bias`, `robustness`, `explainability`, `groundedness`, `functional`, `prompt`, `smoke`, `human`. These correspond to the dataset-driven rows of rule `05`. **Unit test** and **Integration test** (the two Code-level rows) are NOT part of this enum — they have no golden dataset entries and remain governed entirely by [agentme-edr-004](../principles/004-unit-test-requirements.md) and [agentme-edr-007](../principles/007-project-quality-standards.md) rule `08`.

#### 05-test-type-taxonomy

| Test Type Name | Group | Test Objective | Mocks Allowed | When to Apply | Relevance – Business | Relevance – Development Team | Priority (1-5) |
|---|---|---|---|---|---|---|---|
| Safety/content eval | Safety & adversarial | Detect harmful, biased, or policy-violating output | mocks disallowed for LLM calls | Any user-facing release | Avoids reputational harm; acceptable-use compliance | Automated content gate before merge/release | 5 |
| Adversarial/red-team test | Safety & adversarial | Probe for prompt injection, jailbreaks, unsafe tool use | mocks disallowed for LLM calls | System exposes tool-invocation or agent loops | Reduces security-incident/breach liability | Finds exploitable tool-loop paths before attackers do | 5 |
| Fairness test | Responsible AI | Verify equitable outcomes across user groups | mocks disallowed for LLM calls | Output affects decisions about individuals/groups | Regulatory requirement; protects equitable access | Surfaces uneven outcomes before release | 4 |
| Bias test | Responsible AI | Detect skewed or stereotyped associations | mocks disallowed for LLM calls | User-facing content generation | Lowers legal/reputational exposure | Catches bias introduced by data/prompts/fine-tuning | 3 |
| Robustness test | Responsible AI | Verify stable behavior under noisy/out-of-distribution input | mocks disallowed for LLM calls | Inputs come from untrusted/variable sources | Protects reliability/SLAs | Confirms graceful degradation, guides input validation | 3 |
| Explainability test | Responsible AI | Verify output is justifiable with a faithful rationale | mocks disallowed for LLM calls | Output must be justified to users/auditors/regulators | Required for auditability; builds user trust | Gives rationale trace for debugging wrong answers | 2 |
| Groundedness (RAG) eval | Quality eval | Verify the answer is supported by retrieved context | mocks disallowed for LLM calls | System uses retrieval-augmented generation | Avoids confidently-wrong answers reaching customers | Pinpoints retrieval/prompt bugs | 4 |
| Human evaluation | Quality eval | Manually verify aspects automated scoring can't (ethics, side effects, external state) | mocks disallowed for LLM calls | Before major releases; periodic spot-check | Defensible, human-reviewed sign-off | Catches what automated metrics miss | 3 |
| Functional eval (golden-dataset accuracy / LLM-as-judge) | Quality eval | Measure output correctness against the golden dataset | mocks disallowed for LLM calls | Required before every Workflow release ([agentme-edr-007](../principles/007-project-quality-standards.md) rule `09`); advised elsewhere | Auditable evidence of business correctness before release | Detects regressions from model/provider/prompt changes | 5 |
| Smoke test | Quality eval | Fast pass/fail check on a small, critical subset before running fuller suites | mocks disallowed for LLM calls | Every commit/PR, before functional/responsible-AI evals run | Cheap early warning before slower evals run | Fast, cheap feedback loop | 4 |
| Prompt regression test | Prompt/LLM | Detect behavior change when a prompt or model version changes | mocks disallowed for LLM calls | Whenever a prompt template or model version changes | Prevents shipping a worse experience via a "small" tweak | Fast check on every prompt edit | 3 |
| Integration test | Code-level | Verify real interaction with external systems | mocks disallowed | Component depends on external systems | Reduces production outages from integration mismatches | Catches wiring bugs unit tests can't see | 2 |
| Unit test (offline, mocked) | Code-level | Verify deterministic logic in isolation, offline | mocks allowed | Required for Workflow tier every commit ([agentme-edr-007](../principles/007-project-quality-standards.md) rule `09`) | Lowest-cost point to catch defects | Fastest, fully offline feedback on every commit | 5 |

#### 06-priority-and-relevance-are-descriptive-only

Priority, Relevance, and When to Apply in rule `05` are guidance for prioritization conversations — they do NOT mandate which test types a project must implement, nor their thresholds. [agentme-edr-007](../principles/007-project-quality-standards.md) rule `09` remains the only tier-level testing requirement in force (Workflow unit tests + functional evals). Once a project chooses to implement and threshold a test type, [agentme-edr-028](028-ai-eval-standards.md) rule `02`'s failing-threshold behavior applies uniformly, regardless of this table's priority rating — a project may enforce fairness at 70% and functional at 90%, or skip fairness entirely; that choice is a project/business decision, not one this Policy makes.

#### 07-smoke-is-distinct-from-test-smoke

The `smoke` test type (surfaced as the `eval-smoke` Makefile target, a fast subset of the golden-dataset functional eval) is a different concept from [agentme-edr-008](../devops/008-common-targets.md)'s existing `test-smoke` target (a fast subset of code-level tests). Both may exist in the same project; do not conflate them.

## References

- [agentme-edr-024](024-ml-dataset-structure.md) — Golden dataset file layout, per-entry JSON format, `$schema` pointer, and schema-lint validation
- [agentme-edr-028](028-ai-eval-standards.md) — Eval folder structure, `--type` filtering, per-type Makefile targets, and per-type reports that consume this taxonomy
- [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) — Rule `10`: `_mock` file naming and placement convention for mock adapters referenced by `mock_fixtures`
- [agentme-edr-007](../principles/007-project-quality-standards.md) — Rule `09` tier-level testing requirements (the only mandated AI testing baseline)
- [agentme-edr-008](../devops/008-common-targets.md) — Rule `03` `eval-<qualifier>` Makefile convention; rule `03`'s `test-smoke` (distinguished in rule `07`)
- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM tier definition and mocking utilities referenced by the `mocks allowed` value
- [agentme-edr-004](../principles/004-unit-test-requirements.md) — Unit test requirements underlying the Code-level rows
