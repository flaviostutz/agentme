---
name: agentme-edr-policy-404-dora-lead-time-for-changes
description: Defines calculation, examples, and challenges for DORA's Lead Time for Changes metric and its PR-cycle-time, review-latency, deploy-pipeline-time, and total-lead-time sub-metrics. Use when instrumenting or reviewing lead time measurement.
apply-to: Teams and organizations measuring, reporting, or improving software delivery performance using DORA's four key metrics
valid-from: 2026-09-18
---

# agentme-edr-policy-404: DORA lead time for changes

## Context and Problem Statement

Lead Time for Changes is often reduced to one number that hides whether delay lives in review or in deployment. How should its phases be calculated so a team can see where time is actually spent, and how do the phases combine into a total?

## Decision Outcome

**Measure four additive sub-metrics per deployable service that sum to a total lead time, using the median (p50) as the headline statistic.**

Review latency is a phase inside PR cycle time; PR cycle time plus deploy-pipeline time MUST equal total lead time.

### Details

#### 01-pr-cycle-time

PR cycle time MUST be measured from a PR's first commit to its `merged_at` timestamp. Example: first commit at day 0, merged at day 2 gives a 2-day PR cycle time. Challenges: squash-merge loses the first-commit timestamp, so the PR's `created_at` SHOULD be used as a proxy; stacked PRs and long-lived branches with rebases distort the start time. Teams SHOULD adopt this first, since it uses a single data source (GitHub PRs) and is usually the dominant contributor to total lead time.

#### 02-review-latency

Review latency MUST be measured from a PR's `created_at` to its first review `submitted_at`, as a drill-down inside `01`. Example: PR opened at hour 0, first review at hour 20, gives 20 hours of review latency. Challenges: this is the sub-metric most at risk of being gamed by rubber-stamping; an unusually fast review latency MUST be read jointly with [agentme-edr-405](405-dora-change-failure-rate.md)'s Change Failure Rate rather than treated as a win on its own. Teams SHOULD adopt this second: it reuses `01`'s data source with one extra timestamp, and is usually the most common, most actionable bottleneck.

#### 03-deploy-pipeline-time

Deploy-pipeline time MUST be measured from merge to deploy completion for the affected service, covering any merge-to-deploy gate whether automated or manual (including mandatory regulatory or QA approval gates). Example: merged at hour 0, service deployed at hour 6, gives 6 hours of deploy-pipeline time. Challenges: a PR shipping to multiple services MUST have this computed once per affected service, since deploy timing differs by service; flaky CI re-runs inflate the measurement. Teams SHOULD adopt this third: it requires a second data source (deploy-workflow runs) correlated with PR data, and isolates exactly how much delay sits outside the team's own review process.

#### 04-total-lead-time

Total lead time MUST equal `01` plus `03` (with `02` already counted inside `01`), computed once per PR-and-affected-service pair and rolled up per team. Example: 2-day PR cycle time plus 6-hour deploy-pipeline time gives a total of roughly 2.25 days. Challenges: a handful of extreme outliers can skew a mean, which is why the median MUST be the headline statistic. Teams SHOULD adopt this last: it requires correlating both data sources together, the hardest sub-metric to compute reliably, but it is the single clearest measure of overall delivery speed.

## References

- [agentme-edr-402](402-dora-metrics-framework.md) — DORA metrics framework
- [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)
