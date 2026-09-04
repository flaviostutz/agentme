# XDRS Meta-Policy Compliance Check

This module is shared across XDRS writing skills. Read and execute every check during the final review of a document.

Substitute `[DOCUMENT]` with the appropriate noun for the calling skill: `policy`, `skill`, `article`, `research`, or `initiative`.

---

**Meta-policy compliance**: Check the target scope's `index.md` for a `follows` frontmatter field. `_core` Policies always apply to all scopes. If `follows` lists additional core scope names (e.g., `follows: [myarea-core]`), verify that each listed scope directory exists in the workspace (e.g., `.xdrs/[scope-name]/index.md`). If any listed scope is missing, STOP immediately and tell the user: "Scope `[scope-name]` is listed in `follows` but not found in the workspace. Install it before proceeding." Once all `follows` scopes are confirmed present, verify the [DOCUMENT] satisfies all requirements from those Policies. Scopes are applied in order; last-listed scope in `follows` takes precedence when the same topic is covered by multiple scopes.

- **Scope-type standards:** Read the target scope's `scope-type`. Normalise the value to a list: split on commas and trim whitespace (`scope-type: typeA, typeB` becomes `[typeA, typeB]`). For **each** type in the list, search the `[type]/principles/` directories of all `core`-type scopes for a file ending in `{scope-type}-scope-type.md`. If found, also load all companion files (`{scope-type}-scope-type-{qualifier}.md`) from the **same directory** and apply their rules as additional requirements. Resolve any `NN-parent-scope-type` rule transitively from the primary file. See `_core-adr-policy-010` rules 22 and 24.
- **Scope-local standards:** Scan the target scope's own `[type]/principles/` directories for all files whose filename title starts with `core` (i.e., `NNN-core.md` or `NNN-core-{qualifier}.md`), excluding scope-type definition files (whose title ends with `-scope-type`). If any are found, apply ALL of them as mandatory requirements; they override scope-type standards on conflict. See `_core-adr-policy-010` rules 23 and 24.
