# Python 3.11+ pytest suite; run with: make test
from decimal import Decimal

import pytest

from analyse_cvs.app.checking import (
    check_criteria,
    check_interview_findings,
    check_rows,
    check_scenarios,
    check_scores,
    parse_scenario_notes,
)
from analyse_cvs.app.report_tables import Criterion, aspect_weights, candidates_table, parse_criteria

D = Decimal
ASPECTS = ["Delivery", "Collaboration", "Domain"]
WEIGHTS = {"Delivery": D(30), "Collaboration": D(40), "Domain": D(30)}
GOOD = {
    "Name": "Ana",
    "Overall": "",
    "Base": "7.0",
    "Credibility": "7.0",
    "Rationale": "fine",
    "Delivery": "7.0",
    "Collaboration": "7.0",
    "Domain": "7.0",
    "Scenario notes": "S1 =: ok (cv)<br>S2 =: ok (cv)<br>S3 =: ok (cv)",
    "Notes": "+ strong (cv p1)<br>? odd dates (cv p2)<br>! revised: counterfactual",
}


def crit(*weights_by_aspect):
    return [Criterion(f"c{i}", aspect, D(weight)) for i, (aspect, weight) in enumerate(weights_by_aspect)]


def test_good_criteria_pass(make_report):
    assert check_criteria(parse_criteria(make_report().split("\n"))) == {"errors": [], "warnings": []}


def test_criteria_errors():
    errors = check_criteria(crit(("A", 30), ("B", 30), ("C", "40.5")))["errors"]
    joined = "\n".join(errors)
    assert "expected 6-12 criteria, found 3" in joined
    assert "weight 40.5 must be a whole number" in joined
    assert "add up to 100.5" in joined


def test_aspect_count_and_bounds():
    four = check_criteria(crit(("A", 25), ("A", 5), ("B", 25), ("C", 25), ("D", 10), ("D", 10)))["errors"]
    assert any("expected 3 aspects, found 4" in e for e in four)
    low = check_criteria(crit(("A", 5), ("A", 5), ("B", 25), ("B", 25), ("C", 20), ("C", 20)))["errors"]
    assert any("aspect 'A'" in e for e in low)


def test_parse_scenario_notes():
    text = "S1 +0.5 Delivery, -0.5 Domain: obs (cv)<br>S2 =: none<br>S3 = no comparable evidence"
    assert parse_scenario_notes(text, ASPECTS) == {
        "S1": {"Delivery": D("0.5"), "Domain": D("-0.5")},
        "S2": {},
        "S3": {},
    }


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("S1 =: a<br>S2 =: b", "missing scenario lines: S3"),
        ("S1 =: a<br>S1 =: b<br>S2 =: c<br>S3 =: d", "S1 appears more than once"),
        ("S1 maybe", "unreadable scenario line"),
        ("S1 +0.5 Speed: x<br>S2 =: b<br>S3 =: c", "unreadable scenario line"),
        ("S1 +0.5 Domain, +0.5 Domain: x<br>S2 =: b<br>S3 =: c", "adjusts 'Domain' twice"),
    ],
)
def test_parse_scenario_notes_errors(text, message):
    with pytest.raises(ValueError, match=message):
        parse_scenario_notes(text, ASPECTS)


def test_good_row_has_no_findings():
    assert check_scores(GOOD, WEIGHTS) == {"errors": [], "warnings": []}


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("Base", "7", "one decimal"),
        ("Base", "11.0", "1.0-10.0"),
        ("Credibility", "", "Credibility is empty"),
        ("Domain", "high", "not a number"),
    ],
)
def test_score_errors(field, value, message):
    findings = check_scores({**GOOD, field: value}, WEIGHTS)
    assert any(message in e for e in findings["errors"])


def test_note_warnings():
    row = {
        **GOOD,
        "Rationale": "word " * 26,
        "Notes": "no mark here (cv)<br>+ " + "word " * 15 + "(cv)<br>+ missing source",
    }
    warnings = "\n".join(check_scores(row, WEIGHTS)["warnings"])
    assert "Rationale has more than 25 words" in warnings
    assert "must start with" in warnings
    assert "more than 15 words" in warnings
    assert "no source reference" in warnings


def test_base_gap_warns():
    warnings = check_scores({**GOOD, "Base": "2.0"}, WEIGHTS)["warnings"]
    assert any("differs from the weighted aspect average 7.00" in w for w in warnings)


def test_scenarios_row():
    assert check_scenarios(GOOD, WEIGHTS)["errors"] == []
    bad = {**GOOD, "Scenario notes": "S1 +1.5 Domain: x<br>S2 =: b<br>S3 =: c"}
    assert any("within" in e for e in check_scenarios(bad, WEIGHTS)["errors"])


def test_check_rows_selects_rows_with_base(make_report, candidate_row):
    lines = make_report(candidates=[candidate_row("Ana", "", "7.0", "7.0"), candidate_row("Bo", "", "", "")]).split(
        "\n"
    )
    table = candidates_table(lines, ASPECTS)
    weights = aspect_weights(parse_criteria(lines))
    assert check_rows(table, weights, "scores")["checked"] == 1
    assert check_rows(table, weights, "scenarios", "Bo")["checked"] == 1
    assert check_rows(table, weights, "scores", "Zed")["errors"] == ["no candidate called 'Zed'"]


def test_interview_findings(make_report, candidate_row):
    rows = [candidate_row("Ana", "7.3", "7.0", "7.0"), candidate_row("Bo", "2.4", "3.0", "3.0")]
    lines = make_report(candidates=rows).split("\n")
    table = candidates_table(lines, ASPECTS)
    assert "section" in check_interview_findings(lines, table)["errors"][0]

    unsorted = make_report(candidates=list(reversed(rows)), tail="## Interview list (Overall > 5.0)\n").split("\n")
    errors = check_interview_findings(unsorted, candidates_table(unsorted, ASPECTS))["errors"]
    assert any("not sorted" in e for e in errors)

    incomplete = make_report(candidates=[candidate_row("Ana", "", "", "")]).split("\n")
    errors = check_interview_findings(incomplete, candidates_table(incomplete, ASPECTS))["errors"]
    assert "phases 6-9 not finished" in errors[0]
