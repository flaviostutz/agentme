"""Rebuild the ledger (accounts, openings, events, snapshots, references) from the exported CSV files."""

import json
from collections import defaultdict

from portfolio_manager.app import ppcsv
from portfolio_manager.shared.errors import PmError

EVENT_FIELDS = ("time", "isin", "symbol", "name", "quantity", "currency", "cash", "fee", "tax", "ref")
OPTIONAL_FIELDS = ("price", "gross", "fx_rate", "raw_type")
POSITION_FIELDS = ("isin", "symbol", "name", "quantity")
NON_EVENTS = ("OPENING", "OPENING_CASH")


def _tx_rows(files: dict[str, str]) -> list[dict]:
    rows = []
    for name in (ppcsv.PORTFOLIO_TRANSACTIONS, ppcsv.ACCOUNT_TRANSACTIONS):
        if name not in files:
            msg = f"missing export file {name}"
            raise PmError(msg)
        rows += ppcsv.loads(files[name])
    return rows


def _event(row: dict) -> dict:
    e = {"account": row["ledger_account"], "type": row["ledger_type"], "date": row["Date"]}
    e.update({k: row[f"ledger_{k}"] for k in EVENT_FIELDS})
    e.update({k: row[f"ledger_{k}"] for k in OPTIONAL_FIELDS if row[f"ledger_{k}"] != ""})
    return e


def _accounts(files: dict[str, str], rows: list[dict]) -> dict:
    positions: dict[str, list] = defaultdict(list)
    for r in sorted((r for r in rows if r["ledger_type"] == "OPENING"), key=lambda r: int(r["ledger_seq"])):
        positions[r["ledger_account"]].append({k: r[f"ledger_{k}"] for k in POSITION_FIELDS})
    accounts, openings = [], {}
    for r in ppcsv.loads(files[ppcsv.ACCOUNTS]):
        acct_id = r["ledger_account"]
        accounts.append(
            {
                "id": acct_id,
                "institution": r["ledger_institution"],
                "currency": r["ledger_currency"],
                "mode": r["ledger_mode"],
            }
        )
        if r["ledger_opening_cash"] != "":
            openings[acct_id] = {
                "date": r["ledger_opening_date"] or None,
                "cash": r["ledger_opening_cash"],
                "positions": positions[acct_id],
            }
    return {"accounts": accounts, "openings": openings}


def read(files: dict[str, str]) -> dict:
    """files: {name: text}. Returns accounts, events, snapshots and references as stored in data/*.json."""
    rows = _tx_rows(files)
    events = sorted((r for r in rows if r["ledger_type"] not in NON_EVENTS), key=lambda r: int(r["ledger_seq"]))
    return {
        "accounts": _accounts(files, rows),
        "events": [_event(r) for r in events],
        "snapshots": [json.loads(r["record_json"]) for r in ppcsv.loads(files[ppcsv.SNAPSHOTS])],
        "references": [json.loads(r["record_json"]) for r in ppcsv.loads(files[ppcsv.REFERENCES])],
    }
