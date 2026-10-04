# Runtime: pytest; ECB parsing, prior-day fallback, statement fallback and cache behaviour (downloader is an injected plain function).
from decimal import Decimal

import fx

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


def test_load_cached_uses_cache_when_it_covers_the_period(tmp_path):
    cache = tmp_path / "ecb.csv"
    cache.write_text(CSV, encoding="utf-8")

    def never():
        raise AssertionError("must not download")

    rates, notice = fx.load_cached(cache, "2025-01-03", never)
    assert notice == "" and rates.rate("USD", "2025-01-03")["status"] == "exact"


def test_load_cached_downloads_and_caches(tmp_path):
    cache = tmp_path / "sub" / "ecb.csv"
    rates, notice = fx.load_cached(cache, "2025-01-03", lambda: (CSV, ""))
    assert notice == "" and cache.read_text(encoding="utf-8") == CSV
    assert rates.rate("USD", "2025-01-02")["status"] == "exact"


def test_load_cached_download_failure_degrades_to_notice(tmp_path):
    rates, notice = fx.load_cached(tmp_path / "missing.csv", "2025-01-03", lambda: ("", "offline"))
    assert notice == "offline" and rates.rate("USD", "2025-01-03")["status"] == "unavailable"
    _, empty_notice = fx.load_cached(tmp_path / "missing.csv", "2025-01-03", lambda: ("", ""))
    assert "no data" in empty_notice
