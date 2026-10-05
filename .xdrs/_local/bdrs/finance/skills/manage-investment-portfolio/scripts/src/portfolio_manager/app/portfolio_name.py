"""Derive a default portfolio name from the account holder printed in statements. Holder names are kept in memory only."""

import re
import unicodedata
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from portfolio_manager.shared.models import Doc

PdfReader = Callable[[Path], Doc]


def slug(name: str) -> str:
    """Lowercase ascii slug usable in a work dir name ('Maria  Silva' -> 'maria-silva')."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")


def holders(sources: list[Path], reader: PdfReader, registry) -> list[str]:
    """Holder slug per source file whose adapter exposes holder(doc); unreadable or nameless files are skipped."""
    found = []
    for path in sources:
        doc = reader(path)
        if doc.status != "ok":
            continue
        adapter = registry.detect(doc)
        read_holder = getattr(adapter, "holder", None)
        name = slug(read_holder(doc)) if read_holder else ""
        if name:
            found.append(name)
    return found


def choose(found: list[str]) -> tuple[str | None, list[str]]:
    """The most frequent holder wins; none or a tie returns (None, candidates) so the caller asks the user."""
    ranked = Counter(found).most_common()
    if not ranked:
        return None, []
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        top = ranked[0][1]
        return None, sorted(name for name, count in ranked if count == top)
    return ranked[0][0], []
