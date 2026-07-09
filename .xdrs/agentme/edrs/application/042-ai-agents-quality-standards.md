---
name: agentme-edr-policy-042-ai-agents-quality-standards
description: Defines implementation quality standards for AI agents: tool definition patterns, error handling and recovery, observability, and unit testing. Apply alongside agentme-edr-041 when implementing or reviewing agent code. For agent architecture and structural decisions (framework, sandbox, naming, composition, system prompts) see agentme-edr-041.
apply-to: AI agent implementation code — apply when writing tools, error handlers, logging, and unit tests for agents
valid-from: 2026-06-09
---

# agentme-edr-policy-042: AI agents quality standards

## Context and Problem Statement

Beyond selecting the right framework and structural patterns, agent implementations require consistent standards for how tools are defined, how errors are handled, how execution is observed, and how agents are tested. Without these standards, agents become hard to debug, unreliable, and untestable.

How should agent tools be defined, what error handling must agents implement, how should agent execution be observed, and how should agents be unit tested?

## Decision Outcome

**Agent implementations MUST follow the tool definition, error handling, observability, and unit testing standards defined here, alongside the structural decisions in [agentme-edr-041](041-ai-agents-development-standards.md).**

### Details

#### 01-tool-definition-patterns

Tools provided to agents MUST follow these patterns:

**Tool signature:**

```python
from typing import Any, Dict

def tool_name(arg1: str, arg2: int) -> Dict[str, Any]:
    """
    Brief description of what the tool does.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Dictionary with tool execution results
    """
    # Tool implementation
    return {"status": "success", "result": ...}
```

**Tool requirements:**

- Tool names MUST be descriptive action verbs (e.g., `search_files`, `execute_command`, `read_document`)
- Tool docstrings MUST clearly describe the tool's purpose, arguments, and return value (the LLM reads these)
- Tools MUST return structured data (dictionaries or dataclasses), not bare strings or untyped values
- Tools MUST handle errors gracefully and return error information in the result structure, not raise exceptions
- Tools that interact with external systems MUST be placed in `adapters/connectors/` per [agentme-edr-026](026-pragmatic-hexagonal-architecture.md)

**Error handling in tools:**

```python
def search_files(pattern: str, directory: str = ".") -> Dict[str, Any]:
    """Search for files matching a glob pattern."""
    try:
        matches = list(Path(directory).glob(pattern))
        return {
            "status": "success",
            "matches": [str(m) for m in matches],
            "count": len(matches)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }
```

#### 02-agent-error-handling-and-recovery

Agents MUST implement robust error handling:

**Maximum iteration limits:**

- Every agent MUST have a maximum iteration limit to prevent infinite loops
- The default maximum SHOULD be configurable and logged when reached
- When the maximum is reached, the agent MUST return a structured failure result, not raise an exception

**Tool failure handling:**

- When a tool returns an error, the agent MUST be able to observe the error and decide on recovery actions
- Tools MUST NOT raise exceptions for expected failures (network errors, file not found, etc.)
- Agents MAY implement retry logic with exponential backoff for transient failures

**Terminal states:**

Agents MUST recognize and handle three terminal states:
- **Success**: Goal achieved, task complete
- **Failure**: Goal cannot be achieved, give up gracefully
- **Timeout**: Maximum iterations reached, return partial results if possible

#### 03-agent-observability

Agent execution MUST be observable through logging and tracing:

- Log each iteration of the perceive → plan → act → observe cycle with iteration number and tool selection.
- Use structured logging (JSON) with fields: `iteration`, `tool_selected`, `tool_result_status`, `decision`.
- For LLM calls within agents, follow [agentme-edr-040](040-ai-llm-development-standards.md) rule `03-llm-observability`.
- When agents run as workflow nodes, MLflow tracking from the parent workflow automatically captures agent-level traces.
- The project Makefile MUST expose a `dev-mlflow` target to start a local MLflow tracking server for development inspection, per [agentme-edr-008](../platform/008-common-targets.md) rule `09-ai-project-dev-targets`.

**Example structured log entry:**

```json
{
  "timestamp": "2026-06-05T10:30:45Z",
  "agent": "FileAnalyzerAgent",
  "iteration": 3,
  "tool_selected": "search_files",
  "tool_args": {"pattern": "*.py"},
  "tool_result_status": "success",
  "decision": "continue"
}
```

#### 04-agent-unit-testing

Agent LLM calls are external API calls and MUST be mocked in unit tests per [agentme-edr-040](040-ai-llm-development-standards.md) rule `04-unit-test-mocking`.

Because agents drive a tool-invocation loop — where the LLM decides which tools to call — the fake model must return **tool-call messages** followed by a final answer. Use **`GenericFakeChatModel`** for this:

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

def test_file_analyzer_agent_calls_search_then_stops():
    # Iteration 1: LLM requests a tool call
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "search_files",
            "args": {"pattern": "*.py", "directory": "/workspace"},
            "id": "call_1"
        }]
    )
    # Iteration 2: LLM produces a final answer after observing the tool result
    final_msg = AIMessage(content="Found 3 Python files matching the pattern.")

    fake_model = GenericFakeChatModel(messages=iter([tool_call_msg, final_msg]))

    agent = FileAnalyzerAgent(model=fake_model)
    result = agent.run(directory="/workspace")

    assert result.status == "success"
    assert "3 Python files" in result.summary
```

Agents MUST be designed so that the LLM instance is injectable (constructor parameter) to allow test doubles. See [agentme-edr-040](040-ai-llm-development-standards.md) rule `04-unit-test-mocking` for the injectable LLM pattern.

**`mock_deep_agent`**

Place `mock_deep_agent` in a shared test utilities module (e.g., `tests/helpers.py`) so all test files that need it can import it from one location and mock deep_agent instances when needed.

**Example usage:**

```python
from tests.helpers import mock_deep_agent

def test_workflow_calls_subagent(mocker):
    mock_deep_agent(
        mocker,
        "mypackage.nodes.analysis_node.create_workflow_agent",
        output={"status": "success", "findings": ["issue A"]}
    )

    result = run_analysis_workflow(input_data)

    assert result.findings == ["issue A"]
```

## References

- [agentme-edr-041](041-ai-agents-development-standards.md) — Agent development standards (framework, sandbox, naming, composition, system prompts)
- [agentme-edr-040](040-ai-llm-development-standards.md) — LLM development standards (LangChain configuration, mocking patterns)
- [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) — Hexagonal architecture (tool placement in adapters/connectors)
- [agentme-edr-007](../governance/007-project-quality-standards.md) — Project quality standards including AI-tier testing requirements (rule `09-ai-project-testing-requirements`)
- [agentme-edr-051](051-ai-eval-core-standards.md) — AI eval core standards: eval folder structure (rule `01`) and LLM-as-judge binary scoring contract (rule `02`)
- [agentme-edr-053](053-ai-eval-script.md) — AI eval script: entry-first loop, `--type` filtering, `mock_fixtures`, and MLflow conventions
- [agentme-edr-054](054-ai-eval-report-format.md) — AI eval report format: `report-<type>.md` template, Wilson CI, and convergence analysis
