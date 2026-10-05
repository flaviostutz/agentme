"""PDF connector: loads a source PDF into a Doc with PyMuPDF."""

from pathlib import Path

import pymupdf

from portfolio_manager.shared.models import Doc


def clean_lines(text: str) -> list:
    return [line.strip() for line in text.replace("\x00", "").splitlines() if line.strip()]


def read_pdf(path: Path) -> Doc:
    pymupdf.TOOLS.mupdf_display_errors(False)  # noqa: FBT003
    try:
        with pymupdf.open(path) as pdf:
            if pdf.needs_pass:
                return Doc(path, encrypted=True)
            pages = [clean_lines(p.get_text()) for p in pdf]
            metadata = {k: str(v) for k, v in (pdf.metadata or {}).items() if k in ("producer", "creator") and v}
    except Exception as err:  # noqa: BLE001 - pymupdf raises several types for corrupt files
        return Doc(path, error=f"{type(err).__name__}: {err}")
    return Doc(path, pages=pages, metadata=metadata)
