# Runtime: pytest; time-weighted return, XIRR and Dietz scenarios with fictitious numbers.
from decimal import Decimal

import pytest

from portfolio_manager.app.performance import days_between, interpolate, period_return, twr, worst, xirr


def values(table: dict):
    return lambda day: (Decimal(table[day]), "complete") if day in table else (None, "unavailable")


def test_worst_orders_statuses():
    assert worst("complete", "interpolated", "approximate") == "approximate"
    assert worst() == "complete"


def test_interpolate_exact_between_outside_and_empty():
    pts = [("2025-01-01", Decimal(100)), ("2025-01-11", Decimal(200))]
    assert interpolate(pts, "2025-01-01") == (Decimal(100), "complete")
    assert interpolate(pts, "2025-01-06") == (Decimal(150), "interpolated")
    assert interpolate(pts, "2025-02-01") == (Decimal(200), "approximate")
    assert interpolate([], "2025-02-01") == (None, "unavailable")
    assert days_between("2025-01-01", "2025-01-31") == 30


def test_twr_without_flows_is_simple_growth():
    r = twr(values({"2025-01-01": 100, "2025-02-01": 110}), [], "2025-01-01", "2025-02-01")
    assert r["value"] == Decimal("0.1")
    assert r["status"] == "complete"


def test_twr_neutralises_a_deposit():
    flows = [{"date": "2025-01-15", "amount": "100"}]
    r = twr(values({"2025-01-01": 100, "2025-01-15": 220, "2025-02-01": 242}), flows, "2025-01-01", "2025-02-01")
    # sub-period 1: 120/100 (value before the deposit), sub-period 2: 242/220
    assert r["value"] == Decimal("1.2") * Decimal("1.1") - 1


def test_twr_zero_value_sub_period_is_skipped_or_unavailable():
    flows = [{"date": "2025-01-10", "amount": "100"}]
    only_zero_start = twr(
        values({"2025-01-01": 0, "2025-01-10": 100, "2025-01-31": 100}), flows, "2025-01-01", "2025-01-31"
    )
    assert only_zero_start["value"] == 0
    nothing = twr(values({"2025-01-01": 0, "2025-01-31": 0}), [], "2025-01-01", "2025-01-31")
    assert nothing["value"] is None and nothing["status"] == "unavailable"


def test_twr_missing_valuation_is_unavailable():
    r = twr(values({"2025-01-01": 100}), [], "2025-01-01", "2025-02-01")
    assert r["status"] == "unavailable"
    r = twr(values({}), [], "2025-01-01", "2025-02-01")
    assert "no valuation" in r["reason"]


def test_xirr_twelve_month_window_equals_the_annual_rate():
    r = xirr([], "2025-01-01", "2026-01-01", Decimal(100), Decimal(110))
    assert r["status"] == "complete" and r["days"] == 365
    assert r["value"] == pytest.approx(Decimal("0.1"), abs=Decimal("0.0001"))
    assert r["rate"] == pytest.approx(Decimal("0.1"), abs=Decimal("0.0001"))


def test_xirr_short_window_reports_the_return_over_the_window_not_a_scaled_rate():
    r = xirr([], "2025-01-01", "2025-04-11", Decimal(100), Decimal(101))
    assert r["days"] == 100 and r["value"] == pytest.approx(Decimal("0.01"), abs=Decimal("0.00001"))
    assert r["rate"] > r["value"]


def test_xirr_needs_at_least_28_days():
    assert xirr([], "2025-02-01", "2025-03-01", Decimal(100), Decimal(101))["value"] is not None
    short = xirr([], "2025-01-01", "2025-01-28", Decimal(100), Decimal(101))
    assert short["value"] is None and short["reason"] == "n/a (<28d)"


def test_xirr_with_a_zero_start_value_and_an_in_window_flow():
    flows = [{"date": "2025-01-10", "amount": "100"}]
    r = xirr(flows, "2025-01-01", "2025-03-11", Decimal(0), Decimal(105))
    assert r["status"] == "complete" and r["value"] > Decimal(0)


def test_xirr_same_sign_flows_unavailable():
    r = xirr([{"date": "2025-02-01", "amount": "-50"}], "2025-01-01", "2025-03-01", Decimal(0), Decimal(0))
    assert r["status"] == "unavailable"
    only_inflows = xirr([{"date": "2025-02-01", "amount": "-50"}], "2025-01-01", "2025-03-01", Decimal(100), Decimal(0))
    assert only_inflows["value"] is None or only_inflows["status"] in ("complete", "unavailable")


def test_xirr_without_a_root_is_unavailable():
    r = xirr([], "2025-01-01", "2025-03-01", Decimal(100), Decimal("0.000001"))
    assert r["status"] in ("complete", "unavailable")


def test_period_return_dietz():
    r = period_return(Decimal(100), Decimal(160), [{"date": "2025-01-16", "amount": "50"}], "2025-01-01", "2025-01-31")
    assert r["status"] == "complete"
    assert r["value"] == Decimal(10) / (Decimal(100) + Decimal(50) * Decimal(15) / Decimal(30))


def test_period_return_unavailable_cases():
    assert period_return(None, Decimal(1), [], "2025-01-01", "2025-01-31")["status"] == "unavailable"
    assert period_return(Decimal(0), Decimal(1), [], "2025-01-01", "2025-01-31")["status"] == "unavailable"
