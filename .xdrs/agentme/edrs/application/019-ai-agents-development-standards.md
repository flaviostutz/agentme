---
name: agentme-edr-policy-019-ai-agents-development-standards
description: Defines the structural patterns and design decisions for building AI agents with tool-invocation loops using the deepagents framework: framework selection, sandbox setup, state naming, agent naming, composition patterns, and system prompt structure. Use when designing or scaffolding a new agent. For tool definitions, error handling, observability, and testing see agentme-edr-020. For simple LLM calls see agentme-edr-018, for workflow orchestration see agentme-edr-021.
apply-to: AI agent projects — consult when designing agent structure, choosing sandbox approach, defining naming conventions, and composing multi-agent systems
valid-from: 2026-06-05
---

# agentme-edr-policy-019: AI agents development standards

## Context and Problem Statement

AI applications often need to give LLMs the ability to autonomously choose and invoke tools to accomplish tasks. Without standardized structural patterns for agent design, projects end up with incompatible approaches to framework selection, sandbox setup, state management, naming, composition, and system prompts.

Which framework should be used for building agents, how should agents be sandboxed, named, composed, and how should their system prompts be structured?

## Decision Outcome

**Use the deepagents framework for all agent implementations where an LLM autonomously decides which tools to call and when to stop.**

### Conceptual model

An **Agent** is an LLM-based flow driven by a tool-invocation loop that the LLM itself plans and executes. The LLM decides which tools to call and when to stop. The agent follows a perceive → plan → act → observe cycle autonomously until it reaches a terminal state.

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

- The sandbox MUST always be initialized with `virtual_mode=True` to prevent the agent from reading or writing files outside the mounted workspace. Omitting this flag allows the agent unrestricted host filesystem access, which is a security violation.
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
        sandbox = Sandbox(mount_paths={tmp_dir: "/workspace"}, virtual_mode=True)
        
        # Run agent with sandbox
        agent = FileAnalysisAgent(sandbox=sandbox)
        result = agent.run()
        
        return result
    finally:
        sandbox.shutdown()
        shutil.rmtree(tmp_dir)
```

#### 03-agent-state-management

**State type naming:**

- Agent state types MUST end with `_agent_state` suffix (e.g., `file_analyzer_agent_state`)
- Follow [agentme-edr-021](021-ai-workflow-development-standards.md) rule `11-state-type-conventions` when agents are used as workflow nodes

#### 04-agent-naming-conventions

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

When agents are used as nodes in workflows, the node name MUST use the `_agent` suffix per [agentme-edr-021](021-ai-workflow-development-standards.md) rule `09-node-naming-conventions`.

#### 05-agent-composition

When multiple agents are needed:

- **Single agent with multiple tools:** Use when tools share a common goal and context (e.g., a code analysis agent with `read_file`, `search_code`, and `analyze_pattern` tools).
- **Multiple agents as workflow nodes:** Use when agents have distinct responsibilities and outputs that feed into each other. Orchestrate them using LangGraph per [agentme-edr-021](021-ai-workflow-development-standards.md).
- Do NOT create nested agent loops (agent calling agent autonomously). Use workflows for multi-agent orchestration.

**Decision criteria:**

| Pattern | When to use |
|---|---|
| Single agent + tools | All tools serve the same goal; agent completes in one session |
| Multiple workflow-orchestrated agents | Each agent has a distinct goal; outputs flow between agents; deterministic sequencing needed |
| Nested agents (FORBIDDEN) | Never — always use workflow orchestration instead |

#### 06-agent-system-prompt-structure

Every agent system prompt MUST follow this XML-section template. Sections must appear in this order. Required sections must always be present; optional sections may be omitted when they genuinely do not apply; never reorder them.

```xml
<OBJECTIVE>
[A one or two-sentence summary of the agent's main deliverable.
e.g.: Split the incoming file list into logical batches for parallel processing.]
</OBJECTIVE>

<ROLE>
[Defines who the agent is, its area of expertise, and its core persona.
If running inside a workflow, define exactly which node in WORKFLOW_CONTEXT this agent corresponds to.
e.g.: You are the batch_planning_agent (see WORKFLOW_CONTEXT). You are an expert at partitioning large file sets into balanced, directory-aware batches.]
</ROLE>

<INPUT>
[All inputs for this agent invocation. For standalone agents: list only the agent-specific inputs. For workflow agents: list workflow-level inputs shared across all agents first, then agent-specific inputs such as judge outcomes, counters, or intermediate results from upstream nodes.]
</INPUT>

<!-- Optional: include when the agent follows a non-trivial sequence of steps -->
<STEPS>
[Numbered list or chronological steps detailing how the agent should process an incoming request.
e.g.:
1. Analyse the file list and group files by directory.
2. Assign files to batches respecting the size constraints.
3. Emit the JSON output described in OUTPUT_FORMAT.]
</STEPS>

<!-- Optional: include when tool use needs explicit guidance -->
<TOOL_GUIDANCE>
[Explicit instructions on when and how to use external tools, preventing the agent from guessing or using the wrong sequence.
e.g.: Do not call any tools. All reasoning is done in-context using the INPUT fields only.]
</TOOL_GUIDANCE>

<!-- Optional: include when hard constraints need to be stated explicitly -->
<GUARDRAILS>
[Hard, non-negotiable constraints the agent must never violate.
e.g.: NEVER create batches with fewer than 5 or more than 20 files. NEVER split files from the same directory across different batches unless unavoidable.]
</GUARDRAILS>

<OUTPUT_FORMAT>
[A templated example or JSON schema specifying exactly how the final response should look.
e.g.: Respond with a JSON object matching this schema: ...]
</OUTPUT_FORMAT>

<!-- Workflow-only: omit this section for standalone (non-workflow) agents -->
<WORKFLOW_CONTEXT>
[A detailed prose or diagram description of the overall workflow graph so the agent understands its role within the larger flow. Reference the specific node name that maps to this agent. Include enough detail about upstream and downstream nodes so the agent can reason about its context.]
</WORKFLOW_CONTEXT>
```

**Rules:**

| Section | Required? | Notes |
|---|---|---|
| `<OBJECTIVE>` | Required | One or two sentences summarising the agent's main deliverable. |
| `<ROLE>` | Required | Agent persona and expertise. When inside a workflow, MUST reference its node name from `<WORKFLOW_CONTEXT>`. |
| `<INPUT>` | Required | List ALL inputs. For workflow agents: workflow-level inputs first, then agent-specific inputs. |
| `<STEPS>` | Optional | Include when the agent follows a non-trivial numbered sequence of steps. |
| `<TOOL_GUIDANCE>` | Optional | Include when tool use order or conditions need explicit direction. |
| `<GUARDRAILS>` | Optional | Hard constraints that must never be violated. |
| `<OUTPUT_FORMAT>` | Required | MUST include a concrete schema or templated example; do not leave it vague. |
| `<WORKFLOW_CONTEXT>` | Conditional | MUST be omitted for standalone agents. MUST be present when the agent runs as a node inside a LangGraph workflow. |

## References

- [agentme-edr-018](018-ai-llm-development-standards.md) — LLM development standards (LangChain configuration, mocking patterns)
- [agentme-edr-021](021-ai-workflow-development-standards.md) — Workflow development standards (using agents as workflow nodes)
- [agentme-edr-020](020-ai-agents-quality-standards.md) — Agent implementation quality standards (tool definitions, error handling, observability, unit testing)
- [agentme-edr-014](014-python-project-tooling.md) — Python project tooling and structure
