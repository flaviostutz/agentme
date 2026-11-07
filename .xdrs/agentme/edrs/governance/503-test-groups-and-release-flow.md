---
name: agentme-edr-policy-503-test-groups-and-release-flow
description: Defines four test groups, objective-based test types, General/AI-focused affinity, reusable techniques and release gates. Use when selecting tests, distinguishing objectives from methods, or making the UAT go/no-go decision.
apply-to: Software projects that plan, run or discuss tests across the delivery flow, including AI systems
valid-from: 2026-10-30
---

# agentme-edr-policy-503: Test groups and release flow

## Context and Problem Statement

Test objectives, techniques, levels and rollout stages are often mixed together. How should software and AI tests be classified by the outcome they assess, and how does their evidence support the release decision?

## Decision Outcome

**Organize testing as Group -> objective-based Type -> reusable Technique, across Development, Governance, Business and Production.**

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

A test belongs to group Governance only when its pass/fail criteria come from a law, regulation, standard, contract or internal control and its evidence is retained for audit; any other purpose belongs to another group. Group Business distinguishes Quality, Operational readiness and User Acceptance Testing (UAT), rather than calling every Business test UAT. Personal-data rules per group are decided by each project under its own data-protection policies; this policy only states the data quality expected from each group.

#### 02-flow-and-gates

The flow is: group Development CI gate, deploy to `acc`, then group Governance, group Business and the group Development performance runs in parallel, then one release decision, then group Production. All three parallel tracks MUST finish before the release decision. A failed gate returns the build to group Development. A rollback or incident in `prd` also returns to group Development.

Each Governance control MUST declare a cadence: per release, or periodic (for example an annual penetration test). Periodic evidence satisfies a release while it is within its declared validity period.

The Business gate in rule `04` with its risk impact analysis MUST be passed before any deploy to `prd`, including deploys with the feature flag off.

#### 03-governance-exceptions

A failed mandatory Governance control MUST block the release, unless the organisation's compliance/risk function records an exception with a reason and a due date to fix. The compliance/risk function sits outside the role roster of [agentme-bdr-402](../../bdrs/operations/402-digital-product-roles.md). Business approvers MUST NOT waive a Governance failure. Requirements of [agentme-edr-501](501-project-quality-standards.md) rule `09` that block a release MUST NOT be waived by this rule or by rule `06`.

#### 04-business-gate-is-recorded-risk-acceptance

UAT is the ultimate business go/no-go gate: the business knows the consequences of deploying, not that the software is perfect. It is the "Production readiness and go-live approval" of [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md): the Product Owner decides and the Tech Lead's opinion MUST be recorded. UAT MUST consider Quality, Operational readiness and other relevant evidence, including Governance results. The gate record MUST list those results, residual risks, what was not tested in `acc` and why (for example cost or impossible simulation), and the Production mitigation for each (slow rollout, flags, monitoring, alarms). Missing evidence MUST be made explicit, not treated as a pass. UAT does not waive the controls of rule `03`.

#### 05-production-rollout-plan

Production tests run under a rollout plan with alpha (internal users), beta (selected real users) and GA stages. Each stage MUST declare audience, deployment window, rollback scenario and test objective. The Business gate approves entry to the first stage; later stage moves follow the plan's criteria and are decided by the Product Owner. Rollback authority stays with the Tech Lead. A/B tests and blue/green follow [agentme-edr-407](../operations/407-a-b-testing-in-production.md); flag-only rollback MUST be rehearsed before launch per that policy.

#### 06-emergency-path

An emergency release (for example a security hotfix) MAY run a reduced Governance and Business scope. Every skipped test MUST be named in a risk record approved by the roles of rules `03` and `04`, with a due date set per case by which it runs; there is no default period. Skipping silently MUST NOT happen. Group Development tests and the requirements of [agentme-edr-501](501-project-quality-standards.md) rule `09` remain mandatory, apart from the A/B exemption that rule already grants.

#### 07-every-test-type-has-one-main-group

Every test type MUST describe an objective and the outcome or evidence it brings to the team, business or control function, independently of its technique. Each type MUST have one main group in this catalogue; tables elsewhere MUST mirror it. The main group reflects the usual purpose, moment and people, with Governance qualified by rule `01`. The same objective pursued in another group is a named purpose-specific variation, not a second main classification.

The catalogue is divided into rules `09` through `12`. It classifies types; it does not require them. Techniques are non-exhaustive options, reusable across types, not mandatory or exclusive implementations. General / AI-focused is descriptive affinity, not an applicability restriction; General types apply to AI systems too.

Unit, integration and E2E are levels/scopes, not objective types. Contract checks, static analysis and dependency scans support correctness or security objectives. Alpha/beta/GA are rollout stages; canary, blue/green and dark launch are deployment strategies whose checks gather evidence. A deployment strategy alone is not a test. Dataset labels and tools are execution interfaces, not the universal taxonomy; AI mappings are in [agentme-edr-152](../application/152-ai-test-types-taxonomy.md#05-test-type-taxonomy).

Examples of variations: developers run accessibility or AI control checks in CI; performance is mainly Development in `acc`, but can supply Governance threshold evidence or Production canary guardrails; usability with beta users supplies Production evidence; post-market monitoring supplies Governance evidence in `prd`. A rollback rehearsal can assess Operational readiness before release or Deployment verification under a rollout plan. Offline evals before A/B remain Development.

Security, accessibility, privacy and resilience tests are mandatory only when another policy, a regulation or a contract requires them. Performance in `prd` follows [agentme-edr-306](../platform/306-performance-testing.md) rule `04`; its prohibitions on spike, stress and resilience in `prd` remain.

#### 08-how-each-group-runs

Group Development runs through the standard Makefile targets of [agentme-edr-303](../platform/303-common-targets.md): `lint`, `test-unit`, `test-integration`, `test-smoke`, `eval-<qualifier>` and `test-performance-<kind>`. AI evals of any group MUST follow the mocking constraint of [agentme-edr-152](../application/152-ai-test-types-taxonomy.md) rules `03` and `08`. Governance and Business runs SHOULD reuse the same targets against `acc`, parameterised by `STAGE`, and keep their outputs as the evidence of rule `01`. Production tests run through the rollout plan of rule `05`.

#### 09-development-objectives

The following types MUST be classified primarily in group Development, subject to rule `07`'s purpose-specific variations.

| Main group | Test type | Outcome assessed / value | AI affinity | Common techniques |
|---|---|---|---|---|
| Development | Functional correctness | Required logic and interface behavior works | General | Scenario assertions, contract checks |
| Development | Accuracy | Model outputs meet task-quality criteria across representative inputs, with uncertainty considered | AI-focused | Golden-dataset evaluation, task rubrics, statistical evaluation |
| Development | Regression protection | Changes preserve required existing behavior | General | Suite replay, baseline comparison |
| Development | Smoke | Essential behavior works sufficiently to proceed | General | Small critical-scenario suite |
| Development | Performance | Speed, capacity, error and resource limits hold | General | Baseline, load, stress, spike, soak |
| Development | Groundedness | Claims are supported by supplied sources | AI-focused | Source-attribution checks, claim-to-context checks |
| Development | Repeatability | Equivalent repeated requests remain sufficiently consistent | AI-focused | Repeated-run semantic comparison |

#### 10-governance-objectives

The following types MUST be classified primarily in group Governance when their purpose meets rule `01`'s control-and-evidence qualification.

| Main group | Test type | Outcome assessed / value | AI affinity | Common techniques |
|---|---|---|---|---|
| Governance | Security assurance | Declared security controls withstand relevant threats | General | Penetration testing, dynamic application security testing (DAST) |
| Governance | Safety | Harmful-output and unsafe-action constraints hold | AI-focused | Policy scenarios, red-team exercises |
| Governance | Adversarial resistance | Malicious inputs cannot bypass declared controls | AI-focused | Prompt-injection exercises, jailbreak exercises |
| Governance | Fairness | Legitimate segments receive intended policy outcomes | AI-focused | Segment-based scenario evaluation |
| Governance | Bias / non-discrimination | Protected attributes do not cause prohibited outcome differences | AI-focused | Paired counterfactual comparison |
| Governance | Robustness | Variable or unexpected inputs preserve required behavior | General | Input perturbation, boundary scenarios |
| Governance | Explainability | Explanations faithfully support assessed outcomes | AI-focused | Rationale review, fidelity checks |
| Governance | Accessibility | People with disabilities can access required functions | General | Automated checks, keyboard and screen-reader testing |
| Governance | Privacy / data protection | Declared processing and access controls hold | General | Access-control checks, retention checks |
| Governance | Resilience / recovery | Required continuity and recovery controls hold | General | Failover drills, backup-restore exercises |

#### 11-business-objectives

The following types MUST be classified primarily in group Business.

| Main group | Test type | Outcome assessed / value | AI affinity | Common techniques |
|---|---|---|---|---|
| Business | Quality | Product fits intended business use and agreed functional and user-experience requirements | General | Usability tests, functional-requirement suite replay, business journeys |
| Business | Operational readiness | Business and technical operations can run the changed service | General | Training-effectiveness checks, procedure rehearsals, communication exercises, rollback rehearsal, incident simulation, runbook exercise, alert verification |
| Business | UAT | Business knows deployment consequences and records go/no-go | General | Evidence review, risk-impact walkthrough, decision/sign-off session |

Quality is business fitness, not an umbrella replacing every other type. Operational readiness includes business operators and support functions: people can perform changed duties, new procedures work in rehearsal, and communications reach and are understood by relevant people. Attendance or a sent message alone does not demonstrate capability. Data-migration rehearsal can support Quality and readiness; UAT considers its consequences.

#### 12-production-objectives

The following types MUST be classified primarily in group Production, under the rollout plan of rule `05`.

| Main group | Test type | Outcome assessed / value | AI affinity | Common techniques |
|---|---|---|---|---|
| Production | Deployment verification | Released deployment, routing and rollback work in production | General | Blue/green verification, canary checks, post-deploy smoke, shadow comparisons |
| Production | Live outcome validation | Real-user outcomes support a version-selection decision | General | A/B experimentation |
| Production | Production reliability | Required service behavior holds during real operation | General | Synthetic transactions, service-level checks, drift/latency/error monitoring |

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
