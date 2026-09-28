#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11", "openpyxl>=3.1"]
# ///
"""Stage, discover and normalize source files of one analysis (.tmp/<id>/).

Subcommands:
  stage <input> --id ID      copy a file, folder or zip into .tmp/<id>/sources/ (tree kept, duplicates skipped)
  discover --id ID           per file: module, text layer, account, period; groups, conflicts, gaps, period proposal
  run <source> --id ID       write .tmp/<id>/normalized/<name>-<ext>.md with an institution module or --mapping
Sources are never modified. Exit codes: 0 ok, 2 invalid input or no known format (use the LLM path).
"""

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import institutions
import ledger
import mapping as mapping_mod
import sourcedoc
from ledger import Ledger, LedgerError
from textutil import month_end, months, slug

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
ARTIFACT = re.compile(r"\.(?:snapshot|grounding|plan|user\d*)\.json$|^(?:answers|hidden|mapping|staging)\.json$")
MAX_ZIP_FILES = 200
MAX_ZIP_BYTES = 200 * 1024 * 1024
LLM_ROWS_LIMIT = 200
PERIOD_MONTHS = 12


def run_dir(cwd: Path, run_id: str) -> Path:
    if not ID_RE.match(run_id):
        raise LedgerError(f"--id must match {ID_RE.pattern}: {run_id!r}")
    return (cwd / ".tmp" / run_id).resolve()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_rel(parts: list) -> Path:
    clean = []
    for part in parts:
        stem, dot, ext = part.rpartition(".")
        clean.append(f"{slug(stem)}.{ext.lower()}" if dot and stem else slug(part))
    return Path(*clean)


class Stager:
    def __init__(self, dest: Path):
        self.dest, self.staged, self.skipped, self.hashes = dest, [], [], {}
        for f in sorted(dest.rglob("*")) if dest.exists() else []:
            if f.is_file():
                self.hashes[sha256(f.read_bytes())] = str(f.relative_to(dest))

    def add(self, origin: str, rel_parts: list, data: bytes) -> None:
        name = rel_parts[-1]
        if name.startswith(".") or "__MACOSX" in rel_parts:
            self.skipped.append({"path": origin, "reason": "hidden or system file"})
            return
        if ARTIFACT.search(name):
            self.skipped.append({"path": origin, "reason": "artifact of a previous analysis"})
            return
        if Path(name).suffix.lower() not in sourcedoc.SUPPORTED:
            self.skipped.append({"path": origin, "reason": f"unsupported format {Path(name).suffix or '(none)'}"})
            return
        digest = sha256(data)
        if digest in self.hashes:
            self.skipped.append({"path": origin, "reason": f"duplicate of {self.hashes[digest]}"})
            return
        target = self.dest / safe_rel(rel_parts)
        n = 2
        while target.exists():
            target = target.with_name(f"{target.stem.rsplit('--', 1)[0]}--{n}{target.suffix}")
            n += 1
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rel = str(target.relative_to(self.dest))
        self.hashes[digest] = rel
        self.staged.append({"source": origin, "path": rel, "sha256": digest})

    def add_zip(self, origin: str, rel_parts: list, path: Path) -> None:
        base = rel_parts[:-1] + [Path(rel_parts[-1]).stem]
        with zipfile.ZipFile(path) as archive:
            members = [m for m in archive.infolist() if not m.is_dir()]
            total = sum(m.file_size for m in members)
            if len(members) > MAX_ZIP_FILES or total > MAX_ZIP_BYTES:
                self.skipped.append({"path": origin, "reason": f"zip over limits ({len(members)} files, {total} bytes;"
                                     f" max {MAX_ZIP_FILES} files, {MAX_ZIP_BYTES} bytes)"})
                return
            for m in members:
                parts = [p for p in m.filename.replace("\\", "/").split("/") if p]
                where = f"{origin}!{m.filename}"
                if m.filename.startswith("/") or ".." in parts or not parts or ":" in parts[0]:
                    self.skipped.append({"path": where, "reason": "unsafe path in zip"})
                elif parts[-1].lower().endswith(".zip"):
                    self.skipped.append({"path": where, "reason": "nested zip not extracted"})
                else:
                    self.add(where, base + parts, archive.read(m))


def cmd_stage(args, cwd: Path) -> dict:
    source = (cwd / args.input).resolve()
    if not source.exists():
        raise LedgerError(f"input does not exist: {source}")
    root = run_dir(cwd, args.id)
    dest = root / "sources"
    if source == root or root in source.parents:
        raise LedgerError("input must not be inside the analysis folder")
    stager = Stager(dest)
    files = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.is_file())
    for f in files:
        rel = [f.name] if source.is_file() else list(f.relative_to(source).parts)
        origin = str(f.relative_to(source.parent))
        if f.suffix.lower() == ".zip":
            try:
                stager.add_zip(origin, rel, f)
            except zipfile.BadZipFile:
                stager.skipped.append({"path": origin, "reason": "corrupt zip"})
        else:
            stager.add(origin, rel, f.read_bytes())
    result = {"id": args.id, "sources": str(dest.relative_to(cwd.resolve())), "staged": stager.staged,
              "skipped": stager.skipped}
    root.mkdir(parents=True, exist_ok=True)
    log = root / "staging.json"
    history = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    log.write_text(json.dumps(history + [result], ensure_ascii=False, indent=1), encoding="utf-8")
    return result


def describe(path: Path, rel: str) -> dict:
    info = {"path": rel, "sha256": sha256(path.read_bytes())}
    try:
        doc = sourcedoc.load(path)
    except LedgerError as err:
        return {**info, "status": "error", "message": str(err)}
    info.update(kind=doc.kind, text=doc.has_text, encrypted=doc.encrypted)
    module = None if doc.encrypted else institutions.find(doc)
    if module is None:
        info["status"] = ("encrypted" if doc.encrypted else "llm-image" if doc.kind == "image"
                          else "mapping" if doc.kind == "table" else "llm" if doc.has_text or doc.kind == "llm-only"
                          else "no-text")
        info["layout"] = layout_signature(doc)
        if doc.table:
            info["header"] = doc.table[0][:12]
        return info
    info.update(status="module", module=module.NAME)
    try:
        meta, rows, notes = module.parse(doc, {"discover": True})
    except LedgerError as err:
        return {**info, "status": "error", "message": str(err)}
    dates = sorted(r.date for r in rows)
    info.update(bank=meta.get("bank"), account=meta.get("iban", "unknown"), rows=len(rows), notes=notes,
                period=meta.get("period") or (f"{dates[0]}..{dates[-1]}" if dates else "unknown"))
    return info


def layout_signature(doc) -> str:
    if doc.table:
        return "table:" + "|".join(doc.table[0][:8])
    first = next((line for line in doc.lines() if line.strip()), "")
    return "text:" + re.sub(r"\d", "9", first)[:60]


def propose_period(groups: dict) -> str:
    """The last PERIOD_MONTHS full months ending at the latest full month any account covers."""
    ends = []
    for files in groups.values():
        periods = [f["period"] for f in files if ".." in f.get("period", "")]
        if periods:
            ends.append(max(date.fromisoformat(p.partition("..")[2]) for p in periods))
    if not ends:
        return "unknown"
    end = max(ends)
    if end != month_end(end):
        end = end.replace(day=1) - timedelta(days=1)
    start = end.replace(day=1)
    for _ in range(PERIOD_MONTHS - 1):
        start = (start - timedelta(days=1)).replace(day=1)
    return f"{start.isoformat()}..{end.isoformat()}"


def cmd_discover(args, cwd: Path) -> dict:
    src = run_dir(cwd, args.id) / "sources"
    if not src.is_dir():
        raise LedgerError(f"nothing staged; run: normalize.py stage <input> --id {args.id}")
    files = [describe(p, str(p.relative_to(src))) for p in sorted(src.rglob("*")) if p.is_file()]
    groups = {}
    for f in files:
        if f.get("account"):
            groups.setdefault(f"{f.get('bank') or f.get('module')}:{f['account']}", []).append(f)
    conflicts, gaps, overlaps = [], [], []
    for key, members in groups.items():
        dated = sorted((f for f in members if ".." in f.get("period", "")), key=lambda f: f["period"])
        for i, a in enumerate(dated):
            for b in dated[i + 1:]:
                if a["period"] == b["period"] and a["sha256"] != b["sha256"]:
                    conflicts.append({"account": key, "period": a["period"], "files": [a["path"], b["path"]]})
                elif a["period"].partition("..")[2] >= b["period"].partition("..")[0]:
                    overlaps.append({"account": key, "files": [a["path"], b["path"]]})
        if dated:
            covered = set().union(*(months(f["period"]) for f in dated))
            wanted = months(f"{dated[0]['period'][:10]}..{max(f['period'][12:] for f in dated)}")
            missing = sorted(wanted - covered)
            if missing:
                gaps.append({"account": key, "missing-months": missing})
    layouts = {}
    for f in files:
        if f.get("layout"):
            layouts.setdefault(f["layout"], []).append(f["path"])
    suggest = [{"layout": k, "files": v} for k, v in layouts.items() if len(v) >= 2]
    proposed = propose_period(groups)
    not_covered = []
    if proposed != "unknown":
        for key, members in groups.items():
            covered = set().union(set(), *(months(f["period"]) for f in members if ".." in f.get("period", "")))
            missing = sorted(months(proposed) - covered)
            if missing:
                not_covered.append({"account": key, "months": missing})
    return {"id": args.id, "files": files, "accounts": {k: [f["path"] for f in v] for k, v in groups.items()},
            "conflicts": conflicts, "overlaps": overlaps, "gaps": gaps, "suggest-module": suggest,
            "proposed-period": proposed, "not-covered": not_covered}


def output_for(root: Path, rel: Path) -> Path:
    stem = "-".join(slug(p) for p in rel.with_suffix("").parts)
    return root / "normalized" / f"{stem}-{rel.suffix.lower().lstrip('.')}.md"


def parse_sets(items: list) -> dict:
    sets = {}
    for item in items:
        key, _, value = item.partition("=")
        if key not in ledger.META_KEYS[1:] or not value:
            raise LedgerError(f"invalid --set {item!r}; keys: {', '.join(ledger.META_KEYS[1:])}")
        sets[key] = value
    return sets


def cmd_run(args, cwd: Path) -> dict:
    root = run_dir(cwd, args.id)
    src = (root / "sources" / args.source).resolve()
    if root / "sources" not in src.parents or not src.is_file():
        raise LedgerError(f"source not found under {root / 'sources'}: {args.source}")
    rel = src.relative_to(root / "sources")
    out = output_for(root, rel)
    if out.exists() and not args.force:
        raise LedgerError(f"{out.name} exists; reuse it or pass --force")
    sets = parse_sets(args.set)
    doc = sourcedoc.load(src)
    if doc.encrypted:
        raise LedgerError("PDF is password protected; ask the user for an unlocked copy")
    if args.mapping:
        spec = json.loads(ledger.resolve_tmp(args.mapping, cwd).read_text(encoding="utf-8"))
        meta, rows, notes = mapping_mod.apply(doc, spec)
        normalizer = "mapping"
    else:
        module = institutions.by_name(args.module) if args.module else institutions.find(doc)
        if module is None:
            raise LedgerError(unknown_hint(doc))
        meta, rows, notes = module.parse(doc, sets)
        normalizer = f"module:{module.NAME}"
    base = {"source": str(src.relative_to(cwd.resolve())), "normalizer": normalizer, "bank": "unknown",
            "account-type": "unknown", "account-holder": "unknown", "iban": "unknown", "currency": "unknown",
            "period": "unknown", "opening-balance": "none", "closing-balance": "none"}
    base.update(meta)
    base.update(sets)
    if base["period"] == "unknown" and rows:
        dates = sorted(r.date for r in rows)
        base["period"] = f"{dates[0]}..{dates[-1]}"
    out.parent.mkdir(parents=True, exist_ok=True)
    ledger.write(out, Ledger(base, rows))
    return {"output": str(out.relative_to(cwd.resolve())), "normalizer": normalizer, "rows": len(rows),
            "sum": ledger.format_value(sum((r.value for r in rows), Decimal(0))), "meta": base, "notes": notes}


def unknown_hint(doc) -> str:
    if doc.kind == "table":
        return "no institution module matched; write a mapping.json and pass --mapping (references/normalized-format.md)"
    if doc.kind == "image":
        return "image source; transcribe with the LLM path and set normalizer: llm-image"
    if doc.kind == "llm-only":
        return (f"{doc.ext} is not read by scripts; if it has more than {LLM_ROWS_LIMIT} rows ask for a CSV/XLSX"
                " re-export, otherwise transcribe with the LLM path (normalizer: llm)")
    if not doc.has_text:
        return "no text layer (scanned?); transcribe with the LLM path and set normalizer: llm-image"
    return "no institution module matched; transcribe with the LLM path (normalizer: llm)"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage", help="copy input files into .tmp/<id>/sources/")
    p.add_argument("input", help="file, folder or zip (read only)")
    p = sub.add_parser("discover", help="describe staged files and propose the analysis period")
    p = sub.add_parser("run", help="normalize one staged file")
    p.add_argument("source", help="path relative to .tmp/<id>/sources/")
    p.add_argument("--module", help="force an institution module by name")
    p.add_argument("--mapping", help="mapping JSON inside .tmp/ for unknown tables")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override a header field")
    p.add_argument("--force", action="store_true", help="overwrite an existing normalized file")
    for p in sub.choices.values():
        p.add_argument("--id", required=True, help="analysis id, e.g. transactions-2026-09-28")
    args = parser.parse_args(argv)
    try:
        result = {"stage": cmd_stage, "discover": cmd_discover, "run": cmd_run}[args.cmd](args, Path.cwd())
    except (LedgerError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    except Exception as err:  # noqa: BLE001 - third-party parsers raise many types for corrupt files
        print(f"error: cannot read {getattr(args, 'source', '')}: {type(err).__name__}: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
