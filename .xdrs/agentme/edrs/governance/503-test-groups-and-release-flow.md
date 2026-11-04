---
name: agentme-edr-policy-503-test-groups-and-release-flow
description: Defines four test groups (Development, Governance, Business, Production), the release flow and gates between them, and the main group of every test type. Use when naming, planning or discussing tests, deciding who approves a release, or classifying a new test type.
apply-to: Software projects that plan, run or discuss tests across the delivery flow, including AI systems
valid-from: 2026-10-30
---

# agentme-edr-policy-503: Test groups and release flow

## Context and Problem Statement

Unit tests, regulator evidence, business acceptance and production rollouts have different risk, people, data and standards, yet are discussed as one thing. What groups of tests exist, how do they flow to production, and where does each test type belong?

## Decision Outcome

**Classify every test type into one of four groups that follow the delivery flow: Development, Governance, Business, Production.**

A group is defined by its objective at a point of the delivery flow, not by the environment where it runs. Gates between groups are explicit and recorded.

### Details

#### 01-four-groups-follow-the-delivery-flow

Test discussions, plans, reports and policies MUST name tests by group and MUST write the group in full with the word "group" (for example "group Governance"), never as a code, so it is not confused with the environments `dev`, `acc` and `prd` of [agentme-adr-301](../../adrs/platform/301-computational-environments.md). The group is where a test is classified; the environment is only where it mostly runs.

| Group | Objective | Main environment | Data | Owners and executors | Users involved | Evidence |
|---|---|---|---|---|---|---|
| Development | Show the system works as built and is fast and stable enough | local, CI, `dev`, `tst`; performance in `acc` | Synthetic, fixtures, mocked dependencies | Developers, Tester/QA, AI Engineer | None | CI results and eval reports |
| Governance | Show security, legal and control requirements are met | `acc` (continuous post-market monitoring in `prd`) | Curated, versioned, synthetic or anonymised | AI Lead (AI controls), Tech Lead (security), Tester/QA; compliance/risk function reviews evidence | None | Retained, auditable evidence per control |
| Business | Let the business know the consequences of deploying | `acc` | Realistic, production-like, anonymised or synthetic | Business analyst, business SMEs as named testers | Selected business users | Gate record (rule `04`) |
| Production | Check real infrastructure, real users and cases that cannot be simulated | `prd` | Real | DevOps/Infra runs; Product Owner and Tech Lead decide | Real users in controlled audiences | Rollout stage records and monitoring |

A test belongs to group Governance only when its pass/fail criteria come from a law, regulation, standard, contract or internal control and its evidence is retained for audit; any other purpose belongs to another group. Business tests are also known as acceptance tests or UAT. Personal-data rules per group are decided by each project under its own data-protection policies; this policy only states the data quality expected from each group.

#### 02-flow-and-gates

The flow is: group Development CI gate, deploy to `acc`, then group Governance, group Business and the group Development performance runs in parallel, then one release decision, then group Production. All three parallel tracks MUST finish before the release decision. A failed gate returns the build to group Development. A rollback or incident in `prd` also returns to group Development.

Each Governance control MUST declare a cadence: per release, or periodic (for example an annual penetration test). Periodic evidence satisfies a release while it is within its declared validity period.

The Business gate in rule `04` with its risk impact analysis MUST be passed before any deploy to `prd`, including deploys with the feature flag off.

#### 03-governance-exceptions

A failed mandatory Governance control MUST block the release, unless the organisation's compliance/risk function records an exception with a reason and a due date to fix. The compliance/risk function sits outside the role roster of [agentme-bdr-402](../../bdrs/operations/402-digital-product-roles.md). Business approvers MUST NOT waive a Governance failure. Requirements of [agentme-edr-501](501-project-quality-standards.md) rule `09` that block a release MUST NOT be waived by this rule or by rule `06`.

#### 04-business-gate-is-recorded-risk-acceptance

The Business gate is the "Production readiness and go-live approval" of [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md): the Product Owner decides and the Tech Lead's opinion MUST be recorded. The gate does not require perfect software; it requires that the consequences of deploying are known. The gate record MUST list the Governance and Business results, what was not tested in `acc` and why (for example cost or impossible simulation), and the Production mitigation for each (slow rollout, flags, monitoring, alarms).

#### 05-production-rollout-plan

Production tests run under a rollout plan with alpha (internal users), beta (selected real users) and GA stages. Each stage MUST declare audience, deployment window, rollback scenario and test objective. The Business gate approves entry to the first stage; later stage moves follow the plan's criteria and are decided by the Product Owner. Rollback authority stays with the Tech Lead. A/B tests and blue/green follow [agentme-edr-407](../operations/407-a-b-testing-in-production.md); flag-only rollback MUST be rehearsed before launch per that policy.

#### 06-emergency-path

An emergency release (for example a security hotfix) MAY run a reduced Governance and Business scope. Every skipped test MUST be named in a risk record approved by the roles of rules `03` and `04`, with a due date set per case by which it runs; there is no default period. Skipping silently MUST NOT happen. Group Development tests and the requirements of [agentme-edr-501](501-project-quality-standards.md) rule `09` remain mandatory, apart from the A/B exemption that rule already grants.

#### 07-every-test-type-has-one-main-group

The main group of a test type is the group, moment and people that normally run it, with Governance as the main group when its default purpose is control evidence. The same technique run for another purpose is a named variation, not a second main group. This catalogue is the only source of the classification; tables elsewhere MUST mirror it and this policy prevails. New test types MUST be added here with a main group.

| Main group | Test types | Common variations |
|---|---|---|
| Development | unit, code-level integration, contract, static analysis and dependency scan, code-level and AI `smoke`, cross-team integration and E2E in `tst`, AI `functional`, `prompt`, `repeatability`, `groundedness`; performance (baseline, load, stress, spike, soak), engineering-owned and run mainly in `acc` | Performance also as developer micro-benchmark, as Governance evidence when a regulation or contract sets the threshold, and as a latency watch on the canary (Production); `functional` re-run in `acc` as Governance evidence |
| Governance | AI `safety`, `adversarial`, `fairness`, `bias`, `robustness`, `explainability`; security (DAST, penetration); accessibility; privacy and data-protection conformity; resilience and disaster recovery; post-market monitoring | Developers run Governance AI evals and accessibility linters in CI; post-market monitoring runs continuously in `prd` |
| Business | business acceptance scenarios, end-to-end user journeys in `acc`, operational acceptance (deploy and rollback rehearsal, runbooks, alerts), usability, data-migration rehearsal | Usability with real users during beta (Production) |
| Production | post-deploy smoke and synthetic probes, alpha, beta, canary and progressive rollout, blue/green verification, shadow traffic and dark launch, A/B, production performance baseline with guardrails, continuous technical monitoring (drift, latency, errors) | Offline eval before an A/B launch is Development |

This policy classifies types; it does not require them. Security, accessibility, privacy and resilience tests are mandatory only when another policy, a regulation or a contract requires them. Performance in `prd` follows [agentme-edr-306](../platform/306-performance-testing.md) rule `04`; its prohibitions on spike, stress and resilience in `prd` remain.

#### 08-how-each-group-runs

Group Development runs through the standard Makefile targets of [agentme-edr-303](../platform/303-common-targets.md): `lint`, `test-unit`, `test-integration`, `test-smoke`, `eval-<qualifier>` and `test-performance-<kind>`. AI evals of any group MUST follow the mocking constraint of [agentme-edr-152](../application/152-ai-test-types-taxonomy.md) rules `03` and `08`. Governance and Business runs SHOULD reuse the same targets against `acc`, parameterised by `STAGE`, and keep their outputs as the evidence of rule `01`. Production tests run through the rollout plan of rule `05`.

## Conflicts

No conflict with existing policies. [agentme-edr-501](501-project-quality-standards.md) rule `09` hard stops are kept intact (rules `03` and `06`). [agentme-edr-306](../platform/306-performance-testing.md) rule `04` still places performance runs mainly in `acc`; this policy classifies them as group Development by objective, not by environment.

## References

- [agentme-edr-152 - AI test types taxonomy](../application/152-ai-test-types-taxonomy.md)
- [agentme-edr-157 - AI A/B testing](../application/157-ai-a-b-testing.md)
- [agentme-edr-158 - AI performance testing](../application/158-ai-performance-testing.md)
- [agentme-edr-303 - Common targets](../platform/303-common-targets.md)
- [agentme-edr-306 - Performance testing](../platform/306-performance-testing.md)
- [agentme-edr-407 - A/B testing in production](../operations/407-a-b-testing-in-production.md)
- [agentme-edr-501 - Project quality standards](501-project-quality-standards.md)
- [agentme-adr-301 - Computational environments](../../adrs/platform/301-computational-environments.md)
- [agentme-bdr-405 - Digital product roles RACI](../../bdrs/operations/405-digital-product-roles-raci.md)
