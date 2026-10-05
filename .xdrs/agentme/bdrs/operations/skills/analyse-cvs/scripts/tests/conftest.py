# Python 3.11+ pytest suite; run with: make test
import pytest

REPORT_TEMPLATE = """# CV analysis: sample (2026-10-04)

## Inputs
- Role: sample

## Criteria
| Criterion | Aspect | Weight % | CV evidence signals |
|---|---|---|---|
| Shipping | Delivery | 15 | releases |
| Quality | Delivery | 15 | tests |
| Teamwork | Collaboration | 20 | pairing |
| Mentoring | Collaboration | 20 | coaching |
| Banking | Domain | 15 | bank roles |
| Regulation | Domain | 15 | compliance |

Anchors, Delivery: 1 = none; 4 = some; 7 = good; 10 = great

## Dry-run Scenarios
### S1: Typical (typical delivery)
- Context: x

## Sources
| Source | Converted file | Status |
|---|---|---|
{sources}

## Candidates
| Name | Overall | Base | Credibility | Rationale | Delivery | Collaboration | Domain | Scenario notes | Notes |
|---|---|---|---|---|---|---|---|---|---|
{candidates}

{tail}
"""

NOTES = "S1 =: ok (cv)<br>S2 =: ok (cv)<br>S3 =: ok (cv)"


ASPECTS = ("7.0", "7.0", "7.0")


def _candidate_row(name, overall, base, cred, aspects=ASPECTS, scenario=NOTES, notes="+ strong (cv p1)"):
    cells = [name, overall, base, cred, "fine", *aspects, scenario, notes]
    return "| " + " | ".join(cells) + " |"


def _make_report(candidates=(), sources=(), tail=""):
    return REPORT_TEMPLATE.format(sources="\n".join(sources), candidates="\n".join(candidates), tail=tail)


@pytest.fixture
def candidate_row():
    return _candidate_row


@pytest.fixture
def make_report():
    return _make_report


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tmp").mkdir()
    return tmp_path


@pytest.fixture
def report(workdir):
    """Return a function that writes a report into .tmp/ and returns its relative path."""

    def write(candidates=(), sources=(), tail=""):
        path = workdir / ".tmp" / "cv-sample-analysis-2026-10-04.md"
        path.write_text(_make_report(candidates, sources, tail), encoding="utf-8")
        return ".tmp/cv-sample-analysis-2026-10-04.md"

    return write
