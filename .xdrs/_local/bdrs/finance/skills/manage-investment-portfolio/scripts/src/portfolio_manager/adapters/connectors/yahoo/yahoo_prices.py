"""Yahoo Finance connector: monthly closes for one ticker (unofficial public chart endpoint, no key, ticker sent only)."""

import json
import urllib.error
import urllib.parse
import urllib.request

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1mo&range=max&events=history"
MAX_BYTES = 2_000_000
USER_AGENT = "Mozilla/5.0 (compatible; portfolio-manager)"


def download_chart(ticker: str) -> tuple[dict | None, str]:
    """Return (payload, error); errors are values so offline runs fall back to the cached response."""
    request = urllib.request.Request(  # noqa: S310  (fixed https URL)
        URL.format(ticker=urllib.parse.quote(ticker, safe="")), headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:  # noqa: S310
            blob = resp.read(MAX_BYTES + 1)
        if len(blob) > MAX_BYTES:
            return None, "Yahoo response too large"
        return json.loads(blob.decode("utf-8")), ""
    except (urllib.error.URLError, OSError, ValueError) as err:
        return None, f"Yahoo download failed: {err}"
