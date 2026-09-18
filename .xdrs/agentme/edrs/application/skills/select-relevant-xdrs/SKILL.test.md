---
skill: select-relevant-xdrs
skill-version: "1.0"
---

## Test Scenarios

### Scenario 1: Install presets for a single-package Node.js library, happy path

**Trigger / Input**

"Install the right agentme XDR presets for this Node.js library." The repository is a single npm
package with a Makefile and no Go code, no monorepo layout, and no deployed/long-running service.

**Expected Behaviour**

1. Phase 1 inventories the shipped agentme XDR files.
2. Phase 2 analyzes the repository and detects a JavaScript/TypeScript single-package library with
   Makefiles, no Go tooling, no monorepo structure, and no service surface.
3. Phase 3 selects exclusions with one-line rationale each — at minimum the Go project tooling XDR
   and the service health-check XDR — while keeping baseline/broadly applicable guidance.
4. Phase 4 runs `npx -y agentme extract --output . --all --exclude <path> --exclude <path>` with
   one `--exclude` flag per excluded XDR, then verifies `.xdrs/index.md`, `.xdrs/agentme/`, and
   `AGENTS.md` exist and that every excluded path is absent from the output.

**Assertions**

- [ ] Output excludes `.xdrs/agentme/edrs/application/102-golang-project-tooling.md` and
      `.xdrs/agentme/edrs/operations/401-service-health-check-endpoint.md` with a one-line
      rationale for each.
- [ ] Output runs `agentme extract` with `--all` plus one `--exclude` flag per excluded XDR path,
      rather than a hand-picked include list.
- [ ] Output verifies after extraction that `.xdrs/index.md`, `.xdrs/agentme/`, and `AGENTS.md`
      exist and that the excluded paths are absent from the result.

### Scenario 2: Extraction blocked when the package exposes no inventory metadata

**Trigger / Input**

Run the skill in an environment where the CLI cannot enumerate the shipped XDRs, and the package
metadata and repository documentation also do not describe the shipped XDR set.

**Expected Behaviour**

Per Phase 1 step 4, since even the fallback inventory sources fail, the skill stops before
attempting any extraction and reports that automatic selection is blocked because the package does
not expose enough metadata in the current environment, rather than guessing an exclude list or
forcing a full installation.

**Assertions**

- [ ] Output stops before running any `agentme extract` command.
- [ ] Output reports that automatic selection is blocked due to insufficient package metadata,
      rather than silently falling back to a default guess.

### Scenario 3: Debatable exclusion is kept, not excluded

**Trigger / Input**

Analyzing a currently single-package repository whose README states the team is planning to split
it into multiple applications "sometime in the future." Whether the monorepo-structure XDR still
applies is debatable.

**Expected Behaviour**

Per the Edge Cases entry on debatable exclusions, since the mismatch is not concrete today, the
skill keeps the monorepo-structure XDR in the installed set rather than excluding it on the basis
of a possible future restructuring.

**Assertions**

- [ ] Output keeps `.xdrs/agentme/edrs/platform/301-monorepo-structure.md` in the installed set.
- [ ] Output does not add it to the exclude list on the basis of a future, not-yet-concrete plan.
