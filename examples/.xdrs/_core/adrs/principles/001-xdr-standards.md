# _core-adr-001: XDR standards

## Context and Problem Statement

We need a consistent way to capture decisions that scales across scopes and subjects, remains easy to navigate, and works well with AI agents.

Decision Records can be of different kinds, depending on the nature of the decision:
- BDR (Business Decision Record): Captures business process, product features, procedures and strategic decisions. Examples: business rules, product policies, customer service, business workflow, control frameworks for regulators for finance, product procedures and manuals, KYC requirements, business requirements in general
- ADR (Architectural Decision Record): Wider architectural and technical decisions. Examples: how big topics relate to each other, system contexts, overview without realy deciding on details, integration patterns, overarching topics, corporate wide practices, corporate systems, external and internal partners etc
- EDR (Engineering Decision Record): captures engineering details about how to implement things. Examples: specific tools and libraries selection, framework usage, best practices on coding, testing, quality, project structure, pipelines etc

Collectively, these are referred to as XDRs.

How should XDRs be structured and organized across types, teams, and scopes?

## Decision Outcome

**Scoped + typed + subject folders**

Provides clear ownership by scope, predictable navigation, and reusable decisions that work well with AI agents by keeping files small and focused.

### Implementation Details

- XDRs MUST contain a clear decision about a certain problem or situation. Avoid being too verbose and focus on explaining clearly the context and the decision. Avoid adding contents that are not original. If you have other references that are important to understand the document, add links and references.
- Make it clear if an instruction is mandatory or advisory
    - Mandatory language: "must", "always", "never", "required", "mandatory"
    - Advisory language: "should", "recommended", "advised", "preferably", "possibly", "optionally"
- Always the following folder structure:
  `.xdrs/[scope]/[type]/[subject]/[number]-[short-title].md`
- **Scopes:** 
  - examples: `business-x`, `business-y`, `team-43`, `_core`
  - `_local` is a reserved scope for XDRs created locally to a specific project or repository. XDRs in `_local` must not be shared with or propagated to other contexts. This scope must always be placed in the lowest position in `.xdrs/index.md` so that its decisions override or extend any decisions from all higher-positioned scopes.
  - **Types:** `adrs`, `bdrs`, `edrs`
  - there can exist sufixes to the standard scope names (e.g: `business-x-mobileapp`, `business-y-servicedesk`)
- **Subjects:** MUST be one of the following depending on the type of the XDR:
  - **ADR:** `principles`, `application`, `data`, `integration`, `platform`, `controls`, `operations`
  - **BDR:** `principles`, `marketing`, `product`, `controls`, `operations`, `organization`, `finance`, `sustainability`
  - **EDR:** `principles`, `application`, `infra`, `ai`, `observability`, `devops`, `governance`
- **XDR Id:** [scope]-[type]-[xdr number unique in scope] (the xdr id must be unique among all XDRs of the same type in the different scopes and always use lowercase)
  - Types in IDs: `adr`, `bdr`, `edr`
  - Define the next number of an XDR by checking what is the highest number present in the type+scope. Don't fill numbering gaps, as they might be old deleted XDRs and we should never reuse numbers of different documents/decisions. Numbering gaps are expected.
- Decisions MUST be concise and reference other XDRs to avoid duplication
- Never use emojis in contents
- Always use file names with lowercase
- Avoid using lengthy instructions on the XDR. If there are long and detailed instructions related to the XDR, or instructions that are outside the decision, create another file with a guide. If the guide is small, keep it in the XDR itself.
- If there is a README.md file in the root of the xdrs folder, always keep it up to date. Never use emojis
- Keep a canonical index with all XDRs of a certain type+scope in `.xdrs/[scope]/[type]/index.md`
  - Organize XDRs by subject for easier navigation
  - Add a list of other scope indexes that this scope might be related to (only add scopes that might be overridden). E.g: "business-x-mobileapp" scope could refer to "business-x" and "sensitive-data" scopes in its index list. XDRs in scopes listed last override XDRs in scopes listed first when addressing the same topic.
  - Document decision conflicts in "Conflicts" section for the XDR that is overriding another XDR in other scopes
  - **Within-scope conflicts:** XDRs within the same type+scope must not conflict. If two XDRs appear to conflict, one should be updated, deprecated, or the conflict resolved through a new XDR.
  - In the index add a short description of what is this scope about (responsibilities, general worries, teams involved, link to discussion process etc)
- Outside the scopes, keep an index pointing to all canonical indexes in `.xdrs/index.md`. Add the text "XDRs in scopes listed last override the ones listed first"
- Always verify if the index is up to date after making changes
- XDRs should be less than 100 lines long as a rule of thumb
  - This is important to make them focused on a clear decision
  - Exceptions can reach 200 lines (templates, more elaborate decision implementations etc)
- ALWAYS use `_local` scope if the user doesn't explicitelly indicate a specific scope while creating an xdr or skill.

**XDR template**

All XDRs MUST follow this template

```markdown
# [scope]-[type]-[number]: [Short Title]

## Context and Problem Statement

[Describe the context, background, or need that led to this decision.
What is the problem we are trying to solve? Who is being impacted? (<3 lines)

Question: In the end, state explicitly the question that needs to be answered. E.g: "Which platform should I use when implementing an AI agent?"]

## Decision Outcome

**[Chosen Option Title]**
[Very short description of what is the decision, aligned with the titles on the Considered Options section]

[Short description of implementation details for the chosen path]

### Implementation Details

[Optional section with implementation specifics, rules, examples or impact. This is the answer to the question in the "Context and Problem Statement". (<100 lines)]

## Considered Options

[Optional section present only when there are meaningful options to be discussed.]

* (REJECTED) **Option 1** - Brief description of option 1
  * Reason: Brief description why this was rejected with important aspects to be re-checked in the case we want to change this decision
* (CHOSEN) **Option 2** - Brief description of option 2
  * Reason: Brief description of why this option was accepted, containing the strengths, strategical motivations and it's differential over the other options.
* (REJECTED) **Option 3** - [same as above, if we have more than 2 options to choose from]

## Conflicts

[If this XDR has conflicts with other scopes, this section is MANDATORY and needs to have an explanation why the conflict is accepted]

* Conflict with [XDR id] (e.g.: adr-business-x-001)
  * Summary: Brief description of the conflict
  * Reason to accept: Brief description of why it was decided to accept this conflict, possibly overriding or diverging from the other decision/scopes

## References

[optional section]
[useful links related to this implementation]
[links to the discussion (PRs, meetings etc)]
[links to related skills]
```

**Examples:**
- `.xdrs/business-x/edrs/devops/003-required-development-workflow.md`
- `.xdrs/business-x/adrs/governance/010-security-and-secrets-management.md`
- `.xdrs/_core/adrs/devops/001-multi-repo.md`

**XDR ID Examples:**
- `business-x-adr-001` (not `ADR-business-x-001` or `business-x-adr-1`)
- `business-x-edr-042` (not `EDR-BUSINESS-X-042`)
- `business-x-bdr-007`

## Procedures

1. Choose the correct type (ADR, BDR, EDR), scope, and subject for each new XDR.
2. Create the XDR using the template in the Implementation Details section above, adapting it for the chosen type and required sections.
3. Update or create the scope `README.md` with examples if needed.
4. Add/update the new/updated XDRs to `.xdrs/[scope]/[type]/index.md` and to the main `.xdrs/index.md`
5. Keep decision texts short and link to other XDRs for shared rules

## Considered Options

* (REJECTED) **Flat list of decisions** - Simple but becomes unmanageable as the number grows.
  * Reason: Does not scale and makes navigation difficult over time.
* (REJECTED) **Per-team folders without scope** - Easier ownership but loses organization hierarchy.
  * Reason: Lacks a clear hierarchy and makes cross-team reuse harder.
* (CHOSEN) **Scoped + typed + subject folders** - Clear ownership by scope first, then decision type, with predictable navigation and reusable decisions.
  * Reason: Scales well, supports AI agents with focused files, enables reuse across scopes, and groups all decisions for a given scope together regardless of type.

## References

- [001-lint skill](skills/001-lint/SKILL.md) - Skill for reviewing code changes against XDRs
