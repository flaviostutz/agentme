# AGENTS.md

**Purpose:** This file is intentionally brief. All project decisions and working instructions are captured as Policies or Skills in the XDRS structure.

## Policy Consultation in XDRS Is Mandatory For Every Request

Before answering **any** request — including simple Q&A, informational questions, and design questions — you MUST:

1. Read the XDRS root index (default: [.xdrs/index.md](.xdrs/index.md)) to identify relevant Policies.
2. Read the relevant Policy files.
3. Base your actions on those Policies.

This rule has NO exceptions. Simple questions ("which command?", "what pattern?", "how does X work?") still require Policy lookup first. Do not answer from general knowledge alone when a Policy may exist on the topic.

## Steps

1. Consult Policies in XDRS **for every request**
   - You MUST search and follow Policies for architecture, engineering and business in the Policy root index (default: [.xdrs/index.md](.xdrs/index.md)) during Informational, Q&A questions, design, plan, implementation, test and review steps etc. This is the source of truth for this agent.

2. **Verify all work with build, tests and linting before completion**
   - Always run build, lint-fix and test at the end of the implementation when changing code
   - Fix any issues

3. **Verify if implementation complies with Policies from XDRS**
   - Analyse your work against the Policies and ensure implementation decisions follow guidelines and patterns
   - Fix any issues

4. **Do not perform risky git operations unless explicitelly asked**
   - The developer should be in control of possible destructive operations on the workspace

**This AGENTS.md file was created with xdrs-core and shouldn't be changed**
