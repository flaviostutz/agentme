"""ECB cache and download behaviour; the downloader is an injected plain function."""

import io
import urllib.error
import zipfile

from portfolio_manager.adapters.connectors.ecb import ecb_rates
from portfolio_manager.adapters.connectors.ecb.ecb_rates import load_cached

CSV = "Date,USD,BRL,\n2025-01-03,1.04,6.40,\n2025-01-02,1.03,N/A,\n"


def test_load_cached_uses_cache_when_it_covers_the_period(tmp_path):
    cache = tmp_path / "ecb.csv"
    cache.write_text(CSV, encoding="utf-8")

    def never():
        raise AssertionError("must not download")

    rates, notice = load_cached(cache, "2025-01-03", never)
    assert notice == "" and rates.rate("USD", "2025-01-03")["status"] == "exact"


def test_load_cached_downloads_and_caches(tmp_path):
    cache = tmp_path / "sub" / "ecb.csv"
    rates, notice = load_cached(cache, "2025-01-03", lambda: (CSV, ""))
    assert notice == "" and cache.read_text(encoding="utf-8") == CSV
    assert rates.rate("USD", "2025-01-02")["status"] == "exact"


def test_load_cached_download_failure_degrades_to_notice(tmp_path):
    rates, notice = load_cached(tmp_path / "missing.csv", "2025-01-03", lambda: ("", "offline"))
    assert notice == "offline" and rates.rate("USD", "2025-01-03")["status"] == "unavailable"
    _, empty_notice = load_cached(tmp_path / "missing.csv", "2025-01-03", lambda: ("", ""))
    assert "no data" in empty_notice


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_download_ecb_reads_the_zipped_csv(monkeypatch):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("eurofxref-hist.csv", CSV)
    monkeypatch.setattr(ecb_rates.urllib.request, "urlopen", lambda *_a, **_k: _Resp(buf.getvalue()))
    assert ecb_rates.download_ecb() == (CSV, "")


def test_download_ecb_failure_is_returned_as_a_value(monkeypatch):
    def boom(*_a, **_k):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(ecb_rates.urllib.request, "urlopen", boom)
    text, err = ecb_rates.download_ecb()
    assert text == "" and "ECB download failed" in err
