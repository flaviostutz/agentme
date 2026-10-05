# Runtime: pytest; Revolut statement and P&L adapters on fictitious layouts.
from decimal import Decimal

import pytest

from portfolio_manager.adapters.connectors.institutions import revolut_pnl, revolut_statement
from portfolio_manager.shared.errors import PmError
from samples_test import ISIN_A
from samples_test import revolut_pnl as pnl_pages
from samples_test import revolut_statement as statement_pages


def test_statement_is_detected_and_other_documents_are_not(make_doc):
    assert revolut_statement.detect(make_doc(statement_pages()))
    assert not revolut_statement.detect(make_doc([["Something else"]]))


def test_statement_parses_events_snapshots_and_reconciles(make_doc):
    (res,) = revolut_statement.parse(make_doc(statement_pages()), {})  # the empty USD block is skipped
    assert res["account"] == {
        "id": "revolut-5731-eur",
        "institution": "revolut",
        "currency": "EUR",
        "mode": "transactions",
    }
    assert [e["type"] for e in res["events"]] == ["DEPOSIT", "BUY", "DIVIDEND", "FEE"]
    buy = res["events"][1]
    assert (buy["isin"], buy["quantity"], buy["cash"], buy["price"]) == (ISIN_A, "2", "-100", "50")
    assert res["events"][3]["cash"] == "-0.5"
    start, end = res["snapshots"]
    assert (start["date"], end["date"]) == ("2024-12-31", "2025-01-31")
    assert end["positions"][0]["isin"] == ISIN_A and end["total"] == "210.5"
    assert all(c["level"] == "ok" for c in res["checks"])
    assert res["unresolved"] == []


def test_statement_unknown_transaction_becomes_unresolved(make_doc):
    extra = ["25 Jan 2025 10:00:00 GMT", "Mystery event", "€1.00"]
    (res,) = revolut_statement.parse(make_doc(statement_pages(extra_tx=extra)), {})
    assert [u["kind"] for u in res["unresolved"]] == ["unknown-transaction"]
    assert len(res["events"]) == 4


def test_statement_cash_residual_is_a_warning_not_a_failure(make_doc):
    (res,) = revolut_statement.parse(make_doc(statement_pages(cash_end="€101.50")), {})
    assert [c["level"] for c in res["checks"] if "ending cash" in c["name"]] == ["warn"]


def test_statement_cash_mismatch_fails(make_doc):
    (res,) = revolut_statement.parse(make_doc(statement_pages(cash_end="€300.00")), {})
    assert "fail" in [c["level"] for c in res["checks"]]


def test_statement_without_any_block_is_a_layout_error(make_doc):
    with pytest.raises(PmError):
        revolut_statement.parse(
            make_doc([["Revolut Securities", "Account number", "A1", "Period", "01 Jan 2025 - 31 Jan 2025"]]), {}
        )


def test_pnl_parses_sales_and_reconciles_with_summary(make_doc):
    assert revolut_pnl.detect(make_doc(pnl_pages()))
    (res,) = revolut_pnl.parse(make_doc(pnl_pages()), {})
    sales = [r for r in res["references"] if r["kind"] == "pnl-sale"]
    assert len(sales) == 1
    assert (sales[0]["isin"], sales[0]["cost"], sales[0]["proceeds"], sales[0]["pnl"]) == (ISIN_A, "100", "150", "50")
    assert sales[0]["acquired"] == "2024-12-01" and sales[0]["sold"] == "2025-01-10"
    summary = next(r for r in res["references"] if r["kind"] == "pnl-summary")
    assert Decimal(summary["gross_pnl"]) == 50
    assert all(c["level"] == "ok" for c in res["checks"])


def test_pnl_paired_column_order_is_also_understood(make_doc):
    pages = pnl_pages()
    page = pages[0]
    start = page.index("€100.00", page.index("Other income & fees") - 12)
    page[start : start + 8] = ["€100.00", "€100.00", "€150.00", "€150.00", "€50.00", "€50.00", "€0.00", "€0.00"]
    (res,) = revolut_pnl.parse(make_doc(pages), {})
    assert [c["level"] for c in res["checks"]] == ["ok", "ok", "ok"]


def test_pnl_inconsistent_row_is_unresolved(make_doc):
    pages = pnl_pages()
    index = pages[0].index("€150.00", 20)
    pages[0][index] = "€999.00"
    (res,) = revolut_pnl.parse(make_doc(pages), {})
    assert [u["kind"] for u in res["unresolved"]] == ["unparsed-sale"]


def test_pnl_missing_summary_is_a_layout_error(make_doc):
    with pytest.raises(PmError):
        revolut_pnl.parse(make_doc([["EUR Profit and Loss Statement", "Sells Summary"]]), {})
