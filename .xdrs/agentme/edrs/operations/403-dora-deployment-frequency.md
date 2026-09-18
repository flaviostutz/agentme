---
name: agentme-edr-policy-403-dora-deployment-frequency
description: Defines calculation, examples, and challenges for DORA's Deployment Frequency metric and its deploys-per-week, batch-size, and automation-ratio sub-metrics. Use when instrumenting or reviewing deployment frequency measurement.
apply-to: Teams and organizations measuring, reporting, or improving software delivery performance using DORA's four key metrics
valid-from: 2026-09-18
---

# agentme-edr-policy-403: DORA deployment frequency

## Context and Problem Statement

Deployment Frequency is the easiest of DORA's four metrics to start measuring, but teams need a concrete, per-service calculation method rather than just the concept. How should deploys-per-week, batch size, and automation ratio be calculated, and in what order should a team adopt them?

## Decision Outcome

**Measure three complementary, non-summing sub-metrics per deployable service, adopted in order of increasing data-source complexity.**

Each sub-metric MUST be scoped per [agentme-edr-402](402-dora-metrics-framework.md)'s `02-per-service-and-team-accounting` and rolled up per team; none of the three sum to a single formula.

### Details

#### 01-deploys-per-week

Deploys-per-week MUST be calculated by counting successful deploy-workflow runs on the service's default or release branch per week, using CODEOWNERS to attribute each run to its service. Example: a service with 12 successful deploy runs over 4 weeks has a Deployment Frequency of 3/week. Challenges: a change touching multiple services MUST be counted independently against each service's own timeline; the measurement window MUST span the service's own release-train or freeze-window cadence rather than a fixed calendar snapshot; "one deploy event" for canary, staged, or multi-region rollouts MUST be defined consistently per service (for example, pipeline-run start); re-run or retry executions of the same release MUST NOT inflate the count. This is the first sub-metric to adopt: it needs only deploy-workflow history as a single data source, and gives the fastest, most direct throughput signal.

#### 02-batch-size

Batch size MUST be calculated by counting commits or PRs merged between two consecutive deploys of the same service. Example: 8 PRs merged between deploy N and deploy N+1 gives a batch size of 8. Challenges: squash-merge collapses commit history, so the count MUST be based on merged PRs rather than raw commits. Teams SHOULD adopt this second: it needs no data source beyond `01`'s deploy history, and is a leading indicator for both Lead Time and Change Failure Rate risk (see [agentme-edr-402](402-dora-metrics-framework.md)'s `07-adoption-order`).

#### 03-automation-ratio

Automation ratio MUST be calculated by dividing automated deploy-workflow runs (triggered by merge, tag, or schedule) by all deploy-workflow runs for the service. Example: 18 automated of 20 total runs gives a 90% automation ratio. Challenges: a mandatory regulatory or manual QA approval gate MUST NOT be conflated with an ad-hoc manual deploy; only the latter counts against automation ratio. Teams SHOULD adopt this third, since it requires classifying trigger type per run and is most useful once volume and batch size are already understood.

## References

- [agentme-edr-402](402-dora-metrics-framework.md) — DORA metrics framework
- [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)
