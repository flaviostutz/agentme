# Tests for normalize.py: staging (folders, zips, skips), discovery (period, conflicts, gaps) and runs.
import json
import zipfile

import ledger
import normalize
import pytest
from conftest import HOLDER, N26_PAGES, SPLITWISE_CSV, make_pdf

RUN = "--id", "t1"


def call(capsys, *argv):
    code = normalize.main([*argv])
    out, err = capsys.readouterr()
    return code, (json.loads(out) if code == 0 else err)


def inbox(work):
    src = work / "inbox"
    (src / "bank").mkdir(parents=True)
    (src / "bank" / "Jan 2026.pdf").write_bytes(make_pdf(N26_PAGES))
    (src / "shared.csv").write_text(SPLITWISE_CSV, encoding="utf-8")
    (src / "unknown.csv").write_text("When;What;How much\n02-01-2026;Shop;-1,00\n", encoding="utf-8")
    (src / ".DS_Store").write_bytes(b"x")
    (src / ".work").mkdir()
    (src / ".work" / "old.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (src / "notes.docx").write_bytes(b"x")
    (src / "x.snapshot.json").write_text("{}", encoding="utf-8")
    (src / "z-copy.csv").write_text(SPLITWISE_CSV, encoding="utf-8")
    return src


def test_stage_folder(work, capsys):
    code, result = call(capsys, "stage", str(inbox(work)), *RUN)
    assert code == 0
    assert sorted(s["path"] for s in result["staged"]) == ["bank/jan-2026.pdf", "shared.csv", "unknown.csv"]
    reasons = sorted(s["reason"].split(" ")[0] for s in result["skipped"])
    assert reasons == ["artifact", "duplicate", "hidden", "hidden", "unsupported"]
    code, again = call(capsys, "stage", "inbox", *RUN)
    assert again["staged"] == [] and len(json.loads((work / ".tmp/t1/.work/staging.json").read_text())) == 2


def test_stage_zip(work, capsys):
    path = work / "export.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("statements/a.csv", "a,b\n1,2\n")
        z.writestr("../evil.csv", "x")
        z.writestr("inner.zip", "x")
        z.writestr("__MACOSX/a.csv", "x")
    (work / "broken.zip").write_bytes(b"nope")
    code, result = call(capsys, "stage", "export.zip", *RUN)
    assert code == 0
    assert [s["path"] for s in result["staged"]] == ["export/statements/a.csv"]
    assert sorted(s["reason"] for s in result["skipped"]) == ["hidden or system file", "nested zip not extracted",
                                                             "unsafe path in zip"]
    assert call(capsys, "stage", "broken.zip", *RUN)[1]["skipped"][0]["reason"] == "corrupt zip"


def test_stage_zip_limits(work, capsys, monkeypatch):
    monkeypatch.setattr(normalize, "MAX_ZIP_FILES", 1)
    with zipfile.ZipFile(work / "big.zip", "w") as z:
        z.writestr("a.csv", "1")
        z.writestr("b.csv", "2")
    assert "over limits" in call(capsys, "stage", "big.zip", *RUN)[1]["skipped"][0]["reason"]


def test_stage_name_clash(work, capsys):
    (work / "a").mkdir()
    (work / "a" / "x.csv").write_text("1", encoding="utf-8")
    (work / "b").mkdir()
    (work / "b" / "x.csv").write_text("2", encoding="utf-8")
    call(capsys, "stage", "a/x.csv", *RUN)
    assert call(capsys, "stage", "b/x.csv", *RUN)[1]["staged"][0]["path"] == "x--2.csv"


@pytest.mark.parametrize(("argv", "message"), [
    (("stage", "missing", *RUN), "input does not exist"),
    (("stage", ".tmp", "--id", "Bad Id"), "--id must match"),
    (("stage", ".tmp/t1", *RUN), "must not be inside"),
    (("discover", *RUN), "nothing staged"),
    (("run", "none.csv", *RUN), "source not found"),    (("rename", "--id", "none", "--to", "t2"), "does not exist"),
    (("rename", *RUN, "--to", "t1"), "already exists"),
    (("rename", *RUN, "--to", "Bad Id"), "--id must match"),])
def test_invalid_input(work, capsys, argv, message):
    (work / ".tmp/t1").mkdir()
    code, err = call(capsys, *argv)
    assert code == 2 and message in err


def test_discover(work, capsys):
    call(capsys, "stage", str(inbox(work)), *RUN)
    code, result = call(capsys, "discover", *RUN)
    assert code == 0
    by_path = {f["path"]: f for f in result["files"]}
    pdf = by_path["bank/jan-2026.pdf"]
    assert (pdf["status"], pdf["module"], pdf["rows"], pdf["period"]) == ("module", "n26", 2,
                                                                          "2026-01-01..2026-01-31")
    assert pdf["holder"] != "unknown"
    assert by_path["shared.csv"]["period"] == "2026-01-03..2026-01-10"
    assert by_path["unknown.csv"]["status"] == "mapping"
    assert by_path["unknown.csv"]["header"] == ["When", "What", "How much"]
    assert result["proposed-period"] == "2025-02-01..2026-01-31"
    assert {n["account"] for n in result["not-covered"]} == set(result["accounts"])


def test_discover_conflicts_gaps_statuses(work, capsys):
    src = work / ".tmp/t1/.work/sources"
    src.mkdir(parents=True)
    feb = [[*N26_PAGES[0][:2], (50, 772, "01.03.2026 until 31.03.2026"), *N26_PAGES[0][3:]], N26_PAGES[1]]
    (src / "jan.pdf").write_bytes(make_pdf(N26_PAGES))
    (src / "jan-other.pdf").write_bytes(make_pdf([N26_PAGES[0], N26_PAGES[1][:3]]))
    (src / "mar.pdf").write_bytes(make_pdf(feb))
    (src / "scan.pdf").write_bytes(make_pdf([[]]))
    (src / "text.pdf").write_bytes(make_pdf([[(50, 800, "Unknown bank statement")]]))
    (src / "photo.png").write_bytes(b"x")
    (src / "old.xls").write_bytes(b"x")
    (src / "broken.pdf").write_bytes(b"x")
    (src / "n26bad.pdf").write_bytes(make_pdf([[(50, 800, "NTSBDEB1")]]))
    result = call(capsys, "discover", *RUN)[1]
    status = {f["path"]: f["status"] for f in result["files"]}
    assert status == {"broken.pdf": "error", "jan-other.pdf": "module", "jan.pdf": "module", "mar.pdf": "module",
                      "n26bad.pdf": "error", "old.xls": "llm", "photo.png": "llm-image", "scan.pdf": "no-text",
                      "text.pdf": "llm"}
    assert len(result["conflicts"]) == 1
    assert result["gaps"][0]["missing-months"] == ["2026-02"]
    assert result["proposed-period"] == "2025-04-01..2026-03-31"


def test_propose_period():
    assert normalize.propose_period({}) == "unknown"
    assert normalize.propose_period({"a": [{"period": "2025-01-01..2026-06-15"}]}) == "2025-06-01..2026-05-31"


def test_rename(work, capsys):
    call(capsys, "stage", str(inbox(work)), *RUN)
    code, result = call(capsys, "rename", *RUN, "--to", "jane-t1")
    assert code == 0 and result["folder"] == ".tmp/jane-t1"
    assert (work / ".tmp/jane-t1/.work/sources/shared.csv").is_file() and not (work / ".tmp/t1").exists()
    call(capsys, "run", "shared.csv", "--id", "jane-t1", "--set", f"account-holder={HOLDER}")
    assert "rename before normalizing" in call(capsys, "rename", "--id", "jane-t1", "--to", "t3")[1]


def test_run_module_and_force(work, capsys):
    call(capsys, "stage", str(inbox(work)), *RUN)
    code, result = call(capsys, "run", "bank/jan-2026.pdf", *RUN)
    assert code == 0
    assert result["output"] == ".tmp/t1/.work/normalized/bank-jan-2026-pdf.md"
    assert (result["normalizer"], result["rows"], result["sum"]) == ("module:n26", 2, "+40.00")
    led = ledger.read(work / result["output"])
    assert led.meta["source"] == ".tmp/t1/.work/sources/bank/jan-2026.pdf"
    assert "exists" in call(capsys, "run", "bank/jan-2026.pdf", *RUN)[1]
    code, result = call(capsys, "run", "bank/jan-2026.pdf", *RUN, "--force", "--set", "account-type=savings")
    assert code == 0 and result["meta"]["account-type"] == "savings"


def test_run_splitwise_needs_holder(work, capsys):
    call(capsys, "stage", str(inbox(work)), *RUN)
    assert "set account-holder" in call(capsys, "run", "shared.csv", *RUN)[1]
    code, result = call(capsys, "run", "shared.csv", *RUN, "--set", f"account-holder={HOLDER}")
    assert code == 0 and result["meta"]["period"] == "2026-01-03..2026-01-10"


def test_run_mapping_and_hints(work, capsys):
    call(capsys, "stage", str(inbox(work)), *RUN)
    assert "--mapping" in call(capsys, "run", "unknown.csv", *RUN)[1]
    spec = {"date": {"column": "When"}, "amount": {"column": "How much", "decimal": ","}, "description": ["What"],
            "meta": {"currency": "EUR"}}
    (work / ".tmp/t1/mapping.json").write_text(json.dumps(spec), encoding="utf-8")
    code, result = call(capsys, "run", "unknown.csv", *RUN, "--mapping", ".tmp/t1/mapping.json")
    assert code == 0 and (result["normalizer"], result["sum"]) == ("mapping", "-1.00")
    assert "unknown institution module" in call(capsys, "run", "unknown.csv", *RUN, "--force", "--module", "bad")[1]
    assert "invalid --set" in call(capsys, "run", "unknown.csv", *RUN, "--force", "--set", "colour=red")[1]


def test_run_hints_and_errors(work, capsys):
    src = work / ".tmp/t1/.work/sources"
    src.mkdir(parents=True)
    files = {"p.png": b"x", "o.ods": b"x", "scan.pdf": make_pdf([[]]), "t.pdf": make_pdf([[(50, 800, "Hello")]]),
             "bad.pdf": b"x"}
    for name, data in files.items():
        (src / name).write_bytes(data)
    assert "llm-image" in call(capsys, "run", "p.png", *RUN)[1]
    assert "re-export" in call(capsys, "run", "o.ods", *RUN)[1]
    assert "no text layer" in call(capsys, "run", "scan.pdf", *RUN)[1]
    assert "normalizer: llm)" in call(capsys, "run", "t.pdf", *RUN)[1]
    assert "cannot read PDF" in call(capsys, "run", "bad.pdf", *RUN)[1]


def test_run_encrypted(work, capsys, monkeypatch):
    import sourcedoc

    src = work / ".tmp/t1/.work/sources"
    src.mkdir(parents=True)
    (src / "x.pdf").write_bytes(b"x")
    monkeypatch.setattr(sourcedoc, "load", lambda p: sourcedoc.Doc(p, "pdf", encrypted=True))
    assert "password protected" in call(capsys, "run", "x.pdf", *RUN)[1]


def test_run_unexpected_parser_error(work, capsys, monkeypatch):
    import sourcedoc

    src = work / ".tmp/t1/.work/sources"
    src.mkdir(parents=True)
    (src / "x.pdf").write_bytes(b"x")

    def boom(path):
        raise RuntimeError("bad xref")

    monkeypatch.setattr(sourcedoc, "load", boom)
    assert "RuntimeError: bad xref" in call(capsys, "run", "x.pdf", *RUN)[1]
