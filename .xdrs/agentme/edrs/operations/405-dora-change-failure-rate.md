---
name: agentme-edr-policy-405-dora-change-failure-rate
description: Defines calculation, examples, and challenges for DORA's Change Failure Rate metric and its hotfix/revert-rate, incident-linked-deploy-rate, and escaped-defect-rate sub-metrics, including cross-team root-cause attribution. Use when instrumenting or reviewing change failure rate measurement.
apply-to: Teams and organizations measuring, reporting, or improving software delivery performance using DORA's four key metrics
valid-from: 2026-09-18
---

# agentme-edr-policy-405: DORA change failure rate

## Context and Problem Statement

Failure shows up in different ways — an immediate rollback, an incident without a rollback, a defect found later — and no single detection method catches all of them. How should each be calculated, and how should a failure whose root cause spans multiple teams be attributed?

## Decision Outcome

**Measure three complementary, non-summing detection signals per deployable service, and attribute cross-team-caused incidents to both the root-cause team and the impacted team.**

The three sub-metrics MUST NOT be summed; a team MAY treat one as primary as it matures, but all three remain independent signals.

### Details

#### 01-hotfix-revert-rate

Hotfix/revert rate MUST be calculated by dividing PRs titled or labeled `revert` merged shortly after a deploy by total deploys for the service, using CODEOWNERS for attribution. Example: 2 reverts following 40 deploys gives a 5% hotfix/revert rate. Challenges: a hotfix that itself gets reverted MUST NOT be double-counted as two separate failures. Teams SHOULD adopt this first, since it catches the most severe, most obvious failures using a single data source.

#### 02-incident-linked-deploy-rate

Incident-linked deploy rate MUST be calculated by dividing GH Issues labeled `incident` that reference a deploy by total deploys for the service, using the issue-label/component convention from [agentme-edr-402](402-dora-metrics-framework.md)'s `03-artifact-to-service-mapping` (CODEOWNERS does not apply to Issues). Example: 3 incident-linked issues following 40 deploys gives 7.5%. Challenges: deploy-to-incident attribution lag, and label-discipline under-reporting when incidents go untagged. Teams SHOULD adopt this second: it reuses `01`'s deploy count with one additional label convention, and catches real failures that did not need a rollback but still affected users.

#### 03-escaped-defect-rate

Escaped defect rate MUST be calculated by dividing GH Issues labeled `bug` and `production`, opened after a release and attributed to the service, by total deploys. Example: 4 escaped defects following 40 deploys gives 10%. Challenges: attribution lag across period boundaries when a defect surfaces well after the causing deploy. Teams SHOULD adopt this third: it reuses the same issue-label convention as `02`, and catches slower-to-surface failures the first two signals miss.

#### 04-cross-team-and-shared-root-cause-attribution

When an incident's root cause is a different team's change, it MUST be counted against the root-cause team's numerator here, per [agentme-edr-402](402-dora-metrics-framework.md)'s `04-cross-team-incident-attribution`; the impacted team MUST instead receive a separate, non-tiered visibility tag rather than a numerator hit. An incident traced to one shared root cause but manifesting across several teams' trackers MUST be linked to a single root-cause record and MUST NOT be counted independently as multiple failures.

## References

- [agentme-edr-402](402-dora-metrics-framework.md) — DORA metrics framework
- [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md) — Digital product roles: RACI (root-cause tracing methodology)
- [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)
