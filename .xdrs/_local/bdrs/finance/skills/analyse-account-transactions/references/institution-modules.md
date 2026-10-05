# Institution modules

An institution module is a parser and checker for one statement layout of one institution. Modules live in
`scripts/src/analyse_account_transactions/adapters/connectors/institutions/<name>.py` and are the only place for bank-specific code.
Every other module is generic.
Add a module only when a layout will be read again: 2 or more files with the same layout, or a layout the user
exports every month. For a one-off file, use a mapping or the LLM path
([normalized-format.md](normalized-format.md)).

## Bundled modules

| Module | Institution | Country | Detects | Reads | Check |
|---|---|---|---|---|---|
| `abn_amro` | ABN AMRO | NL | PDF with `ABNANL2A` or `ABN AMRO` and `Date interval` on page 1; tab-separated export (8+ columns, 8-digit date, currency code) | Rows by column position, purchase time from `BEA` lines, balances | Debit and credit counts and totals of the summary |
| `n26` | N26 | DE | PDF with `NTSBDEB1` on page 1 | Rows by column position, balances | Outgoing and incoming totals |
| `revolut` | Revolut | LT | PDF with `Revolut Bank` on page 1 | Money out, Money in, balance columns | Money out and money in of the account summary |
| `splitwise` | Splitwise | (none) | CSV with `Date, Description, Category, Cost, Currency` | The holder's net share per expense, in one currency | Non-zero rows in the base currency equal the ledger row count |

The Splitwise module needs `--set account-holder=<member name>`. Without it, `discover` uses the first member
and lists all members in the notes, so ask the user which one they are. Rows in other currencies are skipped
and listed in the notes; pass `--set currency=<code>` to pick the base currency.

## Interface

```python
# Runtime: Python >=3.10; institution module registered in institutions/__init__.py as INSTITUTION.
"""<Institution>: <which statements and layout>."""

NAME = "example_bank"      # module name used in normalizer: module:<NAME> and --module
BANK = "Example Bank"      # bank header value
COUNTRY = "NL"             # ISO 3166 alpha-2 of the institution, "" when not a bank

def detect(doc) -> bool:
    """True only for this layout. Use a stable, specific marker such as the BIC or a table header."""

def parse(doc, opts: dict) -> tuple:
    """Return (meta, rows, notes). meta uses shared.constants.META_KEYS, rows come from textutil.make_row,
    notes are short strings for the user. Raise shared.errors.LedgerError when the layout is not as expected."""

def check(doc, led) -> list:
    """Compare totals printed in the source with the ledger. Return
    [{"check": "<name>", "ok": bool, "expected": "...", "found": "..."}] or {"check", "ok": False, "message"}."""
```

`doc` is a `shared.models.Doc`:

| Field | Content |
|---|---|
| `kind` | `pdf`, `table`, `text`, `image` or `llm-only` |
| `texts` | Text per PDF page, or the decoded file text |
| `words` | Per PDF page, words with `text`, `x0`, `x1`, `top`, `bottom` (pdfplumber) |
| `table` | Rows of cells for CSV, TXT, TAB and XLSX |
| `lines()` | Text lines of all pages, or table rows joined with ` \| ` |

Use the helpers in `app/textutil.py`: `parse_amount`, `parse_date`, `group_lines` (words into lines by position),
`title_from` (counterparty from a description), `make_row`.

## Adding a module

1. Confirm the layout with the user: the institution, the statement type, and that more files will follow.
2. Copy the closest bundled module. Keep `detect` strict, because the first matching module in
   `default_registry()` wins. Put a new module before any module with a looser `detect`.
3. Read balances and the period only from the printed text. Never compute them. Read the account IBAN from a
   statement-level anchor (header or footer), never the first IBAN in the text: transfer rows print the
   counterparty's IBAN, often of the same bank.
4. Implement `check` with every total the statement prints (counts, debit and credit totals, balances).
5. Expose the module as an `INSTITUTION` object, add it to the list in `default_registry()` and write a test with a synthetic document. Never commit a real statement or
   real account data as a fixture.
6. Run `make -C <skill-dir> lint test`, then `aat-normalize run --force` and `aat-ground` on the files.

## Rules

- Never guess a value that is not printed. When a row is ambiguous (for example two amounts on one line
  without a column), raise `LedgerError` with the date so the file goes to the LLM path.
- Keep the full source text of a row in `description`, and derive `title` from it.
- Report skipped content (other currencies, pending lines) in `notes`, never silently.
- Keep each module under 400 lines, with Python 3.10+ and only `pdfplumber` and `openpyxl` as dependencies.
