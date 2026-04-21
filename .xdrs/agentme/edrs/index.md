# agentme EDRs Index

Engineering decisions specific to the agentme project: a curated library of XDRs and skills encoding best practices for AI coding agents.

Propose changes via pull request. All changes must be verified for clarity and non-conflict before merging.

## Principles

Foundational standards, principles, and guidelines.

- [agentme-edr-002](principles/002-coding-best-practices.md) - **Coding best practices** - Keep files small, tests nearby, and docs synchronized
- [agentme-edr-004](principles/004-unit-test-requirements.md) - **Unit test requirements** - Define minimum unit-test coverage and naming expectations
- [agentme-edr-007](principles/007-project-quality-standards.md) - **Project quality standards** - Require build, lint, and test verification before completion
- [agentme-edr-009](principles/009-error-handling.md) - **Error handling** - Standardize explicit errors, logging, and propagation rules
- [agentme-edr-012](principles/012-continuous-xdr-enrichment.md) - **Continuous xdr improvement policy** - Promote recurring delivery lessons into reusable XDRs
- [agentme-edr-016](principles/016-cross-language-module-structure.md) - **Cross-language module structure** - Organize modules consistently across supported languages

## Articles

Synthetic views combining agentme XDRs and skills around a specific topic.

- [agentme-article-001](principles/articles/001-continuous-xdr-improvement.md) - **Continuous XDR improvement** (what an XDR is, when to write one, how to discuss it, how to organize it, workflow)

## Application

Language and framework-specific tooling and project structure.

- [agentme-edr-003](application/003-javascript-project-tooling.md) - **JavaScript project tooling and structure** - Scaffold JavaScript libraries with the standard toolchain *(includes skill: [001-create-javascript-project](application/skills/001-create-javascript-project/SKILL.md))*
- [agentme-edr-010](application/010-golang-project-tooling.md) - **Go project tooling and structure** - Scaffold Go CLIs and libraries with the standard layout *(includes skill: [003-create-golang-project](application/skills/003-create-golang-project/SKILL.md))*
- [agentme-edr-014](application/014-python-project-tooling.md) - **Python project tooling and structure** - Scaffold Python packages and CLIs with the standard layout *(includes skill: [005-create-python-project](application/skills/005-create-python-project/SKILL.md))*
- [agentme-edr-015](application/015-cli-tool-standards.md) - **CLI tool standards** - Define command UX and behavior for CLI tools
- [004-select-relevant-xdrs](application/skills/004-select-relevant-xdrs/SKILL.md) - **Select relevant XDRs**

## Devops

Repository structure, build conventions, and CI/CD pipelines.

- [agentme-edr-005](devops/005-monorepo-structure.md) - **Monorepo structure** - Standardize monorepo layout, tooling, and package boundaries *(includes skill: [002-monorepo-setup](devops/skills/002-monorepo-setup/SKILL.md))*
- [agentme-edr-006](devops/006-github-pipelines.md) - **GitHub CI/CD pipelines** - Define required CI stages and workflow structure
- [agentme-edr-008](devops/008-common-targets.md) - **Common development script names** - Reuse standard build, lint, and test target names
- [agentme-edr-017](devops/017-tool-execution-and-scripting.md) - **Tool execution and scripting** - Run tools consistently across shells, Makefiles, and CI

## Governance

Contribution and collaboration standards shared across projects.

- [agentme-edr-013](governance/013-contributing-guide-requirements.md) - **Contributing guide requirements** - Define the minimum structure for CONTRIBUTING guides

## Observability

Health, metrics, logging, and monitoring standards.

- [agentme-edr-011](observability/011-service-health-check-endpoint.md) - **Service health check endpoint** - Expose a standard runtime health-check endpoint for services
