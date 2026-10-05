"""ECB connector: euro reference rates downloaded as a CSV zip and cached in the work dir."""

import io
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path

from portfolio_manager.app.fx import Rates, parse_ecb_csv

ECB_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"


def download_ecb() -> tuple[str, str]:
    """Return (csv_text, error); errors are values so offline runs degrade to statement rates."""
    try:
        with urllib.request.urlopen(ECB_URL, timeout=30) as resp:  # fixed https URL
            blob = resp.read()
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            return zf.read(zf.namelist()[0]).decode("utf-8"), ""
    except (urllib.error.URLError, OSError, zipfile.BadZipFile, KeyError, IndexError) as err:
        return "", f"ECB download failed: {err}"


def load_cached(
    cache_file: Path, needed_until: str, downloader: Callable[[], tuple[str, str]] = download_ecb
) -> tuple[Rates, str]:
    """Use the cached CSV when it covers needed_until, else download and cache it. Returns (Rates, notice)."""
    text = cache_file.read_text(encoding="utf-8") if cache_file.is_file() else ""
    ecb = parse_ecb_csv(text) if text else {}
    covered = max((max(s) for s in ecb.values()), default="")
    if covered >= needed_until:
        return Rates(ecb), ""
    fresh, err = downloader()
    if err or not fresh:
        return Rates(ecb), err or "ECB download returned no data"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(fresh, encoding="utf-8")
    return Rates(parse_ecb_csv(fresh)), ""
