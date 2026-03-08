# _general-edr-001: AI coding agent behavior

## Context and Problem Statement

AI coding agents (such as GitHub Copilot) require clear guidelines about expected behavior to ensure consistency, proper verification of work, and respect for developer workflows.

What behavioral standards should AI coding agents follow when working on code?

## Decision Outcome

**AI agents must follow a defined instruction hierarchy, verify work with automated checks, and defer git operations to developers**

Clear behavior standards ensure consistency through EDR compliance, maintain code quality through automated verification, and respect the developer's role in version control decisions.

### Implementation Details

**Mandatory behaviors for AI coding agents:**

1. **Follow instruction hierarchy when making implementation decisions**
   1. **Closest AGENTS.md** to the file being changed (search from target directory up to workspace root). Instructions in those files override the global EDRs. If multiple AGENTS.md files exist in the path, merge their instructions; the closest AGENTS.md overrides those farther away.
   2. **Global EDR** – Follow scope-based precedence defined in [.xdrs/index.md](../../../../index.md). EDRs in scopes listed last override EDRs in scopes listed first.

2. **Verify all work with build, tests and linting before completion**
   - Check EDRs for workspace tooling: [.xdrs/index.md](../../../../index.md)
   - Run quality checks in sequence relative to the module directory: `STAGE=dev make build-module`, `make lint-module`, then `make test-module`
   - Use `make lint-fix` to fix lint issues
   - Do not run commands outside Makefiles

3. **Verify implementation complies with EDRs**
   - Review relevant EDRs before marking work complete
   - Ensure implementation decisions follow EDR guidelines and patterns

4. **Do not perform git operations**
   - Do not run git commands (add, commit, push, branch creation, etc.)
   - Inform the developer when work is ready for version control

## Considered Options

* (REJECTED) **Minimal guidance** - Let agents operate with default behavior
  * Reason: Results in inconsistent code quality, missed verification steps, and developers losing control of git workflow
* (CHOSEN) **EDR-compliant agents** - Clear behavior standards
  * Reason: Ensures consistency through EDR compliance, maintains code quality through verification, and respects developer control of version control
