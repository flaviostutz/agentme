# agentkit

Curated distribution package of XDRs and speckit agent workflow files for AI-assisted software development.

This collection is being updated as we develop applications and feel the need for new instructions and skills to help with AI agents.

## Getting Started

This will extract all the features of agentkit (skills, github configurations, speckit, xdrs collection):

```sh
npx agentkit
```

If you want the version pinned in a project, add `agentkit` to a repository that already has a `package.json` and run it through the local dependency:

```sh
pnpm add -D agentkit
pnpm exec agentkit extract --output . --presets basic
pnpm exec agentkit check --output . --presets basic
```

## Overview

agentkit is published as an npm package and consumed through `npmdata`-based extraction. It ships a curated set of reusable artifacts for other repositories:

- XDRs in `.xdrs/agentkit/` for engineering, architecture, testing, tooling, and CI/CD standards.
- speckit agent files in `.github/`, `.specify/`, and `.vscode/` for specification-driven AI development workflows.

The package is intentionally static: consumers install it as a development dependency, extract files into their own repository, and commit the generated output.

## Presets

| Preset | Contents |
| --- | --- |
| `basic` | `xdrs-core` baseline ADRs, `AGENTS.md`, and agentkit XDRs |
| `speckit` | speckit agents, prompts, templates, scripts, memory files, and VS Code settings |
| no preset | all shipped artifacts combined |

Typical consumer workflow:

1. For one-off use or a new empty folder, run `npx agentkit --presets <preset>`.
2. For a pinned project version, add `agentkit` to `package.json` and use `pnpm exec agentkit ...`.
3. Review and commit the extracted files.
4. Re-run `extract` and `check` when upgrading the package.

## Usage Scenarios

### Guide AI coding with maintained ADRs and EDRs

Use agentkit when you want architectural and engineering decisions to actively constrain how coding agents implement features. The extracted ADRs and EDRs give the repository a durable source of truth for architecture, coding practices, testing expectations, tooling, and delivery standards.

This is useful when you want agents to:

- consult explicit architecture records before choosing patterns or integrations;
- follow engineering rules for project structure, quality, testing, and operations;
- produce code that stays aligned with documented decisions instead of ad hoc prompt instructions.

### Register feature and product knowledge as BDRs

Use XDR business records to capture product and operational knowledge while features are being delivered. BDRs are meant to document workflows, requirements, business rules, operating procedures, and product decisions in the same structured format as technical decisions.

This is useful when you want feature work to leave behind maintainable documentation for:

- application workflows and operating procedures;
- product requirements and business constraints;
- business decisions that explain why the feature behaves the way it does.

### Keep project documentation current through the speckit workflow

Use the `speckit` distribution when you want the delivery workflow itself to instruct agents to maintain ADRs, EDRs, and BDRs as implementation evolves. In this model, feature development and project documentation happen together: major technical and business decisions are continuously written back into XDRs instead of being deferred to a separate documentation pass.

This is useful when you want to:

- keep the project decision log up to date as new features are specified and implemented;
- have architecture, engineering, and business documentation generated in a consistent XDR format;
- reuse the same XDR-based approach across other repositories that consume agentkit.

## Development

Use the root `Makefile` as the entry point for local verification:

```sh
make build
make lint
make test
```

What these targets do:

- `make build` installs dependencies and creates a local npm package in `dist/`.
- `make lint` runs the repository lint target.
- `make test` rebuilds the package and validates the consumer extraction flow through the runnable example in `examples/`.

## Repository Map

```text
.
├── AGENTS.md           Project instructions for AI coding agents
├── Makefile            Root build, lint, test, and publish entry point
├── .mise.toml          Pinned tool versions (Node.js, pnpm)
├── bin/                CLI entrypoint delegated to npmdata
├── dist/               Generated npm package tarballs
├── examples/           Runnable verification of consumer extraction behavior
├── .github/            Shipped speckit agent and prompt files
├── .specify/           Shipped speckit memory, scripts, and templates
└── .xdrs/              Shipped XDRs plus local project-only decision records
```

Key folders:

- `.xdrs/_core/` contains the baseline XDR framework imported from `xdrs-core`.
- `.xdrs/agentkit/` contains the reusable XDRs distributed to consumers.
- `.xdrs/_local/` contains internal decisions for this repository only and is not shipped to consumers.
- `examples/output/` is generated during tests to validate preset extraction and cleanup behavior.

## Release Notes

The published package exposes the `agentkit` CLI through `bin/npmdata.js` and is released to npm using the root `publish` target. The examples install the locally packed tarball from `dist/` so they exercise the same package shape an external consumer receives.