---
name: agentme-edr-policy-127-external-system-adapter-skills
description: Defines how agents must approach reading or mutating data in external systems (priority order, credential handling, browser configuration, mutation safety) and what constraints apply when encoding that knowledge as reusable adapter skills. Use when automating any interaction with an external system or when authoring adapter skills for a system.
apply-to: All automation tasks that read from or write to external systems; all adapter skill authoring
valid-from: 2026-08-04
---

# agentme-edr-policy-127: External system adapter skills

## Context and Problem Statement

When automating tasks that interact with external systems (SaaS tools, REST APIs, internal platforms), agents face recurring decisions: which integration channel to use, how to handle credentials, and how to capture accumulated system knowledge so it can be reused.

How should agents approach external system interaction, and how should that knowledge be encoded as reusable skills?

## Decision Outcome

Use a priority-ordered integration approach — always leveraging the user's existing session context — and encode system-specific interaction knowledge as business-logic-free adapter skills.

Rules 01–04 govern **runtime behavior** (an agent executing a task against an external system). Rule 05 governs **authoring** (a skill author writing an adapter skill).

### Details

#### 01-approach-priority-order

Agents MUST attempt the following approaches in order, stopping at the first that is feasible:

1. **API via curl** — If the system exposes an API, interact with it directly using the `curl` CLI. Another HTTP client MAY be used only when `curl` is insufficient for the specific operation (e.g. streaming, binary upload).
2. **Playwright UI scraping** — If no API is available or the user cannot provide an API credential, use the `playwright` CLI (via `npx -y --package=@playwright/cli@latest playwright-cli`) to interact with the system's UI using the user's existing browser profile (see rule 03). Another browser automation tool MUST NOT be used.
3. **Git clone** — If the target data is read-only and lives in a git repository, clone the repository locally and read from the local path. For private repositories, follow [agentme-edr-124](124-secrets-management.md) to retrieve the PAT or SSH key from the native keychain.
4. **Local folder** — As a last resort, ask the user to provide a path to a local folder containing the relevant data.

When a higher-priority approach is attempted and fails, the failure reason MUST be stated before trying the next approach.

#### 02-api-credential-handling

API credentials (keys, tokens, passwords) MUST be stored and retrieved using the native OS keychain following [agentme-edr-124](124-secrets-management.md). Agents MUST NOT hardcode, log, or persist credentials to disk. When a required credential is absent, agents MUST prompt the user to store it via the `setup-secrets` Makefile target before proceeding.

#### 03-playwright-browser-config

When using Playwright, agents MUST run the `playwright` CLI via `npx -y --package=@playwright/cli@latest playwright-cli` and MUST use the user's existing browser profile to preserve SSO sessions, CA certificates, cookies, and extensions that the target system depends on.

- MUST use `--user-data-dir` pointing to the user's active browser profile directory, or attach to a running browser instance via CDP.
- MUST NOT launch a blank, incognito, or freshly provisioned profile.
- MUST keep the browser window visible throughout the interaction so the user can follow and intervene.
- SHOULD prefer CDP attachment to an already-running browser over launching a new instance, when the browser is already open.

When the `playwright` CLI is technically insufficient for a required integration capability (e.g., network response interception, which the CLI does not expose), the Playwright Node.js API MAY be used instead. The justification MUST be documented in a `## Conflicts` section within the adapter skill, following the same format used in Policy conflict declarations (citing the policy rule being overridden, the reason, and the mitigations applied).

#### 04-human-in-the-loop-before-mutations

Before executing any write, mutate, or delete operation on an external system, agents MUST present a plain-language summary containing at minimum:

- **System:** name and environment (e.g. "ServiceNow production")
- **Operation:** what action will be taken
- **Fields/values:** which fields will be changed and to what values
- **Estimated impact:** a brief statement of what the change will affect

Agents MUST wait for explicit user confirmation before proceeding. Read-only and query operations do not require confirmation.

#### 05-adapter-skill-no-business-logic

Adapter skills MUST be pure I/O bridges between the agent and the external system. They MUST NOT contain business rules, domain decisions, validation logic, or application-layer concerns, which belong in the application or workflow layer following [agentme-edr-126](126-pragmatic-hexagonal-architecture.md).

An adapter skill SHOULD provide only: session setup, navigation, field interaction, and response parsing specific to the target system.

#### 06-connector-skill-naming

A skill that serves as a base to connect to an external system via API, UI scraping, or file access MUST have a name ending with `-connector` (e.g. `servicenow-connector`, `sap-api-connector`).

#### 07-connector-known-issues-section

Every connector skill MUST contain a `## Known Issues` section documenting previous problems encountered when using that connector and how to overcome them. This section is read by running agents at execution time to self-correct without human intervention. Each entry SHOULD follow this structure:

- **Symptom:** observable sign that the problem has occurred
- **Cause:** brief explanation of the root cause
- **Fix:** concrete steps the agent MUST take to resolve the issue

---

#### guidance

> Non-normative. The following is illustrative guidance, not a requirement.

Adapter skills for a given system benefit from layering so that knowledge at each level can be activated and reused independently:

- **Base skill (connector)** — Session setup, authentication, system overview, and top-level screen or API structure. MUST follow the `-connector` naming rule (rule 06) and MUST include a `## Known Issues` section (rule 07). This skill gives the agent enough context to orient itself in the system. Examples: `servicenow-connector` (login, workspace layout, navigation patterns), `sap-api-connector` (base URL, API key retrieval, OpenAPI spec location).
- **Domain skill** — A specific feature area, building on the base skill. Examples: `servicenow-incidents` (incident concept, workspace, field structure), `sap-api-mutations` (confirmation procedures, human-in-the-loop steps per rule 04).
- **Operation skill** — A specific action within a domain, building on the domain skill. Examples: `servicenow-incidents-change` (open an incident, edit fields, click action buttons, handle known errors), `servicenow-vulnerabilities` (filter, triage, export).

The depth of the hierarchy is discretionary. A simple system may need only a base skill. Complex systems benefit from the full three-layer structure. Higher-level skills SHOULD activate their lower-level dependencies explicitly at the start of their instructions.

When creating adapter skills for a new system, document the chosen integration approach (rule 01) in the skill's frontmatter description, follow the `-connector` naming convention (rule 06) for the base skill, and populate the `## Known Issues` section (rule 07) as experience accumulates. All system-specific adapter skills SHOULD be placed in the `_local` scope of the consuming project.
