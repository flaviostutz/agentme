# Python 3.11+ pytest suite; run with: make test
import pytest

from analyse_cvs.app.slugs import make_slugs, slugify


@pytest.mark.parametrize(
    ("text", "slug"),
    [
        ("Roger Mathias", "roger-mathias"),
        ("Business Analyst (AI)", "business-analyst-ai"),
        ("José Álvarez-Núñez", "jose-alvarez-nunez"),
        ("Søren Straße", "soren-strasse"),
        ("  --Anna  ", "anna"),
    ],
)
def test_slugify(text, slug):
    assert slugify(text) == slug


def test_slugify_rejects_empty_result():
    with pytest.raises(ValueError, match="no slug"):
        slugify("???")


def test_make_slugs_suffixes_duplicates_and_existing():
    assert make_slugs(["Anna Silva", "Anna Silva", "Bo"], ["bo"]) == ["anna-silva", "anna-silva-2", "bo-2"]
