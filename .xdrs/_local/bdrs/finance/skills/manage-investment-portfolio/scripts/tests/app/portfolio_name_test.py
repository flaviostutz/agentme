# Runtime: pytest; portfolio name derivation from statement holders (synthetic data only).
from portfolio_manager.adapters.connectors.institutions import default_registry
from portfolio_manager.adapters.connectors.pdf.pdf_reader import read_pdf
from portfolio_manager.app import portfolio_name
from samples_test import bb_informe, trading212


def test_slug_folds_accents_and_punctuation():
    assert portfolio_name.slug("  José  D'Ávila-Silva ") == "jose-d-avila-silva"
    assert portfolio_name.slug("!!!") == ""


def test_choose_picks_the_most_frequent_holder():
    assert portfolio_name.choose(["ana", "bia", "ana"]) == ("ana", [])
    assert portfolio_name.choose(["ana"]) == ("ana", [])


def test_choose_returns_candidates_on_tie_and_nothing_when_empty():
    assert portfolio_name.choose(["bia", "ana"]) == (None, ["ana", "bia"])
    assert portfolio_name.choose(["ana", "ana", "bia", "bia", "cris"]) == (None, ["ana", "bia"])
    assert portfolio_name.choose([]) == (None, [])


def test_holders_skip_unreadable_files_and_adapters_without_a_holder(make_pdf):
    pages = bb_informe()
    other = bb_informe()
    other[0][3] = "41930 OUTRA PESSOA"
    paths = [
        make_pdf(pages, "a.pdf"),
        make_pdf(other, "b.pdf"),
        make_pdf(trading212(), "t212.pdf"),
        make_pdf([[]], "blank.pdf"),
    ]
    found = portfolio_name.holders(paths, read_pdf, default_registry())
    assert sorted(found) == ["outra-pessoa", "titular-ficticio"]
