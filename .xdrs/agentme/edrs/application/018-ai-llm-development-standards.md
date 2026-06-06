---
name: agentme-edr-policy-018-ai-llm-development-standards
description: Defines the standard framework, provider configuration, observability approach, and unit testing patterns for simple LLM calls in Python. Use when building, reviewing, or scaffolding any code that makes direct LLM calls using LangChain, manages prompt context, or handles conversation history. For agentic patterns see agentme-edr-019, for workflow patterns see agentme-edr-020.
apply-to: Python projects that make direct LLM calls, manage prompt context, or handle conversation threads
valid-from: 2026-06-05
---

# agentme-edr-policy-018: AI LLM development standards

## Context and Problem Statement

LLM-based applications can be built at different levels of abstraction — from a single prompt call to a full autonomous agent or a complex multi-step workflow. Without a shared vocabulary and a prescribed framework, projects mix incompatible patterns for invoking models, managing context, and tracing requests.

Which framework should be used for LLM calls, how should providers be configured, and what is the canonical meaning of "LLM", "agent", and "workflow" in this codebase?

## Decision Outcome

**Use LangChain as the standard framework for all direct LLM interactions. Adopt a strict three-tier conceptual model — LLM / Agent / Workflow — that maps each tier to a specific library.**

This policy covers the **LLM** tier only. For the **Agent** tier, see [agentme-edr-019](019-ai-agents-development-standards.md). For the **Workflow** tier, see [agentme-edr-020](020-ai-workflow-development-standards.md).

### Conceptual model

Three distinct tiers of LLM-based computation are recognized in this project. Every component MUST be classified into exactly one tier:

| Tier | What it is | Library |
|---|---|---|
| **LLM** | A request → response prompt exchange with a model. May include a conversation history or thread. No autonomous decision-making. | `langchain` / `langchain-openai` |
| **Agent** | An LLM-based flow driven by a tool-invocation loop that the LLM itself plans and executes. The LLM decides which tools to call and when to stop. | `deepagents` |
| **Workflow** | A directed graph of nodes that mixes LLM-based nodes (simple LLM calls or agentic loops) with deterministic algorithmic nodes. The graph topology is defined in code, not chosen by the LLM at runtime. | `langgraph` |

These tiers nest: a Workflow may contain Agent nodes; an Agent uses LLM calls internally. The tier of a component is determined by its outermost controlling structure.

See [agentme-edr-019](019-ai-agents-development-standards.md) for Agent implementation standards and [agentme-edr-020](020-ai-workflow-development-standards.md) for Workflow implementation standards.

### Details

#### 01-conceptual-model

Every component that interacts with an LLM MUST be classified as exactly one of the three tiers defined in the conceptual model table above: **LLM**, **Agent**, or **Workflow**.

- Do NOT use the word "agent" to describe a component that only makes a single LLM call without a tool-invocation loop.
- Do NOT use the word "workflow" to describe a component that is purely an LLM call with no graph structure.
- When designing a new feature, identify the correct tier first. The tier determines which library and patterns apply (LangChain, deepagents, or LangGraph).

#### 02-llm-framework

All direct LLM calls MUST use **LangChain** via the `langchain` and `langchain-openai` packages.

- Use `langchain-openai` as the provider integration layer. It supports both OpenAI and Azure OpenAI.
- **Always configure LLM providers using explicit library attributes** such as `api_key`, `base_url`, `model`, `api_version`, etc. Never rely on environment variables for LLM configuration.
- Configuration MUST be passed via constructor parameters or configuration objects, making dependencies explicit and testable.

**Example of explicit configuration:**

```python
from langchain_openai import ChatOpenAI

# OpenAI configuration (explicit)
llm = ChatOpenAI(
    api_key=config.openai_api_key,
    model="gpt-4",
    temperature=0.7
)

# Azure OpenAI configuration (explicit)
llm = ChatOpenAI(
    api_key=config.azure_api_key,
    azure_endpoint=config.azure_endpoint,
    api_version="2024-02-15-preview",
    azure_deployment=config.azure_deployment
)
```

LangChain chain or runnable definitions MUST be placed in `app/workflows/<workflow>/agents.py` (for workflow-scoped LLM calls) or in the appropriate application layer module. Do not inline LLM construction in adapter or CLI code.

#### 03-llm-observability

Enable LangChain auto-tracing at every application entry point by calling `mlflow.langchain.autolog()` during startup, before any LLM call is made.

- This captures inputs, outputs, token counts, and latency for every LangChain chain or runnable automatically.
- Pair with `mlflow.start_run()` at the workflow or agent level to group LLM traces under a named experiment run (see [agentme-edr-020](020-ai-workflow-development-standards.md) for run-level MLflow instrumentation).
- Do not disable autolog in production unless there is an explicit performance justification documented in the codebase.

#### 04-unit-test-mocking

LLM provider calls are external API calls and MUST be mocked in unit tests per [agentme-edr-004](../principles/004-unit-test-requirements.md) rule `06-should-avoid-mocks`. Mocking LLM providers enables offline test execution while testing workflow logic, routing, and state management.

Use **LangChain's `FakeListChatModel`** or a custom `GenericFakeChatModel` wrapper for unit testing LLM calls:

```python
from langchain_core.language_models.fake_chat_models import FakeListChatModel

# Unit test with mocked LLM responses
def test_document_workflow_routing():
    fake_llm = FakeListChatModel(responses=[
        "APPROVE",
        "The document meets all quality criteria."
    ])
    
    workflow = DocumentWorkflow(llm=fake_llm)
    result = workflow.run(input_doc)
    
    assert result.status == "approved"
    assert "quality criteria" in result.reasoning
```

**Mocking boundaries:**

- Mocks are ONLY for unit tests (optional for LLM-tier projects). Integration tests SHOULD use real LLM providers when implemented (see [agentme-edr-020](020-ai-workflow-development-standards.md) rule `13-three-tier-testing-strategy`).
- Evals MAY be used for critical prompts to capture model drift (see [agentme-edr-020](020-ai-workflow-development-standards.md) rule `04-dataset-driven-accuracy-measurement`).
- Mock the LLM provider at the construction boundary (dependency injection), not by patching internal LangChain methods.
- Test files MUST follow the naming convention `<name>_test.py` for unit tests (see [agentme-edr-020](020-ai-workflow-development-standards.md) rule `13-three-tier-testing-strategy` for integration test naming).

When workflows or agents require injectable LLM instances, accept the LLM as a constructor parameter or configuration field:

```python
class DocumentWorkflow:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm or ChatOpenAI(
            api_key=config.openai_api_key,
            model="gpt-4"
        )
```

This allows unit tests to inject `FakeListChatModel` while production code uses the real provider.

### Testing Requirements

For LLM-tier projects (simple LangChain calls without agents or workflows):

- **Unit tests**: NOT required
- **Evaluation tests**: NOT required but SHOULD be used when critical prompts are being used to measure accuracy and detect model drift

## References

- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent implementation standards (deepagents, tool-invocation loops)
- [agentme-edr-020](020-ai-workflow-development-standards.md) — Workflow implementation standards (LangGraph, MLflow run-level tracking)
- [agentme-edr-004](../principles/004-unit-test-requirements.md) — Unit test requirements including external API mocking guidance
- [agentme-edr-014](014-python-project-tooling.md) — Python project tooling and structure
