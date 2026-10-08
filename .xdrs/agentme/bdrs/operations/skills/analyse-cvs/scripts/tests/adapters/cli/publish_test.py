# Python 3.11+ pytest suite; run with: make test
import json

import pytest

from analyse_cvs.adapters.cli import organise, publish, stage

RUN = ".tmp/analyse-cvs/cvs"


@pytest.fixture
def organised(workdir, capsys):
    source = workdir / ".tmp" / "cvs"
    files = {
        "Roger/cv.pdf": b"cv",
        "Roger/extra/letter.docx": b"letter",
        "Roger/interview-chart.md": b"hostile original",
        "Anna/cv.pdf": b"anna",
    }
    for rel, content in files.items():
        (source / rel).parent.mkdir(parents=True, exist_ok=True)
        (source / rel).write_bytes(content)
    assert stage.main([".tmp/cvs", "--run", RUN]) == 0
    plan = workdir / "plan.json"
    plan.write_text(json.dumps({"folders": {"g-01": "anna-silva", "g-02": "roger-mathias"}}))
    assert organise.main([RUN, str(plan)]) == 0
    capsys.readouterr()
    return workdir / ".tmp" / "analyse-cvs" / "cvs"


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def run_json(capsys, *slugs):
    assert publish.main([RUN, *slugs, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def test_originals_are_copied_to_the_candidate_folder(organised, capsys):
    result = run_json(capsys, "roger-mathias")
    assert result["roger-mathias"]["existing"] == []
    assert snapshot(organised / "roger-mathias") == {
        "cv.pdf": b"cv",
        "extra/letter.docx": b"letter",
        "original-interview-chart.md": b"hostile original",
    }
    assert not (organised / "anna-silva").exists()
    assert (organised / ".work" / "sources" / "roger-mathias" / "cv.pdf").is_file()


def test_several_slugs_in_one_call(organised, capsys):
    result = run_json(capsys, "anna-silva", "roger-mathias")
    assert sorted(result) == ["anna-silva", "roger-mathias"]
    assert (organised / "anna-silva" / "cv.pdf").read_bytes() == b"anna"


def test_rerun_never_overwrites_files_or_charts(organised, capsys):
    run_json(capsys, "anna-silva")
    chart = organised / "anna-silva" / "interview-chart.md"
    chart.write_text("my chart")
    (organised / "anna-silva" / "cv.pdf").write_bytes(b"edited by hand")
    result = run_json(capsys, "anna-silva")
    assert result["anna-silva"] == {"copied": [], "existing": ["anna-silva/cv.pdf"]}
    assert chart.read_text() == "my chart"
    assert (organised / "anna-silva" / "cv.pdf").read_bytes() == b"edited by hand"


def test_new_document_is_added_on_rerun(organised, capsys):
    run_json(capsys, "anna-silva")
    (organised / ".work" / "sources" / "anna-silva" / "cover.pdf").write_bytes(b"new")
    result = run_json(capsys, "anna-silva")
    assert result["anna-silva"] == {"copied": ["anna-silva/cover.pdf"], "existing": ["anna-silva/cv.pdf"]}


@pytest.mark.parametrize("slug", ["../escape", "Roger", "a/b", "x-", ".work"])
def test_invalid_slug_is_rejected_before_anything_is_copied(organised, capsys, slug):
    assert publish.main([RUN, "anna-silva", slug]) == 1
    assert "invalid candidate slug" in capsys.readouterr().err
    assert not (organised / "anna-silva").exists()


def test_unknown_slug_is_rejected(organised, capsys):
    assert publish.main([RUN, "nobody"]) == 1
    assert "run cvs-organise first" in capsys.readouterr().err


def test_run_must_exist_inside_tmp(workdir, capsys):
    assert publish.main([".tmp/missing", "anna"]) == 1
    assert "run folder does not exist" in capsys.readouterr().err


def test_text_output(organised, capsys):
    assert publish.main([RUN, "anna-silva"]) == 0
    assert "anna-silva: 1 copied, 0 already there" in capsys.readouterr().out
