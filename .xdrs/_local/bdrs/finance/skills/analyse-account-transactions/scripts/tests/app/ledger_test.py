"""Application-level tests of the ledger with the in-memory workspace (no file system)."""

import json
from decimal import Decimal

import pytest

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app.ports_mock import MemoryWorkspace
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Ledger, Row

FILE = ".tmp/l/a.md"
META = {
    "source": "src.csv",
    "normalizer": "llm",
    "bank": "Test Bank",
    "account-type": "current",
    "account-holder": "Jane Doe",
    "iban": "NL00TEST0000000001",
    "currency": "EUR",
    "period": "2026-01-01..2026-01-31",
    "opening-balance": "none",
    "closing-balance": "none",
}


def workspace() -> MemoryWorkspace:
    store = MemoryWorkspace()
    path = store.resolve_tmp(FILE, must_exist=False)
    rows = [
        Row("2026-01-02", "Coffee", Decimal("-3.50"), "Coffee payment"),
        Row("2026-01-03", "ACME", Decimal("100.00"), "salary"),
    ]
    led = Ledger(dict(META), rows)
    ledger.write(store, path, led)
    ledger.write_snapshot(store, path, led, {})
    return store


def test_apply_plan_without_a_file_system():
    store = workspace()
    plan = {"map": {"Coffee": {"category": "Eating Out", "flow": "Expenditure", "relevance": "Discretionary"}}}
    result = ledger.apply_plan(store, FILE, lambda: json.dumps(plan), source="auto", dry_run=False)
    assert len(result["changes"]) >= 1
    assert ledger.read(store, store.resolve_tmp(FILE)).rows[0].category == "Eating Out"


def test_drop_rows_updates_the_snapshot():
    store = workspace()
    result = ledger.drop_rows(store, FILE, "1")
    assert result["rows"] == 1
    assert store.exists(store.root / ".tmp/l/a.snapshot.json")


def test_paths_must_be_inside_tmp():
    store = workspace()
    with pytest.raises(LedgerError, match="must be inside .tmp/"):
        store.resolve_tmp("elsewhere/a.md")
    with pytest.raises(LedgerError, match="not found"):
        store.resolve_tmp(".tmp/l/missing.md")
    assert store.rel(store.resolve_tmp(FILE)) == FILE
    assert store.read_bytes(store.resolve_tmp(FILE)).startswith(b"# Transactions")
