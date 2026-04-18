# agentme EDRs Index

Engineering decisions specific to the agentme project: a curated library of XDRs and skills encoding best practices for AI coding agents.

Propose changes via pull request. All changes must be verified for clarity and non-conflict before merging.

## Principles

Foundational standards, principles, and guidelines.

- [agentme-edr-002](principles/002-coding-best-practices.md) - **Coding best practices**
- [agentme-edr-004](principles/004-unit-test-requirements.md) - **Unit test requirements**
- [agentme-edr-007](principles/007-project-quality-standards.md) - **Project quality standards**
- [agentme-edr-009](principles/009-error-handling.md) - **Error handling**
- [agentme-edr-012](principles/012-continuous-xdr-enrichment.md) - **Continuous xdr improvement policy**

## Articles

Synthetic views combining agentme XDRs and skills around a specific topic.

- [agentme-article-001](principles/articles/001-continuous-xdr-improvement.md) - **Continuous XDR improvement** (what an XDR is, when to write one, how to discuss it, how to organize it, workflow)

## Application

Language and framework-specific tooling and project structure.

- [agentme-edr-003](application/003-javascript-project-tooling.md) - **JavaScript project tooling and structure** *(includes skill: [001-create-javascript-project](application/skills/001-create-javascript-project/SKILL.md))*
- [agentme-edr-010](application/010-golang-project-tooling.md) - **Go project tooling and structure** *(includes skill: [003-create-golang-project](application/skills/003-create-golang-project/SKILL.md))*
- [agentme-edr-014](application/014-python-project-tooling.md) - **Python project tooling and structure** *(includes skill: [005-create-python-project](application/skills/005-create-python-project/SKILL.md))*
- [004-select-relevant-xdrs](application/skills/004-select-relevant-xdrs/SKILL.md) - **Select relevant XDRs**

## Devops

Repository structure, build conventions, and CI/CD pipelines.

- [agentme-edr-005](devops/005-monorepo-structure.md) - **Monorepo structure** *(includes skill: [002-monorepo-setup](devops/skills/002-monorepo-setup/SKILL.md))*
- [agentme-edr-006](devops/006-github-pipelines.md) - **GitHub CI/CD pipelines**
- [agentme-edr-008](devops/008-common-targets.md) - **Common development script names**

## Governance

Contribution and collaboration standards shared across projects.

- [agentme-edr-013](governance/013-contributing-guide-requirements.md) - **Contributing guide requirements**

## Observability

Health, metrics, logging, and monitoring standards.

- [agentme-edr-011](observability/011-service-health-check-endpoint.md) - **Service health check endpoint**
