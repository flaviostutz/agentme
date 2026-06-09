---
name: agentme-edr-policy-025-ai-agent-xdrs-knowledge-layer
description: Defines how to integrate XDRS as the runtime knowledge source of truth for AI agents — covering document placement, AGENTS.md setup, file tools, and local sandbox configuration. Apply only when the project explicitly uses XDRS to govern agent behavior.
apply-to: AI agent projects that use XDRS as the source of truth for policies and skills
valid-from: 2026-05-27
---

# agentme-edr-policy-025: AI agent XDRS knowledge layer

## Context and Problem Statement

AI agents need access to project-specific policies and skills at runtime to produce consistent, governed outputs. XDRS provides a file-system-based structure for capturing these decisions, but there is no standard pattern for embedding XDRS documents in agent libraries, wiring the agent to consult them, or sandboxing file access securely.

How should an AI agent project integrate XDRS as its runtime source of truth for policies and skills?

## Decision Outcome

**Embed XDRS documents in `lib/data/.xdrs/`, instruct the agent to consult them via `AGENTS.md`, equip the agent with sandboxed file tools, and use the deepagents framework when a local sandbox is required.**

This policy MUST only be applied when the project explicitly chooses XDRS as its knowledge governance layer. It is not required by [agentme-edr-019](019-ai-agents-development-standards.md) or [agentme-edr-021](021-ai-workflow-development-standards.md) in general.

### Details

#### 01-xdrs-knowledge-layer

XDRS documents are the source of truth for all policies and skills that the agent must follow during its tasks. The agent MUST consult XDRS before acting, not rely on general knowledge alone.

**Placing XDRS documents in the library**

- XDRS Policy and Skill documents MUST be placed at `lib/data/.xdrs/`, using the standard XDRS scope/type/subject folder structure (following `_core-adr-policy-001`).
- They MUST be embedded in the package data manifest (e.g. `pyproject.toml` `[tool.hatch.build] include` or equivalent) so they are available at runtime.
- When exposed through a deepagents sandbox, they MUST be mounted at `/.xdrs/` inside the sandbox (see rule `03-local-sandbox`).

**AGENTS.md — mandatory XDRS consultation**

Place an `AGENTS.md` file at the root of the deepagents sandbox (i.e. alongside `/.xdrs/`). This file instructs the agent to always consult XDRS before acting. Its content MUST follow the xdrs-core AGENTS.md template:

```markdown
# AGENTS.md

**Purpose:** This file is intentionally brief. All decisions and working instructions are captured as Policies or Skills in the XDRS structure.

## Policy Consultation in XDRS Is Mandatory For Every Request

Before answering **any** request you MUST:

1. Read the XDRS root index at `/.xdrs/index.md` to identify relevant Policies and Skills.
2. Read the relevant Policy and Skill files.
3. Base your actions on those Policies and Skills.

This rule has NO exceptions. Do not answer from general knowledge alone when a Policy may exist on the topic.
```

The agent system prompt MUST reference `AGENTS.md` so the agent loads it at startup. Example:

```
Read /AGENTS.md and follow all instructions in it before proceeding.
```

#### 02-agent-file-tools

Every agent that uses the XDRS knowledge layer MUST use the file tools provided by the deepagents framework. Do not implement hand-rolled alternatives — see [agentme-edr-019 rule 02-local-sandbox](019-ai-agents-development-standards.md) for the full sandbox and tool requirements.

These tools operate over two sandboxed roots (configured in rule `03-local-sandbox`):

| Root | Content | Source |
|---|---|---|
| `data_root` | Static files shipped with the library (`lib/data/`) | Resolved via `importlib.resources` at workflow startup |
| `temp_root` | Dynamic files generated for the current workflow run | Temporary directory created by `tempfile.mkdtemp()` at workflow startup |

`temp_root` MUST be created at workflow startup and cleaned up in the same `try/finally` block. Pass it explicitly into the workflow; do not read it from a global variable.

#### 03-local-sandbox

Follow [agentme-edr-019 rule 02-local-sandbox](019-ai-agents-development-standards.md) for the general deepagents sandbox setup. When XDRS is in use, add the following mounts to the sandbox configuration:

| Source | Content | Deepagents sandbox path |
|---|---|---|
| `lib/data/.xdrs/` | XDRS Policy and Skill documents | `/.xdrs/` (read-only) |
| Generated at startup | `AGENTS.md` instructing the agent to consult XDRS | `/AGENTS.md` (read-only) |

XDRS documents MUST always be mounted at `/.xdrs/`. `AGENTS.md` MUST always be placed at the sandbox root (`/AGENTS.md`).

Example XDRS mount additions:

```python
from importlib.resources import files
from pathlib import Path

data_root = str(files("myagent").joinpath("data"))
agents_md = Path(temp_root) / "AGENTS.md"
agents_md.write_text(_AGENTS_MD)  # content from xdrs-core AGENTS.md template; see rule 01-xdrs-knowledge-layer

# Add these mounts alongside the base mounts from agentme-edr-019 rule 02-local-sandbox:
# (mount_paths uses {src: dst} dict format per agentme-edr-019)
sandbox = Sandbox(
    mount_paths={
        tmp_dir: "/workspace",
        f"{data_root}/.xdrs": "/.xdrs",
        str(agents_md): "/AGENTS.md",
    },
    virtual_mode=True,
)
```
