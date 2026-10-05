# Runtime: pytest; Trading 212 adapter on a fictitious activity statement.
import pytest

from portfolio_manager.adapters.connectors.institutions import trading212
from portfolio_manager.shared.errors import PmError
from samples_test import ISIN_A
from samples_test import trading212 as pages


def test_detect(make_doc):
    assert trading212.detect(make_doc(pages()))
    assert not trading212.detect(make_doc([["Other"]]))


def test_parse_events_snapshot_and_checks(make_doc):
    (res,) = trading212.parse(make_doc(pages()), {})
    assert res["account"]["id"] == "trading212-1234" and res["account"]["currency"] == "EUR"
    assert res["period"] == {"start": "2025-01-01", "end": "2025-01-31"}
    types = {e["type"]: e for e in res["events"]}
    assert set(types) == {"BUY", "DEPOSIT", "DIVIDEND"}
    assert types["BUY"]["cash"] == "-100" and types["BUY"]["isin"] == ISIN_A
    assert (
        types["DIVIDEND"]["cash"] == "0.85"
        and types["DIVIDEND"]["tax"] == "0.15"
        and types["DIVIDEND"]["date"] == "2025-01-15"
    )
    (snap,) = res["snapshots"]
    assert snap["cash"] == "900.85" and snap["positions"][0]["quantity"] == "2" and snap["total"] == "1010.85"
    assert res["opening"] == {"date": "2024-12-31", "cash": "0", "derived": True}
    assert all(c["level"] == "ok" for c in res["checks"])


def test_deposit_mismatch_with_overview_fails(make_doc):
    (res,) = trading212.parse(make_doc(pages(deposit="€5,000.00")), {})
    assert any(c["level"] == "fail" and "deposits" in c["name"] for c in res["checks"])


def test_unknown_transaction_is_unresolved(make_doc):
    doc_pages = pages()
    i = doc_pages[0].index("Dividends", doc_pages[0].index("Invest account - transactions and dividends"))
    doc_pages[0][i:i] = ["2025-01-05 09:00:00", "Mystery", "€1.00"]
    (res,) = trading212.parse(make_doc(doc_pages), {})
    assert [u["kind"] for u in res["unresolved"]] == ["unknown-transaction"]


def test_layout_drift_raises(make_doc):
    with pytest.raises(PmError):
        trading212.parse(make_doc([["Trading 212", "Activity statement", "no period here"]]), {})
    broken = pages()
    broken[0].remove("Invest account - cash breakdown")
    with pytest.raises(PmError):
        trading212.parse(make_doc(broken), {})
