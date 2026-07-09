---
name: agentme-edr-policy-502-contributing-guide-requirements
description: Defines the minimum contributor workflow guidance required in root CONTRIBUTING.md files. Use when scaffolding or reviewing contribution processes.
apply-to: Projects with open-source contributions
valid-from: 2026-05-25
---

# agentme-edr-policy-502: Contributing guide requirements

## Context and Problem Statement

Projects often document contributor expectations inconsistently or only inside README files, PR templates, or tribal knowledge. That causes avoidable review churn, premature feature implementation, and unfocused pull requests.

What contributor workflow guidance must every project publish so contributors know how to report bugs, discuss features, and submit changes?

## Decision Outcome

**Every project MUST publish a root CONTRIBUTING.md with a small, explicit contribution workflow.**

Projects MUST keep a `CONTRIBUTING.md` file at the repository root. The file MUST explain where bugs, feature discussions, and code changes belong so contributors follow a predictable workflow before opening pull requests.

### Details

#### 01-contributing-md-is-required

Every project MUST have a root `CONTRIBUTING.md` file at the repository root. The file MUST explain where bugs, feature discussions, and code changes belong so contributors follow a predictable workflow before opening pull requests.

#### 02-guide-must-direct-bug-reports-to-issues

The guide MUST direct bug reports to issues.

#### 03-guide-must-route-feature-discussions-to-issues

The guide MUST direct feature ideas and feature discussions to issues before implementation starts.

#### 04-guide-must-require-pull-requests

The guide MUST state that fixes and features are contributed through pull requests.

#### 05-guide-must-require-feature-branches

The guide MUST state that pull requests come from feature branches targeting `main`.

#### 06-guide-must-require-conventional-comments

The guide MUST ask reviewers and contributors to use [Conventional Comments](https://conventionalcomments.org/) for review feedback.

#### 07-guide-must-ask-for-small-pull-requests

The guide MUST ask contributors to keep pull requests small enough to keep review and discussion focused.

#### 08-scaffolding-should-create-contributing-md

Project scaffolding skills SHOULD create the file by default when they initialize a repository.

#### 09-content-should-be-concise

The content SHOULD stay concise and practical; do not turn `CONTRIBUTING.md` into a duplicate of `README.md`.

## Considered Options

* (REJECTED) **Keep contribution rules implicit** - Rely on README text, issue templates, or maintainers explaining the workflow ad hoc.
  * Reason: Inconsistent contributor behavior and avoidable review overhead.
* (CHOSEN) **Require a dedicated CONTRIBUTING.md** - Publish a short, explicit contribution workflow in a predictable location.
  * Reason: Easy to discover, simple to scaffold, and clear enough for both humans and agents.

## References

- [agentme-edr-301 - Monorepo structure](../platform/301-monorepo-structure.md)
- [002-monorepo-setup skill](../platform/skills/002-monorepo-setup/SKILL.md)