# agentme ADRs Index

Architectural decisions for software development in the agentme scope.

## Principles

Structure of the XDRS scopes of a business solution.

- [agentme-adr-001](principles/001-business-application-and-application-service-scopes.md) - **Business application and application service scopes** - One scope per business application and per application service linked through extends; extends inherits policies only

## Governance

Compliance and regulatory decisions for applications.

- [agentme-adr-501](governance/501-gdpr-applicability-and-declarations.md) - **GDPR applicability and declarations** - Applicability test, classification tiers and the mandatory `010-gdpr-applicability` hub: opt-out or pointers to every GDPR item
- [agentme-adr-502](governance/502-privacy-by-design-architecture.md) - **Privacy by design architecture** - Minimisation, EU/EEA residency, processors before data, security baseline, automated decisions and AI

## Data

Data lifecycle architecture decisions.

- [agentme-adr-201](data/201-personal-data-retention-and-erasure.md) - **Personal data retention and erasure** - Retention per category, automated purge, erasure propagation to every copy, backups and operational defaults

## Platform

Platform-level runtime and enabling capabilities.

- [agentme-adr-301](platform/301-computational-environments.md) - **Computational environments** - Environments sbx, dev, tst, acc, prd: purposes, dependency matrix, vendor rule, stage deployment lifecycle
