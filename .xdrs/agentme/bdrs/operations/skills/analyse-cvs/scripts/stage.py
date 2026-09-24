#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Copy candidate documents from a .tmp/ folder to safe staging names (doc-NN.<ext>).

Top-level files and files inside top-level subfolders (any depth) are staged. Each top-level
subfolder becomes a group (g-NN), a clue that its documents belong to one candidate.
Raw file and folder names are never passed to a shell: the agent only ever sees staged names and ids.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".pptx", ".html", ".htm", ".txt", ".md"}
STAGING = Path("md") / ".staging"
MANIFEST = STAGING / "manifest.json"


def resolve_folder(folder: str, cwd: Path) -> Path:
    root = (cwd / ".tmp").resolve()
    path = (cwd / folder).resolve()
    if path == root or root not in path.parents:
        raise ValueError(f"folder must be inside {root}: {path}")
    if not path.is_dir():
        raise ValueError(f"folder does not exist: {path}")
    return path


def _visible(p: Path) -> bool:
    return not p.name.startswith(".") and not p.is_symlink()


def _group_files(group_dir: Path) -> list:
    files = []
    for root, dirs, names in os.walk(group_dir):
        base = Path(root)
        dirs[:] = sorted(d for d in dirs if _visible(base / d))
        files.extend(base / n for n in names if _visible(base / n) and (base / n).is_file())
    return files


def list_sources(folder: Path) -> tuple:
    """Return (groups, [(path, group_id)]) sorted by relative path."""
    groups, sources = [], []
    for entry in sorted(folder.iterdir()):
        if not _visible(entry) or entry.name == "md":
            continue
        if entry.is_file():
            sources.append((entry, None))
        elif entry.is_dir():
            gid = f"g-{len(groups) + 1:02d}"
            groups.append({"id": gid, "name": entry.name})
            sources.extend((f, gid) for f in _group_files(entry))
    sources.sort(key=lambda s: s[0].relative_to(folder).as_posix())
    return groups, sources


def stage(folder: Path) -> dict:
    staging = folder / STAGING
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    groups, sources = list_sources(folder)
    files = []
    n = 0
    for src, gid in sources:
        rel = src.relative_to(folder).as_posix()
        ext = src.suffix.lower()
        if ext not in SUPPORTED:
            files.append({"id": None, "source": rel, "group": gid, "staged": None, "status": "unsupported"})
            continue
        n += 1
        doc_id = f"doc-{n:02d}"
        dest = staging / f"{doc_id}{ext}"
        shutil.copyfile(src, dest)
        files.append({
            "id": doc_id,
            "source": rel,
            "group": gid,
            "staged": dest.relative_to(folder).as_posix(),
            "status": "staged",
        })
    manifest = {"groups": groups, "files": files}
    (folder / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", help="source folder, relative to the current directory, inside .tmp/")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        folder = resolve_folder(args.folder, Path.cwd())
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    manifest = stage(folder)
    files = manifest["files"]
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        for g in manifest["groups"]:
            print(f"group {g['id']}: {g['name']!r}")
        for r in files:
            target = r["staged"] or "-"
            print(f"{r['status']:<12} {target:<24} {r['group'] or '-':<5} {r['source']!r}")
        print(f"{sum(r['status'] == 'staged' for r in files)} staged, "
              f"{sum(r['status'] == 'unsupported' for r in files)} unsupported, "
              f"{len(manifest['groups'])} group(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
