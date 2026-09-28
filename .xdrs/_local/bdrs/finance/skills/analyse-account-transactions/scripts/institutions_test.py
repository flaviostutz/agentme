# Tests for the bundled institution modules, using synthetic PDFs and tables built in conftest.py.
from pathlib import Path

import institutions
import pytest
import sourcedoc
from conftest import ABN_PAGES, HOLDER, N26_PAGES, REVOLUT_PAGES, SPLITWISE_CSV, make_pdf
from institutions import abn_amro, n26, revolut, splitwise
from ledger import Ledger, LedgerError


def pdf_doc(tmp_path: Path, pages: list, name: str = "s.pdf"):
    path = tmp_path / name
    path.write_bytes(make_pdf(pages))
    return sourcedoc.load(path)


def csv_doc(tmp_path: Path, text: str, name: str = "s.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return sourcedoc.load(path)


def values(rows):
    return [(r.date, str(r.value), r.title) for r in rows]


def test_find_picks_each_module(tmp_path):
    assert institutions.find(pdf_doc(tmp_path, ABN_PAGES, "a.pdf")) is abn_amro
    assert institutions.find(pdf_doc(tmp_path, N26_PAGES, "n.pdf")) is n26
    assert institutions.find(pdf_doc(tmp_path, REVOLUT_PAGES, "r.pdf")) is revolut
    assert institutions.find(csv_doc(tmp_path, SPLITWISE_CSV)) is splitwise
    assert institutions.find(csv_doc(tmp_path, "a,b\n1,2\n", "o.csv")) is None
    assert institutions.find(pdf_doc(tmp_path, [[(50, 800, "Some other bank")]], "x.pdf")) is None


def test_by_name():
    assert institutions.by_name("n26") is n26
    with pytest.raises(KeyError, match="unknown institution module"):
        institutions.by_name("nope")


def test_abn_amro_pdf(tmp_path):
    doc = pdf_doc(tmp_path, ABN_PAGES)
    meta, rows, notes = abn_amro.parse(doc, {})
    assert meta["account-holder"] == HOLDER
    assert meta["iban"] == "NL00ABNA0000000001"
    assert meta["account-type"] == "current"
    assert meta["period"] == "2026-01-01..2026-01-31"
    assert (meta["opening-balance"], meta["closing-balance"], meta["currency"]) == ("+100.00", "+140.00", "EUR")
    assert values(rows) == [("2026-01-02", "-10.00", "Coffee Bar"), ("2026-01-05", "50.00", "ACME SALARY")]
    assert rows[0].timestamp == "2026-01-02 08:30"
    assert rows[1].description.endswith("Omschrijving: payroll")
    assert notes == []
    findings = abn_amro.check(doc, Ledger(meta, rows))
    assert [f["ok"] for f in findings] == [True, True]


def test_abn_amro_check_mismatch_and_missing_summary(tmp_path):
    doc = pdf_doc(tmp_path, ABN_PAGES)
    meta, rows, _ = abn_amro.parse(doc, {})
    assert [f["ok"] for f in abn_amro.check(doc, Ledger(meta, rows[:1]))] == [False, False]
    bare = pdf_doc(tmp_path, [ABN_PAGES[0][:13]], "bare.pdf")
    assert [f.get("message", "") for f in abn_amro.check(bare, Ledger(meta, rows))] == [
        "summary counts not found on page 1", "summary totals not found on page 1"]


def test_abn_amro_row_with_two_amounts_fails(tmp_path):
    page = [*ABN_PAGES[0][:13], (480, 680, "1,00", "right")]
    with pytest.raises(LedgerError, match="expected one amount"):
        abn_amro.parse(pdf_doc(tmp_path, [page]), {})


def test_abn_amro_titles_and_timestamps():
    assert abn_amro.title("GEA, Betaalpas ATM 12") == "Cash withdrawal"
    assert abn_amro.title("Naam: ACME Energy B.V. Omschrijving: bill") == "ACME Energy"
    assert abn_amro.title("12:30 998877") == "998877"
    assert abn_amro.title("BEA, Betaalpas 33/45,PAS022 NR:61SCC9, 18.04.26/08:21 'S-GRAVENHAGE") == "33/45"
    assert abn_amro.title("BEA, Apple Pay U2pi B.V. NR:19ZR60, 28.08.26/09:57 'S-GRAVENHAGE") == "U2pi B.V"
    assert abn_amro.timestamp_for("2026-01-02", "no time") == "2026-01-02"
    assert abn_amro.timestamp_for("2026-01-02", "31.02.26/10:00") == "2026-01-02"


def test_abn_amro_tab_export():
    table = [["NL00ABNA0000000001", "EUR", "20260102", "100,00", "90,00", "20260102", "-10,00", "BEA, Shop A,PAS1"],
             ["NL00ABNA0000000001", "EUR", "20260103", "90,00", "140,00", "20260103", "50,00", "Naam: ACME Kenmerk: x"]]
    doc = sourcedoc.Doc(Path("x.tab"), "table", table=table)
    assert abn_amro.detect(doc)
    meta, rows, _ = abn_amro.parse(doc, {})
    assert (meta["iban"], meta["opening-balance"], meta["closing-balance"]) == ("NL00ABNA0000000001", "+100.00",
                                                                                "+140.00")
    assert values(rows) == [("2026-01-02", "-10.00", "Shop A"), ("2026-01-03", "50.00", "ACME")]
    assert abn_amro.check(doc, Ledger(meta, rows)) == []
    assert not abn_amro.detect(sourcedoc.Doc(Path("x.png"), "image"))


def test_n26_pdf(tmp_path):
    doc = pdf_doc(tmp_path, N26_PAGES)
    meta, rows, _ = n26.parse(doc, {})
    assert meta["account-holder"] == HOLDER
    assert meta["iban"] == "DE00100110010000000001"
    assert meta["period"] == "2026-01-01..2026-01-31"
    assert (meta["opening-balance"], meta["closing-balance"]) == ("+100.00", "+140.00")
    assert values(rows) == [("2026-01-02", "-10.00", "Coffee Bar"), ("2026-01-05", "50.00", "ACME Salary")]
    assert rows[0].description == "Coffee Bar Mastercard • Food"
    assert all(f["ok"] for f in n26.check(doc, Ledger(meta, rows)))
    assert [f["ok"] for f in n26.check(doc, Ledger(meta, rows[:1]))] == [True, False]


def test_n26_without_rows_or_summary(tmp_path):
    empty = pdf_doc(tmp_path, [[(50, 800, "BIC: NTSBDEB1")]])
    with pytest.raises(LedgerError, match="without transaction rows"):
        n26.parse(empty, {})
    assert [f["message"] for f in n26.check(empty, Ledger({}, []))] == [
        "'Outgoing transactions' summary not found", "'Incoming transactions' summary not found"]


def test_revolut_pdf(tmp_path):
    doc = pdf_doc(tmp_path, REVOLUT_PAGES)
    meta, rows, _ = revolut.parse(doc, {})
    assert (meta["currency"], meta["iban"], meta["account-holder"]) == ("EUR", "LT000000000000000001", HOLDER)
    assert meta["period"] == "2026-01-01..2026-01-31"
    assert (meta["opening-balance"], meta["closing-balance"]) == ("+100.00", "+140.00")
    assert values(rows) == [("2026-01-02", "-10.00", "Coffee Bar"), ("2026-01-05", "50.00", "ACME")]
    assert rows[1].description == "Transfer from ACME Reference: salary"
    assert all(f["ok"] for f in revolut.check(doc, Ledger(meta, rows)))
    assert not all(f["ok"] for f in revolut.check(doc, Ledger(meta, rows[1:])))


def test_revolut_errors(tmp_path):
    page = [*REVOLUT_PAGES[0][:15], (480, 680, "€1.00", "right")]
    with pytest.raises(LedgerError, match="expected one amount"):
        revolut.parse(pdf_doc(tmp_path, [page]), {})
    bare = pdf_doc(tmp_path, [[(50, 800, "Revolut Bank UAB")]], "bare.pdf")
    assert revolut.check(bare, Ledger({}, []))[0]["ok"] is False
    assert revolut.columns([{"text": "Date", "x1": 1}, {"text": "Description", "x1": 2}, {"text": "Balance", "x1": 3}]) \
        is None


def test_splitwise(tmp_path):
    doc = csv_doc(tmp_path, SPLITWISE_CSV)
    meta, rows, notes = splitwise.parse(doc, {"account-holder": HOLDER})
    assert values(rows) == [("2026-01-03", "30.00", "Dinner"), ("2026-01-10", "-10.00", "Groceries")]
    assert meta["closing-balance"] == "+20.00"
    assert meta["opening-balance"] == "+0.00"
    assert meta["account-type"] == "shared-expenses"
    assert notes == ["skipped 1 row(s) in USD (not the base currency EUR)"]
    assert "John Roe -30.00" in rows[0].description
    led = Ledger({**meta, "period": "2026-01-01..2026-01-31"}, rows)
    assert splitwise.check(doc, led)[0]["ok"]
    assert not splitwise.check(doc, Ledger(led.meta, rows[:1]))[0]["ok"]


def test_splitwise_member_selection(tmp_path):
    doc = csv_doc(tmp_path, SPLITWISE_CSV)
    with pytest.raises(LedgerError, match="set account-holder"):
        splitwise.parse(doc, {})
    meta, _, notes = splitwise.parse(doc, {"discover": True})
    assert meta["account-holder"] == HOLDER
    assert notes[-1].startswith("members")
    meta, rows, _ = splitwise.parse(doc, {"account-holder": "John Roe", "currency": "USD"})
    assert values(rows) == [("2026-01-12", "-7.50", "Taxi")]
    assert meta["closing-balance"] == "-7.50"
