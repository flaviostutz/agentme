"""Classifications: the research queue lists only ISIN, ticker and name; imported entries need a source URL and an as-of date."""

import re
from datetime import date
from decimal import Decimal

SECURITY_CLASSES = ("equity", "bond", "fund", "etf", "cash", "commodity", "crypto", "real-estate", "other")
FIELDS = (
    "isin",
    "ticker",
    "name",
    "security_class",
    "region",
    "country",
    "sector",
    "currency",
    "exchange",
    "theme",
    "issuer",
    "source_url",
    "as_of",
)
REQUIRED = ("isin", "security_class", "source_url", "as_of")
ISIN = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}\d$")


def queue(securities: list, known: list) -> list:
    """Securities still lacking a classification, with identifiers only."""
    have = {k["isin"] for k in known}
    seen, out = set(), []
    for a in securities:
        key = a["isin"]
        if key and key not in have and key not in seen and not a.get("unsupported"):
            seen.add(key)
            out.append({"isin": key, "ticker": a["symbol"], "name": a["name"]})
    return sorted(out, key=lambda r: r["isin"])


def validate(entries) -> tuple:
    """Return (valid entries, errors). Unknown fields (for example amounts or accounts) are rejected."""
    if not isinstance(entries, list):
        return [], ["classifications must be a JSON list of objects"]
    valid, errors = [], []
    for i, e in enumerate(entries):
        where = f"entry {i}"
        if not isinstance(e, dict):
            errors.append(f"{where}: must be an object")
            continue
        extra = sorted(set(e) - set(FIELDS))
        problems = [f"unknown field(s) {', '.join(extra)}"] if extra else []
        problems += [f"missing {f}" for f in REQUIRED if not e.get(f)]
        if e.get("isin") and not ISIN.match(str(e["isin"])):
            problems.append("isin is not a valid ISIN")
        if e.get("security_class") and e["security_class"] not in SECURITY_CLASSES:
            problems.append(f"security_class must be one of {', '.join(SECURITY_CLASSES)}")
        if e.get("source_url") and not str(e["source_url"]).startswith("https://"):
            problems.append("source_url must be an https URL")
        if e.get("as_of"):
            try:
                date.fromisoformat(e["as_of"])
            except (TypeError, ValueError):
                problems.append("as_of must be YYYY-MM-DD")
        if problems:
            errors.append(f"{where} ({e.get('isin', '?')}): " + "; ".join(problems))
        else:
            valid.append({f: e[f] for f in FIELDS if e.get(f)})
    return valid, errors


def merge(existing: list, new: list) -> list:
    """New entries replace older ones for the same ISIN."""
    by_isin = {e["isin"]: e for e in existing}
    by_isin.update({e["isin"]: e for e in new})
    return [by_isin[k] for k in sorted(by_isin)]


def allocation(securities: list, known: list, field: str) -> dict:
    """EUR value per classification value (securities without a classification are grouped as 'unclassified')."""
    by_isin = {k["isin"]: k for k in known}
    out: dict = {}
    for a in securities:
        if a.get("unsupported") or a.get("value_eur") is None:
            continue
        label = (
            by_isin.get(a["isin"], {}).get(field)
            or (a.get("security_class") if field == "security_class" else None)
            or "unclassified"
        )
        out[label] = out.get(label, Decimal(0)) + Decimal(a["value_eur"])
    return out
