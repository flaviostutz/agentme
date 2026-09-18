---
name: agentme-edr-policy-402-dora-metrics-framework
description: Defines the framework for measuring DORA's four software delivery metrics per team and service, including sub-metric composition, maturity-tier definition, distribution reporting, adoption order, and daily usage by role. Use when implementing or reviewing DORA metrics measurement, dashboards, or reporting.
apply-to: Teams and organizations measuring, reporting, or improving software delivery performance using DORA's four key metrics
valid-from: 2026-09-18
---

# agentme-edr-policy-402: DORA metrics framework

## Context and Problem Statement

Teams need objective signals of software delivery performance, but without a shared framework, teams measure different things, blend unlike services together, or reduce delivery health to one misleading number. How should DORA's four key metrics be scoped, combined into a maturity signal, and used across teams so results stay comparable, actionable, and resistant to gaming?

## Decision Outcome

**Adopt DORA's four key metrics, each measured per service and rolled up per team, decomposed into incrementally-adoptable sub-metrics defined in one companion policy per metric.**

Every team gets a maturity tier per metric plus one blended tier; company-wide reporting always shows a tier distribution, never a company-wide average.

### Details

#### 01-four-key-metrics

This framework covers DORA's four key metrics: Deployment Frequency ([agentme-edr-403](403-dora-deployment-frequency.md)), Lead Time for Changes ([agentme-edr-404](404-dora-lead-time-for-changes.md)), Change Failure Rate ([agentme-edr-405](405-dora-change-failure-rate.md)), and Time to Restore Service ([agentme-edr-406](406-dora-time-to-restore-service.md); DORA's current term is "Failed Deployment Recovery Time"). Sub-metrics MUST follow a hybrid composition model: Lead Time and Time to Restore sub-metrics are additive and sum to the parent value, while Deployment Frequency and Change Failure Rate sub-metrics are complementary signals that MUST NOT be summed. All time-based sub-metrics MUST use the median (p50) as the headline statistic instead of the mean, to resist outlier skew; percentile bands (p85/p95) MAY be added for distribution visibility.

#### 02-per-service-and-team-accounting

Every metric and sub-metric MUST be measured and reported per team, never only as an org-wide aggregate. The atomic unit of attribution MUST be the deployable service, not the team directly: a team's figures MUST be a rollup of its owned services, per [agentme-bdr-402](../../bdrs/operations/402-digital-product-roles.md)'s `01-product-team-purpose`/`02-product-team-scope-of-work` (a team owns its product's full lifecycle end-to-end). A change touching multiple services MUST be measured independently against each affected service's own timeline; it MUST NOT be flagged as cross-team or assigned to one majority owner.

#### 03-artifact-to-service-mapping

Code-path-based artifacts (pull requests, commits, deploy-workflow runs) MUST be attributed to a service using the repository's CODEOWNERS file, with path patterns defined at service-directory granularity. CODEOWNERS MUST NOT be used for GH Issues, since issues have no file path; issue-based sub-metrics MUST instead use an explicit label or component convention (for example a `service:<name>` label) cross-walked to the owning service.

#### 04-cross-team-incident-attribution

When an incident's root cause is traced to a different team's change, it MUST be counted against the root-cause team's Change Failure Rate ([agentme-edr-405](405-dora-change-failure-rate.md)) and, separately, tagged as a non-tiered visibility signal for the impacted team. It MUST NOT be double-counted into the impacted team's own numerator. Root-cause determination MUST follow [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md)'s `04-accountability-network-and-root-cause-tracing` methodology rather than a separate one defined here.

#### 05-maturity-level-definition

Each team MUST be assigned a named maturity tier (Elite, High, Medium, or Low, per DORA's current published bands, cited and dated rather than hardcoded here) for each of the four metrics. Each team MUST also receive one blended maturity label equal to the floor (worst) of its four per-metric tiers. This floor combination is this framework's own practical proxy, since DORA does not publish an official per-team combination formula; it is grounded in DORA's own finding that top performers tend to do well across all metrics. A Low tier on a metric with a genuine regulatory floor MUST NOT be treated as an excuse to stop improving the rest of that metric or any other metric within the team's control.

#### 06-maturity-level-distribution-reporting

Maturity level MUST NOT be averaged across teams into one company-wide figure. Company-wide reporting MUST show the percentage of teams at each blended tier as the headline view, with the four per-metric tier distributions available as a supporting drill-down. Distributions MUST NOT be used to rank or compete teams against each other, and individual team results MUST NOT be reported in a way that isolates one team's metrics from the others' — both patterns are documented by DORA as pitfalls that fuel finger-pointing and gaming.

#### 07-adoption-order

Teams SHOULD adopt the four metrics in this order: Deployment Frequency, then Lead Time for Changes, then Change Failure Rate, then Time to Restore Service. Each step needs one more data source or organizational capability than the last (deploy-workflow history only; then PR data; then a failure-labeling convention; then incident-management timestamps), and DORA's research shows that improving batch size and frequency first cascades into better lead time and stability. Each companion policy defines its own internal sub-metric adoption order using the same ease-plus-impact rationale.

#### 08-daily-usage-by-role

Roles SHOULD consult these metrics at the cadence below when carrying out their accountabilities as defined in [agentme-bdr-402](../../bdrs/operations/402-digital-product-roles.md), [agentme-bdr-404](../../bdrs/operations/404-team-roles-and-specialists.md), and [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md):

| Role | Cadence | Usage |
|---|---|---|
| Tech Lead / AI Lead | Daily | Primary consumer; accountable for CI/CD pipeline health and incident response; reads review latency ([agentme-edr-404](404-dora-lead-time-for-changes.md) `02`) jointly with Change Failure Rate to catch rubber-stamping |
| PO | Weekly | Reads Deployment Frequency and Lead Time alongside Change Failure Rate before go-live approvals |
| EM | Weekly/quarterly | Cross-checks a sustained Low tier against the team's `agentme-bdr-402` `03-workforce-allocation` operations-and-controls capacity |
| PjM | As-needed | Investigates cross-team blockers when Lead Time or Change Failure Rate issues trace to cross-team dependencies |
| PM / Leadership | Quarterly | Reads the tier distribution from rule `06`, never a company-wide average |

## Considered Options

* (REJECTED) **Single composite delivery score** — blend all four metrics into one number
  * Reason: Hides which metric needs attention; contradicts DORA's own guidance against "one metric to rule them all"
* (REJECTED) **Company-wide averaged maturity score** — one blended number across all teams
  * Reason: Masks teams that need help; contradicts DORA's guidance against disparate comparisons and siloed competition
* (REJECTED) **Strict-composition redesign for Deployment Frequency and Change Failure Rate** — force all sub-metrics to sum to the parent value
  * Reason: Would require dropping batch size (an orthogonal dimension) and escaped-defect-rate (different attribution lag) to force a clean sum

## References

- [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)
- [agentme-edr-403](403-dora-deployment-frequency.md) — Deployment Frequency
- [agentme-edr-404](404-dora-lead-time-for-changes.md) — Lead Time for Changes
- [agentme-edr-405](405-dora-change-failure-rate.md) — Change Failure Rate
- [agentme-edr-406](406-dora-time-to-restore-service.md) — Time to Restore Service
- [agentme-edr-401](401-service-health-check-endpoint.md) — Service health check endpoint
- [agentme-edr-302](../platform/302-github-pipelines.md) — GitHub CI/CD pipelines
- [agentme-bdr-402](../../bdrs/operations/402-digital-product-roles.md) — Digital product roles: org & cross-team
- [agentme-bdr-404](../../bdrs/operations/404-team-roles-and-specialists.md) — Digital product roles: team & specialists
- [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md) — Digital product roles: RACI
