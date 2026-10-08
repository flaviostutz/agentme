"""What the user decided about each completeness finding; stored in the script-owned acceptances.json."""

import re
from datetime import date

from portfolio_manager.shared.errors import PmError

FILE = "acceptances.json"
MAX_NOTE = 200
EVERY_REASON = ("opened-on-date", "no-activity", "unobtainable", "accept-as-is")
SOURCE_REASONS = ("unobtainable", "accept-as-is")
# Finding kind -> reasons the user may give. Every kind produced by inputcheck must be listed here.
KIND_REASONS = {
    "gap": EVERY_REASON,
    "late-start": EVERY_REASON,
    "stale-end": EVERY_REASON,
    "derived-opening": EVERY_REASON,
    "check-warn": SOURCE_REASONS,
    "overlap": SOURCE_REASONS,
    "scope": ("accept-as-is",),
    "expected-start": ("accept-as-is",),
}


def load(raw: object) -> dict:
    """Normalised store {settings: {expected_start?}, accepted: [{id, kind, reason, note}]}."""
    if raw is None:
        return {"settings": {}, "accepted": []}
    if not isinstance(raw, dict) or not isinstance(raw.get("accepted", []), list):
        msg = f"{FILE} is malformed; it is written by `pm accept`, do not edit it by hand"
        raise PmError(msg)
    return {"settings": dict(raw.get("settings", {})), "accepted": list(raw.get("accepted", []))}


def expected_start(store: dict) -> str:
    return store["settings"].get("expected_start", "")


def parse_day(text: str | None) -> date:
    try:
        return date.fromisoformat(text or "")
    except ValueError as err:
        msg = f"--from must be a date like 2025-01-01, got {text!r}"
        raise PmError(msg) from err


def with_expected_start(store: dict, day: str) -> dict:
    return {**store, "settings": {**store["settings"], "expected_start": day}}


def clean_note(note: str | None) -> str:
    """One line of at most MAX_NOTE characters; the note is the user's own words and is required."""
    text = re.sub(r"\s+", " ", note or "").strip()
    if not text:
        msg = "--note is required: write in the user's words why this is acceptable"
        raise PmError(msg)
    if len(text) > MAX_NOTE:
        msg = f"--note has {len(text)} characters; the limit is {MAX_NOTE}"
        raise PmError(msg)
    return text


def check_reason(kind: str, reason: str | None) -> None:
    allowed = KIND_REASONS[kind]
    if reason in allowed:
        return
    if reason in EVERY_REASON:
        msg = f"reason {reason!r} is not valid for {kind} (use {' or '.join(allowed)})"
    else:
        msg = f"unknown reason {reason!r} (use one of {', '.join(EVERY_REASON)})"
    raise PmError(msg)


def add(store: dict, findings: list, ids: list, reason: str | None, note: str) -> dict:
    """Record the acceptance for each id; ids must name a current finding."""
    by_id = {f["id"]: f for f in findings}
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        listed = ", ".join(sorted(by_id)[:10]) or "none"
        msg = f"unknown finding id {unknown[0]!r}; current ids: {listed}"
        raise PmError(msg)
    for i in ids:
        check_reason(by_id[i]["kind"], reason)
    kept = [a for a in store["accepted"] if a["id"] not in ids]
    new = [{"id": i, "kind": by_id[i]["kind"], "reason": reason, "note": note} for i in dict.fromkeys(ids)]
    return {**store, "accepted": sorted(kept + new, key=lambda a: a["id"])}


def annotate(findings: list, store: dict) -> list:
    """Attach {reason, note} to each finding the user accepted; acceptances of vanished findings are ignored."""
    given = {a["id"]: {"reason": a["reason"], "note": a["note"]} for a in store["accepted"]}
    return [dict(f, accepted=given.get(f["id"])) for f in findings]
