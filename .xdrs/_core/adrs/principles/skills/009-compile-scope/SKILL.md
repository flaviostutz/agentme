---
name: 009-compile-scope
description: >
  Compiles or updates any scope declaring `scope-type: compiled` from its configured external sources. Reads compilation meta-policies to discover sources, fetches content (git clone, local copy, or web scrape), plans policy changes, migrates policies one at a time with structured format, `## Source` sections, and `**compilation-note:**` markers, then runs lint and review. Documents source inconsistencies without inventing fixes. Activate when the user asks to compile, update, sync, refresh, or recompile a compiled scope.
metadata:
  author: flaviostutz
  version: "1.0"
---

## Overview

Performs a full compilation cycle for any scope declaring `scope-type: compiled`: discovers compilation meta-policies across all type folders, fetches sources into a temporary directory, plans which policies to create, update, or remove, migrates them one at a time with full source traceability, runs lint and review, and documents any inconsistencies found in the source. Works for both initial compilation and re-compilation (updates). Requires `_core-adr-policy-019-compiled-scope-type` to be present in the workspace.

## Instructions

### Phase 0: Prerequisites Gate

1. Identify the target scope. Verify its `index.md` declares `scope-type: compiled` (alone or combined with other types). If not, output: `FAIL — [scope-name] does not declare scope-type: compiled. This skill only applies to compiled scopes.`
2. Scan ALL type folders (`adrs/`, `bdrs/`, `edrs/`) inside the target scope for local meta-policy files whose filename matches `NNN-core.md` in `[type]/principles/`. Collect every match.
3. If no meta-policy is found in any type folder, output: `FAIL — Compilation cannot proceed: no local meta-policy NNN-core.md found in any [type]/principles/ folder of [scope-name]. Create it first with ## Sources and ## Selectors sections per _core-adr-policy-019 rule 07.`
4. Read every found meta-policy fully. For each, extract:
   - **Sources**: parse all `- [web] ...`, `- [git] ...`, `- [local] ...` bullet entries from the `## Sources` section.
   - **Selectors**: read the `## Selectors` section content (used in Phase 2).
   - **Fetch Procedures**: read the `## Fetch Procedures` section if present (used in Phase 1).
   - **Compilation Notes**: read if present (used in Phase 2–3).
   - **Review Notes**: read if present (used in Phase 6).

### Phase 1: Fetch Sources

1. Create a temporary directory `.tmp/compilation-[YYYYMMDDHHMMSS]/` in the workspace root.
2. For each source discovered in Phase 0, fetch in the following preference order (first available wins; if all equivalent URLs are listed, try each in order):
   - **Git URL** (`- [git] ...`): run `git clone --depth=1 [url] .tmp/compilation-[ts]/source-N/`. If `git` is not available or the clone fails, fall back to the next option.
   - **Local folder** (`- [local] ...`): copy the folder contents to `.tmp/compilation-[ts]/source-N/`.
   - **Web URL** (`- [web] ...`): before scraping, search the workspace for a skill specialized in fetching content from this URL or website domain (e.g., a skill whose description or name references the domain, the product, or the content type). Some websites require special handling — SSO, client certificates, shadow DOM, iframes, CAPTCHAs, or other quirks. If a specialized fetch skill is found, follow it to retrieve the content. If no specialized skill exists, fall back to `npx --package=@playwright/cli@latest playwright-cli`; run with `--help` to confirm available commands and save output as `.html` file(s) in `.tmp/compilation-[ts]/source-N/`.
3. If any source cannot be fetched via any listed option, report the failure and continue with remaining sources. Do not abort the entire compilation for a single failed source.
4. Convert non-markdown documents found in the fetched source directories. Use only the format converters actually needed:
   - PDF files: `uvx markitdown[pdf] <file> -o <output>.md`
   - XLSX files: `uvx markitdown[xlsx] <file> -o <output>.md`
   - DOCX files: `uvx markitdown[docx] <file> -o <output>.md`
   - PPTX files: `uvx markitdown[pptx] <file> -o <output>.md`
   - HTML files saved from web scraping: `uvx markitdown <file.html> -o <output>.md`

### Phase 2: Plan Policies

1. For each type folder governed by a meta-policy (from Phase 0), apply the `## Selectors` rules to the fetched content to determine which portions to include.
2. List all existing policies in the scope under each governed type folder.
3. Analyse the selected content and produce a TODO list showing for each expected policy:
   - **CREATE** — new policy to be compiled from source (does not yet exist in scope)
   - **UPDATE** — existing policy whose source content has changed
   - **REMOVE** — existing policy whose source content no longer exists or is excluded by selectors
   - **KEEP** — existing policy that is up to date; no action needed
4. Present the TODO list to the user and wait for confirmation before proceeding to Phase 3.

### Phase 3: Migrate Policies (one at a time)

For each TODO item marked CREATE or UPDATE, in sequence:

1. **Write the policy file** following `_core-adr-policy-019` and `_core-adr-policy-008`:
   - Use standard policy frontmatter: `name`, `description`, `apply-to`, `valid-from`. Generate these from the source text; they are exempt from the no-invented-content rule per policy-019 rule 05.
   - Use structured numbered rule blocks for all claims (per `_core-adr-policy-008`).
   - Transcribe source content faithfully. Do NOT invent, infer beyond what the source states, or fill gaps. Preserve ambiguities as-is.

2. **Add a `**compilation-note:**` marker** inside a rule body only when the mapping from source to rule is not obvious — for example: indirect references, conclusions drawn by connecting multiple source sections, interpretations that required judgment, or cases where the same source passage could be read differently. Do NOT add a marker when the rule is a direct, literal transcription of a single source statement. Place the marker as a new sentence at the end of the rule body. Example:
   ```
   All API keys MUST be rotated every 90 days. **compilation-note:** derived from [source-1/security/api-guidelines.md section 4.2] — "Keys should be invalidated and replaced quarterly"; frequency inferred as 90 days from the term "quarterly".
   ```

3. **Add a `## Source` section** as the LAST section of the policy (after `## References` if present, otherwise after `## Decision Outcome`). List the relative file path(s) of the source document(s) as plain text — NOT as markdown links. Paths are relative to the temporary source directory (e.g., `source-1/docs/chapter-3.md`).
   ```
   ## Source

   - source-1/standards/section-4/api-security.md
   ```

4. For REMOVE items: delete the policy file and remove its entry from the type's `index.md`.

5. Note any content in the source that is inconsistent, contradictory, or cannot be faithfully expressed as a valid XDRS policy. Record these for Phase 7.

### Phase 4: Verify Each Policy

After writing each policy:

1. Confirm the `## Source` section is present with at least one path entry.
2. Confirm the policy uses structured numbered rule blocks (`_core-adr-policy-008`).
3. Confirm `**compilation-note:**` markers are present for every rule whose mapping from source is non-obvious (indirect references, multi-source conclusions, interpretations requiring judgment). Direct literal transcriptions do not require a marker.
4. Confirm no normative statements are present that cannot be traced to the listed source file.
5. Add any new inconsistencies found to the list for Phase 7.

### Phase 5: Lint

1. Run `npx xdrs-core lint` from the workspace root (or `make lint` if a `Makefile` is present with a `lint` target).
2. Review all reported errors and warnings.
3. Fix only mechanical and structural errors (missing required frontmatter fields, naming violations, index link mismatches). Do NOT invent content to satisfy content-level findings.
4. Re-run lint after fixes until it passes or only unfixable findings remain.

### Phase 6: Review

1. Read and follow `.xdrs/_core/adrs/principles/skills/001-review/SKILL.md` fully, scoped to the compiled scope.
2. Apply any review notes from the meta-policy's `## Review Notes` section as additional mandatory conventions during this review.
3. Fix only mechanical and structural findings from the review. Do NOT invent content to resolve content-level findings.
4. Any review findings that require inventing or guessing content MUST be recorded as inconsistencies in Phase 7.

### Phase 7: Document Inconsistencies

1. Collect all inconsistencies noted during Phases 3, 4, and 6.
2. If any inconsistencies exist:
   - Determine the next available policy number in the `001–100` principles block for the relevant type folder.
   - Create or update `[type]/principles/NNN-inconsistencies-from-source.md` in the scope.
   - The policy `name` field MUST be `[scope]-[type]-policy-NNN-inconsistencies-from-source`.
   - List each inconsistency with: source file path, affected compiled policy, and a description of the inconsistency.
   - Do NOT propose or include fixes.
3. If no inconsistencies exist, report that the compilation is clean.

### Phase 8: Cleanup

1. Remove the temporary directory `.tmp/compilation-[ts]/` created in Phase 1.
2. Report a compilation summary:
   - Policies created, updated, removed.
   - Inconsistencies documented (with file path).
   - Any sources that could not be fetched.
   - Lint and review pass/fail status.
