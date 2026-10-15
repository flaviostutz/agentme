---
name: agentme-edr-policy-158-ai-performance-testing
description: Extends agentme-edr-306 for AI components - latency, error rate, cost and integrity metrics, real LLM by default, proxy or adapter fault simulation with optional LLM mocking, integrity scoring (deterministic, local semantic model, LLM judge last), offline scoring of recorded samples, AI fault scenarios. Use when measuring how an LLM, Agent or Workflow behaves under load, stress, long runs or failing providers.
apply-to: AI components (LLM, Agent or Workflow tier) covered by a performance-<slug> module under agentme-edr-306
valid-from: 2026-10-15
---

# agentme-edr-policy-158: AI performance testing

## Context and Problem Statement

AI components fail under load and faulty conditions like any system, plus in AI-specific ways: slow or rate-limited providers, runaway token cost, and wrong outputs that arrive with a success status. Evals show output quality on a golden dataset, not behavior under environmental conditions.

Question: What must AI performance tests add to the generic performance Policy?

## Decision Outcome

**Run AI performance tests under agentme-edr-306 and measure AI components the same way as non-AI ones, adding cost and integrity metrics, controlled LLM mocking and offline scoring.**

Every rule in [agentme-edr-306](../platform/306-performance-testing.md) applies unchanged, including the six kinds, the environment matrix, prod guardrails and report files. Performance tests are not evals: `performance` is not a `test_types` value in [agentme-edr-152](152-ai-test-types-taxonomy.md), the module has its own dataset, and `eval.py` never runs it.

### Details

#### 01-metrics-must-cover-latency-error-rate-cost-and-integrity

`thresholds.yaml` MUST declare limits for all four metrics for every gated scenario:

- latency: end-to-end for the workflow, agent or LLM call, as p50, p95 and p99;
- error rate: provider errors, timeouts, tool failures and malformed or empty outputs, counted as errors even when the HTTP status is success;
- cost: tokens used multiplied by the price table, reported per request and per run;
- integrity: share of sampled outputs that pass the checks of rule `04`.

Token usage MUST be recorded per request. Prices MUST come from a `prices.yaml` in the module (model name, input and output price per 1000 tokens, date) so that cost is computed, never estimated by a model.

#### 02-llm-must-be-real-by-default

Scenarios MUST call the real LLM provider and the real system under test. The goal is to see the true latency, rate limits and cost the system will have. Every run MUST declare a cost cap (maximum requests or maximum spend) and abort when it is reached.

#### 03-proxy-or-adapter-may-simulate-failures-and-mock-the-llm

Provider failures (timeouts, rate limiting, 5xx errors, slow or truncated responses, malformed output) MUST be simulated by a proxy or adapter in front of the provider, per [agentme-edr-306](../platform/306-performance-testing.md) rule `01-six-kinds-of-performance-test`.

When provider performance is not the object of the scenario (for example, load on the surrounding workflow, database or API), the same proxy or adapter MAY return canned LLM responses to avoid cost. Canned responses MAY come from `mock_fixtures` of the performance dataset. The report MUST state for each run whether the LLM was real or mocked, and results of mocked runs MUST NOT be used as evidence of provider latency or cost.

This is the one place where an LLM is mocked for a test that calls a deployed system; the real-LLM constraint of [agentme-edr-152](152-ai-test-types-taxonomy.md) rule `08-eval-mocking-constraint` governs golden-dataset evals and is not changed.

#### 04-integrity-scoring-order

Integrity of recorded outputs MUST be judged in this order:

1. deterministic checks always: schema validity, required fields, exact, regex or numeric match, expected tool calls, absence of duplicates;
2. for free text with an expected output: semantic similarity computed by a model running locally, with the threshold declared in `thresholds.yaml`;
3. an LLM-as-judge with binary output per [agentme-edr-151](151-ai-eval-standards.md) rule `02-llm-as-judge-binary-output`, only when checks 1 and 2 are not feasible; its cost MUST be reported apart from the system cost.

Inputs and expected outputs come from the module's `dataset/`; scenarios without a dataset MUST use deterministic checks only.

#### 05-scoring-must-run-offline-after-the-run

During the run the load tool MUST only record samples (input, output, latency, token usage, error, timestamp) into `dist/samples-<kind>.jsonl`, redacted per [agentme-edr-306](../platform/306-performance-testing.md) rule `06-datasets-and-data-safety`. Integrity scoring MUST happen after the run from those samples, so scoring adds no load and no latency to the measurement. The exit code and `results-<kind>.json` are produced after scoring.

#### 06-ai-resilience-scenarios-must-check-half-done-work

Resilience scenarios for agents and workflows SHOULD cover provider down, rate limiting, slow provider, malformed output and tool or connector failure. Graceful behavior means a clear error to the caller, bounded retries without a retry storm, and no half-done work. The post-run consistency check of [agentme-edr-306](../platform/306-performance-testing.md) rule `05-thresholds-and-exit-codes` MUST also detect repeated side effects (a tool called twice for one request) and workflow runs left in an intermediate state.

#### 07-results-must-add-ai-fields

`results-<kind>.json` and `report-<kind>.md` MUST add `llm_mode` (`real` or `mocked`), `cost_per_request`, `total_cost`, `tokens_in`, `tokens_out`, `integrity_pass_rate` and the scoring method used per rule `04`. These files are not eval reports, so [agentme-edr-154](154-ai-eval-report-format.md) does not apply to them.

## References

- [agentme-edr-306](../platform/306-performance-testing.md) - Generic performance testing, extended by this Policy
- [agentme-edr-152](152-ai-test-types-taxonomy.md) - Test types taxonomy and dataset envelope
- [agentme-edr-151](151-ai-eval-standards.md) - LLM-as-judge binary output
- [agentme-edr-154](154-ai-eval-report-format.md) - Eval report format, not applied here
- [agentme-edr-157](157-ai-a-b-testing.md) - AI A/B testing in production
