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
| `check-input` | List completeness findings (gaps, late starts, stale ends, derived openings, scope); `--from <date>` records the first day the user expects covered |
| `accept` | Close findings with the user's reason and note (`--id` repeatable); stored in `acceptances.json` |
| `analyze` | ECB FX, accounting, reconciliation and performance |
| `classify` | Write the classification queue, import researched classifications, or set one entry with `--isin --security-class ...` |
| `benchmark` | Download monthly closes of a benchmark ticker from Yahoo Finance (only the ticker is sent) and save them with the ticker in `config.yaml`; `--offline` reuses the cached copy |
| `report` | Analyze and write the linked markdown reports (`portfolio.md` is the main entry) and `.mmd`/`.svg` graphs; refused (exit 1, nothing written) while a finding is open or a record is unresolved |
| `export` | Write the ledger as Portfolio Performance CSV files in `exports/portfolio-performance/` and verify they read back into the same ledger; `--decimal-comma` for a German number format; same gate as `report` |
| `run` | `init`, `ingest` and `report` in one step (does not export); same gate as `report` |
| `validate` | Check hashes, rejected files, errors and failed checks |

Run it without installing anything, using the package folder as the source:

```bash
uvx --from <skill-dir>/scripts pm ingest --name main --source .tmp/statements
uvx --from <skill-dir>/scripts pm check-input --name main --from 2025-01-01
```

## Layout

Follows agentme-edr-126:

- `src/portfolio_manager/adapters/cli/`: the `pm` entry point
- `src/portfolio_manager/adapters/connectors/`: local file system work dir, PDF reader, ECB rates, Yahoo Finance
  prices and one module per institution layout
- `src/portfolio_manager/app/`: pure logic (accounting, performance, reconciliation, ledger merge, analysis,
  `reports/` package with one module per report); the PDF reader, institution registry, rates loader and
  chart downloader are injected
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
