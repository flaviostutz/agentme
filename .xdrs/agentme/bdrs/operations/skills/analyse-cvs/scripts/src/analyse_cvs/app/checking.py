"""Mechanical checks of criteria, candidate rows and scenario notes in a report."""

import re
from decimal import Decimal
from typing import Any

from analyse_cvs.app.ranking import check_interview, rank_table
from analyse_cvs.app.report_tables import Criterion, Table, as_dict, aspect_weights, matches_candidate
from analyse_cvs.app.scoring import Adjustments, validate_adjustments
from analyse_cvs.shared.constants import (
    ASPECT_COUNT,
    BASE_GAP_LIMIT,
    MAX_ASPECT_WEIGHT,
    MAX_CRITERIA,
    MAX_CRITERION_WEIGHT,
    MIN_ASPECT_WEIGHT,
    MIN_CRITERIA,
    NOTE_WORDS,
    RATIONALE_WORDS,
    SCALE_MAX,
    SCALE_MIN,
    SCENARIOS,
    WEIGHT_TOTAL,
)
from analyse_cvs.shared.decimals import decimal_places, has_one_decimal, parse_decimal

Findings = dict[str, Any]
_SOURCE = re.compile(r"\([^)]+\)\s*$")
_UNSOURCED_FLAGS = ("! revised", "! 2 CV versions", "! embedded instructions")
_NOTE_MARKS = "+-!?"


def new_findings() -> Findings:
    """Return an empty findings object."""
    return {"errors": [], "warnings": []}


def check_criteria(criteria: list[Criterion]) -> Findings:
    """Check criteria count, weights, aspect count and aspect weight bounds."""
    findings = new_findings()
    errors: list[str] = findings["errors"]
    if not MIN_CRITERIA <= len(criteria) <= MAX_CRITERIA:
        errors.append(f"expected {MIN_CRITERIA}-{MAX_CRITERIA} criteria, found {len(criteria)}")
    errors.extend(
        f"criterion {c.name!r}: weight {c.weight} must be a whole number from 1 to {MAX_CRITERION_WEIGHT}"
        for c in criteria
        if not Decimal(0) < c.weight <= MAX_CRITERION_WEIGHT or decimal_places(c.weight) > 0
    )
    total = sum((c.weight for c in criteria), Decimal(0))
    if total != WEIGHT_TOTAL:
        errors.append(f"weights add up to {total}, expected {WEIGHT_TOTAL}")
    weights = aspect_weights(criteria)
    if len(weights) != ASPECT_COUNT:
        errors.append(f"expected {ASPECT_COUNT} aspects, found {len(weights)}: {list(weights)}")
    for aspect, weight in weights.items():
        if not MIN_ASPECT_WEIGHT <= weight <= MAX_ASPECT_WEIGHT:
            errors.append(f"aspect {aspect!r}: weight {weight} must be {MIN_ASPECT_WEIGHT}-{MAX_ASPECT_WEIGHT}")
    return findings


def parse_scenario_notes(text: str, aspects: list[str]) -> Adjustments:
    """Parse the S1-S3 lines of a Scenario notes cell into signed adjustments per aspect."""
    names = "|".join(re.escape(a) for a in sorted(aspects, key=len, reverse=True))
    adj = rf"[+-]\d+(?:\.\d+)? (?:{names})"
    line = re.compile(rf"^(?P<s>S[123]) (?:=|(?P<adj>{adj}(?:, {adj})*))(?::|\s|$)")
    found: Adjustments = {}
    for segment in (s.strip() for s in text.split("<br>") if s.strip()):
        match = line.match(segment)
        if not match:
            msg = f"unreadable scenario line: {segment[:50]!r}"
            raise ValueError(msg)
        scenario = match["s"]
        if scenario in found:
            msg = f"{scenario} appears more than once"
            raise ValueError(msg)
        found[scenario] = {}
        for part in (match["adj"] or "").split(", "):
            if not part:
                continue
            value, aspect = part.split(" ", 1)
            if aspect in found[scenario]:
                msg = f"{scenario} adjusts {aspect!r} twice"
                raise ValueError(msg)
            found[scenario][aspect] = parse_decimal(value)
    missing = [s for s in SCENARIOS if s not in found]
    if missing:
        msg = f"missing scenario lines: {', '.join(missing)}"
        raise ValueError(msg)
    return found


def _score(row: dict[str, str], field: str, errors: list[str]) -> Decimal | None:
    text = row[field]
    if not text:
        errors.append(f"{row['Name']}: {field} is empty")
        return None
    try:
        value = parse_decimal(text)
    except ValueError:
        errors.append(f"{row['Name']}: {field} {text!r} is not a number")
        return None
    if not SCALE_MIN <= value <= SCALE_MAX or not has_one_decimal(value):
        errors.append(f"{row['Name']}: {field} {text!r} must be {SCALE_MIN}-{SCALE_MAX} with one decimal")
        return None
    return value


def _check_notes(row: dict[str, str], warnings: list[str]) -> None:
    name = row["Name"]
    if len(row["Rationale"].split()) > RATIONALE_WORDS:
        warnings.append(f"{name}: Rationale has more than {RATIONALE_WORDS} words")
    for note in (n.strip() for n in row["Notes"].split("<br>") if n.strip()):
        if note[0] not in _NOTE_MARKS:
            warnings.append(f"{name}: note must start with +, -, ! or ?: {note[:40]!r}")
        elif len(note.split()) > NOTE_WORDS:
            warnings.append(f"{name}: note has more than {NOTE_WORDS} words: {note[:40]!r}")
        elif not _SOURCE.search(note) and not note.startswith(_UNSOURCED_FLAGS):
            warnings.append(f"{name}: note has no source reference: {note[:40]!r}")


def check_scores(row: dict[str, str], weights: dict[str, Decimal]) -> Findings:
    """Check the score cells of one row, plus Rationale and Notes limits and the Base gap."""
    findings = new_findings()
    scores = {field: _score(row, field, findings["errors"]) for field in ("Base", "Credibility", *weights)}
    _check_notes(row, findings["warnings"])
    base = scores["Base"]
    aspect_scores = [s for s in (scores[a] for a in weights) if s is not None]
    if base is not None and len(aspect_scores) == len(weights):
        weighted = sum((s * w for s, w in zip(aspect_scores, weights.values(), strict=True)), Decimal(0))
        average = weighted / WEIGHT_TOTAL
        if abs(base - average) > BASE_GAP_LIMIT:
            findings["warnings"].append(
                f"{row['Name']}: Base {base} differs from the weighted aspect average {average:.2f} by more than "
                f"{BASE_GAP_LIMIT}; the Rationale must explain why",
            )
    return findings


def check_scenarios(row: dict[str, str], weights: dict[str, Decimal]) -> Findings:
    """Check that Scenario notes has S1-S3 lines within the adjustment limits."""
    findings = new_findings()
    try:
        validate_adjustments(parse_scenario_notes(row["Scenario notes"], list(weights)), set(weights))
    except ValueError as err:
        findings["errors"].append(f"{row['Name']}: {err}")
    return findings


def check_rows(table: Table, weights: dict[str, Decimal], stage: str, name: str | None = None) -> Findings:
    """Run the scores or scenarios check on the named row, or on every row that has a Base."""
    checker = check_scores if stage == "scores" else check_scenarios
    findings = new_findings()
    checked = 0
    for cells in table.rows:
        row = as_dict(table, cells)
        selected = matches_candidate(row["Name"], name) if name else bool(row["Base"])
        if not selected:
            continue
        checked += 1
        result = checker(row, weights)
        findings["errors"].extend(result["errors"])
        findings["warnings"].extend(result["warnings"])
    if name and not checked:
        findings["errors"].append(f"no candidate called {name!r}")
    findings["checked"] = checked
    return findings


def check_interview_findings(lines: list[str], table: Table) -> Findings:
    """Check that the Candidates table is in rank order and the interview list matches the ranking."""
    findings = new_findings()
    try:
        ranked = rank_table(table)
    except ValueError as err:
        findings["errors"].extend(str(err).split("\n"))
        return findings
    if [r.cells for r in ranked] != table.rows:
        findings["errors"].append("Candidates table is not sorted by unrounded Overall, then by Name")
    findings["errors"].extend(check_interview(lines, ranked))
    return findings
