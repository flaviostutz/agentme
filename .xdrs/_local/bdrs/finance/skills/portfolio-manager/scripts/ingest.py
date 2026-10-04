# Runtime: Python >=3.10; pymupdf+pyyaml via pm.py. Orchestrates raw-file intake, adapter parsing (cached by file hash), merge and validation.
"""Ingest source PDFs into the work dir and validate its content hashes."""

import re
import shutil
from pathlib import Path

import ledger
import registry
from institutions.common import unresolved
from sourcedoc import PmError, read_pdf, sha256_file
from store import CALCULATION_VERSION, Workspace, dumps, sha256_text

DATA_FILES = ("accounts", "events", "snapshots", "references", "unresolved", "ingest")
AI_ADDRESSED = re.compile(r"(?i)\b(ignore (all |any )?(previous|prior|above) (instructions|prompts?)|system prompt|"
                          r"as an? (ai|language model|assistant)|you (must|should) (now )?(tell|reply|respond|answer)|"
                          r"do not (tell|mention|inform) the user)\b")


def collect_sources(source: Path) -> list:
    if source.is_file():
        return [source]
    if not source.is_dir():
        raise PmError(f"source not found: {source}")
    return sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def copy_raw(ws: Workspace, sources: list) -> dict:
    """Copy sources to raw/<sha8>-<name>; identical content is never copied twice and nothing is deleted."""
    raw = {}
    for src in sources:
        sha = sha256_file(src)
        dest = ws.path("raw") / f"{sha[:8]}-{_safe(src.name)}"
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        raw[dest.name] = {"sha256": sha, "original_name": src.name}
    return raw


def _parse_file(ws: Workspace, path: Path, sha: str, answers: dict) -> dict:
    """Return {file, sha256, results, status, notices}; cached by file hash, answers and calculation version."""
    key = f"{sha[:16]}-{sha256_text(dumps(answers))[:8]}-v{CALCULATION_VERSION}"
    cache_rel = f"cache/parse-{key}.json"
    cached = ws.read(cache_rel)
    if cached is not None:
        return {**cached, "file": path.name, "sha256": sha}
    doc = read_pdf(path)
    out = {"results": [], "status": "ok", "notices": [], "problem": ""}
    if doc.status != "ok":
        out.update(status=doc.status, problem=doc.error or f"PDF is {doc.status}")
    else:
        adapter = registry.detect(doc)
        if adapter is None:
            out.update(status="unsupported", problem="no adapter recognises this layout")
        else:
            try:
                out["results"] = adapter.parse(doc, answers)
            except (PmError, ValueError, IndexError, KeyError, ArithmeticError) as err:  # adapters reject drifted layouts
                out.update(status="layout-drift", problem=f"{type(err).__name__}: {err}")
        out["notices"] = [s[:120] for s in doc.lines() if AI_ADDRESSED.search(s)][:5]
    ws.write(cache_rel, out)
    return {**out, "file": path.name, "sha256": sha}


def _problem_items(parsed: list) -> tuple:
    """Files that could not be parsed become unresolved items; they never block the rest."""
    usable, items, files = [], [], []
    for p in parsed:
        if p["status"] == "ok":
            usable.append(p)
            continue
        item = unresolved(p["sha256"], f"file-{p['status']}", p["problem"],
                          "This file was not loaded. Provide a readable copy (unlocked, with text) or confirm it should be ignored.", p["file"])
        items.append(item)
        files.append({"file": p["file"], "sha256": p["sha256"], "status": p["status"], "adapter": ""})
    return usable, items, files


def ingest(ws: Workspace, sources: list, run_id: str) -> dict:
    raw = copy_raw(ws, sources)
    manifest = ws.manifest()
    manifest["raw"] = {**manifest.get("raw", {}), **raw}
    answers = ws.read("answers.json", {"accept_files": [], "answers": {}})
    parsed = []
    for name in sorted(manifest["raw"]):
        path = ws.path("raw") / name
        if path.is_file():
            parsed.append(_parse_file(ws, path, manifest["raw"][name]["sha256"], answers))
    usable, items, bad_files = _problem_items(parsed)
    data = ledger.merge(usable, answers)
    answered = set(answers.get("answers", {}))
    data["unresolved"] = sorted(data["unresolved"] + [i for i in items if i["id"] not in answered], key=lambda u: u["id"])
    data["ingest"]["files"] = sorted(data["ingest"]["files"] + bad_files, key=lambda f: f["file"])
    data["ingest"]["ai_addressed"] = [{"file": p["file"], "text": t} for p in parsed for t in p["notices"]]
    hashes = {}
    for key in DATA_FILES:
        hashes[f"data/{key}.json"] = ws.write(f"data/{key}.json", data[key])
    manifest.update(files=hashes, status="ingested", calculation_version=CALCULATION_VERSION)
    ws.save_manifest(manifest)
    ws.log(run_id, step="ingest", files=len(parsed), unresolved=len(data["unresolved"]))
    return data


def validate(ws: Workspace) -> list:
    """Return findings [{level: error|warn, message}] about hashes, rejected files, errors and unresolved items."""
    out = []
    manifest = ws.manifest()
    for name, info in sorted(manifest.get("raw", {}).items()):
        path = ws.path("raw") / name
        if not path.is_file():
            out.append({"level": "error", "message": f"raw file missing: {name}"})
        elif sha256_file(path) != info["sha256"]:
            out.append({"level": "error", "message": f"raw file changed after ingest: {name}"})
    for rel, sha in sorted(manifest.get("files", {}).items()):
        path = ws.path(rel)
        if not path.is_file():
            out.append({"level": "error", "message": f"ledger file missing: {rel}"})
        elif sha256_text(path.read_text(encoding="utf-8")) != sha:
            out.append({"level": "error", "message": f"ledger file edited outside the skill: {rel}"})
    info = ws.read("data/ingest.json", {})
    out += [{"level": "error", "message": m} for m in info.get("errors", [])]
    out += [{"level": "warn", "message": f"{c['file']}: {c['name']} expected {c['expected']} got {c['actual']} ({c['level']})"}
            for c in info.get("checks", [])]
    out += [{"level": "warn", "message": f"{f['file']}: {f['status']}"} for f in info.get("files", []) if f["status"] not in ("loaded", "accepted")]
    out += [{"level": "warn", "message": f"AI-addressed text ignored in {n['file']}: {n['text']}"} for n in info.get("ai_addressed", [])]
    n_unres = len(ws.read("data/unresolved.json", []))
    if n_unres:
        out.append({"level": "warn", "message": f"{n_unres} unresolved record(s) need an answer"})
    if not manifest.get("raw"):
        out.append({"level": "error", "message": "nothing ingested yet"})
    return out
