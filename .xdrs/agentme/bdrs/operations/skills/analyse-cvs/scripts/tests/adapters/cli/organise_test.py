# Python 3.11+ pytest suite; run with: make test
import json

import pytest

from analyse_cvs.adapters.cli import organise, stage

RUN = ".tmp/analyse-cvs/cvs"


@pytest.fixture
def source(workdir):
    folder = workdir / ".tmp" / "cvs"
    folder.mkdir(parents=True)
    return folder


def make(source, files):
    for rel, content in files.items():
        (source / rel).parent.mkdir(parents=True, exist_ok=True)
        (source / rel).write_bytes(content)


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def stage_all(capsys):
    assert stage.main([".tmp/cvs", "--run", RUN, "--json"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    return {f["source"]: f["id"] for f in manifest["files"]}


def plan_file(workdir, plan):
    path = workdir / "plan.json"
    path.write_text(json.dumps(plan))
    return str(path)


def run_json(capsys, workdir, plan):
    assert organise.main([RUN, plan_file(workdir, plan), "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def sources_dir(workdir):
    return workdir / ".tmp" / "analyse-cvs" / "cvs" / ".work" / "sources"


def test_group_documents_are_copied_keeping_subpaths(source, workdir, capsys):
    make(source, {"Roger M/cv.pdf": b"a", "Roger M/extra/letter.docx": b"b", "Roger M/photo.jpg": b"c"})
    stage_all(capsys)
    before = snapshot(source)
    result = run_json(capsys, workdir, {"folders": {"g-01": "roger-mathias"}})
    base = sources_dir(workdir) / "roger-mathias"
    assert snapshot(base) == {"cv.pdf": b"a", "extra/letter.docx": b"b", "photo.jpg": b"c"}
    assert result["slugs"] == ["roger-mathias"]
    assert result["organised"]["doc-01"] == ".work/sources/roger-mathias/cv.pdf"
    assert snapshot(source) == before


def test_files_entry_overrides_group_and_uses_the_file_name(source, workdir, capsys):
    make(source, {"Mixed/anna.pdf": b"a", "Mixed/roger/cv.pdf": b"b"})
    ids = stage_all(capsys)
    run_json(capsys, workdir, {"folders": {"g-01": "roger-mathias"}, "files": {ids["Mixed/anna.pdf"]: "anna-silva"}})
    assert snapshot(sources_dir(workdir)) == {"anna-silva/anna.pdf": b"a", "roger-mathias/roger/cv.pdf": b"b"}


def test_top_level_file_is_organised_with_a_files_entry(source, workdir, capsys):
    make(source, {"anna.txt": b"a"})
    ids = stage_all(capsys)
    result = run_json(capsys, workdir, {"files": {ids["anna.txt"]: "anna-silva"}})
    assert (sources_dir(workdir) / "anna-silva" / "anna.txt").read_bytes() == b"a"
    assert result["unassigned"] == []


def test_two_groups_merged_into_one_slug_suffix_clashes(source, workdir, capsys):
    make(source, {"Roger 1/cv.pdf": b"one", "Roger 2/cv.pdf": b"two", "Roger 2/letter.pdf": b"L"})
    stage_all(capsys)
    run_json(capsys, workdir, {"folders": {"g-01": "roger", "g-02": "roger"}})
    assert snapshot(sources_dir(workdir) / "roger") == {"cv.pdf": b"one", "cv-2.pdf": b"two", "letter.pdf": b"L"}


def test_rerun_reuses_identical_copies(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"one"})
    stage_all(capsys)
    plan = {"folders": {"g-01": "roger"}}
    run_json(capsys, workdir, plan)
    result = run_json(capsys, workdir, plan)
    assert snapshot(sources_dir(workdir) / "roger") == {"cv.pdf": b"one"}
    assert result["organised"]["doc-01"] == ".work/sources/roger/cv.pdf"


def test_changed_source_on_rerun_gets_a_new_name(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"one"})
    stage_all(capsys)
    plan = {"folders": {"g-01": "roger"}}
    run_json(capsys, workdir, plan)
    (source / "Roger" / "cv.pdf").write_bytes(b"newer")
    run_json(capsys, workdir, plan)
    assert snapshot(sources_dir(workdir) / "roger") == {"cv.pdf": b"one", "cv-2.pdf": b"newer"}


def test_manifest_records_organised_paths(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"a", "Roger/old.doc": b"b"})
    stage_all(capsys)
    run_json(capsys, workdir, {"folders": {"g-01": "roger"}})
    manifest = json.loads((workdir / ".tmp" / "analyse-cvs" / "cvs" / ".work" / "staging" / "manifest.json").read_text())
    assert [(f["source"], f["organised"]) for f in manifest["files"]] == [
        ("Roger/cv.pdf", ".work/sources/roger/cv.pdf"),
        ("Roger/old.doc", ".work/sources/roger/old.doc"),
    ]


def test_unplanned_documents_are_reported_as_unassigned(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"a", "stray.pdf": b"b"})
    stage_all(capsys)
    result = run_json(capsys, workdir, {"folders": {"g-01": "roger"}})
    assert result["unassigned"] == ["doc-02"]
    assert list(snapshot(sources_dir(workdir))) == ["roger/cv.pdf"]


@pytest.mark.parametrize("name", ["$(rm -rf ~).pdf", "a'b\".docx", "`id`.txt"])
def test_unsafe_filenames_are_copied_without_a_shell(source, workdir, capsys, name):
    make(source, {f"Roger/{name}": b"content"})
    stage_all(capsys)
    run_json(capsys, workdir, {"folders": {"g-01": "roger"}})
    assert snapshot(sources_dir(workdir) / "roger") == {name: b"content"}


@pytest.mark.parametrize(
    ("plan", "message"),
    [
        ({"rename": {}}, "unknown plan keys"),
        ({"folders": {"g-09": "x"}}, "unknown folders id"),
        ({"files": {"doc-09": "x"}}, "unknown files id"),
        ({"folders": {"g-01": "../escape"}}, "invalid candidate slug"),
        ({"folders": {"g-01": "Roger M"}}, "invalid candidate slug"),
        ({"folders": {"g-01": 7}}, "invalid candidate slug"),
    ],
)
def test_invalid_plans_change_nothing(source, workdir, capsys, plan, message):
    make(source, {"Roger/cv.pdf": b"a"})
    stage_all(capsys)
    assert organise.main([RUN, plan_file(workdir, plan)]) == 1
    assert message in capsys.readouterr().err
    assert not sources_dir(workdir).exists()


def test_target_that_is_a_file_is_rejected(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"a"})
    stage_all(capsys)
    sources_dir(workdir).mkdir(parents=True)
    (sources_dir(workdir) / "roger").write_text("file")
    assert organise.main([RUN, plan_file(workdir, {"folders": {"g-01": "roger"}})]) == 1
    assert "not a folder" in capsys.readouterr().err


def test_missing_source_file_changes_nothing(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"a", "Roger/letter.pdf": b"b"})
    stage_all(capsys)
    (source / "Roger" / "letter.pdf").unlink()
    assert organise.main([RUN, plan_file(workdir, {"folders": {"g-01": "roger"}})]) == 1
    assert "source file missing" in capsys.readouterr().err
    assert not sources_dir(workdir).exists()


def test_manifest_is_required(source, workdir, capsys):
    (workdir / ".tmp" / "analyse-cvs" / "cvs").mkdir(parents=True)
    assert organise.main([RUN, plan_file(workdir, {})]) == 1
    assert "run cvs-stage first" in capsys.readouterr().err


@pytest.mark.parametrize("run", ["elsewhere", ".tmp", ".tmp/missing"])
def test_run_must_be_an_existing_folder_inside_tmp(workdir, capsys, run):
    assert organise.main([run, plan_file(workdir, {})]) == 1
    assert "run folder" in capsys.readouterr().err


def test_manifest_source_root_outside_tmp_is_rejected(source, workdir, capsys, tmp_path):
    make(source, {"Roger/cv.pdf": b"a"})
    stage_all(capsys)
    manifest_path = workdir / ".tmp" / "analyse-cvs" / "cvs" / ".work" / "staging" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["source_root"] = str(tmp_path)
    manifest_path.write_text(json.dumps(manifest))
    assert organise.main([RUN, plan_file(workdir, {"folders": {"g-01": "roger"}})]) == 1
    assert "must be inside" in capsys.readouterr().err


def test_text_output(source, workdir, capsys):
    make(source, {"Roger/cv.pdf": b"a", "stray.pdf": b"b"})
    stage_all(capsys)
    assert organise.main([RUN, plan_file(workdir, {"folders": {"g-01": "roger"}})]) == 0
    out = capsys.readouterr().out
    assert "'doc-01' -> .work/sources/roger/cv.pdf" in out
    assert "unassigned doc-02" in out
    assert "1 file(s) copied for 1 candidate folder(s)" in out
