"""In-memory LedgerStore for tests of the application layer (no file system)."""

from pathlib import Path, PurePosixPath

from analyse_account_transactions.shared.errors import LedgerError


class MemoryWorkspace:
    """Implements LedgerStore over a dict of files below a fake working folder; paths must be inside .tmp/."""

    def __init__(self, root: str = "/work", files: dict[str, str] | None = None) -> None:
        self.root = Path(root)
        self.files: dict[Path, str] = {}
        for name, text in (files or {}).items():
            self.files[self.root / name] = text

    def resolve_tmp(self, path: str, *, must_exist: bool = True) -> Path:
        resolved = Path(PurePosixPath(self.root, path))
        parts = resolved.relative_to(self.root).parts if resolved.is_relative_to(self.root) else ()
        if not parts or parts[0] != ".tmp" or len(parts) < 2:  # noqa: PLR2004 - .tmp/<file> at least
            msg = f"{path} must be inside .tmp/ of the working folder"
            raise LedgerError(msg)
        if must_exist and resolved not in self.files:
            msg = f"{path} not found"
            raise LedgerError(msg)
        return resolved

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))

    def exists(self, path: Path) -> bool:
        return path in self.files

    def read_text(self, path: Path) -> str:
        return self.files[path]

    def read_bytes(self, path: Path) -> bytes:
        return self.files[path].encode("utf-8")

    def write_text(self, path: Path, text: str) -> None:
        self.files[path] = text
