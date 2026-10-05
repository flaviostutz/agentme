# Tests for ground.py: one-to-one matching, date slack, line window, source-only lines and exit codes.
import json

import pytest

from analyse_account_transactions.adapters.cli import ground as cli_ground
from analyse_account_transactions.adapters.cli import normalize as cli_normalize
from analyse_account_transactions.adapters.connectors.sources.sourcedoc import LocalSources
from analyse_account_transactions.app import ground
from conftest import HOLDER, N26_PAGES, SPLITWISE_CSV, make_pdf, row, write_ledger

SOURCE = """<statement>
2026-01-02 Coffee 3.50
2026-01-02 Coffee 3.50
05/01/2026 Book
12.00
Jan 8, 2026 Bakery 2,10
10 Jan 2026 Tram 1.00
2026-01-03 Late booking 4.00
20260111 Ref 99.99
Value 2026-01-12 0.00
"""


def run(capsys, *argv):
    code = cli_ground.main([*argv])
    out, err = capsys.readouterr()
    return code, out, err


def normalized(work, capsys, name, data, *sets):
    inbox = work / "inbox"
    inbox.mkdir(exist_ok=True)
    (inbox / name).write_bytes(data)
    cli_normalize.main(["stage", "inbox", "--id", "g"])
    cli_normalize.main(["run", name, "--id", "g", *sets])
    capsys.readouterr()
    return f".tmp/g/.work/normalized/{name.replace('.', '-')}.md"


def test_n26_grounded(work, capsys):
    path = normalized(work, capsys, "n.pdf", make_pdf(N26_PAGES))
    code, out, _ = run(capsys, path)
    assert code == 0
    assert "2/2 rows grounded, 0 unmatched" in out and "balance True" in out and "module check ok" in out
    saved = json.loads((work / ".tmp/g/.work/normalized/n-pdf.grounding.json").read_text())
    assert saved["matched-by"] == {"line": 2} and len(saved["sample"]) == 2


def test_splitwise_source_only_line(work, capsys):
    path = normalized(work, capsys, "s.csv", SPLITWISE_CSV.encode(), "--set", f"account-holder={HOLDER}")
    code, out, _ = run(capsys, path, "--json")
    result = json.loads(out)
    assert code == 0 and result["matched"] == 2
    assert [s["dates"] for s in result["source-only"]] == [["2026-01-12"]]


def text_case(work):
    (work / ".tmp/g").mkdir(parents=True)
    (work / ".tmp/g/src.ofx").write_text(SOURCE, encoding="utf-8")
    rows = [row("2026-01-02", "Coffee", "-3.50")] * 3 + [
        row("2026-01-05", "Book", "-12.00"),
        row("2026-01-08", "Bakery", "-2.10"),
        row("2026-01-10", "Tram", "-1.00"),
        row("2026-01-01", "Late", "-4.00"),
    ]
    return write_ledger(
        work / ".tmp/g/l.md", rows, source=".tmp/g/src.ofx", opening_balance="+30.00", closing_balance="+0.00"
    )


def test_matching_rules(work, capsys):
    text_case(work)
    code, out, _ = run(capsys, ".tmp/g/l.md", "--json", "--sample", "0")
    result = json.loads(out)
    assert code == 1
    assert result["matched-by"] == {"line": 4, "window": 1, "date+2": 1}
    assert [u["row"] for u in result["unmatched"]] == [3]
    assert [s["line"] for s in result["source-only"]] == [9]
    assert result["balance-chain"]["ok"] is False
    assert result["sample"] == []


def test_dates_and_amounts():
    assert ground.dates_in("on 31.12.2025 and 2026-01-02 or 20260103, Feb 4, 2026, 5 March 2026") == {
        "2025-12-31",
        "2026-01-02",
        "2026-01-03",
        "2026-02-04",
        "2026-03-05",
    }
    assert ground.dates_in("99.99.2026 Foo 30, 2026 12 Abc 2026") == set()
    assert ground.dates_in("03/04/2026") == {"2026-04-03", "2026-03-04"}
    assert ground.dates_in("03/04/2026", "dmy") == {"2026-04-03"}
    assert ground.dates_in("03/04/2026", "mdy") == {"2026-03-04"}
    assert ground.numeric_order(["13-01-2026", "25-02-2026", "31.03.2026 01-02-2026"]) == "dmy"
    assert ground.numeric_order(["01/13/2026", "02/25/2026", "03/31/2026"]) == "mdy"
    assert ground.numeric_order(["13-01-2026", "25-02-2026", "31.03.2026", "01/13/2026"]) == ""
    assert ground.amounts_in("1.234,56 and 7.00 but 2026-01-02 and 1.2.3") == {
        ground.parse_amount("1234.56"),
        ground.parse_amount("7.00"),
    }
    assert ground.amounts_in("", ["-3,50", "EUR", "x"]) == {ground.parse_amount("3.50")}


def test_llm_image_is_unverified(work, capsys):
    write_ledger(work / ".tmp/g/i.md", [row("2026-01-02", "Shop", "-1.00")], normalizer="llm-image")
    code, out, _ = run(capsys, ".tmp/g/i.md")
    assert code == 0 and "unverified" in out


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("elsewhere.csv", "path must be inside"),
        (".tmp/g/missing.csv", "file does not exist"),
        (".tmp/g/p.png", "has no text"),
    ],
)
def test_invalid_sources(work, capsys, source, message):
    write_ledger(work / ".tmp/g/l.md", [row("2026-01-02", "Shop", "-1.00")], source=source)
    (work / ".tmp/g/p.png").write_bytes(b"x")
    code, _, err = run(capsys, ".tmp/g/l.md")
    assert code == 2 and message in err


def test_parser_crash(work, capsys, monkeypatch):
    text_case(work)

    def boom(_self, path):
        raise RuntimeError("corrupt")

    monkeypatch.setattr(LocalSources, "load", boom)
    code, _, err = run(capsys, ".tmp/g/l.md")
    assert code == 2 and "RuntimeError: corrupt" in err
