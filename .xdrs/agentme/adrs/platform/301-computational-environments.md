---
name: agentme-adr-policy-301-computational-environments
description: Defines the computational environments (sbx, dev, tst, acc, prd), the purpose and access of each, which environments a system may depend on, and how external vendor services are consumed in non-production environments. Use when designing, deploying, testing or connecting any system.
apply-to: All systems built and operated by teams adopting agentme, in every deployment, test and acceptance activity
valid-from: 2026-10-16
---

# agentme-adr-policy-301: Computational environments

## Context and Problem Statement

Teams deploy, integrate and accept systems in several environments. Without shared definitions, environments get mixed purposes, unstable dependencies leak into development and testing, and vendor services are consumed inconsistently.

Question: Which environments exist, what may each depend on, and how are external vendor services consumed in them?

## Decision Outcome

**Five environments with fixed purposes, outbound dependencies limited per environment, and production-grade vendor endpoints in every non-production environment**

Environments are always referred to by their short name. How short names are used in `STAGE`, files, resources and tags is defined in [agentme-edr-307](../../edrs/platform/307-environment-short-names.md).

### Details

#### 01-environment-set-and-purposes

Every computational environment MUST be exactly one of the environments below.

| Short name | Environment | Main purpose |
|---|---|---|
| `sbx` | sandbox | Spikes and proofs of concept, isolated from the company |
| `dev` | development | Developers and teams check that their own solution runs, at least in part |
| `tst` | test | Different teams check that their solutions integrate and do not break each other |
| `acc` | acceptance | Verify architecture and integrations in a production-like area, and run UAT |
| `prd` | production | Serve final users; the most important environment for the whole company |

A developer's local machine and a CI runner are not environments. Local runs MUST follow the dependency rules of `dev`.

#### 02-sbx-must-be-isolated-and-short-lived

`sbx` MUST be connected only to the public internet and MUST NOT be connected to the company in any way; it is treated like an external client working from home. It MUST hold no company data, and no company credentials.

Each `sbx` environment MUST be ephemeral: it MUST have an owner and an expiry date set at creation, and it MUST be fully deleted at expiry unless the owner renews it.

#### 03-dev-must-support-partial-solutions

`dev` MUST be accessible to all developers. A `dev` environment MAY run only part of a solution, and it MAY be created for each push or pull request (for example `dev-pr123`).

A `dev` environment MUST NOT require another system's `dev` environment to be running in order to work, although it MAY connect to it. It SHOULD use the `tst` environment of other systems instead.

#### 04-tst-must-run-the-full-dependency-chain

`tst` MUST be accessible to all developers and MUST run the complete solution with its entire chain of dependencies, so that systems can depend on each other. It SHOULD be updated automatically when changes are merged to the main branch.

#### 05-acc-must-mirror-prd-architecture

`acc` MUST use exactly the same architecture as `prd`, at a lower scale, and MUST run the complete dependency chain. It is the place for UAT checks and approvals.

`acc` MUST have no final users. Its users MUST be internal employees, plus named external testers when UAT requires them.

#### 06-prd-serves-final-users

`prd` MUST be the only environment used by final users. Developers and engineers MUST have access to the monitoring and consoles of their solutions in `prd`.

#### 07-outbound-dependencies-must-follow-the-matrix

A system's runtime MUST depend only on the targets allowed for its environment below. Access by people is governed by rules `02-sbx-must-be-isolated-and-short-lived` to `06-prd-serves-final-users`, and shared platform services by `08-shared-platform-services-must-exclude-sbx`.

| Caller | MAY depend on | MUST NOT depend on |
|---|---|---|
| `sbx` | public internet, vendor non-production endpoints | any company system |
| `dev` | `dev`, `tst` | `sbx`, `acc`, `prd`; requiring another system's `dev` to work |
| `tst` | `tst` | `sbx`, `dev`, `acc`, `prd` |
| `acc` | `acc` | `sbx`, `dev`, `tst`, `prd` |
| `prd` | `prd` | `sbx`, `dev`, `tst`, `acc` |

External vendor endpoints are an exception to this matrix and follow `10-vendor-environments-must-be-production-grade`.

#### 08-shared-platform-services-must-exclude-sbx

Shared platform services (CI, package and image registries, identity, observability, and similar) MAY be used from `dev`, `tst`, `acc` and `prd`. Each environment MUST send to them only its own data. `sbx` MUST NOT use them.

#### 09-credentials-must-be-distinct-per-environment

Credentials MUST be distinct per environment, and a credential MUST NOT be valid in more than one environment. Secrets handling follows [agentme-edr-124](../../edrs/application/124-secrets-management.md).

#### 10-vendor-environments-must-be-production-grade

Systems MUST NOT connect to the `sbx`, `dev`, `tst` or `acc` environments of an external vendor, because vendors release unfinished changes there.

When selecting or contracting a vendor, the company MUST require a production-grade non-production endpoint: a simulator, staging or "sandbox" version of its APIs with the same API shape and functionality as production, and a service level similar to production. The vendor MUST NOT release changes there while developing, testing or accepting its own software.

`sbx`, `dev`, `tst` and `acc` MUST use that non-production endpoint, and `prd` MUST use the live endpoint and MUST NOT call any vendor non-production endpoint. The vendor SHOULD provide one non-production endpoint per environment; a single shared non-production endpoint MAY be used, and recorded.

When the vendor cannot provide a production-grade non-production endpoint, teams MUST apply the fallbacks below in this order:

1. A mock or simulator owned by the company.
2. An endpoint offered by the vendor with similar functionality, only as a last resort, because it destabilizes development teams.

Each fallback, and each shared endpoint, MUST be recorded as an exception as defined in [agentme-edr-307](../../edrs/platform/307-environment-short-names.md).

## References

- [agentme-edr-307](../../edrs/platform/307-environment-short-names.md) - Short names and their use in `STAGE`, files, resources and tags
- [agentme-edr-303](../../edrs/platform/303-common-targets.md) - `STAGE` variable and `deploy` targets
- [agentme-edr-306](../../edrs/platform/306-performance-testing.md) - Performance tests against `acc`
