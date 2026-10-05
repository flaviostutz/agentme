"""Organise a staged folder into one plainly named folder per candidate."""

import re
from pathlib import Path
from typing import Any

from analyse_cvs.adapters.connectors.local_fs import folders
from analyse_cvs.shared.constants import MANIFEST

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(plan: dict[str, Any], manifest: dict[str, Any], folder: Path) -> None:
    """Raise ValueError when the plan has unknown keys, unknown ids, bad slugs or file targets."""
    groups = {g["id"] for g in manifest["groups"]}
    docs = {f["id"] for f in manifest["files"] if f["id"]}
    unknown_keys = set(plan) - {"folders", "files"}
    if unknown_keys:
        msg = f"unknown plan keys: {sorted(unknown_keys)}"
        raise ValueError(msg)
    for kind, ids in (("folders", groups), ("files", docs)):
        for key, slug in plan.get(kind, {}).items():
            if key not in ids:
                msg = f"unknown {kind} id: {key}"
                raise ValueError(msg)
            if not isinstance(slug, str) or not SLUG_RE.match(slug) or slug == "md":
                msg = f"invalid candidate slug for {key}: {slug!r}"
                raise ValueError(msg)
            target = folder / slug
            if target.exists() and not target.is_dir():
                msg = f"target exists and is not a folder: {slug}"
                raise ValueError(msg)


def _rename_groups(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    folder: Path,
    moves: dict[str, str],
    touched: set[Path],
) -> list[dict[str, Any]]:
    renamed: list[dict[str, Any]] = []
    groups = {g["id"]: g for g in manifest["groups"]}
    for gid, slug in plan.get("folders", {}).items():
        group = groups[gid]
        src, dst = folder / group["name"], folder / slug
        if group["name"] == slug or not src.is_dir():
            continue
        if dst.exists() and not src.samefile(dst):
            folders.move_tree(src, dst, moves, folder)
            renamed.append({"group": gid, "from": group["name"], "to": slug, "merged": True})
        else:
            folders.rename_folder(src, dst, folder / f".organise-{slug}")
            for f in manifest["files"]:
                if f["group"] == gid:
                    moves[f["source"]] = slug + f["source"][len(group["name"]) :]
            renamed.append({"group": gid, "from": group["name"], "to": slug, "merged": False})
        touched.add(src)
        group["name"] = slug
    return renamed


def _move_files(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    folder: Path,
    moves: dict[str, str],
    touched: set[Path],
) -> None:
    for doc_id, slug in plan.get("files", {}).items():
        entry = next(f for f in manifest["files"] if f["id"] == doc_id)
        old = folder / moves.get(entry["source"], entry["source"])
        if old.parent == folder / slug or not old.is_file():
            continue
        new = folders.free_path(folder / slug / old.name)
        folders.move_file(old, new)
        touched.add(old.parent)
        moves[entry["source"]] = new.relative_to(folder).as_posix()


def organise(folder: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """Apply the plan, update the manifest and return the renamed, sources and removed report."""
    manifest_path = folder / MANIFEST
    manifest = folders.read_json(manifest_path)
    validate(plan, manifest, folder)

    moves: dict[str, str] = {}
    removed: list[str] = []
    touched: set[Path] = set()
    renamed = _rename_groups(plan, manifest, folder, moves, touched)
    _move_files(plan, manifest, folder, moves, touched)

    for path in sorted(touched, key=lambda p: len(p.parts), reverse=True):
        if path != folder and folder in path.parents:
            top = folder / path.relative_to(folder).parts[0]
            folders.remove_if_empty(top, removed, folder)

    for f in manifest["files"]:
        f["source"] = moves.get(f["source"], f["source"])
    folders.write_json(manifest_path, manifest)

    return {
        "renamed": renamed,
        "sources": {f["id"]: f["source"] for f in manifest["files"] if f["id"]},
        "removed": sorted(set(removed)),
    }
