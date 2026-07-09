---
name: agentme-edr-policy-151-ai-eval-core-standards
description: Defines the eval folder structure and Makefile interface for AI projects, and the LLM-as-judge binary scoring contract applicable to all AI tiers and test types. Use when scaffolding evals or implementing an LLM judge. For eval script requirements see agentme-edr-153. For report format see agentme-edr-154. For repeatability see agentme-edr-155. For when evals are required see agentme-edr-501 rule 09-ai-project-testing-requirements. For the test type taxonomy see agentme-edr-152.
apply-to: Python AI projects (LLM, Agent, or Workflow tier) that implement eval testing
valid-from: 2026-06-05
---

# agentme-edr-policy-151: AI eval core standards

## Context and Problem Statement

Eval tests measure AI component accuracy against expected outputs using real LLM providers. Without a shared folder layout and a common LLM judge contract, eval setups diverge across LLM, Agent, and Workflow projects, making them hard to scaffold, run, and compare.

How should eval tests be structured, and how must LLM judges produce scores across all AI tiers?

## Decision Outcome

**Use a per-component folder structure under `evals/` with a standardized Makefile interface, and require all LLM judges to produce binary (`0`/`1`) output compatible with classification metrics.**

For when evals are required per AI tier, see [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09-ai-project-testing-requirements`.

### Details

#### 01-eval-folder-structure

Evals are grouped first by the component being evaluated, then by the specific evaluation scenario. Create one directory per component under `evals/`, and one directory per eval scenario inside it. Place `evals/` at the same level as `lib/` and `examples/`:

```text
evals/
  <component>/           # the component being evaluated (e.g., workflow-x, agent-y, model-z)
    eval-<name>/
      golden_dataset/    # EDR-024 + EDR-030 compliant golden dataset (README.md, dataset.schema.json, data/)
      eval.py            # evaluation script
      report-<type>.md   # generated report, one per evaluated test type (overwritten on each run — see agentme-edr-154 rule 01)
      Makefile           # lint, eval, run, and eval-<type> targets
    eval-<name2>/
      ...
  <component2>/
    ...
```

`<component>` MUST match the name of the component under evaluation and use lowercase hyphen-separated words (e.g., `workflow-document-review`, `agent-support`, `model-classifier`).

`<name>` identifies the specific evaluation scenario using lowercase hyphen-separated words (e.g., `eval-basic`, `eval-complex`, `eval-edge-cases`). A scenario's `golden_dataset` MAY mix multiple test types across its entries: label each entry with its applicable `test_types` ([agentme-edr-152](152-ai-test-types-taxonomy.md) rule `04`) and use the `eval-<type>` targets below to run one type at a time.

The `golden_dataset/` subfolder MUST be a valid [agentme-edr-201](../data/201-ml-dataset-structure.md) dataset (`README.md`, `dataset.schema.json`, one JSON file per entry under `data/` per rule `04-complex-structured-datasets-must-use-per-entry-json-files`, lint-validated per rule `06`) whose entries follow the golden dataset envelope defined in [agentme-edr-152](152-ai-test-types-taxonomy.md) rule `02`.

Each `evals/<component>/eval-<name>/Makefile` MUST declare a `TEST_TYPES` variable listing the `test_types` values present in its golden dataset, and define:

| Target | Behaviour |
|---|---|
| `lint` | Validates every `golden_dataset/data/*.json` file against `golden_dataset/dataset.schema.json` per [agentme-edr-201](../data/201-ml-dataset-structure.md) rule `06` |
| `eval` | Depends on `lint`; runs `eval.py --type=all` with threshold enforcement; exits non-zero on failure (CI-safe) |
| `run` | Depends on `lint`; runs `eval.py --type=all` with threshold enforcement; same as `eval` but intended for local exploration |
| `eval-<type>` | Depends on `lint`; runs `eval.py --type=<type>` for one declared test type, following [agentme-edr-303](../platform/303-common-targets.md) rule `03`'s `eval-<qualifier>` convention |

```makefile
TEST_TYPES := smoke functional safety

lint:
	mise exec -- uv run --project . python lint_dataset.py golden_dataset/

eval: lint
	mise exec -- uv run --project . python eval.py --type=all

run: lint
	mise exec -- uv run --project . python eval.py --type=all

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

#### 02-llm-as-judge-binary-output

LLM judges scoring component outputs MUST produce binary output: `0` (fail) or `1` (success). This rule applies to all AI tiers (LLM, Agent, Workflow) and to all eval test types that use an LLM judge (functional, quality, safety, repeatability, or any other).

**Requirements:**

- Judge prompts MUST instruct the model to output exactly `0` or `1`
- Scoring logic MUST parse the response and map to binary. Ambiguous/invalid responses: score as `0` or raise error
- Reports using LLM judges MUST use classification metrics (Accuracy, F1, Precision, Recall), not regression metrics (RMSE, R2, MAE)
- **F1 computation:** F1 MUST be computed from a binary confusion matrix treating score `1` as the positive class. In a standard golden dataset where every entry is expected to pass, all entries are true positives or false negatives (no true negatives exist), so Recall = TP / (TP + FN) and Precision = TP / (TP + FP) where FP = entries the judge scores `1` that the entry-level expected outcome marks as expected-fail. When all entries are expected-pass, Recall = Accuracy and Precision = 1, making F1 a conservative lower-bound on accuracy. Projects with adversarial or expected-fail entries MUST annotate each golden dataset entry with its expected binary outcome (`1` = should pass, `0` = should fail) in `expected_output` to enable a correct confusion matrix.
- Multi-class classification not supported. For multiple quality levels, use multiple binary judges (e.g., one for "factually correct", another for "tone appropriate")

**Rationale:** Binary output makes LLM judges compatible with classification metrics infrastructure (Accuracy, F1, Wilson CI, convergence analysis) defined in [agentme-edr-154](154-ai-eval-report-format.md) rule `01`.

**Example LLM judge prompt:**

```
Evaluate whether the document review decision is correct.

Input: {input_summary}
Expected: {expected_decision}
Actual: {actual_decision}

Output exactly "1" if the actual decision matches the expected decision and reasoning, or "0" if it does not.

Output:
```

## References

- [agentme-edr-153](153-ai-eval-script.md) — AI eval script: entry-first eval loop, `--type` filtering, `mock_fixtures`, and MLflow conventions
- [agentme-edr-154](154-ai-eval-report-format.md) — AI eval report format: `report-<type>.md` template, Wilson CI, and convergence analysis
- [agentme-edr-155](155-ai-eval-repeatability.md) — AI eval repeatability: loop exception, scoring methods (including LLM-as-judge per rule `02`), and cadence
- [agentme-edr-501](../governance/501-project-quality-standards.md) — Project quality standards: when evals are required per AI tier (rule `09`) and statistical model eval targets (rule `07`)
- [agentme-edr-152](152-ai-test-types-taxonomy.md) — AI test types taxonomy: `test_types` enum and golden dataset entry envelope
- [agentme-edr-201](../data/201-ml-dataset-structure.md) — ML dataset structure, per-entry JSON format, and schema-lint validation for golden datasets
- [agentme-edr-303](../platform/303-common-targets.md) — `eval-<qualifier>` Makefile convention (rule `03`)
