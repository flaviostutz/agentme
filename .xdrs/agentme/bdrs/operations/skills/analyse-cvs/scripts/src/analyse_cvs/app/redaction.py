"""Redact labelled protected attributes and all images from converted CV markdown text."""

import re
import unicodedata

from analyse_cvs.shared.constants import MARK

LABELS = {
    "date_of_birth": [
        "date of birth", "birth date", "birthdate", "born", "dob", "d.o.b.", "age",
        "geboortedatum", "geboren", "leeftijd",
        "data de nascimento", "nascimento", "nascido", "nascida", "idade",
        "geburtsdatum", "geburtstag", "alter",
        "date de naissance", "né le", "née le", "âge",
        "fecha de nacimiento", "nacido", "nacida", "edad",
    ],
    "gender": [
        "gender", "sex", "geslacht", "gênero", "género", "sexo", "geschlecht", "genre", "sexe",
    ],
    "nationality": [
        "nationality", "citizenship", "nationaliteit", "nacionalidade", "cidadania",
        "staatsangehörigkeit", "staatsbürgerschaft", "nationalität",
        "nationalité", "citoyenneté", "nacionalidad", "ciudadanía",
    ],
    "ethnicity": [
        "ethnicity", "ethnic origin", "race", "etniciteit", "afkomst", "etnia", "raça",
        "ethnische herkunft", "ethnie", "origine ethnique", "origen étnico",
    ],
    "marital_status": [
        "marital status", "civil status", "relationship status", "burgerlijke staat",
        "estado civil", "familienstand", "situation familiale", "état civil",
    ],
    "children": [
        "children", "kids", "dependants", "dependents", "kinderen", "filhos", "kinder",
        "enfants", "hijos",
    ],
    "religion": [
        "religion", "religious affiliation", "faith", "religie", "geloof", "religião",
        "konfession", "religionszugehörigkeit", "religión",
    ],
    "health": [
        "health", "health status", "disability", "disabilities", "gezondheid", "handicap",
        "beperking", "saúde", "deficiência", "gesundheit", "behinderung", "santé", "salud",
        "discapacidad",
    ],
    "political": [
        "political affiliation", "political party", "political views", "politieke voorkeur",
        "politieke partij", "filiação política", "partido político", "parteizugehörigkeit",
        "affiliation politique", "parti politique", "afiliación política",
    ],
}  # fmt: skip

_LABEL_TO_CATEGORY = {label: cat for cat, labels in LABELS.items() for label in labels}
_ALT = "|".join(re.escape(label) for label in sorted(_LABEL_TO_CATEGORY, key=len, reverse=True))

# A label at line start, table cell start, bullet start or after an inline '·'/'•' separator,
# followed by ':' or a table cell separator. The value stops at the next separator.
FIELD_RE = re.compile(
    r"(?P<prefix>(?:^|[|·•])[ \t]*(?:[-*+][ \t]+)?(?:\*\*|__)?[ \t]*)"
    rf"(?P<label>{_ALT})"
    r"(?P<sep>[ \t]*(?:\*\*|__)?[ \t]*[:|][ \t]*(?:\*\*|__)?[ \t]*)"
    r"(?P<value>[^|·•\n]*?)"
    r"(?P<trail>[ \t]*(?=[|·•]|$))",
    re.IGNORECASE | re.MULTILINE,
)
IMAGE_RE = re.compile(r"!\[[^\]\n]*\]\([^)\n]*\)|!\[[^\]\n]*\]\[[^\]\n]*\]|<img\b[^>]*>", re.IGNORECASE)


def redact(text: str) -> tuple[str, dict[str, int]]:
    """Return the redacted text and the redaction count per category plus images."""
    counts = dict.fromkeys(LABELS, 0)
    counts["images"] = 0

    def field(m: re.Match[str]) -> str:
        value = m.group("value")
        if not value.strip() or value.strip() == MARK:
            return m.group(0)
        counts[_LABEL_TO_CATEGORY[m.group("label").lower()]] += 1
        return f"{m.group('prefix')}{m.group('label')}{m.group('sep')}{MARK}{m.group('trail')}"

    def image(_m: re.Match[str]) -> str:
        counts["images"] += 1
        return MARK

    text = unicodedata.normalize("NFC", text)
    text = IMAGE_RE.sub(image, text)
    text = FIELD_RE.sub(field, text)
    return text, counts
