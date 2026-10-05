"""Derive plain ASCII kebab-case slugs for roles and candidates."""

import re
import unicodedata
from collections.abc import Iterable

_TRANSLIT = str.maketrans(
    {"ß": "ss", "ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "đ": "d", "ł": "l"}
)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Return lowercase ASCII kebab-case of text, or raise ValueError when nothing is left."""
    folded = unicodedata.normalize("NFKD", text.translate(_TRANSLIT)).encode("ascii", "ignore").decode("ascii")
    slug = _NON_ALNUM.sub("-", folded.lower()).strip("-")
    if not slug:
        msg = f"no slug can be derived from {text!r}"
        raise ValueError(msg)
    return slug


def make_slugs(names: list[str], existing: Iterable[str] = ()) -> list[str]:
    """Slugify each name as a different person, adding -2, -3 when a slug is already taken."""
    taken = set(existing)
    slugs: list[str] = []
    for name in names:
        base = slugify(name)
        slug, n = base, 2
        while slug in taken:
            slug = f"{base}-{n}"
            n += 1
        taken.add(slug)
        slugs.append(slug)
    return slugs
