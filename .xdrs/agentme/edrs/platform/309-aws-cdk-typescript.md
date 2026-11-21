---
name: agentme-edr-policy-309-aws-cdk-with-typescript
description: Defines how AWS resources are deployed with AWS CDK in TypeScript: layout, stage configuration, offline synthesis in build, deploy command, tests and TypeScript/ts-node setup. Use when a module deploys AWS resources.
apply-to: Modules that deploy AWS resources
valid-from: 2026-11-19
---

# agentme-edr-policy-309: AWS CDK with TypeScript

## Context and Problem Statement

AWS resources need one standard infrastructure as code tool so that pipelines and developers build, test and deploy them the same way, in the TypeScript language already used by the project standards.

Which tool and project setup must modules use to deploy AWS resources?

## Decision Outcome

**Use AWS CDK v2 in TypeScript inside the `infra/` folder of the module, following [agentme-edr-308](308-iac-module-and-deployment.md), with offline synthesis in `make build` and `cdk deploy` as the only deploy mechanism.**

The environment lifecycle is defined in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `11-stage-deployment-lifecycle` and the `deploy.yml` workflow in [agentme-edr-302](302-github-pipelines.md).

### Details

#### 01-cdk-v2-in-typescript

AWS resources MUST be defined with `aws-cdk-lib` v2 (and `constructs`) written in TypeScript, using the toolchain of [agentme-edr-101](../application/101-javascript-project-tooling.md). The `aws-cdk` CLI MUST be a dev dependency of the module and run through the Makefile with `mise exec -- pnpm exec cdk`.

#### 02-layout

```text
orders/
  src/                  # application code
  infra/
    cdk.json            # {"app": "npx ts-node --prefer-ts-exts bin/app.ts"}
    tsconfig.json       # extends ../tsconfig.json, "noEmit": true
    bin/app.ts          # reads STAGE, builds the stacks
    stacks/             # stack and construct classes
    config/stages.ts    # typed stage configuration
```

`cdk` commands MUST run from `infra/`. `infra/` MUST NOT be emitted to the module `dist/`, which is why its `tsconfig.json` is `noEmit`. `cdk.out/` MUST be git-ignored and removed by `make clean`.

#### 03-typescript-and-ts-node-versions

The app runs through ts-node, which can fail with the newest TypeScript releases. The module MUST pin a TypeScript version that its ts-node version supports and MUST NOT upgrade one without verifying `make build`.

#### 04-stage-configuration

`config/stages.ts` MUST follow [agentme-edr-308](308-iac-module-and-deployment.md) rule `03-stage-configuration-is-typed-code`. The stack `env.region` MUST come from it, and `AWS_REGION` SHOULD be the same value. `env.account` MUST come from `CDK_DEFAULT_ACCOUNT` and MUST NOT be hardcoded; when `expectedAccountId` is set and the account is known, `bin/app.ts` MUST throw on mismatch.

```ts
export type StageConfig = { region: string; expectedAccountId?: string; minCapacity: number };

const byPrefix: Record<string, StageConfig> = {
  dev: { region: 'eu-west-1', minCapacity: 1 },
  tst: { region: 'eu-west-1', minCapacity: 1, expectedAccountId: '111111111111' },
  acc: { region: 'eu-west-1', minCapacity: 2, expectedAccountId: '222222222222' },
  prd: { region: 'eu-west-1', minCapacity: 3, expectedAccountId: '333333333333' },
};

// 'dev-pr123' resolves to the 'dev' configuration; unknown prefixes throw
export const getStageConfig = (stage: string): StageConfig => {
  const config = byPrefix[stage.split('-')[0]];
  if (!config) throw new Error(`Unknown STAGE '${stage}'`);
  return config;
};
```

#### 05-naming-and-tags

Stack names MUST end with `-<stage>` and every stack MUST carry the tag `stage` with the full `STAGE` value, per [agentme-edr-307](307-environment-short-names.md) rule `04-resources-and-tags-must-carry-the-stage`.

#### 06-no-context-lookups

Stacks MUST NOT use context lookups (`fromLookup` and similar), so synthesis works without credentials. Values from other stacks or accounts MUST be passed through stage configuration, stack references or parameters.

#### 07-build-synthesizes-offline

The module `build` target MUST type-check `infra/` and synthesize it with lookups disabled, with `STAGE` defaulting to `dev`:

```makefile
STAGE ?= dev
build:
	mise exec -- pnpm exec tsc -p infra/tsconfig.json
	cd infra && STAGE=$(STAGE) mise exec -- pnpm exec cdk synth --no-lookups --quiet
```

A stack that needs a lookup makes this step fail, which is intended.

#### 08-deploy-command

`make deploy` MUST require `STAGE` and the `CI` rule of [agentme-edr-308](308-iac-module-and-deployment.md) rule `08-deploy-targets-require-stage-and-the-pipeline`, then run:

```bash
cd infra && mise exec -- pnpm exec cdk deploy --all --require-approval never
```

It MUST NOT pass `--profile`. The account MUST be prepared once with `cdk bootstrap` for each account and region before the first deploy, per rule `10-account-must-be-bootstrapped-before-the-first-deploy` of [agentme-edr-308](308-iac-module-and-deployment.md).

#### 09-tests

Stacks MUST have Jest tests using `aws-cdk-lib/assertions` (`Template.fromStack`) that check the resources and properties that matter, and `getStageConfig` MUST have tests for known stages, variants and unknown prefixes. Tests live next to the code in `infra/`, run in `make test` offline, and count towards the coverage rules of [agentme-edr-122](../application/122-unit-test-requirements.md).

## References

- [agentme-edr-308](308-iac-module-and-deployment.md) - IaC module, stage configuration, credentials and deploy rules
- [AWS CDK environments](https://docs.aws.amazon.com/cdk/v2/guide/environments.html) - `CDK_DEFAULT_ACCOUNT` and `CDK_DEFAULT_REGION`
