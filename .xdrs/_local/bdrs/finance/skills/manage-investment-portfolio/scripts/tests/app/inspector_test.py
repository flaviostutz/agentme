"""Inspector fingerprints: structure only, never amounts."""

from portfolio_manager.adapters.connectors.pdf.pdf_reader import read_pdf
from portfolio_manager.app import inspector
from samples_test import trading212


def test_inspector_reports_structure_without_amounts(make_pdf):
    path = make_pdf(trading212(), "t212.pdf")
    info = inspector.inspect_pdf(path, read_pdf)
    assert info["status"] == "ok" and info["institutions"]["trading212"] >= 1
    assert info["date_formats"] and info["isin_count"] >= 1
    assert "1,010.85" not in str(info) and "ABC1234" not in str(info)
    locked = inspector.inspect_pdf(make_pdf([["x"]], "locked.pdf", password="pw"), read_pdf)
    assert locked["status"] == "encrypted" and "pages" not in locked
