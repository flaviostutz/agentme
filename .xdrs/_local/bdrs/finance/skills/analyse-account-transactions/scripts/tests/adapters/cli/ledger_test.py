# Tests for ledger.py: file format, classification plans (apply), duplicate removal (drop) and trim.
import io
import json

import pytest

from analyse_account_transactions.adapters.cli import ledger as cli_ledger
from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import ledger
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.values import format_value, parse_decimal
from conftest import load_snapshot, read, row, write_ledger, write_snapshot

FILE = ".tmp/l/a.md"
HEAD = "| timestamp | title | value | description | category | flow | relevance | needs-investigation |\n"


def run(capsys, *argv):
    code = cli_ledger.main([*argv])
    out, err = capsys.readouterr()
    return code, out, err


def setup(work, rows=None, snapshot=True, **meta):
    rows = rows or [
        row("2026-01-02", "Coffee", "-3.50"),
        row("2026-01-03", "Coffe", "-2.00"),
        row("2026-01-04", "ACME", "+100.00", desc="salary | January"),
    ]
    path = write_ledger(work / FILE, rows, **meta)
    if snapshot:
        write_snapshot(path, read(path), {})
    return path


def plan(work, data, name="plan.json"):
    (work / ".tmp/l" / name).write_text(json.dumps(data), encoding="utf-8")
    return f".tmp/l/{name}"


def test_roundtrip_and_escaping(work):
    path = setup(work)
    led = read(path)
    assert led.rows[2].description == "salary | January"
    assert "salary \\| January" in path.read_text()
    assert ledger.render(led, "a") == path.read_text()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("# x\n", "no transaction table"),
        ("| timestamp | title |\n", "header must be"),
        (HEAD + "|---|\n| a | b |\n", "expected 8 columns"),
        (HEAD + "| 2026-01-01 | t | 1.5 | d |  |  |  |  |\n", "signed with 2 decimals"),
        (HEAD + "| 2026-01-01 | t | +1.00 | d |  |  |  |  \\|\n", "must start and end"),
    ],
)
def test_parse_errors(text, message):
    with pytest.raises(LedgerError, match=message):
        ledger.parse_text(text)


def test_helpers(work):
    assert format_value(parse_decimal("0")) == "+0.00"
    with pytest.raises(LedgerError, match="not a number"):
        parse_decimal("x")
    assert ledger.clip_description("a  b\n c") == "a b c"
    with pytest.raises(LedgerError, match="must be inside"):
        LocalWorkspace(work).resolve_tmp("../x.md")
    with pytest.raises(LedgerError, match="snapshot missing"):
        load_snapshot(setup(work, snapshot=False))


def test_apply_plan(work, capsys):
    setup(work)
    p = plan(
        work,
        {
            "rename": {"Coffe": "Coffee"},
            "map": {
                "Coffee": {"category": "Eating Out", "flow": "Expenditure", "relevance": "Discretionary"},
                "ACME": {"category": "Income", "flow": "Income", "relevance": ""},
            },
            "rows": {"3": {"needs": "yes"}},
        },
    )
    code, out, _ = run(capsys, "apply", FILE, "--input", p, "--dry-run")
    assert code == 0 and "(dry run)" in out
    assert read(work / FILE).rows[0].category == ""
    code, out, _ = run(capsys, "apply", FILE, "--input", p, "--json")
    result = json.loads(out)
    rows = read(work / FILE).rows
    assert [r.title for r in rows] == ["Coffee", "Coffee", "ACME"]
    assert [(r.category, r.needs) for r in rows] == [("Eating Out", "no"), ("Eating Out", "no"), ("Income", "yes")]
    assert result["protected_rows"] == []


def test_user_answers_are_protected(work, capsys, monkeypatch):
    setup(work)
    answer = {"rows": {"1": {"category": "Groceries & Household", "flow": "Expenditure", "relevance": "Essential"}}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(answer)))
    assert run(capsys, "apply", FILE, "--input", "-", "--source", "user")[0] == 0
    snap = json.loads((work / ".tmp/l/a.snapshot.json").read_text())
    assert snap["user"]["1"]["category"] == "Groceries & Household"
    auto = plan(
        work, {"map": {"Coffee": {"category": "Eating Out", "flow": "Expenditure", "relevance": "Discretionary"}}}
    )
    code, out, _ = run(capsys, "apply", FILE, "--input", auto)
    assert code == 0 and "1 protected user row(s)" in out
    assert read(work / FILE).rows[0].category == "Groceries & Household"
    code, _, err = run(capsys, "apply", FILE, "--input", plan(work, {"rename": {"Coffee": "Koffie"}}, "p2.json"))
    assert code == 0 and read(work / FILE).rows[0].title == "Koffie"
    code, _, err = run(capsys, "apply", FILE, "--input", plan(work, {"rows": {"1": {"needs": "no"}}}, "p3.json"))
    assert code == 2 and "answered by the user" in err


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"other": {}}, "only 'rename', 'map' and 'rows'"),
        ({"rows": {"9": {"needs": "no"}}}, "does not exist"),
        ({"rows": {"1": {"colour": "red"}}}, "unknown keys"),
        ({"map": {"Coffee": {"category": "Food"}}}, "invalid category"),
        ({"rows": {"1": {"title": " "}}}, "empty title"),
    ],
)
def test_apply_invalid_plans(work, capsys, data, message):
    setup(work)
    code, _, err = run(capsys, "apply", FILE, "--input", plan(work, data))
    assert code == 2 and message in err


def test_apply_invalid_json(work, capsys):
    setup(work)
    (work / ".tmp/l/bad.json").write_text("{", encoding="utf-8")
    assert "not valid JSON" in run(capsys, "apply", FILE, "--input", ".tmp/l/bad.json")[2]


def test_drop(work, capsys):
    path = setup(work)
    snap = json.loads(ledger.snapshot_path(path).read_text())
    snap["user"] = {"3": {"category": "Income", "flow": "Income", "relevance": ""}}
    ledger.snapshot_path(path).write_text(json.dumps(snap))
    code, out, _ = run(capsys, "drop", FILE, "--rows", "2,1")
    assert code == 0 and "dropped 2 row(s); 1 left" in out
    assert json.loads(ledger.snapshot_path(path).read_text())["user"] == {"1": snap["user"]["3"]}
    assert "out of range" in run(capsys, "drop", FILE, "--rows", "5")[2]
    assert "comma-separated" in run(capsys, "drop", FILE, "--rows", "a")[2]


def test_trim(work, capsys):
    rows = [row("2025-12-30", "Old", "-5.00"), row("2026-01-02", "Coffee", "-3.50"), row("2026-02-01", "New", "+9.00")]
    setup(
        work,
        rows,
        snapshot=False,
        opening_balance="+100.00",
        closing_balance="+100.50",
        period="2025-12-15..2026-02-14",
    )
    code, out, _ = run(capsys, "trim", FILE, "--from", "2026-01-01", "--until", "2026-01-31")
    assert code == 0 and "dropped 2 row(s)" in out
    led = read(work / FILE)
    assert (led.meta["opening-balance"], led.meta["closing-balance"]) == ("+95.00", "+91.50")
    assert led.meta["period"] == "2026-01-01..2026-01-31"
    write_snapshot(work / FILE, led, {})
    assert "before the snapshot" in run(capsys, "trim", FILE, "--from", "2026-01-01", "--until", "2026-01-31")[2]


def test_trim_unknown_period_and_errors(work, capsys):
    setup(work, snapshot=False, period="unknown")
    assert run(capsys, "trim", FILE, "--from", "2026-01-03", "--until", "2026-01-31")[0] == 0
    assert read(work / FILE).meta["period"] == "2026-01-03..2026-01-31"
    assert "YYYY-MM-DD" in run(capsys, "trim", FILE, "--from", "2026-1-3", "--until", "2026-01-31")[2]
    assert "after --until" in run(capsys, "trim", FILE, "--from", "2026-02-01", "--until", "2026-01-31")[2]
