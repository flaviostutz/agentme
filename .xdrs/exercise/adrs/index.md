# exercise ADRs Index

Architectural decisions for the exercise questionnaire system.

## Application

- [exercise-adr-policy-101](application/101-question-flow-engine.md) - **Question flow engine** - Single question queue, follow-up routes, next-question priority, refill, pruning and session end
- [exercise-adr-policy-102](application/102-web-client-architecture.md) - **Web client architecture** - Static browser app, shared engine, answers kept on the device

## Data

- [exercise-adr-policy-201](data/201-domain-model.md) - **Domain model** - Domain, Characteristic, Profile, Question and Answer entities and their relationships
- [exercise-adr-policy-202](data/202-registries.md) - **Registries** - JSON registries, schemas and configuration that hold the catalogue, and where they live
- [exercise-adr-policy-203](data/203-reference-instruments.md) - **Reference instruments** - Stored instruments, their related Profiles and item-to-question mapping
