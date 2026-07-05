# _core-adr-article-001: XDRS Overview

## Overview

This article introduces XDRS, explains its purpose and design, and guides
teams through adopting, extending, and distributing them. It is an entry point for anyone new to
the framework and links out to the authoritative Policy documents for full details.

## Content

### What the central elements are

The XDRS framework is built around a small set of artifact types that play different roles in the
same decision system.

A standard Decision Record normally combines several concerns in the same document: a reason
(why, options considered), a policy (rules, core decision), a plan (consequences, implementation
approach), a how-to (step-by-step procedure), and a view on a topic. The XDRS framework separates
these concerns into different document types: Policies as the source of truth, Research for
reasoning and evidence, Plans for implementation approach, Skills for execution procedures, and
Articles for topic overviews. Supporting artifacts may explain, justify, or operationalize the
policy, but they do not replace it. The compilation process of a raw Decision Record is to
distribute it into those different documents and create links between them. You can also use the
framework standalone, generating these elements individually directly during the writing process
without starting from a raw Decision Record.

- **Policies** are the authoritative decisions. They answer a concrete question and
  record the adopted direction. They are the central policy artifact of the framework for the
  scope and topic they cover. Three policy types exist: **ADR** for architectural and
  technical decisions, **BDR** for business and operational decisions, and **EDR** for engineering
  implementation decisions. See [_core-adr-policy-001](../001-xdrs-core.md).
- **Research** captures exploration before or around a decision: constraints, findings, options,
  pros, and cons. Research supports elaboration, discussion, and updates,
  but it is not the final rule. A single Research document may inform multiple downstream ADRs,
  BDRs, or EDRs. If Research and a Policy disagree, the Policy wins. See
  [_core-adr-policy-006](../006-research-standards.md).
- **Skills** describe how to execute work under the constraints of the decisions. They add the
  procedural detail that Policies intentionally avoid. A Skill may be used by a human, an AI agent, or
  both. Skills are task-based, should end in a verifiable outcome, and are only mandatory when a
  policy such as a Policy document makes them mandatory. See [_core-adr-policy-003](../003-skill-standards.md).
- **Articles** are synthetic views, like this one. They explain a topic across multiple Policies,
  Research documents, and Skills, helping readers understand the system without making new
  decisions. See [_core-adr-policy-004](../004-article-standards.md).
- **Plans** describe a problem, a proposed solution, and the approach and activities needed to
  solve it. They have a clear start and end and a well-defined scope. Plans are ephemeral: they
  must be deleted after full implementation, with lasting outputs captured as Policies, Skills,
  Articles, or other artifacts. See [_core-adr-policy-007](../007-plan-standards.md).
- **Indexes and folder structure** are the discovery layer. They do not make decisions by
  themselves, but they determine how people and agents find the right artifacts, how scopes
  override one another, and how a large set of decisions remains navigable.

### How they differ

The easiest way to distinguish the central elements is by asking what job each one performs.

- **Policy**: "What did we decide?"
- **Research**: "What did we learn while evaluating options?"
- **Skill**: "How do we carry out work under this decision?"
- **Article**: "How do these artifacts fit together for a reader?"
- **Plan**: "What are we going to do, why, and how?"
- **Index/Scope structure**: "Where do I look, and which decision set takes precedence?"

This separation matters because mixing these jobs into one file makes the system harder to search,
harder to update, and harder for agents to apply correctly.

### How to decide whether a Policy should be used

Before treating a Policy as a rule for the current case, check its metadata first. All documents present in the collection are considered active — if a document exists, it is current.

- **Valid first**: if present, the convergence date indicates when full adoption is expected. New implementations SHOULD adopt the decision immediately; compliance is not enforced during reviews until the date.
- **Applied to second**: if present, the current codebase, workflow, system, or audience must fit that scope.
- **Decision text last**: the Policy's own context and implementation details still determine the final boundaries and exceptions.
- **Then enforce**: only decisions that pass those checks should be used as active requirements. The rest may still be useful context.

Documents that are no longer relevant should be removed from the collection. Historical versions are available via versioned packages or git history.

### How they relate over time

The framework is easiest to understand as a lifecycle rather than a static folder tree.

1. **Explore** — A team starts with a problem, constraints, and uncertainty. Research is the best
  place to compare options, record findings, and keep tradeoffs visible. That same research may
  later support more than one decision record.
2. **Decide** — Once a direction is chosen, a Policy captures the final answer in concise,
  authoritative form. The Policy should make clear when the decision applies, and may link back to
  the Research that informed its considered options.
3. **Execute** — If the decision affects daily work, a Skill explains how to apply it in practice.
   The Skill operationalizes the decision without turning the Policy into a procedure manual.
4. **Explain** — When the topic becomes broad or cross-cutting, an Article synthesizes the Policy,
   Research, and Skills into a navigable explanation for humans and agents.
5. **Distribute and override** — Canonical indexes and scope ordering make the artifacts
   discoverable across teams. Broader scopes can be reused, and more specific scopes can extend or
   override them.

This gives Policies a timeline feel:

- Research usually appears before or around a decision.
- The Policy marks the adopted outcome.
- Skills appear when the decision must be executed repeatedly.
- Articles appear when the ecosystem around the decision needs explanation or onboarding support.

### How the structure supports the model

Every decision record and its supporting artifacts live at a fixed path:

```
.xdrs/
  [scope]/
    [type]/
      [subject]/
        [number]-[short-title].md
        researches/
          [number]-[short-title].md
        skills/
          [number]-[skill-name]/
            SKILL.md
        articles/
          [number]-[short-title].md
        plans/
          [number]-[short-title].md
```

- **Scopes** represent ownership domains such as `_core`, `business-x`, or `team-43`.
- **Types** are `adrs`, `bdrs`, or `edrs`.
- **Subjects** narrow the domain further, such as `principles`, `application`, or `finance`.
- **Canonical indexes** list the artifacts for each scope+type, while the root `.xdrs/index.md`
  defines precedence across scopes.

This organization keeps the authoritative decision, the supporting evidence, the implementation
guidance, and the explanatory overview close together without collapsing them into one document.

### Why this separation works

- **Small focused files** keep decisions readable and agent-friendly.
- **Research beside the Policy** preserves why options were accepted or rejected.
- **Skills beside the Policy** reduce drift between decisions and execution.
- **Articles above the artifacts** help readers understand the whole topic without replacing the
  source of truth.
- **Indexes and scopes** let the framework scale across teams while preserving override behavior.

### Getting started

1. Create or open a project workspace.
2. Run `npx xdrs-core` in the workspace root. This installs:
   - `AGENTS.md` — instructs AI agents to always consult XDRS.
   - `.xdrs/index.md` — root index (editable, `keepExisting` mode).
   - `_core` Policies, Research documents, and skills under `.xdrs/_core/`.
3. Start a conversation with your AI agent:
   > Create an ADR about our decision to use Python for AI projects.

### Guidelines

Follow [_core-adr-policy-001](../001-xdrs-core.md) and [_core-adr-policy-002](../002-policy-standards.md) strictly. Key rules:

- Use uppercase BCP 14 keywords: MUST/MUST NOT for non-negotiable rules, SHOULD/SHOULD NOT for strong recommendations, MAY/OPTIONAL for optional choices.
- Before citing a Policy as a requirement, check `Valid` first, then `Applied to`, and finally the decision text to confirm the decision is in scope for the current case.
- All documents present in the collection are considered active. Remove documents that are no longer relevant.
- Keep Policies under 1300 words as a rule of thumb (exceptions up to 2600 words for templates or more elaborate decisions). Move procedural detail to a co-located Skill.
- Keep exploratory option analysis in a co-located Research document instead of bloating the Policy.
- ALWAYS update the scope+type index and the root index after adding or changing a Policy.
- Use `_local` scope when a decision is project-specific and MUST NOT be shared.
- NEVER reuse a number once it has been assigned, even if the Policy is deleted.

### How to extend

- **New scope** — create `.xdrs/[scope]/[type]/index.md` and add it to `.xdrs/index.md`.
- **New subject** — create the subject folder under the existing scope+type path. Add an
  allowed subject or use `principles` if none fits (propose a new subject via a `_core` ADR).
- **New research** — add a `researches/[number]-[short-title].md` inside the relevant subject
  folder, following [_core-adr-policy-006](../006-research-standards.md).
- **New skill** — add a `skills/[number]-[skill-name]/SKILL.md` inside the relevant subject
  folder, following [_core-adr-policy-003](../003-skill-standards.md).
- **New article** — add an `articles/[number]-[short-title].md` inside the relevant subject
  folder, following [_core-adr-policy-004](../004-article-standards.md).
- **New plan** — add a `plans/[number]-[short-title].md` inside the relevant subject
  folder, following [_core-adr-policy-007](../007-plan-standards.md).

### Using XDRS in your own project

1. **Install** — add the scope package as a dependency and run `npx xdrs-core extract` (or
   `pnpm exec xdrs-core extract`) to unpack XDRS files into `.xdrs/` in your workspace.
2. **Pins and upgrades** — update the npm dependency version to pull in the latest decisions
   for a scope. The `filedist` mechanism tracks managed files in `.filedist.lock` and keeps
  `.xdrs/index.md` in `keepExisting` mode so local edits are preserved.
3. **Multi-scope** — list multiple scope packages as dependencies. Edit `.xdrs/index.md` to
   add each scope's canonical index link; place more specific scopes below broader ones.
4. **Verify** — run `npx xdrs-core check` to confirm all managed files are in sync with the
   installed packages.
5. **Distribute your own scope** — pack `.xdrs/[scope]/` with `pnpm pack` and publish to an
   npm registry (public or internal). Pin a tag for prerelease versions.

## References

- [Presentation slides](.assets/001-xdrs-overview-slides.md) - Marp slide deck overview of this article
- [_core-adr-policy-001](../001-xdrs-core.md) - XDRS elements: types, scopes, subjects, folder structure
- [_core-adr-policy-002](../002-policy-standards.md) - Policy document standards and mandatory template
- [_core-adr-policy-003](../003-skill-standards.md) - Skill standards and co-location rules
- [_core-adr-policy-004](../004-article-standards.md) - Article standards
- [_core-adr-policy-006](../006-research-standards.md) - Research standards
- [_core-adr-policy-007](../007-plan-standards.md) - Plan standards
- [001-review skill](../skills/001-review/SKILL.md) - Reviewing code against Policies
- [002-write-policy skill](../skills/002-write-policy/SKILL.md) - Writing a new Policy
- [003-write-skill skill](../skills/003-write-skill/SKILL.md) - Writing a new skill
- [004-write-article skill](../skills/004-write-article/SKILL.md) - Writing a new article
- [005-write-research skill](../skills/005-write-research/SKILL.md) - Writing a new research document
- [_core-adr-policy-005](../005-semantic-versioning-for-xdrs-packages.md) - Semantic versioning rules for XDRS packages
