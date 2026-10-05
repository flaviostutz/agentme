"""Data shapes shared across layers."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Doc:
    """A source PDF loaded as text lines per page; locked, image-only or unreadable files are flagged."""

    path: Path
    pages: list[list[str]] = field(default_factory=list)  # one list of stripped non-empty lines per page
    metadata: dict[str, Any] = field(default_factory=dict)
    encrypted: bool = False
    error: str = ""

    @property
    def has_text(self) -> bool:
        return any(self.pages)

    @property
    def status(self) -> str:
        if self.encrypted:
            return "encrypted"
        if self.error:
            return "unreadable"
        return "ok" if self.has_text else "image-only"

    def lines(self) -> list[str]:
        return [line for page in self.pages for line in page]

    def text(self) -> str:
        return "\n".join(self.lines())
