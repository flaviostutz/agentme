# XDRS Scope Placement Analysis

This module is shared across XDRS writing skills. Run this analysis **before** the prerequisites gate to determine and confirm the target scope for the document being authored.

---

## Step A — Check User-Stated Scope

If the user explicitly named a target scope in their request, note it as the proposed scope and proceed to Step C for validation. Do not skip validation even when a scope is stated — the content must match the scope's purpose.

If no scope was stated, proceed to Step B.

## Step B — Analyze Content Nature

Determine the appropriate scope-type by matching the content being authored to one of the types below. A scope may declare multiple types (`scope-type: typeA, typeB`); a scope is a candidate if ANY of its declared types match.

| Content nature | Scope-type | Reference policy |
|---|---|---|
| Authoring standards, writing templates, or governance rules intended to be shared across **multiple related scopes** | `core` | ADR-011 |
| Industry standards, compliance frameworks, reference architectures, or canonical blueprints to be adopted or adapted | `reference` | ADR-012 |
| Live services, active shared platforms, or existing infrastructure that can be consumed directly | `platform` | ADR-013 |
| Business area, product line, team, or general architectural/engineering decision | `standard` | ADR-014 |

**Special case — local meta-policy**: If the content is governance or authoring standards that apply to **only one** target scope (not shared across multiple), the correct placement is a **local meta-policy file** (`NNN-core.md`) inside that scope's `[type]/principles/` directory, NOT a new scope. Recommend this option clearly and ask the user to confirm before continuing.

## Step C — Enumerate and Rank Workspace Scopes

1. Read `.xdrs/index.md` to list all declared scopes.
2. For each scope whose `scope-type` matches the type identified in Step A or B (match if ANY of a scope's declared types fit), read its `index.md` and assess the following signals, in order of weight:
   - **Primary**: Does `apply-to` or `description` describe a domain that covers this content?
   - **Secondary**: Does the scope's `follows:` chain declare a governance relationship relevant to this content area?
   - **Tertiary**: Does the scope contain local meta-policies (`NNN-core.md` files in `[type]/principles/`) that indicate it already governs this type of content?
3. Rank all matching scopes from most to least relevant. Select the highest-ranked scope as the recommendation.
4. If `_local` is the only scope in the workspace, recommend it as the default.

## Step D — Handle Mismatches and Gaps

- **Mismatch (user-stated scope)**: If the proposed scope from Step A has a `scope-type` that does not match the content nature identified in Step B, explain the mismatch with a clear rationale and ask the user to confirm the choice or select an alternative scope.
- **No existing scope fits**: Recommend creating a new scope and provide naming guidance per scope-type:
  - `core`: name MUST contain `core`; `-core` suffix preferred (e.g., `myarea-core`)
  - `reference`: `{domain}-ref-{name}` pattern (e.g., `security-ref-iso27001`)
  - `platform`: `{domain}-plat-{name}` pattern (e.g., `infra-plat-aws`)
  - `standard`: any valid lowercase scope name (no special pattern required)

## Step E — Confirm with User

Present the recommended scope (or the proposed scope from Step A with any mismatch notes) and confirm with the user before proceeding to the prerequisites gate. Once confirmed, the scope is locked for the rest of the authoring workflow.
