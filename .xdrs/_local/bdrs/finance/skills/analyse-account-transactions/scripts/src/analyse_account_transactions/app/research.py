"""Cache of web research about counterparties (.tmp/<id>/research/cache.json). Makes no network calls.

lookup  cached findings for names (case/space-insensitive)
add     store one finding
import  merge caches of other analyses (newest wins)
Names and cities are what may be sent to a search engine, so they are rejected when they contain an IBAN,
an amount or a long number (account, card or reference).
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from analyse_account_transactions.app.jsonfile import read_json, write_json
from analyse_account_transactions.app.ports import LedgerStore
from analyse_account_transactions.shared.constants import CATEGORIES
from analyse_account_transactions.shared.errors import LedgerError

VERSION = 1
PRIVATE = [
    ("an IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,}")),
    ("an amount", re.compile(r"\d+[.,]\d{2}\b|[€$£]\s?\d")),
    ("a long number", re.compile(r"\d{6,}")),
    ("an e-mail address", re.compile(r"\S+@\S+\.\w+")),
]
MAX_NAME = 80
MAX_FINDING = 400
Clock = Callable[[], datetime]


@dataclass
class Finding:
    name: str
    url: str
    finding: str
    city: str = ""
    category_hint: str = ""


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load(store: LedgerStore, path: Path) -> dict[str, Any]:
    data = read_json(store, path)
    if data is None:
        return {}
    if not isinstance(data, dict) or data.get("version") != VERSION or not isinstance(data.get("entries"), dict):
        msg = f"{path.name} is not a research cache (version {VERSION})"
        raise LedgerError(msg)
    return data["entries"]


def save(store: LedgerStore, path: Path, entries: dict[str, Any]) -> None:
    write_json(store, path, {"version": VERSION, "entries": dict(sorted(entries.items()))})


def check_query(field: str, text: str) -> None:
    if not text.strip() or len(text) > MAX_NAME:
        msg = f"--{field} must be 1..{MAX_NAME} characters"
        raise LedgerError(msg)
    for label, pattern in PRIVATE:
        if pattern.search(text):
            msg = f"--{field} contains {label}; search the counterparty name only"
            raise LedgerError(msg)


def lookup(store: LedgerStore, cache: str, names: list[str]) -> dict[str, Any]:
    entries = load(store, store.resolve_tmp(cache, must_exist=False))
    found = {n: entries[norm(n)] for n in names if norm(n) in entries}
    return {"found": found, "missing": [n for n in names if norm(n) not in entries]}


def add(store: LedgerStore, cache: str, finding: Finding, clock: Clock) -> dict[str, Any]:
    check_query("name", finding.name)
    if finding.city:
        check_query("city", finding.city)
    if not re.match(r"^https?://\S+$", finding.url):
        msg = "--url must be an http(s) URL"
        raise LedgerError(msg)
    if not finding.finding.strip() or len(finding.finding) > MAX_FINDING:
        msg = f"--finding must be 1..{MAX_FINDING} characters"
        raise LedgerError(msg)
    if finding.category_hint and finding.category_hint not in CATEGORIES:
        msg = f"--category-hint must be one of {CATEGORIES}"
        raise LedgerError(msg)
    path = store.resolve_tmp(cache, must_exist=False)
    entries = load(store, path)
    entry = {
        "name": finding.name.strip(),
        "city": finding.city,
        "url": finding.url,
        "finding": finding.finding.strip(),
        "category-hint": finding.category_hint,
        "checked": clock().date().isoformat(),
    }
    entries[norm(finding.name)] = entry
    save(store, path, entries)
    return {"added": entry, "total": len(entries)}


def import_caches(store: LedgerStore, cache: str, files: list[str]) -> dict[str, Any]:
    path = store.resolve_tmp(cache, must_exist=False)
    entries = load(store, path)
    added = 0
    for p in files:
        for key, entry in load(store, store.resolve_tmp(p)).items():
            if key not in entries or entry.get("checked", "") > entries[key].get("checked", ""):
                added += key not in entries
                entries[key] = entry
    save(store, path, entries)
    return {"total": len(entries), "added": added}
