"""Institution adapter registry: detect which adapter reads a document (first match wins)."""

import hashlib
from pathlib import Path
from types import ModuleType

from portfolio_manager.adapters.connectors.institutions import (
    bb_informe,
    bb_portfolio,
    revolut_pnl,
    revolut_statement,
    trading212,
    upvest_expost,
    upvest_snapshot,
    upvest_tax,
)
from portfolio_manager.shared.models import Doc

ADAPTERS = [
    revolut_statement,
    revolut_pnl,
    trading212,
    upvest_snapshot,
    upvest_tax,
    upvest_expost,
    bb_portfolio,
    bb_informe,
]


class InstitutionRegistry:
    """Ordered institution adapters; each is a module with NAME, detect(doc) and parse(doc, answers)."""

    def __init__(self, adapters: list[ModuleType]) -> None:
        self.adapters = adapters

    def detect(self, doc: Doc) -> ModuleType | None:
        """Return the first adapter that recognizes the document, or None."""
        return next((a for a in self.adapters if a.detect(doc)), None)

    def by_name(self, name: str) -> ModuleType | None:
        return next((a for a in self.adapters if name == a.NAME), None)

    def fingerprint(self) -> str:
        """Hash of the adapter sources, so cached parse results are dropped when an adapter changes."""
        digest = hashlib.sha256()
        for adapter in self.adapters:
            digest.update(Path(adapter.__file__).read_bytes())
        return digest.hexdigest()[:8]


def default_registry() -> InstitutionRegistry:
    return InstitutionRegistry(list(ADAPTERS))
