---
name: agentme-edr-policy-029-ai-workflow-naming-conventions
description: Defines the naming vocabulary for LangGraph workflow elements: node suffixes/prefixes, state type names, state attribute grouping, workflow class/variable names, judge node output schema, route function names, and cross-element coherence rules. Use when naming any part of a LangGraph workflow — nodes, states, routes, or the workflow itself. For workflow structure and toolchain see agentme-edr-021.
apply-to: AI workflow projects using LangGraph StateGraph built with Python
valid-from: 2026-06-21
---

# agentme-edr-policy-029: AI workflow naming conventions

## Context and Problem Statement

LangGraph workflows grow complex quickly. Without a shared naming vocabulary, node functions, state fields, route functions, and workflow classes diverge in style, making graphs hard to read, trace, and review. A reader should be able to follow the full lifecycle of a concept through a graph using names alone — without reading implementation code.

Which naming conventions should LangGraph workflow elements follow to make graphs self-documenting and unambiguous?

## Decision Outcome

**Adopt a suffix/prefix role convention for nodes, a `_state` suffix for state types, a grouping-prefix discipline for state attributes, and a coherence rule that ties all names to a single vocabulary word per concept.**

### Details

#### 01-node-naming-conventions

LangGraph node names MUST follow a suffix convention that communicates the node's role at a glance. Names MUST be action-oriented and descriptive.

| Convention | Node type | When to use |
|---|---|---|
| suffix `_llm` | LLM call | Any node whose primary action is a direct LLM inference call (see [agentme-edr-018](018-ai-llm-development-standards.md)) |
| suffix `_step` | Algorithmic step | Deterministic logic with no LLM involvement (transformation, validation, routing) |
| suffix `_tool` | Tool/API call | A node that wraps a single external tool or API (e.g. a REST endpoint, DB query) |
| suffix `_agent` | Subgraph agent | A node that invokes a nested subgraph containing its own tool-invocation cycle and LLM calls; use the **deepagents** library for these nodes (see [agentme-edr-019](019-ai-agents-development-standards.md)) |
| prefix `evaluate_` | Judge node | A node that evaluates the quality, correctness, completeness, or progress of prior outputs and returns a structured verdict; MUST follow rule `03-judge-node-output-format` |

The Python function implementing the node SHOULD share the same name as the node alias passed to `add_node`, so that graph definitions and stack traces remain unambiguous:

```python
def draft_doc_llm(state): ...
graph.add_node("draft_doc_llm", draft_doc_llm)

# Tool node — calls the Stripe API
def stripe_api_tool(state): ...
graph.add_node("stripe_api_tool", stripe_api_tool)

# Agent node — uses deepagents for tool-invocation loop
def code_reviewer_agent(state): ...
graph.add_node("code_reviewer_agent", code_reviewer_agent)
```

Names MUST NOT use generic labels such as `node1`, `process`, or `run`. Each name must clearly express what action the node performs.

Judge nodes use a **prefix** convention instead of a suffix: the name MUST start with `evaluate_` followed by the subject being judged (e.g. `evaluate_progress`, `evaluate_quality`, `evaluate_completeness`, `evaluate_relevance`). This makes judge nodes immediately distinguishable from all other node types at a glance.

**Grouping prefix for related nodes:** When multiple nodes deal with the same subject, entity, or workflow region, SHOULD use a shared grouping word as a prefix followed by a verb and the role suffix. The pattern is `<group>_<verb>_<role_suffix>`. This makes the graph topology scannable and clusters related nodes together alphabetically in logs, traces, and code.

```python
# Nodes grouped under the "invoice" subject
def invoice_fetch_tool(state): ...       # fetches invoice data from an API
def invoice_validate_step(state): ...    # validates invoice fields deterministically
def invoice_summarize_llm(state): ...    # summarizes invoice content with an LLM
def invoice_review_agent(state): ...     # runs an agent loop to review the invoice

graph.add_node("invoice_fetch_tool", invoice_fetch_tool)
graph.add_node("invoice_validate_step", invoice_validate_step)
graph.add_node("invoice_summarize_llm", invoice_summarize_llm)
graph.add_node("invoice_review_agent", invoice_review_agent)
```

The grouping prefix is optional for workflows where all nodes clearly belong to a single domain. It MUST be used when a workflow spans multiple subjects or regions (e.g. `invoice_*`, `payment_*`, `notification_*`) to prevent name collisions and to make the graph structure self-documenting.

Grouping names MUST be consistent across the entire workflow. Do not use synonyms or near-synonyms for the same concept (e.g. do not mix `invoice_*` and `bill_*`, or `user_*` and `account_*`, when they refer to the same entity). Pick one word per concept and apply it everywhere.

**Semantic word order in compound names:** When a name combines multiple semantic parts (group prefix, action, subject, role suffix), adjacent words MUST group semantically related concepts together. Do not insert an unrelated word between two words that belong together. More explicit names are preferred over ambiguous orderings, provided the name is not already verbose.

The test: read each pair of adjacent words — they should feel like a natural phrase. If an unrelated word splits two related words apart, reorder.

```python
# Preferred: "evaluate_skip" groups the evaluation and the action being evaluated
def map_evaluate_skip_step(state): ...    # map phase → evaluates whether to skip → deterministic

# Avoid: "skip" splits the "map" group from the "evaluate" role
def map_skip_evaluate_step(state): ...   # ambiguous: does it skip, or does it evaluate a skip?
```

This applies equally to state attributes and route function names.

#### 02-state-type-conventions

All TypedDict and dataclass types that represent LangGraph node or workflow state MUST end with `_state` in their name. This suffix signals at a glance that the type is a state boundary, not a plain data model.

**Naming reference:**

| Owner | Naming pattern | Example |
|---|---|---|
| Single agent / agent subgraph | `<agent_name>_agent_state` | `reviewer_agent_state` |
| Full workflow (`StateGraph`) | `<workflow_name>_workflow_state` | `document_workflow_state` |
| Named group of nodes sharing state | `<group_responsibility>_state` | `retrieval_pipeline_state` |

**Boundary rules:**

- Each agent or agent subgraph MUST define its own dedicated state type. Do not reuse or extend a generic state across unrelated agents.
- Each workflow (`StateGraph`) MUST define its own top-level state type. The workflow state is the authoritative boundary for that graph's inputs and outputs.
- When a group of nodes (not a full workflow and not a single agent) shares a state type, the type name MUST clearly reflect the shared responsibility. Generic names such as `shared_state`, `common_state`, or `global_state` are FORBIDDEN.
- Large workflows MUST NOT use a single monolithic state that all nodes read and write. Split the state into per-phase or per-agent state types scoped to the subgraph or set of nodes that produce or consume each field.

State type names SHOULD align with the agent or node names defined in rule `01-node-naming-conventions` (e.g., an agent node named `draft_doc_agent` has a state type named `draft_doc_agent_state`).

**State attribute naming — grouping and consistency:**

State attributes MUST follow the same grouping-prefix discipline as node names. When multiple attributes belong to the same subject, entity, or workflow phase, they MUST share a common prefix so that related fields cluster together and the state definition is self-documenting.

- Use `<group>_<attribute>` for fields that belong to a specific subject or phase (e.g. `invoice_raw`, `invoice_validated`, `invoice_summary`).
- The grouping prefix MUST be the same word used in the corresponding node names for that subject (e.g. nodes named `invoice_fetch_tool`, `invoice_validate_step` → state fields named `invoice_raw`, `invoice_validated`).
- Do not use synonyms or near-synonyms for the same concept across attributes or across nodes and attributes (e.g. do not mix `invoice_*` fields with `bill_*` fields, or `user_*` fields with `account_*` fields when they refer to the same entity). Pick one word per concept and apply it everywhere.

```python
class document_workflow_state(TypedDict):
    # "invoice" group — all fields related to the invoice entity
    invoice_raw: str
    invoice_validated: bool
    invoice_summary: str

    # "payment" group — all fields related to the payment entity
    payment_status: str
    payment_amount: float

    # "evaluate" group — judge verdicts
    evaluate_invoice_verdict: JudgeVerdict
```

Generic attribute names such as `data`, `result`, `output`, `info`, or `item` are FORBIDDEN unless they are top-level workflow inputs/outputs with no meaningful domain label.

#### 03-judge-node-output-format

Every node whose name starts with `evaluate_` (a judge node) MUST return a structured verdict object as its output. This ensures all judge nodes are interchangeable and their results can be uniformly consumed by downstream routing logic, logged, and compared across runs.

**Required output schema:**

```python
from typing import Literal, Optional
from dataclasses import dataclass, field

FindingLevel = Literal["OK", "INFO", "WARNING", "ERROR"]

@dataclass
class JudgeFinding:
    level: FindingLevel
    # MUST: short action-oriented label; < 10 words
    title: str
    # MUST when level != "OK": why this is an issue; < 30 words
    reason: Optional[str] = None
    # MUST when level != "OK": notes/findings using mandatory (MUST) or advisory (SHOULD) language; < 400 words
    details: Optional[str] = None
    # OPTIONAL: possible fixes, only when directly inferrable from the finding without further analysis; < 200 words
    fix: Optional[str] = None

@dataclass
class JudgeVerdict:
    # MUST: highest severity level across all findings; "OK" only when every finding is "OK"
    verdict: FindingLevel
    # MUST: at least one finding present
    findings: list[JudgeFinding] = field(default_factory=list)
```

Example (for logging, state storage, and inter-node communication):

```json
{
  "verdict": "WARNING",
  "findings": [
    {
      "level": "OK",
      "title": "All required sections present"
    },
    {
      "level": "WARNING",
      "title": "Code coverage below threshold",
      "reason": "Current coverage is 62%, minimum required is 80%.",
      "details": "The following modules have no test coverage: auth.py, payments.py. SHOULD add unit tests for all public methods in these modules.",
      "fix": "Add unit tests for auth.py and payments.py. Run `make test-coverage` to verify the threshold is met."
    }
  ]
}
```

**Routing from judge nodes:**

Downstream conditional edges MUST route on `verdict` only:

```python
def route_after_evaluate_quality(state) -> str:
    if state["evaluate_quality_result"].verdict in ("ERROR", "WARNING"):
        return "revise_draft_llm"
    return "publish_step"
```

**Logging:** Log `verdict` and the count of each level as MLflow metrics on the current run per [agentme-edr-021](021-ai-workflow-development-standards.md) rule `03-observability-and-experiment-tracking`.

#### 04-workflow-naming-conventions

LangGraph `StateGraph` instances and their enclosing classes MUST be given a meaningful name that conveys the workflow's input, output, and/or behavior. The name MUST end with `Workflow` (PascalCase class) or `_workflow` (snake_case variable or directory).

Choose a name that summarises what the workflow consumes, processes, and produces — avoid generic labels such as `Pipeline`, `Flow`, `Graph`, or `Process`.

| Context | Pattern | Example |
|---|---|---|
| Python class | `<DescriptiveName>Workflow` | `FileMapJudgeReduceWorkflow` |
| Python variable / instance | `<descriptive_name>_workflow` | `file_map_judge_reduce_workflow` |
| Directory under `app/workflows/` | `<descriptive_name>_workflow` | `financial_report_analysis_workflow/` |

**Good names** communicate purpose at a glance:

- `FileMapJudgeReduceWorkflow` — maps files, judges each, then reduces results
- `FinancialReportAnalysisWorkflow` — analyses financial report inputs
- `MarketingCampaignExecutorWorkflow` — executes a marketing campaign end-to-end

**Bad names** (FORBIDDEN): `MainWorkflow`, `AgentGraph`, `ProcessFlow`, `Workflow1`, `RunGraph`.

#### 05-cross-element-naming-coherence

All naming across a workflow MUST form a coherent, self-documenting vocabulary. By reading any single name — a workflow class, a node function, a state type, a state attribute, or a route function — it MUST be immediately clear what entity or phase it belongs to, what role it plays, and where its output lives in the state. A reader MUST be able to trace the full lifecycle of a concept through the graph using names alone, without reading implementation code.

**Coherence rules:**

1. **Workflow → state → directory:** A workflow class named `InvoiceAnalysisWorkflow` MUST own a top-level state named `invoice_analysis_workflow_state` and live in directory `invoice_analysis_workflow/`. The same root phrase (`invoice_analysis_workflow`) MUST appear in all three.

2. **Node → state field:** When a node writes a result to state, the state field MUST share the node's grouping prefix and communicate what was produced. The node `invoice_summarize_llm` writes to `invoice_summary`, not to `summary`, `llm_output`, or `result`. The group prefix (`invoice_`) MUST match exactly.

3. **Route → node:** Route functions MUST be named `route_after_<node_name>` using the exact name of the node they follow (e.g. `route_after_evaluate_invoice`). Do not name routes after what they decide — name them after their position in the graph.

4. **Agent node → agent state:** An agent node named `code_review_agent` MUST have a corresponding state type named `code_review_agent_state`. Do not reuse the parent workflow state or a generic state for the agent's internal fields.

5. **One word per concept, everywhere:** A concept introduced as `invoice` in a node name MUST remain `invoice` in every state attribute, route function, and subgraph that refers to it. Synonyms, abbreviations, and near-synonyms (e.g. mixing `invoice_*` with `bill_*`, or `user_*` with `account_*` for the same entity) are FORBIDDEN.

**Coherent example:**

```python
# Workflow and state share the same root phrase
class InvoiceProcessingWorkflow: ...

class invoice_processing_workflow_state(TypedDict):
    invoice_raw: str                       # written by invoice_fetch_tool
    invoice_validated: bool                # written by invoice_validate_step
    invoice_summary: str                   # written by invoice_summarize_llm
    evaluate_invoice_verdict: JudgeVerdict # written by evaluate_invoice

# Node names align with the state fields they produce
def invoice_fetch_tool(state): ...         # → invoice_raw
def invoice_validate_step(state): ...      # → invoice_validated
def invoice_summarize_llm(state): ...      # → invoice_summary
def evaluate_invoice(state): ...           # → evaluate_invoice_verdict

# Route named after the exact node it follows
def route_after_evaluate_invoice(state) -> str:
    if state["evaluate_invoice_verdict"].verdict == "ERROR":
        return "invoice_summarize_llm"
    return END
```

**Incoherent counter-example (FORBIDDEN):**

```python
class InvoiceProcessingWorkflow: ...

class billing_pipeline_state(TypedDict):  # FORBIDDEN: "billing" ≠ "invoice"
    raw_data: str                          # FORBIDDEN: no group prefix
    is_valid: bool                         # FORBIDDEN: no group prefix
    summary: str                           # FORBIDDEN: which node produced this?
    llm_result: JudgeVerdict              # FORBIDDEN: which judge, which subject?

def fetch_invoice(state): ...     # FORBIDDEN: no role suffix
def validate(state): ...          # FORBIDDEN: no group, no suffix
def summarize_invoice(state): ... # FORBIDDEN: verb before group (wrong order)
def check_quality(state): ...     # FORBIDDEN: "check" ≠ "evaluate" prefix
def after_quality_check(state): ... # FORBIDDEN: not named "route_after_<node>"
```

## References

- [agentme-edr-021](021-ai-workflow-development-standards.md) — Workflow structure, LangGraph toolchain, observability, and testing patterns
- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards (drives `_llm` node suffix and mocking patterns)
- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent development standards (drives `_agent` node suffix and state conventions)
