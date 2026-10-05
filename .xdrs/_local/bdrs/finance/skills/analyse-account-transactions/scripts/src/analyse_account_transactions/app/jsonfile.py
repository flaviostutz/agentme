"""JSON files read and written through the store (indent 1, UTF-8 characters kept)."""

import json
from pathlib import Path
from typing import Any

from analyse_account_transactions.app.ports import LedgerStore


def read_json(store: LedgerStore, path: Path) -> Any | None:
    """The parsed JSON, or None when the file does not exist; json.JSONDecodeError for invalid JSON."""
    if not store.exists(path):
        return None
    return json.loads(store.read_text(path))


def write_json(store: LedgerStore, path: Path, data: Any) -> None:
    store.write_text(path, json.dumps(data, ensure_ascii=False, indent=1))
