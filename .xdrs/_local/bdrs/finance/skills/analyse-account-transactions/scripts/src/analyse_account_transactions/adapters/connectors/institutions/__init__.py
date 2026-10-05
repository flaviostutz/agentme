"""Registry of institution modules (specialised parsers and checkers for known statement layouts).

Each module defines an Institution: name, bank, country (ISO 3166 alpha-2 of the institution, '' when not a
bank), detect(doc) -> bool, parse(doc, opts) -> (meta, rows, notes) and check(doc, ledger) -> list of findings.
The first institution whose detect() returns True wins, so keep detect() strict.
"""

from analyse_account_transactions.adapters.connectors.institutions import abn_amro, n26, revolut, splitwise
from analyse_account_transactions.shared.models import Doc, Institution


class Institutions:
    """InstitutionRegistry over an ordered list of institutions."""

    def __init__(self, institutions: list[Institution]) -> None:
        self.institutions = institutions

    def find(self, doc: Doc) -> Institution | None:
        return next((m for m in self.institutions if m.detect(doc)), None)

    def by_name(self, name: str) -> Institution:
        for m in self.institutions:
            if m.name == name:
                return m
        known = ", ".join(m.name for m in self.institutions)
        msg = f"unknown institution module {name!r}; known: {known}"
        raise KeyError(msg)


def default_registry() -> Institutions:
    return Institutions([n26.INSTITUTION, revolut.INSTITUTION, splitwise.INSTITUTION, abn_amro.INSTITUTION])
