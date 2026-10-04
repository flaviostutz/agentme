# Runtime: Python >=3.10; work-dir store: deterministic atomic JSON, manifest with content hashes, run lock, JSONL logs.
"""Work-dir persistence for the portfolio manager. Everything lives under <cwd>/.tmp/portfolio-manager-<name>/."""

import contextlib
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from sourcedoc import PmError

SUBDIRS = ("raw", "data", "cache", "derived", "reports", "graphs", "logs")
DEFAULT_CONFIG = {
    "base_currency": "EUR",
    "tolerances": {"money": "0.01", "quantity": "0.000001"},
    "tracked_accounts": [],
}
CALCULATION_VERSION = 1


def resolve_tmp(path: str, cwd: Path) -> Path:
    """Resolve path and refuse anything outside <cwd>/.tmp (the skill writes only there)."""
    root = (cwd / ".tmp").resolve()
    resolved = (cwd / path).resolve()
    if root != resolved and root not in resolved.parents:
        raise PmError(f"path must be inside {root}: {resolved}")
    return resolved


def work_dir(name: str, cwd: Path) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        raise PmError(f"invalid work name {name!r}: use letters, digits, dot, dash or underscore")
    return resolve_tmp(f".tmp/portfolio-manager-{name}", cwd)


def dumps(obj) -> str:
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class Workspace:
    """Handle for one work dir: config, manifest, data files, lock and logs."""

    def __init__(self, root: Path):
        self.root = root

    def path(self, rel: str) -> Path:
        return self.root / rel

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
            raise PmError(f"cannot read config.yaml in {self.root}: {err}") from err
        if not isinstance(data, dict):
            raise PmError("config.yaml must be a mapping")
        return {**DEFAULT_CONFIG, **data}

    def read(self, rel: str, default=None):
        path = self.path(rel)
        if not path.is_file():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            raise PmError(f"cannot read {rel}: {err}") from err

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
            raise PmError(f"another run holds the lock ({path}); remove that file if no run is active") from err
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        try:
            yield
        finally:
            path.unlink(missing_ok=True)
