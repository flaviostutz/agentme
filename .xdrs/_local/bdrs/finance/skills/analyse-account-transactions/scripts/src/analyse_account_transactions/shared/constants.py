"""Vocabulary of the normalized transaction format and the source formats the scripts read."""

import re
from decimal import Decimal

CREDIT_CATEGORIES = ["Income", "Transfers In"]
DEBIT_CATEGORIES = [
    "Housing & Utilities",
    "Groceries & Household",
    "Transport",
    "Health & Insurance",
    "Eating Out",
    "Leisure, Shopping & Gifts",
    "Obligations & Family",
    "Transfers Out & Savings",
]
UNKNOWN = "Unknown"
CATEGORIES = [*CREDIT_CATEGORIES, *DEBIT_CATEGORIES, UNKNOWN]
FLOWS = ["Income", "Savings", "Expenditure"]
RELEVANCES = ["Essential", "Important", "Discretionary"]
NEEDS = ["yes", "no", "user"]
COLUMNS = ["timestamp", "title", "value", "description", "category", "flow", "relevance", "needs-investigation"]
CLASS_FIELDS = ["category", "flow", "relevance"]
META_KEYS = [
    "source",
    "normalizer",
    "bank",
    "account-type",
    "account-holder",
    "iban",
    "currency",
    "period",
    "opening-balance",
    "closing-balance",
]
NORMALIZERS = re.compile(r"^(?:module:[a-z0-9_]+|mapping|llm|llm-image)$")
MAX_TITLE_WORDS = 4
MAX_DESCRIPTION = 399
CENT = Decimal("0.01")

PDF = {".pdf"}
TABLE = {".csv", ".txt", ".tab", ".xlsx"}
TEXT = {".xml", ".ofx", ".qfx", ".qif", ".sta", ".mt940", ".940", ".json"}
IMAGE = {".png", ".jpg", ".jpeg", ".heic"}
LLM_ONLY = {".xls", ".ods"}
SUPPORTED = PDF | TABLE | TEXT | IMAGE | LLM_ONLY
