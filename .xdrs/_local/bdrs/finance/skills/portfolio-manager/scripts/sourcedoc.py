# Runtime: Python >=3.10; imported by pm.py, inspector.py and adapters, which declare pymupdf.
"""Load a source PDF into a Doc (text lines per page); locked, image-only or unreadable files are flagged."""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path


class PmError(ValueError):
    """Invalid input: path, file layout, plan or answer. Maps to exit code 2."""


@dataclass
class Doc:
    path: Path
    pages: list = field(default_factory=list)  # one list of stripped non-empty lines per page
    metadata: dict = field(default_factory=dict)
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

    def lines(self) -> list:
        return [line for page in self.pages for line in page]

    def text(self) -> str:
        return "\n".join(self.lines())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_lines(text: str) -> list:
    return [line.strip() for line in text.replace("\x00", "").splitlines() if line.strip()]


def read_pdf(path: Path) -> Doc:
    import pymupdf

    pymupdf.TOOLS.mupdf_display_errors(False)
    try:
        with pymupdf.open(path) as pdf:
            if pdf.needs_pass:
                return Doc(path, encrypted=True)
            pages = [clean_lines(p.get_text()) for p in pdf]
            metadata = {k: str(v) for k, v in (pdf.metadata or {}).items() if k in ("producer", "creator") and v}
    except Exception as err:  # noqa: BLE001 - pymupdf raises several types for corrupt files
        return Doc(path, error=f"{type(err).__name__}: {err}")
    return Doc(path, pages=pages, metadata=metadata)
