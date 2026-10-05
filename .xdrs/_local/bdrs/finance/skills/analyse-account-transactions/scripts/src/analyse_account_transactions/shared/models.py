"""Data types shared by the application layer and the adapters."""

from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from analyse_account_transactions.shared.values import format_value


@dataclass
class Row:
    timestamp: str
    title: str
    value: Decimal
    description: str
    category: str = ""
    flow: str = ""
    relevance: str = ""
    needs: str = ""

    @property
    def date(self) -> str:
        return self.timestamp[:10]

    def key(self) -> list[str]:
        return [self.timestamp, format_value(self.value), self.description]


@dataclass
class Ledger:
    meta: dict[str, str]
    rows: list[Row]


@dataclass
class Doc:
    """A loaded source file: page text and word positions (PDF), a table, raw text, or a marker for the LLM path."""

    path: Path
    kind: str  # pdf | table | text | image | llm-only
    texts: list[str] = field(default_factory=list)  # one string per PDF page, or one for text files
    words: list[list[dict[str, Any]]] = field(default_factory=list)  # pdfplumber word dicts per PDF page
    table: list[list[str]] = field(default_factory=list)  # rows of strings
    encrypted: bool = False

    @property
    def ext(self) -> str:
        return self.path.suffix.lower()

    @property
    def has_text(self) -> bool:
        return any(t.strip() for t in self.texts) or bool(self.table)

    def lines(self) -> list[str]:
        """All source lines used by grounding: text lines, or table rows joined with ' | '."""
        if self.table:
            return [" | ".join(r) for r in self.table]
        return [line for t in self.texts for line in t.splitlines()]


ParseResult = tuple[dict[str, str], list[Row], list[str]]


@dataclass(frozen=True)
class Institution:
    """A specialised parser and checker for one known statement layout.

    detect(doc) -> bool, parse(doc, opts) -> (meta, rows, notes), check(doc, ledger) -> list of findings.
    """

    name: str
    bank: str
    country: str  # ISO 3166 alpha-2 of the institution, '' when not a bank
    detect: Callable[[Doc], bool]
    parse: Callable[[Doc, dict[str, Any]], ParseResult]
    check: Callable[[Doc, Ledger], list[dict[str, Any]]]
