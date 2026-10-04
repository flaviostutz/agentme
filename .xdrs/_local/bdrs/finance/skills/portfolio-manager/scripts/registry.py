# Runtime: Python >=3.10; imported by pm.py (ingest). Maps a source document to the adapter that can read it.
"""Adapter registry: detect which institution adapter reads a document."""

from institutions import (
    bb_informe,
    bb_portfolio,
    revolut_pnl,
    revolut_statement,
    trading212,
    upvest_expost,
    upvest_snapshot,
    upvest_tax,
)
from sourcedoc import Doc

ADAPTERS = [revolut_statement, revolut_pnl, trading212, upvest_snapshot, upvest_tax, upvest_expost, bb_portfolio, bb_informe]


def detect(doc: Doc):
    """Return the first adapter whose detect() accepts the document, or None."""
    for adapter in ADAPTERS:
        if adapter.detect(doc):
            return adapter
    return None


def by_name(name: str):
    return next((a for a in ADAPTERS if a.NAME == name), None)
