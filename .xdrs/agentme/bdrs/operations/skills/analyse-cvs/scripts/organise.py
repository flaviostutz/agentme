#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Organise a staged .tmp/ source folder into one plainly named folder per candidate.

Reads md/.staging/manifest.json written by stage.py and a plan file:
  {"folders": {"g-01": "roger-mathias"}, "files": {"doc-05": "anna-silva"}}
"folders" renames a group folder to a candidate slug, merging into an existing slug folder.
"files" moves a staged document's source file into the candidate slug folder.
Clashing filenames get a -2, -3 suffix. Folders left empty are removed. Safe to re-run.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from stage import MANIFEST, resolve_folder

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
JUNK = {".DS_Store", "Thumbs.db"}


def validate(plan: dict, manifest: dict, folder: Path) -> None:
    groups = {g["id"] for g in manifest["groups"]}
    docs = {f["id"] for f in manifest["files"] if f["id"]}
    unknown_keys = set(plan) - {"folders", "files"}
    if unknown_keys:
        raise ValueError(f"unknown plan keys: {sorted(unknown_keys)}")
    for kind, ids in (("folders", groups), ("files", docs)):
        for key, slug in plan.get(kind, {}).items():
            if key not in ids:
                raise ValueError(f"unknown {kind} id: {key}")
            if not isinstance(slug, str) or not SLUG_RE.match(slug) or slug == "md":
                raise ValueError(f"invalid candidate slug for {key}: {slug!r}")
            target = folder / slug
            if target.exists() and not target.is_dir():
                raise ValueError(f"target exists and is not a folder: {slug}")


def free_path(path: Path) -> Path:
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def remove_if_empty(path: Path, removed: list, folder: Path) -> None:
    if not path.is_dir() or path.is_symlink():
        return
    for child in path.iterdir():
        remove_if_empty(child, removed, folder)
    children = list(path.iterdir())
    if all(c.name in JUNK and c.is_file() and not c.is_symlink() for c in children):
        for c in children:
            c.unlink()
        path.rmdir()
        removed.append(path.relative_to(folder).as_posix())


def move_tree(src: Path, dst: Path, moves: dict, folder: Path) -> None:
    """Move every entry under src into dst, keeping relative paths and suffixing clashes."""
    for root, _dirs, names in os.walk(src):
        for name in names:
            old = Path(root) / name
            new = free_path(dst / old.relative_to(src))
            new.parent.mkdir(parents=True, exist_ok=True)
            old.rename(new)
            moves[old.relative_to(folder).as_posix()] = new.relative_to(folder).as_posix()


def organise(folder: Path, plan: dict) -> dict:
    manifest_path = folder / MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate(plan, manifest, folder)

    moves, renamed, removed = {}, [], []
    groups = {g["id"]: g for g in manifest["groups"]}
    touched = set()

    for gid, slug in plan.get("folders", {}).items():
        group = groups[gid]
        src, dst = folder / group["name"], folder / slug
        if group["name"] == slug or not src.is_dir():
            continue
        if dst.exists() and not src.samefile(dst):
            move_tree(src, dst, moves, folder)
            renamed.append({"group": gid, "from": group["name"], "to": slug, "merged": True})
        else:
            # Two-step rename handles case-only changes on case-insensitive filesystems.
            tmp = folder / f".organise-{slug}"
            src.rename(tmp)
            tmp.rename(dst)
            for f in manifest["files"]:
                if f["group"] == gid:
                    moves[f["source"]] = slug + f["source"][len(group["name"]):]
            renamed.append({"group": gid, "from": group["name"], "to": slug, "merged": False})
        touched.add(src)
        group["name"] = slug

    def current(source: str) -> str:
        return moves.get(source, source)

    for doc_id, slug in plan.get("files", {}).items():
        entry = next(f for f in manifest["files"] if f["id"] == doc_id)
        old = folder / current(entry["source"])
        if old.parent == folder / slug or not old.is_file():
            continue
        new = free_path(folder / slug / old.name)
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)
        touched.add(old.parent)
        moves[entry["source"]] = new.relative_to(folder).as_posix()

    for path in sorted(touched, key=lambda p: len(p.parts), reverse=True):
        if path != folder and folder in path.parents:
            top = folder / path.relative_to(folder).parts[0]
            remove_if_empty(top, removed, folder)

    for f in manifest["files"]:
        f["source"] = current(f["source"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "renamed": renamed,
        "sources": {f["id"]: f["source"] for f in manifest["files"] if f["id"]},
        "removed": sorted(set(removed)),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="source folder, relative to the current directory, inside .tmp/")
    parser.add_argument("plan", help="JSON plan file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        folder = resolve_folder(args.folder, Path.cwd())
        if not (folder / MANIFEST).is_file():
            raise ValueError("manifest not found; run stage.py first")
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        result = organise(folder, plan)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in result["renamed"]:
            print(f"{'merged' if r['merged'] else 'renamed'} {r['from']!r} -> {r['to']}")
        for path in result["removed"]:
            print(f"removed empty folder {path!r}")
        print(f"{len(result['renamed'])} folder(s) renamed or merged, {len(result['removed'])} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
