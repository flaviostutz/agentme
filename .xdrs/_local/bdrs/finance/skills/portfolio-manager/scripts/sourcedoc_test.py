# Runtime: pytest; PDF loading (text, image-only, locked, corrupt), inspector fingerprints and adapter detection on synthetic PDFs.
from pathlib import Path

import inspector
import registry
import sourcedoc
from samples_test import bb_portfolio, revolut_statement, trading212


def test_read_pdf_extracts_lines_and_hashes(make_pdf):
    path = make_pdf([["Hello", "  World  "]])
    doc = sourcedoc.read_pdf(path)
    assert doc.status == "ok" and doc.lines() == ["Hello", "World"] and doc.text() == "Hello\nWorld"
    assert len(sourcedoc.sha256_file(path)) == 64


def test_image_only_encrypted_and_corrupt_pdfs_are_flagged(make_pdf, tmp_path):
    assert sourcedoc.read_pdf(make_pdf([[]], "empty.pdf")).status == "image-only"
    assert sourcedoc.read_pdf(make_pdf([["secret"]], "locked.pdf", password="pw")).status == "encrypted"
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"not a pdf")
    doc = sourcedoc.read_pdf(broken)
    assert doc.status == "unreadable" and doc.error


def test_clean_lines_drops_nul_and_blank_rows():
    assert sourcedoc.clean_lines("a\x00b\n\n  c  \n") == ["ab", "c"]


def test_inspector_reports_structure_without_amounts(make_pdf, tmp_path):
    path = make_pdf(trading212(), "t212.pdf")
    info = inspector.inspect_pdf(path)
    assert info["status"] == "ok" and info["institutions"]["trading212"] >= 1
    assert info["date_formats"] and info["isin_count"] >= 1
    assert "1,010.85" not in str(info) and "ABC1234" not in str(info)
    locked = inspector.inspect_pdf(make_pdf([["x"]], "locked.pdf", password="pw"))
    assert locked["status"] == "encrypted" and "pages" not in locked
    assert [i["file"] for i in inspector.inspect_dir(Path(path).parent)] == sorted(i["file"] for i in inspector.inspect_dir(Path(path).parent))


def test_registry_detects_the_right_adapter(make_doc):
    assert registry.detect(make_doc(trading212())).NAME == "trading212"
    assert registry.detect(make_doc(revolut_statement())).NAME == "revolut_statement"
    assert registry.detect(make_doc(bb_portfolio())).NAME == "bb_portfolio"
    assert registry.detect(make_doc([["unknown layout"]])) is None
    assert registry.by_name("bb_informe").NAME == "bb_informe" and registry.by_name("nope") is None
