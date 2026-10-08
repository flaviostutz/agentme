"""Copy the staged originals into one plainly named folder per candidate under <run>/.work/sources."""

import re
from pathlib import Path, PurePosixPath
from typing import Any

from analyse_cvs.adapters.connectors.local_fs import folders
from analyse_cvs.shared.constants import MANIFEST, SOURCES_DIR

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(plan: dict[str, Any], manifest: dict[str, Any], run: Path) -> None:
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
            if not isinstance(slug, str) or not SLUG_RE.match(slug):
                msg = f"invalid candidate slug for {key}: {slug!r}"
                raise ValueError(msg)
            target = run / SOURCES_DIR / slug
            if target.exists() and not target.is_dir():
                msg = f"target exists and is not a folder: {slug}"
                raise ValueError(msg)


def _target(entry: dict[str, Any], plan: dict[str, Any], group_names: dict[str, str]) -> tuple[str, str] | None:
    """Return (slug, path inside the slug folder) for a manifest entry, or None when the plan skips it."""
    if entry["id"] in plan.get("files", {}):
        return plan["files"][entry["id"]], PurePosixPath(entry["source"]).name
    slug = plan.get("folders", {}).get(entry["group"])
    if slug is None:
        return None
    inside = PurePosixPath(entry["source"]).relative_to(group_names[entry["group"]])
    return slug, inside.as_posix()


def organise(run: Path, source: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """Copy the planned originals from source into <run>/.work/sources/<slug>/ and update the manifest.

    A files entry overrides the folder of its group. Different files that clash get a -2, -3 suffix.
    """
    manifest_path = run / MANIFEST
    manifest = folders.read_json(manifest_path)
    validate(plan, manifest, run)
    group_names = {g["id"]: g["name"] for g in manifest["groups"]}

    work: list[tuple[dict[str, Any], Path, Path]] = []
    unassigned: list[str] = []
    for entry in manifest["files"]:
        target = _target(entry, plan, group_names)
        if target is None:
            if entry["id"] and "organised" not in entry:
                unassigned.append(entry["id"])
            continue
        original = source / entry["source"]
        if not original.is_file() or original.is_symlink():
            msg = f"source file missing or not a regular file: {entry['source']}"
            raise ValueError(msg)
        work.append((entry, original, run / SOURCES_DIR / target[0] / target[1]))

    for entry, original, dest in work:
        entry["organised"] = folders.copy_unique(original, dest).relative_to(run).as_posix()
    folders.write_json(manifest_path, manifest)

    return {
        "organised": {e["id"] or e["source"]: e["organised"] for e, _, _ in work},
        "slugs": sorted({PurePosixPath(e["organised"]).parts[2] for e, _, _ in work}),
        "unassigned": unassigned,
    }
