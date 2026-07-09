---
name: agentme-edr-policy-055-ai-eval-repeatability
description: Defines the repeatability test type for AI evals — REPEAT_COUNT loop exception to the entry-first constraint, semantic-similarity and LLM-as-judge scoring methods, repeatability_accuracy metric, and the repeatability report format and run cadence. Use when implementing repeatability evals. For the entry-first constraint see agentme-edr-053 rule 01. For LLM-as-judge binary output see agentme-edr-051 rule 02. For the base report template see agentme-edr-054 rule 01. For the repeatability test type definition see agentme-edr-052.
apply-to: Python AI projects (LLM, Agent, or Workflow tier) that implement repeatability eval testing
valid-from: 2026-07-07
---

# agentme-edr-policy-055: AI eval repeatability

## Context and Problem Statement

Some AI components must be tested for output consistency across multiple invocations with the same input — a property the standard entry-first eval loop cannot capture because it invokes each entry only once. Without a shared repeatability protocol, teams either skip this test or implement ad-hoc variations that produce incomparable results.

How should repeatability be measured in evals, and how should its results be reported?

## Decision Outcome

**Exempt `repeatability` entries from the entry-first constraint, invoking each `REPEAT_COUNT` times and scoring via semantic-similarity or LLM-as-judge; schedule at release cadence rather than per-commit.**

For the `repeatability` test type definition and its disambiguation from `reproducibility`, see [agentme-edr-052](052-ai-test-types-taxonomy.md) rule `09`.

### Details

#### 01-repeatability-eval-loop-exception

Entries whose `test_types` includes `repeatability` are exempt from [agentme-edr-053](053-ai-eval-script.md) rule `01`'s "invoke exactly once per entry" constraint. The following constants MUST be declared in `eval.py` and MUST NOT be exposed as Makefile variables, CLI flags, or stored as per-entry dataset fields:

- `REPEAT_COUNT` — number of times each repeatability entry is invoked. SHOULD default to 3-5 for routine CI runs and 10-20 for focused passes on decision-critical or previously-flagged components. Projects SHOULD calibrate the value once per component by plotting cumulative pass rate against repeat count for a few representative entries and picking the point where it plateaus, rather than guessing.
- `EVAL_MIN_ACCURACY_REPEATABILITY` — minimum fraction of repeatability entries that must PASS for the eval to exit 0.
- `REPEAT_SEMANTIC_SIMILARITY_SCORE` — minimum average pairwise cosine similarity for a single entry to PASS; declared only when using semantic-similarity scoring.

`eval.py` MUST invoke the component `REPEAT_COUNT` times for every repeatability entry and score the resulting outputs by comparing them to each other. `expected_output` is unused for repeatability entries and SHOULD be omitted or set to `null` in the dataset.

**Choosing the scoring method:** Two approaches are supported, declared as a constant in `eval.py`:

- **Semantic-similarity:** Embed all `REPEAT_COUNT` outputs for an entry into vectors and compute the average pairwise cosine similarity. The entry passes (score = 1) if the average similarity ≥ `REPEAT_SEMANTIC_SIMILARITY_SCORE`; otherwise it fails (score = 0). Use for classification or short structured outputs.
- **LLM-as-judge:** Provide all `REPEAT_COUNT` outputs for an entry to an LLM judge (kept at low/zero temperature) that returns 0 (fail) or 1 (pass) directly, based on whether the outputs are sufficiently consistent. No `REPEAT_SEMANTIC_SIMILARITY_SCORE` constant is needed. Use for free-text or complex structured outputs where vector distance is an unreliable proxy for agreement. The judge MUST follow [agentme-edr-051](051-ai-eval-core-standards.md) rule `02`'s binary output contract.

**`repeatability_accuracy`:** the fraction of repeatability entries that received PASS (score = 1), logged to MLflow as `repeatability_accuracy`. The eval exits non-zero if `repeatability_accuracy` < `EVAL_MIN_ACCURACY_REPEATABILITY`. Both `repeatability_accuracy` and `repeat_count` MUST be logged to MLflow and included in `report-repeatability.md` (rule `02`).

```python
REPEAT_COUNT = 5
EVAL_MIN_ACCURACY_REPEATABILITY = 0.8
REPEAT_SEMANTIC_SIMILARITY_SCORE = 0.9  # only when using semantic-similarity scoring

for entry in repeatability_entries:
    outputs = [invoke_component(entry, graph) for _ in range(REPEAT_COUNT)]
    entry_pass = score_agreement(outputs)  # returns 0 or 1; expected_output is not used
    results["repeatability"].append(entry_pass)  # 1 = PASS, 0 = FAIL

repeatability_accuracy = sum(results["repeatability"]) / len(results["repeatability"])
mlflow.log_metric("repeatability_accuracy", repeatability_accuracy)
mlflow.log_metric("repeat_count", REPEAT_COUNT)

if repeatability_accuracy < EVAL_MIN_ACCURACY_REPEATABILITY:
    raise SystemExit(f"Eval failed: repeatability_accuracy {repeatability_accuracy:.2f} < {EVAL_MIN_ACCURACY_REPEATABILITY}")
```

`mock_fixtures` configuration per [agentme-edr-053](053-ai-eval-script.md) rule `01` applies to each of the `REPEAT_COUNT` invocations. Any prompt or response caching (provider-side or gateway-side) MUST be bypassed for these invocations — a cache hit would return an identical cached response and falsely report perfect stability instead of measuring the model's actual variance.

**Scoping:** this test type MUST NOT be applied to components whose intended behavior is diverse or creative output (e.g. brainstorming, creative writing) — low agreement there is correct behavior, not a defect.

#### 02-repeatability-report-and-cadence

`--type=repeatability` MUST produce `report-repeatability.md` with a shape adapted from [agentme-edr-054](054-ai-eval-report-format.md) rule `01`'s template: the header MUST include a **Repeat count:** line stating the `REPEAT_COUNT` value used for the run, alongside the usual Date/Dataset/Script/Thresholds lines. The body MUST have an aggregate row reporting `repeatability_accuracy` (the fraction of entries that PASS — see rule `01`) with a Wilson score interval computed over the number of `repeatability` entries, plus a per-item table listing each entry's individual pass/fail result and, when using semantic-similarity, its computed average pairwise cosine similarity — instead of the `Expected | Actual | Correct` columns used by other types.

Because `repeatability` entries multiply real LLM-provider calls by `REPEAT_COUNT`, projects SHOULD schedule `make eval-repeatability` at release cadence rather than on every commit, aligned with the Workflow eval cadence in [agentme-edr-007](../governance/007-project-quality-standards.md) rule `09`, rather than treating it as a mandatory per-commit gate.

## References

- [agentme-edr-053](053-ai-eval-script.md) — AI eval script: rule `01` defines the entry-first constraint this policy exempts for repeatability entries
- [agentme-edr-051](051-ai-eval-core-standards.md) — AI eval core standards: rule `02` defines the LLM-as-judge binary output contract used by the LLM-as-judge scoring method in rule `01`
- [agentme-edr-054](054-ai-eval-report-format.md) — AI eval report format: rule `01` defines the base report template that `report-repeatability.md` adapts
- [agentme-edr-052](052-ai-test-types-taxonomy.md) — AI test types taxonomy: `repeatability` test type definition and disambiguation from `reproducibility` (rule `09`)
- [agentme-edr-007](../governance/007-project-quality-standards.md) — Project quality standards: Workflow eval cadence (rule `09`) that repeatability runs align with
