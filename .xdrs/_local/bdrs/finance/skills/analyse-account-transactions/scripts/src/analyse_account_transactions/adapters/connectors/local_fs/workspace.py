import zipfile
from pathlib import Path

from analyse_account_transactions.app.ports import ZipEntry
from analyse_account_transactions.shared.errors import CorruptArchiveError, LedgerError


class LocalWorkspace:
    """LedgerStore and StagingFs backed by the local file system; all analysis files live under <cwd>/.tmp/."""

    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd

    def resolve_tmp(self, path: str, *, must_exist: bool = True) -> Path:
        root = (self.cwd / ".tmp").resolve()
        resolved = (self.cwd / path).resolve()
        if root not in resolved.parents:
            msg = f"path must be inside {root}: {resolved}"
            raise LedgerError(msg)
        if must_exist and not resolved.is_file():
            msg = f"file does not exist: {resolved}"
            raise LedgerError(msg)
        return resolved

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.cwd.resolve()))

    def resolve_input(self, arg: str) -> Path:
        source = (self.cwd / arg).resolve()
        if not source.exists():
            msg = f"input does not exist: {source}"
            raise LedgerError(msg)
        return source

    def analysis_root(self, run_id: str) -> Path:
        return (self.cwd / ".tmp" / run_id).resolve()

    def resolve_path(self, path: Path) -> Path:
        return path.resolve()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def list_files(self, folder: Path) -> list[Path]:
        return sorted(p for p in folder.rglob("*") if p.is_file()) if folder.exists() else []

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def read_bytes(self, path: Path) -> bytes:
        return path.read_bytes()

    def write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_bytes(self, path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def rename(self, old: Path, new: Path) -> None:
        old.rename(new)

    def list_zip(self, path: Path) -> list[ZipEntry]:
        try:
            with zipfile.ZipFile(path) as archive:
                return [m for m in archive.infolist() if not m.is_dir()]
        except zipfile.BadZipFile as err:
            msg = f"corrupt zip: {path.name}"
            raise CorruptArchiveError(msg) from err

    def read_zip_entry(self, path: Path, name: str) -> bytes:
        try:
            with zipfile.ZipFile(path) as archive:
                return archive.read(name)
        except zipfile.BadZipFile as err:
            msg = f"corrupt zip: {path.name}"
            raise CorruptArchiveError(msg) from err
