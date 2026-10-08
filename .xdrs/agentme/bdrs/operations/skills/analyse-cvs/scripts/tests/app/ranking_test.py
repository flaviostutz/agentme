# Python 3.11+ pytest suite; run with: make test
import pytest

from analyse_cvs.app.ranking import apply_ranking, check_interview, interview_section, rank_table
from analyse_cvs.app.report_tables import candidates_table

ASPECTS = ["Delivery", "Collaboration", "Domain"]


@pytest.fixture
def ranked_report(make_report, candidate_row):
    def build(tail=""):
        rows = [
            candidate_row("Cy", "3.7", "4.0", "4.0"),
            candidate_row("Bo", "5.0", "5.0", "5.5"),
            candidate_row("Dee", "5.0", "5.0", "5.6"),
            candidate_row("Ana", "7.3", "7.0", "7.0"),
        ]
        lines = make_report(candidates=rows, tail=tail).split("\n")
        return lines, candidates_table(lines, ASPECTS)

    return build


def test_rank_orders_by_unrounded_overall_and_invites_above_five(ranked_report):
    _, table = ranked_report()
    ranked = rank_table(table)
    assert [(r.name, str(r.overall), r.invited) for r in ranked] == [
        ("Ana", "7.3", True),
        ("Dee", "5.0", True),
        ("Bo", "5.0", False),
        ("Cy", "3.7", False),
    ]


def test_ties_are_sorted_by_name(make_report, candidate_row):
    lines = make_report(
        candidates=[candidate_row("Zed", "7.0", "7.0", "5.5"), candidate_row("amy", "7.0", "7.0", "5.5")]
    ).split("\n")
    assert [r.name for r in rank_table(candidates_table(lines, ASPECTS))] == ["amy", "Zed"]


def test_incomplete_and_mismatching_rows_are_reported(make_report, candidate_row):
    rows = [candidate_row("Ana", "", "", ""), candidate_row("Bo", "9.0", "5.0", "5.5")]
    lines = make_report(candidates=rows).split("\n")
    with pytest.raises(ValueError, match="Ana: Base, Credibility and Overall must all be filled") as err:
        rank_table(candidates_table(lines, ASPECTS))
    assert "Bo: stored Overall 9.0 but Base and Credibility give 5.0" in str(err.value)
    mismatch = make_report(candidates=[candidate_row("Bo", "9.0", "5.0", "5.5")]).split("\n")
    with pytest.raises(ValueError, match=r"Bo: stored Overall 9\.0 but Base and Credibility give 5\.0"):
        rank_table(candidates_table(mismatch, ASPECTS))


def test_interview_section_lists_invited_in_rank_order(ranked_report):
    _, table = ranked_report()
    section = interview_section(rank_table(table))
    assert section[:2] == ["## Interview list (Overall > 5.0)", "Invited: 2 of 4"]
    assert [line for line in section if line.startswith("###")] == [
        "### 1. Ana (Overall 7.3, Credibility 7.0)",
        "### 2. Dee (Overall 5.0, Credibility 5.6)",
    ]
    assert section[-1] == "This list is a recommendation; a human decides who to interview."
    assert section.count("- Chart: <fill>") == 2
    assert not any(line.startswith(("- Why invite", "- Investigate", "- Questions")) for line in section)


def test_nobody_invited(make_report, candidate_row):
    lines = make_report(candidates=[candidate_row("Bo", "5.0", "5.0", "5.5")]).split("\n")
    section = interview_section(rank_table(candidates_table(lines, ASPECTS)))
    assert "Invited: 0 of 1" in section
    assert any(line.startswith("No candidate scored above 5.0") for line in section)


def test_apply_ranking_sorts_rows_and_appends_section(ranked_report):
    lines, table = ranked_report()
    updated = apply_ranking(lines, table, rank_table(table))
    new_table = candidates_table(updated, ASPECTS)
    assert [row[0] for row in new_table.rows] == ["Ana", "Dee", "Bo", "Cy"]
    assert updated.count("## Interview list (Overall > 5.0)") == 1


def test_apply_ranking_replaces_an_existing_section(ranked_report):
    old = "## Interview list (Overall > 5.0)\nInvited: 0 of 4\n\nold text\n\n## Appendix\nkeep"
    lines, table = ranked_report(tail=old)
    updated = apply_ranking(lines, table, rank_table(table))
    text = "\n".join(updated)
    assert "old text" not in text
    assert "Invited: 2 of 4" in text
    assert text.count("## Interview list (Overall > 5.0)") == 1
    assert "## Appendix\nkeep" in text


def test_check_interview(ranked_report):
    lines, table = ranked_report()
    ranked = rank_table(table)
    assert check_interview(lines, ranked) == ["section '## Interview list (Overall > 5.0)' not found"]

    written = apply_ranking(lines, table, ranked)
    errors = check_interview(written, ranked)
    assert "interview list still has unfilled Chart links" in errors

    filled = [line.replace("<fill>", "[chart](x/interview-chart.md)") for line in written]
    assert check_interview(filled, ranked) == []

    broken = [line for line in filled if not line.startswith("This list") and "### 2." not in line]
    errors = check_interview(broken, ranked)
    assert any("missing or different line" in e for e in errors)
    assert "closing recommendation sentence is missing" in errors
