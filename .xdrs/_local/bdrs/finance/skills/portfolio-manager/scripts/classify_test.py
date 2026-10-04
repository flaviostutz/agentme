# Runtime: pytest; classification queue, validation (sources required, no amounts) and allocation.
from decimal import Decimal

import classify

GOOD = {"isin": "IE00B4L5Y983", "asset_class": "etf", "region": "World", "source_url": "https://example.org/fund", "as_of": "2025-06-30"}


def test_validate_accepts_complete_entries():
    valid, errors = classify.validate([GOOD])
    assert errors == [] and valid == [GOOD]


def test_validate_rejects_amounts_and_unknown_fields():
    _, errors = classify.validate([{**GOOD, "quantity": "5", "account": "x"}])
    assert "unknown field(s) account, quantity" in errors[0]


def test_validate_rejects_bad_values():
    bad = [{"isin": "nope", "asset_class": "magic", "source_url": "http://x", "as_of": "yesterday"}, {"isin": "IE00B4L5Y983"}, "text"]
    _, errors = classify.validate(bad)
    assert len(errors) == 3
    assert "not a valid ISIN" in errors[0] and "https" in errors[0] and "YYYY-MM-DD" in errors[0] and "asset_class" in errors[0]
    assert "missing source_url" in errors[1]
    assert "must be an object" in errors[2]


def test_validate_rejects_non_list():
    assert classify.validate({"a": 1})[1] == ["classifications must be a JSON list of objects"]


def test_merge_replaces_by_isin():
    new = {**GOOD, "region": "Europe"}
    assert classify.merge([GOOD], [new]) == [new]


def test_queue_lists_identifiers_only_and_skips_known_and_unsupported():
    assets = [{"isin": "IE00B4L5Y983", "symbol": "A", "name": "Alpha", "value": "10"},
              {"isin": "US0378331005", "symbol": "B", "name": "Beta", "value": "20"},
              {"isin": "US0378331005", "symbol": "B", "name": "Beta", "value": "20"},
              {"isin": "", "symbol": "C", "name": "Gamma"},
              {"isin": "XS0000000009", "symbol": "D", "name": "D", "unsupported": True}]
    q = classify.queue(assets, [GOOD])
    assert q == [{"isin": "US0378331005", "ticker": "B", "name": "Beta"}]


def test_allocation_groups_with_unclassified_and_asset_class_fallback():
    assets = [{"isin": "IE00B4L5Y983", "value_eur": "60", "asset_class": None}, {"isin": "", "value_eur": "30", "asset_class": "bond"},
              {"isin": "X", "value_eur": "10", "asset_class": None}, {"isin": "U", "value_eur": "5", "unsupported": True},
              {"isin": "N", "value_eur": None}]
    by_region = classify.allocation(assets, [GOOD], "region")
    assert by_region == {"World": Decimal(60), "unclassified": Decimal(40)}
    by_class = classify.allocation(assets, [GOOD], "asset_class")
    assert by_class == {"etf": Decimal(60), "bond": Decimal(30), "unclassified": Decimal(10)}
