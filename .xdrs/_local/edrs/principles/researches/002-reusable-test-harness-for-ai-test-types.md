# _local-edr-research-002: Reusable Test Harness for AI Test Types

## Abstract

`_local-edr-research-001` cataloged 12 AI-application test types across 5 groups but left open how to implement them without writing bespoke code per type. This study asks whether a single harness — a fixed dataset envelope, a runner that invokes the component under test, and a pluggable scorer — can cover most of those 12 types by changing only the dataset content and the scorer plugin. Methods compared agentme's existing dataset/eval conventions (agentme-edr-024, agentme-edr-028) against two external harnesses, promptfoo and DeepEval, that already generalize this pattern across many test objectives. Results show agentme's own folder/script convention already has the same three-part shape as both external tools, and mapped all 12 test types against what actually varies between them. The harness covers 10 of 12 rows by swapping dataset content and scorer; Unit test (offline, mocked) is structurally different (no dataset, no scorer) and stays outside it; adversarial/red-team and robustness additionally need an input-generation step before the shared runner. The practical takeaway is that agentme does not need a new framework — it needs to name "Scorer" as an explicit pluggable extension point in its eval convention.

## Introduction

`_local-edr-research-001` produced a taxonomy of 12 AI-application test types — code-level, prompt/LLM, quality eval, safety/adversarial, and responsible AI (fairness, bias, robustness, explainability). It showed that agentme-edr-028 already prescribes a folder layout (`evals/<component>/eval-<name>/dataset/`, `eval.py`, `report.md`, `Makefile`) and agentme-edr-024 a dataset layout (`README.md`, `dataset.schema.json`, JSONL/CSV/`data/`) for the "Golden-dataset accuracy / LLM-as-judge eval" row, but did not examine whether that same machinery can implement the other dataset/provider-driven rows — RAG groundedness, human evaluation, safety/content, adversarial, fairness, bias, robustness, explainability — without a fresh `eval.py` per row.

agentme-edr-028 rule `02-eval-script-requirements` shows exactly one worked example: an `eval.py` that loads a dataset, invokes a workflow graph, and compares an output field to an expected label with a hardcoded accuracy calculation. Nothing states which parts of that script should change when the objective moves from accuracy to bias or groundedness, versus which parts stay identical. Left unstated, every new test type risks becoming a full rewrite instead of a configuration change.

**Constraints and assumptions:**

- This study treats the "harness" question as applying to the 10 rows from research 001 whose Level includes Integration Tests or Production Tests and whose Can Use Mocks is "No" or "Not for LLM calls" — i.e., every row except Unit test (offline, mocked), which is intentionally excluded because it has no dataset and no scorer in the sense used here.
- Per the requester's direction, external evidence is reviewed only to answer whether it offers something better than agentme's existing LangChain/LangGraph/MLflow-based approach for this specific harness-and-swappable-dataset question, not as a general framework survey.
- The study does not implement or benchmark any concrete scorer; it maps what a shared harness would need to expose as an extension point.
- Per direction from the requester, this research is exploratory: it does not propose a new EDR and is not paired with a planned Policy change.

The objective is to determine which parts of a dataset-driven AI test can be shared across test types in one reusable harness, and which parts must genuinely vary per type or group, so that implementing a new test objective becomes primarily a matter of authoring a new dataset and selecting or writing a scorer.

Question: Can agentme's existing dataset/eval conventions be organized as one reusable harness where only the dataset content and the scorer plugin change per test type, and if so, which concrete technique does each type/group need for that scorer?

## Methods

The study proceeded in four steps.

**Step 1 — Re-read agentme's existing dataset-driven testing conventions.** agentme-edr-024 (ML dataset structure: mandatory `README.md` + `dataset.schema.json`, plus type-specific data placement for file/annotation pairs, tabular CSV, and JSONL) and agentme-edr-028 (eval folder layout, `eval.py` requirements, MLflow logging, Wilson-score-CI report format, per-eval-scenario Makefile targets) were re-read in full to extract the exact shape of agentme's current harness: what is fixed by policy (folder names, report template, threshold enforcement) versus what is left to each `eval.py` author (the comparison/scoring logic itself, currently shown only as a hardcoded accuracy check in the rule's example). agentme-edr-018 rule `04-unit-test-mocking` was re-read to confirm the boundary case (Unit test (offline, mocked) has no analogous dataset/scorer split — it uses fakes and plain assertions) and agentme-edr-007 rule `09-ai-project-testing-requirements` was re-read for which tiers currently require this machinery.

**Step 2 — Review two external harnesses for the same shared-runner-plus-swappable-dataset pattern.** Two tools were selected because they are widely used and each already generalizes "one harness, many test objectives" across a range comparable to research 001's 12 types, rather than being single-metric point solutions:

1. **promptfoo** (docs: `configuration/guide`, `red-team/quickstart`) — a YAML-configured harness where `tests:` entries (loadable from YAML/JSON/CSV/JSONL/Google Sheets/Azure Blob) each carry `vars` (the dataset content) and one or more `assert` entries (`contains-json`, `javascript`, `similar` embedding-similarity, `llm-rubric` model-graded assertions); the same `assert` engine is reused by the `redteam` subsystem, which auto-generates adversarial `tests` entries from vulnerability "plugins" (jailbreak, prompt injection, PII, bias) and attack "strategies," then scores them with the identical assertion mechanism used for ordinary accuracy tests.
2. **DeepEval** (docs: `getting-started`, `metrics-introduction`) — a Python harness where an `LLMTestCase` (`input`, `actual_output`, `expected_output`, optional `retrieval_context`/`tools_called`) is the fixed dataset envelope, and a `Metric` object (`GEval` for custom LLM-as-judge rubrics, `DAGMetric` for deterministic decision-tree scoring, or 50+ predefined metrics such as `BiasMetric`, `FaithfulnessMetric`, `TaskCompletionMetric`, `AnswerRelevancyMetric`) is the pluggable scorer; the same `test_case` + `metrics=[...]` call shape is reused unchanged across RAG, agent, chatbot/multi-turn, and safety metric categories, and integrates with LangChain/LangGraph traces via a callback handler rather than replacing them.

**Step 3 — Extract the common three-part shape.** Both external tools and agentme's own convention decompose into the same three parts: (a) a **Dataset** of items with a fixed envelope — input/context plus an optional expected value and metadata; (b) a **Runner** that iterates the dataset, invokes the real component, and captures the actual output (and, for RAG/agent cases, retrieved context or tool calls); (c) a pluggable **Scorer** selected per test objective, producing a 0–1 (or pass/fail) score plus a reason, aggregated against a threshold. This shape was used as the lens for Step 4.

**Step 4 — Map each of research 001's 12 test types against the three-part shape.** For every row, this study recorded whether it fits the shape at all (Fits / Partial / N/A), what specifically differs in Dataset content, and what specifically differs in Scorer/technique, reusing agentme-edr-024's dataset-type categories (JSONL for complex records, CSV for tabular, file+annotation for images/documents) and agentme-edr-028's report/threshold conventions as the constant Runner/Report layer. This mapping is the basis for the Results table.

## Results

### The common three-part harness shape

Every dataset-driven test type examined decomposes into the same three parts, matching both agentme's own convention and the two external tools reviewed:

```text
Dataset (edr-024: README + schema + JSONL/CSV/data)
  -> Runner (edr-028: eval.py — load dataset, invoke real component, capture output)
    -> Scorer (varies per test type — the one part not yet named as a pluggable unit in edr-028)
      -> Report + threshold (edr-028: report.md, Wilson-score CI, pass/fail exit code)
```

A single dataset item envelope covers every row examined: `{id, input, context?, expected?, metadata?}`, filled at runtime with `actual_output` (and, for RAG/agent rows, `retrieved_context` or `tool_calls`) before scoring.

### Test type mapping against the harness shape

| # | Type Name (from research 001) | Group | Fits shared harness? | What differs — Dataset content | What differs — Scorer / technique |
|---|---|---|---|---|---|
| 1 | Safety/content eval | Safety & adversarial | Fits | Prompts probing harmful/policy-violating topics | Classifier or `llm-rubric`-style safety scorer |
| 2 | Adversarial / red-team test | Safety & adversarial | Partial | Attack-pattern inputs — MUST be generated, not just authored (plugin/strategy or PyRIT-style generator) | Vulnerability-plugin scorer (jailbreak/injection detectors) |
| 3 | Fairness test | Responsible AI | Fits | Paired inputs across demographic groups | Disparate-impact / demographic-parity scorer |
| 4 | Bias test | Responsible AI | Fits | Counterfactual/template probe inputs | Stereotype/representation classifier scorer (e.g. `BiasMetric`) |
| 5 | Robustness test | Responsible AI | Partial | Perturbed/OOD inputs — MUST be generated by fuzzing the base dataset | Correctness scorer re-run on perturbed inputs, diffed against base |
| 6 | Explainability test | Responsible AI | Fits | Inputs requiring a rationale in the output | Rationale-faithfulness / citation-check scorer |
| 7 | RAG groundedness/faithfulness eval | Quality eval | Fits | Input + retrieved `context` field required | Groundedness/faithfulness scorer (e.g. `FaithfulnessMetric`) |
| 8 | Human evaluation | Quality eval | Fits | Same dataset as row 9, sampled for review | Human labeling UI in place of an automated scorer |
| 9 | Golden-dataset accuracy / LLM-as-judge eval | Quality eval | Fits (agentme's current worked example) | Input + expected output/label | Exact-match/F1/similarity scorer, or `llm-rubric`/`GEval` when no ground truth |
| 10 | Prompt regression test | Prompt/LLM | Fits | Same input across prompt/model versions | Diff/equality scorer against last known-good output |
| 11 | Integration test | Code-level | N/A | No dataset envelope — real dependency wiring only | Assertion on side effects, no scorer object |
| 12 | Unit test (offline, mocked) | Code-level | N/A | No dataset — fakes (`FakeListChatModel`) supply canned responses | Plain `assert`, no scorer object |

Nine of the twelve rows fit the shared harness by only changing dataset content and the scorer; two (Adversarial/red-team, Robustness) additionally need an input-generation step before the shared runner; two (Integration test, Unit test) are structurally outside the shape. Across the ten dataset/provider-driven rows, five different scorer techniques recur: exact-match/similarity/F1 (row 9), an `llm-rubric`/`GEval`-style model-graded rubric (rows 1, 6, 9), a classifier trained or prompted for a specific label such as bias or safety (rows 1, 3, 4), a groundedness/faithfulness comparison against retrieved context (row 7), and a diff/equality check against a prior known-good output (row 10) — meaning a harness needs to ship only a handful of scorer implementations, not one per row.

### Harness options compared

| Option | Test-case abstraction | Pluggable scorer/assertion | Auto-generates adversarial data | RAG/agent support | LangChain/LangGraph/MLflow fit | Pros | Cons |
|---|---|---|---|---|---|---|---|
| agentme-edr-028 current pattern | Ad hoc per `eval.py` | Hardcoded per script (no named extension point yet) | No | Possible, not templated | Native (already the standard) | No new tool, already MLflow-logged and local-only | Every new test type currently means rewriting `eval.py`, not swapping a plugin |
| promptfoo | YAML `tests` + `vars` | `assert` types (`contains-json`, `javascript`, `similar`, `llm-rubric`) | Yes — `redteam` plugins/strategies | Yes, via HTTP/script/browser targets | External CLI/config layer alongside LangChain/MLflow, not native | Attack-pattern generation and CSV/JSONL/Sheets loading built in | Introduces a second config language and runner outside agentme's Python/Makefile convention |
| DeepEval | `LLMTestCase` / `Golden` | `Metric` classes (50+, incl. `BiasMetric`, `FaithfulnessMetric`, `TaskCompletionMetric`) | Only via companion "DeepTeam" tool | Yes, native tracing for LangChain/LangGraph/CrewAI/etc. | Integrates via callback handler, doesn't replace MLflow logging | Ready-made scorers for most Responsible-AI/RAG/agent rows; native LangChain/LangGraph hooks | Most metrics are LLM-as-judge and its cloud reporting (Confident AI) is optional but central to its intended workflow |

## Discussion

The central finding is that agentme's own eval convention already has the right shape — it is not missing a harness, it is missing a name for the one part that should vary: the Scorer. agentme-edr-028 rule `02-eval-script-requirements`'s only example hardcodes an accuracy comparison inline in `eval.py`, so nothing currently tells an author writing a bias, safety, or groundedness eval that the dataset-load/invoke/report skeleton is meant to be copied unchanged while only the scoring function and the dataset's `dataset.schema.json` are supposed to differ. That ambiguity is exactly what causes each new test type to be treated as a fresh script rather than a configuration choice.

Both external tools confirm the same three-part decomposition independently arrived at different ecosystems (a YAML-config tool and a Python-native tool), which is evidence the shape itself is sound rather than an artifact of agentme's own conventions. Neither tool, however, is a clear replacement for agentme's approach: promptfoo's YAML/CLI model sits outside the Python/LangChain/LangGraph/MLflow stack agentme-edr-018 and agentme-edr-028 already standardize on, and DeepEval's most valuable scorers (Responsible-AI and RAG metrics) are LLM-as-judge implementations that would still need to be wired into agentme-edr-028's existing MLflow-based reporting rather than adopted wholesale. The practical opportunity is narrower and cheaper: extract a small internal `Scorer` interface — one implementation per test type or group (exact-match/similarity, `llm-rubric`, bias/toxicity classifier, groundedness) — that plugs into the existing `eval.py`/`report.md`/MLflow skeleton agentme-edr-028 already mandates, optionally reusing DeepEval's or promptfoo's individual scorer implementations rather than the whole framework, where that is cheaper than writing one internally.

Adversarial/red-team and robustness are the genuine exceptions the mapping surfaces: for these two rows, the dataset itself cannot simply be hand-authored like an accuracy dataset — it must be generated (attack-pattern library, PyRIT-style automated red-teaming, or input-perturbation/fuzzing), which is an extra pipeline stage upstream of the shared Runner rather than a difference in the Runner or Scorer. Any future EDR that names the Scorer extension point should treat this input-generation stage as a separate, optional pre-processing step rather than folding it into the same abstraction, since conflating the two would overstate what "just changing the dataset" can mean for these two rows specifically.

Human evaluation is a partial special case worth flagging: it reuses the exact same dataset and Runner as the automated Golden-dataset/LLM-as-judge row, with a human reviewer substituted for the automated Scorer — evidence that "swap the scorer" should be read broadly enough to include a manual labeling step, not only an automated function.

The main limitation of this study is that it did not implement or benchmark any concrete scorer, so the claim that "only dataset and scorer change" is a structural argument, not a measured one; a follow-up spike building two or three scorers against agentme-edr-028's existing skeleton would validate or falsify it directly. The external evidence set is again two tools, not an exhaustive survey, chosen specifically because they already generalize across many test objectives rather than for market coverage.

## Conclusion

A single reusable harness — agentme-edr-024's dataset conventions feeding agentme-edr-028's runner/report/MLflow skeleton, plus a newly named pluggable Scorer — can implement 10 of research 001's 12 test types by changing only the dataset content and the Scorer plugin. Adversarial/red-team and robustness additionally require an input-generation stage before the shared runner, since their datasets must be adversarially generated or perturbed rather than hand-authored. Unit test (offline, mocked) and Integration test remain structurally outside this shape, since neither uses a dataset-plus-scorer in this sense.

The practical takeaway is that agentme does not need to adopt an external framework such as promptfoo or DeepEval wholesale — its own edr-024/edr-028 pattern already matches their shape — but it does need to name "Scorer" as an explicit, swappable extension point rather than leaving scoring logic hardcoded inline in each `eval.py`, and to treat adversarial/robustness dataset generation as a distinct upstream stage.

This research is exploratory and does not propose a Policy change. Open questions for any follow-up: which concrete Scorer implementations agentme should build in-house versus reuse from promptfoo/DeepEval for hard metrics (bias, faithfulness, task completion); how a `Scorer` interface should be expressed in Python within agentme-edr-028's existing `eval.py` convention; and how the adversarial/robustness input-generation stage should be specified so it composes with, rather than replaces, the shared runner.

## References

- [agentme-edr-030](../../../../agentme/edrs/application/030-ai-test-types-taxonomy.md) - Adopted Policy: names the Scorer's input via the golden dataset `test_types` label and shared envelope this study argued for
- [_local-edr-research-001](001-ai-application-testing-taxonomy.md) - The 12-type, 5-group taxonomy this study builds on
- [agentme-edr-024](../../../../agentme/edrs/application/024-ml-dataset-structure.md) - Dataset folder/schema conventions used as the harness's Dataset layer
- [agentme-edr-028](../../../../agentme/edrs/application/028-ai-eval-standards.md) - Eval folder, script, and report conventions used as the harness's Runner/Report layer
- [agentme-edr-018](../../../../agentme/edrs/application/018-ai-llm-development-standards.md) - Mocking pattern that keeps Unit test (offline, mocked) outside this harness
- [agentme-edr-007](../../../../agentme/edrs/principles/007-project-quality-standards.md) - Per-tier testing requirements (rule `09-ai-project-testing-requirements`)
- [promptfoo configuration guide](https://www.promptfoo.dev/docs/configuration/guide/) - YAML test-case/assertion model and dataset loading options
- [promptfoo red-team quickstart](https://www.promptfoo.dev/docs/red-team/quickstart/) - Plugin/strategy-based adversarial dataset generation reusing the same assertion engine
- [DeepEval getting started](https://deepeval.com/docs/getting-started) - `LLMTestCase`/`Golden` dataset envelope and LangChain/LangGraph tracing integration
- [DeepEval metrics introduction](https://deepeval.com/docs/metrics-introduction) - Pluggable `Metric` categories (RAG, agent, chatbot, safety) reused across test objectives
