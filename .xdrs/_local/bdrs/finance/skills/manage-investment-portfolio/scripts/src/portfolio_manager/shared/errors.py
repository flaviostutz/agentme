"""Error types shared across layers."""


class PmError(ValueError):
    """Invalid input: path, file layout, plan or answer. Maps to exit code 2."""
