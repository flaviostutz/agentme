# Python 3.9+ pytest suite; run with: uv run --no-project --with pytest pytest scripts
import json

import organise
import pytest
import stage


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / ".tmp" / "cvs"
    folder.mkdir(parents=True)
    return folder


def write(path, content=b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def run(workdir, capsys, plan):
    assert stage.main([".tmp/cvs", "--json"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    plan_file = workdir / "md" / ".staging" / "plan.json"
    plan_file.write_text(json.dumps(plan))
    code = organise.main([".tmp/cvs", str(plan_file), "--json"])
    captured = capsys.readouterr()
    return code, manifest, (json.loads(captured.out) if code == 0 else captured.err)


def tree(folder):
    rels = (p.relative_to(folder) for p in folder.rglob("*"))
    return sorted(r.as_posix() for r in rels if r.parts[0] != "md")


def test_group_folder_renamed(workdir, capsys):
    write(workdir / "Roger Mathias - CV 2026 (1)" / "cv.pdf")
    write(workdir / "Roger Mathias - CV 2026 (1)" / "letter.docx")
    code, _, result = run(workdir, capsys, {"folders": {"g-01": "roger-mathias"}})
    assert code == 0
    assert tree(workdir) == ["roger-mathias", "roger-mathias/cv.pdf", "roger-mathias/letter.docx"]
    assert result["renamed"] == [
        {"group": "g-01", "from": "Roger Mathias - CV 2026 (1)", "to": "roger-mathias", "merged": False}
    ]
    assert result["sources"] == {"doc-01": "roger-mathias/cv.pdf", "doc-02": "roger-mathias/letter.docx"}


def test_case_only_rename(workdir, capsys):
    write(workdir / "Roger" / "cv.pdf")
    code, _, _ = run(workdir, capsys, {"folders": {"g-01": "roger"}})
    assert code == 0
    assert [p.name for p in workdir.iterdir() if p.name != "md"] == ["roger"]


def test_merge_into_existing_folder_with_clash_suffix(workdir, capsys):
    write(workdir / "roger-mathias" / "cv.pdf", b"old")
    write(workdir / "Roger M" / "cv.pdf", b"new")
    write(workdir / "Roger M" / "sub" / "cert.txt")
    code, _, result = run(workdir, capsys, {"folders": {"g-01": "roger-mathias"}})
    assert code == 0
    assert tree(workdir) == [
        "roger-mathias", "roger-mathias/cv-2.pdf", "roger-mathias/cv.pdf",
        "roger-mathias/sub", "roger-mathias/sub/cert.txt",
    ]
    assert (workdir / "roger-mathias" / "cv-2.pdf").read_bytes() == b"new"
    assert result["renamed"][0]["merged"] is True
    assert "Roger M" in result["removed"]


def test_loose_file_moved_into_candidate_folder(workdir, capsys):
    write(workdir / "anna silva cv.pdf")
    code, _, result = run(workdir, capsys, {"files": {"doc-01": "anna-silva"}})
    assert code == 0
    assert tree(workdir) == ["anna-silva", "anna-silva/anna silva cv.pdf"]
    assert result["sources"] == {"doc-01": "anna-silva/anna silva cv.pdf"}


def test_container_emptied_and_removed(workdir, capsys):
    write(workdir / "batch" / "a.pdf")
    write(workdir / "batch" / "nested" / "b.pdf")
    write(workdir / "batch" / ".DS_Store")
    code, _, result = run(workdir, capsys, {"files": {"doc-01": "anna-silva", "doc-02": "bob-jones"}})
    assert code == 0
    assert tree(workdir) == ["anna-silva", "anna-silva/a.pdf", "bob-jones", "bob-jones/b.pdf"]
    assert result["removed"] == ["batch", "batch/nested"]


def test_container_with_unsupported_leftover_kept(workdir, capsys):
    write(workdir / "batch" / "a.pdf")
    write(workdir / "batch" / "photo.jpg")
    code, _, result = run(workdir, capsys, {"files": {"doc-01": "anna-silva"}})
    assert code == 0
    assert tree(workdir) == ["anna-silva", "anna-silva/a.pdf", "batch", "batch/photo.jpg"]
    assert result["removed"] == []


def test_group_rename_then_file_moved_out(workdir, capsys):
    write(workdir / "Roger stuff" / "cv.pdf")
    write(workdir / "Roger stuff" / "other-person.pdf")
    plan = {"folders": {"g-01": "roger-mathias"}, "files": {"doc-02": "anna-silva"}}
    code, _, result = run(workdir, capsys, plan)
    assert code == 0
    assert result["sources"] == {"doc-01": "roger-mathias/cv.pdf", "doc-02": "anna-silva/other-person.pdf"}


@pytest.mark.parametrize("slug", ["../x", "Roger", "md", "a b", "", "a--b", 3])
def test_invalid_slug_rejected_without_changes(workdir, capsys, slug):
    write(workdir / "Roger" / "cv.pdf")
    code, _, err = run(workdir, capsys, {"folders": {"g-01": slug}})
    assert code == 1
    assert "invalid candidate slug" in err
    assert tree(workdir) == ["Roger", "Roger/cv.pdf"]


@pytest.mark.parametrize("plan", [{"folders": {"g-09": "x"}}, {"files": {"doc-09": "x"}}, {"other": {}}])
def test_unknown_ids_rejected(workdir, capsys, plan):
    write(workdir / "Roger" / "cv.pdf")
    code, _, err = run(workdir, capsys, plan)
    assert code == 1
    assert "unknown" in err


def test_target_is_a_file_rejected(workdir, capsys):
    write(workdir / "roger")
    write(workdir / "Roger CV" / "cv.pdf")
    code, _, err = run(workdir, capsys, {"folders": {"g-01": "roger"}})
    assert code == 1
    assert "not a folder" in err


def test_folder_outside_tmp_rejected(workdir, capsys, tmp_path):
    (tmp_path / "plan.json").write_text("{}")
    assert organise.main(["elsewhere", str(tmp_path / "plan.json")]) == 1
    assert "must be inside" in capsys.readouterr().err


def test_missing_manifest_rejected(workdir, capsys, tmp_path):
    (tmp_path / "plan.json").write_text("{}")
    assert organise.main([".tmp/cvs", str(tmp_path / "plan.json")]) == 1
    assert "run stage.py first" in capsys.readouterr().err


def test_rerun_is_noop(workdir, capsys):
    write(workdir / "Roger M" / "cv.pdf")
    write(workdir / "anna.pdf")
    plan = {"folders": {"g-01": "roger-mathias"}, "files": {"doc-02": "anna-silva"}}
    code, _, _ = run(workdir, capsys, plan)
    assert code == 0
    before = tree(workdir)
    plan_file = workdir / "md" / ".staging" / "plan.json"
    assert organise.main([".tmp/cvs", str(plan_file), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["renamed"] == [] and result["removed"] == []
    assert tree(workdir) == before


def test_human_readable_output(workdir, capsys):
    write(workdir / "Roger M" / "cv.pdf")
    assert stage.main([".tmp/cvs"]) == 0
    plan_file = workdir / "md" / ".staging" / "plan.json"
    plan_file.write_text(json.dumps({"folders": {"g-01": "roger-mathias"}}))
    capsys.readouterr()
    assert organise.main([".tmp/cvs", str(plan_file)]) == 0
    out = capsys.readouterr().out
    assert "renamed 'Roger M' -> roger-mathias" in out
