---
name: compile-scope
description: >
  Compiles or updates any scope declaring `scope-type: compiled` from its configured external sources. Reads compilation meta-policies to discover sources, fetches content (git clone, local copy, or web scrape), plans policy changes, migrates policies one at a time with structured format, `## Source` sections, and `**compilation-note:**` markers, then runs lint and review. Documents source inconsistencies without inventing fixes. Activate when the user asks to compile, update, sync, refresh, or recompile a compiled scope.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-09-19
---

## Overview

Performs a full compilation cycle for any scope declaring `scope-type: compiled`: discovers compilation meta-policies across all type folders, checks whether each governed source is already in sync before doing any work, fetches due sources into a temporary staging directory, plans which policies to create, update, or remove, migrates them one at a time with full source traceability, runs lint and review, persists selected source content and updates sync tracking, and documents any inconsistencies found in the source. Works for both initial compilation and re-compilation (updates). By default, fetched source content used to compile policies is persisted under `.assets/sources/[name]/` in the scope (see `_core-adr-policy-019` rules 12–13); this content is never authoritative for decisions (rule 14). Requires `_core-adr-policy-019-compiled-scope-type` to be present in the workspace.

### Inputs

#### Required

- Name of the compiled scope to sync.

#### Optional

- Force-refetch flag to bypass the re-sync short-circuit.

### Outputs

#### Contents

- Updated compiled scope, or a no-op already-in-sync report.

#### Changes

- Policy files created, updated, or removed.

### Halt Conditions

- No local meta-policy found in the scope.
- Scope does not declare scope-type: compiled.
- A source cannot be fetched or converted.

### User Interaction

- Confirmation of the CREATE/UPDATE/REMOVE plan before migrating.

### Runtime Requirements

- Network/git access for remote sources.
- `uvx markitdown` for non-Markdown source conversion, if needed.
- `npx @playwright/cli` as a web-scraping fallback.

## Instructions

### Phase 0: Prerequisites Gate

1. Identify the target scope. Verify its `index.md` declares `scope-type: compiled` (alone or combined with other types). If not, output: `FAIL — [scope-name] does not declare scope-type: compiled. This skill only applies to compiled scopes.`
2. Scan ALL type folders (`adrs/`, `bdrs/`, `edrs/`) inside the target scope for local meta-policy files whose filename matches `NNN-core.md` in `[type]/principles/`. Collect every match.
3. If no meta-policy is found in any type folder, output: `FAIL — Compilation cannot proceed: no local meta-policy NNN-core.md found in any [type]/principles/ folder of [scope-name]. Create it first with ## Sources and ## Selectors sections per _core-adr-policy-019 rule 07.`
4. Read every found meta-policy fully. For each, extract:
   - **Sources**: parse all `- [web] ...`, `- [git] ...`, `- [local] ...` bullet entries from the `## Sources` section, including each source's `name` slug (per `_core-adr-policy-019` rule 07).
   - **Selectors**: read the `## Selectors` section content (used in Phase 3).
   - **Sync Settings**: parse `Source re-sync period days` and, if present, `Source storage: temporary` from the `## Sync Settings` section (used in Phase 1 and Phase 9).
   - **Fetch Procedures**: read the `## Fetch Procedures` section if present (used in Phase 2).
   - **Compilation Notes**: read if present (used in Phase 3–4).
   - **Review Notes**: read if present (used in Phase 7).

### Phase 1: Check Sync Necessity

1. For each source `name` extracted in Phase 0, look for `.assets/sources/[name]/source.md` in the governed type folder.
2. If `source.md` does not exist for a source, that source has never been synced — it is due for Phase 2.
3. If `source.md` exists, read its `last-fetch-timestamp` and `last-compilation-timestamp`. Compute the elapsed days since `last-fetch-timestamp`. That source is due for Phase 2 if either is true: the elapsed days exceed the meta-policy's `Source re-sync period days`, or `last-compilation-timestamp` is older than `last-fetch-timestamp` (a previous run fetched but never finished compiling).
4. If the input includes an explicit force-refetch/recompile request (see Inputs > Optional), treat every source as due regardless of timestamps.
5. If no source across any governed meta-policy is due, output: `OK — [scope-name] is already in sync. No action taken.` and halt — do not proceed to later phases.
6. Otherwise, proceed to Phase 2, but scope fetching and compilation to only the meta-policies and sources that are due; meta-policies with no due sources MAY be skipped entirely.

### Phase 2: Fetch Sources

1. Create a temporary directory `.tmp/compilation-[YYYYMMDDHHMMSS]/staging/` in the workspace root.
2. For each due source (from Phase 1), fetch in the following preference order (first available wins; if all equivalent URLs are listed, try each in order):
   - **Git URL** (`- [git] ...`): run `git clone --depth=1 [url] .tmp/compilation-[ts]/staging/[name]/`. If `git` is not available or the clone fails, fall back to the next option.
   - **Local folder** (`- [local] ...`): copy the folder contents to `.tmp/compilation-[ts]/staging/[name]/`.
   - **Web URL** (`- [web] ...`): before scraping, search the workspace for a skill specialized in fetching content from this URL or website domain (e.g., a skill whose description or name references the domain, the product, or the content type). Some websites require special handling — SSO, client certificates, shadow DOM, iframes, CAPTCHAs, or other quirks. If a specialized fetch skill is found, follow it to retrieve the content. If no specialized skill exists, fall back to `npx --package=@playwright/cli@latest playwright-cli`; run with `--help` to confirm available commands and save output as `.html` file(s) in `.tmp/compilation-[ts]/staging/[name]/`.
3. If any source cannot be fetched via any listed option, report the failure and continue with remaining sources. Do not abort the entire compilation for a single failed source.
4. Immediately after a source is fetched successfully, create `.assets/sources/[name]/source.md` if absent and update its `last-fetch-timestamp` to the current time — this happens regardless of the `Source storage` setting, since the tracking file always persists per `_core-adr-policy-019` rule 12.
5. Convert non-markdown documents found in the fetched source directories. Use only the format converters actually needed:
   - PDF files: `uvx markitdown[pdf] <file> -o <output>.md`
   - XLSX files: `uvx markitdown[xlsx] <file> -o <output>.md`
   - DOCX files: `uvx markitdown[docx] <file> -o <output>.md`
   - PPTX files: `uvx markitdown[pptx] <file> -o <output>.md`
   - HTML files saved from web scraping: `uvx markitdown <file.html> -o <output>.md`

### Phase 3: Plan Policies

1. For each type folder governed by a meta-policy (from Phase 0), apply the `## Selectors` rules to the fetched staging content to determine which portions to include.
2. List all existing policies in the scope under each governed type folder.
3. If `.assets/sources/[name]/` already holds a previous persisted snapshot, diff the newly selected staging content against it (for example, by content hash per file) to pre-seed which policies are likely unaffected.
4. Analyse the selected content and produce a TODO list showing for each expected policy:
   - **CREATE** — new policy to be compiled from source (does not yet exist in scope)
   - **UPDATE** — existing policy whose source content has changed
   - **REMOVE** — existing policy whose source content no longer exists or is excluded by selectors
   - **KEEP** — existing policy that is up to date; no action needed (default for policies whose source content is unchanged per the step 3 diff)
5. Present the TODO list to the user and wait for confirmation before proceeding to Phase 4.

### Phase 4: Migrate Policies (one at a time)

For each TODO item marked CREATE or UPDATE, in sequence:

1. **Write the policy file** following `_core-adr-policy-019` and `_core-adr-policy-008`:
   - Use standard policy frontmatter: `name`, `description`, `apply-to`, `valid-from`. Generate these from the source text; they are exempt from the no-invented-content rule per policy-019 rule 05.
   - Use structured numbered rule blocks for all claims (per `_core-adr-policy-008`).
   - Transcribe source content faithfully. Do NOT invent, infer beyond what the source states, or fill gaps. Preserve ambiguities as-is.

2. **Add a `**compilation-note:**` marker** inside a rule body only when the mapping from source to rule is not obvious — for example: indirect references, conclusions drawn by connecting multiple source sections, interpretations that required judgment, or cases where the same source passage could be read differently. Do NOT add a marker when the rule is a direct, literal transcription of a single source statement. Place the marker as a new sentence at the end of the rule body. Example:
   ```
   All API keys MUST be rotated every 90 days. **compilation-note:** derived from [api-guidelines/security/api-guidelines.md section 4.2] — "Keys should be invalidated and replaced quarterly"; frequency inferred as 90 days from the term "quarterly".
   ```

3. **Add a `## Source` section** as the LAST section of the policy (after `## References` if present, otherwise after `## Decision Outcome`). List the relative file path(s) of the source document(s) as plain text — NOT as markdown links. Paths are relative to `.assets/sources/` and use the source's `name` slug as their first segment (e.g., `api-guidelines/standards/section-4/api-security.md`), regardless of whether storage is currently persistent or temporary.
   ```
   ## Source

   - api-guidelines/standards/section-4/api-security.md
   ```

4. For REMOVE items: delete the policy file and remove its entry from the type's `index.md`.

5. Note any content in the source that is inconsistent, contradictory, or cannot be faithfully expressed as a valid XDRS policy. Record these for Phase 8.

### Phase 5: Verify Each Policy

After writing each policy:

1. Confirm the `## Source` section is present with at least one path entry.
2. Confirm the policy uses structured numbered rule blocks (`_core-adr-policy-008`).
3. Confirm `**compilation-note:**` markers are present for every rule whose mapping from source is non-obvious (indirect references, multi-source conclusions, interpretations requiring judgment). Direct literal transcriptions do not require a marker.
4. Confirm no normative statements are present that cannot be traced to the listed source file.
5. Add any new inconsistencies found to the list for Phase 8.

### Phase 6: Lint

1. Run `npx xdrs-core lint` from the workspace root (or `make lint` if a `Makefile` is present with a `lint` target).
2. Review all reported errors.
3. Fix only mechanical and structural errors (missing required frontmatter fields, naming violations, index link mismatches). Do NOT invent content to satisfy content-level findings.
4. Re-run lint after fixes until it passes or only unfixable findings remain.

### Phase 7: Review

1. Read and follow `.xdrs/_core/adrs/principles/skills/review/SKILL.md` fully, scoped to the compiled scope.
2. Apply any review notes from the meta-policy's `## Review Notes` section as additional mandatory conventions during this review.
3. Fix only mechanical and structural findings from the review. Do NOT invent content to resolve content-level findings.
4. Any review findings that require inventing or guessing content MUST be recorded as inconsistencies in Phase 8.

### Phase 8: Document Inconsistencies

1. Collect all inconsistencies noted during Phases 4, 5, and 7.
2. If any inconsistencies exist:
   - Determine the next available policy number in the `001–100` principles block for the relevant type folder.
   - Create or update `[type]/principles/NNN-inconsistencies-from-source.md` in the scope.
   - The policy `name` field MUST be `[scope]-[type]-policy-NNN-inconsistencies-from-source`.
   - List each inconsistency with: source file path, affected compiled policy, and a description of the inconsistency.
   - Do NOT propose or include fixes.
3. If no inconsistencies exist, report that the compilation is clean.

### Phase 9: Persist Sources and Update Tracking

1. For each meta-policy and source processed in this run, check its `Source storage` setting.
2. If storage is persistent (the default): replace the contents of `.assets/sources/[name]/` (excluding `source.md`) with the staged content actually selected and used in Phase 3–4 — remove any previously persisted file that is no longer selected or used, per `_core-adr-policy-019` rule 13.
3. If storage is `temporary`: do not copy any bulk staged content into `.assets/sources/[name]/`; only `source.md` lives there.
4. For every source processed in this run, update `.assets/sources/[name]/source.md`'s `last-compilation-timestamp` to the current time — this step only runs after Phase 6 (Lint) and Phase 7 (Review) both pass for the policies depending on that source.
5. If a source's `Source storage` setting changed since its last run, reconcile per `_core-adr-policy-019` rule 12: switching to `temporary` removes previously persisted bulk content (keeping `source.md`); switching away from `temporary` begins persisting bulk content from this run onward.

### Phase 10: Cleanup

1. Remove the temporary staging directory `.tmp/compilation-[ts]/` created in Phase 2. Never remove or modify persisted content under `.assets/sources/` — that is governed solely by Phase 9.
2. Report a compilation summary:
   - Policies created, updated, removed.
   - Inconsistencies documented (with file path).
   - Any sources that could not be fetched.
   - Lint and review pass/fail status.
   - Sources persisted, kept temporary, or skipped as already in sync.

## Anti-Patterns

- **Mistake:** Inventing content to fill gaps when source material is incomplete or ambiguous.
  **Why it happens:** The agent wants to produce a "complete" policy and fills gaps with plausible-sounding text.
  **Instead:** Transcribe faithfully, preserve ambiguities as-is, and record inconsistencies in Phase 8 instead of guessing.

- **Mistake:** Skipping the Phase 3 confirmation and migrating policies before the user approves the CREATE/UPDATE/REMOVE plan.
  **Why it happens:** Momentum from prior compilations makes the plan feel obviously correct.
  **Instead:** Always present the TODO list and wait for explicit confirmation before Phase 4.

- **Mistake:** Leaving the temporary `.tmp/compilation-[ts]/` directory behind after a run.
  **Why it happens:** Phase 10 cleanup is easy to forget once the summary is reported.
  **Instead:** Always remove the temporary directory as the first Phase 10 step, even on partial failures.

- **Mistake:** Persisting every fetched file under `.assets/sources/[name]/`, including content excluded by selectors or no longer used by any compiled policy.
  **Why it happens:** It feels safer to keep everything "just in case" rather than compute what is actually still used.
  **Instead:** Persist only Selector-matched content actually referenced by a compiled policy's `## Source` section, per `_core-adr-policy-019` rule 13; remove the rest during Phase 9.

- **Mistake:** Skipping Phase 1 and always re-fetching and recompiling, even when every source is well within its re-sync period.
  **Why it happens:** Re-running the full cycle unconditionally feels more thorough or "safe".
  **Instead:** Always check `.assets/sources/[name]/source.md` timestamps against `Source re-sync period days` first, and short-circuit with a no-op report when nothing is due.

- **Mistake:** Reading or citing content under `.assets/sources/` as if it were an authoritative policy, or adding a markdown link to it from another document.
  **Why it happens:** The raw source content is readily available and often more detailed than the compiled policy.
  **Instead:** Treat only compiled policies as authoritative per `_core-adr-policy-019` rule 14; source content exists solely to support fetch/diff/recompilation, and linking to it is also forbidden mechanically by lint.

## References

- [_core-adr-policy-019 - Compiled scope type](../../019-compiled-scope-type.md)
- [_core-adr-policy-008 - Policy structured standards](../../008-policy-structured-standards.md)
