---
name: agentme-edr-policy-021-ai-eval-standards
description: Defines how to structure, write, and run eval tests for AI projects — folder layout, script requirements, and MLflow tracking. Use when implementing evals for LLM, Agent, or Workflow projects. For when evals are required see agentme-edr-007 rule 09-ai-project-testing-requirements.
apply-to: Python AI projects (LLM, Agent, or Workflow tier) that implement eval testing
valid-from: 2026-06-05
---

# agentme-edr-policy-021: AI eval standards

## Context and Problem Statement

Eval tests measure AI component accuracy against expected outputs using real LLM providers. Without a shared folder layout and script convention, eval setups diverge across LLM, Agent, and Workflow projects, making them hard to run, compare, and integrate into CI/CD pipelines.

How should eval tests be structured and run across all AI tiers?

## Decision Outcome

**Use a per-component folder structure under `evals/` with a standardized Makefile interface and MLflow-backed scripts, applicable to LLM, Agent, and Workflow components.**

For when evals are required per AI tier, see [agentme-edr-007](../principles/007-project-quality-standards.md) rule `09-ai-project-testing-requirements`.

### Details

#### 01-eval-folder-structure

For each AI component being evaluated (an LLM chain, agent, or workflow), create a corresponding directory under `evals/` at the same level as `lib/` and `examples/`:

```text
evals/
  <component>/
    Makefile                  # eval targets for this component
    dataset_<group>/          # one folder per eval group (see agentme-edr-024)
    eval_<group>.py           # evaluation script for each group
```

Where `<component>` is the name of the LLM chain, agent, or workflow being evaluated (e.g., `summarizer`, `file_analyzer_agent`, `document_review_workflow`).

The per-component `evals/<component>/Makefile` MUST define:

| Target | Behaviour |
|---|---|
| `eval` | Runs all eval groups for the component |
| `eval-<group>` | Runs one named group (e.g. `eval-simple`, `eval-complex`) |

The module root Makefile MUST expose a `make eval` target that delegates to `eval` in every `evals/<component>/Makefile`:

```makefile
eval:
	$(MAKE) -C evals/summarizer eval
	$(MAKE) -C evals/document_review_workflow eval
```

#### 02-eval-script-requirements

Each `eval_<group>.py` script MUST:

- Load the dataset from `evals/<component>/dataset_<group>/` following [agentme-edr-024](024-ml-dataset-structure.md). For input/output pairs, use the JSONL format per `agentme-edr-024.04-complex-structured-datasets-must-use-jsonl`.
- Run every input through the live component against **real LLM providers** (not mocked responses), to capture model drift.
- Log per-sample and aggregate metrics to an MLflow experiment that runs **locally** — a remote MLflow server MUST NOT be required.
- Compare outputs to expected values using project-defined quality thresholds. Thresholds MUST be declared explicitly (e.g., in a Makefile variable or README).
- Exit with a non-zero status when any metric falls below its defined threshold, consistent with [agentme-edr-007](../principles/007-project-quality-standards.md) rule `07-statistical-models-must-have-eval-targets`.

**Example:**

```python
import mlflow
from my_package.app.workflows.document_review_workflow.graph import graph

EVAL_MIN_ACCURACY = 0.85

with mlflow.start_run():
    results = []
    for sample in load_dataset("evals/document_review_workflow/dataset_basic/"):
        output = graph.invoke({"document": sample["input"]})
        results.append(output["label"] == sample["expected_label"])

    accuracy = sum(results) / len(results)
    mlflow.log_metric("accuracy", accuracy)

    if accuracy < EVAL_MIN_ACCURACY:
        raise SystemExit(f"Eval failed: accuracy {accuracy:.2f} < {EVAL_MIN_ACCURACY}")
```

## References

- [agentme-edr-007](../principles/007-project-quality-standards.md) — Project quality standards: when evals are required per AI tier (rule `09-ai-project-testing-requirements`) and statistical model eval targets (rule `07-statistical-models-must-have-eval-targets`)
- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards: LangChain framework and observability
- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent development standards
- [agentme-edr-020](020-ai-workflow-development-standards.md) — Workflow development standards
- [agentme-edr-024](024-ml-dataset-structure.md) — ML dataset structure for eval datasets
