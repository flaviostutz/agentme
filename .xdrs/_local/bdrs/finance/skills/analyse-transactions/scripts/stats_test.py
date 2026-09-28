# Tests for stats.py and patterns.py over a synthetic, fully classified year of transactions.
import json
from datetime import date, timedelta
from decimal import Decimal

import patterns
import pytest
import stats
from conftest import row, write_ledger

FILE = ".tmp/s/year.md"
ESS = ("Housing & Utilities", "Expenditure", "Essential", "no")
FUN = ("Leisure, Shopping & Gifts", "Expenditure", "Discretionary", "no")


def year_rows() -> list:
    rows = []
    for m in range(1, 13):
        rows.append(row(f"2025-{m:02d}-25", "ACME", "+3000.00", "Income", "Income", "", "no"))
        rows.append(row(f"2025-{m:02d}-01", "Rent", "-1000.00", *ESS))
        rows.append(row(f"2025-{m:02d}-05", "Streamflix", "-15.99" if m > 9 else "-12.99", *FUN))
        rows.append(row(f"2025-{m:02d}-26", "Savings", "-500.00", "Transfers Out & Savings", "Savings", "", "no"))
        if m <= 4:
            rows.append(row(f"2025-{m:02d}-01", "Gym", "-30.00", "Health & Insurance", "Expenditure", "Important",
                            "no"))
    start = date(2025, 1, 1)
    for i in range(40):
        day = (start + timedelta(days=3 * i)).isoformat()
        rows.append(row(f"{day} 08:30", "Coffee", "-3.50", "Eating Out", "Expenditure", "Discretionary", "no"))
    rows.append(row("2025-03-15", "Insurer", "-600.00", "Health & Insurance", "Expenditure", "Essential", "no"))
    rows.append(row("2025-06-10", "ATM", "-50.00", *FUN))
    rows.append(row("2025-07-10", "ATM", "-50.00", *FUN))
    rows.append(row("2025-08-10", "Shop", "+10.00", *FUN[:3], "yes"))
    return rows


def run(capsys, *argv):
    code = stats.main([*argv])
    out, err = capsys.readouterr()
    return code, (json.loads(out) if out.strip() else None), err


@pytest.fixture
def year(work):
    write_ledger(work / FILE, year_rows(), period="2025-01-01..2025-12-31")
    return FILE


def test_totals_and_flow(year, capsys):
    code, result, _ = run(capsys, "totals", year)
    assert code == 0 and result["currency"] == "EUR"
    assert result["credits"] == "36010.00"
    code, result, _ = run(capsys, "flow", year)
    assert code == 0 and result["ok"]
    assert (result["income"], result["put_aside"]) == ("36000.00", "6000.00")
    assert result["refunds"] == {"rows": 1, "total": "10.00"}
    assert Decimal(result["income"]) == Decimal(result["savings"]) + Decimal(result["expenditures"])


def test_flow_fails_with_unassigned_rows(work, capsys):
    write_ledger(work / FILE, [row("2025-01-01", "X", "-1.00")])
    code, result, err = run(capsys, "flow", FILE)
    assert code == 1 and result["unassigned_rows"] == [1] and "invariant failed" in err


def test_relevance(year, capsys):
    result = run(capsys, "relevance", year)[1]
    essential = next(c for c in result["classes"] if c["relevance"] == "Essential")
    assert essential["top"][0]["title"] == "Rent" and essential["total"] == "12600.00"
    assert result["shares_display_sum"] in ("99.9", "100.0", "100.1")


def test_recurrence_buckets_sum(year, capsys):
    code, result, _ = run(capsys, "recurrence", year, "--assign", '{"Insurer": "Yearly"}')
    assert code == 0 and result["ok"]
    by = {b["bucket"]: b for b in result["buckets"]}
    assert [t["title"] for t in by["Daily"]["top"]] == ["Coffee"]
    assert by["Yearly"]["top"][0]["inferred"] is True
    assert {t["title"] for t in by["Monthly"]["top"]} >= {"ACME", "Rent", "Savings"}


def test_recurring(year, capsys):
    result = run(capsys, "recurring", year, "--assign", '{"Insurer": "Yearly"}')[1]
    items = {i["label"]: i for i in result["items"]}
    assert items["Rent"]["status"] == "active" and Decimal(items["Rent"]["per_year"]) > 11900
    assert items["Gym"]["status"] == "stopped" and items["Gym"]["per_year"] == "0.00"
    assert items["Insurer"]["inferred"] and items["Insurer"]["per_year"] == "600.00"
    assert items["Streamflix"]["price_change"] is True
    assert "Coffee" not in items
    assert result["totals"]["stopped"] == 1


def test_recurring_per_amount_split():
    rows = [row(f"2025-{m:02d}-{d}", "Store", v, *FUN) for m in range(1, 7) for d, v in (("03", "-5.00"),
                                                                                         ("20", "-80.00"))]
    result = patterns.recurring(rows, {}, {"": date(2025, 6, 30)})
    assert sorted(i["label"] for i in result["items"]) == ["Store (5.00)", "Store (80.00)"]


def test_insights(year, work, capsys):
    (work / ".tmp/s/hidden.json").write_text(json.dumps({"ATM": "cash", "Ghost": "card"}))
    result = run(capsys, "insights", year, "--hidden", ".tmp/s/hidden.json", "--threshold", "large-share=0.5")[1]
    assert [s["title"] for s in result["small_but_adds_up"]] == ["Coffee"]
    assert [x["title"] for x in result["large"]] == ["Rent"]
    assert result["hidden"]["cash"] == {"rows": 2, "total": "100.00", "titles": ["ATM"]}
    assert result["hidden_titles_not_found"] == ["Ghost"]
    assert [s["title"] for s in result["hidden"]["subscriptions"]] == ["Streamflix"]
    assert [p["title"] for p in result["hidden"]["price_rises"]] == ["Streamflix"]
    assert result["thresholds"]["large-share"] == "0.50"


def test_query(year, capsys):
    result = run(capsys, "query", year, "--filter", "needs=yes")[1]
    assert result["rows"] == 1 and result["items"][0]["title"] == "Shop"
    result = run(capsys, "query", year, "--filter", "title~coff", "--group-by", "hour")[1]
    assert result["groups"] == [{"key": "08", "rows": 40, "total": "-140.00", "share_of_rows": "100.0"}]
    result = run(capsys, "query", year, "--filter", "category=Housing & Utilities", "--group-by", "weekday")[1]
    assert sum(g["rows"] for g in result["groups"]) == 12
    result = run(capsys, "query", year, "--filter", "month=2025-01", "--group-by", "bucket")[1]
    assert {g["key"] for g in result["groups"]} >= {"Daily", "Monthly"}
    assert run(capsys, "query", year, "--filter", "file~year", "--group-by", "relevance")[1]["rows"] == 96
    assert run(capsys, "query", year, "--filter", "hour=unknown")[1]["rows"] == 56


def test_duplicates_and_estimate(year, work, capsys):
    write_ledger(work / ".tmp/s/copy.md", year_rows()[:2], period="2025-01-01..2025-01-31")
    result = run(capsys, "duplicates", year, ".tmp/s/copy.md")[1]
    assert len(result["duplicates"]) == 2
    code, result, _ = run(capsys, "estimate", year, "--target", "title=coffee", "--reduce-pct", "50")
    assert code == 0 and (result["current"], result["saving"], result["months"]) == ("140.00", "70.00", "12.00")
    assert result["saving_per_month"] == "5.84"


def test_months_and_ends_without_periods(work):
    files = [{"file": "a", "meta": {}}]
    rows = [stats.Tagged("a", row("2025-01-01", "X", "-1.00")), stats.Tagged("a", row("2025-01-10", "X", "-1.00"))]
    assert stats.months_covered(files, rows) == 1
    assert stats.months_covered([], []) == 1
    assert stats.period_ends(files, rows)[""] == date(2025, 1, 10)
    with pytest.raises(stats.LedgerError, match="no rows"):
        stats.period_ends(files, [])
    assert stats.currency_of([{"meta": {"currency": "EUR"}}, {"meta": {"currency": "USD"}}]) == "mixed: EUR, USD"


@pytest.mark.parametrize("argv", [
    ["query", FILE, "--filter", "colour=red"],
    ["estimate", FILE, "--target", "vendor=x", "--reduce-pct", "10"],
    ["estimate", FILE, "--target", "title=x", "--reduce-pct", "0"],
    ["estimate", FILE, "--target", "title=x", "--reduce-pct", "abc"],
    ["recurrence", FILE, "--assign", "{"],
    ["recurrence", FILE, "--assign", "[]"],
    ["recurrence", FILE, "--assign", '{"Coffee": "Daily"}'],
    ["recurring", FILE, "--assign", '{"Coffee": "Daily"}'],
    ["insights", FILE, "--threshold", "nope=1"],
    ["insights", FILE, "--hidden", ".tmp/s/bad.json"],
    ["insights", FILE, "--hidden", ".tmp/s/kind.json"],
    ["totals", ".tmp/s/none.md"],
])
def test_invalid_input(year, work, capsys, argv):
    (work / ".tmp/s/bad.json").write_text("{")
    (work / ".tmp/s/kind.json").write_text('{"ATM": "wallet"}')
    assert run(capsys, *argv)[0] == 2


def test_estimate_needs_target(year, capsys):
    with pytest.raises(SystemExit):
        stats.main(["estimate", FILE])
