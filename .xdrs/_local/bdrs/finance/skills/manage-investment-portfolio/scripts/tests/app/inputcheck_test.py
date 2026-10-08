# Runtime: pytest; coverage findings, acceptances and the advisory text on plain in-memory data (no mocks).

from portfolio_manager.app import acceptance, inputcheck


def cover(account, start, end, kind="ledger", file="f.pdf"):
    return {"file": file, "account": account, "kind": kind, "adapter": "x", "start": start, "end": end}


TX = {"id": "tx", "mode": "transactions"}
SNAP = {"id": "snap", "mode": "snapshot"}
FULL_YEAR = {"coverage": [cover("tx", "2025-01-01", "2025-12-31")]}


def found(ingest, accounts=(TX,), snapshots=(), openings=None, start="2025-01-01"):
    return inputcheck.findings(ingest, list(accounts), list(snapshots), openings or {}, start)


def kinds(findings):
    return [f["kind"] for f in findings]


def test_transaction_accounts_flag_any_uncovered_day_and_ignore_adjacent_or_overlapping_spans():
    coverage = [
        cover("tx", "2025-01-01", "2025-01-31"),
        cover("tx", "2025-02-01", "2025-02-28"),
        cover("tx", "2025-02-15", "2025-03-31"),
        cover("tx", "2025-04-02", "2025-04-30"),
    ]
    gaps = inputcheck.gaps({"coverage": coverage}, [TX], [])
    assert [(g["account"], g["start"], g["end"], g["days"]) for g in gaps] == [("tx", "2025-04-01", "2025-04-01", 1)]


def test_reference_statements_do_not_hide_a_transaction_gap():
    coverage = [
        cover("tx", "2025-01-01", "2025-01-31"),
        cover("tx", "2025-03-01", "2025-03-31"),
        cover("tx", "2025-01-01", "2025-12-31", kind="reference"),
    ]
    assert len(inputcheck.gaps({"coverage": coverage}, [TX], [])) == 1


def test_snapshot_accounts_flag_more_than_35_days_between_values():
    snaps = [{"account": "snap", "date": d} for d in ("2025-01-31", "2025-03-07", "2025-04-30")]
    gaps = inputcheck.gaps({}, [SNAP], snaps)
    assert [(g["start"], g["end"]) for g in gaps] == [("2025-03-08", "2025-04-29")]


def test_quarterly_statement_periods_close_the_gap_between_snapshot_dates():
    coverage = [
        cover("snap", "2025-07-01", "2025-09-30", kind="snapshot"),
        cover("snap", "2025-10-01", "2025-12-31", kind="snapshot"),
    ]
    snaps = [{"account": "snap", "date": d} for d in ("2025-09-30", "2025-12-31")]
    assert inputcheck.gaps({"coverage": coverage}, [SNAP], snaps) == []


def test_a_gap_is_a_finding_with_its_range_as_label():  # unit
    coverage = [cover("tx", "2025-01-01", "2025-01-31"), cover("tx", "2025-03-01", "2025-12-31")]
    gap = next(f for f in found({"coverage": coverage}) if f["kind"] == "gap")
    assert (gap["account"], gap["label"]) == ("tx", "2025-02-01..2025-02-28")


def test_late_start_is_flagged_beyond_35_days_after_the_expected_start():  # boundary
    on_time = {"coverage": [cover("tx", "2025-02-05", "2025-12-31")]}
    late = {"coverage": [cover("tx", "2025-02-06", "2025-12-31")]}
    assert "late-start" not in kinds(found(on_time))
    flagged = next(f for f in found(late) if f["kind"] == "late-start")
    assert flagged["message"] == "first statement 2025-02-06, expected 2025-01-01"


def test_late_start_is_not_judged_without_an_expected_start():
    late = {"coverage": [cover("tx", "2025-06-01", "2025-12-31")]}
    assert kinds(found(late, start="")) == ["scope", "expected-start"]


def test_reference_only_account_raises_late_start():  # unit
    ingest = {
        "coverage": [cover("tx", "2025-01-01", "2025-12-31"), cover("ref", "2025-01-01", "2025-12-31", "reference")]
    }
    accounts = [TX, {"id": "ref", "mode": "snapshot"}]
    flagged = [f for f in found(ingest, accounts) if f["kind"] == "late-start"]
    assert [(f["account"], f["message"]) for f in flagged] == [
        ("ref", "no ledger or snapshot statement (reference statements only)")
    ]


def test_stale_end_is_flagged_beyond_35_days_before_the_latest_data():  # boundary
    ingest = {
        "coverage": [cover("tx", "2025-01-01", "2025-03-31"), cover("snap", "2025-01-01", "2025-02-24", "snapshot")]
    }
    assert "stale-end" not in kinds(found(ingest, [TX, SNAP]))
    ingest["coverage"][1] = cover("snap", "2025-01-01", "2025-02-23", "snapshot")
    flagged = [f for f in found(ingest, [TX, SNAP]) if f["kind"] == "stale-end"]
    assert [(f["account"], f["message"]) for f in flagged] == [
        ("snap", "last value 2025-02-23, latest data 2025-03-31")
    ]


def test_derived_opening_is_flagged_for_cash_or_positions_but_not_for_an_empty_opening():  # unit
    cash = {"tx": {"date": "2025-01-01", "cash": "10.5", "positions": []}}
    held = {
        "tx": {
            "date": "2025-01-01",
            "cash": "0",
            "positions": [{"isin": "IE00B4L5Y983", "symbol": "", "quantity": "2"}],
        }
    }
    empty = {"tx": {"date": "2025-01-01", "cash": "0", "positions": []}}
    assert kinds(found(FULL_YEAR, openings=cash)).count("derived-opening") == 1
    assert kinds(found(FULL_YEAR, openings=held)).count("derived-opening") == 1
    assert "derived-opening" not in kinds(found(FULL_YEAR, openings=empty))


def test_warn_level_reconciliation_is_a_finding_but_ok_and_fail_levels_are_not():  # unit
    checks = [
        {"level": "warn", "file": "a.pdf", "name": "cash", "expected": "1", "actual": "2", "account": "tx"},
        {"level": "ok", "file": "a.pdf", "name": "total", "expected": "1", "actual": "1", "account": "tx"},
        {"level": "fail", "file": "b.pdf", "name": "cash", "expected": "1", "actual": "9", "account": "tx"},
    ]
    warns = [f for f in found({**FULL_YEAR, "checks": checks}) if f["kind"] == "check-warn"]
    assert [f["message"] for f in warns] == ["a.pdf: cash expected 1 got 2"]


def test_overlap_notes_are_findings_but_merged_timestamps_are_not():  # unit
    notes = [
        {"level": "warn", "kind": "overlap-mismatch", "message": "tx: a and b differ"},
        {"level": "info", "kind": "period-flows-overlap", "message": "tx: periods overlap"},
        {"level": "info", "kind": "merged-timestamp", "message": "tx: merged"},
    ]
    overlaps = [f for f in found({**FULL_YEAR, "notes": notes}) if f["kind"] == "overlap"]
    assert sorted(f["message"] for f in overlaps) == ["tx: a and b differ", "tx: periods overlap"]


def test_expected_start_finding_exists_only_until_the_user_gives_a_start():  # unit
    assert "expected-start" in kinds(found(FULL_YEAR, start=""))
    assert "expected-start" not in kinds(found(FULL_YEAR, start="2025-01-01"))


def test_finding_ids_are_stable_and_the_scope_id_follows_the_account_list():  # determinism
    first = found(FULL_YEAR)
    assert [f["id"] for f in first] == [f["id"] for f in found(FULL_YEAR)]
    more = found(
        {"coverage": [*FULL_YEAR["coverage"], cover("snap", "2025-01-01", "2025-12-31", "snapshot")]}, [TX, SNAP]
    )
    scope = lambda fs: next(f["id"] for f in fs if f["kind"] == "scope")  # noqa: E731
    assert scope(first) != scope(more)
    assert len({f["id"] for f in more}) == len(more)


def test_every_finding_kind_has_a_valid_reason_list():  # unit
    assert set(inputcheck.KIND_ORDER) == set(acceptance.KIND_REASONS)
    assert all(set(r) <= set(acceptance.EVERY_REASON) and r for r in acceptance.KIND_REASONS.values())


def test_check_marks_accepted_findings_and_lists_notes_duplicates_and_skipped_files():
    ingest = {
        "coverage": [cover("tx", "2025-01-01", "2025-01-31"), cover("tx", "2025-03-01", "2025-03-31")],
        "files": [
            {"file": "copy.pdf", "status": "duplicate", "duplicate_of": "f.pdf"},
            {"file": "scan.pdf", "status": "unsupported"},
        ],
        "notes": [{"level": "info", "kind": "merged-timestamp", "message": "tx: merged"}],
        "checks": [{"level": "fail", "file": "f.pdf", "name": "cash", "expected": "1", "actual": "2"}],
    }
    gap_id = next(f["id"] for f in found(ingest, start="2025-01-01") if f["kind"] == "gap")
    store = acceptance.add(
        acceptance.with_expected_start(acceptance.load(None), "2025-01-01"),
        found(ingest),
        [gap_id],
        "no-activity",
        "no trades in Feb",
    )
    result = inputcheck.check(ingest, [TX], [], [{"id": "u1", "kind": "k", "where": "w"}], {}, store)
    text = "\n".join(inputcheck.render(result))
    for expected in (
        f'- ACCEPTED gap tx: no-activity - "no trades in Feb" id {gap_id}',
        "- SCOPE accounts in scope: tx",
        "MERGED",
        "DUPLICATE copy.pdf",
        "NOT LOADED scan.pdf",
        "FAILED CHECK",
        "UNRESOLVED",
        "Ask the user per finding. Never accept for them.",
    ):
        assert expected in text
    assert [f["kind"] for f in inputcheck.open_findings(result)] == ["scope"]


def test_acceptance_of_a_vanished_finding_is_ignored():  # unit
    store = {
        "settings": {"expected_start": "2025-01-01"},
        "accepted": [{"id": "gone", "kind": "gap", "reason": "accept-as-is", "note": "x"}],
    }
    result = inputcheck.check(FULL_YEAR, [TX], [], [], {}, store)
    assert [f["kind"] for f in result["findings"]] == ["scope"] and not result["findings"][0]["accepted"]


def test_clean_input_with_everything_accepted_reports_nothing_open():
    store = acceptance.with_expected_start(acceptance.load(None), "2025-01-01")
    scope = found(FULL_YEAR)[0]
    store = acceptance.add(store, [scope], [scope["id"]], "accept-as-is", "single account")
    text = "\n".join(inputcheck.render(inputcheck.check(FULL_YEAR, [TX], [], [], {}, store)))
    assert "Input check: 0 open, 1 accepted." in text and "Nothing open; reports can be written." in text
    assert "2025-01-01 to 2025-12-31" in text
