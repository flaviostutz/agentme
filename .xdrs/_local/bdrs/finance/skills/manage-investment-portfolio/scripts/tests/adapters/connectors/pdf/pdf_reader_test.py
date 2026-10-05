"""PDF loading (text, image-only, locked, corrupt) on synthetic PDFs."""

from portfolio_manager.adapters.connectors.pdf.pdf_reader import clean_lines, read_pdf
from portfolio_manager.shared.values import sha256_file


def test_read_pdf_extracts_lines_and_hashes(make_pdf):
    path = make_pdf([["Hello", "  World  "]])
    doc = read_pdf(path)
    assert doc.status == "ok" and doc.lines() == ["Hello", "World"] and doc.text() == "Hello\nWorld"
    assert len(sha256_file(path)) == 64


def test_image_only_encrypted_and_corrupt_pdfs_are_flagged(make_pdf, tmp_path):
    assert read_pdf(make_pdf([[]], "empty.pdf")).status == "image-only"
    assert read_pdf(make_pdf([["secret"]], "locked.pdf", password="pw")).status == "encrypted"
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"not a pdf")
    doc = read_pdf(broken)
    assert doc.status == "unreadable" and doc.error


def test_clean_lines_drops_nul_and_blank_rows():
    assert clean_lines("a\x00b\n\n  c  \n") == ["ab", "c"]
