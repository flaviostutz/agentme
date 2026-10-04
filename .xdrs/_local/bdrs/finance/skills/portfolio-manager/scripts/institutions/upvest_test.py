# Runtime: pytest; Upvest snapshot, tax and ex-post cost adapters on fictitious layouts.
import pytest

from institutions import upvest_expost, upvest_snapshot, upvest_tax
from samples_test import ISIN_A
from samples_test import upvest_expost as expost_pages
from samples_test import upvest_snapshot as snapshot_pages
from samples_test import upvest_tax as tax_pages
from sourcedoc import PmError


def test_snapshot_parses_positions_and_ignores_german_copy(make_doc):
    assert upvest_snapshot.detect(make_doc(snapshot_pages()))
    (res,) = upvest_snapshot.parse(make_doc(snapshot_pages()), {})
    assert res["account"]["id"] == "upvest-5731"
    (snap,) = res["snapshots"]
    assert snap["date"] == "2025-06-30" and snap["total"] == "525"
    assert snap["positions"][0]["isin"] == ISIN_A and snap["positions"][0]["quantity"] == "10.5"
    assert snap["positions"][0]["price"] == "50" and snap["positions"][0]["value"] == "525"
    assert all(c["level"] == "ok" for c in res["checks"])


def test_snapshot_total_and_count_mismatch_fail(make_doc):
    (res,) = upvest_snapshot.parse(make_doc(snapshot_pages(total="600.00 EUR", count="2")), {})
    assert [c["level"] for c in res["checks"]] == ["fail", "fail"]


def test_snapshot_without_totals_is_a_layout_error(make_doc):
    page = snapshot_pages(german_tail=False)[0]
    page.remove("Total value")
    with pytest.raises(PmError):
        upvest_snapshot.parse(make_doc([page]), {})


def test_snapshot_unparsable_block_is_unresolved(make_doc):
    page = snapshot_pages()[0]
    page.insert(page.index("Number of positions"), "3 / unit(s)")
    (res,) = upvest_snapshot.parse(make_doc([page]), {})
    assert [u["kind"] for u in res["unresolved"]] == ["unparsed-position"]


def test_tax_statement_extracts_transactions_and_dividends(make_doc):
    assert upvest_tax.detect(make_doc(tax_pages()))
    (res,) = upvest_tax.parse(make_doc(tax_pages()), {})
    kinds = [r["kind"] for r in res["references"]]
    assert kinds == ["tax-transaction", "tax-dividend"]
    tx, div = res["references"]
    assert (tx["date"], tx["side"], tx["units"], tx["value"]) == ("2025-03-15", "BUY", "2", "100")
    assert (div["date"], div["income"], div["tax"], div["units"]) == ("2025-06-20", "1", "0.1", "2")
    assert res["period"] == {"start": "2025-01-01", "end": "2025-12-31"}
    assert all(c["level"] == "ok" for c in res["checks"])


def test_tax_statement_without_year_is_a_layout_error(make_doc):
    with pytest.raises(PmError):
        upvest_tax.parse(make_doc([["Upvest Securities", "Annual tax statement"]]), {})


def test_expost_extracts_costs_and_reconciles(make_doc):
    assert upvest_expost.detect(make_doc(expost_pages()))
    (res,) = upvest_expost.parse(make_doc(expost_pages()), {})
    (ref,) = res["references"]
    assert ref["kind"] == "cost-report" and ref["total_cost"] == "5" and ref["avg_valuation"] == "1000"
    assert ref["per_instrument"] == [{"isin": ISIN_A, "service_costs": "1", "product_costs": "3", "inducements": "1"}]
    assert res["checks"][0]["level"] == "ok"


def test_expost_total_mismatch_fails_and_bad_layout_raises(make_doc):
    (res,) = upvest_expost.parse(make_doc(expost_pages(total_cost="50.00")), {})
    assert res["checks"][0]["level"] == "fail"
    with pytest.raises(PmError):
        upvest_expost.parse(make_doc([["Upvest Securities", "Ex-post cost report"]]), {})
