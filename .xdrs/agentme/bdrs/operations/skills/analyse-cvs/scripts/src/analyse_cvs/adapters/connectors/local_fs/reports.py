"""Read and write the analysis report, which must live inside .tmp/."""

from pathlib import Path


def resolve_report(report: str, cwd: Path) -> Path:
    """Return the absolute report path, which must be an existing markdown file inside <cwd>/.tmp."""
    root = (cwd / ".tmp").resolve()
    path = (cwd / report).resolve()
    if root not in path.parents or path.suffix != ".md":
        msg = f"report must be a .md file inside {root}: {path}"
        raise ValueError(msg)
    if not path.is_file():
        msg = f"report does not exist: {path}"
        raise ValueError(msg)
    return path


def read_lines(path: Path) -> list[str]:
    """Read the report as lines without line terminators."""
    return path.read_text(encoding="utf-8").split("\n")


def write_lines(path: Path, lines: list[str]) -> None:
    """Write the lines back with a single trailing newline."""
    text = "\n".join(lines).rstrip("\n")
    path.write_text(text + "\n", encoding="utf-8")
