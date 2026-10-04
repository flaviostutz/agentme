# Runtime: pytest; FIFO lots, realized P&L, income, flows and transfers on fictitious events.
from decimal import Decimal

import accounting
from institutions.common import event

ACCT = {"id": "x-1", "currency": "EUR", "mode": "transactions", "institution": "x"}


def to_eur(amount, ccy, day):
    return amount, "exact"


def ev(etype, day, qty=0, cash=0, isin="IE0000000001", **kw):
    return event("x-1", etype, day, f"{etype}{day}", isin=isin, symbol="ABC", quantity=Decimal(str(qty)), cash=Decimal(str(cash)), **kw)


def run(events, opening=None):
    return accounting.run([ACCT], {"x-1": opening or {}}, events, to_eur)["x-1"]


def test_fifo_example_realized_and_remaining_basis():
    res = run([ev("DEPOSIT", "2025-01-01", cash=3000, isin=""), ev("BUY", "2025-01-02", 10, -1000), ev("BUY", "2025-01-03", 10, -1200),
               ev("SELL", "2025-02-01", 10, 1500)])
    assert [r["pnl"] for r in res["realized"]] == ["500"]
    assert res["realized"][0]["acquired"] == "2025-01-02"
    assert res["lots"][0]["quantity"] == "10" and res["lots"][0]["cost"] == "1200"
    assert res["realized_status"] == "complete"
    assert res["cash"] == "2300"


def test_sell_spanning_two_lots_and_partial_lot_cost_scaling():
    res = run([ev("BUY", "2025-01-02", 10, -1000), ev("BUY", "2025-01-03", 10, -2000), ev("SELL", "2025-02-01", 15, 3000)])
    assert [r["quantity"] for r in res["realized"]] == ["10", "5"]
    assert [r["pnl"] for r in res["realized"]] == ["1000", "0"]
    assert res["lots"][0]["cost"] == "1000"


def test_oversell_is_an_error_and_marks_position_unreliable():
    res = run([ev("BUY", "2025-01-02", 1, -10), ev("SELL", "2025-01-03", 2, 30)])
    assert any("only 1 was held" in e for e in res["errors"])
    assert res["unreliable"] == ["IE0000000001"]


def test_opening_lots_have_no_cost_so_realized_is_partial():
    opening = {"date": "2024-12-31", "cash": "0", "positions": [{"isin": "IE0000000001", "symbol": "ABC", "name": "", "quantity": "5"}]}
    res = run([ev("SELL", "2025-01-03", 5, 60)], opening)
    assert res["realized"][0]["pnl"] is None and res["realized"][0]["cost_status"] == "unavailable"
    assert res["realized_status"] == "partial"


def test_split_scales_lot_quantities_and_errors_without_position():
    res = run([ev("BUY", "2025-01-02", 10, -1000), ev("SPLIT", "2025-01-10", 10)])
    assert res["lots"][0]["quantity"] == "20"
    bad = run([ev("SPLIT", "2025-01-10", 10)])
    assert any("split" in e for e in bad["errors"])


def test_income_flows_and_negative_cash_days():
    res = run([ev("DIVIDEND", "2025-01-02", cash=9, tax=1), ev("INTEREST", "2025-01-03", cash=2), ev("FEE", "2025-01-04", cash=-3),
               ev("TAX", "2025-01-05", cash=-4), ev("DEPOSIT", "2025-01-06", cash=100), ev("WITHDRAWAL", "2025-01-07", cash=-200)])
    assert res["income"] == {"dividends": "9", "interest": "2", "fees": "3", "taxes": "4", "withholding": "1"}
    assert [f["type"] for f in res["flows"]] == ["DEPOSIT", "WITHDRAWAL"]
    assert "2025-01-07" in res["negative_cash_days"]


def test_states_are_recorded_per_event_date():
    res = run([ev("BUY", "2025-01-02", 1, -10), ev("BUY", "2025-01-03", 1, -10)])
    assert [s["date"] for s in res["states"]] == ["2025-01-02", "2025-01-03"]
    assert res["states"][1]["positions"] == {"IE0000000001": "2"}


def test_transfer_moves_lots_with_acquisition_date_and_cost():
    other = {"id": "y-1", "currency": "EUR", "mode": "transactions", "institution": "y"}
    out = event("x-1", "TRANSFER_OUT", "2025-03-01", "o", isin="IE0000000001", symbol="ABC", quantity=Decimal(4))
    back = event("y-1", "TRANSFER_IN", "2025-03-01", "i", isin="IE0000000001", symbol="ABC", quantity=Decimal(4))
    res = accounting.run([ACCT, other], {}, [ev("BUY", "2025-01-02", 10, -1000), out, back], to_eur)
    assert res["y-1"]["lots"][0]["acquired"] == "2025-01-02" and res["y-1"]["lots"][0]["cost"] == "400"
    assert res["x-1"]["lots"][0]["quantity"] == "6"


def test_unmatched_transfer_in_has_unknown_cost_and_excess_transfer_out_errors():
    res = run([event("x-1", "TRANSFER_IN", "2025-03-01", "i", isin="IE0000000001", symbol="ABC", quantity=Decimal(4)),
               event("x-1", "TRANSFER_OUT", "2025-03-02", "o", isin="IE0000000001", symbol="ABC", quantity=Decimal(9))])
    assert any("exceeds" in e for e in res["errors"])


def test_non_transaction_accounts_are_ignored():
    snap = {"id": "s-1", "currency": "EUR", "mode": "snapshot", "institution": "s"}
    assert accounting.run([snap], {}, [event("s-1", "BUY", "2025-01-01", "r")], to_eur) == {}
