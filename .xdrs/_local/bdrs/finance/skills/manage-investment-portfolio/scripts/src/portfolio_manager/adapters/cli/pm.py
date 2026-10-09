"""Portfolio manager CLI.

Commands: portfolio-name, init, inspect, ingest, check-input, answer, accept, analyze, classify, benchmark, report,
export, run, validate.

Reports and exports are refused (exit 1, nothing written) while a coverage finding is open or a record is unresolved.
Exit codes: 0 ok, 1 validation failures found or output refused, 2 invalid input.
Successful runs end with `results-path: ...`; errors print `error: ...`.
"""

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from portfolio_manager.adapters.connectors.ecb.ecb_rates import download_ecb, load_cached
from portfolio_manager.adapters.connectors.institutions import default_registry
from portfolio_manager.adapters.connectors.local_fs.workspace import (
    SKILL_DIR,
    Workspace,
    collect_sources,
    resolve_tmp,
    work_dir,
)
from portfolio_manager.adapters.connectors.pdf.pdf_reader import read_pdf
from portfolio_manager.adapters.connectors.yahoo.yahoo_prices import download_chart
from portfolio_manager.app import acceptance, export_pp, inputcheck, inspector, reports, workflow
from portfolio_manager.app import classify as classify_mod
from portfolio_manager.app import ingest as ingest_mod
from portfolio_manager.app import portfolio_name as portfolio_name_mod
from portfolio_manager.app.fx import Rates
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.values import CALCULATION_VERSION

WORK_COMMANDS = (
    "init",
    "inspect",
    "ingest",
    "check-input",
    "answer",
    "accept",
    "analyze",
    "classify",
    "benchmark",
    "report",
    "export",
    "run",
    "validate",
)
COMMANDS = ("portfolio-name", *WORK_COMMANDS)
DEFAULT_PORTFOLIO = "main"
EXPORT_DIR = "exports/portfolio-performance"
SET_FIELDS = classify_mod.FIELDS
Result = tuple[int, str]


def _ws(args: argparse.Namespace, cwd: Path) -> Workspace:
    return Workspace(work_dir(args.portfolio, cwd))


def _need(ws: Workspace) -> None:
    if not ws.exists():
        msg = f"work dir not initialised: run `pm init --portfolio <portfolio>` first ({ws.root})"
        raise PmError(msg)


def _run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S")


def _summary(ws: Workspace, lines: list[str]) -> str:
    rel = f"{SKILL_DIR}/{ws.root.name}/"
    return "\n".join([*lines, f"results-path: {rel}"])


def _rates_loader(ws: Workspace, *, offline: bool) -> Callable[[str], tuple[Rates, str]]:
    def offline_downloader() -> tuple[str, str]:
        return "", "offline mode"

    downloader = offline_downloader if offline else download_ecb

    def load(needed_until: str) -> tuple[Rates, str]:
        return load_cached(ws.cache_path("ecb-hist.csv"), needed_until, downloader)

    return load


def _ingest(ws: Workspace, sources: list[Path]) -> dict:
    return ingest_mod.ingest(ws, sources, _run_id(), read_pdf, default_registry())


def cmd_portfolio_name(args: argparse.Namespace, cwd: Path) -> Result:
    sources = collect_sources(resolve_tmp(args.source, cwd))
    found = portfolio_name_mod.holders(sources, read_pdf, default_registry())
    name, candidates = portfolio_name_mod.choose(found)
    if name:
        return 0, f"portfolio: {name}"
    if candidates:
        return 1, f"Several holders found: {', '.join(candidates)}. Ask the user which portfolio name to use."
    return (
        1,
        f"No holder name found in the statements. Ask the user for a portfolio name (default {DEFAULT_PORTFOLIO}).",
    )


def cmd_init(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    created = ws.init()
    return 0, _summary(ws, ["Work dir created." if created else "Work dir already exists; nothing overwritten."])


def cmd_inspect(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    sources = collect_sources(resolve_tmp(args.source, cwd))
    infos = [inspector.inspect_pdf(p, read_pdf) for p in sources]
    ws.write("inspect.json", infos)
    bad = [i["file"] for i in infos if i["status"] != "ok"]
    lines = [f"Inspected {len(infos)} PDF file(s); structure only (no values) saved to inspect.json."]
    if bad:
        lines.append(f"Unreadable or locked: {len(bad)} ({', '.join(bad[:5])}).")
    return 0, _summary(ws, lines)


def cmd_ingest(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    sources = collect_sources(resolve_tmp(args.source, cwd)) if args.source else []
    with ws.lock():
        data = _ingest(ws, sources)
    files = data["ingest"]["files"]
    loaded = sum(1 for f in files if f["status"] in ("loaded", "accepted"))
    lines = [
        (
            f"Ingested {loaded} of {len(files)} file(s); {len(data['events'])} event(s), "
            f"{len(data['snapshots'])} snapshot(s)."
        ),
        f"Unresolved: {len(data['unresolved'])}.",
        f"Errors: {len(data['ingest']['errors'])}.",
    ]
    return (1 if data["ingest"]["errors"] else 0), _summary(ws, lines)


def cmd_answer(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    workflow.record_answer(ws, args.id, args.value, args.accept_file)
    with ws.lock():
        data = _ingest(ws, [])
    return 0, _summary(ws, [f"Answer saved. Unresolved remaining: {len(data['unresolved'])}."])


def cmd_accept(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        count = workflow.record_acceptances(ws, args.id, args.reason, args.note)
        remaining = len(inputcheck.open_findings(workflow.current_check(ws)))
    return 0, _summary(ws, [f"Accepted {count} finding(s). Open findings remaining: {remaining}."])


def cmd_validate(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    findings = ingest_mod.validate(ws)
    if ws.manifest()["status"] != "empty":
        findings += [
            {"level": "warn", "message": f"open {f['kind']} {f['account']} {f['message']} (id {f['id']})"}
            for f in inputcheck.open_findings(workflow.current_check(ws))
        ]
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]
    lines = [f"Validation: {len(errors)} error(s), {len(warns)} warning(s)."]
    lines += [f"- {f['level']}: {f['message'][:110]}" for f in (errors + warns)[:6]]
    return (1 if errors else 0), _summary(ws, lines)


def cmd_check_input(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    if args.start:
        with ws.lock():
            workflow.set_expected_start(ws, args.start)
    result = workflow.current_check(ws)
    ws.write("derived/input-check.json", result)
    pending = inputcheck.open_findings(result) or result["unresolved"]
    return (1 if pending else 0), _summary(ws, inputcheck.render(result))


def cmd_analyze(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        result = workflow.run_analyze(ws, _rates_loader(ws, offline=args.offline))
    pf = result["portfolio"]
    lines = [f"Analysed {len(result['accounts'])} account(s); checks: {result['check_counts']}."]
    if pf:
        lines.append(f"Consolidated value {pf['value_eur']} EUR at {pf['common_date']} (status {pf['value_status']}).")
    if result["excluded"]:
        lines.append(f"Excluded (no FX rate): {', '.join(e['account'] for e in result['excluded'])}.")
    if result["fx_notice"]:
        lines.append(f"FX notice: {result['fx_notice'][:90]}")
    return (1 if result["errors"] else 0), _summary(ws, lines)


def _classify_entries(args: argparse.Namespace, cwd: Path, known: list) -> list | None:
    """Entries to import from --import or the --set flags (merged over the known entry); None when neither is used."""
    given = {f: getattr(args, f) for f in SET_FIELDS if getattr(args, f, None)}
    if args.import_file and given:
        msg = "use either --import or the --isin/--security-class/... flags, not both"
        raise PmError(msg)
    if args.import_file:
        try:
            return json.loads(resolve_tmp(args.import_file, cwd).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            msg = f"cannot read {args.import_file}: {err}"
            raise PmError(msg) from err
    if not given:
        return None
    if "isin" not in given:
        msg = "--isin is required to set a classification"
        raise PmError(msg)
    old = next((k for k in known if k["isin"] == given["isin"]), {})
    return [{**old, **given}]


def cmd_classify(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    known = ws.read("data/classifications.json", [])
    entries = _classify_entries(args, cwd, known)
    if entries is not None:
        valid, errors = classify_mod.validate(entries)
        if errors:
            rejected = [f"Rejected: {len(errors)} problem(s); nothing imported.", *[f"- {e[:110]}" for e in errors[:6]]]
            return 1, _summary(ws, rejected)
        ws.write_tracked("data/classifications.json", classify_mod.merge(known, valid))
        return 0, _summary(ws, [f"Imported {len(valid)} classification(s)."])
    analysis = ws.read("derived/analysis.json")
    if analysis is None:
        msg = "no analysis yet: run `pm analyze` first"
        raise PmError(msg)
    securities = [r for a in analysis["accounts"].values() for r in a["securities"]]
    pending = classify_mod.queue(securities, known)
    ws.write("derived/classify-queue.json", pending)
    return 0, _summary(
        ws,
        [f"Classification queue: {len(pending)} instrument(s) (identifiers only) in derived/classify-queue.json."],
    )


def _offline_chart(_ticker: str) -> tuple[dict | None, str]:
    return None, "offline mode"


def cmd_benchmark(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        info = workflow.run_benchmark(ws, args.ticker, _offline_chart if args.offline else download_chart)
    line = (
        f"Benchmark {info['ticker']}: {info['months']} monthly close(s) in {info['currency']} "
        f"from the {info['source']}. Run `pm report` to see the comparison."
    )
    return 0, _summary(ws, [line])


def _report_result(ws: Workspace, *, offline: bool) -> Result:
    if refusal := workflow.blocked(ws, "Report"):
        return 1, _summary(ws, [refusal])
    analysis, files, unresolved = workflow.run_report(ws, _rates_loader(ws, offline=offline))
    lines = reports.summary(analysis, unresolved, len(files), f"{SKILL_DIR}/{ws.root.name}/")
    if not workflow.configured_ticker(ws):
        lines.append(
            "No benchmark yet: ask the user whether to compare with a market ETF, then run "
            "`pm benchmark --ticker <ticker>` (only the ticker is sent to Yahoo Finance)."
        )
    return (1 if analysis["errors"] else 0), _summary(ws, lines)


def cmd_report(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        return _report_result(ws, offline=args.offline)


def cmd_export(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        if refusal := workflow.blocked(ws, "Export"):
            return 1, _summary(ws, [refusal])
        data = {k: ws.read(f"data/{k}.json") for k in workflow.LEDGER_FILES}
        if any(v is None for v in data.values()):
            msg = "nothing ingested yet: run `pm ingest` first"
            raise PmError(msg)
        unresolved = ws.read("data/unresolved.json", [])
        errors = ws.read("data/ingest.json", {}).get("errors", [])
        files = export_pp.build(data, decimal_comma=args.decimal_comma)
        problems = export_pp.verify(data, files)
        ws.clean_outputs(EXPORT_DIR, "*", {f"{EXPORT_DIR}/{name}" for name in files})
        for name, text in files.items():
            ws.write_text(f"{EXPORT_DIR}/{name}", text)
    modes = {a["id"]: a["mode"] for a in data["accounts"]["accounts"]}
    skipped = sorted(k for k, mode in modes.items() if mode != "transactions")
    lines = [f"Exported {len(data['events'])} event(s) as {len(files)} file(s) to {EXPORT_DIR}/."]
    if skipped:
        lines.append(f"Value-only accounts (snapshots, no transactions): {', '.join(skipped)}.")
    if unresolved or errors:
        lines.append(
            f"WARNING: {len(unresolved)} unresolved record(s) and {len(errors)} ingest error(s): "
            "the export is incomplete; resolve them and export again."
        )
    lines += [f"ERROR: {p}; do not use these files." for p in problems]
    return (1 if unresolved or errors or problems else 0), _summary(ws, lines)


def cmd_run(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    if not ws.exists():
        ws.init()
    sources = collect_sources(resolve_tmp(args.source, cwd)) if args.source else []
    with ws.lock():
        manifest = ws.manifest()
        stale = manifest.get("calculation_version") != CALCULATION_VERSION
        if sources or manifest["status"] == "empty" or stale:
            _ingest(ws, sources)
        return _report_result(ws, offline=args.offline)


HANDLERS = {
    "portfolio-name": cmd_portfolio_name,
    "init": cmd_init,
    "inspect": cmd_inspect,
    "ingest": cmd_ingest,
    "answer": cmd_answer,
    "accept": cmd_accept,
    "validate": cmd_validate,
    "check-input": cmd_check_input,
    "analyze": cmd_analyze,
    "classify": cmd_classify,
    "benchmark": cmd_benchmark,
    "report": cmd_report,
    "export": cmd_export,
    "run": cmd_run,
}


def _portfolio_arg(sp: argparse.ArgumentParser) -> None:
    sp.add_argument(
        "--portfolio",
        "--name",
        dest="portfolio",
        default=DEFAULT_PORTFOLIO,
        help=(
            "portfolio name (alias --name); run folder .tmp/manage-investment-portfolio/<name>/ "
            f"(default {DEFAULT_PORTFOLIO})"
        ),
    )


def _source_arg(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--source", help="file or folder with statement PDFs, inside .tmp/")


def _offline_arg(sp: argparse.ArgumentParser) -> None:
    sp.add_argument(
        "--offline", action="store_true", help="do not download ECB rates; use the cache and statement rates only"
    )


def _export_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument(
        "--decimal-comma",
        action="store_true",
        help="write ',' decimals in Value, Shares, Fees, Taxes and Gross Amount (German number format)",
    )


def _classify_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--import", dest="import_file", help="JSON list of researched classifications, inside .tmp/")
    for field in SET_FIELDS:
        flag = "--security-name" if field == "name" else f"--{field.replace('_', '-')}"  # --name is the portfolio alias
        sp.add_argument(flag, dest=field, help=f"classification {field} for --isin")


def _answer_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--id", help="unresolved record id")
    sp.add_argument("--value", help="the user's answer")
    sp.add_argument("--accept-file", help="sha256 prefix of a rejected file to load anyway")


def _check_input_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--from", dest="start", help="first day the user expects the statements to cover (YYYY-MM-DD)")


def _accept_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--id", action="append", help="finding id from `pm check-input`; repeat for several")
    sp.add_argument("--reason", help="one of: " + ", ".join(acceptance.EVERY_REASON))
    sp.add_argument("--note", help=f"the user's own words, one line of at most {acceptance.MAX_NOTE} characters")


def _benchmark_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument(
        "--ticker", help="Yahoo Finance ticker of the benchmark ETF or index (e.g. IWDA.AS); default: config.yaml"
    )
    sp.add_argument("--offline", action="store_true", help="do not download; use the cached response only")


def _portfolio_name_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--source", required=True, help="file or folder with statement PDFs, inside .tmp/")


EXTRA_ARGS = {
    "portfolio-name": [_portfolio_name_args],
    "inspect": [_source_arg],
    "ingest": [_source_arg],
    "run": [_source_arg, _offline_arg],
    "analyze": [_offline_arg],
    "report": [_offline_arg],
    "export": [_export_args],
    "classify": [_classify_args],
    "benchmark": [_benchmark_args],
    "answer": [_answer_args],
    "check-input": [_check_input_args],
    "accept": [_accept_args],
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pm", description=(__doc__ or "").splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        sp = sub.add_parser(name, help=f"{name} the portfolio work dir")
        if name in WORK_COMMANDS:
            _portfolio_arg(sp)
        for add in EXTRA_ARGS.get(name, []):
            add(sp)
    return p


def run(argv: list[str], cwd: Path) -> Result:
    """Run a command; returns (exit_code, stdout_text)."""
    args = build_parser().parse_args(argv)
    try:
        return HANDLERS[args.command](args, cwd)
    except PmError as err:
        return 2, f"error: {err}"


def main(argv: list[str] | None = None) -> int:
    code, text = run(sys.argv[1:] if argv is None else argv, Path.cwd())
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
