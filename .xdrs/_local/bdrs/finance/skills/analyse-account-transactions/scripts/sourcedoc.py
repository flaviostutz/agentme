# Runtime: Python >=3.10; imported by normalize.py and ground.py, which declare pdfplumber and openpyxl.
"""Load a staged source file into a Doc: page text and word positions (PDF), a table (CSV/TXT/TAB/XLSX)
or raw text (XML, OFX, QIF, MT940, JSON). Images and legacy spreadsheets are marked for the LLM path."""

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from ledger import LedgerError

PDF = {".pdf"}
TABLE = {".csv", ".txt", ".tab", ".xlsx"}
TEXT = {".xml", ".ofx", ".qfx", ".qif", ".sta", ".mt940", ".940", ".json"}
IMAGE = {".png", ".jpg", ".jpeg", ".heic"}
LLM_ONLY = {".xls", ".ods"}
SUPPORTED = PDF | TABLE | TEXT | IMAGE | LLM_ONLY


@dataclass
class Doc:
    path: Path
    kind: str  # pdf | table | text | image | llm-only
    texts: list = field(default_factory=list)  # one string per PDF page, or one for text files
    words: list = field(default_factory=list)  # pdfplumber word dicts per PDF page
    table: list = field(default_factory=list)  # rows of strings
    encrypted: bool = False

    @property
    def ext(self) -> str:
        return self.path.suffix.lower()

    @property
    def has_text(self) -> bool:
        return any(t.strip() for t in self.texts) or bool(self.table)

    def lines(self) -> list:
        """All source lines used by grounding: text lines, or table rows joined with ' | '."""
        if self.table:
            return [" | ".join(r) for r in self.table]
        return [line for t in self.texts for line in t.splitlines()]


def decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def parse_csv(text: str) -> list:
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if "\t" in text else csv.excel
    rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(text), dialect)]
    return [r for r in rows if any(r)]


def cell_text(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, float):
        return str(Decimal(repr(value)))
    return str(value).strip()


def read_xlsx(path: Path) -> list:
    import openpyxl

    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = [[cell_text(c) for c in r] for r in book.worksheets[0].iter_rows(values_only=True)]
    finally:
        book.close()
    return [r for r in rows if any(r)]


def read_pdf(path: Path) -> Doc:
    import pdfplumber

    try:
        with pdfplumber.open(path) as pdf:
            texts = [p.extract_text() or "" for p in pdf.pages]
            words = [p.extract_words() for p in pdf.pages]
    except Exception as err:  # pdfminer raises PDFPasswordIncorrect and others for locked/corrupt files
        if "password" in type(err).__name__.lower() or "encrypt" in str(err).lower():
            return Doc(path, "pdf", encrypted=True)
        raise LedgerError(f"cannot read PDF {path.name}: {type(err).__name__}: {err}") from err
    return Doc(path, "pdf", texts=texts, words=words)


def load(path: Path) -> Doc:
    ext = path.suffix.lower()
    if ext not in SUPPORTED:
        raise LedgerError(f"unsupported format {ext}")
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
