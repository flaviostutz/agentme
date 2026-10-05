# Runtime: pytest; canonical record builders and checks.
from decimal import Decimal

from portfolio_manager.app import records as common


def test_account_id_uses_last_four_alphanumerics():
    assert common.account_id("bank", "AB-12.34 5") == "bank-2345"
    assert common.account_id("bank", "ACC0005731") == "bank-5731"
    assert common.account_id("up", "ACC0007311-1", drop_suffix=True) == "up-7311"


def test_account_id_suffix_difference():
    assert common.account_id("up", "X7311-1") == "up-3111"
    assert common.account_id("up", "X7311-1", drop_suffix=True) == "up-7311"


def test_event_cash_is_signed_and_optional_fields_only_when_given():
    e = common.event("a", "BUY", "2025-01-01", "r", cash=Decimal("-10.50"), quantity=Decimal(2), price=Decimal(5))
    assert e["cash"] == "-10.5" and e["quantity"] == "2" and e["price"] == "5" and "gross" not in e
    full = common.event("a", "SELL", "2025-01-01", "r", gross=Decimal(1), fx_rate=Decimal(2), raw_type="x")
    assert full["gross"] == "1" and full["fx_rate"] == "2" and full["raw_type"] == "x"


def test_check_levels():
    assert common.check("n", Decimal(10), Decimal("10.01"), Decimal("0.01"))["level"] == "ok"
    assert common.check("n", Decimal(10), Decimal("10.5"), Decimal("0.01"), Decimal(1))["level"] == "warn"
    assert common.check("n", Decimal(10), Decimal(20), Decimal("0.01"))["level"] == "fail"


def test_tolerance_grows_with_rows():
    assert common.rounding_tolerance(4) == Decimal("0.03")


def test_unresolved_id_is_stable_and_text_is_capped():
    a = common.unresolved("sha", "kind", "x" * 500, "q?")
    b = common.unresolved("sha", "kind", "x" * 500, "q?")
    assert a == b and len(a["text"]) == 400 and len(a["id"]) == 12


def test_position_snapshot_and_result_shapes():
    p = common.position("IE00B4L5Y983", "A", "Alpha", None, "1.50", "3", "EUR")
    assert p["quantity"] is None and p["price"] == "1.5"
    s = common.snapshot("a", "2025-01-01", [p], currency="EUR", ref="r", total=Decimal(3))
    assert s["total"] == "3" and s["cash"] is None
    r = common.result("x", "ledger", {"id": "a"}, {"start": "s", "end": "e"})
    assert r["events"] == [] and r["opening"] == {}
