---
name: agentme-edr-policy-019-ai-agents-development-standards
description: Defines the standard framework and patterns for building AI agents with tool-invocation loops using the deepagents framework. Use when building agents where the LLM autonomously decides which tools to call and when to stop. For simple LLM calls see agentme-edr-018, for workflow orchestration see agentme-edr-020.
apply-to: AI agent projects that use tool-invocation loops where the LLM decides which tools to call and when to stop
valid-from: 2026-06-05
---

# agentme-edr-policy-019: AI agents development standards

## Context and Problem Statement

AI applications often need to give LLMs the ability to autonomously choose and invoke tools to accomplish tasks. Without standardized patterns for agent implementation, projects end up with incompatible approaches to tool definition, state management, and runtime environments.

Which framework should be used for building agents with tool-invocation loops, and what are the essential patterns for agent state, tools, and execution environments?

## Decision Outcome

**Use the deepagents framework for all agent implementations where an LLM autonomously decides which tools to call and when to stop.**

This policy covers the **Agent** tier only. For simple LLM calls, see [agentme-edr-018](018-ai-llm-development-standards.md). For workflow orchestration that contains agents as nodes, see [agentme-edr-020](020-ai-workflow-development-standards.md).

### Conceptual model

An **Agent** is an LLM-based flow driven by a tool-invocation loop that the LLM itself plans and executes. The LLM decides which tools to call and when to stop. The agent follows a perceive → plan → act → observe cycle autonomously until it reaches a terminal state.

Agents differ from simple LLM calls (no tools) and workflows (predefined graph topology):

| Tier | What it is | Library |
|---|---|---|
| **LLM** | A request → response prompt exchange. No autonomous decision-making. | `langchain` / `langchain-openai` |
| **Agent** | An LLM-based flow with a tool-invocation loop. The LLM decides which tools to call. | `deepagents` |
| **Workflow** | A directed graph of nodes. The graph topology is defined in code, not chosen by the LLM. | `langgraph` |

### Details

#### 01-agent-framework

All agent implementations MUST use the **deepagents** framework.

- Use deepagents whenever the LLM needs to autonomously select and invoke tools to accomplish a task.
- The agent MUST follow the perceive → plan → act → observe cycle where the LLM observes tool outputs and decides the next action.
- All LLM calls within agents MUST follow [agentme-edr-018](018-ai-llm-development-standards.md) for LangChain configuration and observability.

**When to use agents vs workflows:**

- Use an **agent** when the LLM should autonomously decide the sequence of tool calls based on runtime observations.
- Use a **workflow** when the execution path is predefined in code, even if individual nodes involve LLM calls or agent subgraphs.
- When in doubt, prefer workflows (explicit control flow) over agents (autonomous control flow) for maintainability and predictability.

#### 02-local-sandbox

When an agent requires a **local sandbox** — an isolated environment where the agent can read files, glob-search directories, and execute shell commands — use the **[deepagents](https://github.com/deepagents/deepagents) framework** to provide that sandbox.

**When to apply this rule:**

Use deepagents sandbox whenever ANY of the following is true:
- The agent needs to execute shell commands or scripts in a controlled environment.
- The agent needs to list, read, or search files across multiple directories at runtime.
- The agent operates on user-supplied or generated file trees that must not escape a sandboxed boundary.

**Integration requirements:**

- Initialize the sandbox at the start of the agent run and shut it down in the same `try/finally` block.
- Pass the sandbox handle into the agent's state so all tool calls share the same sandbox instance.
- If the host-side code needs to pass files into the sandbox (e.g. generated config or input data), create a temporary directory with `tempfile.mkdtemp()`, write the files there, and mount it into the sandbox. Clean it up in the `finally` block.
- Replace hand-rolled `read_file`, `search_files`, and `grep_file` tool implementations with the equivalent tools provided by deepagents.

**Example:**

```python
import tempfile
from deepagents import Sandbox

def run_file_analysis_agent(input_files: List[Path]) -> AnalysisResult:
    tmp_dir = tempfile.mkdtemp()
    try:
        # Copy input files to temp directory
        for f in input_files:
            shutil.copy(f, tmp_dir)
        
        # Initialize sandbox with mounted directory
        sandbox = Sandbox(mount_paths={tmp_dir: "/workspace"})
        
        # Run agent with sandbox
        agent = FileAnalysisAgent(sandbox=sandbox)
        result = agent.run()
        
        return result
    finally:
        sandbox.shutdown()
        shutil.rmtree(tmp_dir)
```

#### 03-agent-state-management

Agents MUST maintain explicit state that tracks:
- The current task or goal
- Tool invocation history (what tools were called, with what arguments, and what they returned)
- Agent reasoning or plan (if applicable)
- Terminal conditions (success, failure, or maximum iterations reached)

**State type naming:**

- Agent state types MUST end with `_agent_state` suffix (e.g., `file_analyzer_agent_state`)
- Follow [agentme-edr-020](020-ai-workflow-development-standards.md) rule `11-state-type-conventions` when agents are used as workflow nodes

**State persistence:**

- Agents SHOULD expose methods to serialize and restore state for debugging and checkpointing
- Long-running agents MUST implement state checkpointing to enable recovery from failures

#### 04-tool-definition-patterns

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

#### 05-agent-error-handling-and-recovery

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

#### 06-agent-naming-conventions

Agent class names MUST follow the pattern `<Purpose>Agent` where `<Purpose>` describes what the agent does:

**Good names:**
- `FileAnalyzerAgent` — analyzes files
- `CodeReviewerAgent` — reviews code
- `DataExtractorAgent` — extracts data from documents

**Bad names (FORBIDDEN):**
- `Agent` (too generic)
- `MainAgent` (not descriptive)
- `MyAgent` (not descriptive)
- `Agent1` (numbered, not semantic)

When agents are used as nodes in workflows, the node name MUST use the `_agent` suffix per [agentme-edr-020](020-ai-workflow-development-standards.md) rule `09-node-naming-conventions`.

### Testing Requirements

For agent-tier projects:

- **Unit tests**: MAY be used but are NOT required
- **Evaluation tests**: MAY be used but are NOT required
- **Integration tests**: MAY be used but are NOT required

When tests are implemented, follow [agentme-edr-018](018-ai-llm-development-standards.md) for LLM mocking patterns and [agentme-edr-020](020-ai-workflow-development-standards.md) for testing strategy.

## References

- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards (LangChain configuration, mocking patterns)
- [agentme-edr-020](020-ai-workflow-development-standards.md) — Workflow development standards (using agents as workflow nodes)
- [agentme-edr-026](026-pragmatic-hexagonal-architecture.md) — Hexagonal architecture (tool placement in adapters/connectors)
- [agentme-edr-014](014-python-project-tooling.md) — Python project tooling and structure
