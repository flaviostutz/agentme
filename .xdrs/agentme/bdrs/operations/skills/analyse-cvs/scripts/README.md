# analyse-cvs scripts

Python package behind the `analyse-cvs` skill. It stages candidate documents under safe names, redacts protected attributes from converted markdown, organises source folders per candidate, derives slugs, computes scores exactly, checks and ranks the report, and fills the Sources and Candidates tables. All arithmetic uses `Decimal`/`Fraction`, never `float` (agentme-edr-105). See [../SKILL.md](../SKILL.md) for usage by agents.

## Commands

| Command | Purpose |
|---------|---------|
| `cvs-stage <folder> [--json]` | Copy supported files from `.tmp/<folder>` to `md/.staging/doc-NN.<ext>` and write the manifest |
| `cvs-redact <file> [--json]` | Redact labelled protected attributes and images from a markdown file, in place |
| `cvs-organise <folder> <plan.json> [--json]` | Rename or merge source folders and move files into one folder per candidate |
| `cvs-slug <name>... [--existing a,b] [--json]` | Derive ASCII kebab-case slugs, suffixing duplicates with `-2`, `-3` |
| `cvs-score dryrun <report> <name> --adjustments <json>` | Apply scenario adjustments to one row and print the new aspect scores and Base (read-only) |
| `cvs-score overall <report> <name>` | Compute Overall and the invite flag from Base and Credibility (read-only) |
| `cvs-check <report> --stage criteria\|scores\|scenarios\|interview [--name N]` | Mechanical checks; exit 1 on errors, warnings are listed (read-only) |
| `cvs-rank <report> [--write]` | Rank by unrounded Overall; with `--write` sort the Candidates table and write the interview list skeleton |
| `cvs-sources <folder> <report> <docs.json>` | Rename converted files, fill Sources and Candidates, delete staging |

Run them without installing anything, using the package folder as the source:

```bash
uvx --from <skill-dir>/scripts cvs-stage .tmp/my-cvs --json
```

## Layout

Follows agentme-edr-126:

- `src/analyse_cvs/adapters/cli/`: one entry point per command
- `src/analyse_cvs/adapters/connectors/local_fs/`: filesystem access
- `src/analyse_cvs/app/`: staging, redaction, organising, slugs, scoring, checking, ranking and registering logic
- `src/analyse_cvs/shared/`: shared constants and exact decimal helpers
- `tests/`: unit tests mirroring `src/`

## Development

- `make install` syncs the virtualenv into `.cache/venv` from `uv.lock`
- `make lint` runs ruff, ty and pip-audit
- `make lint-fix` applies ruff fixes
- `make test` runs pytest with an 80% line and branch coverage floor
- `make lock` refreshes `uv.lock`
- `make clean` removes caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill.
