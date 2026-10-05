"""Fingerprint source PDFs: institution keywords, vocabulary terms, date and number formats, text quality."""

import re
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import sha256_file

INSTITUTIONS = {
    "n26": r"\bn26\b",
    "upvest": r"\bupvest\b",
    "trading212": r"trading\s*212",
    "revolut": r"\brevolut\b",
    "interactive-brokers": r"interactive\s+brokers|\bibkr\b",
    "degiro": r"\bdegiro\b|\bflatex\b",
    "scalable": r"scalable\s+capital",
    "trade-republic": r"trade\s+republic",
    "xp": r"\bxp\s+(inc|investimentos)\b",
    "btg": r"\bbtg\b",
    "nubank": r"\bnu\s?(bank|invest)\b|\bnuinvest\b",
    "avenue": r"\bavenue\b",
    "itau": r"\bita[uú]\b",
    "bradesco": r"\bbradesco\b",
    "banco-do-brasil": r"\bbanco do brasil\b|bb\.com\.br",
    "bunq": r"\bbunq\b",
    "abn-amro": r"\babn\s*amro\b",
    "etoro": r"\betoro\b",
    "schwab": r"\bschwab\b",
    "fidelity": r"\bfidelity\b",
    "lightyear": r"\blightyear\b",
    "xtb": r"\bxtb\b",
}
VOCAB = [
    "statement",
    "account",
    "summary",
    "trades",
    "trade",
    "dividend",
    "dividends",
    "interest",
    "deposits",
    "withdrawals",
    "positions",
    "holdings",
    "portfolio",
    "quantity",
    "price",
    "fee",
    "fees",
    "commission",
    "tax",
    "withholding",
    "isin",
    "symbol",
    "buy",
    "sell",
    "cash",
    "balance",
    "transfer",
    "realized",
    "unrealized",
    "cost basis",
    "market value",
    "performance",
    "costs",
    "quarterly",
    "annual",
    "orders",
    "execution",
    "extrato",
    "relatório",
    "investimentos",
    "posição",
    "carteira",
    "rendimento",
    "compra",
    "venda",
    "saldo",
    "comprovante",
    "depot",
    "wertpapier",
    "kauf",
    "verkauf",
    "steuer",
    "kosten",
    "bestand",
]
DATE_FORMATS = {
    "dd/mm/yyyy": r"\b\d{2}/\d{2}/\d{4}\b",
    "dd.mm.yyyy": r"\b\d{2}\.\d{2}\.\d{4}\b",
    "yyyy-mm-dd": r"\b\d{4}-\d{2}-\d{2}\b",
    "d Mon yyyy": r"\b\d{1,2} [A-Z][a-z]{2,8}\.? \d{4}\b",
}
NUMBER_FORMATS = {
    "comma-decimal": r"\b\d{1,3}(?:\.\d{3})*,\d{2,}\b",
    "dot-decimal": r"\b\d{1,3}(?:,\d{3})*\.\d{2,}\b",
}
CURRENCIES = ["EUR", "USD", "BRL", "GBP", "R$", "US$", "€", "$"]


def _heading_candidates(lines: list) -> list:
    out = [s for s in lines if 3 <= len(s) <= 50 and not re.search(r"\d", s) and any(v in s.lower() for v in VOCAB)]
    return [h for h, _ in Counter(out).most_common(25)]


def inspect_pdf(path: Path, reader: Callable[[Path], Doc]) -> dict[str, Any]:
    doc = reader(path)
    info = {"file": path.name, "sha256": sha256_file(path)[:16], "bytes": path.stat().st_size, "status": doc.status}
    if doc.status in ("encrypted", "unreadable"):
        info["error"] = doc.error
        return info
    text = doc.text()
    low = text.lower()
    info.update(
        {
            "pages": len(doc.pages),
            "chars": len(text),
            "pdf_producer": doc.metadata.get("producer", ""),
            "institutions": {k: n for k, rx in INSTITUTIONS.items() if (n := len(re.findall(rx, low)))},
            "vocab": {v: n for v in VOCAB if (n := low.count(v))},
            "date_formats": {k: n for k, rx in DATE_FORMATS.items() if (n := len(re.findall(rx, text)))},
            "number_formats": {k: n for k, rx in NUMBER_FORMATS.items() if (n := len(re.findall(rx, text)))},
            "currencies": {c: n for c in CURRENCIES if (n := text.count(c))},
            "isin_count": len(re.findall(r"\b[A-Z]{2}[A-Z0-9]{9}\d\b", text)),
            "headings": _heading_candidates(doc.lines()),
        }
    )
    return info
