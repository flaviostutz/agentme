---
name: agentme-edr-policy-021-pragmatic-hexagonal-architecture
description: Defines a pragmatic variant of Hexagonal Architecture for organizing application source code into Adapters (inbound/outbound I/O boundaries) and Application (business logic) layers, with explicit naming conventions and folder structure. Use when designing or reviewing the internal layout of application modules.
apply-to: All application projects
valid-from: 2026-05-28
---

# agentme-edr-policy-021: Pragmatic hexagonal architecture

## Context and Problem Statement

Applications often mix business logic with infrastructure concerns (database access, HTTP handling, environment variable reading), making code hard to test, refactor, and reuse.

How should application source code be organized to separate business logic from infrastructure while avoiding unnecessary abstraction layers?

## Decision Outcome

**Organize application source code into three conceptual layers — External (not in codebase), Adapters (inbound/outbound I/O boundaries), and Application (business logic exposed as typed library interfaces) — following a pragmatic variant of Hexagonal Architecture that avoids unnecessary abstractions.**

### Details

#### 01-three-layer-separation

Every application is conceptually divided into three layers:

| Layer | Description |
|-------|-------------|
| **External** | Systems outside the codebase boundary (databases, third-party APIs, message brokers, filesystems, users) |
| **Adapters** | Bridge between External and Application — translate external protocols into application calls and vice versa |
| **Application** | Business logic that delegates I/O to adapters |

#### 02-adapter-naming-conventions

**Inbound adapters** receive external requests or events and trigger application logic. Each gets a flat folder under `adapters/`:

- `cli/` — command-line interface entry point
- `http/` — HTTP/REST server
- `grpc/` — gRPC server
- `ws/` — WebSocket server
- `kafka/` — Kafka consumer
- `mqtt/` — MQTT subscriber
- Additional inbound adapters are allowed with descriptive names

**Outbound adapters** are called by the application to reach external systems. They live under `adapters/connectors/` with one subfolder per external resource, named descriptively:

- e.g.: `stripe-api/`, `config-file/`, `s3-datalake/`, `whatsapp/`, `postgres/`, `redis-cache/`

**Clarification:** "inbound" means the adapter triggers application logic in response to an external stimulus. "Outbound" means the application calls the adapter to interact with an external system.

#### 03-application-layer-rules

- Expose functionality as typed library interfaces
- All inputs must be explicitly passed as typed parameters
- No global variables, no direct environment variable access in `app/` or `shared/`
- Business logic with well-defined input/output behavior
- Group related logic into subfolders (aggregation roots)
- Environment variables must be read only in the bootstrap/entry-point layer of inbound adapters, converted into typed configuration objects, and passed explicitly to all other components

#### 04-mandatory-folder-structure

```text
mysystem/
  Makefile             # targets to run different inbound interfaces (e.g. run-http, run-cli)
  src/
    adapters/          # mandatory
      cli/             # if CLI exists — bootstrap/entry point for CLI
      http/            # if HTTP server exists — bootstrap/entry point for HTTP
      grpc/            # if gRPC exists
      connectors/      # if external resource access exists
        postgres/      # one folder per external resource
        stripe-api/
    app/               # mandatory — core business logic
      feature1.ts
      feature-group/   # optional subfolders for grouping
    shared/            # utilities and functions shared among adapters and app
      logging.ts
      errors.ts
```

`shared/` must contain only infrastructure-agnostic utilities — not business rules or domain logic.

#### 05-pragmatic-coupling

- Application MAY import from Adapters when it simplifies the design
- Avoid excessive abstractions, interface types, and indirection layers
- Only introduce interfaces or abstract types when building a framework where the extra complexity demonstrably pays off
- Prefer concrete implementations over abstract ports — skip the purism of classic Hexagonal Architecture in favor of practicality
- Some coupling between Application and Adapters is acceptable and expected

#### 06-bootstrap-and-entry-points

- Each inbound adapter folder (`cli/`, `http/`, `grpc/`, etc.) contains the bootstrap and entry point for that interface
- The project root Makefile must have targets to run the different inbound interfaces following [agentme-edr-008](../devops/008-common-targets.md) extension conventions (e.g. `run-http`, `run-grpc`)
- Bootstrap code lives in the adapter that receives inbound requests, not in a separate wiring layer

#### 07-minimum-complexity-threshold

- Trivial scripts and single-purpose tools (fewer than ~300 lines with a single I/O boundary) MAY skip this layering
- All other projects MUST use this structure from the start

#### 08-examples-of-data-flow

```text
HTTP request  →  adapters/http/     →  app/create-user     →  adapters/connectors/postgres/
CLI command   →  adapters/cli/      →  app/create-dir      →  adapters/connectors/local-fs/
Kafka message →  adapters/kafka/    →  app/process-event   →  adapters/connectors/stripe-api/
```

## References

- [agentme-edr-016](../principles/016-cross-language-module-structure.md) — Defines the module-root structure (Makefile, dist/, .cache/) that wraps this internal layout
- [agentme-edr-002](../principles/002-coding-best-practices.md) — File size limits and code organization practices that complement this architecture
