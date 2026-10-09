"""Yahoo chart download behaviour; urlopen is replaced by a plain function and nothing leaves the machine."""

import io
import json
import urllib.error

from portfolio_manager.adapters.connectors.yahoo import yahoo_prices


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_download_returns_the_parsed_payload_and_only_sends_the_quoted_ticker(monkeypatch):
    seen = []

    def fake(request, timeout):
        seen.append((request.full_url, timeout))
        return _Resp(json.dumps({"chart": {"result": []}}).encode())

    monkeypatch.setattr(yahoo_prices.urllib.request, "urlopen", fake)
    assert yahoo_prices.download_chart("IWDA.AS") == ({"chart": {"result": []}}, "")
    assert seen[0][0].startswith("https://query1.finance.yahoo.com/v8/finance/chart/IWDA.AS?")


def test_download_failure_is_returned_as_a_value(monkeypatch):
    def boom(*_a, **_k):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(yahoo_prices.urllib.request, "urlopen", boom)
    payload, err = yahoo_prices.download_chart("IWDA.AS")
    assert payload is None and "Yahoo download failed" in err


def test_invalid_json_and_oversized_responses_are_errors(monkeypatch):
    monkeypatch.setattr(yahoo_prices.urllib.request, "urlopen", lambda *_a, **_k: _Resp(b"<html>"))
    assert yahoo_prices.download_chart("X")[0] is None
    monkeypatch.setattr(yahoo_prices, "MAX_BYTES", 5)
    monkeypatch.setattr(yahoo_prices.urllib.request, "urlopen", lambda *_a, **_k: _Resp(b"0123456789"))
    assert yahoo_prices.download_chart("X") == (None, "Yahoo response too large")
