"""Portfolio manager CLI: init, inspect, ingest, answer, analyze, classify, report, run, validate.

Exit codes: 0 ok, 1 validation failures found, 2 invalid input. Successful runs end with `results-path: ...`; errors print `error: ...`.
"""

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from portfolio_manager.adapters.connectors.ecb.ecb_rates import download_ecb, load_cached
from portfolio_manager.adapters.connectors.institutions import default_registry
from portfolio_manager.adapters.connectors.local_fs.workspace import Workspace, collect_sources, resolve_tmp, work_dir
from portfolio_manager.adapters.connectors.pdf.pdf_reader import read_pdf
from portfolio_manager.app import classify as classify_mod
from portfolio_manager.app import ingest as ingest_mod
from portfolio_manager.app import inspector
from portfolio_manager.app import report as report_mod
from portfolio_manager.app import workflow
from portfolio_manager.app.fx import Rates
from portfolio_manager.shared.errors import PmError

COMMANDS = ("init", "inspect", "ingest", "answer", "analyze", "classify", "report", "run", "validate")
Result = tuple[int, str]


def _ws(args: argparse.Namespace, cwd: Path) -> Workspace:
    return Workspace(work_dir(args.name, cwd))


def _need(ws: Workspace) -> None:
    if not ws.exists():
        msg = f"work dir not initialised: run `pm init --name <name>` first ({ws.root})"
        raise PmError(msg)


def _run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S")


def _summary(ws: Workspace, lines: list[str]) -> str:
    rel = f".tmp/{ws.root.name}/"
    return "\n".join([*lines, f"results-path: {rel}"])


def _rates_loader(ws: Workspace, offline: bool) -> Callable[[str], tuple[Rates, str]]:
    def offline_downloader() -> tuple[str, str]:
        return "", "offline mode"

    downloader = offline_downloader if offline else download_ecb

    def load(needed_until: str) -> tuple[Rates, str]:
        return load_cached(ws.path("cache/ecb-hist.csv"), needed_until, downloader)

    return load


def _ingest(ws: Workspace, sources: list[Path]) -> dict:
    return ingest_mod.ingest(ws, sources, _run_id(), read_pdf, default_registry())


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
        f"Ingested {loaded} of {len(files)} file(s); {len(data['events'])} event(s), {len(data['snapshots'])} snapshot(s).",
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


def cmd_validate(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    findings = ingest_mod.validate(ws)
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]
    lines = [f"Validation: {len(errors)} error(s), {len(warns)} warning(s)."]
    lines += [f"- {f['level']}: {f['message'][:110]}" for f in (errors + warns)[:6]]
    return (1 if errors else 0), _summary(ws, lines)


def cmd_analyze(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        result = workflow.run_analyze(ws, _rates_loader(ws, args.offline))
    pf = result["portfolio"]
    lines = [f"Analysed {len(result['accounts'])} account(s); checks: {result['check_counts']}."]
    if pf:
        lines.append(f"Consolidated value {pf['value_eur']} EUR at {pf['common_date']} (status {pf['value_status']}).")
    if result["excluded"]:
        lines.append(f"Excluded (no FX rate): {', '.join(e['account'] for e in result['excluded'])}.")
    if result["fx_notice"]:
        lines.append(f"FX notice: {result['fx_notice'][:90]}")
    return (1 if result["errors"] else 0), _summary(ws, lines)


def cmd_classify(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    known = ws.read("data/classifications.json", [])
    if args.import_file:
        try:
            entries = json.loads(resolve_tmp(args.import_file, cwd).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            msg = f"cannot read {args.import_file}: {err}"
            raise PmError(msg) from err
        valid, errors = classify_mod.validate(entries)
        if errors:
            rejected = [f"Rejected: {len(errors)} problem(s); nothing imported.", *[f"- {e[:110]}" for e in errors[:6]]]
            return 1, _summary(ws, rejected)
        ws.write("data/classifications.json", classify_mod.merge(known, valid))
        return 0, _summary(ws, [f"Imported {len(valid)} classification(s)."])
    analysis = ws.read("derived/analysis.json")
    if analysis is None:
        msg = "no analysis yet: run `pm analyze` first"
        raise PmError(msg)
    assets = [r for a in analysis["accounts"].values() for r in a["assets"]]
    pending = classify_mod.queue(assets, known)
    ws.write("derived/classify-queue.json", pending)
    return 0, _summary(
        ws,
        [f"Classification queue: {len(pending)} instrument(s) (identifiers only) in derived/classify-queue.json."],
    )


def _report_result(ws: Workspace, offline: bool) -> Result:
    analysis, files, unresolved = workflow.run_report(ws, _rates_loader(ws, offline))
    lines = report_mod.summary(analysis, unresolved, len(files), f".tmp/{ws.root.name}/")
    return (1 if analysis["errors"] else 0), _summary(ws, lines)


def cmd_report(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        return _report_result(ws, args.offline)


def cmd_run(args: argparse.Namespace, cwd: Path) -> Result:
    ws = _ws(args, cwd)
    if not ws.exists():
        ws.init()
    sources = collect_sources(resolve_tmp(args.source, cwd)) if args.source else []
    with ws.lock():
        if sources or ws.manifest()["status"] == "empty":
            _ingest(ws, sources)
        return _report_result(ws, args.offline)


HANDLERS = {
    "init": cmd_init,
    "inspect": cmd_inspect,
    "ingest": cmd_ingest,
    "answer": cmd_answer,
    "validate": cmd_validate,
    "analyze": cmd_analyze,
    "classify": cmd_classify,
    "report": cmd_report,
    "run": cmd_run,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pm", description=(__doc__ or "").splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        sp = sub.add_parser(name, help=f"{name} the portfolio work dir")
        sp.add_argument("--name", default="main", help="work dir name: .tmp/portfolio-manager-<name>/")
        if name in ("inspect", "ingest", "run"):
            sp.add_argument("--source", help="file or folder with statement PDFs, inside .tmp/")
        if name in ("analyze", "run", "report"):
            sp.add_argument(
                "--offline",
                action="store_true",
                help="do not download ECB rates; use the cache and statement rates only",
            )
        if name == "classify":
            sp.add_argument("--import", dest="import_file", help="JSON list of researched classifications, inside .tmp/")
        if name == "answer":
            sp.add_argument("--id", help="unresolved record id")
            sp.add_argument("--value", help="the user's answer")
            sp.add_argument("--accept-file", help="sha256 prefix of a rejected file to load anyway")
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
