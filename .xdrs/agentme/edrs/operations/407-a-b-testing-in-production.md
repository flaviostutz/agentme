---
name: agentme-edr-policy-407-a-b-testing-in-production
description: Defines how to plan, run, stop and retire an A/B test in production for any software - plan fixed before launch, sticky random audience split, feature-flag control, version tags in logs, flag-only rollback and dated cleanup. Use when two versions of a system will run side by side for real users to compare results.
apply-to: Any software system whose versions are compared by running two of them side by side in production for real users or clients
valid-from: 2026-10-14
---

# agentme-edr-policy-407: A/B testing in production

## Context and Problem Statement

Offline tests cannot reproduce the diversity of real usage. Without a shared way to run two versions side by side for real users, experiments are unplanned, hard to read, and leave extra versions running forever.

Question: How must a team plan, run, stop and retire an A/B test in production?

## Decision Outcome

**Time-boxed A/B tests with a plan fixed before launch, controlled by a feature flag.**

An A/B test shows version A (control, the stable one) and version B (variant) of the same system to different groups of real users, then compares measured results to decide which version stays. A/B tests are optional unless another Policy mandates them; once a team runs one, every rule below MUST be followed. For AI components see [agentme-edr-157](../application/157-ai-a-b-testing.md), which extends this Policy; when A/B is mandatory see [agentme-edr-501](../governance/501-project-quality-standards.md) rule `09-ai-project-testing-requirements`.

### Details

#### 01-plan-must-be-defined-before-launch

Before launch the team MUST write down, in any place it chooses (README, issue, pull request):

- target metrics: the measures that decide which version is better;
- operational metrics: at least errors, latency and cost per request;
- duration: long enough for the metrics to converge;
- audience and split, per rule `02-audience-must-be-defined-and-split-random-and-sticky`;
- winning rule: the difference in target metrics that makes B the winner, and the limits operational metrics MUST NOT cross.

When the experiment ends the team MUST record the outcome (B wins, A wins or inconclusive) next to the plan. An inconclusive outcome keeps A as the version in operation, B and its flag MUST be removed, and the team MAY run a longer experiment.

#### 02-audience-must-be-defined-and-split-random-and-sticky

The plan MUST state who may receive B (for example internal staff only, a percentage of all users, or beta opt-in users) and the assignment unit (user, account or session). Inside that audience, assignment MUST be random and sticky: the same unit MUST keep the same variant for the whole experiment, and a conversation or run MUST NOT switch variant midway.

The default split MUST be 50/50 so both groups have a similar sample size. An unbalanced split (for example 90/10) MAY be used to roll a new version out while watching it; the plan MUST then state that the analysis error is larger and the duration MUST be long enough for the smaller group to gather enough samples.

#### 03-feature-flag-must-control-the-experiment

Audience, ratio and kill switch MUST be controlled by a feature flag mechanism; the tool is the team's choice. The flag MUST serve the stable version A when the flag service is unreachable. Flag edits MUST be limited to named roles and MUST leave an audit trail.

#### 04-one-experiment-per-component-with-frozen-split

A component MUST have at most one active experiment. The audience and split MUST NOT change after launch; changing them starts a new experiment with a new analysis window.

#### 05-logs-must-carry-version-and-experiment

Every log produced by the system under test MUST include the component version (container image tag, release or equivalent that covers everything that can change behavior), the experiment id and the variant. When no experiment is active the fields MUST still be present, with the experiment id null and the variant `stable`.

```json
{"level":"info","experiment_id":"exp-2026-11-summarizer","variant":"B","component_version":"1.4.0","latency_ms":1840}
```

#### 06-stopping-must-be-fast-and-flag-only

Changing the flag alone MUST return all users to the stable version, with no redeploy. The team MUST rehearse this before launch and MUST document the rollback procedure, including which version is stable, in the README or another place operations can find during an emergency.

#### 07-experiment-must-be-time-boxed-and-cleaned-up

The team MUST discuss and decide the planned end date during planning; tooling does not need to enforce it. Only one version SHOULD stay in operation in the long run. Every variant branch and flag MUST carry a removal comment with a due date, so linters that read dated TODOs can flag expired ones, and the date MUST be updated when the experiment is extended:

```text
// TODO [2026-12-18]: Remove variant B and flag summarizer-v2-exp after experiment exp-2026-11-summarizer
```

After the decision the losing version's code, flag and deployment MUST be removed.

#### 08-versions-must-be-whole-deployments

A and B MUST be whole deployments of the component, each identified by one version. Switching internals (configuration, libraries, workflows or prompts) per request inside one deployment MUST be an exception, MAY be used only when whole deployments are not possible, and MUST have all of:

- a written justification in the README;
- approval by the Tech Lead (the AI Lead for AI components);
- a documented matrix of which internal combinations are tested and known to work together;
- one known-good combination to roll back to.

#### 09-experiment-data-must-be-minimal

Collected metrics and feedback MUST be limited to what the planned metrics need, and logs MUST NOT contain personally identifiable information.

#### 10-flag-logic-must-be-unit-tested

Assignment, stickiness, the default to A and the kill-switch path MUST be covered by offline unit tests with a mocked flag provider, per [agentme-edr-122](../application/122-unit-test-requirements.md). The A/B test itself runs on real production traffic with nothing mocked.

## References

- [agentme-edr-157](../application/157-ai-a-b-testing.md) - AI A/B testing, extends this Policy
- [agentme-edr-501](../governance/501-project-quality-standards.md) - Tier requirements that make A/B mandatory for AI components
- [agentme-edr-122](../application/122-unit-test-requirements.md) - Unit test requirements
- [agentme-edr-306](../platform/306-performance-testing.md) - Performance testing, which also covers prod guardrails
