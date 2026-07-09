# agentme EDRs Index

Engineering decisions specific to the agentme project: a curated library of XDRs and skills encoding best practices for AI coding agents.

Propose changes via pull request. All changes must be verified for clarity and non-conflict before merging.

## Principles

Foundational standards, principles, and guidelines.

- [agentme-edr-012](principles/012-continuous-xdr-enrichment.md) - **Continuous xdr improvement policy** - Promote recurring delivery lessons into reusable XDRs
- [agentme-edr-016](principles/016-cross-language-module-structure.md) - **Cross-language module structure** - Organize modules consistently across supported languages

## Articles

Synthetic views combining agentme XDRs and skills around a specific topic.

- [agentme-article-001](principles/articles/001-continuous-xdr-improvement.md) - **Continuous XDR improvement** (what an XDR is, when to write one, how to discuss it, how to organize it, workflow)

## Application

Language and framework-specific tooling and project structure.

- [agentme-edr-121](application/121-coding-best-practices.md) - **Coding best practices** - Keep files small, tests nearby, and docs synchronized
- [agentme-edr-122](application/122-unit-test-requirements.md) - **Unit test requirements** - Define minimum unit-test coverage and naming expectations
- [agentme-edr-123](application/123-error-handling.md) - **Error handling** - Standardize explicit errors, logging, and propagation rules
- [agentme-edr-124](application/124-secrets-management.md) - **Secrets management** - Handle secrets securely using native keychains and cloud secret managers
- [agentme-edr-125](application/125-coding-abstraction-practices.md) - **Coding abstraction practices** - Define when abstractions are justified and when they must be inlined

### Language and framework tooling

- [agentme-edr-101](application/101-javascript-project-tooling.md) - **JavaScript project tooling and structure** - Scaffold JavaScript libraries with the standard toolchain *(includes skill: [001-create-javascript-project](application/skills/001-create-javascript-project/SKILL.md))*
- [agentme-edr-102](application/102-golang-project-tooling.md) - **Go project tooling and structure** - Scaffold Go CLIs and libraries with the standard layout *(includes skill: [003-create-golang-project](application/skills/003-create-golang-project/SKILL.md))*
- [agentme-edr-103](application/103-python-project-tooling.md) - **Python project tooling and structure** - Scaffold Python packages and CLIs with the standard layout *(includes skill: [005-create-python-project](application/skills/005-create-python-project/SKILL.md))*
- [agentme-edr-104](application/104-cli-tool-standards.md) - **CLI tool standards** - Define command UX and behavior for CLI tools
- [agentme-edr-126](application/126-pragmatic-hexagonal-architecture.md) - **Pragmatic hexagonal architecture** - Organize application layers as External/Adapters/Application with practical coupling rules
- [004-select-relevant-xdrs](application/skills/004-select-relevant-xdrs/SKILL.md) - **Select relevant XDRs**

### AI development

Standards for building LLM, Agent, and Workflow components.

- [agentme-edr-141](application/141-ai-llm-development-standards.md) - **AI LLM development standards** - Standard framework (LangChain) and patterns for simple LLM calls with explicit configuration (no environment variables)
- [agentme-edr-142](application/142-ai-agents-development-standards.md) - **AI agents development standards** - Structural patterns for agents: framework selection, sandbox setup, naming conventions, composition, and system prompt structure
- [agentme-edr-143](application/143-ai-agents-quality-standards.md) - **AI agents implementation quality standards** - Tool definition patterns, error handling, observability, and unit testing for agents
- [agentme-edr-144](application/144-ai-workflow-development-standards.md) - **AI workflow development standards** - Standard toolchain (LangGraph), evaluation, and testing patterns for workflow projects
- [agentme-edr-145](application/145-ai-workflow-naming-conventions.md) - **AI workflow naming conventions** - Node suffix/prefix roles, state type and attribute naming, judge output schema, workflow class names, and cross-element coherence rules
- [agentme-edr-146](application/146-ai-agent-xdrs-knowledge-layer.md) - **AI agent XDRS knowledge layer** - How to integrate XDRS as the runtime source of truth for policies and skills in AI agents (apply only when the project explicitly uses XDRS)

### AI evaluation and testing

Standards for eval datasets, scripts, reports, and test type taxonomy.

- [agentme-edr-151](application/151-ai-eval-core-standards.md) - **AI eval core standards** - Eval folder structure and Makefile interface; LLM-as-judge binary scoring contract applicable to all AI tiers and test types
- [agentme-edr-152](application/152-ai-test-types-taxonomy.md) - **AI test types taxonomy** - Names AI test types (`functional`, `safety`, `smoke`, `repeatability`, `adversarial`, `fairness`, `bias`, and 5 others) with group, objective, mocking constraint, and relevance, and defines the shared golden dataset entry envelope
- [agentme-edr-153](application/153-ai-eval-script.md) - **AI eval script** - eval.py requirements: entry-first loop, --type filtering, mock_fixtures wiring, human entries, threshold enforcement, and MLflow experiment conventions
- [agentme-edr-154](application/154-ai-eval-report-format.md) - **AI eval report format** - report-<type>.md template, Wilson score confidence interval, convergence analysis, and human-type checklist artifact
- [agentme-edr-155](application/155-ai-eval-repeatability.md) - **AI eval repeatability** - Repeatability test type: REPEAT_COUNT loop exception, semantic-similarity and LLM-as-judge scoring, repeatability_accuracy metric, report shape, and run cadence

## Data

Data layer implementation and data management decisions.

- [agentme-edr-201](data/201-ml-dataset-structure.md) - **ML dataset structure** - Standard folder layout and file conventions for ML datasets

## Platform

Infrastructure implementation, delivery pipeline, and developer environment decisions.

- [agentme-edr-301](platform/301-monorepo-structure.md) - **Monorepo structure** - Standardize monorepo layout, tooling, and package boundaries *(includes skill: [002-monorepo-setup](platform/skills/002-monorepo-setup/SKILL.md))*
- [agentme-edr-302](platform/302-github-pipelines.md) - **GitHub CI/CD pipelines** - Define required CI stages and workflow structure
- [agentme-edr-303](platform/303-common-targets.md) - **Common development script names** - Reuse standard build, lint, and test target names
- [agentme-edr-304](platform/304-tool-execution-and-scripting.md) - **Tool execution and scripting** - Run tools consistently across shells, Makefiles, and CI
- [agentme-edr-305](platform/305-environment-variable-configuration.md) - **Environment variable configuration files** - Manage non-secret configuration with `.env` files, `.gitignore` rules, stage variants, and Makefile loading

## Governance

Contribution and collaboration standards shared across projects.

- [agentme-edr-501](governance/501-project-quality-standards.md) - **Project quality standards** - Require build, lint, and test verification before completion
- [agentme-edr-502](governance/502-contributing-guide-requirements.md) - **Contributing guide requirements** - Define the minimum structure for CONTRIBUTING guides

## Operations

Production behavior and operational response decisions.

- [agentme-edr-401](operations/401-service-health-check-endpoint.md) - **Service health check endpoint** - Expose a standard runtime health-check endpoint for services
