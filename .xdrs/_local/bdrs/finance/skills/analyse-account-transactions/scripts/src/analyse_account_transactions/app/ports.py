"""Ports the application layer needs from the outside world; implemented by the connectors in adapters/connectors."""

from pathlib import Path
from typing import Protocol

from analyse_account_transactions.shared.models import Doc, Institution


class LedgerStore(Protocol):
    """Text files of an analysis under .tmp/."""

    def resolve_tmp(self, path: str, *, must_exist: bool = True) -> Path:
        """Resolve a path given relative to the working folder; it must be inside .tmp/."""
        ...

    def rel(self, path: Path) -> str:
        """The path relative to the working folder."""
        ...

    def exists(self, path: Path) -> bool: ...

    def read_text(self, path: Path) -> str: ...

    def read_bytes(self, path: Path) -> bytes: ...

    def write_text(self, path: Path, text: str) -> None:
        """Write the file, creating missing parent folders."""
        ...


class ZipEntry(Protocol):
    filename: str
    file_size: int


class StagingFs(LedgerStore, Protocol):
    """File operations for staging, discovering and renaming the files of one analysis."""

    def resolve_input(self, arg: str) -> Path:
        """Resolve an existing input file, folder or zip given relative to the working folder."""
        ...

    def analysis_root(self, run_id: str) -> Path:
        """The folder .tmp/<run_id> (absolute, resolved)."""
        ...

    def resolve_path(self, path: Path) -> Path: ...

    def is_dir(self, path: Path) -> bool: ...

    def is_file(self, path: Path) -> bool: ...

    def list_files(self, folder: Path) -> list[Path]:
        """All files below the folder, sorted; empty when the folder does not exist."""
        ...

    def write_bytes(self, path: Path, data: bytes) -> None:
        """Write the file, creating missing parent folders."""
        ...

    def rename(self, old: Path, new: Path) -> None: ...

    def list_zip(self, path: Path) -> list[ZipEntry]:
        """File entries of a zip; raises CorruptArchiveError when it cannot be opened."""
        ...

    def read_zip_entry(self, path: Path, name: str) -> bytes: ...


class Sources(Protocol):
    """Reads staged source files (PDF, spreadsheets, text) into documents."""

    def load(self, path: Path) -> Doc: ...


class InstitutionRegistry(Protocol):
    """Known institution modules; the first whose detect() matches wins."""

    def find(self, doc: Doc) -> Institution | None: ...

    def by_name(self, name: str) -> Institution:
        """Raises KeyError for an unknown name."""
        ...
