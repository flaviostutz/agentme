# Shared pytest fixtures: a .tmp working folder and synthetic statements (fictitious names and accounts only).
from decimal import Decimal
from pathlib import Path

import pytest
from pdfminer.fontmetrics import FONT_METRICS

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import ledger
from analyse_account_transactions.shared.models import Ledger, Row

HOLDER = "Jane Doe"
OTHER = "John Roe"


def make_pdf(pages: list, size: int = 10) -> bytes:
    """Minimal Helvetica PDF; items are (x, y, text) or (x, y, text, 'right') with x as the right edge."""
    widths = FONT_METRICS["Helvetica"][1]
    streams = []
    for items in pages:
        ops = []
        for x, y, text, *align in items:
            if align:
                x -= sum(widths.get(c, 556) for c in text) * size / 1000
            raw = text.encode("cp1252").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            ops.append(b"BT /F1 %d Tf %.2f %d Td (" % (size, x, y) + raw + b") Tj ET")
        streams.append(b"\n".join(ops))
    n = len(pages)
    kids = b" ".join(b"%d 0 R" % (4 + 2 * i) for i in range(n))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [" + kids + b"] /Count %d >>" % n,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    for i, s in enumerate(streams):
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >>"
            b" /Contents %d 0 R >>" % (5 + 2 * i)
        )
        objects.append(b"<< /Length %d >>\nstream\n" % len(s) + s + b"\nendstream")
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for k, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % k + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


ABN_PAGES = [
    [
        (50, 800, "ABN AMRO Bank N.V. ABNANL2A"),
        (50, 786, f"Account holder name {HOLDER}"),
        (50, 772, "Personal Account NL00ABNA0000000001"),
        (50, 758, "Date interval 01-01-2026 until 31-01-2026"),
        (50, 744, "Balance 01-01-2026 € 100,00"),
        (50, 730, "Balance 31-01-2026 € 140,00"),
        (50, 700, "Date"),
        (120, 700, "Description"),
        (400, 700, "Debited", "right"),
        (480, 700, "Credited", "right"),
        (50, 680, "02-01-2026"),
        (120, 680, "BEA, Apple Pay Coffee Bar,PAS123 02.01.26/08:30"),
        (400, 680, "10,00", "right"),
        (50, 666, "05-01-2026"),
        (120, 666, "/TRTP/SEPA/NAME/ACME SALARY/REMI/January"),
        (480, 666, "50,00", "right"),
        (120, 652, "Omschrijving: payroll"),
        (50, 600, "Number of debit Number of credit"),
        (50, 586, "transactions transactions"),
        (50, 572, "1 1"),
        (50, 558, "Total amount debited Total amount credited"),
        (50, 544, "€ 10,00 € 50,00"),
    ]
]

N26_PAGES = [
    [
        (50, 800, "N26 Bank AG BIC: NTSBDEB1"),
        (50, 786, "IBAN: DE00100110010000000099 • BIC: NTSBDEB1"),
        (50, 772, "01.01.2026 until 31.01.2026"),
        (50, 740, "Description Booking Date Amount"),
        (50, 720, "Coffee Bar 02.01.2026 -10,00€"),
        (50, 706, "Mastercard • Food"),
        (50, 692, "Value Date 02.01.2026"),
        (50, 678, "ACME Salary 05.01.2026 +50,00€"),
        (50, 60, f"{HOLDER} Issued on"),
        (50, 46, "IBAN: DE00100110010000000001 • BIC: NTSBDEB1XXX"),
        (50, 32, "1 / 2"),
    ],
    [
        (50, 800, "Overview"),
        (50, 780, "Previous balance +100,00€"),
        (50, 766, "Outgoing transactions -10,00€"),
        (50, 752, "Incoming transactions +50,00€"),
        (50, 738, "Your new balance +140,00€"),
    ],
]

REVOLUT_PAGES = [
    [
        (50, 800, "EUR Statement"),
        (50, 786, "Revolut Bank UAB"),
        (50, 772, HOLDER),
        (50, 758, "IBAN LT000000000000000001"),
        (50, 744, "Transactions from January 1, 2026 to January 31, 2026"),
        (50, 730, "Account (Current Account) €100.00 €10.00 €50.00 €140.00"),
        (50, 700, "Date"),
        (120, 700, "Description"),
        (400, 700, "Money out", "right"),
        (480, 700, "Money in", "right"),
        (560, 700, "Balance", "right"),
        (50, 680, "Jan 2, 2026"),
        (120, 680, "Coffee Bar"),
        (400, 680, "€10.00", "right"),
        (560, 680, "€90.00", "right"),
        (50, 666, "Jan 5, 2026"),
        (120, 666, "Transfer from ACME"),
        (480, 666, "€50.00", "right"),
        (560, 666, "€140.00", "right"),
        (120, 652, "Reference: salary"),
        (50, 600, "Report lost or stolen card"),
    ]
]

SPLITWISE_CSV = (
    f"Date,Description,Category,Cost,Currency,{HOLDER},{OTHER}\n"
    "\n"
    "2026-01-03,Dinner,Dining out,60.00,EUR,30.00,-30.00\n"
    "2026-01-10,Groceries,Groceries,20.00,EUR,-10.00,10.00\n"
    "2026-01-12,Taxi,Taxi,15.00,USD,7.50,-7.50\n"
    "2026-01-15,Note,General,0.00,EUR,0.00,0.00\n"
    "\n"
    f" ,Total balance, , ,EUR,20.00,-20.00\n"
)


@pytest.fixture
def work(tmp_path, monkeypatch) -> Path:
    """Empty project folder with .tmp/, used as the current directory."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tmp").mkdir()
    return tmp_path


def row(ts, title, value, category="", flow="", relevance="", needs="", desc="") -> Row:
    return Row(ts, title, Decimal(value), desc or f"{title} payment", category, flow, relevance, needs)


def write_ledger(path: Path, rows: list, **meta) -> Path:
    base = {
        "source": "src.csv",
        "normalizer": "llm",
        "bank": "Test Bank",
        "account-type": "current",
        "account-holder": HOLDER,
        "iban": "NL00TEST0000000001",
        "currency": "EUR",
        "period": "2026-01-01..2026-01-31",
        "opening-balance": "none",
        "closing-balance": "none",
    }
    base.update({k.replace("_", "-"): v for k, v in meta.items()})
    path.parent.mkdir(parents=True, exist_ok=True)
    write(path, Ledger(base, list(rows)))
    return path


STORE = LocalWorkspace(Path("/"))


def read(path: Path) -> Ledger:
    return ledger.read(STORE, path)


def write(path: Path, led: Ledger) -> None:
    ledger.write(STORE, path, led)


def write_snapshot(path: Path, led: Ledger, user: dict) -> None:
    ledger.write_snapshot(STORE, path, led, user)


def load_snapshot(path: Path) -> dict:
    return ledger.load_snapshot(STORE, path)
