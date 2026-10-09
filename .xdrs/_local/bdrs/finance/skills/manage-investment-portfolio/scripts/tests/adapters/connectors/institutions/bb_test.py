# Runtime: pytest; Banco do Brasil portfolio and annual income adapters on fictitious layouts.
from decimal import Decimal

import pytest

from portfolio_manager.adapters.connectors.institutions import bb_informe, bb_portfolio
from portfolio_manager.shared.errors import PmError
from samples_test import bb_informe as informe_pages
from samples_test import bb_portfolio as portfolio_pages


def test_portfolio_parses_both_ends_flows_and_unsupported_savings(make_doc):
    assert bb_portfolio.detect(make_doc(portfolio_pages()))
    (res,) = bb_portfolio.parse(make_doc(portfolio_pages()), {})
    assert res["account"] == {
        "id": "bb-1930",
        "institution": "banco-do-brasil",
        "currency": "BRL",
        "mode": "value-only",
    }
    start, end = res["snapshots"]
    assert (start["date"], end["date"]) == ("2025-01-01", "2025-01-31")
    assert (start["positions_value"], end["positions_value"], end["total"]) == ("1500", "1600", "1600")
    cdb, savings = end["positions"]
    assert cdb["security_class"] == "fixed-income" and "unsupported" not in cdb
    assert savings["security_class"] == "savings" and savings["unsupported"] == "savings product"
    flows = [r for r in res["references"] if r["kind"] == "period-flows"]
    assert (flows[0]["entries"], flows[0]["exits"]) == ("200", "100")
    assert all(c["level"] == "ok" for c in res["checks"])


def test_portfolio_cover_total_mismatch_fails(make_doc):
    (res,) = bb_portfolio.parse(make_doc(portfolio_pages(end_total="R$ 9.999,00")), {})
    assert res["checks"][-1]["level"] == "fail"


def test_portfolio_layout_errors(make_doc):
    with pytest.raises(PmError):
        bb_portfolio.parse(make_doc([["PORTFÓLIO DE INVESTIMENTOS", "bb.com.br"]]), {})
    pages = portfolio_pages()
    pages[0].remove("Distribuição da carteira")
    with pytest.raises(PmError):
        bb_portfolio.parse(make_doc(pages), {})


def test_portfolio_without_rows_is_unresolved(make_doc):
    pages = portfolio_pages()
    i = pages[0].index("CDB TESTE")
    del pages[0][i : i + 16]
    (res,) = bb_portfolio.parse(make_doc(pages), {})
    assert [u["kind"] for u in res["unresolved"]] == ["no-positions"]


def test_informe_year_end_balances_per_section(make_doc):
    assert bb_informe.detect(make_doc(informe_pages()))
    (res,) = bb_informe.parse(make_doc(informe_pages()), {})
    assert res["account"]["id"] == "bb-1930"
    refs = res["references"]
    assert [(r["section"], r["security"]) for r in refs] == [("exempt", "Cdb Teste"), ("current-account", "Saldo Cc")]
    assert (refs[0]["start"], refs[0]["end"], refs[0]["income"]) == ("1000", "1100", "50")
    assert refs[1]["income"] is None and Decimal(refs[1]["end"]) == 20


def test_informe_bad_layout_raises(make_doc):
    with pytest.raises(PmError):
        bb_informe.parse(make_doc([["Informe de Rendimentos Financeiros"]]), {})


def test_informe_holder_reads_the_name_but_never_the_account_number_or_cpf(make_doc):
    assert bb_informe.holder(make_doc(informe_pages())) == "TITULAR FICTICIO"
    pages = informe_pages()
    pages[0][3] = "41930 TITULAR FICTICIO 123.456.789-00"
    assert bb_informe.holder(make_doc(pages)) == "TITULAR FICTICIO"
    assert bb_informe.holder(make_doc([["Informe de Rendimentos Financeiros"]])) == ""
    assert bb_informe.holder(make_doc([["Conta Nome"]])) == ""
