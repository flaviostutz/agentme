# Tests for sourcedoc.py (loading sources) and mapping.py (LLM-written column mappings).
from pathlib import Path

import mapping
import openpyxl
import pytest
import sourcedoc
from conftest import N26_PAGES, make_pdf
from ledger import LedgerError


def test_load_kinds(tmp_path):
    (tmp_path / "a.csv").write_bytes("Datum;Naam;Bedrag\n02-01-2026;Caf\xe9;1,00\n".encode("cp1252"))
    doc = sourcedoc.load(tmp_path / "a.csv")
    assert doc.kind == "table" and doc.table[1] == ["02-01-2026", "Café", "1,00"]
    assert doc.lines()[0] == "Datum | Naam | Bedrag"
    (tmp_path / "b.ofx").write_text("<OFX>\n<STMTTRN>\n", encoding="utf-8")
    doc = sourcedoc.load(tmp_path / "b.ofx")
    assert (doc.kind, doc.lines(), doc.has_text) == ("text", ["<OFX>", "<STMTTRN>"], True)
    for name, kind in (("c.png", "image"), ("d.xls", "llm-only")):
        (tmp_path / name).write_bytes(b"x")
        assert sourcedoc.load(tmp_path / name).kind == kind
    (tmp_path / "e.doc").write_bytes(b"x")
    with pytest.raises(LedgerError, match="unsupported format"):
        sourcedoc.load(tmp_path / "e.doc")


def test_decode_fallbacks():
    assert sourcedoc.decode("\ufeffabc".encode()) == "abc"
    assert sourcedoc.decode(b"caf\xe9") == "café"
    assert sourcedoc.decode(b"\x81\x8d") == "\x81\x8d"


def test_parse_csv_without_dialect():
    assert sourcedoc.parse_csv("single\n\nvalue\n") == [["single"], ["value"]]
    assert sourcedoc.parse_csv("a\tb\n1\t2\n") == [["a", "b"], ["1", "2"]]


def test_xlsx(tmp_path):
    import datetime

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(["Date", "Amount", "Note", None])
    sheet.append([datetime.datetime(2026, 1, 2), 12.5, " Shop ", None])  # noqa: DTZ001 - xlsx cells are naive
    sheet.append([None, None, None, None])
    book.save(tmp_path / "x.xlsx")
    doc = sourcedoc.load(tmp_path / "x.xlsx")
    assert doc.table == [["Date", "Amount", "Note", ""], ["2026-01-02", "12.5", "Shop", ""]]


def test_pdf(tmp_path):
    (tmp_path / "s.pdf").write_bytes(make_pdf(N26_PAGES))
    doc = sourcedoc.load(tmp_path / "s.pdf")
    assert doc.kind == "pdf" and len(doc.texts) == 2 and doc.has_text and not doc.encrypted
    assert "Coffee Bar 02.01.2026 -10,00€" in doc.lines()
    (tmp_path / "bad.pdf").write_bytes(b"not a pdf")
    with pytest.raises(LedgerError, match="cannot read PDF"):
        sourcedoc.load(tmp_path / "bad.pdf")


def test_pdf_password(tmp_path, monkeypatch):
    import pdfplumber

    class PDFPasswordIncorrect(Exception):
        pass

    def locked(path):
        raise PDFPasswordIncorrect()

    monkeypatch.setattr(pdfplumber, "open", locked)
    assert sourcedoc.load(tmp_path / "x.pdf").encrypted


BANK_CSV = ("Datum;Naam;Bedrag;Af Bij;Munt\n"
            "02-01-2026;Coffee Bar;3,50;Af;EUR\n"
            "03-01-2026;ACME;1.200,00;Bij;EUR\n"
            "04-01-2026;Hotel;90,00;Af;USD\n"
            ";Total;;;\n")
SPEC = {"delimiter": ";", "date": {"column": "Datum", "format": "%d-%m-%Y"},
        "amount": {"column": "Bedrag", "decimal": ","}, "sign": {"column": "Af Bij", "debit": ["Af"]},
        "description": ["Naam", "Af Bij"], "title": "Naam", "currency": {"column": "Munt"},
        "meta": {"bank": "Test Bank"}}


def bank_doc(tmp_path: Path, text: str = BANK_CSV):
    (tmp_path / "t.csv").write_text(text, encoding="utf-8")
    return sourcedoc.load(tmp_path / "t.csv")


def test_mapping_signed(tmp_path):
    meta, rows, notes = mapping.apply(bank_doc(tmp_path), SPEC)
    assert [(r.date, str(r.value), r.title, r.description) for r in rows] == [
        ("2026-01-02", "-3.50", "Coffee Bar", "Coffee Bar Af"), ("2026-01-03", "1200.00", "ACME", "ACME Bij")]
    assert meta == {"bank": "Test Bank", "currency": "EUR"}
    assert notes == ["skipped 1 row(s) without a date", "skipped 1 row(s) in USD (not EUR)"]


def test_mapping_debit_credit_and_excel(tmp_path):
    text = "x\nWhen,Out,In,Who\n46024,5.00,,Shop\n46025,,20.00,Boss\n"
    spec = {"header-row": 2, "date": {"column": "When", "format": "excel"},
            "amount": {"debit": "Out", "credit": "In", "decimal": "."}, "description": ["Who"]}
    _, rows, notes = mapping.apply(bank_doc(tmp_path, text), spec)
    assert [(r.date, str(r.value), r.title) for r in rows] == [("2026-01-02", "-5.00", "Shop"),
                                                                ("2026-01-03", "20.00", "Boss")]
    assert notes == []


@pytest.mark.parametrize(("spec", "message"), [
    ([], "must be a JSON object"),
    ({**SPEC, "extra": 1}, "unknown keys"),
    ({k: v for k, v in SPEC.items() if k != "date"}, "'date' is required"),
    ({**SPEC, "amount": {"debit": "Bedrag"}}, "needs 'column' or both"),
    ({**SPEC, "meta": {"colour": "red"}}, "mapping meta: unknown keys"),
    ({**SPEC, "header-row": 9}, "outside the table"),
    ({**SPEC, "title": "Nope"}, "column 'Nope' not in header"),
    ({**SPEC, "date": {"column": "Datum", "format": "%Y/%m/%d"}}, "row 2"),
])
def test_mapping_errors(tmp_path, spec, message):
    with pytest.raises(LedgerError, match=message):
        mapping.apply(bank_doc(tmp_path), spec)
