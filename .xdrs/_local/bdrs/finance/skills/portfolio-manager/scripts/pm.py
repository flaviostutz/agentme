#!/usr/bin/env python3
# Runtime: uv run --with pymupdf --with pyyaml python pm.py <command> ... (Python >=3.11); writes only under <cwd>/.tmp/.
"""Portfolio manager CLI: init, inspect, ingest, answer, analyze, classify, report, run, validate.

Exit codes: 0 ok, 1 validation failures found, 2 invalid input. Successful runs end with `results-path: ...`; errors print `error: ...`.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import analyze as analyze_mod
import classify as classify_mod
import fx
import ingest as ingest_mod
import report as report_mod
from sourcedoc import PmError
from store import Workspace, resolve_tmp, work_dir

COMMANDS = ("init", "inspect", "ingest", "answer", "analyze", "classify", "report", "run", "validate")


def _ws(args, cwd: Path) -> Workspace:
    return Workspace(work_dir(args.name, cwd))


def _need(ws: Workspace) -> None:
    if not ws.exists():
        raise PmError(f"work dir not initialised: run `pm.py init --name <name>` first ({ws.root})")


def _run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S")


def _summary(ws: Workspace, lines: list) -> str:
    rel = f".tmp/{ws.root.name}/"
    return "\n".join([*lines, f"results-path: {rel}"])


def cmd_init(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    created = ws.init()
    return 0, _summary(ws, ["Work dir created." if created else "Work dir already exists; nothing overwritten."])


def cmd_inspect(args, cwd: Path) -> tuple:
    import inspector
    ws = _ws(args, cwd)
    _need(ws)
    sources = ingest_mod.collect_sources(resolve_tmp(args.source, cwd))
    infos = [inspector.inspect_pdf(p) for p in sources]
    ws.write("inspect.json", infos)
    bad = [i["file"] for i in infos if i["status"] != "ok"]
    lines = [f"Inspected {len(infos)} PDF file(s); structure only (no values) saved to inspect.json."]
    if bad:
        lines.append(f"Unreadable or locked: {len(bad)} ({', '.join(bad[:5])}).")
    return 0, _summary(ws, lines)


def cmd_ingest(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    sources = ingest_mod.collect_sources(resolve_tmp(args.source, cwd)) if args.source else []
    with ws.lock():
        data = ingest_mod.ingest(ws, sources, _run_id())
    files = data["ingest"]["files"]
    loaded = sum(1 for f in files if f["status"] in ("loaded", "accepted"))
    lines = [f"Ingested {loaded} of {len(files)} file(s); {len(data['events'])} event(s), {len(data['snapshots'])} snapshot(s).",
             f"Unresolved: {len(data['unresolved'])}.", f"Errors: {len(data['ingest']['errors'])}."]
    return (1 if data["ingest"]["errors"] else 0), _summary(ws, lines)


def cmd_answer(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    answers = ws.read("answers.json", {"accept_files": [], "answers": {}})
    manifest = ws.manifest()
    if args.accept_file:
        shas = [i["sha256"] for i in manifest.get("raw", {}).values() if i["sha256"].startswith(args.accept_file)]
        if len(shas) != 1:
            raise PmError(f"--accept-file must match exactly one ingested file (matched {len(shas)})")
        answers["accept_files"] = sorted(set(answers["accept_files"]) | {shas[0]})
    else:
        pending = {u["id"] for u in ws.read("data/unresolved.json", [])}
        if args.id not in pending:
            raise PmError(f"unknown unresolved id {args.id!r}; pending ids: {', '.join(sorted(pending)[:10]) or 'none'}")
        if not args.value:
            raise PmError("--value is required with --id")
        answers["answers"][args.id] = args.value
    ws.write("answers.json", answers)
    with ws.lock():
        data = ingest_mod.ingest(ws, [], _run_id())
    return 0, _summary(ws, [f"Answer saved. Unresolved remaining: {len(data['unresolved'])}."])


def cmd_validate(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    findings = ingest_mod.validate(ws)
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]
    lines = [f"Validation: {len(errors)} error(s), {len(warns)} warning(s)."]
    lines += [f"- {f['level']}: {f['message'][:110]}" for f in (errors + warns)[:6]]
    return (1 if errors else 0), _summary(ws, lines)


def run_analyze(ws: Workspace, offline: bool) -> dict:
    """Recompute the derived analysis from the canonical ledger (never from cached results)."""
    data = {k: ws.read(f"data/{k}.json") for k in ("accounts", "events", "snapshots", "references")}
    if any(v is None for v in data.values()):
        raise PmError("nothing ingested yet: run `pm.py ingest` first")
    last = max((s["date"] for s in data["snapshots"]), default="1970-01-01")
    downloader = (lambda: ("", "offline mode")) if offline else fx.download_ecb
    rates, notice = fx.load_cached(ws.path("cache/ecb-hist.csv"), last, downloader)
    manifest = ws.manifest()
    manifest["status"] = "analyzing"
    ws.save_manifest(manifest)
    result = analyze_mod.analyze(data, rates)
    result["fx_notice"] = notice
    ws.write("derived/analysis.json", result)
    manifest["status"] = "analyzed"
    ws.save_manifest(manifest)
    return result


def cmd_analyze(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        result = run_analyze(ws, args.offline)
    pf = result["portfolio"]
    lines = [f"Analysed {len(result['accounts'])} account(s); checks: {result['check_counts']}."]
    if pf:
        lines.append(f"Consolidated value {pf['value_eur']} EUR at {pf['common_date']} (status {pf['value_status']}).")
    if result["excluded"]:
        lines.append(f"Excluded (no FX rate): {', '.join(e['account'] for e in result['excluded'])}.")
    if result["fx_notice"]:
        lines.append(f"FX notice: {result['fx_notice'][:90]}")
    return (1 if result["errors"] else 0), _summary(ws, lines)


def cmd_classify(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    known = ws.read("data/classifications.json", [])
    if args.import_file:
        try:
            entries = json.loads(resolve_tmp(args.import_file, cwd).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            raise PmError(f"cannot read {args.import_file}: {err}") from err
        valid, errors = classify_mod.validate(entries)
        if errors:
            return 1, _summary(ws, [f"Rejected: {len(errors)} problem(s); nothing imported.", *[f"- {e[:110]}" for e in errors[:6]]])
        ws.write("data/classifications.json", classify_mod.merge(known, valid))
        return 0, _summary(ws, [f"Imported {len(valid)} classification(s)."])
    analysis = ws.read("derived/analysis.json")
    if analysis is None:
        raise PmError("no analysis yet: run `pm.py analyze` first")
    assets = [r for a in analysis["accounts"].values() for r in a["assets"]]
    pending = classify_mod.queue(assets, known)
    ws.write("derived/classify-queue.json", pending)
    return 0, _summary(ws, [f"Classification queue: {len(pending)} instrument(s) (identifiers only) in derived/classify-queue.json."])


def run_report(ws: Workspace, offline: bool) -> tuple:
    analysis = run_analyze(ws, offline)
    unresolved = ws.read("data/unresolved.json", [])
    files = report_mod.render(analysis, unresolved, ws.read("data/classifications.json", []))
    for sub, pattern in (("reports", "*.md"), ("graphs", "*.mmd")):
        for old in ws.path(sub).glob(pattern):
            if f"{sub}/{old.name}" not in files:
                old.unlink()
    for rel, text in files.items():
        ws.write_text(rel, text)
    return analysis, files, unresolved


def cmd_report(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    _need(ws)
    with ws.lock():
        analysis, files, unresolved = run_report(ws, args.offline)
    return (1 if analysis["errors"] else 0), _summary(ws, report_mod.summary(analysis, unresolved, len(files), f".tmp/{ws.root.name}/"))


def cmd_run(args, cwd: Path) -> tuple:
    ws = _ws(args, cwd)
    if not ws.exists():
        ws.init()
    sources = ingest_mod.collect_sources(resolve_tmp(args.source, cwd)) if args.source else []
    with ws.lock():
        if sources or ws.manifest()["status"] == "empty":
            ingest_mod.ingest(ws, sources, _run_id())
        analysis, files, unresolved = run_report(ws, args.offline)
    return (1 if analysis["errors"] else 0), _summary(ws, report_mod.summary(analysis, unresolved, len(files), f".tmp/{ws.root.name}/"))


HANDLERS = {"init": cmd_init, "inspect": cmd_inspect, "ingest": cmd_ingest, "answer": cmd_answer, "validate": cmd_validate,
            "analyze": cmd_analyze, "classify": cmd_classify, "report": cmd_report, "run": cmd_run}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pm.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        sp = sub.add_parser(name, help=f"{name} the portfolio work dir")
        sp.add_argument("--name", default="main", help="work dir name: .tmp/portfolio-manager-<name>/")
        if name in ("inspect", "ingest", "run"):
            sp.add_argument("--source", help="file or folder with statement PDFs, inside .tmp/")
        if name in ("analyze", "run", "report"):
            sp.add_argument("--offline", action="store_true", help="do not download ECB rates; use the cache and statement rates only")
        if name == "classify":
            sp.add_argument("--import", dest="import_file", help="JSON list of researched classifications, inside .tmp/")
        if name == "answer":
            sp.add_argument("--id", help="unresolved record id")
            sp.add_argument("--value", help="the user's answer")
            sp.add_argument("--accept-file", help="sha256 prefix of a rejected file to load anyway")
    return p


def main(argv: list, cwd: Path) -> tuple:
    """Run a command; returns (exit_code, stdout_text)."""
    args = build_parser().parse_args(argv)
    handler = HANDLERS.get(args.command)
    try:
        if handler is None:
            raise PmError(f"command not available yet: {args.command}")
        return handler(args, cwd)
    except PmError as err:
        return 2, f"error: {err}"


if __name__ == "__main__":
    code, text = main(sys.argv[1:], Path.cwd())
    print(text)
    sys.exit(code)
