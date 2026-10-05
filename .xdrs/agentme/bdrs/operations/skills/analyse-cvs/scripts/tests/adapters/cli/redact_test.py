# Python 3.11+ pytest suite; run with: make test
import json

from analyse_cvs.adapters.cli import redact


def test_idempotent(tmp_path, capsys):
    path = tmp_path / "cv.md"
    path.write_text("Date of birth: 1990\n![x](y.png)\n", encoding="utf-8")
    assert redact.main([str(path), "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    once = path.read_text(encoding="utf-8")
    assert redact.main([str(path), "--json"]) == 0
    second = json.loads(capsys.readouterr().out)
    assert first["total"] == 2
    assert second["total"] == 0
    assert path.read_text(encoding="utf-8") == once


def test_missing_file(tmp_path, capsys):
    assert redact.main([str(tmp_path / "nope.md")]) == 1
    assert "not found" in capsys.readouterr().err


def test_human_readable_output(tmp_path, capsys):
    path = tmp_path / "cv.md"
    path.write_text("Gender: Male\n", encoding="utf-8")
    assert redact.main([str(path)]) == 0
    assert "1 redaction(s) (gender=1)" in capsys.readouterr().out
