"""Input check: what the statements cover per account, where days or months are missing, and what was merged or skipped.

The check is advisory. It reports facts; the user decides whether to proceed, add statements or stop.
"""

from datetime import date, timedelta

from portfolio_manager.app.records import short_hash

SNAPSHOT_GAP_DAYS = 35
SKIPPED = ("unsupported", "layout-drift", "encrypted", "image-only", "unreadable", "rejected")


def _day(text: str) -> date:
    return date.fromisoformat(text)


def _gap(account: str, start: date, end: date, rule: str) -> dict:
    s, e = start.isoformat(), end.isoformat()
    return {
        "id": short_hash("gap", account, s, e),
        "account": account,
        "start": s,
        "end": e,
        "days": (end - start).days + 1,
        "rule": rule,
    }


def _span_gaps(account: str, spans: list, tolerance: int, rule: str) -> list:
    """Days between covered spans that exceed `tolerance` uncovered days are a gap."""
    out, reach = [], None
    for start, end in sorted((_day(s), _day(e)) for s, e in spans):
        if reach is not None and (start - reach).days - 1 > tolerance:
            out.append(_gap(account, reach + timedelta(days=1), start - timedelta(days=1), rule))
        reach = end if reach is None else max(reach, end)
    return out


def _snapshot_gaps(account: str, dates: list, spans: list) -> list:
    """Snapshot and value-only accounts: more than 35 days with neither a reported value nor a covered period."""
    return _span_gaps(
        account,
        [*((d, d) for d in dates), *spans],
        SNAPSHOT_GAP_DAYS,
        f"more than {SNAPSHOT_GAP_DAYS} days between values",
    )


def gaps(ingest: dict, accounts: list, snapshots: list) -> list:
    modes = {a["id"]: a["mode"] for a in accounts}
    coverage = ingest.get("coverage", [])
    out = []
    for acct, mode in sorted(modes.items()):
        if mode == "transactions":
            spans = [(c["start"], c["end"]) for c in coverage if c["account"] == acct and c["kind"] == "ledger"]
            out += _span_gaps(acct, spans, 0, "uncovered days")
        else:
            spans = [(c["start"], c["end"]) for c in coverage if c["account"] == acct and c["kind"] == "snapshot"]
            out += _snapshot_gaps(acct, [s["date"] for s in snapshots if s["account"] == acct], spans)
    return out


def _covered(coverage: list, account: str) -> tuple:
    spans = sorted((c["start"], c["end"]) for c in coverage if c["account"] == account)
    return (spans[0][0], max(e for _, e in spans), len(spans)) if spans else ("", "", 0)


def check(ingest: dict, accounts: list, snapshots: list, unresolved: list, answers: dict) -> dict:
    """Facts about the loaded statements; every gap carries the user's note when one was recorded."""
    notes = ingest.get("notes", [])
    given = answers.get("answers", {})
    found = [dict(g, note=given.get(g["id"], "")) for g in gaps(ingest, accounts, snapshots)]
    coverage = ingest.get("coverage", [])
    files = ingest.get("files", [])
    return {
        "accounts": [
            dict(
                zip(("first", "last", "statements"), _covered(coverage, a["id"]), strict=True),
                account=a["id"],
                mode=a["mode"],
            )
            for a in accounts
        ],
        "gaps": found,
        "overlaps": [n for n in notes if n["kind"] in ("overlap-mismatch", "period-flows-overlap")],
        "merges": [n for n in notes if n["kind"] == "merged-timestamp"],
        "duplicates": [f for f in files if f["status"] == "duplicate"],
        "skipped": [f for f in files if f["status"] in SKIPPED],
        "failed_checks": [c for c in ingest.get("checks", []) if c["level"] == "fail"],
        "unresolved": [{"id": u["id"], "kind": u["kind"], "where": u["where"]} for u in unresolved],
    }


def render(result: dict) -> list:
    """Short text lines for chat; details stay in derived/input-check.json."""
    lines = ["Input check (advisory):"]
    lines += [
        f"- {a['account']} ({a['mode']}): {a['first'] or 'no statements'} to {a['last']} in {a['statements']} statement(s)"
        for a in result["accounts"]
    ]
    for g in result["gaps"]:
        note = f" - noted: {g['note']}" if g["note"] else ""
        lines.append(
            f"- GAP {g['account']} {g['start']}..{g['end']} ({g['days']} days; {g['rule']}) id {g['id']}{note}"
        )
    lines += [f"- OVERLAP {o['message']}" for o in result["overlaps"]]
    lines += [f"- MERGED {m['message']}" for m in result["merges"]]
    lines += [
        f"- DUPLICATE {d['file']} is identical to {d['duplicate_of']} and was ignored" for d in result["duplicates"]
    ]
    lines += [f"- NOT LOADED {f['file']}: {f['status']}" for f in result["skipped"]]
    lines += [
        f"- FAILED CHECK {c['file']}: {c['name']} expected {c['expected']} got {c['actual']}"
        for c in result["failed_checks"]
    ]
    lines += [f"- UNRESOLVED {u['kind']} {u['id']} {u['where']}" for u in result["unresolved"]]
    open_gaps = sum(1 for g in result["gaps"] if not g["note"])
    if len(lines) == 1 + len(result["accounts"]):
        lines.append("No gaps, overlaps, merges or skipped files.")
    lines.append(
        f"Gaps without a note: {open_gaps}. Proceed, add statements, or stop; note a gap with `pm answer --id <gap id> --value <note>`."
    )
    return lines
