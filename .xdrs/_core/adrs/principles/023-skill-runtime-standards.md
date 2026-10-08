---
name: _core-adr-policy-023-skill-runtime-standards
description: Defines how skills behave at runtime - where they place work files, when to halt or ask the user, quality gate before creating a skill, and word caps for generated content. Use when authoring or reviewing skill instructions.
apply-to: All skill packages
valid-from: 2026-10-08
---

# _core-adr-policy-023: Skill runtime standards

## Context and Problem Statement

Skills run for humans and AI agents in many workspaces. Without shared runtime rules, each skill invents its own place for generated files, its own halting behavior, and its own output sizes, which litters workspaces, risks leaking secrets, and makes skills unpredictable.

How should a skill behave while running, so that its files, questions, stops and generated content are consistent across skills?

## Decision Outcome

**A shared runtime contract for every skill, separate from the skill package format**

Package structure, `SKILL.md` format, scripts and validation are defined in [`_core-adr-policy-003`](003-skill-standards.md). This Policy defines only what a skill does while it runs.

### Details

**Work files**

Files a skill creates while running MUST follow this layout unless the skill or the user sets another location:
- Each skill owns `.tmp/[skill-name]/` at the workspace root, created lazily. Workspaces SHOULD gitignore `.tmp/`; skills MUST NOT edit `.gitignore` for it.
- Skills MUST NOT store files directly in `.tmp/[skill-name]/`. Final outputs go in one run folder per run, `.tmp/[skill-name]/[run-name]/`.
- `[run-name]` is a short name describing the run (e.g. `report-anthony`), using only lowercase letters, digits and hyphens. When the run has no natural name, use the local start time `[YYYYMMDDHHMMSS]`. When the name is taken, append `-2`, `-3`...
- `.tmp/[skill-name]/.work/` holds reusable intermediate files such as caches and staging. It is safe to delete at any time. Skills MUST re-check freshness before reusing its content and MUST namespace content per input (e.g. `.work/staging/[input-name]/`). Clearing and refetching an input is not safe while another run uses the same input.
- Skills that produce no final outputs use only `.work/`, with no run folder.
- Temporary scripts and other throwaway files MUST go in the OS temp dir and be deleted when the run ends. Secrets MUST NOT be written anywhere else and MUST always be deleted.
- A skill that uses another skill's output MUST receive the source run folder path as input, read it in place and never change data there. When changes are needed, it copies the files into its own run folder.
- On a read-only workspace, use the same layout under the OS temp dir.
- Keep run folders after the run. When a run folder was created, even on halt or failure, end the final chat message with `results-path: [dir]/`.
- Skills that create files MUST restate the parts of this layout they use in their own `## Instructions`, to run standalone.

**Quality gate**

Before creating a skill, confirm it removes real ambiguity or repetitive effort compared to not having it. Skills that only restate a Policy, or that handle a one-off task unlikely to recur, SHOULD NOT be created.

**Clarify First**

Generative skills — those producing a deliverable document (Policy, Skill, Article, Research, Initiative, Presentation) — SHOULD list the 2-4 inputs they need confirmed (e.g., topic, scope, audience) and ask the user when any is unknown, stopping once those inputs are confirmed rather than over-interrogating. Skills that route, review, or report instead of authoring a new deliverable do not need this pattern.

**Halt behavior**

Skills MUST halt on missing required input, dubious/ambiguous input, or insufficient agent confidence, unless the user explicitly instructs the agent to proceed anyway. This override applies generally; a skill's own `## Halt Conditions` list does not need to restate it.

**Generated content caps**

Every natural-language content a skill generates MUST declare a hard word cap written exactly as `<N words`, whether a human or an agent executes the skill. This covers files, templates, reports, intermediate chat messages, HITL questions, final summaries, and text posted to external systems (e.g., PR comments, commit messages).
- Exempt, with no marker: code (including its comments), structured data (JSON, YAML, tracking files), verbatim copies, and frontmatter fields already limited in characters by a spec or Policy.
- Caps MUST be in words; other limits MAY coexist but never replace them.
- Declare each cap once: in the template placeholder (including templates in `references/` or `.assets/`), else in the Instructions step producing the content, else in its `#### Contents` bullet.
- A blanket statement MAY cover a content class (e.g., all intermediate messages); a more specific cap overrides it.
- Write the number inline; a Policy reference is optional.
- Content whose size cannot be bounded MUST be marked `(uncapped: <reason>)`, the reason explaining why.
- Caps are hard: condense, or split into another item only where the skill allows it; never split one logical item across messages. An explicit user request lifts the cap for that item only.

## References

- [_core-adr-policy-003 - Skill standards](003-skill-standards.md)
