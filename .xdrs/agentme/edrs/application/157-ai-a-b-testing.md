---
name: agentme-edr-policy-157-ai-a-b-testing
description: Extends agentme-edr-407 for AI components - quality, cost and latency metrics, duration for noisy output, offline eval gate before exposure, controlled first group for high-impact decisions, segment slicing and experiment fields in AI logs. Use when comparing two versions of an LLM, Agent or Workflow in production.
apply-to: AI components (LLM, Agent or Workflow tier) compared through an A/B test in production
valid-from: 2026-10-14
---

# agentme-edr-policy-157: AI A/B testing

## Context and Problem Statement

AI output is non-deterministic and a prompt, model or graph change can alter behavior in ways offline evals miss. Real usage is the only complete evidence of which version is better.

Question: What must an A/B test of an AI component add to the generic A/B Policy?

## Decision Outcome

**Run AI A/B tests under agentme-edr-407, adding AI-specific metrics, longer durations, an offline eval gate and a controlled first group for high-impact decisions.**

Every rule in [agentme-edr-407](../operations/407-a-b-testing-in-production.md) applies unchanged. A/B tests here are not evals: they use real production traffic and no golden dataset. [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09-ai-project-testing-requirements` defines when an A/B test is mandatory.

### Details

#### 01-metrics-must-cover-quality-cost-and-latency

The plan MUST define at least one quality metric from: an LLM-as-judge scoring sampled production traces (binary output per [agentme-edr-151](151-ai-eval-standards.md) rule `02-llm-as-judge-binary-output`), manual checks of sampled traces, or human positive/negative feedback from users. The operational metrics of [agentme-edr-407](../operations/407-a-b-testing-in-production.md) rule `01-plan-must-be-defined-before-launch` MUST include token cost per request and workflow or agent latency.

#### 02-duration-must-be-sized-for-noisy-output

AI output varies between identical requests, so the duration MUST be justified in the plan from daily request volume, the share of requests judged or reviewed, and the expected feedback rate. A low-volume service MUST plan weeks, not days (for example 120 requests per day needs about 6 weeks).

#### 03-offline-evals-must-pass-before-exposure

The evals the project's tier requires per [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09-ai-project-testing-requirements` MUST pass for version B before B receives any production traffic. An A/B test complements these evals and MUST NOT replace them.

#### 04-high-impact-decisions-need-a-controlled-first-group

When the component makes regulated or high-impact decisions, or takes irreversible actions, B MUST first run with a controlled group (employees, champions or beta users) that gives active feedback. B MUST NOT be opened to the full audience of [agentme-edr-407](../operations/407-a-b-testing-in-production.md) rule `02-audience-must-be-defined-and-split-random-and-sticky` until that group shows no blocking problem.

#### 05-results-should-be-sliced-by-listed-segments

The plan SHOULD list the segments to slice results by (for example language, customer type or channel). Protected attributes MAY be used for slicing only with a documented lawful basis, following [agentme-edr-156](156-ai-eval-fairness-bias.md).

#### 06-logs-and-tracking-must-carry-experiment-fields

The experiment id, variant and component version required by [agentme-edr-407](../operations/407-a-b-testing-in-production.md) rule `05-logs-must-carry-version-and-experiment` MUST be added to the existing JSON structured logs per [agentme-edr-143](143-ai-agents-quality-standards.md) rule `03-agent-observability`, and MUST be recorded as parameters in the experiment tracking of [agentme-edr-144](144-ai-workflow-development-standards.md) rule `03-observability-and-experiment-tracking`.

#### 07-internals-switching-must-be-documented

When rule `08-versions-must-be-whole-deployments` of [agentme-edr-407](../operations/407-a-b-testing-in-production.md) allows an exception for AI internals (prompt, model, parameters, tools, graph, retrieval data), the README MUST document the justification, the version matrix and the known-good rollback combination. Approval is by the AI Lead.

#### 08-experiment-plan-shape

Teams MAY use this shape for the plan, which fits in the README or an issue:

```text
Experiment: exp-2026-11-summarizer (A = 1.3.2, B = 1.4.0 with prompt v2)
Hypothesis: prompt v2 summarizes contracts more accurately
Target metrics: LLM-judge accuracy, thumbs-up rate
Operational metrics: tokens/request, p95 latency, error rate, cost/request
Audience: beta opt-in users, 50/50, sticky per user
Duration: 3 weeks (end date 2026-12-18)
Winning rule: accuracy +3 points and no operational metric worse by more than 10%
Rollback: set flag summarizer-v2-exp to off in the flag console; all users
return to 1.3.2 within the flag refresh interval, no deploy needed
```

## References

- [agentme-edr-407](../operations/407-a-b-testing-in-production.md) - Generic A/B testing in production, extended by this Policy
- [agentme-edr-501](../governance/501-project-quality-standards.md) - Rule 09 defines when A/B is mandatory and the offline eval gate
- [agentme-edr-151](151-ai-eval-standards.md) - LLM-as-judge binary output
- [agentme-edr-156](156-ai-eval-fairness-bias.md) - Fairness and protected attributes
- [agentme-edr-143](143-ai-agents-quality-standards.md) - Agent observability
- [agentme-edr-144](144-ai-workflow-development-standards.md) - Workflow observability and experiment tracking
- [agentme-edr-158](158-ai-performance-testing.md) - AI performance testing, an `acc` complement to A/B tests
