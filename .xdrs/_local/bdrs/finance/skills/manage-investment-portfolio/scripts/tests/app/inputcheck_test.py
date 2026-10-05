# Runtime: pytest; coverage, gap and advisory-report rules on plain in-memory data (no mocks).

from portfolio_manager.app import inputcheck


def cover(account, start, end, kind="ledger", file="f.pdf"):
    return {"file": file, "account": account, "kind": kind, "adapter": "x", "start": start, "end": end}


TX = {"id": "tx", "mode": "transactions"}
SNAP = {"id": "snap", "mode": "snapshot"}


def test_transaction_accounts_flag_any_uncovered_day_and_ignore_adjacent_or_overlapping_spans():
    coverage = [
        cover("tx", "2025-01-01", "2025-01-31"),
        cover("tx", "2025-02-01", "2025-02-28"),
        cover("tx", "2025-02-15", "2025-03-31"),
        cover("tx", "2025-04-02", "2025-04-30"),
    ]
    found = inputcheck.gaps({"coverage": coverage}, [TX], [])
    assert [(g["account"], g["start"], g["end"], g["days"]) for g in found] == [("tx", "2025-04-01", "2025-04-01", 1)]


def test_reference_statements_do_not_hide_a_transaction_gap():
    coverage = [
        cover("tx", "2025-01-01", "2025-01-31"),
        cover("tx", "2025-03-01", "2025-03-31"),
        cover("tx", "2025-01-01", "2025-12-31", kind="reference"),
    ]
    assert len(inputcheck.gaps({"coverage": coverage}, [TX], [])) == 1


def test_snapshot_accounts_flag_more_than_35_days_between_values():
    snaps = [{"account": "snap", "date": d} for d in ("2025-01-31", "2025-03-07", "2025-04-30")]
    found = inputcheck.gaps({}, [SNAP], snaps)
    assert [(g["start"], g["end"]) for g in found] == [("2025-03-08", "2025-04-29")]


def test_quarterly_statement_periods_close_the_gap_between_snapshot_dates():
    coverage = [
        cover("snap", "2025-07-01", "2025-09-30", kind="snapshot"),
        cover("snap", "2025-10-01", "2025-12-31", kind="snapshot"),
    ]
    snaps = [{"account": "snap", "date": d} for d in ("2025-09-30", "2025-12-31")]
    assert inputcheck.gaps({"coverage": coverage}, [SNAP], snaps) == []


def test_check_reports_notes_duplicates_skipped_files_and_recorded_gap_notes():
    ingest = {
        "coverage": [cover("tx", "2025-01-01", "2025-01-31"), cover("tx", "2025-03-01", "2025-03-31")],
        "files": [
            {"file": "copy.pdf", "status": "duplicate", "duplicate_of": "f.pdf"},
            {"file": "scan.pdf", "status": "unsupported"},
        ],
        "notes": [
            {"level": "warn", "kind": "overlap-mismatch", "message": "tx: a and b differ"},
            {"level": "info", "kind": "merged-timestamp", "message": "tx: merged"},
        ],
        "checks": [{"level": "fail", "file": "f.pdf", "name": "cash", "expected": "1", "actual": "2"}],
    }
    gap_id = inputcheck.gaps(ingest, [TX], [])[0]["id"]
    result = inputcheck.check(
        ingest, [TX], [], [{"id": "u1", "kind": "k", "where": "w"}], {"answers": {gap_id: "no trades"}}
    )
    text = "\n".join(inputcheck.render(result))
    assert result["gaps"][0]["note"] == "no trades"
    for expected in (
        "noted: no trades",
        "OVERLAP",
        "MERGED",
        "DUPLICATE copy.pdf",
        "NOT LOADED scan.pdf",
        "FAILED CHECK",
        "UNRESOLVED",
    ):
        assert expected in text
    assert "Gaps without a note: 0" in text


def test_clean_input_reports_nothing_to_flag():
    ingest = {"coverage": [cover("tx", "2025-01-01", "2025-12-31")]}
    text = "\n".join(inputcheck.render(inputcheck.check(ingest, [TX], [], [], {})))
    assert "No gaps, overlaps, merges or skipped files." in text and "2025-01-01 to 2025-12-31" in text
