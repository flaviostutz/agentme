# Python 3.11+ pytest suite; run with: make test
from decimal import Decimal

import pytest

from analyse_cvs.app.report_tables import (
    aspect_weights,
    candidates_table,
    find_row,
    find_table,
    parse_criteria,
    replace_rows,
    split_row,
)


def test_split_row_keeps_escaped_pipes():
    assert split_row("| a \\| b | c |") == ["a \\| b", "c"]


def test_criteria_and_aspect_weights(make_report):
    lines = make_report().split("\n")
    criteria = parse_criteria(lines)
    assert len(criteria) == 6
    assert aspect_weights(criteria) == {"Delivery": Decimal(30), "Collaboration": Decimal(40), "Domain": Decimal(30)}


def test_find_table_errors():
    with pytest.raises(ValueError, match="not found"):
        find_table(["# x"], "## Sources")
    with pytest.raises(ValueError, match="no table"):
        find_table(["## Sources", "text", "## Candidates"], "## Sources")
    with pytest.raises(ValueError, match="no table"):
        find_table(["## Sources", "| a |"], "## Sources")
    with pytest.raises(ValueError, match="cells"):
        find_table(["## T", "| a | b |", "|---|---|", "| 1 |"], "## T")


def test_missing_columns_are_reported():
    lines = ["## Candidates", "| Name | Overall |", "|---|---|"]
    with pytest.raises(ValueError, match="column 'Base' not found"):
        candidates_table(lines, ["Delivery"])


def test_bad_weight_is_reported():
    lines = ["## Criteria", "| Criterion | Aspect | Weight % |", "|---|---|---|", "| X | A | many |"]
    with pytest.raises(ValueError, match="criterion 'X'"):
        parse_criteria(lines)


def test_find_row_and_replace_rows(make_report, candidate_row):
    lines = make_report(candidates=[candidate_row("Ana", "", "", ""), candidate_row("Bo", "", "", "")]).split("\n")
    table = candidates_table(lines, ["Delivery", "Collaboration", "Domain"])
    assert find_row(table, "ana")["Name"] == "Ana"
    assert find_row(table, "bo")["Name"] == "Bo"
    with pytest.raises(ValueError, match="exactly one"):
        find_row(table, "Zed")
    swapped = replace_rows(lines, table, list(reversed(table.rows)))
    assert find_table(swapped, "## Candidates").rows[0][0] == "Bo"
