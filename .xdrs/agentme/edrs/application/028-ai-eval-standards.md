---
name: agentme-edr-policy-028-ai-eval-standards
description: Defines how to structure, write, and run eval tests for AI projects — folder layout, golden dataset, --type test-type filtering, per-type Makefile targets and reports, and MLflow tracking. Use when implementing evals for LLM, Agent, or Workflow projects. For when evals are required see agentme-edr-007 rule 09-ai-project-testing-requirements. For the test type taxonomy see agentme-edr-030.
apply-to: Python AI projects (LLM, Agent, or Workflow tier) that implement eval testing
valid-from: 2026-06-05
---

# agentme-edr-policy-028: AI eval standards

## Context and Problem Statement

Eval tests measure AI component accuracy against expected outputs using real LLM providers. Without a shared folder layout and script convention, eval setups diverge across LLM, Agent, and Workflow projects, making them hard to run, compare, and integrate into CI/CD pipelines.

How should eval tests be structured and run across all AI tiers?

## Decision Outcome

**Use a per-component folder structure under `evals/` with a standardized Makefile interface and MLflow-backed scripts, applicable to LLM, Agent, and Workflow components.**

For when evals are required per AI tier, see [agentme-edr-007](../principles/007-project-quality-standards.md) rule `09-ai-project-testing-requirements`.

### Details

#### 01-eval-folder-structure

Evals are grouped first by the component being evaluated, then by the specific evaluation scenario. Create one directory per component under `evals/`, and one directory per eval scenario inside it. Place `evals/` at the same level as `lib/` and `examples/`:

```text
evals/
  <component>/           # the component being evaluated (e.g., workflow-x, agent-y, model-z)
    eval-<name>/
      golden_dataset/    # EDR-024 + EDR-030 compliant golden dataset (README.md, dataset.schema.json, data/)
      eval.py            # evaluation script
      report-<type>.md   # generated report, one per evaluated test type (overwritten on each run — see rule 03)
      Makefile           # lint, eval, run, and eval-<type> targets
    eval-<name2>/
      ...
  <component2>/
    ...
```

`<component>` MUST match the name of the component under evaluation and use lowercase hyphen-separated words (e.g., `workflow-document-review`, `agent-support`, `model-classifier`).

`<name>` identifies the specific evaluation scenario using lowercase hyphen-separated words (e.g., `eval-basic`, `eval-complex`, `eval-edge-cases`). A scenario's `golden_dataset` MAY mix multiple test types across its entries: label each entry with its applicable `test_types` ([agentme-edr-030](030-ai-test-types-taxonomy.md) rule `04`) and use the `eval-<type>` targets below to run one type at a time.

The `golden_dataset/` subfolder MUST be a valid [agentme-edr-024](024-ml-dataset-structure.md) dataset (`README.md`, `dataset.schema.json`, one JSON file per entry under `data/` per rule `04-complex-structured-datasets-must-use-per-entry-json-files`, lint-validated per rule `06`) whose entries follow the golden dataset envelope defined in [agentme-edr-030](030-ai-test-types-taxonomy.md) rule `02`.

Each `evals/<component>/eval-<name>/Makefile` MUST declare a `TEST_TYPES` variable listing the `test_types` values present in its golden dataset, and define:

| Target | Behaviour |
|---|---|
| `lint` | Validates every `golden_dataset/data/*.json` file against `golden_dataset/dataset.schema.json` per [agentme-edr-024](024-ml-dataset-structure.md) rule `06` |
| `eval` | Depends on `lint`; runs `eval.py --type=all` with threshold enforcement; exits non-zero on failure (CI-safe) |
| `run` | Depends on `lint`; runs `eval.py --type=all` without threshold enforcement (exploration / debugging) |
| `eval-<type>` | Depends on `lint`; runs `eval.py --type=<type>` for one declared test type, following [agentme-edr-008](../devops/008-common-targets.md) rule `03`'s `eval-<qualifier>` convention |

```makefile
TEST_TYPES := smoke functional safety

lint:
	mise exec -- uv run --project . python lint_dataset.py golden_dataset/

eval: lint
	mise exec -- uv run --project . python eval.py --type=all

run: lint
	mise exec -- uv run --project . python eval.py --type=all --no-threshold

eval-%: lint
	mise exec -- uv run --project . python eval.py --type=$*
```

The module root Makefile MUST expose `make eval` and `make lint` targets that delegate to `eval` and `lint` respectively in every `evals/<component>/eval-<name>/Makefile`:

```makefile
eval:
	$(MAKE) -C evals/workflow-document-review/eval-basic eval
	$(MAKE) -C evals/workflow-document-review/eval-complex eval

lint:
	$(MAKE) -C evals/workflow-document-review/eval-basic lint
	$(MAKE) -C evals/workflow-document-review/eval-complex lint
```

#### 02-eval-script-requirements

Each `eval.py` script MUST:

- Load the golden dataset from `golden_dataset/` in the same eval folder, following [agentme-edr-024](024-ml-dataset-structure.md) and the entry envelope in [agentme-edr-030](030-ai-test-types-taxonomy.md) rule `02` (one JSON file per entry, `test_types` array, `input`, `expected_output`).
- Accept a required `--type=<test_type>|all` CLI argument and filter entries whose `test_types` array contains the requested value; `--type=all` includes every entry, evaluated once for each `test_types` value it carries.
- When an entry carries more than one `test_types` value, invoke the real component only **once** per entry per run and cache its `actual_output`; run each applicable type's scorer against that single cached output — never invoke the component twice for the same entry.
- Run every invocation through the live component against **real LLM providers** (not mocked responses), to capture model drift.
- `--type=human` MUST NOT invoke an automated scorer: export each entry where `human` ∈ `test_types` (its `input`, `expected_output.human_test` instructions, and `actual_output`) into a manual-review checklist, and MUST NOT enforce a pass/fail threshold for it. An entry's OTHER `test_types` (e.g. `functional`) are still scored automatically under their own `--type=` invocation, since `human` is an additive label, not an exclusive one.
- Log per-sample and aggregate metrics to a **local** MLflow experiment scoped to the invoked `--type` value (e.g. `<component>/<eval-name>/smoke`, or `<component>/<eval-name>/all` when `--type=all` — see rule `04`); a remote MLflow server MUST NOT be required.
- Compare outputs to expected values using project-defined quality thresholds per test type. Thresholds MUST be declared explicitly (e.g., in a Makefile variable or README) — this Policy does not mandate which test types a project must threshold or what value to use (see [agentme-edr-030](030-ai-test-types-taxonomy.md) rule `06`).
- Write one `report-<type>.md` per evaluated test type in the same folder per rule `03`.
- Exit with a non-zero status when any metric falls below its defined threshold, consistent with [agentme-edr-007](../principles/007-project-quality-standards.md) rule `07-statistical-models-must-have-eval-targets`. This does not apply to the `human` type, which has no automated threshold.

**Example:**

```python
import argparse
import mlflow
from my_package.app.workflows.document_review_workflow.graph import graph

EVAL_MIN_ACCURACY = {"functional": 0.85, "smoke": 0.85}

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True)
args = parser.parse_args()

entries = load_golden_dataset("golden_dataset/", test_type=args.type)  # "all" loads every entry

mlflow.set_experiment(f"document-review/eval-basic/{args.type}")

with mlflow.start_run():
    for test_type in resolve_types(args.type, entries):
        typed_entries = [e for e in entries if test_type in e["test_types"]]
        results = []
        for entry in typed_entries:
            actual_output = get_or_invoke_once(entry, graph)  # invoke once, reuse across types
            if test_type == "human":
                export_human_review(entry, actual_output)
                continue
            results.append(score(test_type, actual_output, entry["expected_output"]))

        if test_type == "human":
            continue

        accuracy = sum(results) / len(results)
        mlflow.log_metric(f"{test_type}_accuracy", accuracy)
        write_eval_report(test_type, results, thresholds={"accuracy": EVAL_MIN_ACCURACY[test_type]})

        if accuracy < EVAL_MIN_ACCURACY[test_type]:
            raise SystemExit(f"Eval failed: {test_type} accuracy {accuracy:.2f} < {EVAL_MIN_ACCURACY[test_type]}")
```

#### 03-eval-report-file

Each eval script MUST produce one `report-<type>.md` per evaluated test type in the same `evals/<component>/eval-<name>/` folder and overwrite each on every run — only the types included in the current `--type` invocation are (re)written; report files for other types are left untouched. The `human` type does not produce a metrics report (see below).

**Generation constraint:** The report MUST be produced programmatically, reading raw metric values directly from MLflow. No LLM or generative model may write, summarize, or paraphrase any section of the report, to prevent hallucinated metric values.

The report MUST follow this template:

```markdown
# Eval Report: <name> — <type>

**Date:** <ISO date>
**Dataset:** golden_dataset/
**Script:** eval.py --type=<type>
**Thresholds:** accuracy ≥ <value>, F1 ≥ <value>

## Overall Results

| Metric    | Value  | 95% CI         | Threshold | Status  |
|-----------|--------|----------------|-----------|---------|
| Accuracy  | <val>  | [<low>, <high>]| ≥ <thr>   | ✓/✗ PASS/FAIL |
| F1 Score  | <val>  | —              | ≥ <thr>   | ✓/✗ PASS/FAIL |
| Precision | <val>  | —              | —         | —       |
| Recall    | <val>  | —              | —         | —       |
| Samples   | <n>    | —              | —         | —       |

**Overall: PASS / FAIL**

## Per-item Results

| ID  | Input Summary | Expected | Actual | Correct |
|-----|---------------|----------|--------|---------|
| 001 | <summary>     | <label>  | <label>| ✓       |
| 002 | <summary>     | <label>  | <label>| ✗       |

## Notes

- <observations, failure patterns, MLflow run link>
```

**Confidence interval:** The 95% CI for accuracy MUST be computed using the **Wilson score interval** (preferred over the normal approximation for small $n$). A wide interval signals that the dataset is too small to support confident conclusions and the sample count should be increased.

The Wilson score bounds at 95% confidence ($z = 1.96$) are:

$$\frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Where $\hat{p}$ is observed accuracy and $n$ is sample count. Accuracy and F1 are required; precision and recall are recommended.

**Filled-in example** (`evals/workflow-document-review/eval-basic/report-functional.md` for a document review workflow):

```markdown
# Eval Report: eval-basic — functional

**Date:** 2026-06-12
**Dataset:** golden_dataset/
**Script:** eval.py --type=functional
**Thresholds:** accuracy ≥ 0.85, F1 ≥ 0.80

## Overall Results

| Metric    | Value | 95% CI       | Threshold | Status      |
|-----------|-------|--------------|-----------|-------------|
| Accuracy  | 0.88  | [0.69, 0.97] | ≥ 0.85    | ✓ PASS      |
| F1 Score  | 0.86  | —            | ≥ 0.80    | ✓ PASS      |
| Precision | 0.89  | —            | —         | —           |
| Recall    | 0.84  | —            | —         | —           |
| Samples   | 25    | —            | —         | —           |

**Overall: PASS**

> Note: CI [0.69, 0.97] is wide — 25 samples may be insufficient for high confidence. Consider expanding the dataset.

## Per-item Results

| ID  | Input Summary                       | Expected | Actual   | Correct |
|-----|--------------------------------------|----------|----------|---------|
| 001 | Contract renewal, 3 pages, standard | approve  | approve  | ✓       |
| 002 | NDA with unusual liability clause   | escalate | escalate | ✓       |
| 003 | Vendor invoice, missing PO number   | reject   | reject   | ✓       |
| 004 | Employment agreement, standard terms| approve  | approve  | ✓       |
| 005 | Amendment with redlined IP clause   | escalate | approve  | ✗       |

## Notes

- Sample 005 misclassified: redlined IP clause not flagged as escalation trigger. Possible model drift.
- MLflow run: experiment `workflow-document-review/eval-basic/functional` — view with `mlflow ui`
```

**`human` type artifact:** instead of `report-human.md` with metrics, `--type=human` produces a checklist artifact (still named `report-human.md`) listing, per entry, its `input`, `expected_output.human_test` instructions, and the captured `actual_output` — with no Overall Results table, threshold, or PASS/FAIL section, since this type is never auto-scored.

#### 04-eval-mlflow-unique-port

Each `evals/<component>/eval-<name>/Makefile` MUST start its MLflow tracking server on a **unique port** to prevent conflicts when multiple eval Makefiles are run concurrently or in parallel (e.g., in CI or across multiple terminal sessions).

Ports MUST be statically assigned per eval scenario (not per test type) and MUST NOT reuse the default `5000` port (reserved for `dev-mlflow` per [agentme-edr-008](../devops/008-common-targets.md) rule `09-ai-project-dev-targets`). Assign ports starting at `5100` and incrementing by 1 for each additional eval scenario across the entire project.

The MLflow **experiment** (not the port) is scoped to the invoked `--type` value: `make eval-smoke` logs into an experiment containing only smoke-labeled runs (e.g. `<component>/<eval-name>/smoke`), while `make eval` (`--type=all`) logs into one experiment containing runs for every included test type (e.g. `<component>/<eval-name>/all`), each run tagged with its `test_type` since one entry can belong to more than one type.

## References

- [agentme-edr-007](../principles/007-project-quality-standards.md) — Project quality standards: when evals are required per AI tier (rule `09-ai-project-testing-requirements`) and statistical model eval targets (rule `07-statistical-models-must-have-eval-targets`)
- [agentme-edr-030](030-ai-test-types-taxonomy.md) — AI test types taxonomy: `test_types` enum, golden dataset entry envelope, and mocking constraints per type
- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards: LangChain framework and observability
- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent development standards
- [agentme-edr-021](021-ai-workflow-development-standards.md) — Workflow development standards
- [agentme-edr-024](024-ml-dataset-structure.md) — ML dataset structure, per-entry JSON format, and schema-lint validation for golden datasets
- [agentme-edr-008](../devops/008-common-targets.md) — `eval-<qualifier>` Makefile convention (rule `03`) and Mise tool-execution flow (rule `02`)
