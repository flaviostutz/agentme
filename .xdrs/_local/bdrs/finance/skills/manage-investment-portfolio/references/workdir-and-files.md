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
| `logs/` | JSONL run logs (timestamps live only here) |
| `answers.json` | `answers` (record id to value) and `accept_files` (sha256) |
| `manifest.json` | Hashes of raw and ledger files, used by `validate` |

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
