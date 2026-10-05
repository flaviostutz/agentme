# Tests for answers.py (stored user answers) and research.py (counterparty research cache).
import json

import pytest

from analyse_account_transactions.adapters.cli import answers, research
from analyse_account_transactions.app import ledger
from conftest import read, row, write, write_ledger, write_snapshot

FILE = ".tmp/a/n.md"
GROCERY = {"category": "Groceries & Household", "flow": "Expenditure", "relevance": "Essential"}


def call(module, capsys, *argv):
    code = module.main([*argv])
    out, err = capsys.readouterr()
    return code, (json.loads(out) if out.strip() else err)


def answered(work):
    rows = [
        row("2026-01-02", "Shop", "-1.00", GROCERY["category"], GROCERY["flow"], GROCERY["relevance"], "user"),
        row("2026-01-02", "Shop", "-1.00", GROCERY["category"], GROCERY["flow"], GROCERY["relevance"], "user"),
        row("2026-01-03", "Cafe", "-2.00", "Eating Out", "Expenditure", "Discretionary", "no"),
    ]
    return write_ledger(work / FILE, rows)


def test_export_apply_roundtrip(work, capsys):
    answered(work)
    code, result = call(answers, capsys, "export", FILE, "--into", ".tmp/a/answers.json")
    assert code == 0 and (result["total"], result["added"]) == (2, 2)
    keys = sorted(json.loads((work / ".tmp/a/answers.json").read_text())["answers"])
    assert [k.rsplit("|", 1)[1] for k in keys] == ["1", "2"]
    assert call(answers, capsys, "export", FILE, "--into", ".tmp/a/answers.json")[1]["added"] == 0
    fresh = write_ledger(
        work / ".tmp/b/n.md",
        [row("2026-01-02", "Shop", "-1.00"), row("2026-01-03", "Cafe", "-2.00"), row("2026-01-02", "Shop", "-1.00")],
    )
    write_snapshot(fresh, read(fresh), {})
    code, result = call(answers, capsys, "apply", ".tmp/b/n.md", "--answers", ".tmp/a/answers.json")
    assert code == 0 and (result["applied"], result["skipped"]) == (2, [])
    rows = read(fresh).rows
    assert [(r.category, r.needs) for r in rows] == [
        (GROCERY["category"], "user"),
        ("", ""),
        (GROCERY["category"], "user"),
    ]
    assert json.loads(ledger.snapshot_path(fresh).read_text())["user"]["3"] == GROCERY


def test_export_updates_changed_answer(work, capsys):
    path = answered(work)
    call(answers, capsys, "export", FILE, "--into", ".tmp/a/answers.json")
    led = read(path)
    led.rows[0].relevance = "Important"
    write(path, led)
    assert call(answers, capsys, "export", FILE, "--into", ".tmp/a/answers.json")[1]["updated"] == 1


def test_apply_skips_invalid_answer(work, capsys):
    answered(work)
    call(answers, capsys, "export", FILE, "--into", ".tmp/a/answers.json")
    data = json.loads((work / ".tmp/a/answers.json").read_text())
    first = min(data["answers"])
    data["answers"][first]["category"] = "Food"
    (work / ".tmp/a/answers.json").write_text(json.dumps(data))
    fresh = write_ledger(work / ".tmp/b/n.md", [row("2026-01-02", "Shop", "-1.00")])
    write_snapshot(fresh, read(fresh), {})
    result = call(answers, capsys, "apply", ".tmp/b/n.md", "--answers", ".tmp/a/answers.json")[1]
    assert result["applied"] == 0 and "invalid category" in result["skipped"][0]["message"]


def test_import_newest_wins(work, capsys):
    base = {"version": 1, "answers": {"k|1": {**GROCERY, "answered": "2026-01-01T00:00:00Z"}}}
    newer = {
        "version": 1,
        "answers": {
            "k|1": {**GROCERY, "relevance": "Important", "answered": "2026-02-01T00:00:00Z"},
            "j|1": {**GROCERY, "answered": "2026-01-01T00:00:00Z"},
        },
    }
    (work / ".tmp/base.json").write_text(json.dumps(base))
    (work / ".tmp/newer.json").write_text(json.dumps(newer))
    result = call(answers, capsys, "import", ".tmp/newer.json", "--into", ".tmp/base.json")[1]
    assert (result["added"], result["updated"], result["total"]) == (1, 1, 2)
    assert json.loads((work / ".tmp/base.json").read_text())["answers"]["k|1"]["relevance"] == "Important"
    (work / ".tmp/bad.json").write_text("[]")
    code, err = call(answers, capsys, "import", ".tmp/bad.json", "--into", ".tmp/base.json")
    assert code == 2 and "not an answers file" in err


CACHE = ".tmp/r/cache.json"


def test_research_add_lookup_import(work, capsys):
    code, result = call(
        research,
        capsys,
        "add",
        "--cache",
        CACHE,
        "--name",
        "Cafe Rose",
        "--city",
        "Utrecht",
        "--url",
        "https://example.com/rose",
        "--finding",
        "A cafe.",
        "--category-hint",
        "Eating Out",
    )
    assert code == 0 and result["total"] == 1
    code, result = call(research, capsys, "lookup", "cafe  ROSE", "Other", "--cache", CACHE)
    assert code == 1 and list(result["found"]) == ["cafe  ROSE"] and result["missing"] == ["Other"]
    assert call(research, capsys, "lookup", "Cafe Rose", "--cache", CACHE)[0] == 0
    other = {
        "version": 1,
        "entries": {
            "caferose": {"name": "Cafe Rose", "checked": "2999-01-01", "finding": "new"},
            "bakery": {"name": "Bakery", "checked": "2026-01-01", "finding": "b"},
        },
    }
    (work / ".tmp/r/other.json").write_text(json.dumps(other))
    result = call(research, capsys, "import", ".tmp/r/other.json", "--cache", CACHE)[1]
    assert (result["total"], result["added"]) == (2, 1)
    assert json.loads((work / CACHE).read_text())["entries"]["caferose"]["finding"] == "new"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--name", "NL91 ABNA 0417 1643 00"], "contains an IBAN"),
        (["--name", "Shop 12,50"], "contains an amount"),
        (["--name", "Ref 1234567"], "contains a long number"),
        (["--name", "a@b.com"], "contains an e-mail"),
        (["--name", " "], "must be 1..80"),
        (["--name", "Shop", "--city", "x" * 81], "must be 1..80"),
        (["--name", "Shop", "--url", "ftp://x"], "http(s) URL"),
        (["--name", "Shop", "--finding", " "], "--finding must be"),
        (["--name", "Shop", "--category-hint", "Food"], "--category-hint must be"),
    ],
)
def test_research_rejects(work, capsys, args, message):
    base = {"--url": "https://example.com", "--finding": "A shop."}
    for k, v in zip(args[::2], args[1::2]):
        base[k] = v
    argv = [x for kv in base.items() for x in kv]
    if "--name" not in base:
        argv += ["--name", "Shop"]
    code, err = call(research, capsys, "add", "--cache", CACHE, *argv)
    assert code == 2 and message in err


def test_research_bad_cache(work, capsys):
    (work / ".tmp/r").mkdir()
    (work / CACHE).write_text('{"version": 2}')
    code, err = call(research, capsys, "lookup", "x", "--cache", CACHE)
    assert code == 2 and "not a research cache" in err
