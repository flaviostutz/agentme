---
name: agentme-edr-policy-406-dora-time-to-restore-service
description: Defines calculation, examples, and challenges for DORA's Time to Restore Service metric and its total-restore-time, detection-time, acknowledgement-time, and resolution-time sub-metrics, using GitHub Issues as the worked example. Use when instrumenting or reviewing incident restore-time measurement.
apply-to: Teams and organizations measuring, reporting, or improving software delivery performance using DORA's four key metrics
valid-from: 2026-09-18
---

# agentme-edr-policy-406: DORA time to restore service

## Context and Problem Statement

Restoring service after a failed deployment is DORA's safety-net metric (DORA's current term is "Failed Deployment Recovery Time"), but a single total-time figure hides whether delay lives in detection, response, or the fix itself. How should the total and its phases be calculated in a tool-agnostic way?

## Decision Outcome

**Measure a total restore time plus three additive phase sub-metrics per impacted service, using any incident-management tool with equivalent timestamps; GitHub Issues is the worked example.**

The total MUST be tracked standalone, and the three phases decompose it, always attributed to the impacted or owning service regardless of where the root cause is traced.

### Details

#### 01-total-restore-time

Total restore time MUST be measured from an incident's opened timestamp to its closed timestamp, attributed via the issue-label/component convention from [agentme-edr-402](402-dora-metrics-framework.md)'s `03-artifact-to-service-mapping` to the service that was down or degraded. Example: opened at 10:00, closed at 11:30, gives 90 minutes. Challenges: partial-vs-full restores and reopened incidents. Teams SHOULD adopt this first: it needs only two timestamps on one incident record, no extra tracked event, and gives an immediate, if coarse, restore-time signal.

#### 02-detection-time

Detection time MUST be measured from the underlying failure's occurrence to the incident's detected timestamp, a tracked event distinct from "opened." Example: failure at 10:00, detected at 10:05, gives 5 minutes. Challenges: without paging or monitoring, detection relies on user reports and is easy to under-track. Teams SHOULD adopt this second: it requires one additional tracked "detected" event, and exposes how much time is lost before anyone notices, a leading indicator for monitoring coverage gaps.

#### 03-acknowledgement-time

Acknowledgement time MUST be measured from detected to acknowledged or assigned. Example: detected at 10:05, acknowledged at 10:10, gives 5 minutes. Challenges: on-call handoff and timezone gaps. Teams SHOULD adopt this third: it requires one additional tracked "acknowledged" event, and exposes on-call responsiveness separately from the fix itself.

#### 04-resolution-time

Resolution time MUST be measured from acknowledged to actually-fixed, not merely issue-closed. Example: acknowledged at 10:10, fixed at 11:30, gives 80 minutes. Challenges: extensive or mandatory manual rollout testing can gate the fix itself, extending this phase. Rules `02`, `03`, and `04` MUST sum to the total measured in `01`. Teams SHOULD adopt this last: it requires a reliable "fixed" event, the hardest to track consistently, but it isolates how long the actual fix takes once someone is engaged.

## References

- [agentme-edr-402](402-dora-metrics-framework.md) — DORA metrics framework
- [agentme-bdr-405](../../bdrs/operations/405-digital-product-roles-raci.md) — Digital product roles: RACI (incident-response accountability)
- [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/)
