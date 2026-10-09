# Runtime: pytest; ledger merge rules and store safety on plain in-memory data (no mocks).


from portfolio_manager.app import ledger


def event(**kw) -> dict:
    base = {
        "account": "a",
        "date": "2025-01-02",
        "time": "10:00:00",
        "type": "BUY",
        "symbol": "ABC",
        "isin": "IE00B4L5Y983",
        "quantity": "1",
        "cash": "-10",
        "ref": "r",
    }
    return {**base, **kw}


def snapshot(total: str, date: str = "2025-01-31", positions: list | None = None) -> dict:
    return {"account": "a", "date": date, "total": total, "positions": positions or []}


def test_overlapping_statements_dedupe_but_identical_trades_stay_separate():
    one = [event(), event()]
    two = [event(), event(), event(date="2025-01-05", quantity="2")]
    merged, notes = ledger.merge_events([one, two])
    assert notes == []
    assert [(e["date"], e["quantity"]) for e in merged] == [
        ("2025-01-02", "1"),
        ("2025-01-02", "1"),
        ("2025-01-05", "2"),
    ]


def test_copies_with_different_times_merge_keeping_the_richest_timestamp_and_smallest_ref():
    merged, notes = ledger.merge_events([[event(time="", ref="b")], [event(time="10:00:05", ref="a")]])
    assert [(e["time"], e["ref"]) for e in merged] == [("10:00:05", "a")]
    assert [n["kind"] for n in notes] == ["merged-timestamp"]


def test_overlapping_statements_that_disagree_are_flagged_and_agreeing_ones_are_not():
    def stmt(name, start, end, events):
        return {"file": name, "account": "a", "start": start, "end": end, "events": events}

    same = [stmt("x", "2025-01-01", "2025-01-31", [event()]), stmt("y", "2025-01-02", "2025-02-28", [event()])]
    assert ledger._overlap_notes(same) == []
    differ = [stmt("x", "2025-01-01", "2025-01-31", [event()]), stmt("y", "2025-01-02", "2025-02-28", [])]
    notes = ledger._overlap_notes(differ)
    assert len(notes) == 1 and notes[0]["kind"] == "overlap-mismatch" and "x and y" in notes[0]["message"]
    outside = [stmt("x", "2025-01-01", "2025-01-31", [event()]), stmt("y", "2025-02-01", "2025-02-28", [])]
    assert ledger._overlap_notes(outside) == []


def test_overlapping_period_flow_windows_keep_the_earlier_one():
    def flows(start, end, entries):
        return {
            "kind": "period-flows",
            "account": "bb",
            "security": "FUND",
            "from": start,
            "to": end,
            "entries": entries,
        }

    kept, notes = ledger._period_flow_notes(
        [flows("2025-07-01", "2026-03-31", "5"), flows("2025-01-01", "2025-12-31", "9"), {"kind": "other"}]
    )
    assert [r.get("entries") for r in kept if r["kind"] == "period-flows"] == ["9"]
    assert [n["kind"] for n in notes] == ["period-flows-overlap"]


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
