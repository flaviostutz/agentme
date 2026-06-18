---
name: agentme-edr-policy-028-ai-eval-standards
description: Defines how to structure, write, and run eval tests for AI projects — folder layout, script requirements, and MLflow tracking. Use when implementing evals for LLM, Agent, or Workflow projects. For when evals are required see agentme-edr-007 rule 09-ai-project-testing-requirements.
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
      dataset/           # EDR-024 compliant dataset (README.md, dataset.schema.json, data/)
      eval-<name>.py     # evaluation script
      eval-<name>-report.md     # generated report (overwritten on each run — see rule 03)
      Makefile           # eval and run targets
    eval-<name2>/
      ...
  <component2>/
    ...
```

`<component>` MUST match the name of the component under evaluation and use lowercase hyphen-separated words (e.g., `workflow-document-review`, `agent-support`, `model-classifier`).

`<name>` identifies the specific evaluation scenario using lowercase hyphen-separated words (e.g., `eval-basic`, `eval-complex`, `eval-edge-cases`, `eval-bias-test`).

The `dataset/` subfolder MUST be a valid [agentme-edr-024](024-ml-dataset-structure.md) dataset — it MUST include `README.md` and `dataset.schema.json` at its root. For input/output pairs, use JSONL files per `agentme-edr-024.04-complex-structured-datasets-must-use-jsonl`.

Each `evals/<component>/eval-<name>/Makefile` MUST define:

| Target | Behaviour |
|---|---|
| `eval` | Runs the eval with threshold enforcement; exits non-zero on failure (CI-safe) |
| `run` | Runs the eval without threshold enforcement (exploration / debugging) |

The module root Makefile MUST expose a `make eval` target that delegates to `eval` in every `evals/<component>/eval-<name>/Makefile`:

```makefile
eval:
	$(MAKE) -C evals/workflow-document-review/eval-basic eval
	$(MAKE) -C evals/workflow-document-review/eval-complex eval
```

#### 02-eval-script-requirements

Each `eval-<name>.py` script MUST:

- Load the dataset from `dataset/` in the same eval folder, following [agentme-edr-024](024-ml-dataset-structure.md). For input/output pairs, use the JSONL format per `agentme-edr-024.04-complex-structured-datasets-must-use-jsonl`.
- Run every input through the live component against **real LLM providers** (not mocked responses), to capture model drift.
- Log per-sample and aggregate metrics to an MLflow experiment that runs **locally** — a remote MLflow server MUST NOT be required.
- Compare outputs to expected values using project-defined quality thresholds. Thresholds MUST be declared explicitly (e.g., in a Makefile variable or README).
- Write `eval-<name>-report.md` in the same folder per rule `03-eval-report-file`.
- Exit with a non-zero status when any metric falls below its defined threshold, consistent with [agentme-edr-007](../principles/007-project-quality-standards.md) rule `07-statistical-models-must-have-eval-targets`.

**Example:**

```python
import mlflow
from my_package.app.workflows.document_review_workflow.graph import graph

EVAL_MIN_ACCURACY = 0.85

with mlflow.start_run() as run:
    results = []
    for sample in load_dataset("dataset/"):
        output = graph.invoke({"document": sample["input"]})
        results.append(output["label"] == sample["expected_label"])

    accuracy = sum(results) / len(results)
    mlflow.log_metric("accuracy", accuracy)

    write_eval_report(run, results, thresholds={"accuracy": EVAL_MIN_ACCURACY})

    if accuracy < EVAL_MIN_ACCURACY:
        raise SystemExit(f"Eval failed: accuracy {accuracy:.2f} < {EVAL_MIN_ACCURACY}")
```

#### 03-eval-report-file

Each eval script MUST produce `eval-<name>-report.md` in the same `evals/<component>/eval-<name>/` folder and overwrite it on every run.

**Generation constraint:** The report MUST be produced programmatically, reading raw metric values directly from MLflow. No LLM or generative model may write, summarize, or paraphrase any section of the report, to prevent hallucinated metric values.

The report MUST follow this template:

```markdown
# Eval Report: <name>

**Date:** <ISO date>
**Dataset:** dataset/
**Script:** eval-<name>.py
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

**Filled-in example** (`evals/workflow-document-review/eval-basic/eval-basic-report.md` for a document review workflow):

```markdown
# Eval Report: eval-basic

**Date:** 2026-06-12
**Dataset:** dataset/
**Script:** eval-basic.py
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
|-----|-------------------------------------|----------|----------|---------|
| 001 | Contract renewal, 3 pages, standard | approve  | approve  | ✓       |
| 002 | NDA with unusual liability clause   | escalate | escalate | ✓       |
| 003 | Vendor invoice, missing PO number   | reject   | reject   | ✓       |
| 004 | Employment agreement, standard terms| approve  | approve  | ✓       |
| 005 | Amendment with redlined IP clause   | escalate | approve  | ✗       |

## Notes

- Sample 005 misclassified: redlined IP clause not flagged as escalation trigger. Possible model drift.
- MLflow run: experiment `workflow-document-review/eval-basic` — view with `mlflow ui`
```

## References

- [agentme-edr-007](../principles/007-project-quality-standards.md) — Project quality standards: when evals are required per AI tier (rule `09-ai-project-testing-requirements`) and statistical model eval targets (rule `07-statistical-models-must-have-eval-targets`)
- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards: LangChain framework and observability
- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent development standards
- [agentme-edr-021](021-ai-workflow-development-standards.md) — Workflow development standards

- [agentme-edr-024](024-ml-dataset-structure.md) — ML dataset structure for eval datasets
