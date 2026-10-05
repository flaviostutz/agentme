"""Stage, discover and normalize source files of one analysis (working files in .tmp/<id>/.work/).

stage     copy a file, folder or zip into .tmp/<id>/.work/sources/ (tree kept, duplicates skipped)
discover  per file: module, text layer, account, period; groups, conflicts, gaps, period proposal
rename    move .tmp/<id>/ to .tmp/<new>/ (before any file is normalized)
run       write .tmp/<id>/.work/normalized/<name>-<ext>.md with an institution module or a mapping
Sources are never modified.
"""

import hashlib
import json
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app import mapping as mapping_mod
from analyse_account_transactions.app.jsonfile import read_json, write_json
from analyse_account_transactions.app.ports import InstitutionRegistry, Sources, StagingFs
from analyse_account_transactions.app.textutil import month_end, months, slug
from analyse_account_transactions.shared.constants import META_KEYS, SUPPORTED
from analyse_account_transactions.shared.errors import CorruptArchiveError, LedgerError
from analyse_account_transactions.shared.models import Doc, Ledger, ParseResult
from analyse_account_transactions.shared.values import format_value

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
ARTIFACT = re.compile(r"\.(?:snapshot|grounding|plan|user\d*)\.json$|^(?:answers|hidden|mapping|staging)\.json$")
MAX_ZIP_FILES = 200
MAX_ZIP_BYTES = 200 * 1024 * 1024
LLM_ROWS_LIMIT = 200
PERIOD_MONTHS = 12
PERIOD_RANGE_LEN = 10  # "YYYY-MM-DD"
PERIOD_END_FROM = 12  # offset of the end date in "YYYY-MM-DD..YYYY-MM-DD"
MIN_LAYOUT_FILES = 2


def analysis_dir(fs: StagingFs, run_id: str) -> Path:
    if not ID_RE.match(run_id):
        msg = f"--id must match {ID_RE.pattern}: {run_id!r}"
        raise LedgerError(msg)
    return fs.analysis_root(run_id)


def run_dir(fs: StagingFs, run_id: str) -> Path:
    return analysis_dir(fs, run_id) / ".work"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_rel(parts: list[str]) -> Path:
    clean = []
    for part in parts:
        stem, dot, ext = part.rpartition(".")
        clean.append(f"{slug(stem)}.{ext.lower()}" if dot and stem else slug(part))
    return Path(*clean)


class Stager:
    def __init__(self, fs: StagingFs, dest: Path) -> None:
        self.fs, self.dest = fs, dest
        self.staged: list[dict[str, Any]] = []
        self.skipped: list[dict[str, Any]] = []
        self.hashes: dict[str, str] = {}
        for f in fs.list_files(dest):
            self.hashes[sha256(fs.read_bytes(f))] = str(f.relative_to(dest))

    def add(self, origin: str, rel_parts: list[str], data: bytes) -> None:
        name = rel_parts[-1]
        if any(p.startswith(".") for p in rel_parts) or "__MACOSX" in rel_parts:
            self.skipped.append({"path": origin, "reason": "hidden or system file"})
            return
        if ARTIFACT.search(name):
            self.skipped.append({"path": origin, "reason": "artifact of a previous analysis"})
            return
        if Path(name).suffix.lower() not in SUPPORTED:
            self.skipped.append({"path": origin, "reason": f"unsupported format {Path(name).suffix or '(none)'}"})
            return
        digest = sha256(data)
        if digest in self.hashes:
            self.skipped.append({"path": origin, "reason": f"duplicate of {self.hashes[digest]}"})
            return
        target = self.dest / safe_rel(rel_parts)
        n = 2
        while self.fs.exists(target):
            target = target.with_name(f"{target.stem.rsplit('--', 1)[0]}--{n}{target.suffix}")
            n += 1
        self.fs.write_bytes(target, data)
        rel = str(target.relative_to(self.dest))
        self.hashes[digest] = rel
        self.staged.append({"source": origin, "path": rel, "sha256": digest})

    def add_zip(self, origin: str, rel_parts: list[str], path: Path) -> None:
        base = [*rel_parts[:-1], Path(rel_parts[-1]).stem]
        members = self.fs.list_zip(path)
        total = sum(m.file_size for m in members)
        if len(members) > MAX_ZIP_FILES or total > MAX_ZIP_BYTES:
            reason = (
                f"zip over limits ({len(members)} files, {total} bytes;"
                f" max {MAX_ZIP_FILES} files, {MAX_ZIP_BYTES} bytes)"
            )
            self.skipped.append({"path": origin, "reason": reason})
            return
        for m in members:
            parts = [p for p in m.filename.replace("\\", "/").split("/") if p]
            where = f"{origin}!{m.filename}"
            if m.filename.startswith("/") or ".." in parts or not parts or ":" in parts[0]:
                self.skipped.append({"path": where, "reason": "unsafe path in zip"})
            elif parts[-1].lower().endswith(".zip"):
                self.skipped.append({"path": where, "reason": "nested zip not extracted"})
            else:
                self.add(where, base + parts, self.fs.read_zip_entry(path, m.filename))


def stage(fs: StagingFs, input_arg: str, run_id: str) -> dict[str, Any]:
    source = fs.resolve_input(input_arg)
    root = run_dir(fs, run_id)
    dest = root / "sources"
    if source == root.parent or root.parent in source.parents:
        msg = "input must not be inside the analysis folder"
        raise LedgerError(msg)
    stager = Stager(fs, dest)
    files = [source] if fs.is_file(source) else fs.list_files(source)
    for f in files:
        rel = [f.name] if fs.is_file(source) else list(f.relative_to(source).parts)
        origin = str(f.relative_to(source.parent))
        if f.suffix.lower() == ".zip":
            try:
                stager.add_zip(origin, rel, f)
            except CorruptArchiveError:
                stager.skipped.append({"path": origin, "reason": "corrupt zip"})
        else:
            stager.add(origin, rel, fs.read_bytes(f))
    result = {"id": run_id, "sources": fs.rel(dest), "staged": stager.staged, "skipped": stager.skipped}
    log = root / "staging.json"
    history = read_json(fs, log) or []
    write_json(fs, log, [*history, result])
    return result


def layout_signature(doc: Doc) -> str:
    if doc.table:
        return "table:" + "|".join(doc.table[0][:8])
    first = next((line for line in doc.lines() if line.strip()), "")
    return "text:" + re.sub(r"\d", "9", first)[:60]


def _fallback_status(doc: Doc) -> str:
    if doc.encrypted:
        return "encrypted"
    if doc.kind == "image":
        return "llm-image"
    if doc.kind == "table":
        return "mapping"
    return "llm" if doc.has_text or doc.kind == "llm-only" else "no-text"


def describe(fs: StagingFs, sources: Sources, registry: InstitutionRegistry, path: Path, rel: str) -> dict[str, Any]:
    info: dict[str, Any] = {"path": rel, "sha256": sha256(fs.read_bytes(path))}
    try:
        doc = sources.load(path)
    except LedgerError as err:
        return {**info, "status": "error", "message": str(err)}
    info.update(kind=doc.kind, text=doc.has_text, encrypted=doc.encrypted)
    module = None if doc.encrypted else registry.find(doc)
    if module is None:
        info["status"] = _fallback_status(doc)
        info["layout"] = layout_signature(doc)
        if doc.table:
            info["header"] = doc.table[0][:12]
        return info
    info.update(status="module", module=module.name)
    try:
        meta, rows, notes = module.parse(doc, {"discover": True})
    except LedgerError as err:
        return {**info, "status": "error", "message": str(err)}
    dates = sorted(r.date for r in rows)
    info.update(
        bank=meta.get("bank"),
        account=meta.get("iban", "unknown"),
        holder=meta.get("account-holder", "unknown"),
        rows=len(rows),
        notes=notes,
        period=meta.get("period") or (f"{dates[0]}..{dates[-1]}" if dates else "unknown"),
    )
    return info


def propose_period(groups: dict[str, list[dict[str, Any]]]) -> str:
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


def _account_issues(
    groups: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (conflicts, gaps, overlaps) per account group."""
    conflicts: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    overlaps: list[dict[str, Any]] = []
    for key, members in groups.items():
        dated = sorted((f for f in members if ".." in f.get("period", "")), key=lambda f: f["period"])
        for i, a in enumerate(dated):
            for b in dated[i + 1 :]:
                if a["period"] == b["period"] and a["sha256"] != b["sha256"]:
                    conflicts.append({"account": key, "period": a["period"], "files": [a["path"], b["path"]]})
                elif a["period"].partition("..")[2] >= b["period"].partition("..")[0]:
                    overlaps.append({"account": key, "files": [a["path"], b["path"]]})
        if dated:
            covered = set().union(*(months(f["period"]) for f in dated))
            first = dated[0]["period"][:PERIOD_RANGE_LEN]
            wanted = months(f"{first}..{max(f['period'][PERIOD_END_FROM:] for f in dated)}")
            missing = sorted(wanted - covered)
            if missing:
                gaps.append({"account": key, "missing-months": missing})
    return conflicts, gaps, overlaps


def discover(fs: StagingFs, sources: Sources, registry: InstitutionRegistry, run_id: str) -> dict[str, Any]:
    src = run_dir(fs, run_id) / "sources"
    if not fs.is_dir(src):
        msg = f"nothing staged; run: aat-normalize stage <input> --id {run_id}"
        raise LedgerError(msg)
    files = [describe(fs, sources, registry, p, str(p.relative_to(src))) for p in fs.list_files(src)]
    groups: dict[str, list[dict[str, Any]]] = {}
    for f in files:
        if f.get("account"):
            groups.setdefault(f"{f.get('bank') or f.get('module')}:{f['account']}", []).append(f)
    conflicts, gaps, overlaps = _account_issues(groups)
    layouts: dict[str, list[str]] = {}
    for f in files:
        if f.get("layout"):
            layouts.setdefault(f["layout"], []).append(f["path"])
    suggest = [{"layout": k, "files": v} for k, v in layouts.items() if len(v) >= MIN_LAYOUT_FILES]
    proposed = propose_period(groups)
    not_covered = []
    if proposed != "unknown":
        for key, members in groups.items():
            covered = set().union(set(), *(months(f["period"]) for f in members if ".." in f.get("period", "")))
            missing = sorted(months(proposed) - covered)
            if missing:
                not_covered.append({"account": key, "months": missing})
    return {
        "id": run_id,
        "files": files,
        "accounts": {k: [f["path"] for f in v] for k, v in groups.items()},
        "conflicts": conflicts,
        "overlaps": overlaps,
        "gaps": gaps,
        "suggest-module": suggest,
        "proposed-period": proposed,
        "not-covered": not_covered,
    }


def rename(fs: StagingFs, run_id: str, new_id: str) -> dict[str, Any]:
    old, new = analysis_dir(fs, run_id), analysis_dir(fs, new_id)
    if not fs.is_dir(old):
        msg = f"analysis folder does not exist: {old}"
        raise LedgerError(msg)
    if fs.exists(new):
        msg = f"analysis folder already exists: {new}"
        raise LedgerError(msg)
    if fs.exists(old / ".work" / "normalized"):
        msg = "rename before normalizing; normalized files keep the source path"
        raise LedgerError(msg)
    fs.rename(old, new)
    return {"id": new_id, "folder": fs.rel(new)}


def output_for(root: Path, rel: Path) -> Path:
    stem = "-".join(slug(p) for p in rel.with_suffix("").parts)
    return root / "normalized" / f"{stem}-{rel.suffix.lower().lstrip('.')}.md"


def parse_sets(items: list[str]) -> dict[str, str]:
    sets = {}
    for item in items:
        key, _, value = item.partition("=")
        if key not in META_KEYS[1:] or not value:
            msg = f"invalid --set {item!r}; keys: {', '.join(META_KEYS[1:])}"
            raise LedgerError(msg)
        sets[key] = value
    return sets


def unknown_hint(doc: Doc) -> str:
    if doc.kind == "table":
        return (
            "no institution module matched; write a mapping.json and pass --mapping (references/normalized-format.md)"
        )
    if doc.kind == "image":
        return "image source; transcribe with the LLM path and set normalizer: llm-image"
    if doc.kind == "llm-only":
        return (
            f"{doc.ext} is not read by scripts; if it has more than {LLM_ROWS_LIMIT} rows ask for a CSV/XLSX"
            " re-export, otherwise transcribe with the LLM path (normalizer: llm)"
        )
    if not doc.has_text:
        return "no text layer (scanned?); transcribe with the LLM path and set normalizer: llm-image"
    return "no institution module matched; transcribe with the LLM path (normalizer: llm)"


def _parse_source(
    fs: StagingFs,
    registry: InstitutionRegistry,
    doc: Doc,
    options: dict[str, Any],
) -> tuple[ParseResult, str]:
    """Parse with the mapping file, the named module or the first module that detects the layout."""
    if options["mapping"]:
        spec = json.loads(fs.read_text(fs.resolve_tmp(options["mapping"])))
        return mapping_mod.apply(doc, spec), "mapping"
    module = registry.by_name(options["module"]) if options["module"] else registry.find(doc)
    if module is None:
        raise LedgerError(unknown_hint(doc))
    return module.parse(doc, options["sets"]), f"module:{module.name}"


def run(  # noqa: PLR0913, PLR0917 - the three ports plus the request, kept flat
    fs: StagingFs,
    sources: Sources,
    registry: InstitutionRegistry,
    run_id: str,
    source: str,
    options: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one staged source; options: module, mapping, set (list of KEY=VALUE) and force."""
    root = run_dir(fs, run_id)
    src = fs.resolve_path(root / "sources" / source)
    if root / "sources" not in src.parents or not fs.is_file(src):
        msg = f"source not found under {root / 'sources'}: {source}"
        raise LedgerError(msg)
    out = output_for(root, src.relative_to(root / "sources"))
    if fs.exists(out) and not options["force"]:
        msg = f"{out.name} exists; reuse it or pass --force"
        raise LedgerError(msg)
    sets = parse_sets(options["set"])
    doc = sources.load(src)
    if doc.encrypted:
        msg = "PDF is password protected; ask the user for an unlocked copy"
        raise LedgerError(msg)
    (meta, rows, notes), normalizer = _parse_source(fs, registry, doc, {**options, "sets": sets})
    base = {
        "source": fs.rel(src),
        "normalizer": normalizer,
        "bank": "unknown",
        "account-type": "unknown",
        "account-holder": "unknown",
        "iban": "unknown",
        "currency": "unknown",
        "period": "unknown",
        "opening-balance": "none",
        "closing-balance": "none",
    }
    base.update(meta)
    base.update(sets)
    if base["period"] == "unknown" and rows:
        dates = sorted(r.date for r in rows)
        base["period"] = f"{dates[0]}..{dates[-1]}"
    ledger.write(fs, out, Ledger(base, rows))
    return {
        "output": fs.rel(out),
        "normalizer": normalizer,
        "rows": len(rows),
        "sum": format_value(sum((r.value for r in rows), Decimal(0))),
        "meta": base,
        "notes": notes,
    }
