"""Test helpers: `make_doc` (a Doc from line lists) and `make_pdf` (a real PDF built with PyMuPDF)."""

from pathlib import Path

import pytest

from portfolio_manager.shared.models import Doc


@pytest.fixture
def make_doc(tmp_path):
    """Return a factory: make_doc(pages, name) -> Doc backed by a real file (adapters hash the file)."""

    def factory(pages: list, name: str = "statement.pdf") -> Doc:
        path = tmp_path / name
        path.write_text("\n".join("\n".join(p) for p in pages), encoding="utf-8")
        return Doc(path, pages=pages)

    return factory


@pytest.fixture
def make_pdf(tmp_path):
    """Return a factory: make_pdf(pages, name, password) -> Path of a PDF with one text line per row."""
    import pymupdf

    def factory(pages: list, name: str = "synthetic.pdf", password: str = "") -> Path:
        pdf = pymupdf.open()
        font = pymupdf.Font("helv")
        for lines in pages:
            for chunk in range(0, max(len(lines), 1), 50):
                page = pdf.new_page()
                writer = pymupdf.TextWriter(page.rect)
                for i, line in enumerate(lines[chunk : chunk + 50]):
                    writer.append((40, 60 + 14 * i), line, font=font, fontsize=9)
                writer.write_text(page)
        path = tmp_path / name
        if password:
            pdf.save(path, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password)
        else:
            pdf.save(path)
        pdf.close()
        return path

    return factory
