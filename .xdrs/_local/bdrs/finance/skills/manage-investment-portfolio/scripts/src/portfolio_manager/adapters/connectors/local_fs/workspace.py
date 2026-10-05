"""Work-dir persistence. Everything lives under <cwd>/.tmp/manage-investment-portfolio-<portfolio>/."""

import contextlib
import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.values import dumps, sha256_file, sha256_text

SUBDIRS = ("raw", "data", "cache", "derived", "reports", "graphs", "exports/portfolio-performance", "logs")
DEFAULT_CONFIG = {
    "base_currency": "EUR",
    "tolerances": {"money": "0.01", "quantity": "0.000001"},
    "tracked_accounts": [],
}


def resolve_tmp(path: str, cwd: Path) -> Path:
    """Resolve path and refuse anything outside <cwd>/.tmp (the skill writes only there)."""
    root = (cwd / ".tmp").resolve()
    resolved = (cwd / path).resolve()
    if root != resolved and root not in resolved.parents:
        msg = f"path must be inside {root}: {resolved}"
        raise PmError(msg)
    return resolved


def work_dir(name: str, cwd: Path) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        msg = f"invalid portfolio name {name!r}: use letters, digits, dot, dash or underscore"
        raise PmError(msg)
    return resolve_tmp(f".tmp/manage-investment-portfolio-{name}", cwd)


def collect_sources(source: Path) -> list[Path]:
    """A single file, or every PDF under a folder (sorted)."""
    if source.is_file():
        return [source]
    if not source.is_dir():
        msg = f"source not found: {source}"
        raise PmError(msg)
    return sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


class Workspace:
    """Handle for one work dir: config, manifest, data files, lock and logs."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, rel: str) -> Path:
        return self.root / rel

    def import_raw(self, source: Path) -> tuple[str, dict[str, str]]:
        """Copy source to raw/<sha8>-<name>; identical content is never copied twice. Returns (name, info)."""
        sha = sha256_file(source)
        dest = self.path("raw") / f"{sha[:8]}-{re.sub(r'[^A-Za-z0-9._-]+', '_', source.name)}"
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        return dest.name, {"sha256": sha, "original_name": source.name}

    def is_file(self, rel: str) -> bool:
        return self.path(rel).is_file()

    def file_sha256(self, rel: str) -> str:
        """sha256 of the raw bytes of a file in the work dir."""
        return sha256_file(self.path(rel))

    def text_sha256(self, rel: str) -> str:
        return sha256_text(self.path(rel).read_text(encoding="utf-8"))

    def clean_outputs(self, sub: str, pattern: str, keep: set[str]) -> None:
        """Delete files of a sub folder matching pattern whose relative path is not in keep."""
        for old in self.path(sub).glob(pattern):
            if f"{sub}/{old.name}" not in keep:
                old.unlink()

    def exists(self) -> bool:
        return (self.root / "config.yaml").is_file()

    def init(self) -> bool:
        """Create the layout; returns False when config.yaml already existed (nothing is overwritten)."""
        for sub in SUBDIRS:
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        cfg = self.root / "config.yaml"
        if cfg.exists():
            return False
        cfg.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=True), encoding="utf-8")
        return True

    def config(self) -> dict:
        try:
            data = yaml.safe_load(self.path("config.yaml").read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as err:
            msg = f"cannot read config.yaml in {self.root}: {err}"
            raise PmError(msg) from err
        if not isinstance(data, dict):
            msg = "config.yaml must be a mapping"
            raise PmError(msg)
        return {**DEFAULT_CONFIG, **data}

    def read(self, rel: str, default=None):
        path = self.path(rel)
        if not path.is_file():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            msg = f"cannot read {rel}: {err}"
            raise PmError(msg) from err

    def write(self, rel: str, obj) -> str:
        """Write deterministic JSON atomically and return its sha256."""
        text = dumps(obj)
        write_atomic(self.path(rel), text)
        return sha256_text(text)

    def write_text(self, rel: str, text: str) -> str:
        write_atomic(self.path(rel), text)
        return sha256_text(text)

    def manifest(self) -> dict:
        return self.read("manifest.json", {"raw": {}, "files": {}, "status": "empty"})

    def save_manifest(self, manifest: dict) -> None:
        self.write("manifest.json", manifest)

    def write_tracked(self, rel: str, obj) -> None:
        """Write a script-owned input file and record its hash in the manifest so hand edits are detectable."""
        sha = self.write(rel, obj)
        manifest = self.manifest()
        manifest["files"] = {**manifest.get("files", {}), rel: sha}
        self.save_manifest(manifest)

    def log(self, run_id: str, **fields) -> None:
        line = json.dumps({"ts": datetime.now(UTC).isoformat(timespec="seconds"), **fields}, sort_keys=True)
        path = self.path(f"logs/{run_id}.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    @contextlib.contextmanager
    def lock(self):
        """Exclusive run lock; a leftover lock file means another run is active or crashed (never removed automatically)."""
        path = self.path("logs/.lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as err:
            msg = f"another run holds the lock ({path}); remove that file if no run is active"
            raise PmError(msg) from err
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        try:
            yield
        finally:
            path.unlink(missing_ok=True)
