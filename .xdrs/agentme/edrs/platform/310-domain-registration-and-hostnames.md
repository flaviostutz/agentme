---
name: agentme-edr-policy-310-domain-registration-and-hostnames
description: Defines when web projects register domains and how hostnames are assigned to modules of a monorepo module group per stage, using the pattern module.stage.group.base-domain with prd omitting the stage. Use when exposing any web, API or other HTTP module on a domain name.
apply-to: Monorepos with module groups whose web, API or other HTTP modules are reachable by hostname in any deployed environment
valid-from: 2026-11-27
---

# agentme-edr-policy-310: Domain registration and hostnames

## Context and Problem Statement

Web projects expose modules (web, api, admin) in several stages. Ad hoc domains and hostnames per stage make URLs unpredictable, break TLS and CORS setups, and scatter DNS ownership.

How must domains be registered and hostnames assigned to modules grouped in a monorepo?

## Decision Outcome

**Register one base domain per organization or project, give each module group a subdomain, and name every module host `<module>.<stage>.<group>.<base-domain>`, omitting `<stage>` in `prd`.**

Stages and `STAGE` values follow [agentme-adr-301](../../adrs/platform/301-computational-environments.md) and [agentme-edr-307](307-environment-short-names.md). The module group is the set of related modules in one monorepo (see [agentme-edr-301](301-monorepo-structure.md)), for example `neurome`.

### Details

#### 01-applicability

This policy applies when a module is reachable by hostname in a deployed stage. A project MUST declare in its README either the base domain and module group name, or that it is not reachable by hostname (for example a library, CLI, or private service reached only by cloud-native addresses). Projects reached only through `localhost` are exempt.

#### 02-base-domain-must-be-registered-and-owned

A web project MUST use a base domain registered under an account owned by the organization, never by an individual. An existing organization domain MAY be reused. The registrar account, the DNS hosted zone and its delegation owner MUST be recorded in the project README. A zone holding `prd` records SHOULD be separate from zones for other stages when the organization's account layout separates them, per [agentme-adr-301](../../adrs/platform/301-computational-environments.md) rule `09-credentials-must-be-distinct-per-environment`.

#### 03-module-group-is-the-first-subdomain

Each module group MUST receive exactly one label directly under the base domain, in lowercase letters, digits and hyphens (for example `neurome` under `stutz.click`). It SHOULD be the monorepo or product name.

#### 04-hostname-pattern

The host of a module MUST follow:

```text
<module>.<stage>.<group>.<base-domain>      # non-prd stages
<module>.<group>.<base-domain>              # prd
```

- `<stage>` is the full `STAGE` value, validated per [agentme-edr-307](307-environment-short-names.md) rule `02-stage-value-must-be-validated`, including variants (`acc`, `tst-pr234`, `dev-flavio`). It is one label.
- `prd` MUST NOT appear in the hostname; the base domain of the group is production.
- `<module>` SHOULD be the module name or very close to it (`api` for `api`), and MAY be any label the team chooses. It MUST be the same in every stage of the same module.
- Each label MUST be lowercase, up to 63 characters; the whole name MUST fit the 253 character DNS limit.

Example for group `neurome` under `stutz.click`:

| Purpose | prd | acc | tst-pr234 |
|---|---|---|---|
| Group address (redirect) | `neurome.stutz.click` | `acc.neurome.stutz.click` | `tst-pr234.neurome.stutz.click` |
| Web module `web` | `web.neurome.stutz.click` | `web.acc.neurome.stutz.click` | `web.tst-pr234.neurome.stutz.click` |
| API module `api` | `api.neurome.stutz.click` | `api.acc.neurome.stutz.click` | `api.tst-pr234.neurome.stutz.click` |

#### 05-group-address-must-redirect-to-the-web-module

The group address of each stage (`<group>.<base-domain>` for `prd`, `<stage>.<group>.<base-domain>` otherwise) MUST redirect to the primary web module host of the same stage. Other modules MUST NOT be served from the group address.

#### 06-dns-and-certificates-must-be-managed-as-code

Records, hosted zones owned by the project, and TLS certificates for module hosts MUST be defined in the `infra/` module of the owning module and applied through `STAGE=<stage> make deploy`, following [agentme-edr-308](308-iac-module-and-deployment.md). The hostname MUST be derived from `STAGE`, the module label and the group configuration in the typed stage configuration, never hand-written per stage.

A wildcard certificate covers only one label level, so certificates MUST list the group address and each module host (or use `*.<stage>.<group>.<base-domain>` per stage, and `*.<group>.<base-domain>` for `prd`).

#### 07-stage-removal-must-remove-records

`undeploy` of a variant stage MUST remove its DNS records and certificates so short-lived stages such as `tst-pr234` leave no dangling names.

#### 08-hostnames-must-not-be-hardcoded

Application code and tests MUST read their own and their peers' hostnames from configuration (see [agentme-edr-305](305-environment-variable-configuration.md) and [agentme-edr-307](307-environment-short-names.md) rule `05-vendor-endpoints-must-be-configured-per-environment`), never as literals for a specific stage.

## References

- [agentme-adr-301](../../adrs/platform/301-computational-environments.md) - Environments and credentials
- [agentme-edr-307](307-environment-short-names.md) - `STAGE` values and variants
- [agentme-edr-308](308-iac-module-and-deployment.md) - IaC and deploy targets
