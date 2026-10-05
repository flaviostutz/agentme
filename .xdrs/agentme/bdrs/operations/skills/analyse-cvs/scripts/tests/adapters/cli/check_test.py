# Python 3.11+ pytest suite; run with: make test
import json

from analyse_cvs.adapters.cli import check


def test_criteria_stage_passes(report, capsys):
    assert check.main([report(), "--stage", "criteria"]) == 0
    assert capsys.readouterr().out.strip() == "0 error(s), 0 warning(s)"


def test_scores_stage_prints_errors_and_exits_1(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "7", "7.0")])
    assert check.main([path, "--stage", "scores"]) == 1
    out = capsys.readouterr().out
    assert "error: Ana: Base '7' must be 1.0-10.0 with one decimal" in out
    assert "1 error(s)" in out


def test_warnings_do_not_fail(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "2.0", "7.0")])
    assert check.main([path, "--stage", "scores", "--name", "Ana"]) == 0
    assert "warning: Ana: Base 2.0 differs" in capsys.readouterr().out


def test_scenarios_stage_json(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "7.0", "7.0", scenario="S1 =: x")])
    assert check.main([path, "--stage", "scenarios", "--json"]) == 1
    findings = json.loads(capsys.readouterr().out)
    assert findings["errors"] == ["Ana: missing scenario lines: S2, S3"]
    assert findings["checked"] == 1


def test_interview_stage(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "7.3", "7.0", "7.0")])
    assert check.main([path, "--stage", "interview"]) == 1
    assert "not found" in capsys.readouterr().out


def test_missing_report(workdir, capsys):
    assert check.main([".tmp/none.md", "--stage", "criteria"]) == 1
    assert "report does not exist" in capsys.readouterr().err
