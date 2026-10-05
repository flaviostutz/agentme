# Runtime: pytest; CSV dialect of the Portfolio Performance export on plain strings (no mocks).
from portfolio_manager.app import ppcsv


def test_dialect_uses_semicolons_and_quotes_only_when_needed():
    text = ppcsv.dumps(("a", "b"), [{"a": "x;y", "b": 'say "hi"'}, {"a": "plain"}])
    assert text == 'a;b\n"x;y";"say ""hi"""\nplain;\n'


def test_formula_like_text_is_prefixed_and_numbers_are_not():
    assert ppcsv.encode_cell("=SUM(A1)") == "'=SUM(A1)"
    assert ppcsv.encode_cell("-ETF") == "'-ETF"
    assert ppcsv.encode_cell("-12.5") == "-12.5"
    assert ppcsv.encode_cell(None) == ""


def test_decode_reverses_encode_for_any_text():
    for text in ("=1+1", "'quoted", "'", "@x", "+x", "plain", "-5", "", "\tx", "a;b\nc"):
        assert ppcsv.loads(ppcsv.dumps(("c",), [{"c": text}])) == [{"c": text}]


def test_decimal_comma_changes_only_the_portfolio_performance_number_columns():
    row = {"Value": "1.5", "Shares": "0.00000001", "Note": "a.b", "ledger_cash": "1.5"}
    text = ppcsv.dumps(("Value", "Shares", "Note", "ledger_cash"), [row], decimal_comma=True)
    assert text == 'Value;Shares;Note;ledger_cash\n"1,5";"0,00000001";a.b;1.5\n'.replace('"', "")
