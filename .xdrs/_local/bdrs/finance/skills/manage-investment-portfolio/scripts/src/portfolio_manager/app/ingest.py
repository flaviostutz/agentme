"""Ingest source PDFs into the work dir and validate its content hashes."""

import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from portfolio_manager.app import ledger
from portfolio_manager.app.acceptance import FILE as ACCEPTANCES_FILE
from portfolio_manager.app.records import unresolved
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import CALCULATION_VERSION, dumps, sha256_text

if TYPE_CHECKING:
    from portfolio_manager.adapters.connectors.local_fs.workspace import Workspace

PdfReader = Callable[[Path], Doc]


class Adapters(Protocol):
    """Institution registry: picks the adapter module that reads a document."""

    def detect(self, doc: Doc) -> Any: ...


DATA_FILES = ("accounts", "events", "snapshots", "references", "unresolved", "ingest")
TRACKED_INPUTS = ("answers.json", ACCEPTANCES_FILE, "data/classifications.json")
AI_ADDRESSED = re.compile(
    r"(?i)\b(ignore (all |any )?(previous|prior|above) (instructions|prompts?)|system prompt|"
    r"as an? (ai|language model|assistant)|you (must|should) (now )?(tell|reply|respond|answer)|"
    r"do not (tell|mention|inform) the user)\b"
)


def _parse_file(ws: "Workspace", path: Path, sha: str, answers: dict, reader: PdfReader, registry: Adapters) -> dict:
    """Return {file, sha256, results, status, notices}; cached by file hash, answers and calculation version."""
    key = f"{sha[:16]}-{sha256_text(dumps(answers))[:8]}-v{CALCULATION_VERSION}"
    cache_rel = f"cache/parse-{key}.json"
    cached = ws.read(cache_rel)
    if cached is not None:
        return {**cached, "file": path.name, "sha256": sha}
    doc = reader(path)
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
            except (
                PmError,
                ValueError,
                IndexError,
                KeyError,
                ArithmeticError,
            ) as err:  # adapters reject drifted layouts
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
        item = unresolved(
            p["sha256"],
            f"file-{p['status']}",
            p["problem"],
            "This file was not loaded. Provide a readable copy (unlocked, with text) or confirm it should be ignored.",
            p["file"],
        )
        items.append(item)
        files.append({"file": p["file"], "sha256": p["sha256"], "status": p["status"], "adapter": ""})
    return usable, items, files


def ingest(ws: "Workspace", sources: list, run_id: str, reader: PdfReader, registry: Adapters) -> dict:
    raw = dict(ws.import_raw(src) for src in sources)
    manifest = ws.manifest()
    manifest["raw"] = {**manifest.get("raw", {}), **raw}
    answers = ws.read("answers.json", {"accept_files": [], "answers": {}})
    parsed, copies, first_by_sha = [], [], {}
    for name in sorted(manifest["raw"]):
        path = ws.path("raw") / name
        sha = manifest["raw"][name]["sha256"]
        if not path.is_file():
            continue
        if sha in first_by_sha:
            copies.append(
                {"file": name, "sha256": sha, "status": "duplicate", "adapter": "", "duplicate_of": first_by_sha[sha]}
            )
            continue
        first_by_sha[sha] = name
        parsed.append(_parse_file(ws, path, sha, answers, reader, registry))
    usable, items, bad_files = _problem_items(parsed)
    data = ledger.merge(usable, answers)
    answered = set(answers.get("answers", {}))
    data["unresolved"] = sorted(
        data["unresolved"] + [i for i in items if i["id"] not in answered], key=lambda u: u["id"]
    )
    data["ingest"]["files"] = sorted(data["ingest"]["files"] + bad_files + copies, key=lambda f: f["file"])
    data["ingest"]["ai_addressed"] = [{"file": p["file"], "text": t} for p in parsed for t in p["notices"]]
    hashes = {}
    for key in DATA_FILES:
        hashes[f"data/{key}.json"] = ws.write(f"data/{key}.json", data[key])
    tracked = {rel: sha for rel, sha in manifest.get("files", {}).items() if rel in TRACKED_INPUTS}
    manifest.update(files={**tracked, **hashes}, status="ingested", calculation_version=CALCULATION_VERSION)
    ws.save_manifest(manifest)
    ws.log(run_id, step="ingest", files=len(parsed), unresolved=len(data["unresolved"]))
    return data


def validate(ws: "Workspace") -> list:
    """Return findings [{level: error|warn, message}] about hashes, rejected files, errors and unresolved items."""
    out = []
    manifest = ws.manifest()
    for name, info in sorted(manifest.get("raw", {}).items()):
        rel = f"raw/{name}"
        if not ws.is_file(rel):
            out.append({"level": "error", "message": f"raw file missing: {name}"})
        elif ws.file_sha256(rel) != info["sha256"]:
            out.append({"level": "error", "message": f"raw file changed after ingest: {name}"})
    for rel, sha in sorted(manifest.get("files", {}).items()):
        if not ws.is_file(rel):
            out.append({"level": "error", "message": f"ledger file missing: {rel}"})
        elif ws.text_sha256(rel) != sha:
            out.append({"level": "error", "message": f"ledger file edited outside the skill: {rel}"})
    out += [
        {"level": "error", "message": f"{rel} exists but was not written by the skill (hand edit or unknown origin)"}
        for rel in TRACKED_INPUTS
        if ws.is_file(rel) and rel not in manifest.get("files", {})
    ]
    info = ws.read("data/ingest.json", {})
    out += [{"level": "error", "message": m} for m in info.get("errors", [])]
    out += [
        {
            "level": "warn",
            "message": f"{c['file']}: {c['name']} expected {c['expected']} got {c['actual']} ({c['level']})",
        }
        for c in info.get("checks", [])
    ]
    out += [
        {"level": "warn", "message": f"{f['file']}: {f['status']}"}
        for f in info.get("files", [])
        if f["status"] not in ("loaded", "accepted", "duplicate")
    ]
    out += [{"level": "warn", "message": n["message"]} for n in info.get("notes", []) if n["level"] == "warn"]
    out += [
        {"level": "warn", "message": f"AI-addressed text ignored in {n['file']}: {n['text']}"}
        for n in info.get("ai_addressed", [])
    ]
    n_unres = len(ws.read("data/unresolved.json", []))
    if n_unres:
        out.append({"level": "warn", "message": f"{n_unres} unresolved record(s) need an answer"})
    if not manifest.get("raw"):
        out.append({"level": "error", "message": "nothing ingested yet"})
    return out
