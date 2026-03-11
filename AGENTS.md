# AGENTS.md

**Purpose:** This file is intentionally brief. All project decisions and working instructions are captured as XDRs.

1. **Always consult XDRs before making implementation decisions**
   - You MUST follow coding agent behavior and decision hierarchy rules in [.xdrs/_core/edrs/principles/001-coding-agent-behavior.md](.xdrs/_core/edrs/principles/001-coding-agent-behavior.md)
   - You MUST search and follow XDRs in [.xdrs/index.md](.xdrs/index.md) during design, plan, implementation, test and review steps
   - You MUST follow XDRs as the source of truth for all decisions and procedures

2. **Verify all work with build, tests and linting before completion**
   - Always run `make build`, `make lint-fix` and `make test` at the end of the implementation
   - Fix any issues

3. **Verify if implementation complies with XDRs**
   - Re-analyse your work against the XDRs and ensure implementation decisions follow guidelines and patterns

4. **Do not perform git operations**
   - Do not run git commands (add, commit, push, branch creation, etc.)

