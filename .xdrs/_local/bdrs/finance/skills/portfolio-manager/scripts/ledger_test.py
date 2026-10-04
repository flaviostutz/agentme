# Runtime: pytest; ledger merge rules and store safety on plain in-memory data (no mocks).
from pathlib import Path

import pytest

import ledger
import store
from sourcedoc import PmError


def event(**kw) -> dict:
    base = {"account": "a", "date": "2025-01-02", "time": "10:00:00", "type": "BUY", "symbol": "ABC", "isin": "IE00B4L5Y983",
            "quantity": "1", "cash": "-10", "ref": "r"}
    return {**base, **kw}


def snapshot(total: str, date: str = "2025-01-31", positions: list | None = None) -> dict:
    return {"account": "a", "date": date, "total": total, "positions": positions or []}


def test_overlapping_statements_dedupe_but_identical_trades_stay_separate():
    one = [event(), event()]
    two = [event(), event(), event(date="2025-01-05", quantity="2")]
    merged = ledger.merge_events([one, two])
    assert [(e["date"], e["quantity"]) for e in merged] == [("2025-01-02", "1"), ("2025-01-02", "1"), ("2025-01-05", "2")]


def test_restated_snapshot_total_is_an_error_and_richer_snapshot_wins():
    _, errors = ledger._merge_snapshots([snapshot("100"), snapshot("101")])
    assert errors and "restated" in errors[0]
    pos = [{"isin": "X", "symbol": "", "quantity": "1", "price": "1"}]
    kept, errors = ledger._merge_snapshots([snapshot("100"), snapshot("100", positions=pos)])
    assert errors == [] and kept[0]["positions"] == pos


def test_opening_quantity_is_derived_and_negative_opening_is_an_error():
    accounts = {"a": {"mode": "transactions"}}
    held = [{"isin": "IE00B4L5Y983", "symbol": "ABC", "name": "", "quantity": "3", "price": "1"}]
    result, errors = ledger._openings(accounts, [event(quantity="1")], [snapshot("3", positions=held)], {})
    assert errors == [] and result["a"]["positions"][0]["quantity"] == "2"
    _, errors = ledger._openings(accounts, [event(quantity="5")], [snapshot("3", positions=held)], {})
    assert len(errors) == 1 and "sold more than held" in errors[0]


def test_symbol_only_events_get_the_isin_from_snapshots():
    events = [event(isin="")]
    held = [{"isin": "IE00B4L5Y983", "symbol": "ABC", "quantity": "1", "price": "1"}]
    ledger._unify_isin(events, [snapshot("1", positions=held)], [])
    assert events[0]["isin"] == "IE00B4L5Y983"


def test_resolve_tmp_only_allows_paths_inside_tmp(tmp_path):
    (tmp_path / ".tmp").mkdir()
    assert store.resolve_tmp(".tmp/x", tmp_path) == (tmp_path / ".tmp" / "x").resolve()
    for bad in ("x", "../.tmp/x", "/etc", ".tmp/../x"):
        with pytest.raises(PmError):
            store.resolve_tmp(bad, tmp_path)


def test_work_dir_name_validation(tmp_path):
    (tmp_path / ".tmp").mkdir()
    assert store.work_dir("my-run_1", tmp_path).name == "portfolio-manager-my-run_1"
    for bad in ("", "a/b", "a b"):
        with pytest.raises(PmError):
            store.work_dir(bad, tmp_path)


def test_dumps_is_deterministic_and_workspace_roundtrips(tmp_path):
    assert store.dumps({"b": 1, "a": [2]}) == store.dumps({"a": [2], "b": 1})
    ws = store.Workspace(tmp_path / "ws")
    assert ws.init() is True and ws.init() is False
    ws.write("data/x.json", {"k": 1})
    assert ws.read("data/x.json") == {"k": 1} and ws.read("data/none.json", "dflt") == "dflt"
    ws.write_text("reports/a.md", "hi\n")
    assert ws.path("reports/a.md").read_text(encoding="utf-8") == "hi\n"
    assert isinstance(ws.root, Path)


def test_lock_excludes_a_second_holder(tmp_path):
    ws = store.Workspace(tmp_path / "ws")
    ws.init()
    with ws.lock(), pytest.raises(PmError), ws.lock():
        pass
    with ws.lock():
        pass
