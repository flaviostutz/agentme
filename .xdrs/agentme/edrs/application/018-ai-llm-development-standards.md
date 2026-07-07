---
name: agentme-edr-policy-018-ai-llm-development-standards
description: Defines the standard framework, provider configuration, observability approach, and LLM mocking patterns for simple LLM calls in Python. Use when building, reviewing, or scaffolding any code that makes direct LLM calls using LangChain, manages prompt context, or handles conversation history. For agentic patterns see agentme-edr-019, for workflow patterns see agentme-edr-021.
apply-to: Python projects that make direct LLM calls, manage prompt context, or handle conversation threads
valid-from: 2026-06-05
---

# agentme-edr-policy-018: AI LLM development standards

## Context and Problem Statement

LLM-based applications can be built at different levels of abstraction — from a single prompt call to a full autonomous agent or a complex multi-step workflow. Without a shared vocabulary and a prescribed framework, projects mix incompatible patterns for invoking models, managing context, and tracing requests.

Which framework should be used for LLM calls, how should providers be configured, and what is the canonical meaning of "LLM", "agent", and "workflow" in this codebase?

## Decision Outcome

**Use LangChain as the standard framework for all direct LLM interactions. Adopt a strict three-tier conceptual model — LLM / Agent / Workflow — that maps each tier to a specific library.**

### Conceptual model

Three distinct tiers of LLM-based computation are recognized in this policy. Every component MUST be classified into exactly one tier:

| Tier | What it is | Library |
|---|---|---|
| **LLM** | A request → response prompt exchange with a model. May include a conversation history or thread. No autonomous decision-making. | `langchain` / `langchain-openai` |
| **Agent** | An LLM-based flow driven by a tool-invocation loop that the LLM itself plans and executes. The LLM decides which tools to call and when to stop. | `deepagents` |
| **Workflow** | A directed graph of nodes that mixes LLM-based nodes (simple LLM calls or agentic loops) with deterministic algorithmic nodes. The graph topology is defined in code, not chosen by the LLM at runtime. | `langgraph` |

These tiers nest: in general, a Workflow may contain Agent nodes; an Agent uses LLM calls internally. The tier of a component is determined by its outermost controlling structure.

See [agentme-edr-019](019-ai-agents-development-standards.md) for Agent implementation standards and [agentme-edr-021](021-ai-workflow-development-standards.md) for Workflow implementation standards.

### Details

#### 01-conceptual-model

Every component that interacts with an LLM MUST be classified as exactly one of the three tiers defined in the conceptual model table above: **LLM**, **Agent**, or **Workflow**.

- Do NOT use the word "agent" to describe a component that only makes a single LLM call without a tool-invocation loop.
- Do NOT use the word "workflow" to describe a component that is purely an LLM call with no graph structure.
- When designing a new feature, identify the correct tier first. The tier determines which library and patterns apply (LangChain, deepagents, or LangGraph).

**Function calling boundary:**

- A **single** function call decided by the LLM (e.g., "call get_weather(location)") is still an LLM-tier interaction if the function is called once and the result is returned to the user.
- An **iterative** function-calling loop where the LLM observes results and decides next actions autonomously is an Agent (see [agentme-edr-019](019-ai-agents-development-standards.md)).

#### 02-llm-framework

All direct LLM calls MUST use **LangChain** via the `langchain` packages.

- Use `langchain-openai` as the provider integration layer. It supports both OpenAI and Azure OpenAI.
- LLM providers MUST be configured using explicit library attributes such as `api_key`, `base_url`, `model`, `api_version`, etc. MUST NOT rely on environment variables for LLM configuration.
- Configuration MUST be passed via constructor parameters or configuration objects, making dependencies explicit and testable.

**Example of explicit configuration:**

```python
# Azure OpenAI configuration (explicit)
llm = ChatOpenAI(
    api_key=config.azure_api_key,
    azure_endpoint=config.azure_endpoint,
    api_version="2024-02-15-preview",
    azure_deployment=config.azure_deployment
)
```

#### 03-llm-observability

Enable LangChain auto-tracing at every application entry point by calling `mlflow.langchain.autolog()` during startup, before any LLM call is made.

- This captures inputs, outputs, token counts, and latency for every LangChain chain or runnable automatically.
- The project Makefile MUST expose a `dev-mlflow` target to start a local MLflow tracking server for development inspection, per [agentme-edr-008](../devops/008-common-targets.md) rule `09-ai-project-dev-targets`.

#### 04-unit-test-mocking

LLM provider calls are external API calls and MUST be mocked in unit tests. Mocking LLM providers enables offline test execution while testing the logic, routing, and state management of LLM calls, agents, and workflows.

Use LangChain's built-in fake models from `langchain_core.language_models.fake_chat_models`. Choose the utility based on what the code under test expects from the model:

| Utility | When to use |
|---|---|
| `FakeListChatModel` | The code only reads the text content of the response (`AIMessage.content`). Returns plain-text `AIMessage` objects from a pre-defined list, in order. |
| `GenericFakeChatModel` | The code expects tool calls, structured outputs, or needs to inspect the message type beyond plain text. Accepts a list of pre-built `AIMessage` (or `AIMessageChunk`) objects, giving full control over the response structure. |

**`FakeListChatModel` — plain text responses:**

```python
from langchain_core.language_models.fake_chat_models import FakeListChatModel

def test_document_approval_routing():
    fake_model = FakeListChatModel(responses=[
        "APPROVE",
        "The document meets all quality criteria."
    ])

    workflow = DocumentWorkflow(model=fake_model)
    result = workflow.run(input_doc)

    assert result.status == "approved"
    assert "quality criteria" in result.reasoning
```

**`GenericFakeChatModel` — tool-call or structured responses:**

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
import json

def test_agent_tool_invocation():
    # Simulate the LLM requesting a tool call, then producing a final answer
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "search_files",
            "args": {"pattern": "*.py"},
            "id": "call_1"
        }]
    )
    final_msg = AIMessage(content="Found 3 Python files.")

    fake_model = GenericFakeChatModel(messages=iter([tool_call_msg, final_msg]))

    agent = FileAnalyzerAgent(model=fake_model)
    result = agent.run()

    assert result.summary == "Found 3 Python files."
```

**Injectable LLM pattern (required for testability):**

Whenever a workflow, agent, or node makes LLM calls, it MUST accept the LLM instance as a constructor parameter or configuration field so that unit tests can inject a fake:

```python
class DocumentWorkflow:
    def __init__(self, model: Optional[BaseChatModel] = None):
        self.model = model or ChatOpenAI(
            api_key=config.openai_api_key,
            model="gpt-4"
        )
```

This allows unit tests to inject `FakeListChatModel` or `GenericFakeChatModel` while production code uses the real provider.

#### 05-prompt-management

Prompt templates MUST be managed explicitly and versioned:

- Store prompt templates as separate files in `prompts/` directory when they exceed 10 lines or are reused across multiple components.
- Use LangChain `PromptTemplate` or `ChatPromptTemplate` for parameterized prompts.

**Example prompt file structure:**

```text
lib/src/<package_name>/
  prompts/
    summarize.txt
    extract_entities.txt
```

**Example usage:**

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_file(
    "prompts/summarize_v1.0.0.txt",
    input_variables=["document"]
)
```

#### 06-output-length-constraints

Every free-text field generated by an LLM MUST have an explicit word or token limit defined wherever the content is specified — in prompt text, output schema definitions, or both. This prevents runaway verbosity, reduces token costs, and makes quality evaluation deterministic.

**Rules:**

- Append `[max N words]` (or `[max N tokens]` when appropriate) directly inside the instruction or field description that requests the generated content.
- Apply the constraint to every level: the top-level prompt instruction AND any nested schema field that contains free text.
- When a field is an enumeration or a short code (e.g., `"APPROVE"` / `"REJECT"`), no word limit is needed.
- Inline examples are encouraged whenever the expected output style is non-obvious.

**Prompt example:**

```text
Generate a summary of this text. [max 40 words]
Identify the three main topics covered. [max 10 words each]
```

**Output schema example:**

```python
class EvaluationResult(BaseModel):
    evaluation: str = Field(description="Most important aspects of the text [max 100 words]")
    verdict: Literal["PASS", "FAIL"]
    improvement_suggestion: str = Field(description="Concrete next step for the author [max 30 words]")
```

**Combined prompt + schema example:**

```python
prompt = """
Evaluate the following document against our quality criteria. [max 200 words total]

Return a JSON object with:
- "evaluation": overall assessment [max 100 words]
- "verdict": "PASS" or "FAIL"
- "improvement_suggestion": one concrete improvement [max 30 words]
"""
```

## References

- [agentme-edr-019](019-ai-agents-development-standards.md) — Agent implementation standards (deepagents, tool-invocation loops)
- [agentme-edr-021](021-ai-workflow-development-standards.md) — Workflow implementation standards (LangGraph, MLflow run-level tracking)
- [agentme-edr-004](../principles/004-unit-test-requirements.md) — Unit test requirements including external API mocking guidance
- [agentme-edr-014](014-python-project-tooling.md) — Python project tooling and structure
- [agentme-edr-007](../principles/007-project-quality-standards.md) — Project quality standards including AI-tier testing requirements (rule `09-ai-project-testing-requirements`)
- [agentme-edr-028](028-ai-eval-standards.md) — AI eval standards: folder structure, script requirements, and MLflow tracking
