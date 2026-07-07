# agentme EDRs Index

Engineering decisions specific to the agentme project: a curated library of XDRs and skills encoding best practices for AI coding agents.

Propose changes via pull request. All changes must be verified for clarity and non-conflict before merging.

## Principles

Foundational standards, principles, and guidelines.

- [agentme-edr-002](principles/002-coding-best-practices.md) - **Coding best practices** - Keep files small, tests nearby, and docs synchronized
- [agentme-edr-023](principles/023-coding-abstraction-practices.md) - **Coding abstraction practices** - Define when abstractions are justified and when they must be inlined
- [agentme-edr-004](principles/004-unit-test-requirements.md) - **Unit test requirements** - Define minimum unit-test coverage and naming expectations
- [agentme-edr-007](principles/007-project-quality-standards.md) - **Project quality standards** - Require build, lint, and test verification before completion
- [agentme-edr-009](principles/009-error-handling.md) - **Error handling** - Standardize explicit errors, logging, and propagation rules
- [agentme-edr-012](principles/012-continuous-xdr-enrichment.md) - **Continuous xdr improvement policy** - Promote recurring delivery lessons into reusable XDRs
- [agentme-edr-016](principles/016-cross-language-module-structure.md) - **Cross-language module structure** - Organize modules consistently across supported languages
- [agentme-edr-022](principles/022-secrets-management.md) - **Secrets management** - Handle secrets securely using native keychains and cloud secret managers

## Articles

Synthetic views combining agentme XDRs and skills around a specific topic.

- [agentme-article-001](principles/articles/001-continuous-xdr-improvement.md) - **Continuous XDR improvement** (what an XDR is, when to write one, how to discuss it, how to organize it, workflow)

## Application

Language and framework-specific tooling and project structure.

### Language and framework tooling

- [agentme-edr-003](application/003-javascript-project-tooling.md) - **JavaScript project tooling and structure** - Scaffold JavaScript libraries with the standard toolchain *(includes skill: [001-create-javascript-project](application/skills/001-create-javascript-project/SKILL.md))*
- [agentme-edr-010](application/010-golang-project-tooling.md) - **Go project tooling and structure** - Scaffold Go CLIs and libraries with the standard layout *(includes skill: [003-create-golang-project](application/skills/003-create-golang-project/SKILL.md))*
- [agentme-edr-014](application/014-python-project-tooling.md) - **Python project tooling and structure** - Scaffold Python packages and CLIs with the standard layout *(includes skill: [005-create-python-project](application/skills/005-create-python-project/SKILL.md))*
- [agentme-edr-015](application/015-cli-tool-standards.md) - **CLI tool standards** - Define command UX and behavior for CLI tools
- [agentme-edr-026](application/026-pragmatic-hexagonal-architecture.md) - **Pragmatic hexagonal architecture** - Organize application layers as External/Adapters/Application with practical coupling rules
- [004-select-relevant-xdrs](application/skills/004-select-relevant-xdrs/SKILL.md) - **Select relevant XDRs**

### AI development

Standards for building LLM, Agent, and Workflow components.

- [agentme-edr-018](application/018-ai-llm-development-standards.md) - **AI LLM development standards** - Standard framework (LangChain) and patterns for simple LLM calls with explicit configuration (no environment variables)
- [agentme-edr-019](application/019-ai-agents-development-standards.md) - **AI agents development standards** - Structural patterns for agents: framework selection, sandbox setup, naming conventions, composition, and system prompt structure
- [agentme-edr-020](application/020-ai-agents-quality-standards.md) - **AI agents implementation quality standards** - Tool definition patterns, error handling, observability, and unit testing for agents
- [agentme-edr-021](application/021-ai-workflow-development-standards.md) - **AI workflow development standards** - Standard toolchain (LangGraph), evaluation, and testing patterns for workflow projects
- [agentme-edr-029](application/029-ai-workflow-naming-conventions.md) - **AI workflow naming conventions** - Node suffix/prefix roles, state type and attribute naming, judge output schema, workflow class names, and cross-element coherence rules
- [agentme-edr-025](application/025-ai-agent-xdrs-knowledge-layer.md) - **AI agent XDRS knowledge layer** - How to integrate XDRS as the runtime source of truth for policies and skills in AI agents (apply only when the project explicitly uses XDRS)

### AI evaluation and testing

Standards for eval datasets, scripts, reports, and test type taxonomy.

- [agentme-edr-030](application/030-ai-test-types-taxonomy.md) - **AI test types taxonomy** - Names AI test types (`functional`, `safety`, `smoke`, `repeatability`, `adversarial`, `fairness`, and 6 others) with group, objective, mocking constraint, and relevance, and defines the shared golden dataset entry envelope
- [agentme-edr-028](application/028-ai-eval-core-standards.md) - **AI eval core standards** - Eval folder structure and Makefile interface; LLM-as-judge binary scoring contract applicable to all AI tiers and test types
- [agentme-edr-031](application/031-ai-eval-script.md) - **AI eval script** - eval.py requirements: entry-first loop, --type filtering, mock_fixtures wiring, human entries, threshold enforcement, and MLflow experiment conventions
- [agentme-edr-032](application/032-ai-eval-report-format.md) - **AI eval report format** - report-<type>.md template, Wilson score confidence interval, convergence analysis, and human-type checklist artifact
- [agentme-edr-033](application/033-ai-eval-repeatability.md) - **AI eval repeatability** - Repeatability test type: REPEAT_COUNT loop exception, semantic-similarity and LLM-as-judge scoring, repeatability_accuracy metric, report shape, and run cadence
- [agentme-edr-024](application/024-ml-dataset-structure.md) - **ML dataset structure** - Standard folder layout and file conventions for ML datasets

## Devops

Repository structure, build conventions, and CI/CD pipelines.

- [agentme-edr-005](devops/005-monorepo-structure.md) - **Monorepo structure** - Standardize monorepo layout, tooling, and package boundaries *(includes skill: [002-monorepo-setup](devops/skills/002-monorepo-setup/SKILL.md))*
- [agentme-edr-006](devops/006-github-pipelines.md) - **GitHub CI/CD pipelines** - Define required CI stages and workflow structure
- [agentme-edr-008](devops/008-common-targets.md) - **Common development script names** - Reuse standard build, lint, and test target names
- [agentme-edr-017](devops/017-tool-execution-and-scripting.md) - **Tool execution and scripting** - Run tools consistently across shells, Makefiles, and CI
- [agentme-edr-027](devops/027-environment-variable-configuration.md) - **Environment variable configuration files** - Manage non-secret configuration with `.env` files, `.gitignore` rules, stage variants, and Makefile loading

## Governance

Contribution and collaboration standards shared across projects.

- [agentme-edr-013](governance/013-contributing-guide-requirements.md) - **Contributing guide requirements** - Define the minimum structure for CONTRIBUTING guides

## Observability

Health, metrics, logging, and monitoring standards.

- [agentme-edr-011](observability/011-service-health-check-endpoint.md) - **Service health check endpoint** - Expose a standard runtime health-check endpoint for services
