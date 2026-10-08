# Python 3.11+ pytest suite; run with: make test
import json

import pytest

from analyse_cvs.adapters.cli import stage

RUN = ".tmp/analyse-cvs/cvs"


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / ".tmp" / "cvs"
    folder.mkdir(parents=True)
    return folder


def run_json(capsys, *args):
    assert stage.main([*args, "--run", RUN, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def run_files(capsys, *args):
    return run_json(capsys, *args)["files"]


def staging_dir(workdir):
    return workdir.parent / "analyse-cvs" / "cvs" / ".work" / "staging"


@pytest.mark.parametrize("name", ["$(rm -rf ~).pdf", "a'b\".docx", "`id`.txt", "line\nbreak.md"])
def test_unsafe_filename_staged_without_shell(workdir, capsys, name):
    (workdir / name).write_bytes(b"content")
    results = run_files(capsys, ".tmp/cvs")
    assert results[0]["source"] == name
    assert results[0]["status"] == "staged"
    staged = workdir.parent / "analyse-cvs" / "cvs" / results[0]["staged"]
    assert staged.name.startswith("doc-01.")
    assert staged.read_bytes() == b"content"


def test_uppercase_extension_staged_lowercase(workdir, capsys):
    (workdir / "Jane CV.PDF").write_bytes(b"x")
    results = run_files(capsys, ".tmp/cvs")
    assert results == [
        {
            "id": "doc-01",
            "source": "Jane CV.PDF",
            "group": None,
            "staged": ".work/staging/doc-01.pdf",
            "status": "staged",
        }
    ]


def test_unsupported_files_reported(workdir, capsys):
    (workdir / "old.doc").write_bytes(b"x")
    (workdir / "bundle.zip").write_bytes(b"x")
    results = run_files(capsys, ".tmp/cvs")
    assert {r["source"]: r["status"] for r in results} == {"old.doc": "unsupported", "bundle.zip": "unsupported"}
    assert all(r["staged"] is None and r["id"] is None for r in results)


def test_numbering_is_sequential_over_supported_files(workdir, capsys):
    for name in ["a.pdf", "b.doc", "c.docx"]:
        (workdir / name).write_bytes(b"x")
    results = run_files(capsys, ".tmp/cvs")
    assert [r["staged"] for r in results] == [".work/staging/doc-01.pdf", None, ".work/staging/doc-02.docx"]


def test_hidden_files_and_symlinks_skipped_and_md_folder_is_a_group(workdir, capsys, tmp_path):
    (workdir / "md").mkdir()
    (workdir / "md" / "old.md").write_text("x")
    (workdir / ".DS_Store").write_bytes(b"x")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret")
    (workdir / "link.txt").symlink_to(outside)
    (workdir / "cv.pdf").write_bytes(b"x")
    manifest = run_json(capsys, ".tmp/cvs")
    assert [r["source"] for r in manifest["files"]] == ["cv.pdf", "md/old.md"]
    assert manifest["groups"] == [{"id": "g-01", "name": "md"}]


def test_subfolders_become_groups(workdir, capsys):
    roger = workdir / "Roger Mathias - CV 2026 (1)"
    (roger / "extra").mkdir(parents=True)
    (roger / "cv.pdf").write_bytes(b"x")
    (roger / "extra" / "letter.docx").write_bytes(b"x")
    (roger / "photo.jpg").write_bytes(b"x")
    (workdir / "anna.pdf").write_bytes(b"x")
    manifest = run_json(capsys, ".tmp/cvs")
    assert manifest["groups"] == [{"id": "g-01", "name": "Roger Mathias - CV 2026 (1)"}]
    assert [(f["source"], f["group"], f["id"]) for f in manifest["files"]] == [
        ("Roger Mathias - CV 2026 (1)/cv.pdf", "g-01", "doc-01"),
        ("Roger Mathias - CV 2026 (1)/extra/letter.docx", "g-01", "doc-02"),
        ("Roger Mathias - CV 2026 (1)/photo.jpg", "g-01", None),
        ("anna.pdf", None, "doc-03"),
    ]


def test_unsafe_folder_name_staged(workdir, capsys):
    unsafe = workdir / "$(touch pwned) `id`"
    unsafe.mkdir()
    (unsafe / "cv.pdf").write_bytes(b"x")
    manifest = run_json(capsys, ".tmp/cvs")
    assert manifest["groups"][0]["name"] == "$(touch pwned) `id`"
    assert manifest["files"][0]["staged"] == ".work/staging/doc-01.pdf"


def test_hidden_and_symlinked_folders_skipped(workdir, capsys, tmp_path):
    (workdir / ".git").mkdir()
    (workdir / ".git" / "x.txt").write_text("x")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.pdf").write_bytes(b"x")
    (workdir / "linked").symlink_to(outside)
    real = workdir / "real"
    (real / ".hidden").mkdir(parents=True)
    (real / ".hidden" / "a.pdf").write_bytes(b"x")
    (real / "inner-link").symlink_to(outside)
    (real / "cv.pdf").write_bytes(b"x")
    manifest = run_json(capsys, ".tmp/cvs")
    assert [g["name"] for g in manifest["groups"]] == ["real"]
    assert [f["source"] for f in manifest["files"]] == ["real/cv.pdf"]


def test_manifest_written_with_source_root(workdir, capsys):
    (workdir / "cv.pdf").write_bytes(b"x")
    manifest = run_json(capsys, ".tmp/cvs")
    written = json.loads((staging_dir(workdir) / "manifest.json").read_text())
    assert written == manifest
    assert manifest["source_root"] == workdir.resolve().as_posix()


def test_source_folder_is_left_untouched(workdir, capsys):
    (workdir / "cv.pdf").write_bytes(b"x")
    (workdir / "roger").mkdir()
    (workdir / "roger" / "cv.docx").write_bytes(b"y")
    before = sorted(p.relative_to(workdir).as_posix() for p in workdir.rglob("*"))
    run_json(capsys, ".tmp/cvs")
    assert sorted(p.relative_to(workdir).as_posix() for p in workdir.rglob("*")) == before


def test_staging_is_recreated_but_other_work_is_kept(workdir, capsys):
    staging = staging_dir(workdir)
    staging.mkdir(parents=True)
    (staging / "doc-09.pdf").write_bytes(b"stale")
    kept = staging.parent / "md"
    kept.mkdir()
    (kept / "anna-cv.md").write_text("keep")
    (workdir / "cv.pdf").write_bytes(b"x")
    run_json(capsys, ".tmp/cvs")
    assert sorted(p.name for p in staging.iterdir()) == ["doc-01.pdf", "manifest.json"]
    assert (kept / "anna-cv.md").read_text() == "keep"


@pytest.mark.parametrize("folder", ["elsewhere", ".tmp", ".tmp/../elsewhere", "/etc"])
def test_source_outside_tmp_rejected(workdir, capsys, tmp_path, folder):
    (tmp_path / "elsewhere").mkdir()
    assert stage.main([folder, "--run", RUN]) == 1
    assert "must be inside" in capsys.readouterr().err


def test_missing_source_rejected(workdir, capsys):
    assert stage.main([".tmp/missing", "--run", RUN]) == 1
    assert "does not exist" in capsys.readouterr().err


@pytest.mark.parametrize("run", ["elsewhere", ".tmp", ".tmp/../elsewhere"])
def test_run_outside_tmp_rejected(workdir, capsys, run):
    assert stage.main([".tmp/cvs", "--run", run]) == 1
    assert "run folder must be inside" in capsys.readouterr().err


@pytest.mark.parametrize("run", [".tmp/cvs", ".tmp/cvs/run", ".tmp/cvs/../cvs"])
def test_run_equal_or_nested_with_source_rejected(workdir, capsys, run):
    (workdir / "cv.pdf").write_bytes(b"x")
    assert stage.main([".tmp/cvs", "--run", run]) == 1
    assert "separate, not nested" in capsys.readouterr().err
    assert not (workdir / ".work").exists()


def test_source_nested_in_run_rejected(workdir, capsys, tmp_path):
    inner = tmp_path / ".tmp" / "run" / "source"
    inner.mkdir(parents=True)
    assert stage.main([".tmp/run/source", "--run", ".tmp/run"]) == 1
    assert "separate, not nested" in capsys.readouterr().err


def test_human_readable_output(workdir, capsys):
    (workdir / "cv.pdf").write_bytes(b"x")
    (workdir / "old.doc").write_bytes(b"x")
    assert stage.main([".tmp/cvs", "--run", RUN]) == 0
    out = capsys.readouterr().out
    assert "doc-01.pdf" in out
    assert "1 staged, 1 unsupported, 0 group(s)" in out
