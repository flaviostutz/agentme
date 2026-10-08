"""CSV dialect of the Portfolio Performance export: ';' delimiter, '.' decimals, UTF-8, formula-safe text cells."""

import csv
import io

DELIMITER = ";"
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r", "'")

SECURITIES = "securities.csv"
ACCOUNTS = "accounts.csv"
ACCOUNT_TRANSACTIONS = "account-transactions.csv"
PORTFOLIO_TRANSACTIONS = "portfolio-transactions.csv"
SNAPSHOTS = "snapshots.csv"
REFERENCES = "references.csv"
README = "README.txt"

# Column names follow the Portfolio Performance CSV import so the wizard maps them automatically.
SECURITY_COLUMNS = ("ISIN", "Ticker Symbol", "Security Name", "Currency", "Note")
TRANSACTION_COLUMNS = (
    "Date",
    "Time",
    "Type",
    "Value",
    "Shares",
    "ISIN",
    "Ticker Symbol",
    "Security Name",
    "Fees",
    "Taxes",
    "Gross Amount",
    "Currency Gross Amount",
    "Note",
    "Cash Account",
    "Securities Account",
)
# Extra columns (ignored by Portfolio Performance) carry every ledger field so the files rebuild the ledger exactly.
LEDGER_COLUMNS = (
    "ledger_seq",
    "ledger_type",
    "ledger_account",
    "ledger_time",
    "ledger_isin",
    "ledger_symbol",
    "ledger_name",
    "ledger_quantity",
    "ledger_currency",
    "ledger_cash",
    "ledger_fee",
    "ledger_tax",
    "ledger_ref",
    "ledger_price",
    "ledger_gross",
    "ledger_fx_rate",
    "ledger_raw_type",
)
ACCOUNT_COLUMNS = (
    "Cash Account",
    "Securities Account",
    "ledger_account",
    "ledger_institution",
    "ledger_currency",
    "ledger_mode",
    "ledger_opening_date",
    "ledger_opening_cash",
)
SNAPSHOT_COLUMNS = ("account", "date", "currency", "cash", "positions_value", "total", "record_json")
REFERENCE_COLUMNS = ("kind", "account", "security", "from", "to", "record_json")
# Columns Portfolio Performance parses as numbers; only these switch to ',' decimals (ledger_* stay exact with '.').
NUMBER_COLUMNS = ("Value", "Shares", "Fees", "Taxes", "Gross Amount")


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def encode_cell(value: object) -> str:
    """Text that a spreadsheet could read as a formula gets a leading quote; the reader removes it again."""
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_STARTS) and not _is_number(text):
        return "'" + text
    return text


def decode_cell(text: str) -> str:
    return text[1:] if text.startswith("'") and not _is_number(text) else text


def _cell(column: str, value: object, *, decimal_comma: bool) -> str:
    if decimal_comma and column in NUMBER_COLUMNS:
        return ("" if value is None else str(value)).replace(".", ",")
    return encode_cell(value)


def dumps(columns: tuple[str, ...], rows: list[dict], *, decimal_comma: bool = False) -> str:
    """Header plus rows with exactly `columns`; missing keys become empty cells."""
    out = io.StringIO(newline="")
    writer = csv.writer(out, delimiter=DELIMITER, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_cell(c, row.get(c), decimal_comma=decimal_comma) for c in columns])
    return out.getvalue()


def loads(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=DELIMITER)
    return [{k: decode_cell(v or "") for k, v in row.items()} for row in reader]
