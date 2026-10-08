"""Rank candidates by unrounded Overall and build the interview list skeleton."""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from analyse_cvs.app.report_tables import Table, as_dict, replace_rows
from analyse_cvs.app.scoring import is_invited, overall_exact
from analyse_cvs.shared.constants import INTERVIEW_CLOSING, INTERVIEW_HEADING, NONE_INVITED, PLACEHOLDER
from analyse_cvs.shared.decimals import parse_decimal, round_one_fraction, show


@dataclass(frozen=True)
class Ranked:
    """A candidate row with its exact Overall."""

    name: str
    cells: list[str]
    exact: Fraction
    overall: Decimal
    credibility: str

    @property
    def invited(self) -> bool:
        """True when the unrounded Overall is above 5.0."""
        return is_invited(self.exact)


def rank_table(table: Table) -> list[Ranked]:
    """Rank the rows; raise ValueError listing rows with missing scores or a stored Overall that differs."""
    ranked: list[Ranked] = []
    problems: list[str] = []
    for cells in table.rows:
        row = as_dict(table, cells)
        name = row["Name"]
        try:
            exact = overall_exact(parse_decimal(row["Base"]), parse_decimal(row["Credibility"]))
            stored = parse_decimal(row["Overall"])
        except ValueError:
            problems.append(f"{name}: Base, Credibility and Overall must all be filled (phases 6-9 not finished)")
            continue
        rounded = round_one_fraction(exact)
        if stored != rounded:
            problems.append(f"{name}: stored Overall {row['Overall']} but Base and Credibility give {show(rounded)}")
        ranked.append(Ranked(name, cells, exact, rounded, row["Credibility"]))
    if problems:
        raise ValueError("\n".join(problems))
    return sorted(ranked, key=lambda r: (-r.exact, r.name.casefold()))


def interview_section(ranked: list[Ranked]) -> list[str]:
    """Return the interview list section with one heading per invited candidate and an unfilled Chart bullet."""
    invited = [r for r in ranked if r.invited]
    lines = [INTERVIEW_HEADING, f"Invited: {len(invited)} of {len(ranked)}", ""]
    if not invited:
        lines += [NONE_INVITED, ""]
    for position, r in enumerate(invited, start=1):
        lines.append(f"### {position}. {r.name} (Overall {show(r.overall)}, Credibility {r.credibility})")
        lines.append(f"- Chart: {PLACEHOLDER}")
        lines.append("")
    lines.append(INTERVIEW_CLOSING)
    return lines


def _section_bounds(lines: list[str]) -> tuple[int, int] | None:
    start = next((i for i, line in enumerate(lines) if line.strip() == INTERVIEW_HEADING), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def apply_ranking(lines: list[str], table: Table, ranked: list[Ranked]) -> list[str]:
    """Return the lines with sorted Candidates rows and a fresh interview list section."""
    updated = replace_rows(lines, table, [r.cells for r in ranked])
    section = interview_section(ranked)
    bounds = _section_bounds(updated)
    if bounds is None:
        while updated and not updated[-1].strip():
            updated.pop()
        return [*updated, "", *section, ""]
    start, end = bounds
    tail = [""] if end < len(updated) else []
    return [*updated[:start], *section, *tail, *updated[end:]]


def check_interview(lines: list[str], ranked: list[Ranked]) -> list[str]:
    """Return errors for an interview list that is missing, out of order or still has placeholders."""
    bounds = _section_bounds(lines)
    if bounds is None:
        return [f"section {INTERVIEW_HEADING!r} not found"]
    section = lines[bounds[0] : bounds[1]]
    expected = interview_section(ranked)
    errors: list[str] = [
        f"missing or different line: {want!r}"
        for want in (line for line in expected if line.startswith(("Invited:", "###")))
        if want not in section
    ]
    if any(PLACEHOLDER in line for line in section):
        errors.append("interview list still has unfilled Chart links")
    if INTERVIEW_CLOSING not in section:
        errors.append("closing recommendation sentence is missing")
    invited_lines = [line for line in section if line.startswith("### ")]
    if invited_lines != [line for line in expected if line.startswith("### ")]:
        errors.append("invited candidates are not listed in rank order")
    return errors
