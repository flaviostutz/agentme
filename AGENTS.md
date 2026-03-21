# AGENTS.md

**Purpose:** This file is intentionally brief. All project decisions and working instructions are captured as XDRs.

1. **Always consult XDRs before making decisions**
   - You MUST search and follow Decision Records (XDRs) for architecture, engineering and business in [.xdrs/index.md](.xdrs/index.md) during design, plan, implementation, test and review steps. This is the source of truth.

2. **Verify all work with build, tests and linting before completion**
   - Always run build, lint-fix and test at the end of the implementation
   - Fix any issues

3. **Verify if implementation complies with XDRs**
   - Analyse your work against the XDRs and ensure implementation decisions follow guidelines and patterns
   - Fix any issues

4. **Document decisions as XDRs when appropriate**
   - Check if what is being performed shouldn't be documented as an XDR in _local scope (because the decision has potential to be reused in the future or the topic is complex and would benefit from a document for clarity). Create or update existing documents accordingly.

5. **Do not perform git operations unless explicitelly asked**
   - The developer should be in control of possible destructive operations on the workspace

Check for additional instructions on [AGENTS.local.md](AGENTS.local.md).

**This AGENTS.md file was created with xdrs-core and shouldn't be changed**
