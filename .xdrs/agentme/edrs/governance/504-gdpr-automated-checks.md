---
name: agentme-edr-policy-504-gdpr-automated-checks
description: Defines the deterministic GDPR declaration check, the full GDPR audit before release, finding severities and the review-gdpr skill that performs them. Use when verifying that an application complies with agentme GDPR policies or wiring the check into CI.
apply-to: Applications following agentme, before release and on changes to personal data, hub policies or runbooks
valid-from: 2026-11-23
---

# agentme-edr-policy-504: GDPR automated checks

## Context and Problem Statement

GDPR rules are only useful if compliance is verified the same way every time. Some checks are deterministic (a declaration exists and is current), others need judgement (is this consent flow valid?).

Question: How is GDPR compliance verified, how are findings ranked and when must verification run?

## Decision Outcome

**Applications MUST pass a deterministic declaration check and a full audit with the `review-gdpr` skill before release, and findings follow fixed severities**

The skill is [review-gdpr](skills/review-gdpr/SKILL.md). The declaration contract it checks is defined only in [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md). Nothing here is legal advice and a clean report is not a compliance certificate.

### Details

#### 01-declaration-check

The `check` command of the skill scripts validates the hub policy offline and deterministically: the hub exists once, opt-out or applicable form is well-formed, every item has a resolving pointer or a valid reasoned not-applicable, review dates are current, and an opt-out has no other `gdpr-*` policy beside it. It exits non-zero on any error. Applications MUST run it, or the full audit, before each release. Wiring it into CI is OPTIONAL and decided by each application; CI is the recommended way to run it.

#### 02-full-audit

The skill's full audit reads the application and its documents, judges them against the agentme GDPR policies, and reports findings. It MUST be run before release when the application's data, consent flows, processors or runbooks changed since the last audit, and SHOULD be run at least yearly otherwise. It is read-only and MUST NOT open data files that may contain personal data without the human's approval of each file.

#### 03-severities

- **ERROR**: a missing, invalid, expired or contradicted hub or item; a missing mandatory item; a technical violation of a MUST rule in the GDPR policies.
- **WARNING**: a present pointer whose target cannot be verified (external URL, access denied), a SHOULD violation, or evidence too weak to judge.

Each finding MUST give the location, the policy reference using `policy-name.NN-rule-title`, why it matters, and a proposed fix. Missing declarations MAY come with a proposed draft, which the skill MUST NOT create without the human's approval.

#### 04-report

The report is shown in chat and saved to `.tmp/review-gdpr/<id>/report.md`. Matched personal data values MUST be redacted to type and location in every output.

#### 05-single-item-list

The script's item list MUST equal the table in [agentme-adr-policy-501](../../adrs/governance/501-gdpr-applicability-and-declarations.md) rule 06; the script's tests MUST fail when they differ.

## References

- [review-gdpr skill](skills/review-gdpr/SKILL.md)
- [agentme-edr-005 - Skill scripts and composition](../principles/005-skill-scripts-and-composition.md)
