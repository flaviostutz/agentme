# Licensing

The scripts depend on `pymupdf` (PDF text extraction), which is licensed under the GNU AGPL v3 (a commercial
licence is available from Artifex). It is downloaded by `uv` at run time and is not vendored or redistributed
by this repository. Using the skill locally on one's own statements is not affected. Anyone who bundles or
serves the scripts together with `pymupdf` as a network service must check the AGPL terms or obtain the
commercial licence. `pyyaml` is MIT licensed.

ECB reference rates come from the public ECB statistical data warehouse (`eurofxref-hist.zip`); keep the cache
file when working offline.
