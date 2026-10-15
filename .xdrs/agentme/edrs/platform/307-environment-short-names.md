---
name: agentme-edr-policy-307-environment-short-names
description: Defines how the environment short names (sbx, dev, tst, acc, prd) are used in the STAGE variable, .env files, resource names, tags and labels, and how vendor endpoints and their exceptions are configured per environment. Use when naming, configuring or deploying anything per environment.
apply-to: All projects that deploy, configure or name resources per environment
valid-from: 2026-10-16
---

# agentme-edr-policy-307: Environment short names

## Context and Problem Statement

Environments defined in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) show up in Makefiles, env files, resource names and tags. Mixed spellings (`production`, `staging`, `test`, `pre-prod`) make scripts, filters and reviews inconsistent.

Question: How must environment short names be used in names, files, tags and vendor configuration?

## Decision Outcome

**Only the five short names `sbx`, `dev`, `tst`, `acc` and `prd`, in a validated `STAGE` value, `.env.<stage>` files, `-<stage>` resource suffixes and a `stage` tag**

### Details

#### 01-only-short-names-must-be-used

The environment name in `STAGE`, env file names, resource names, tags, labels, pipeline variables and documentation MUST be one of `sbx`, `dev`, `tst`, `acc` or `prd`. Long or alternative names (`sandbox`, `development`, `test`, `staging`, `pre-prod`, `production`) MUST NOT be used for these environments.

#### 02-stage-value-must-be-validated

`STAGE` follows [agentme-edr-303](303-common-targets.md) rule `04-standard-environment-variables`. Its prefix MUST be one of the five short names. The optional variant MUST contain only lowercase letters, digits and hyphens, and its meaning is chosen by the team (for example `dev-pr123`, `prd-blue`).

Environment-aware Makefile targets MUST fail fast with a message naming the value when `STAGE` does not match this pattern:

```text
^(sbx|dev|tst|acc|prd)(-[a-z0-9]+)*$
```

#### 03-env-files-must-use-the-prefix-name

Deployment configuration MUST follow [agentme-edr-305](305-environment-variable-configuration.md) rule `04-stage-specific-dotenv-committed` using `.env.<prefix>` (for example `.env.tst`, `.env.prd`).

A variant MAY add `.env.<prefix>-<variant>` (for example `.env.dev-pr123`). It MUST be loaded after `.env.<prefix>` and only overrides values; the `.env.<prefix>` file MUST still exist.

#### 04-resources-and-tags-must-carry-the-stage

Resource names SHOULD end with `-<stage>` using the full `STAGE` value (for example `orders-api-tst`, `orders-api-dev-pr123`). Every deployed resource that supports tags or labels MUST carry the key `stage` with the full `STAGE` value (for example `stage=acc`).

#### 05-vendor-endpoints-must-be-configured-per-environment

Vendor endpoint addresses MUST be set per environment through `.env.<prefix>` (per rule `03-env-files-must-use-the-prefix-name`) and MUST NOT be hardcoded in code. `.env.prd` MUST hold only live vendor endpoints; `.env.sbx`, `.env.dev`, `.env.tst` and `.env.acc` MUST hold only the vendor's production-grade non-production endpoints or a recorded fallback, as defined in [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `10-vendor-environments-must-be-production-grade`. Credentials are not configuration and follow [agentme-edr-124](../application/124-secrets-management.md).

```text
# .env.tst
PAYMENTS_URL=https://sandbox.payments.example
# .env.prd
PAYMENTS_URL=https://api.payments.example
```

#### 06-vendor-exceptions-must-be-recorded

Each use of a company mock, a vendor-offered similar endpoint, or a shared non-production endpoint MUST be recorded in the project README under a `Vendor environment exceptions` heading. Each entry MUST state the vendor, the environments affected, which fallback or shared endpoint is used, the reason, and the date recorded.

## References

- [agentme-adr-301](../../adrs/platform/301-computational-environments.md) - Environments, purposes and dependency rules
- [agentme-edr-303](303-common-targets.md) - `STAGE` variable and `deploy` targets
- [agentme-edr-305](305-environment-variable-configuration.md) - Env files per stage
