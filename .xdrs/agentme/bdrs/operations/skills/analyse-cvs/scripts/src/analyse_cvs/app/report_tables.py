"""Read and edit the markdown tables of an analysis report."""

import re
from dataclasses import dataclass
from decimal import Decimal

from analyse_cvs.app.slugs import slugify
from analyse_cvs.shared.decimals import parse_decimal

_SPLIT = re.compile(r"(?<!\\)\|")
_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
REQUIRED_CANDIDATE_COLUMNS = ("Name", "Overall", "Base", "Credibility", "Rationale", "Scenario notes", "Notes")


@dataclass
class Table:
    """A markdown table located inside the report lines."""

    header: list[str]
    start: int
    rows: list[list[str]]

    @property
    def first_row(self) -> int:
        """Line index of the first data row."""
        return self.start + 2

    @property
    def end(self) -> int:
        """Line index just after the last data row."""
        return self.first_row + len(self.rows)

    def column(self, name: str) -> int:
        """Return the index of the column called name (case-insensitive) or raise ValueError."""
        for i, title in enumerate(self.header):
            if title.casefold() == name.casefold():
                return i
        msg = f"column {name!r} not found; columns are {self.header}"
        raise ValueError(msg)


@dataclass(frozen=True)
class Criterion:
    """One weighted criterion of the Criteria table."""

    name: str
    aspect: str
    weight: Decimal


def split_row(line: str) -> list[str]:
    """Split a table line into stripped cells, keeping escaped pipes inside cells."""
    inner = line.strip()
    inner = inner.removeprefix("|")
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [cell.strip() for cell in _SPLIT.split(inner)]


def render_row(cells: list[str]) -> str:
    """Render cells as a markdown table line."""
    return "| " + " | ".join(cells) + " |"


def find_table(lines: list[str], heading: str) -> Table:
    """Locate the first table under the heading line, or raise ValueError."""
    try:
        at = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        msg = f"section {heading!r} not found in the report"
        raise ValueError(msg) from None
    start = at + 1
    while start < len(lines) and not lines[start].startswith("|"):
        if lines[start].startswith("#"):
            msg = f"no table found under {heading!r}"
            raise ValueError(msg)
        start += 1
    if start + 1 >= len(lines) or not _SEPARATOR.match(lines[start + 1].strip()):
        msg = f"no table found under {heading!r}"
        raise ValueError(msg)
    header = split_row(lines[start])
    rows: list[list[str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(header):
            msg = f"row {len(rows) + 1} under {heading!r} has {len(cells)} cells, expected {len(header)}: {line[:60]!r}"
            raise ValueError(msg)
        rows.append(cells)
    return Table(header, start, rows)


def replace_rows(lines: list[str], table: Table, rows: list[list[str]]) -> list[str]:
    """Return the lines with the table's data rows replaced by rows."""
    return [*lines[: table.first_row], *(render_row(r) for r in rows), *lines[table.end :]]


def parse_criteria(lines: list[str]) -> list[Criterion]:
    """Read the Criteria table into criteria with exact decimal weights."""
    table = find_table(lines, "## Criteria")
    name_col, aspect_col, weight_col = table.column("Criterion"), table.column("Aspect"), table.column("Weight %")
    criteria: list[Criterion] = []
    for cells in table.rows:
        try:
            weight = parse_decimal(cells[weight_col].removesuffix("%"))
        except ValueError as err:
            msg = f"criterion {cells[name_col]!r}: weight {err}"
            raise ValueError(msg) from err
        criteria.append(Criterion(cells[name_col], cells[aspect_col], weight))
    return criteria


def aspect_weights(criteria: list[Criterion]) -> dict[str, Decimal]:
    """Sum the criteria weights per aspect, keeping the order of first appearance."""
    weights: dict[str, Decimal] = {}
    for criterion in criteria:
        weights[criterion.aspect] = weights.get(criterion.aspect, Decimal(0)) + criterion.weight
    return weights


def candidates_table(lines: list[str], aspects: list[str]) -> Table:
    """Return the Candidates table after checking that every required and aspect column exists."""
    table = find_table(lines, "## Candidates")
    for name in (*REQUIRED_CANDIDATE_COLUMNS, *aspects):
        table.column(name)
    return table


def as_dict(table: Table, cells: list[str]) -> dict[str, str]:
    """Map the header titles to the cells of one row."""
    return dict(zip(table.header, cells, strict=True))


def matches_candidate(row_name: str, query: str) -> bool:
    """Return True when query is the row's name (case-insensitive) or its slug."""
    if row_name.casefold() == query.casefold():
        return True
    try:
        return slugify(row_name) == query
    except ValueError:
        return False


def find_row(table: Table, name: str) -> dict[str, str]:
    """Return the row of the candidate called name or having slug name, or raise ValueError."""
    name_col = table.column("Name")
    found = [c for c in table.rows if matches_candidate(c[name_col], name)]
    if len(found) != 1:
        msg = f"expected exactly one candidate called {name!r}, found {len(found)}"
        raise ValueError(msg)
    return as_dict(table, found[0])
