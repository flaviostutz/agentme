# Work dir and files

One run folder per portfolio, `.tmp/manage-investment-portfolio/<portfolio>/` (the portfolio name allows lowercase
letters, digits and single `-`). Disposable caches live apart, in `.tmp/manage-investment-portfolio/.work/<portfolio>/`:
`parse-*.json` (parse results keyed by file hash, answers, adapter sources and calculation version), `ecb-hist.csv` (ECB rates) and
`yahoo-<ticker>.json` (last benchmark response). `.work/` is safe to delete at any time; the next run refetches
or reparses what is missing. Nothing is stored directly in `.tmp/manage-investment-portfolio/`.

| Path | Content |
| --- | --- |
| `config.yaml` | `base_currency` (EUR), tolerances, `tracked_accounts`, `benchmark.ticker` (set by `pm benchmark`); never overwritten by `init` |
| `raw/` | Copies of the statement PDFs, named with the content hash |
| `data/` | Canonical ledger: `accounts`, `events`, `snapshots`, `references`, `unresolved`, `ingest` (JSON, sorted keys), and `benchmark.json` (monthly closes of the benchmark, written by `pm benchmark`) |
| `derived/` | `analysis.json`, `classify-queue.json`, `securities.json` |
| `reports/` | Markdown reports: `portfolio.md` is the main entry and every report links to the others |
| `graphs/` | Mermaid `.mmd` files and `wealth-bridge.svg` |
| `exports/portfolio-performance/` | Written by `pm export` only: Portfolio Performance CSV files (see below); fully rewritten on each export |
| `logs/` | JSONL run logs (timestamps live only here) |
| `answers.json` | `answers` (record id to value) and `accept_files` (sha256) |
| `acceptances.json` | Written by `pm check-input --from` and `pm accept`: `settings.expected_start` and `accepted` (finding id, kind, reason, note). Tracked by `validate`; never edit by hand |
| `manifest.json` | Hashes of raw and ledger files, used by `validate` |

## Completeness findings

`pm check-input` computes findings from the ledger and `acceptances.json` and writes `derived/input-check.json`.
A finding id is a hash of its kind, account and key facts, so a new statement that fixes the cause removes the
finding and a changed cause creates a new id that needs a new decision. `pm report`, `pm run` and `pm export`
are refused while a finding is open or a record is unresolved.

| Kind | Raised when | Reasons the user may give |
| --- | --- | --- |
| `gap` | A period between two statements of one account is not covered | `opened-on-date`, `no-activity`, `unobtainable`, `accept-as-is` |
| `late-start` | The first statement starts more than 35 days after the expected start, or the account has only reference statements | same four |
| `stale-end` | An account's last statement is more than 35 days before the latest data of any account | same four |
| `derived-opening` | An opening position was derived without a cost basis | same four |
| `check-warn` | A statement check failed softly | `unobtainable`, `accept-as-is` |
| `overlap` | Overlapping statements disagree (`overlap-mismatch`) or double-count period flows (`period-flows-overlap`) | `unobtainable`, `accept-as-is` |
| `scope` | Which accounts are covered; the user confirms nothing else is missing | `accept-as-is` |
| `expected-start` | No expected start date was given with `--from` yet | `accept-as-is` |

`pm accept --id <id> [--id ...] --reason <reason> --note "<text>"` stores one record per id. The note is the
user's own words: one line, 1 to 200 characters. An invalid kind and reason pair, an unknown id or a missing
note exits 2 and stores nothing. `portfolio.md` shows the reason and note per account.

## Portfolio Performance export

`pm export` turns `data/` into CSV files that Portfolio Performance imports directly and that read back
into the identical ledger (`export` verifies this and exits 1 on any difference).

| File | Content |
| --- | --- |
| `portfolio-transactions.csv` | PP columns: Buy, Sell, Delivery and Transfer in/out (splits, opening lots, transfers) |
| `account-transactions.csv` | PP columns: Deposit, Removal, Interest, Dividend, Fees, Taxes and their reversals (opening cash too) |
| `securities.csv` | One row per instrument: ISIN, ticker, name, currency (most frequent value wins) |
| `accounts.csv` | One securities and one cash account per investment account (`<id>` and `<id> (<currency>)`) |
| `snapshots.csv`, `references.csv` | Value-only snapshots and reference records, not importable by PP; kept for the round trip |
| `README.txt` | Import order, mapping, and known PP caveats |

Beyond the PP columns, the transaction and account files carry `ledger_*` columns (sequence, event type,
raw type, tax, fee, gross, FX rate, dedupe ref and more), and `snapshots.csv` and `references.csv` carry a
`record_json` cell with the full record, so nothing is lost. PP ignores unknown
columns. Dividend withholding tax has no PP import column and stays only in `ledger_tax`. Text cells that
start with a formula character are prefixed with `'` and decoded on read-back. Numbers use `.` decimals;
`--decimal-comma` switches only Value, Shares, Fees, Taxes and Gross Amount to `,` (the `ledger_*` columns
stay exact, so the round trip is unchanged).

## Reports and graphs

| Report | Content |
| --- | --- |
| `portfolio.md` | Wealth since inception per investment account, last 12 months (TWR, XIRR, net flows), wealth bridge, top 10 open positions, benchmark, performance, trust and notes |
| `monthly.md`, `yearly.md` | Performance per month (latest 24) and per year for the portfolio and each investment account, with a XIRR chart each. Every row has a Window column; TWR, XIRR and period return of a row share that window |
| `investment-accounts.md` | Wealth share per investment account, then one section per account: cash, positions, flows, data quality |
| `securities.md` | Open positions across investment accounts, contribution to the gain, lots per account |
| `income.md` | Dividends and interest: trailing 12 months, per year, per payer, withholding drag |
| `risk.md` | CAGR, volatility, best/worst month and drawdown from inception and for the latest 12 complete calendar months, CAGR per year and the volatility vs CAGR quadrant |
| `markets.md` | Allocation by classification; only when classifications exist |
| `concepts.md` | Plain-language definitions that the other reports link to |

Graphs: `wealth`, `wealth-by-account`, `twr-12m`, `xirr-12m`, `net-flows-12m`, `monthly-xirr-<scope>`,
`yearly-xirr-<scope>`, `allocation`, `income`, `drawdown`, `cagr-per-year` and `benchmark` as Mermaid, and
`wealth-bridge.svg`, `quadrant-inception.svg` and `quadrant-12m.svg` (fixed-size SVGs with a white background).
`<scope>` is `portfolio` or the account id as a file-name slug. The 12-month charts are drawn only when the window
is a full 12 months and only from complete points; a XIRR chart needs two complete rows. Months without a value
are omitted from a chart, never drawn as zero.

## Benchmark

`pm benchmark --ticker <ticker>` downloads monthly closes from the unofficial Yahoo Finance chart endpoint (no key;
only the ticker is sent) and stores them in `data/benchmark.json`. Offline runs reuse `.work/<portfolio>/yahoo-<ticker>.json`.
Prices in another currency are converted to EUR with the ECB rate of the month, so the comparison is marked
approximate. A response that does not parse is rejected and nothing is stored.

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
