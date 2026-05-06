# AGENTS.md

**Purpose:** This file is intentionally brief. All project decisions and working instructions are captured as XDRs.

## XDR Consultation Is Mandatory For Every Request

Before answering **any** request — including simple Q&A, informational questions, and design questions — you MUST:

1. Read the XDR root index (default: [.xdrs/index.md](.xdrs/index.md)) to identify relevant XDRs.
2. Read the relevant XDR files.
3. Base your actions on those XDRs.

This rule has NO exceptions. Simple questions ("which command?", "what pattern?", "how does X work?") still require XDR lookup first. Do not answer from general knowledge alone when an XDR may exist on the topic.

## Steps

1. Consult XDRs **for every request**
   - You MUST search and follow Decision Records (XDRs) for architecture, engineering and business in the XDR root index (default: [.xdrs/index.md](.xdrs/index.md)) during Informational, Q&A questions, design, plan, implementation, test and review steps etc. This is the source of truth for this agent.

2. **Verify all work with build, tests and linting before completion**
   - Always run build, lint-fix and test at the end of the implementation when changing code
   - Fix any issues

3. **Verify if implementation complies with XDRs**
   - Analyse your work against the XDRs and ensure implementation decisions follow guidelines and patterns
   - Fix any issues

4. **Document decisions as XDRs when appropriate**
   - Check if what is being performed shouldn't be documented as an XDR in _local scope (because the decision has potential to be reused in the future or the topic is complex and would benefit from a document for clarity). Create or update existing documents accordingly.

5. **Do not perform git operations unless explicitelly asked**
   - The developer should be in control of possible destructive operations on the workspace

**This AGENTS.md file was created with xdrs-core and shouldn't be changed**
