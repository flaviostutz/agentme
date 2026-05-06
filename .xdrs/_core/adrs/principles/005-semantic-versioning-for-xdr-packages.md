---
name: _core-adr-005-semantic-versioning-for-xdr-packages
description: Defines how semantic versioning applies to XDR packages. Use when publishing or versioning a package containing XDRs, research, skills, or articles.
---

# _core-adr-005: Semantic versioning for XDR packages

## Context and Problem Statement

Teams consume XDR packages as reusable guidance, constraints, Research documents, skills, and articles. If package versions do not reflect the real impact of a release, upgrades become risky and teams lose trust in reuse.

Question: How should semantic versioning be used when publishing or versioning a package containing XDRs, Research documents, skills, and articles?

## Decision Outcome

**semantic versioning aligned with decision impact**

XDR packages must use semantic versioning so the package version communicates the expected upgrade impact on consuming teams and projects.

### Details

- Package versions MUST follow `MAJOR.MINOR.PATCH`.
- The published package version MUST represent the impact of the package as a whole, not only of a single changed file.
- If a release contains changes of different severities, the highest-impact change MUST define the version bump.
- When uncertainty exists between two levels, the safer and more explicit version bump SHOULD be chosen.

**MAJOR**
- Use a major bump for breaking changes.
- Use a major bump when an existing XDR changes meaning in a way that can require consuming teams to revisit architecture, governance, operations, or implementation decisions.
- Use a major bump when impactful concepts are introduced or changed in a way that materially alters how the package should be adopted or interpreted.
- Typical cases: removed or renamed XDRs that affect references, changed mandatory rules, changed conflict/override behavior, or changed guidance that invalidates previously compliant usage.

**MINOR**
- Use a minor bump for backward-compatible additions and new capabilities.
- Use a minor bump for new XDRs that do not break existing guidance.
- Use a minor bump for new or updated Research documents, articles, and skill changes that extend the package without requiring consumers to undo previous adoption work.
- Typical cases: new features, new optional guidance, new Research documents, new articles, expanded skills, or additive non-breaking decision coverage.

**PATCH**
- Use a patch bump for low-risk fixes and simple improvements.
- Use a patch bump for corrections that preserve the existing meaning and upgrade expectations of the package.
- Typical cases: typo fixes, broken links, wording clarifications, examples, simple additions, formatting fixes, and small consistency improvements.

- Teams publishing XDR packages SHOULD treat the version number as an upgrade contract.
- Consumers SHOULD be able to assume that patch upgrades are low risk, minor upgrades are additive, and major upgrades may require review or migration work.
- Release notes SHOULD explain the reason for the chosen bump, especially for major releases.

## References

- https://semver.org/
- [_core-adr-006 - Research standards](006-research-standards.md)
