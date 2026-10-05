"""Load a staged source file into a Doc: page text and word positions (PDF), a table (CSV/TXT/TAB/XLSX).

Raw text (XML, OFX, QIF, MT940, JSON) is loaded as text. Images and legacy spreadsheets are marked for the LLM path.
"""

import csv
import io
from decimal import Decimal
from pathlib import Path
from typing import Any

import openpyxl
import pdfplumber

from analyse_account_transactions.shared.constants import IMAGE, LLM_ONLY, PDF, SUPPORTED, TEXT
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Doc

SNIFF_CHARS = 4096


def decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def parse_csv(text: str) -> list[list[str]]:
    try:
        dialect = csv.Sniffer().sniff(text[:SNIFF_CHARS], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if "\t" in text else csv.excel
    rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(text), dialect)]
    return [r for r in rows if any(r)]


def cell_text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, float):
        return str(Decimal(repr(value)))
    return str(value).strip()


def read_xlsx(path: Path) -> list[list[str]]:
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = [[cell_text(c) for c in r] for r in book.worksheets[0].iter_rows(values_only=True)]
    finally:
        book.close()
    return [r for r in rows if any(r)]


def read_pdf(path: Path) -> Doc:
    try:
        with pdfplumber.open(path) as pdf:
            texts = [p.extract_text() or "" for p in pdf.pages]
            words = [p.extract_words() for p in pdf.pages]
    except Exception as err:
        if "password" in type(err).__name__.lower() or "encrypt" in str(err).lower():
            return Doc(path, "pdf", encrypted=True)
        msg = f"cannot read PDF {path.name}: {type(err).__name__}: {err}"
        raise LedgerError(msg) from err
    return Doc(path, "pdf", texts=texts, words=words)


def load(path: Path) -> Doc:
    ext = path.suffix.lower()
    if ext not in SUPPORTED:
        msg = f"unsupported format {ext}"
        raise LedgerError(msg)
    if ext in PDF:
        return read_pdf(path)
    if ext in IMAGE:
        return Doc(path, "image")
    if ext in LLM_ONLY:
        return Doc(path, "llm-only")
    if ext == ".xlsx":
        return Doc(path, "table", table=read_xlsx(path))
    text = decode(path.read_bytes())
    if ext in TEXT:
        return Doc(path, "text", texts=[text])
    return Doc(path, "table", texts=[text], table=parse_csv(text))


class LocalSources:
    """Sources port backed by local files."""

    def load(self, path: Path) -> Doc:
        return load(path)
