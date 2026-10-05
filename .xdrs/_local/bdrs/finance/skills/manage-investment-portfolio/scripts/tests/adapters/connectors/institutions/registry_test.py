"""Registry detection over synthetic documents."""

from portfolio_manager.adapters.connectors.institutions import default_registry
from samples_test import bb_portfolio, revolut_statement, trading212


def test_registry_detects_the_right_adapter(make_doc):
    registry = default_registry()
    assert registry.detect(make_doc(trading212())).NAME == "trading212"
    assert registry.detect(make_doc(revolut_statement())).NAME == "revolut_statement"
    assert registry.detect(make_doc(bb_portfolio())).NAME == "bb_portfolio"
    assert registry.detect(make_doc([["unknown layout"]])) is None
    assert registry.by_name("bb_informe").NAME == "bb_informe" and registry.by_name("nope") is None
