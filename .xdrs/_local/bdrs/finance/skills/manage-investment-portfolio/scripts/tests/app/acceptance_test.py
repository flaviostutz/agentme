# Runtime: pytest; acceptance rules (reasons per kind, notes, store) on plain in-memory data (no mocks).

import pytest

from portfolio_manager.app import acceptance
from portfolio_manager.shared.errors import PmError

FINDINGS = [
    {"id": "g1", "kind": "gap"},
    {"id": "o1", "kind": "overlap"},
    {"id": "s1", "kind": "scope"},
]


def test_invalid_reason_for_the_kind_is_rejected_with_the_allowed_ones():  # negative
    with pytest.raises(PmError) as err:
        acceptance.add(acceptance.load(None), FINDINGS, ["o1"], "opened-on-date", "x")
    assert str(err.value) == "reason 'opened-on-date' is not valid for overlap (use unobtainable or accept-as-is)"


def test_unknown_reason_and_unknown_id_are_rejected():  # negative
    with pytest.raises(PmError, match="unknown reason 'because'"):
        acceptance.add(acceptance.load(None), FINDINGS, ["g1"], "because", "x")
    with pytest.raises(PmError, match="unknown finding id 'zzz'; current ids: g1, o1, s1"):
        acceptance.add(acceptance.load(None), FINDINGS, ["zzz"], "accept-as-is", "x")


def test_a_failing_pair_in_a_batch_saves_nothing_of_the_batch():  # negative
    store = acceptance.load(None)
    with pytest.raises(PmError):
        acceptance.add(store, FINDINGS, ["g1", "o1"], "no-activity", "x")
    assert store["accepted"] == []


def test_batch_accept_stores_one_record_per_id_sorted_and_replaces_an_earlier_answer():  # unit
    store = acceptance.add(acceptance.load(None), FINDINGS, ["s1", "g1", "g1"], "accept-as-is", "first")
    store = acceptance.add(store, FINDINGS, ["g1"], "no-activity", "second")
    assert store["accepted"] == [
        {"id": "g1", "kind": "gap", "reason": "no-activity", "note": "second"},
        {"id": "s1", "kind": "scope", "reason": "accept-as-is", "note": "first"},
    ]


def test_note_is_one_collapsed_line_required_and_limited_to_200_characters():  # boundary
    assert acceptance.clean_note("  opened\n on   2025-03-01\t ") == "opened on 2025-03-01"
    assert acceptance.clean_note("x" * 200) == "x" * 200
    with pytest.raises(PmError, match="limit is 200"):
        acceptance.clean_note("x" * 201)
    for empty in (None, "", "  \n "):
        with pytest.raises(PmError, match="--note is required"):
            acceptance.clean_note(empty)


def test_start_date_must_be_a_real_iso_date():  # negative
    assert acceptance.parse_day("2025-01-01").isoformat() == "2025-01-01"
    for bad in (None, "", "01/02/2025", "2025-13-01"):
        with pytest.raises(PmError, match="--from must be a date"):
            acceptance.parse_day(bad)


def test_expected_start_is_kept_next_to_the_acceptances():  # unit
    store = acceptance.add(acceptance.load(None), FINDINGS, ["s1"], "accept-as-is", "ok")
    store = acceptance.with_expected_start(store, "2025-01-01")
    assert acceptance.expected_start(store) == "2025-01-01" and len(store["accepted"]) == 1
    assert acceptance.expected_start(acceptance.load(None)) == ""


def test_a_malformed_store_is_refused():  # negative
    with pytest.raises(PmError, match="malformed"):
        acceptance.load(["x"])
    with pytest.raises(PmError, match="malformed"):
        acceptance.load({"accepted": "x"})
