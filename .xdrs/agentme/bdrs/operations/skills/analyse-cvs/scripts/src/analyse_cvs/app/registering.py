"""Register converted documents: rename them per candidate, fill Sources and add Candidates rows."""

from pathlib import Path
from typing import Any

from analyse_cvs.adapters.connectors.local_fs import folders
from analyse_cvs.app.organising import SLUG_RE
from analyse_cvs.app.report_tables import Table, find_table, render_row
from analyse_cvs.shared.constants import DOC_TYPES, MANIFEST, STAGING

Docs = dict[str, dict[str, str]]
CONVERTED = "converted"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def validate_docs(docs: Docs, staged: dict[str, dict[str, Any]], known_sources: set[str], folder: Path) -> None:
    """Raise ValueError when decisions are missing, unknown or inconsistent, before anything changes."""
    names: dict[str, str] = {}
    for doc_id, entry in docs.items():
        if doc_id not in staged:
            msg = f"unknown staged document id: {doc_id}"
            raise ValueError(msg)
        if "skip" in entry:
            continue
        slug, doc_type, name = entry.get("slug", ""), entry.get("type", ""), entry.get("candidate", "")
        if not SLUG_RE.match(slug) or doc_type not in DOC_TYPES or not name:
            msg = f"{doc_id}: needs candidate, slug (kebab-case) and type ({', '.join(sorted(DOC_TYPES))})"
            raise ValueError(msg)
        if names.setdefault(slug, name).casefold() != name.casefold():
            msg = f"slug {slug} is used for two names: {names[slug]!r} and {name!r}"
            raise ValueError(msg)
        if not (folder / STAGING / f"{doc_id}-converted.md").is_file():
            msg = f"{doc_id}: converted file {doc_id}-converted.md not found"
            raise ValueError(msg)
    pending = [i for i, f in staged.items() if i not in docs and f["source"] not in known_sources]
    if pending:
        msg = f"no decision for staged documents: {', '.join(pending)}"
        raise ValueError(msg)


def _insert_rows(lines: list[str], table: Table, rows: list[list[str]]) -> list[str]:
    return [*lines[: table.end], *(render_row(r) for r in rows), *lines[table.end :]]


def register(folder: Path, lines: list[str], docs: Docs) -> tuple[list[str], dict[str, Any]]:
    """Rename converted files, add Sources and Candidates rows and return the new lines and a summary."""
    manifest = folders.read_json(folder / MANIFEST)
    staged = {f["id"]: f for f in manifest["files"] if f["id"]}
    sources, candidates = find_table(lines, "## Sources"), find_table(lines, "## Candidates")
    source_col = sources.column("Source")
    known = {row[source_col] for row in sources.rows}
    validate_docs(docs, staged, known, folder)

    renamed: dict[str, str] = {}
    source_rows: list[list[str]] = []
    new_names: dict[str, str] = {}
    for doc_id in sorted(docs):
        entry, source = docs[doc_id], _cell(staged[doc_id]["source"])
        if source in known:
            continue
        if "skip" in entry:
            source_rows.append([source, "", f"skipped: {_cell(entry['skip'])}"])
            continue
        target = folders.free_path(folder / "md" / f"{entry['slug']}-{entry['type']}.md")
        folders.move_file(folder / STAGING / f"{doc_id}-converted.md", target)
        renamed[doc_id] = target.relative_to(folder).as_posix()
        source_rows.append([source, renamed[doc_id], CONVERTED])
        new_names.setdefault(entry["candidate"].casefold(), entry["candidate"])
    source_rows += [
        [_cell(f["source"]), "", "skipped: unsupported format"]
        for f in manifest["files"]
        if not f["id"] and _cell(f["source"]) not in known
    ]

    name_col = candidates.column("Name")
    existing = {row[name_col].casefold() for row in candidates.rows}
    candidate_rows = []
    for key, name in new_names.items():
        if key not in existing:
            cells = [""] * len(candidates.header)
            cells[name_col] = _cell(name)
            candidate_rows.append(cells)

    updated = _insert_rows(lines, sources, source_rows)
    updated = _insert_rows(updated, find_table(updated, "## Candidates"), candidate_rows)
    summary = {
        "renamed": renamed,
        "sources_added": len(source_rows),
        "candidates_added": [r[name_col] for r in candidate_rows],
    }
    return updated, summary
