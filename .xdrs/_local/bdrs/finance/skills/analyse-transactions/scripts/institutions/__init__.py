# Runtime: Python >=3.10; package imported by normalize.py and ground.py (scripts/ must be on sys.path).
"""Registry of institution modules (specialised parsers and checkers for known statement layouts).

Each module exposes:
  NAME, BANK, COUNTRY (ISO 3166 alpha-2 of the institution, '' when not a bank),
  detect(doc) -> bool, parse(doc, opts) -> (meta, rows, notes), check(doc, ledger) -> list of findings.
The first module whose detect() returns True wins, so keep detect() strict."""

from institutions import abn_amro, n26, revolut, splitwise

MODULES = [n26, revolut, splitwise, abn_amro]


def find(doc):
    return next((m for m in MODULES if m.detect(doc)), None)


def by_name(name: str):
    for m in MODULES:
        if m.NAME == name:
            return m
    raise KeyError(f"unknown institution module {name!r}; known: {', '.join(m.NAME for m in MODULES)}")
