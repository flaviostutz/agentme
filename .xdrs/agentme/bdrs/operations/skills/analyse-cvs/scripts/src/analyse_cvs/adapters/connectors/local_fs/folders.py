"""Filesystem operations on candidate source folders and run folders under .tmp/."""

import filecmp
import json
import os
import shutil
from pathlib import Path
from typing import Any

from analyse_cvs.shared.constants import STAGING


def resolve_run(run: str, cwd: Path, source: Path | None = None) -> Path:
    """Return the absolute run folder inside <cwd>/.tmp.

    With a source folder the run may be new but must not be the source or nested with it; without one
    the run must already exist.
    """
    root = (cwd / ".tmp").resolve()
    path = (cwd / run).resolve()
    if path == root or root not in path.parents:
        msg = f"run folder must be inside {root}: {path}"
        raise ValueError(msg)
    if source is not None:
        if path == source or path in source.parents or source in path.parents:
            msg = f"run folder and source folder must be separate, not nested: {path}"
            raise ValueError(msg)
    elif not path.is_dir():
        msg = f"run folder does not exist: {path}"
        raise ValueError(msg)
    return path


def resolve_folder(folder: str, cwd: Path) -> Path:
    """Return the absolute source folder, which must be a directory inside <cwd>/.tmp."""
    root = (cwd / ".tmp").resolve()
    path = (cwd / folder).resolve()
    if path == root or root not in path.parents:
        msg = f"folder must be inside {root}: {path}"
        raise ValueError(msg)
    if not path.is_dir():
        msg = f"folder does not exist: {path}"
        raise ValueError(msg)
    return path


def _visible(path: Path) -> bool:
    return not path.name.startswith(".") and not path.is_symlink()


def _group_files(group_dir: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(group_dir):
        base = Path(root)
        dirs[:] = sorted(d for d in dirs if _visible(base / d))
        files.extend(base / n for n in names if _visible(base / n) and (base / n).is_file())
    return files


def list_sources(folder: Path) -> tuple[list[dict[str, str]], list[tuple[Path, str | None]]]:
    """Return (groups, [(path, group_id)]) sorted by relative path."""
    groups: list[dict[str, str]] = []
    sources: list[tuple[Path, str | None]] = []
    for entry in sorted(folder.iterdir()):
        if not _visible(entry):
            continue
        if entry.is_file():
            sources.append((entry, None))
        elif entry.is_dir():
            gid = f"g-{len(groups) + 1:02d}"
            groups.append({"id": gid, "name": entry.name})
            sources.extend((f, gid) for f in _group_files(entry))
    sources.sort(key=lambda s: s[0].relative_to(folder).as_posix())
    return groups, sources


def reset_staging(folder: Path) -> Path:
    """Recreate an empty staging folder and return it."""
    staging = folder / STAGING
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    return staging


def remove_staging(folder: Path) -> None:
    """Delete the staging folder when present."""
    shutil.rmtree(folder / STAGING, ignore_errors=True)


def copy_file(src: Path, dest: Path) -> None:
    """Copy a file's bytes to dest."""
    shutil.copyfile(src, dest)


def write_json(path: Path, data: Any) -> None:
    """Write data as indented UTF-8 JSON."""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def free_path(path: Path) -> Path:
    """Return path, or the first free name with a -2, -3 suffix when it exists."""
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def copy_unique(src: Path, dest: Path) -> Path:
    """Copy src to dest, or to a -2, -3 name when different content exists; identical content is reused."""
    n = 1
    target = dest
    while target.exists():
        if filecmp.cmp(src, target, shallow=False):
            return target
        n += 1
        target = dest.with_name(f"{dest.stem}-{n}{dest.suffix}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)
    return target


def move_file(old: Path, new: Path) -> None:
    """Move a file, creating the target folder."""
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
