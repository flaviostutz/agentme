"""Stage candidate documents under safe names (doc-NN.<ext>) in the run folder and build the manifest."""

from pathlib import Path
from typing import Any

from analyse_cvs.adapters.connectors.local_fs import folders
from analyse_cvs.shared.constants import MANIFEST, SUPPORTED


def stage(source: Path, run: Path) -> dict[str, Any]:
    """Copy supported files from source to <run>/.work/staging, write the manifest and return it."""
    staging = folders.reset_staging(run)
    groups, sources = folders.list_sources(source)
    files: list[dict[str, Any]] = []
    count = 0
    for src, gid in sources:
        rel = src.relative_to(source).as_posix()
        ext = src.suffix.lower()
        if ext not in SUPPORTED:
            files.append({"id": None, "source": rel, "group": gid, "staged": None, "status": "unsupported"})
            continue
        count += 1
        doc_id = f"doc-{count:02d}"
        dest = staging / f"{doc_id}{ext}"
        folders.copy_file(src, dest)
        files.append(
            {
                "id": doc_id,
                "source": rel,
                "group": gid,
                "staged": dest.relative_to(run).as_posix(),
                "status": "staged",
            },
        )
    manifest = {"source_root": source.as_posix(), "groups": groups, "files": files}
    folders.write_json(run / MANIFEST, manifest)
    return manifest
