# Python 3.11+ pytest suite; run with: make test
import json

from analyse_cvs.adapters.cli import check, rank


def rows(candidate_row):
    return [
        candidate_row("Cy", "3.7", "4.0", "4.0"),
        candidate_row("Bo", "5.0", "5.0", "5.5"),
        candidate_row("Ana", "7.3", "7.0", "7.0"),
    ]


def test_read_only_ranking(report, candidate_row, workdir, capsys):
    path = report(candidates=rows(candidate_row))
    before = (workdir / path).read_text()
    assert rank.main([path]) == 0
    assert capsys.readouterr().out.splitlines() == ["1. Ana 7.3 (invite)", "2. Bo 5.0", "3. Cy 3.7", "Invited: 1 of 3"]
    assert (workdir / path).read_text() == before


def test_json_output(report, candidate_row, capsys):
    path = report(candidates=rows(candidate_row))
    assert rank.main([path, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["invited"] == 1
    assert data["ranking"][0] == {"rank": 1, "name": "Ana", "overall": "7.3", "invited": True}


def test_write_sorts_table_and_adds_interview_list(report, candidate_row, workdir, capsys):
    path = report(candidates=rows(candidate_row))
    assert rank.main([path, "--write"]) == 0
    text = (workdir / path).read_text()
    assert text.index("| Ana |") < text.index("| Bo |") < text.index("| Cy |")
    assert "### 1. Ana (Overall 7.3, Credibility 7.0)" in text
    assert text.endswith("This list is a recommendation; a human decides who to interview.\n")
    assert "- Chart: <fill>" in text
    capsys.readouterr()
    assert check.main([path, "--stage", "interview"]) == 1
    assert "unfilled Chart links" in capsys.readouterr().out

    (workdir / path).write_text(text.replace("<fill>", "[chart](ana/interview-chart.md)"))
    assert check.main([path, "--stage", "interview"]) == 0


def test_write_is_repeatable(report, candidate_row, workdir):
    path = report(candidates=rows(candidate_row))
    assert rank.main([path, "--write"]) == 0
    first = (workdir / path).read_text()
    assert rank.main([path, "--write"]) == 0
    assert (workdir / path).read_text() == first


def test_incomplete_row_blocks_ranking(report, candidate_row, workdir, capsys):
    path = report(candidates=[candidate_row("Ana", "", "", "")])
    before = (workdir / path).read_text()
    assert rank.main([path, "--write"]) == 1
    assert "phases 6-9 not finished" in capsys.readouterr().err
    assert (workdir / path).read_text() == before
