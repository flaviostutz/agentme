---
name: _core-adr-policy-021-skill-bundling
description: Defines how a skill package MAY be bundled into a self-contained standalone distributable via a per-skill Makefile, including dist/ staging, recursive dependency delegation, and selective copying. Use when packaging a skill for standalone distribution outside the full xdrs-core package.
apply-to: Skill packages that need standalone distribution outside the full xdrs-core package
valid-from: 2026-09-19
---

# _core-adr-policy-021: Skill bundling

## Context and Problem Statement

Skills sometimes need to be shared or distributed as standalone artifacts outside the full `xdrs-core` package — for example, published separately or handed to a team that does not consume the whole repository. A skill that references shared `.assets/` modules (see `_core-adr-policy-003`) or embeds another skill as a dependency cannot simply be copied as a single `SKILL.md` file without breaking those references. No automated bundling utility exists yet, so each skill's own build process must resolve its dependencies; this means the same short recursive-copy pattern is duplicated across every bundling-enabled skill's `Makefile`, an accepted tradeoff until a shared build utility exists.

Question: How should a skill package that depends on shared assets or other skills be packaged into a self-contained standalone distributable?

## Decision Outcome

**Optional per-skill `Makefile` that stages a self-contained `dist/` output, recursively delegating to each dependency's own bundling `Makefile`**

A skill MAY add its own `Makefile` to become bundling-enabled. Running `make build` inside the skill's folder stages a self-contained copy of the skill and everything it needs in a local, gitignored `dist/` folder, with exactly two top-level entries: `dist/build/` (the skill's own files, ready to use standalone) and `dist/<skill-name>.zip` (a packaged archive of it) — see Details for the exact layout. Inside `dist/build/`, the skill's own resources stay flat while every bundled dependency is corralled into its own `dist/<dependency-name>/` subfolder, so it is always immediately recognizable as a separate bundled/copied skill rather than merged into the skill's own files. When the skill embeds another skill as a dependency and that dependency is itself bundling-enabled, `build` delegates to the dependency's own `make build` and copies its output wholesale, so the mechanism nests recursively without a central build utility. This is independent of the repository-level `.filedist-package.yml` distribution flow used to publish whole XDRS packages; it operates entirely within a single skill's own folder.

### Details

#### 01-bundling-is-optional
A skill MAY opt into standalone bundling by adding its own `Makefile` with `build`, `test`, and `clean` targets inside its own package folder (`skills/[skill-name]/Makefile`). Skills that are always consumed as part of the full `xdrs-core` package are not required to add one.

#### 02-dist-output-location
When present, the bundling `Makefile` MUST stage the skill's own unpacked files in `dist/build/`, relative to the root of the skill's own package (`skills/[skill-name]/dist/build/`). `dist/` MUST NOT be committed: a `.gitignore` entry covering `dist` (a bare `dist` or `**/dist` line) MUST exist in either the repository root `.gitignore` or a `.gitignore` local to the skill package. If the root `.gitignore` already covers it, no additional local entry is needed.

#### 03-works-without-bundling
A skill's `SKILL.md` MUST remain fully functional when consumed directly from its normal in-repo location, without ever running `make build`. The `dist/` output is an additional, optional artifact for standalone distribution; `SKILL.md` MUST NOT hard-depend on `dist/` existing.

#### 04-selective-copy
`make build` MUST copy only the files strictly necessary for the skill to run: its own `SKILL.md`, whichever of `scripts/`, `references/`, or `.assets/` it actually uses, and the specific shared modules or dependency skills it references. Tests, fixtures, or unrelated repository resources MUST NOT be copied into `dist/`.

#### 05-preserve-relative-paths
Files that belong to the skill's own package (`scripts/`, `references/`, its own `.assets/`) MUST be copied preserving their path relative to `SKILL.md` unchanged, since `SKILL.md` and its own files move into `dist/build/` together as a unit and their relative relationship to each other does not change. Links to a bundled dependency (a shared `.assets/` module elsewhere or another skill) are the one exception: `dist/build/` sits two directory levels below the original `SKILL.md`, so an unrewritten external link would no longer resolve once the target has been copied. `build` MUST rewrite such links inside the copied `SKILL.md` (and any other copied file that references them) to the flattened path defined by rule `06-recursive-delegation`, using a mechanical text substitution (for example `sed`).

#### 06-recursive-delegation
When a skill's `build` target embeds another skill as a dependency, `build` MUST stage that dependency under `dist/build/dist/<dependency-name>/` (a `dist/` subfolder nested inside `dist/build/` itself, not a sibling of it): if the dependency has its own bundling `Makefile`, run `$(MAKE) -C <dependency-path> build` first and copy the contents of its already-built `dist/build/` (not its whole `dist/` output, so its own zip is not carried along) into `dist/build/dist/<dependency-name>/`; if it does not, create `dist/build/dist/<dependency-name>/` and copy only its bare `SKILL.md` into it. Using the same `dist/build/dist/<dependency-name>/` shape in both cases keeps the bundle consistent regardless of whether the dependency is itself bundling-enabled, and — because the copied subtree carries its own already-rewritten links unchanged — nested transitive dependencies resolve correctly with no further rewriting. After staging, `build` MUST rewrite the original cross-package reference inside the copied `SKILL.md` (per rule `05-preserve-relative-paths`) to `dist/<dependency-name>/SKILL.md` (relative from inside `dist/build/`). A minimal illustrative pattern:

```makefile
DEPS := ../shared-skill ../another-skill
BUILD := dist/build

build: clean
	mkdir -p $(BUILD)
	cp SKILL.md $(BUILD)/
	@for d in $(DEPS); do \
	  name=$$(basename $$d); \
	  mkdir -p $(BUILD)/dist/$$name; \
	  if [ -f $$d/Makefile ]; then \
	    $(MAKE) -C $$d build; \
	    cp -R $$d/dist/build/. $(BUILD)/dist/$$name/; \
	  else \
	    cp $$d/SKILL.md $(BUILD)/dist/$$name/; \
	  fi; \
	  sed -i.bak "s#$$d/SKILL.md#dist/$$name/SKILL.md#g" $(BUILD)/SKILL.md && rm -f $(BUILD)/SKILL.md.bak; \
	done

test: build
clean:
	rm -rf dist
```

#### 07-dependency-must-have-own-makefile
A skill that is itself listed as another skill's bundling dependency, and that has cross-skill references of its own, MUST have its own bundling `Makefile`. Without one, only its bare `SKILL.md` can be copied and its own references cannot be resolved automatically. This is not mechanically lint-enforceable; authors MUST self-check it when wiring a dependency into another skill's `Makefile`, and a `make test` run that exercises every resolved reference is the practical backstop for catching a violation.

#### 08-no-cycle-detection
The recursive delegation described in rule `06-recursive-delegation` has no cycle detection. Authors MUST NOT introduce circular bundling dependencies between skills, since that would cause unbounded recursive `make build` invocations.

#### 09-standard-targets
The bundling `Makefile` MUST expose `build`, `test`, and `clean` targets, mirroring the repository root `Makefile` convention. `clean` MUST remove only its own `dist/` and MUST NOT cascade into dependency skills' own `dist/` folders. `test` SHOULD cascade into each bundling-enabled dependency's own `test` target and SHOULD verify the skill still works from its bundled `dist/` output.

#### 10-zip-artifact
`make build` SHOULD also produce a single zip archive of the complete `dist/build/` tree (which already includes every bundled dependency folder from rule `06-recursive-delegation`) as `dist/<skill-name>.zip`. Since `dist/build/` is a subdirectory of `dist/`, the archive naturally cannot include itself: create it directly, for example with `cd dist/build && zip -rq ../<skill-name>.zip .`.

#### 11-build-depends-on-clean
The `build` target MUST depend on the `clean` target (`build: clean`) so every build starts from a clean `dist/`, instead of duplicating `clean`'s removal logic inline.

## References

- [_core-adr-policy-001 - XDRS standards](001-xdrs-standards.md)
- [_core-adr-policy-003 - Skill standards](003-skill-standards.md)
- [_core-adr-policy-008 - Policy structured standards](008-policy-structured-standards.md)
