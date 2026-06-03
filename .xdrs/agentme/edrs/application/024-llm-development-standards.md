---
name: agentme-edr-policy-024-llm-development-standards
description: Defines the standard framework, provider compatibility, and observability approach for LLM-based applications in Python. Use when building, reviewing, or scaffolding any code that makes direct LLM calls, manages prompt context, or handles conversation history.
apply-to: Python projects that make LLM calls, manage prompt context, or handle conversation threads
valid-from: 2026-06-03
---

# agentme-edr-policy-024: LLM development standards

## Context and Problem Statement

LLM-based applications can be built at different levels of abstraction — from a single prompt call to a full autonomous agent or a complex multi-step workflow. Without a shared vocabulary and a prescribed framework, projects mix incompatible patterns for invoking models, managing context, and tracing requests.

Which framework should be used for LLM calls, how should providers be configured, and what is the canonical meaning of "LLM", "agent", and "workflow" in this codebase?

## Decision Outcome

**Use LangChain as the standard framework for all direct LLM interactions. Adopt a strict three-tier conceptual model — LLM / Agent / Workflow — that maps each tier to a specific library.**

### Conceptual model

Three distinct tiers of LLM-based computation are recognized in this project. Every component MUST be classified into exactly one tier:

| Tier | What it is | Library |
|---|---|---|
| **LLM** | A request → response prompt exchange with a model. May include a conversation history or thread. No autonomous decision-making. | `langchain` / `langchain-openai` |
| **Agent** | An LLM-based flow driven by a tool-invocation loop that the LLM itself plans and executes. The LLM decides which tools to call and when to stop. | `deepagents` |
| **Workflow** | A directed graph of nodes that mixes LLM-based nodes (simple LLM calls or agentic loops) with deterministic algorithmic nodes. The graph topology is defined in code, not chosen by the LLM at runtime. | `langgraph` |

These tiers nest: a Workflow may contain Agent nodes; an Agent uses LLM calls internally. The tier of a component is determined by its outermost controlling structure.

See [agentme-edr-018](018-ai-agent-development-standards.md) for Agent and Workflow implementation standards.

### Details

#### 01-conceptual-model

Every component that interacts with an LLM MUST be classified as exactly one of the three tiers defined in the conceptual model table above: **LLM**, **Agent**, or **Workflow**.

- Do NOT use the word "agent" to describe a component that only makes a single LLM call without a tool-invocation loop.
- Do NOT use the word "workflow" to describe a component that is purely an LLM call with no graph structure.
- When designing a new feature, identify the correct tier first. The tier determines which library and patterns apply (LangChain, deepagents, or LangGraph).

#### 02-llm-framework

All direct LLM calls MUST use **LangChain** via the `langchain` and `langchain-openai` packages.

- Use `langchain-openai` as the provider integration layer. It supports both OpenAI and Azure OpenAI through environment variables, with no code changes required to switch.
- Select the provider by setting `OPENAI_API_TYPE=azure` for Azure OpenAI or omitting it for OpenAI.
- Never hardcode provider-specific URLs, deployment names, or API versions in code; inject them through environment variables or a configuration object.

Minimum required environment variable surface:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | API key (both providers) |
| `OPENAI_API_BASE` / `AZURE_OPENAI_ENDPOINT` | Endpoint (Azure only) |
| `OPENAI_API_VERSION` | API version (Azure only) |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment/model name (Azure only) |
| `OPENAI_MODEL` | Model name (OpenAI only) |

LangChain chain or runnable definitions MUST be placed in `app/workflows/<workflow>/agents.py` (for workflow-scoped LLM calls) or in the appropriate application layer module. Do not inline LLM construction in adapter or CLI code.

#### 03-llm-observability

Enable LangChain auto-tracing at every application entry point by calling `mlflow.langchain.autolog()` during startup, before any LLM call is made.

- This captures inputs, outputs, token counts, and latency for every LangChain chain or runnable automatically.
- Pair with `mlflow.start_run()` at the workflow or agent level to group LLM traces under a named experiment run (see [agentme-edr-018](018-ai-agent-development-standards.md) for run-level MLflow instrumentation).
- Do not disable autolog in production unless there is an explicit performance justification documented in the codebase.

## References

- [agentme-edr-018](018-ai-agent-development-standards.md) — Agent and Workflow implementation standards (LangGraph, deepagents, MLflow run-level tracking)
- [agentme-edr-014](014-python-project-tooling.md) — Python project tooling and structure
