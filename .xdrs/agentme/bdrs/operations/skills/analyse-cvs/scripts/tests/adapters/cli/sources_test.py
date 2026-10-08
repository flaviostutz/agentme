# Python 3.11+ pytest suite; run with: make test
import json

import pytest

from analyse_cvs.adapters.cli import sources, stage

RUN = ".tmp/analyse-cvs/sample"


@pytest.fixture
def staged(workdir, capsys):
    source = workdir / ".tmp" / "cvs"
    for rel in ("roger/cv.pdf", "roger/letter.pdf", "anna.txt", "notes.xlsx"):
        (source / rel).parent.mkdir(parents=True, exist_ok=True)
        (source / rel).write_bytes(b"x")
    assert stage.main([".tmp/cvs", "--run", RUN, "--json"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    run = workdir / RUN
    ids = {f["source"]: f["id"] for f in manifest["files"]}
    for doc_id in filter(None, ids.values()):
        (run / ".work" / "staging" / f"{doc_id}-converted.md").write_text(f"text {doc_id}")
    return run, ids


def decisions(workdir, ids, **overrides):
    docs = {
        ids["roger/cv.pdf"]: {"candidate": "Roger Mathias", "slug": "roger-mathias", "type": "cv"},
        ids["roger/letter.pdf"]: {"candidate": "roger mathias", "slug": "roger-mathias", "type": "cover-letter"},
        ids["anna.txt"]: {"candidate": "Anna Silva", "slug": "anna-silva", "type": "cv"},
    }
    docs.update(overrides)
    path = workdir / "docs.json"
    path.write_text(json.dumps(docs))
    return str(path)


def test_registers_documents_sources_and_candidates(staged, report, workdir, capsys):
    run, ids = staged
    path = report()
    assert sources.main([RUN, path, decisions(workdir, ids), "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert sorted(summary["renamed"].values()) == [
        ".work/md/anna-silva-cv.md",
        ".work/md/roger-mathias-cover-letter.md",
        ".work/md/roger-mathias-cv.md",
    ]
    assert summary["sources_added"] == 4
    assert sorted(summary["candidates_added"]) == ["Anna Silva", "Roger Mathias"]
    assert (run / ".work" / "md" / "roger-mathias-cv.md").read_text().startswith("text doc-")
    assert not (run / ".work" / "staging").exists()
    text = (workdir / path).read_text()
    assert "| notes.xlsx |  | skipped: unsupported format |" in text
    assert "| roger/cv.pdf | .work/md/roger-mathias-cv.md | converted |" in text
    assert text.count("| Roger Mathias |") == 1


def test_text_output(staged, report, workdir, capsys):
    _, ids = staged
    assert sources.main([RUN, report(), decisions(workdir, ids)]) == 0
    out = capsys.readouterr().out
    assert "4 source row(s), 2 new candidate(s)" in out


def test_repeated_type_gets_suffix(staged, report, workdir):
    run, ids = staged
    docs = decisions(
        workdir,
        ids,
        **{ids["roger/letter.pdf"]: {"candidate": "Roger Mathias", "slug": "roger-mathias", "type": "cv"}},
    )
    assert sources.main([RUN, report(), docs]) == 0
    assert (run / ".work" / "md" / "roger-mathias-cv-2.md").is_file()


def test_skipped_document_is_recorded(staged, report, workdir):
    _, ids = staged
    path = report()
    docs = decisions(workdir, ids, **{ids["anna.txt"]: {"skip": "unreadable | scanned"}})
    assert sources.main([RUN, path, docs]) == 0
    text = (workdir / path).read_text()
    assert "| anna.txt |  | skipped: unreadable \\| scanned |" in text
    assert "Anna Silva" not in text


def test_resume_skips_known_sources_by_raw_path(staged, report, workdir, candidate_row, capsys):
    _, ids = staged
    path = report(
        sources=[
            "| roger/cv.pdf | .work/md/roger-mathias-cv.md | converted |",
            "| roger/letter.pdf | .work/md/x.md | converted |",
        ],
        candidates=[candidate_row("Roger Mathias", "", "", "")],
    )
    docs = workdir / "docs.json"
    docs.write_text(json.dumps({ids["anna.txt"]: {"candidate": "Anna Silva", "slug": "anna-silva", "type": "cv"}}))
    assert sources.main([RUN, path, str(docs), "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["candidates_added"] == ["Anna Silva"]
    assert summary["sources_added"] == 2


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"doc-99": {"skip": "x"}}, "unknown staged document id"),
        ({"doc-03": {"candidate": "A", "slug": "Bad Slug", "type": "cv"}}, "kebab-case"),
        ({"doc-03": {"candidate": "A", "slug": "a", "type": "resume"}}, "needs candidate"),
        ({"doc-03": {"candidate": "Someone Else", "slug": "roger-mathias", "type": "cv"}}, "used for two names"),
    ],
)
def test_invalid_decisions_change_nothing(staged, report, workdir, capsys, override, message):
    run, ids = staged
    path = report()
    before = (workdir / path).read_text()
    docs = decisions(workdir, ids, **override)
    assert sources.main([RUN, path, docs]) == 1
    assert message in capsys.readouterr().err
    assert (workdir / path).read_text() == before
    assert (run / ".work" / "staging").is_dir()
    assert not (run / ".work" / "md").exists()


def test_missing_decision_and_missing_converted_file(staged, report, workdir, capsys):
    run, ids = staged
    docs = workdir / "docs.json"
    docs.write_text(json.dumps({ids["anna.txt"]: {"candidate": "Anna Silva", "slug": "anna-silva", "type": "cv"}}))
    assert sources.main([RUN, report(), str(docs)]) == 1
    assert "no decision for staged documents" in capsys.readouterr().err
    (run / ".work" / "staging" / f"{ids['anna.txt']}-converted.md").unlink()
    assert sources.main([RUN, report(), str(docs)]) == 1
    assert "converted file" in capsys.readouterr().err


def test_docs_file_shape_is_validated(staged, report, workdir, capsys):
    docs = workdir / "docs.json"
    docs.write_text("[]")
    assert sources.main([RUN, report(), str(docs)]) == 1
    assert "must map document ids" in capsys.readouterr().err


def test_source_folder_is_never_touched(staged, report, workdir):
    _, ids = staged
    source = workdir / ".tmp" / "cvs"
    before = sorted(p.relative_to(source).as_posix() for p in source.rglob("*"))
    assert sources.main([RUN, report(), decisions(workdir, ids)]) == 0
    assert sorted(p.relative_to(source).as_posix() for p in source.rglob("*")) == before


def test_run_must_exist_inside_tmp(report, workdir, capsys):
    path = report()
    docs = workdir / "docs.json"
    docs.write_text("{}")
    assert sources.main([".tmp/missing", path, str(docs)]) == 1
    assert "run folder does not exist" in capsys.readouterr().err
