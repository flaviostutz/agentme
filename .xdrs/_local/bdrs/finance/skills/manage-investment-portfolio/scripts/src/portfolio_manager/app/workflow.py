"""Pipeline steps shared by several commands: analyze, report and recording answers."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from portfolio_manager.app import analyze as analyze_mod
from portfolio_manager.app import inputcheck
from portfolio_manager.app import report as report_mod
from portfolio_manager.app.fx import Rates
from portfolio_manager.shared.errors import PmError

if TYPE_CHECKING:
    from portfolio_manager.adapters.connectors.local_fs.workspace import Workspace

RatesLoader = Callable[[str], tuple[Rates, str]]
LEDGER_FILES = ("accounts", "events", "snapshots", "references")


def run_analyze(ws: "Workspace", load_rates: RatesLoader) -> dict[str, Any]:
    """Recompute the derived analysis from the canonical ledger (never from cached results)."""
    data = {k: ws.read(f"data/{k}.json") for k in LEDGER_FILES}
    if any(v is None for v in data.values()):
        msg = "nothing ingested yet: run `pm ingest` first"
        raise PmError(msg)
    last = max((s["date"] for s in data["snapshots"]), default="1970-01-01")
    rates, notice = load_rates(last)
    manifest = ws.manifest()
    manifest["status"] = "analyzing"
    ws.save_manifest(manifest)
    result = analyze_mod.analyze(data, rates)
    result["fx_notice"] = notice
    ws.write("derived/analysis.json", result)
    manifest["status"] = "analyzed"
    ws.save_manifest(manifest)
    return result


def run_report(ws: "Workspace", load_rates: RatesLoader) -> tuple[dict[str, Any], dict[str, str], list[dict[str, Any]]]:
    """Analyze, then write the markdown reports and graphs; stale outputs are removed."""
    analysis = run_analyze(ws, load_rates)
    unresolved = ws.read("data/unresolved.json", [])
    files = report_mod.render(analysis, unresolved, ws.read("data/classifications.json", []))
    ws.clean_outputs("reports", "*.md", set(files))
    ws.clean_outputs("graphs", "*.mmd", set(files))
    for rel, text in files.items():
        ws.write_text(rel, text)
    return analysis, files, unresolved


def record_answer(ws: "Workspace", answer_id: str | None, value: str | None, accept_file: str | None) -> None:
    """Store an answer or an accepted file in answers.json; the caller re-ingests afterwards."""
    answers = ws.read("answers.json", {"accept_files": [], "answers": {}})
    if accept_file:
        shas = [i["sha256"] for i in ws.manifest().get("raw", {}).values() if i["sha256"].startswith(accept_file)]
        if len(shas) != 1:
            msg = f"--accept-file must match exactly one ingested file (matched {len(shas)})"
            raise PmError(msg)
        answers["accept_files"] = sorted(set(answers["accept_files"]) | {shas[0]})
    else:
        pending = {u["id"] for u in ws.read("data/unresolved.json", [])}
        ingest = ws.read("data/ingest.json", {})
        accounts = ws.read("data/accounts.json", {}).get("accounts", [])
        noted = {g["id"] for g in inputcheck.gaps(ingest, accounts, ws.read("data/snapshots.json", []))}
        if answer_id not in pending | noted:
            msg = f"unknown id {answer_id!r}; pending ids: {', '.join(sorted(pending | noted)[:10]) or 'none'}"
            raise PmError(msg)
        if not value:
            msg = "--value is required with --id"
            raise PmError(msg)
        answers["answers"][answer_id] = value
    ws.write_tracked("answers.json", answers)
