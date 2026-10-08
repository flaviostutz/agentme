"""Copy the organised originals of invited candidates from .work/sources into their final folders in the run."""

import os
from pathlib import Path
from typing import Any

from analyse_cvs.adapters.connectors.local_fs import folders
from analyse_cvs.app.organising import SLUG_RE
from analyse_cvs.shared.constants import CHART_NAME, SOURCES_DIR

ORIGINAL_CHART_NAME = f"original-{CHART_NAME}"


def validate(run: Path, slugs: list[str]) -> None:
    """Raise ValueError when a slug is malformed or has no organised folder, before anything is copied."""
    for slug in slugs:
        if not SLUG_RE.match(slug):
            msg = f"invalid candidate slug: {slug!r}"
            raise ValueError(msg)
        if not (run / SOURCES_DIR / slug).is_dir():
            msg = f"no organised documents for {slug}; run cvs-organise first"
            raise ValueError(msg)


def _destination(base: Path, original: Path, root: Path) -> Path:
    rel = original.relative_to(root)
    if rel.as_posix() == CHART_NAME:
        rel = rel.with_name(ORIGINAL_CHART_NAME)
    return base / rel


def publish(run: Path, slugs: list[str]) -> dict[str, Any]:
    """Copy each candidate's organised originals to <run>/<slug>/ without overwriting; return what was done."""
    validate(run, slugs)
    result: dict[str, Any] = {}
    for slug in slugs:
        root, base = run / SOURCES_DIR / slug, run / slug
        copied: list[str] = []
        existing: list[str] = []
        for current, dirs, names in os.walk(root):
            dirs.sort()
            for name in sorted(names):
                original = Path(current) / name
                dest = _destination(base, original, root)
                if dest.exists():
                    existing.append(dest.relative_to(run).as_posix())
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                folders.copy_file(original, dest)
                copied.append(dest.relative_to(run).as_posix())
        result[slug] = {"copied": copied, "existing": existing}
    return result
