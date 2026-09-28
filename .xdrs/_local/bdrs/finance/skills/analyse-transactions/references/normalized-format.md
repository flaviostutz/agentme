# Normalized format

Every source file becomes one normalized file at `.tmp/<id>/.work/normalized/<name>-<ext>.md`. `<name>` is the
source path below `sources/`, with each folder and the file stem slugged (lowercase, `a-z0-9._-`) and joined
with `-`. For example, `sources/2025/ABN Jan.pdf` becomes `normalized/2025-abn-jan-pdf.md`. Scripts write the
file when an institution module or a mapping reads the source; the LLM writes it by hand only on the LLM path,
using the same name.

## File layout

```markdown
# Transactions: <name>-<ext>

source: .tmp/<id>/.work/sources/<relative path>
normalizer: module:<name> | mapping | llm | llm-image
bank: <bank name or unknown>
account-type: current | savings | credit-card | pseudo | unknown
account-holder: <name as printed, or unknown>
iban: <full IBAN or account number, or unknown>
currency: <ISO 4217 code>
period: YYYY-MM-DD..YYYY-MM-DD
opening-balance: <signed value or none>
closing-balance: <signed value or none>

| timestamp | title | value | description | category | flow | relevance | needs-investigation |
|---|---|---|---|---|---|---|---|
| 2026-01-03 14:22 | Albert Heijn | -23.45 | BEA, Betaalpas Albert Heijn 1234 ... | | | | |
```

Header rules:

- Header keys appear in the order above, one per line, as `key: value`. Unknown keys are ignored.
- `source`, `normalizer` and `currency` are required. Missing values are written as `unknown`, and missing
  balances as `none`.
- `period` is the statement period printed in the source. When the source has none, use the first and last
  row dates.
- `account-type: pseudo` marks shared-expense or budgeting apps (for example Splitwise). They do not hold
  money, so they never count as an own account for transfers.

Row rules:

- `timestamp`: `YYYY-MM-DD`, or `YYYY-MM-DD HH:MM` when the description holds the purchase time. Use the
  purchase date when the description prints it, otherwise the booking date.
- `title`: the counterparty in at most 4 words, the same spelling for every row of that counterparty. Leave
  out payment processors (`SumUp *`, `Zettle_*`, `PAYPAL *`), references and legal suffixes (B.V., GmbH, Ltd).
- `value`: signed with 2 decimals from the account holder's view: `-12.34` money out, `+12.34` money in. This
  also applies to credit card statements, where a purchase is negative and a card settlement is positive.
- `description`: the full source text of the row, on one line, at most 399 characters (cut with `...`).
  Pipes are escaped as `\|`.
- The last 4 columns stay empty until classification. `validate.py --phase convert` rejects filled cells.
- One row per booked transaction, in source order. Leave out pending or reserved lines, balance lines, page
  headers and footers.

## LLM path

Use it when `normalize.py run` prints a hint instead of writing the file (no module and no table), or when
the user supplies an image or `xls`/`ods` file.

1. Read the source with your own tools (`read_file` for text, a PDF or image viewer for the rest).
2. Write the file above with `normalizer: llm`, or `normalizer: llm-image` when you transcribed an image or
   a scan without a text layer.
3. Copy every value exactly as printed, and turn it into the signed 2-decimal form. Never compute a value.
4. Write the balances only when the source prints them.
5. Run `ground.py` on the file. `llm-image` files cannot be grounded, and the report lists their rows as
   unverified.

## Mapping for unknown tables

For a CSV, TXT, TAB or XLSX export that no module reads, write `.tmp/<id>/.work/mappings/<name>.json` after reading
the header and a few rows, and pass it with `normalize.py run <source> --id <id> --mapping <file>`.

| Key | Required | Meaning |
|---|---|---|
| `date` | yes | `{"column": "<name>", "format": "<strptime>"}`. Use `"format": "excel"` for serial day numbers, or leave `format` out to try common day-first formats. |
| `amount` | yes | `{"column": "<name>"}` for a signed amount, or `{"debit": "<name>", "credit": "<name>"}` for two unsigned columns. Add `"decimal": ","` or `"decimal": "."` when the separator is ambiguous. |
| `description` | yes | List of column names, joined with a space. |
| `sign` | no | `{"column": "<name>", "debit": ["Af", "D"]}` when the amount is unsigned and another column says debit or credit. |
| `title` | no | Column with a short counterparty name. Without it, the title comes from the description. |
| `currency` | no | `{"column": "<name>"}`. Rows in another currency than `meta.currency` are skipped and listed in the notes. |
| `delimiter` | no | Re-reads a CSV or TXT with this delimiter, when the automatic guess was wrong. |
| `header-row` | no | 1-based row with the column names (default 1). |
| `meta` | no | Header values the table does not hold: `bank`, `iban`, `currency`, `account-holder`, `account-type`, `period`, balances. |

Example for a semicolon CSV with `Af Bij` (debit or credit) and unsigned amounts:

```json
{
  "date": {"column": "Datum", "format": "%Y%m%d"},
  "amount": {"column": "Bedrag (EUR)", "decimal": ","},
  "sign": {"column": "Af Bij", "debit": ["Af"]},
  "description": ["Naam / Omschrijving", "Mededelingen"],
  "title": "Naam / Omschrijving",
  "meta": {"bank": "Example Bank", "currency": "EUR", "account-type": "current"}
}
```

A row with an empty date cell is skipped as a footer. Any other unreadable date or amount stops the run with
the row number, so fix the mapping instead of editing the output. When 2 or more files share an unknown layout,
`discover` lists them under `suggest-module`: offer to write an institution module
([institution-modules.md](institution-modules.md)).

## Working folder

`.tmp/<id>/` holds only `report.md` (written by the LLM) and `.work/`. Nothing is deleted after the run. Paths
below are relative to `.tmp/<id>/.work/`:

| Path | Written by | Content |
|---|---|---|
| `sources/` | `normalize.py stage` | Read-only copies of the inputs, with the folder tree kept |
| `staging.json` | `normalize.py stage` | Origin, copy, hash and skip reason for every input file |
| `mappings/` | LLM | Mapping files for unknown tables |
| `normalized/*.md` | `normalize.py run` or LLM | Normalized files, later classified in place |
| `normalized/*.grounding.json` | `ground.py` | Grounding result per file |
| `normalized/*.snapshot.json` | `validate.py --phase convert` | Row keys, sum and user answers, used to detect changed values |
| `plans/*.json` | LLM | Classification plans for `ledger.py apply` |
| `hidden.json` | LLM | Title to hidden-spending kind map for `stats.py insights` |
| `answers.json` | `answers.py export` | The user's answers, reusable by later analyses |
| `research/cache.json` | `research.py add` | Web findings about counterparties |
