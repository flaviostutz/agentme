# analyse-account-transactions scripts

Python package behind the `analyse-account-transactions` skill. It converts bank statements to normalized markdown, grounds the classification, keeps the ledger, validates files, stores answers and research, and calculates statistics. See [../SKILL.md](../SKILL.md) for usage by agents.

## Commands

| Command | Purpose |
|---------|---------|
| `aat-normalize` | Subcommands `stage`, `discover`, `rename` and `run`: stage sources, describe them and propose the period, rename the analysis, normalize one file |
| `aat-ground` | Check every normalized row's date and amount against the source file, plus balance chain |
| `aat-ledger` | Apply a classification plan, drop duplicate rows, trim rows outside the period |
| `aat-validate` | Validate normalized files and accounts |
| `aat-answers` | Keep the user's classification answers across analyses |
| `aat-research` | Cache of web research about counterparties (no network calls) |
| `aat-stats` | Exact totals, flows, recurrence, insights, queries and estimates |

Run them without installing anything, using the package folder as the source:

```bash
uvx --from <skill-dir>/scripts aat-stats totals .tmp/my-analysis/normalized/account-pdf.md
```

## Layout

Follows agentme-edr-126:

- `src/analyse_account_transactions/adapters/cli/`: one entry point per command
- `src/analyse_account_transactions/adapters/connectors/`: local file system, source documents (PDF, XLSX) and institution readers
- `src/analyse_account_transactions/app/`: pure logic; ports and the in-memory `ports_mock.py` live next to it
- `src/analyse_account_transactions/shared/`: constants, models, errors
- `tests/`: unit tests mirroring `src/`

## Development

- `make install` syncs the virtualenv into `.cache/venv` from `uv.lock`
- `make lint` runs ruff, ty and pip-audit
- `make lint-fix` applies ruff fixes
- `make test` runs pytest with an 80% line and branch coverage floor
- `make lock` refreshes `uv.lock`
- `make clean` removes caches

The skill-level `Makefile` in the parent folder delegates to these targets and bundles the skill.
