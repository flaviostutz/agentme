# manage-investment-portfolio scripts

Python package behind the `manage-investment-portfolio` skill. It parses broker and bank statement PDFs into a canonical
ledger, reconciles it against the statements, computes performance, and writes markdown reports and graphs.
See [../SKILL.md](../SKILL.md) for usage by agents.

## Commands

One CLI, `pm`, with these subcommands (all take `--name <work-name>`):

| Subcommand | Purpose |
|------------|---------|
| `init` | Create the work folder and `config.yaml` |
| `inspect` | Report page counts, status and detected institution of PDFs, never amounts |
| `ingest` | Copy PDFs to `raw/`, parse them with the institution adapters and merge into the ledger |
| `answer` | Store an answer for an unresolved record, or accept a rejected file, then re-ingest |
| `analyze` | ECB FX, accounting, reconciliation and performance |
| `classify` | Write the classification queue or import researched classifications |
| `report` | Analyze and write markdown reports and `.mmd` graphs |
| `run` | `init`, `ingest` and `report` in one step |
| `validate` | Check hashes, rejected files, errors and failed checks |

Run it without installing anything, using the package folder as the source:

```bash
uvx --from <skill-dir>/scripts pm run --name main --offline --source .tmp/statements
```

## Layout

Follows agentme-edr-126:

- `src/portfolio_manager/adapters/cli/`: the `pm` entry point
- `src/portfolio_manager/adapters/connectors/`: local file system work dir, PDF reader, ECB rates and one module
  per institution layout
- `src/portfolio_manager/app/`: pure logic (accounting, performance, reconciliation, ledger merge, analysis,
  reports); the PDF reader, institution registry and rates loader are injected
- `src/portfolio_manager/shared/`: models, errors and value helpers
- `tests/`: unit tests mirroring `src/`, on synthetic documents only

## Development

- `make install` syncs the virtualenv into `.cache/venv` from `uv.lock`
- `make lint` runs ruff, ty and pip-audit
- `make lint-fix` applies ruff fixes
- `make test` runs pytest with an 80% line and branch coverage floor
- `make lock` refreshes `uv.lock`
- `make clean` removes caches

The ported parsers and analysis code are dense; `pyproject.toml` relaxes a few complexity, annotation, line
length and typing rules for `app/`, `adapters/connectors/` and `analyze.py` only. Tighten them when touching
those modules.

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill.
