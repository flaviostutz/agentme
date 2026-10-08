"""Input check: what the statements cover per account and what is missing, doubtful or unconfirmed.

Findings are facts computed by the script. The user decides about each one: add statements or accept it
with a reason and a note (`pm accept`). Reports are refused while a finding is open.
"""

from datetime import date, timedelta
from decimal import Decimal

from portfolio_manager.app import acceptance
from portfolio_manager.app.records import short_hash

TOLERANCE_DAYS = 35
SKIPPED = ("unsupported", "layout-drift", "encrypted", "image-only", "unreadable", "rejected")
OVERLAP_KINDS = ("overlap-mismatch", "period-flows-overlap")
KIND_ORDER = tuple(acceptance.KIND_REASONS)


def _day(text: str) -> date:
    return date.fromisoformat(text)


def _finding(kind: str, account: str, message: str, *key: object, **extra: object) -> dict:
    return {
        "id": short_hash(kind, account, *key),
        "kind": kind,
        "account": account,
        "label": kind,
        "message": message,
        **extra,
    }


def _gap(account: str, start: date, end: date, rule: str) -> dict:
    s, e = start.isoformat(), end.isoformat()
    days = (end - start).days + 1
    extra = {"label": f"{s}..{e}", "start": s, "end": e, "days": days, "rule": rule}
    return _finding("gap", account, f"{s}..{e} ({days} days; {rule})", s, e, **extra)


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
        TOLERANCE_DAYS,
        f"more than {TOLERANCE_DAYS} days between values",
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


def _bounds(ingest: dict, snapshots: list) -> dict:
    """{account: (first, last)} over ledger and snapshot statements; reference statements do not count."""
    days: dict = {}
    for c in ingest.get("coverage", []):
        if c["kind"] in ("ledger", "snapshot"):
            days.setdefault(c["account"], []).extend([c["start"], c["end"]])
    for s in snapshots:
        days.setdefault(s["account"], []).append(s["date"])
    return {a: (min(d), max(d)) for a, d in days.items()}


def latest_date(ingest: dict, snapshots: list) -> str:
    """Latest date any ledger or snapshot statement covers; empty when there is none."""
    return max((last for _, last in _bounds(ingest, snapshots).values()), default="")


def _late_starts(accounts: list, bounds: dict, start: str) -> list:
    out = []
    for a in accounts:
        first = bounds.get(a["id"], ("", ""))[0]
        if not first:
            msg = "no ledger or snapshot statement (reference statements only)"
            out.append(_finding("late-start", a["id"], msg, "none"))
        elif start and (_day(first) - _day(start)).days > TOLERANCE_DAYS:
            out.append(_finding("late-start", a["id"], f"first statement {first}, expected {start}", start, first))
    return out


def _stale_ends(bounds: dict, latest: str) -> list:
    return [
        _finding("stale-end", acct, f"last value {last}, latest data {latest}", last, latest)
        for acct, (_, last) in sorted(bounds.items())
        if latest and (_day(latest) - _day(last)).days > TOLERANCE_DAYS
    ]


def _derived_openings(openings: dict) -> list:
    out = []
    for acct, op in sorted(openings.items()):
        cash = op.get("cash", "0")
        held = [(p["isin"] or p["symbol"], p["quantity"]) for p in op.get("positions", [])]
        if Decimal(cash) != 0 or held:
            when = op.get("date") or "the first statement"
            msg = f"balance before {when}: cash {cash} and {len(held)} position(s) that no statement shows"
            out.append(_finding("derived-opening", acct, msg, op.get("date"), cash, held))
    return out


def _check_warns(ingest: dict) -> list:
    return [
        _finding(
            "check-warn",
            c.get("account", ""),
            f"{c['file']}: {c['name']} expected {c['expected']} got {c['actual']}",
            c["file"],
            c["name"],
            c["expected"],
            c["actual"],
        )
        for c in ingest.get("checks", [])
        if c["level"] == "warn"
    ]


def _overlaps(ingest: dict) -> list:
    return [
        _finding("overlap", "", n["message"], n["kind"], n["message"])
        for n in ingest.get("notes", [])
        if n["kind"] in OVERLAP_KINDS
    ]


def _scope(accounts: list) -> list:
    ids = sorted(a["id"] for a in accounts)
    if not ids:
        return []
    return [_finding("scope", "", f"accounts in scope: {', '.join(ids)}; confirm no other account is missing", *ids)]


def _expected_start(start: str) -> list:
    if start:
        return []
    msg = "no expected start date given (`pm check-input --from YYYY-MM-DD`); coverage before the first statement is unknown"
    return [_finding("expected-start", "", msg)]


def findings(ingest: dict, accounts: list, snapshots: list, openings: dict, start: str) -> list:
    """Every coverage fact the user must confirm or fix before reports are written."""
    bounds = _bounds(ingest, snapshots)
    found = [
        *gaps(ingest, accounts, snapshots),
        *_late_starts(accounts, bounds, start),
        *_stale_ends(bounds, latest_date(ingest, snapshots)),
        *_derived_openings(openings),
        *_check_warns(ingest),
        *_overlaps(ingest),
        *_scope(accounts),
        *_expected_start(start),
    ]
    unique = {f["id"]: f for f in found}.values()
    return sorted(unique, key=lambda f: (KIND_ORDER.index(f["kind"]), f["account"], f["id"]))


def _covered(coverage: list, account: str) -> tuple:
    spans = sorted((c["start"], c["end"]) for c in coverage if c["account"] == account)
    return (spans[0][0], max(e for _, e in spans), len(spans)) if spans else ("", "", 0)


def check(ingest: dict, accounts: list, snapshots: list, unresolved: list, openings: dict, store: dict) -> dict:
    """Facts about the loaded statements; each finding says whether the user accepted it."""
    notes = ingest.get("notes", [])
    coverage = ingest.get("coverage", [])
    files = ingest.get("files", [])
    start = acceptance.expected_start(store)
    return {
        "expected_start": start,
        "accounts": [
            dict(
                zip(("first", "last", "statements"), _covered(coverage, a["id"]), strict=True),
                account=a["id"],
                mode=a["mode"],
            )
            for a in accounts
        ],
        "findings": acceptance.annotate(findings(ingest, accounts, snapshots, openings, start), store),
        "merges": [n for n in notes if n["kind"] == "merged-timestamp"],
        "duplicates": [f for f in files if f["status"] == "duplicate"],
        "skipped": [f for f in files if f["status"] in SKIPPED],
        "failed_checks": [c for c in ingest.get("checks", []) if c["level"] == "fail"],
        "unresolved": [{"id": u["id"], "kind": u["kind"], "where": u["where"]} for u in unresolved],
    }


def open_findings(result: dict) -> list:
    return [f for f in result["findings"] if not f["accepted"]]


def _words(*parts: str) -> str:
    return " ".join(p for p in parts if p)


def render(result: dict) -> list:
    """Short text lines for chat; details stay in derived/input-check.json."""
    still_open = open_findings(result)
    accepted = [f for f in result["findings"] if f["accepted"]]
    lines = [f"Input check: {len(still_open)} open, {len(accepted)} accepted."]
    lines += [
        f"- {a['account']} ({a['mode']}): {a['first'] or 'no statements'} to {a['last']} in {a['statements']} statement(s)"
        for a in result["accounts"]
    ]
    lines += [f"- {_words(f['kind'].upper(), f['account'], f['message'], 'id', f['id'])}" for f in still_open]
    lines += [
        f'- ACCEPTED {_words(f["kind"], f["account"])}: {f["accepted"]["reason"]} - "{f["accepted"]["note"]}" id {f["id"]}'
        for f in accepted
    ]
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
    if still_open or result["unresolved"]:
        lines.append("Ask the user per finding. Never accept for them.")
    else:
        lines.append("Nothing open; reports can be written.")
    return lines
