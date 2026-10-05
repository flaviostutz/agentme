# Runtime: pytest; ECB parsing, prior-day fallback, statement fallback and cache behaviour (downloader is an injected plain function).
from decimal import Decimal

from portfolio_manager.app import fx

CSV = "Date,USD,BRL,\n2025-01-03,1.04,6.40,\n2025-01-02,1.03,N/A,\n"


def test_parse_ecb_csv_skips_na_and_blank_columns():
    rates = fx.parse_ecb_csv(CSV)
    assert rates["USD"]["2025-01-02"] == Decimal("1.03")
    assert "2025-01-02" not in rates["BRL"]
    assert "" not in rates


def test_rate_exact_prior_day_statement_and_unavailable():
    r = fx.Rates(fx.parse_ecb_csv(CSV))
    assert r.rate("EUR", "2025-05-05") == {"rate": Decimal(1), "rate_date": "2025-05-05", "status": "exact"}
    assert r.rate("USD", "2025-01-03")["status"] == "exact"
    weekend = r.rate("USD", "2025-01-05")
    assert weekend["status"] == "prior-day rate" and weekend["rate_date"] == "2025-01-03"
    assert r.rate("USD", "2025-03-01")["status"] == "unavailable"
    r.add_statement("USD", "2025-03-01", Decimal("1.1"))
    assert r.rate("USD", "2025-03-01")["status"] == "statement"


def test_to_eur_converts_or_reports_unavailable():
    r = fx.Rates(fx.parse_ecb_csv(CSV))
    assert r.to_eur(Decimal(104), "USD", "2025-01-03") == (Decimal(100), "exact")
    assert r.to_eur(Decimal(1), "CHF", "2025-01-03") == (None, "unavailable")
