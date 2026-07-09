---
name: _core-adr-policy-018-external-path-symlinks
description: Governs how XDRS files that need to be accessible from paths outside the .xdrs/ root must be exposed using symlinks. Use when placing skills, articles, or any XDRS content at non-standard external paths required by external tools or conventions.
apply-to: All XDRS workspaces where files need to be accessible from paths outside the .xdrs/ root
valid-from: 2026-07-10
---

# _core-adr-policy-018: External path symlinks

## Context and Problem Statement

Some external tools and runtime environments require files at specific paths outside the `.xdrs/` folder. Examples include AI agent runtimes that expect skills in `.agents/skills/`, documentation generators that read from `docs/`, or CI tooling that references scripts from a fixed project-root path. Without a rule, contributors may duplicate files, breaking the single-source-of-truth guarantee that the `.xdrs/` root provides.

This policy extends [`_core-adr-policy-001`](001-xdrs-core.md), which already prohibits creating or modifying XDRS documents via symlinked paths.

How should XDRS files be made accessible from paths outside the `.xdrs/` root without duplicating their content?

## Decision Outcome

**Symlinks from external paths to the canonical `.xdrs/` location**

When a file or directory inside `.xdrs/` needs to be reachable from an external path, a symlink MUST be created at the external path pointing to the canonical `.xdrs/` location. The canonical file always lives inside `.xdrs/`. Copying is never acceptable.

**Example:** `.agents/skills/001-review` (symlink) → `.xdrs/_core/adrs/principles/skills/001-review/`

### Details

#### 01-canonical-source-must-be-in-xdrs
Every XDRS file or directory that needs to be accessible from an external path MUST reside inside the `.xdrs/` root. The external path MUST be a symlink only.

#### 02-files-must-not-be-copied-outside-xdrs
XDRS files MUST NOT be copied to any path outside `.xdrs/`. Creating a copy — even a temporary one — violates the single-source-of-truth guarantee. Only symlinks are acceptable for external access.

#### 03-symlinks-must-point-from-external-to-xdrs
Symlinks MUST point from the external path to the `.xdrs/` target. The reverse direction — a symlink inside `.xdrs/` pointing outward — MUST NOT be used.

#### 04-symlinks-should-be-declared
Symlinks SHOULD be declared in `.filedist-package.yml` under the `symlinks:` block so they are created and managed automatically. When a symlink is created manually rather than through automation, its source and target MUST be documented in a README or equivalent note co-located with the external path.

#### 05-symlinks-may-target-a-directory-or-a-single-file
A symlink MAY target a directory (for example, an entire skill package folder) or an individual file, depending on what the external tool requires.

#### 06-parent-directory-must-exist-before-symlink-creation
The parent directory of the external symlink path MUST exist before the symlink is created. Symlink creation MUST NOT implicitly create parent directories as a side effect.

## References

- [`_core-adr-policy-001`](001-xdrs-core.md) — XDRS core framework: folder structure and the rule prohibiting modifications via symlinked paths
- [`_core-adr-policy-008`](008-policy-structured-standards.md) — Policy structured standards: numbered rule block format used in this document
