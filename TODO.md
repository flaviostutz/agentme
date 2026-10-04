# TODO

<!-- Format: see agentme-edr-001 -->

## [BACKLOG] 2- Generate Portfolio Performance import files from the portfolio ledger (2026-09-30)

- status: open
- prompt: Implement an export command in `.xdrs/_local/bdrs/finance/skills/portfolio-manager/scripts/` (for example `pm.py export`) that writes Portfolio Performance importable CSV files (accounts, securities, transactions) from `data/events.json` and `data/accounts.json`. Acceptance: importing the files into Portfolio Performance reproduces the ledger's cash and positions; the export is deterministic and has offline tests with fictitious data.
- deferred reason: Out of scope for the first version of the skill.
- why this is important: Lets the user cross-check the results in an established tool.

## [BACKLOG] 1- ETF look-through exposure for the portfolio-manager skill (2026-09-30)

- status: open
- prompt: Investigate and implement ETF look-through exposure (region, sector, top holdings) in the portfolio-manager skill (`scripts/classify.py`, `scripts/report.py`, `markets.md`). Classifications today come only from identifiers with a source URL and an as-of date; extend `classify` to accept constituent weights per ETF and report aggregated exposure.
- deferred reason: Needs a data source for ETF constituents; out of scope for the first version.
- why this is important: Allocation by ETF name hides the real regional and sector exposure.
