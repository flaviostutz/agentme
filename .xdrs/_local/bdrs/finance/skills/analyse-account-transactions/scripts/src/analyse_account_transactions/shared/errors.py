"""Errors raised by the scripts; the CLIs report them as `error: <message>` with exit code 2."""


class LedgerError(ValueError):
    """Invalid input: path, file layout or plan."""


class CorruptArchiveError(LedgerError):
    """A zip archive that cannot be opened."""
