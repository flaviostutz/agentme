---
name: agentme-edr-policy-053-ai-eval-script
description: Defines eval.py script requirements for AI projects — entry-first eval loop, --type test-type filtering, mock_fixtures wiring, human entries, threshold enforcement, and MLflow experiment naming and port assignment. Use when implementing eval scripts. For eval folder structure see agentme-edr-051 rule 01. For the test type taxonomy and mock_fixtures envelope see agentme-edr-052. For mock file naming see agentme-edr-026 rule 10. For report format see agentme-edr-054. For repeatability loop exception see agentme-edr-055.
apply-to: Python AI projects (LLM, Agent, or Workflow tier) that implement eval testing
valid-from: 2026-07-07
---

# agentme-edr-policy-053: AI eval script

## Context and Problem Statement

Eval scripts execute entries from a golden dataset against a real AI component and measure output quality. Without a shared script contract, eval implementations diverge: some invoke components multiple times per entry (wasting LLM cost), some skip mock isolation, and some omit threshold enforcement — making results inconsistent and hard to trust across projects.

How should eval scripts load datasets, iterate entries, handle mocking, and produce metrics?

## Decision Outcome

**Use an entry-first eval loop with `--type` filtering, fresh mock isolation per entry, real LLM providers, and MLflow-backed metrics with explicit per-type thresholds.**

For when evals are required per AI tier, see [agentme-edr-007](../governance/007-project-quality-standards.md) rule `09-ai-project-testing-requirements`.

### Details

#### 01-eval-script-requirements

Each `eval.py` script MUST:

- Load the golden dataset from `golden_dataset/` in the same eval folder, following [agentme-edr-050](../data/050-ml-dataset-structure.md) and the entry envelope in [agentme-edr-052](052-ai-test-types-taxonomy.md) rule `02` (one JSON file per entry, `test_types` array, `input`, `expected_output`, optional `mock_fixtures`).
- Accept a required `--type=<test_type>|all` CLI argument and filter entries whose `test_types` array contains the requested value; `--type=all` includes every entry.
- Iterate **entry-first**: for each entry in the filtered set, invoke the real component exactly once; then score that single `actual_output` for every `test_types` value the entry carries that falls within the current `--type` scope — MUST NOT invoke the component more than once per entry per run.
- When an entry contains `mock_fixtures` ([agentme-edr-052](052-ai-test-types-taxonomy.md) rule `02`), configure each named mock adapter with its fixture data BEFORE invoking the component for that entry. Each entry MUST use fresh mock instances so fixture state does not bleed across entries. `mock_fixtures` applies to all test types including `human`. `mock_fixtures` MUST NOT configure LLM adapters — the LLM call MUST be real (see [agentme-edr-052](052-ai-test-types-taxonomy.md) rule `03`). How mock adapters are discovered and instantiated is left to the project; see [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) rule `10` for the `_mock` file naming and placement convention.
- Run every component invocation against **real LLM providers** (not mocked responses), to capture model drift.
- For `human` entries: invoke the component to capture `actual_output`, export each entry's `input`, `expected_output.human_test` instructions, and `actual_output` into a manual-review checklist (`report-human.md`). MUST NOT invoke an automated scorer and MUST NOT enforce a pass/fail threshold for it. Other `test_types` on the same entry (e.g. `functional`) are still scored automatically.
- After all entries are processed, compute aggregate metrics per test type, log them to a local MLflow experiment (see rule `02`), write one `report-<type>.md` per evaluated test type ([agentme-edr-054](054-ai-eval-report-format.md) rule `01`), and exit with a non-zero status when any metric falls below its defined threshold per [agentme-edr-007](../governance/007-project-quality-standards.md) rule `07-statistical-models-must-have-eval-targets`. The `human` type has no threshold and does not trigger a non-zero exit.
- Compare outputs to expected values using project-defined quality thresholds per test type. Thresholds and all other scoring parameters MUST be declared as constants in `eval.py` — they are design decisions about what constitutes acceptable quality for the component under test, not runtime configuration, and MUST NOT be passed via Makefile variables or CLI flags. Use one of two naming conventions, chosen consistently within an `eval.py`: (a) **per-type constants** — `EVAL_MIN_<METRIC>_<TYPE>` for each test type (e.g. `EVAL_MIN_ACCURACY_FUNCTIONAL = 0.85`, `EVAL_MIN_ACCURACY_REPEATABILITY = 0.8`); or (b) **dict constant** — `EVAL_MIN_<METRIC> = {<type>: <value>}` (e.g. `EVAL_MIN_ACCURACY = {"functional": 0.85, "smoke": 0.85}`). Per-type constants are preferred when each test type has a dedicated `eval.py`; the dict form is preferred when a single `eval.py` handles multiple types. In either convention, `EVAL_MIN_ACCURACY` (as a scalar) MAY be declared as a project-wide default and MUST be used as fallback when no per-type override is defined for the current test type. This Policy does not mandate which test types a project must threshold or what value to use (see [agentme-edr-052](052-ai-test-types-taxonomy.md) rule `06`).

**Example:**

```python
import argparse
from collections import defaultdict
import mlflow
from my_package.app.workflows.document_review_workflow.graph import graph

# Per-type constants; fall back to EVAL_MIN_ACCURACY default when no override is defined
EVAL_MIN_ACCURACY = 0.85  # project-wide default
EVAL_MIN_ACCURACY_FUNCTIONAL = 0.85
EVAL_MIN_ACCURACY_SMOKE = 0.90
EVAL_MIN_ACCURACY_PER_TYPE = {"functional": EVAL_MIN_ACCURACY_FUNCTIONAL, "smoke": EVAL_MIN_ACCURACY_SMOKE}

def get_min_accuracy(test_type: str) -> float:
    return EVAL_MIN_ACCURACY_PER_TYPE.get(test_type, EVAL_MIN_ACCURACY)

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True)
args = parser.parse_args()

entries = load_golden_dataset("golden_dataset/", test_type=args.type)  # "all" loads every entry
resolved_types = resolve_types(args.type, entries)

mlflow.set_experiment("document-review/eval-basic")

with mlflow.start_run():
    mlflow.set_tag("test_types", ",".join(sorted(resolved_types)))

    results = defaultdict(list)
    cumulative_metrics = defaultdict(lambda: {"accuracy": [], "f1": []})  # Track cumulative metrics

    # Entry-first loop: invoke each entry exactly once
    for idx, entry in enumerate(entries, start=1):
        # Configure mock adapters from mock_fixtures before invocation
        # (implementation left to the project — see agentme-edr-026 rule 10)
        if entry.get("mock_fixtures"):
            configure_mocks(entry["mock_fixtures"])  # project-defined helper

        actual_output = invoke_component(entry, graph)

        for test_type in [t for t in entry["test_types"] if t in resolved_types]:
            if test_type == "human":
                export_human_review(entry, actual_output)
                continue
            
            score_val = score(test_type, actual_output, entry["expected_output"])
            results[test_type].append(score_val)
            
            # Track cumulative metrics for convergence analysis
            cumulative_accuracy = sum(results[test_type]) / len(results[test_type])
            cumulative_f1 = compute_f1(results[test_type])  # project-defined
            cumulative_metrics[test_type]["accuracy"].append(cumulative_accuracy)
            cumulative_metrics[test_type]["f1"].append(cumulative_f1)

    # Aggregate, report, and enforce thresholds per test type
    for test_type in resolved_types:
        if test_type == "human":
            continue

        accuracy = sum(results[test_type]) / len(results[test_type])
        mlflow.log_metric(f"{test_type}_accuracy", accuracy)
        
        # Generate convergence analysis
        stability_window = min(10, len(results[test_type]))
        acc_change = abs(cumulative_metrics[test_type]["accuracy"][-1] - 
                        cumulative_metrics[test_type]["accuracy"][-stability_window])
        f1_change = abs(cumulative_metrics[test_type]["f1"][-1] - 
                       cumulative_metrics[test_type]["f1"][-stability_window])
        
        write_eval_report(
            test_type, 
            results[test_type], 
            cumulative_metrics=cumulative_metrics[test_type],
            stability_window=stability_window,
            thresholds={"accuracy": get_min_accuracy(test_type)}
        )

        if accuracy < get_min_accuracy(test_type):
            raise SystemExit(f"Eval failed: {test_type} accuracy {accuracy:.2f} < {get_min_accuracy(test_type)}")
```

#### 02-eval-mlflow-unique-port

Each `evals/<component>/eval-<name>/Makefile` MUST start its MLflow tracking server on a **unique port** to prevent conflicts when multiple eval Makefiles are run concurrently or in parallel (e.g., in CI or across multiple terminal sessions).

Ports MUST be statically assigned per eval scenario (not per test type) and MUST NOT reuse the default `5000` port (reserved for `dev-mlflow` per [agentme-edr-008](../platform/008-common-targets.md) rule `09-ai-project-dev-targets`). Assign ports starting at `5100` and incrementing by 1 for each additional eval scenario across the entire project.

The MLflow **experiment** is scoped to the eval scenario: `<component>/<eval-name>` (e.g. `document-review/eval-basic`). Each `mlflow.start_run()` call MUST set a `test_types` tag listing the test types evaluated in that invocation (comma-separated, e.g. `"functional,smoke"` for `--type=all`, `"smoke"` for `--type=smoke`). A remote MLflow server MUST NOT be required — all tracking is local.

## References

- [agentme-edr-051](051-ai-eval-core-standards.md) — AI eval core standards: eval folder structure (rule `01`) and LLM-as-judge binary scoring contract (rule `02`)
- [agentme-edr-054](054-ai-eval-report-format.md) — AI eval report format: `report-<type>.md` template, Wilson CI, and convergence analysis
- [agentme-edr-055](055-ai-eval-repeatability.md) — AI eval repeatability: loop exception to rule `01`'s entry-first constraint, scoring methods, and cadence
- [agentme-edr-052](052-ai-test-types-taxonomy.md) — AI test types taxonomy: `test_types` enum, golden dataset entry envelope (including `mock_fixtures`), and mocking constraints per type
- [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) — Rule `10`: `_mock` file naming and placement convention for mock adapters used in `mock_fixtures`
- [agentme-edr-050](../data/050-ml-dataset-structure.md) — ML dataset structure, per-entry JSON format, and schema-lint validation for golden datasets
- [agentme-edr-007](../governance/007-project-quality-standards.md) — Project quality standards: when evals are required per AI tier (rule `09`) and statistical model eval targets (rule `07`)
- [agentme-edr-008](../platform/008-common-targets.md) — `eval-<qualifier>` Makefile convention (rule `03`) and reserved MLflow port `5000` (rule `09`)
