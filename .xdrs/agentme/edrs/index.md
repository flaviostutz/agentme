# agentme EDRs Index

Engineering decisions specific to the agentme project: a curated library of XDRs and skills encoding best practices for AI coding agents.

Propose changes via pull request. All changes must be verified for clarity and non-conflict before merging.

## Related scope indexes

- [_core EDRs Index](../../_core/edrs/index.md) - Cross-business general standards (overridden by this scope where conflicts are documented)

XDRs in scopes listed last override the ones listed first.

## Principles

Foundational standards, principles, and guidelines.

- [agentme-edr-002](principles/002-coding-best-practices.md) - **Coding best practices**
- [agentme-edr-004](principles/004-unit-test-requirements.md) - **Unit test requirements**
- [agentme-edr-007](principles/007-project-quality-standards.md) - **Project quality standards**
- [agentme-edr-009](principles/009-error-handling.md) - **Error handling**

## Application

Language and framework-specific tooling and project structure.

- [agentme-edr-003](application/003-javascript-project-tooling.md) - **JavaScript project tooling and structure** *(includes skill: [001-create-javascript-project](application/skills/001-create-javascript-project/SKILL.md))*
- [agentme-edr-010](application/010-golang-project-tooling.md) - **Go project tooling and structure** *(includes skill: [003-create-golang-project](application/skills/003-create-golang-project/SKILL.md))*

## Devops

Repository structure, build conventions, and CI/CD pipelines.

- [agentme-edr-005](devops/005-monorepo-structure.md) - **Monorepo structure** *(includes skill: [002-monorepo-setup](devops/skills/002-monorepo-setup/SKILL.md))*
- [agentme-edr-006](devops/006-github-pipelines.md) - **GitHub CI/CD pipelines**
- [agentme-edr-008](devops/008-common-targets.md) - **Common development script names**

## Observability

Health, metrics, logging, and monitoring standards.

- [agentme-edr-011](observability/011-service-health-check-endpoint.md) - **Service health check endpoint**
