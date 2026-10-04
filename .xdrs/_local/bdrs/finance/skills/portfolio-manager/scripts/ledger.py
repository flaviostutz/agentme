# Runtime: Python >=3.10; merges per-file adapter results into one canonical ledger (pure functions, no I/O).
"""Merge parsed statements: overlap dedupe, restatement conflicts, ISIN unification and opening positions."""

import json
from collections import Counter, defaultdict
from decimal import Decimal

from institutions.common import dec, unresolved
from util import ZERO

TYPE_RANK = {"DEPOSIT": 0, "TRANSFER_IN": 0, "BUY": 1, "SPLIT": 1, "DIVIDEND": 2, "INTEREST": 2, "SELL": 3,
             "FEE": 4, "TAX": 4, "WITHDRAWAL": 5, "TRANSFER_OUT": 5}
QTY_SIGN = {"BUY": 1, "SELL": -1, "SPLIT": 1, "TRANSFER_IN": 1, "TRANSFER_OUT": -1}


def _key(e: dict) -> tuple:
    return (e["account"], e["date"], e["time"], e["type"], e["symbol"], e["isin"], e["quantity"], e["cash"])


def _sort_key(e: dict) -> tuple:
    return (e["date"], e["time"], e["account"], TYPE_RANK.get(e["type"], 9), e["isin"] or e["symbol"], e["cash"], e["ref"])


def merge_events(per_file: list) -> list:
    """Overlapping statements repeat the same rows; count per key = max across files (identical trades stay separate)."""
    best: dict = {}
    counts: dict = defaultdict(int)
    for events in per_file:
        local = Counter(_key(e) for e in events)
        for e in events:
            best.setdefault(_key(e), e)
        for k, n in local.items():
            counts[k] = max(counts[k], n)
    merged = [best[k] for k, n in counts.items() for _ in range(n)]
    return sorted(merged, key=_sort_key)


def _unify_isin(events: list, snapshots: list, references: list) -> None:
    sym2isin: dict = {}
    for r in references:
        if r.get("kind") == "pnl-sale" and r.get("isin") and r.get("symbol"):
            sym2isin[(r["account"], r["symbol"])] = r["isin"]
    for s in snapshots:
        for p in s["positions"]:
            if p["isin"] and p["symbol"]:
                sym2isin[(s["account"], p["symbol"])] = p["isin"]
    for e in events:
        if not e["isin"] and e["symbol"]:
            e["isin"] = sym2isin.get((e["account"], e["symbol"]), "")


def _merge_snapshots(snapshots: list) -> tuple:
    out: dict = {}
    errors = []
    for s in snapshots:
        k = (s["account"], s["date"])
        if k not in out:
            out[k] = s
            continue
        have = out[k]
        if have["total"] != s["total"] and None not in (have["total"], s["total"]):
            errors.append(f"conflicting statements for {k[0]} on {k[1]}: total {have['total']} vs {s['total']} (restated statement)")
        elif have["positions"] == [] and s["positions"]:
            out[k] = s  # keep the richer snapshot
    return [out[k] for k in sorted(out)], errors


def _openings(accounts: dict, events: list, snapshots: list, first_opening: dict) -> tuple:
    """Opening quantity per instrument = latest reported quantity minus the net quantity of all merged events."""
    result, errors = {}, []
    for acct_id, acct in sorted(accounts.items()):
        if acct["mode"] != "transactions":
            continue
        snaps = [s for s in snapshots if s["account"] == acct_id and s["positions"]]
        end = max(snaps, key=lambda s: s["date"]) if snaps else None
        delta: dict = defaultdict(lambda: ZERO)
        for e in events:
            if e["account"] == acct_id and e["type"] in QTY_SIGN and (end is None or e["date"] <= end["date"]):
                delta[e["isin"] or e["symbol"]] += QTY_SIGN[e["type"]] * Decimal(e["quantity"])
        ending = {(p["isin"] or p["symbol"]): p for p in (end["positions"] if end else [])}
        positions = []
        for key in sorted(set(ending) | set(delta)):
            qty = Decimal(ending[key]["quantity"]) if key in ending and ending[key]["quantity"] is not None else ZERO
            opening = qty - delta[key]
            if opening < -Decimal("0.000001"):
                errors.append(f"{acct_id}: {key} sold more than held (derived opening quantity {dec(opening)}); the position is unreliable")
            elif opening > Decimal("0.000001"):
                src = ending.get(key, {})
                positions.append({"isin": src.get("isin", key if len(key) == 12 else ""), "symbol": src.get("symbol", ""),
                                  "name": src.get("name", ""), "quantity": dec(opening)})
        info = first_opening.get(acct_id, {})
        result[acct_id] = {"date": info.get("date"), "cash": info.get("cash", "0"), "positions": positions}
    return result, errors


def merge(parsed: list, answers: dict) -> dict:
    """parsed: [{file, sha256, results: [adapter result dicts]}]; answers: {accept_files: [sha], answers: {id: value}}."""
    accept = set(answers.get("accept_files", []))
    answered = set(answers.get("answers", {}))
    files, checks, errors = [], [], []
    accounts: dict = {}
    events_by_file, snapshots, references, pending = [], [], [], {}
    first_opening: dict = {}
    for item in parsed:
        results = item["results"]
        fails = [dict(c, file=item["file"]) for r in results for c in r["checks"] if c["level"] == "fail"]
        for r in results:
            checks += [dict(c, file=item["file"], account=r["account"]["id"]) for c in r["checks"] if c["level"] != "ok"]
        if fails and item["sha256"] not in accept:
            u = unresolved(item["sha256"], "rejected-file", "; ".join(f"{c['name']}: expected {c['expected']} got {c['actual']}" for c in fails),
                           "This file failed its own reconciliation and was not loaded. Accept it anyway (answer accept) or fix the source?", item["file"])
            pending[u["id"]] = u
            files.append({"file": item["file"], "sha256": item["sha256"], "status": "rejected", "adapter": results[0]["adapter"] if results else ""})
            continue
        files.append({"file": item["file"], "sha256": item["sha256"], "status": "accepted" if fails else "loaded",
                      "adapter": results[0]["adapter"] if results else ""})
        for r in results:
            acct = r["account"]
            accounts.setdefault(acct["id"], dict(acct))
            if r["kind"] == "ledger":
                events_by_file.append(r["events"])
                if r["opening"] and (acct["id"] not in first_opening or r["opening"]["date"] < first_opening[acct["id"]]["date"]):
                    first_opening[acct["id"]] = r["opening"]
            snapshots += r["snapshots"]
            references += r["references"]
            for u in r["unresolved"]:
                pending[u["id"]] = u
    events = merge_events(events_by_file)
    snapshots, snap_errors = _merge_snapshots(snapshots)
    _unify_isin(events, snapshots, references)
    openings, open_errors = _openings(accounts, events, snapshots, first_opening)
    uniq = {json.dumps(r, sort_keys=True): r for r in references}
    return {
        "accounts": {"accounts": [accounts[k] for k in sorted(accounts)], "openings": openings},
        "events": events,
        "snapshots": snapshots,
        "references": [uniq[k] for k in sorted(uniq)],
        "unresolved": [pending[k] for k in sorted(pending) if k not in answered],
        "ingest": {"files": sorted(files, key=lambda f: f["file"]), "checks": checks, "errors": errors + snap_errors + open_errors},
    }
