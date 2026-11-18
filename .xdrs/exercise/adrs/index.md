# exercise ADRs Index

Architectural decisions for the exercise questionnaire system.

## Application

- [exercise-adr-policy-101](application/101-question-flow-engine.md) - **Question flow engine** - Single question queue, follow-up routes, next-question priority, refill, pruning and session end

## Data

- [exercise-adr-policy-201](data/201-domain-model.md) - **Domain model** - Domain, Characteristic, Profile, Question and Answer entities and their relationships
- [exercise-adr-policy-202](data/202-registries.md) - **Registries** - JSON registries, schemas and configuration that hold the catalogue, and where they live
- [exercise-adr-policy-203](data/203-reference-instruments.md) - **Reference instruments** - Where published instruments (AQ-50, ASRS-v1.1, ARHQ, OCI-R) are stored, the Profile each relates to and how their items map to the bank
