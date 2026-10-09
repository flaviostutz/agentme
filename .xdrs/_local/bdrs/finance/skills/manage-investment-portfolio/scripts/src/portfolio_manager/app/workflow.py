"""Pipeline steps shared by several commands: analyze, report and recording answers."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from portfolio_manager.app import acceptance, inputcheck, reports
from portfolio_manager.app import analyze as analyze_mod
from portfolio_manager.app import benchmark as benchmark_mod
from portfolio_manager.app.fx import Rates
from portfolio_manager.app.ingest import BENCHMARK_FILE
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.values import CALCULATION_VERSION

if TYPE_CHECKING:
    from portfolio_manager.adapters.connectors.local_fs.workspace import Workspace

RatesLoader = Callable[[str], tuple[Rates, str]]
ChartDownloader = Callable[[str], tuple[dict | None, str]]
LEDGER_FILES = ("accounts", "events", "snapshots", "references")


def configured_ticker(ws: "Workspace") -> str | None:
    """The benchmark ticker saved in config.yaml, or None when none is configured."""
    cfg = ws.config().get("benchmark")
    return (cfg.get("ticker") if isinstance(cfg, dict) else None) or None


def run_analyze(ws: "Workspace", load_rates: RatesLoader) -> dict[str, Any]:
    """Recompute the derived analysis from the canonical ledger (never from cached results)."""
    data = {k: ws.read(f"data/{k}.json") for k in LEDGER_FILES}
    if any(v is None for v in data.values()):
        msg = "nothing ingested yet: run `pm ingest` first"
        raise PmError(msg)
    manifest = ws.manifest()
    if manifest.get("calculation_version") != CALCULATION_VERSION:
        msg = (
            f"this work dir was ingested with calculation version {manifest.get('calculation_version')}, "
            f"the skill is at {CALCULATION_VERSION}: run `pm ingest` again (or `pm run`)"
        )
        raise PmError(msg)
    last = max((s["date"] for s in data["snapshots"]), default="1970-01-01")
    rates, notice = load_rates(last)
    manifest["status"] = "analyzing"
    ws.save_manifest(manifest)
    result = analyze_mod.analyze(data, rates, (configured_ticker(ws), ws.read(BENCHMARK_FILE)))
    result["fx_notice"] = notice
    ws.write("derived/analysis.json", result)
    manifest["status"] = "analyzed"
    ws.save_manifest(manifest)
    return result


def run_benchmark(ws: "Workspace", ticker: str | None, downloader: ChartDownloader) -> dict[str, Any]:
    """Download monthly closes for the ticker (or use the cached response when offline) and save them as a tracked input.

    Only the ticker leaves the machine. The ticker is saved in config.yaml once the data has been accepted.
    """
    symbol = benchmark_mod.validate_ticker(ticker or configured_ticker(ws) or "")
    cache = f"yahoo-{symbol}.json"
    payload, error = downloader(symbol)
    source = "download"
    series = None
    if payload is not None:
        try:
            series = benchmark_mod.parse_chart(payload)
        except PmError as err:
            error = str(err)
    if series is None:
        cached = ws.read_cache(cache)
        if cached is None:
            msg = f"benchmark for {symbol} not available: {error or 'no data'}; no cached copy exists"
            raise PmError(msg)
        series, source = benchmark_mod.parse_chart(cached), "cache"
    else:
        ws.write_cache(cache, payload)
    ws.write_tracked(BENCHMARK_FILE, {"ticker": symbol, "source": source, **series})
    cfg = ws.config()
    cfg["benchmark"] = {"ticker": symbol}
    ws.save_config(cfg)
    return {"ticker": symbol, "source": source, "months": len(series["prices"]), "currency": series["currency"]}


def require_ingested(ws: "Workspace") -> None:
    if ws.manifest()["status"] == "empty":
        msg = "nothing ingested yet: run `pm ingest` first"
        raise PmError(msg)


def current_check(ws: "Workspace") -> dict[str, Any]:
    """Completeness check computed from the ledger in data/ and the user's acceptances."""
    require_ingested(ws)
    accounts = ws.read("data/accounts.json", {})
    return inputcheck.check(
        ws.read("data/ingest.json", {}),
        accounts.get("accounts", []),
        ws.read("data/snapshots.json", []),
        ws.read("data/unresolved.json", []),
        accounts.get("openings", {}),
        acceptance.load(ws.read(acceptance.FILE)),
    )


def blocked(ws: "Workspace", what: str) -> str | None:
    """Refusal text while a finding is open or a record is unresolved; None when the output may be written."""
    result = current_check(ws)
    parts = []
    if (n := len(inputcheck.open_findings(result))) > 0:
        parts.append(f"{n} finding(s) open")
    if result["unresolved"]:
        parts.append(f"{len(result['unresolved'])} unresolved record(s)")
    if not parts:
        return None
    return (
        f"{what} refused: {' and '.join(parts)}. Add statements, or the user accepts each finding with "
        "`pm accept` and answers each record with `pm answer`; `pm check-input` lists them."
    )


def set_expected_start(ws: "Workspace", text: str | None) -> None:
    """Save the first day the user expects the statements to cover; it cannot be after the latest data."""
    day = acceptance.parse_day(text).isoformat()
    require_ingested(ws)
    latest = inputcheck.latest_date(ws.read("data/ingest.json", {}), ws.read("data/snapshots.json", []))
    if latest and day > latest:
        msg = f"--from {day} is after the latest statement date {latest}"
        raise PmError(msg)
    ws.write_tracked(acceptance.FILE, acceptance.with_expected_start(acceptance.load(ws.read(acceptance.FILE)), day))


def record_acceptances(ws: "Workspace", ids: list[str] | None, reason: str | None, note: str | None) -> int:
    """Store the user's decision for each finding id; returns how many findings were accepted."""
    if not ids:
        msg = "--id is required (repeat it to accept several findings)"
        raise PmError(msg)
    clean = acceptance.clean_note(note)
    found = current_check(ws)["findings"]
    store = acceptance.add(acceptance.load(ws.read(acceptance.FILE)), found, ids, reason, clean)
    ws.write_tracked(acceptance.FILE, store)
    return len(set(ids))


def run_report(ws: "Workspace", load_rates: RatesLoader) -> tuple[dict[str, Any], dict[str, str], list[dict[str, Any]]]:
    """Analyze, then write the markdown reports and graphs; stale outputs are removed."""
    analysis = run_analyze(ws, load_rates)
    unresolved = ws.read("data/unresolved.json", [])
    files = reports.render(analysis, unresolved, ws.read("data/classifications.json", []), current_check(ws))
    for sub, pattern in (("reports", "*.md"), ("graphs", "*.mmd"), ("graphs", "*.svg")):
        ws.clean_outputs(sub, pattern, set(files))
    for rel, text in files.items():
        ws.write_text(rel, text)
    ws.write("derived/securities.json", {"accounts": {k: a["securities"] for k, a in analysis["accounts"].items()}})
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
        if answer_id not in pending:
            msg = f"unknown id {answer_id!r}; pending ids: {', '.join(sorted(pending)[:10]) or 'none'}"
            raise PmError(msg)
        if not value:
            msg = "--value is required with --id"
            raise PmError(msg)
        answers["answers"][answer_id] = value
    ws.write_tracked("answers.json", answers)
