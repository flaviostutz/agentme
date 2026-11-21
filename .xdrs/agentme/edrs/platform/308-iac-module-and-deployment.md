---
name: agentme-edr-policy-308-iac-module-and-deployment
description: Defines how infrastructure as code lives in a module (infra/ folder), how stage configuration, cloud credentials and deploy targets work identically on a developer machine and in pipelines. Use when a module deploys cloud resources with any IaC tool.
apply-to: Modules that deploy cloud resources using infrastructure as code with any tool (CDK, Terraform, etc.)
valid-from: 2026-11-19
---

# agentme-edr-policy-308: IaC module and deployment

## Context and Problem Statement

Modules that deploy cloud resources end up with per-developer profiles, hidden per-environment settings, and deploy steps that differ between a laptop and the pipeline. This makes deployments hard to test, share and reproduce.

How must infrastructure code, stage configuration and cloud credentials be organized so that local runs and pipelines behave the same?

## Decision Outcome

**Keep infrastructure code in an `infra/` folder of the module, drive it only by `STAGE` plus cloud credentials from environment variables, and keep per-stage configuration as typed, testable code.**

The environments and their deployment lifecycle are defined in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `11-stage-deployment-lifecycle`, and the workflows in [agentme-edr-302](302-github-pipelines.md). For AWS with TypeScript see [agentme-edr-309](309-aws-cdk-typescript.md).

### Details

#### 01-infra-folder-in-the-module

Infrastructure code MUST live in an `infra/` folder inside the module that owns the deployed system, whatever the IaC tool (for example CDK or Terraform). Application code (service, web, UI) stays where its language standard puts it (for example `src/`). A module that only holds infrastructure MAY contain just `infra/`.

The module `Makefile` MUST expose the infra actions through the standard targets of [agentme-edr-303](303-common-targets.md): `build` validates it, `test` tests it, `deploy` and `undeploy` apply it.

#### 02-stage-and-credentials-are-the-only-inputs

`STAGE` (validated per [agentme-edr-307](307-environment-short-names.md)) and the cloud credentials of rule `04-credentials-come-only-from-environment-variables` MUST be the only inputs needed to deploy. Everything else MUST come from the typed stage configuration, so a deploy command is always `STAGE=<stage> make deploy`.

#### 03-stage-configuration-is-typed-code

Per-stage configuration (region, sizes, endpoints, identifiers, expected account) MUST be code in `infra/`, as a typed and pure function or map from `STAGE` to a configuration object, covered by unit tests under [agentme-edr-122](../application/122-unit-test-requirements.md). It MUST NOT contain secrets, which follow [agentme-edr-124](../application/124-secrets-management.md).

A variant such as `dev-pr123` MUST resolve to the configuration of its prefix (`dev`) and MAY override selected values. An unknown prefix MUST fail fast. `.env.<stage>` files carry only feature flags, per [agentme-edr-305](305-environment-variable-configuration.md) rule `04-stage-specific-dotenv-committed`.

#### 04-credentials-come-only-from-environment-variables

Cloud credentials MUST be provided only as environment variables, for example `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN` and `AWS_REGION` for AWS. Credential profiles, shared credential files (such as `~/.aws`), and CLI options that select a profile (such as `--profile`) MUST NOT be used, locally or in pipelines, so both behave the same. The account is the one the credentials belong to.

Credentials SHOULD be short-lived, MUST be distinct per environment as in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `09-credentials-must-be-distinct-per-environment`, and MUST NOT be committed or written to disk.

#### 05-local-credentials-are-exported-from-a-secret-store

On a developer machine, credentials MUST be fetched from the OS keychain or a token tool and exported only into the environment of the process that needs them, never saved in files, `.env`, dotfiles or profiles:

```bash
AWS_ACCESS_KEY_ID=$(fetch-secret aws-dev-id) \
AWS_SECRET_ACCESS_KEY=$(fetch-secret aws-dev-key) \
AWS_REGION=eu-west-1 STAGE=dev make deploy
```

`fetch-secret` stands for the keychain or token tool in use. Fetching directly from a secret manager with libraries inside the tool or application is preferable, per [agentme-edr-124](../application/124-secrets-management.md).

#### 06-expected-account-must-be-checked

Stage configuration MAY declare an `expectedAccountId`. When declared, `deploy` MUST fail when the account of the credentials differs. It SHOULD be declared for `tst`, `acc` and `prd`.

#### 07-build-lint-and-test-stay-offline

`build`, `lint` and `test` of a module with `infra/` MUST run without credentials or network access to the cloud, following [agentme-edr-303](303-common-targets.md) rule `08-default-targets-must-only-include-offline-subtargets`. Infrastructure validation in `build` (for example synthesizing the templates) MUST NOT perform lookups against the cloud account. Only `deploy` and `undeploy` use credentials.

#### 08-deploy-targets-require-stage-and-the-pipeline

`make deploy` and `make undeploy` MUST fail when `STAGE` is not set; only `build`, `lint` and `test` default to `dev`.

Local runs MAY deploy only `sbx` and `dev` variants. For `tst`, `acc` and `prd` the `deploy` target MUST refuse to run unless the `CI` environment variable is `true`, and developers MUST NOT hold credentials for these environments.

#### 09-shared-stages-are-removed-manually

`undeploy` of `tst`, `acc` and `prd` MUST be done manually by a person in the cloud console (for example deleting the CloudFormation stacks); pipelines MUST NOT destroy these environments. `sbx` and `dev` variants MAY be removed locally with `make undeploy`.

#### 10-account-must-be-bootstrapped-before-the-first-deploy

Any one-time preparation that the IaC tool needs in a cloud account (for example the CDK bootstrap stack) MUST be done before the first deploy to that account, and is documented in the module README.

## References

- [agentme-adr-301](../../adrs/platform/301-computational-environments.md) - Environments and deployment lifecycle
- [agentme-edr-302](302-github-pipelines.md) - `deploy.yml` workflow, credentials in pipelines, rollback
- [agentme-edr-309](309-aws-cdk-typescript.md) - AWS CDK with TypeScript
