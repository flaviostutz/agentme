# Python 3.11+ pytest suite; run with: make test
import json

import pytest

from analyse_cvs.adapters.cli import score


def test_overall_text_and_json(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "5.0", "5.6")])
    assert score.main(["overall", path, "ana"]) == 0
    assert capsys.readouterr().out.strip() == "Overall 5.0 (unrounded 5.0222, invited: True)"
    assert score.main(["overall", path, "Ana", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"overall": "5.0", "unrounded": "5.0222", "invited": True}


def test_dryrun_text_and_json(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "7.0", "7.0", scenario="")])
    adjustments = '{"S2": {"Collaboration": "-0.5"}}'
    assert score.main(["dryrun", path, "Ana", "--adjustments", adjustments]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "Base 6.8 (shift -0.2)",
        "Delivery: 7.0",
        "Collaboration: 6.5",
        "Domain: 7.0",
    ]
    assert score.main(["dryrun", path, "Ana", "--adjustments", adjustments, "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["base"] == "6.8"


def test_candidate_can_be_selected_by_slug(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("José Álvarez", "", "7.0", "7.0"), candidate_row("???", "", "7.0", "7.0")])
    assert score.main(["overall", path, "jose-alvarez"]) == 0
    assert capsys.readouterr().out.startswith("Overall 7.3")


def test_dryrun_is_refused_when_already_applied(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "7.0", "7.0")])
    assert score.main(["dryrun", path, "Ana"]) == 1
    assert "already has Scenario notes" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["overall", ".tmp/missing.md", "Ana"], "report does not exist"),
        (["overall", "outside.md", "Ana"], "inside"),
        (["overall", "x", "Ana"], "inside"),
    ],
)
def test_report_path_errors(workdir, capsys, args, message):
    (workdir / "outside.md").write_text("x")
    assert score.main(args) == 1
    assert message in capsys.readouterr().err


def test_unknown_candidate_and_empty_scores(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "", "")])
    assert score.main(["overall", path, "Zed"]) == 1
    assert "exactly one candidate" in capsys.readouterr().err
    assert score.main(["overall", path, "Ana"]) == 1
    assert "not a decimal number" in capsys.readouterr().err


def test_bad_adjustments(report, candidate_row, capsys):
    path = report(candidates=[candidate_row("Ana", "", "7.0", "7.0", scenario="")])
    assert score.main(["dryrun", path, "Ana", "--adjustments", '{"S1": {"Domain": "2.0"}}']) == 1
    assert "within" in capsys.readouterr().err
