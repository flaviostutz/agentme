# Work dir and files

`.tmp/manage-investment-portfolio-<portfolio>/` (the portfolio name allows letters, digits, `.`, `-`, `_`).

| Path | Content |
| --- | --- |
| `config.yaml` | `base_currency` (EUR), tolerances, `tracked_accounts`; never overwritten by `init` |
| `raw/` | Copies of the statement PDFs, named with the content hash |
| `data/` | Canonical ledger: `accounts`, `events`, `snapshots`, `references`, `unresolved`, `ingest` (JSON, sorted keys) |
| `cache/` | Parse results keyed by file hash, answers and calculation version; `ecb-hist.csv` rates |
| `derived/` | `analysis.json`, `classify-queue.json`, classifications |
| `reports/` | Markdown reports |
| `graphs/` | Mermaid `.mmd` files |
| `exports/portfolio-performance/` | Written by `pm export` only: Portfolio Performance CSV files (see below); fully rewritten on each export |
| `logs/` | JSONL run logs (timestamps live only here) |
| `answers.json` | `answers` (record id to value) and `accept_files` (sha256) |
| `manifest.json` | Hashes of raw and ledger files, used by `validate` |

## Portfolio Performance export

`pm export` turns `data/` into CSV files that Portfolio Performance imports directly and that read back
into the identical ledger (`export` verifies this and exits 1 on any difference).

| File | Content |
| --- | --- |
| `portfolio-transactions.csv` | PP columns: Buy, Sell, Delivery and Transfer in/out (splits, opening lots, transfers) |
| `account-transactions.csv` | PP columns: Deposit, Removal, Interest, Dividend, Fees, Taxes and their reversals (opening cash too) |
| `securities.csv` | One row per instrument: ISIN, ticker, name, currency (most frequent value wins) |
| `accounts.csv` | One securities and one cash account per ledger account (`<id>` and `<id> (<currency>)`) |
| `snapshots.csv`, `references.csv` | Value-only snapshots and reference records, not importable by PP; kept for the round trip |
| `README.txt` | Import order, mapping, and known PP caveats |

Beyond the PP columns, the transaction and account files carry `ledger_*` columns (sequence, event type,
raw type, tax, fee, gross, FX rate, dedupe ref and more), and `snapshots.csv` and `references.csv` carry a
`record_json` cell with the full record, so nothing is lost. PP ignores unknown
columns. Dividend withholding tax has no PP import column and stays only in `ledger_tax`. Text cells that
start with a formula character are prefixed with `'` and decoded on read-back. Numbers use `.` decimals;
`--decimal-comma` switches only Value, Shares, Fees, Taxes and Gross Amount to `,` (the `ledger_*` columns
stay exact, so the round trip is unchanged).

## Determinism

JSON is written with sorted keys and atomic replace. Reports, graphs and data carry no timestamps. A rerun
with the same raw files and answers is byte-identical; a change of the calculation version invalidates the
parse cache.

## Safety

Paths must resolve inside `<cwd>/.tmp/`. A lock file excludes parallel runs on the same work dir. Text in
statements matching instructions aimed at an AI is ignored, listed in `data/ingest.json` and shown by
`validate` as a warning.

## Unresolved record kinds

`unknown-transaction`, `unparsed-sale`, `unparsed-position`, `no-positions`, `rejected-file`, and for files
`file-encrypted`, `file-image-only`, `file-unreadable`, `file-unsupported`, `file-layout-drift`.
