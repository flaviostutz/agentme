# Runtime: pytest; Portfolio Performance export and CSV round trip on plain in-memory ledgers (no mocks).
import json
from decimal import Decimal

import pytest

from portfolio_manager.app import export_pp, import_pp, ppcsv
from portfolio_manager.app.records import event, snapshot
from portfolio_manager.shared.errors import PmError

ISIN = "IE00B4L5Y983"
ACCOUNTS = [
    {"id": "t212-1", "institution": "trading212", "currency": "EUR", "mode": "transactions"},
    {"id": "bb-1", "institution": "banco-do-brasil", "currency": "BRL", "mode": "value-only"},
]
OPENINGS = {
    "t212-1": {
        "date": "2024-12-31",
        "cash": "100",
        "positions": [{"isin": ISIN, "symbol": "IWDA", "name": "MSCI World", "quantity": "3"}],
    }
}


def ev(etype: str, day: str, ref: str, **kw) -> dict:
    kw.setdefault("currency", "EUR")
    return event("t212-1", etype, day, ref, **kw)


def ledger(events: list | None = None) -> dict:
    return {
        "accounts": {"accounts": ACCOUNTS, "openings": OPENINGS},
        "events": events if events is not None else [],
        "snapshots": [snapshot("bb-1", "2025-01-31", [], total="10", currency="BRL", ref="s1")],
        "references": [{"kind": "year-end-balance", "account": "bb-1", "year": 2024, "income": None}],
    }


def rows(files: dict, name: str) -> list[dict]:
    return ppcsv.loads(files[name])


def test_every_event_type_maps_to_a_portfolio_performance_type():
    asset = {"isin": ISIN, "symbol": "IWDA", "name": "MSCI World"}
    events = [
        ev("DEPOSIT", "2025-01-02", "1", cash="500"),
        ev("BUY", "2025-01-03", "2", quantity="2", cash="-101.5", fee="1.5", **asset),
        ev("SELL", "2025-01-04", "3", quantity="1", cash="49", fee="1", **asset),
        ev("INTEREST", "2025-01-05", "4", cash="0.5"),
        ev("INTEREST", "2025-01-06", "5", cash="-0.2"),
        ev("FEE", "2025-01-07", "6", cash="-2"),
        ev("FEE", "2025-01-08", "7", cash="2"),
        ev("TAX", "2025-01-09", "8", cash="-3"),
        ev("WITHDRAWAL", "2025-01-10", "9", cash="-50"),
        ev("SPLIT", "2025-01-11", "10", quantity="9", **asset),
        ev("SPLIT", "2025-01-12", "11", quantity="-9", **asset),
        ev("TRANSFER_IN", "2025-01-13", "12", quantity="4", **asset),
        ev("TRANSFER_OUT", "2025-01-14", "13", quantity="4", **asset),
        ev("TRANSFER_IN", "2025-01-15", "14", cash="20"),
    ]
    files = export_pp.build(ledger(events))
    portfolio = [(r["Type"], r["Value"], r["Shares"]) for r in rows(files, ppcsv.PORTFOLIO_TRANSACTIONS)]
    account = [(r["Type"], r["Value"]) for r in rows(files, ppcsv.ACCOUNT_TRANSACTIONS)]
    assert portfolio == [
        ("Delivery (Inbound)", "0", "3"),
        ("Buy", "101.5", "2"),
        ("Sell", "49", "1"),
        ("Delivery (Inbound)", "0", "9"),
        ("Delivery (Outbound)", "0", "9"),
        ("Transfer (Inbound)", "0", "4"),
        ("Transfer (Outbound)", "0", "4"),
    ]
    assert account == [
        ("Deposit", "100"),
        ("Deposit", "500"),
        ("Interest", "0.5"),
        ("Interest Charge", "0.2"),
        ("Fees", "2"),
        ("Fees Refund", "2"),
        ("Taxes", "3"),
        ("Removal", "50"),
        ("Transfer (Inbound)", "20"),
    ]
    assert export_pp.verify(ledger(events), files) == []


def test_trade_fees_and_dividend_gross_are_exported_but_dividend_tax_is_not_a_pp_column():
    events = [
        ev("BUY", "2025-01-03", "2", quantity="2", cash="-101.5", fee="1.5", tax="0.2", isin=ISIN, symbol="IWDA"),
        ev("DIVIDEND", "2025-02-01", "3", quantity="5", cash="12.4", tax="1.86", gross="15", currency="USD", isin=ISIN),
    ]
    files = export_pp.build(ledger(events))
    buy = rows(files, ppcsv.PORTFOLIO_TRANSACTIONS)[1]
    dividend = rows(files, ppcsv.ACCOUNT_TRANSACTIONS)[1]
    assert (buy["Fees"], buy["Taxes"], buy["Gross Amount"]) == ("1.5", "0.2", "")
    assert (dividend["Type"], dividend["Value"], dividend["Gross Amount"], dividend["Currency Gross Amount"]) == (
        "Dividend",
        "12.4",
        "15",
        "USD",
    )
    assert (dividend["Taxes"], dividend["ledger_tax"]) == ("", "1.86")


def test_openings_are_marked_and_dated_and_cash_accounts_are_named_per_currency():
    files = export_pp.build(ledger())
    position = rows(files, ppcsv.PORTFOLIO_TRANSACTIONS)[0]
    cash = rows(files, ppcsv.ACCOUNT_TRANSACTIONS)[0]
    assert (position["ledger_type"], position["Date"], position["Value"], position["Shares"]) == (
        "OPENING",
        "2024-12-31",
        "0",
        "3",
    )
    assert (cash["ledger_type"], cash["Cash Account"], cash["Securities Account"]) == (
        "OPENING_CASH",
        "t212-1 (EUR)",
        "t212-1",
    )
    accounts = rows(files, ppcsv.ACCOUNTS)
    assert [a["Cash Account"] for a in accounts] == ["t212-1 (EUR)", "bb-1 (BRL)"]
    assert accounts[1]["ledger_opening_cash"] == ""


def test_opening_without_a_date_uses_the_first_activity_of_the_account():
    data = ledger([ev("DEPOSIT", "2025-01-02", "1", cash="5")])
    data["accounts"]["openings"] = {"t212-1": {"date": None, "cash": "0", "positions": OPENINGS["t212-1"]["positions"]}}
    files = export_pp.build(data)
    assert rows(files, ppcsv.PORTFOLIO_TRANSACTIONS)[0]["Date"] == "2025-01-02"
    assert export_pp.verify(data, files) == []


def test_securities_use_the_most_frequent_currency_and_name_and_skip_cash_events():
    events = [
        ev(
            "BUY",
            "2025-01-03",
            "1",
            quantity="1",
            cash="-10",
            isin=ISIN,
            symbol="IWDA",
            name="MSCI World",
            currency="USD",
        ),
        ev(
            "BUY",
            "2025-01-04",
            "2",
            quantity="1",
            cash="-10",
            isin=ISIN,
            symbol="IWDA",
            name="World ETF",
            currency="USD",
        ),
        ev("BUY", "2025-01-05", "3", quantity="1", cash="-10", symbol="ONLYSYM", name="No Isin", currency="EUR"),
        ev("DEPOSIT", "2025-01-06", "4", cash="1"),
    ]
    securities = rows(export_pp.build(ledger(events)), ppcsv.SECURITIES)
    assert [(s["ISIN"], s["Ticker Symbol"], s["Currency"]) for s in securities] == [
        (ISIN, "IWDA", "USD"),
        ("", "ONLYSYM", "EUR"),
    ]
    assert securities[0]["Security Name"] == "MSCI World"


def test_round_trip_is_lossless_for_hostile_text_and_optional_fields():
    name = '=HYPERLINK("http://x";"y");\n"quoted" \'single'
    events = [
        ev("BUY", "2025-01-03", "a;b", quantity="0.0000001", cash="-0.0000001", price="0", symbol="-ETF", name=name),
        ev("DEPOSIT", "2025-01-04", "r2", raw_type="+Deposit", fx_rate="1.1", gross="3"),
        ev("BUY", "2025-01-03", "r3", name="'", symbol="@x", isin=ISIN, quantity="1", cash="-1"),
    ]
    data = ledger(events)
    files = export_pp.build(data)
    assert "1E-7" not in files[ppcsv.PORTFOLIO_TRANSACTIONS]
    assert '"=HYPERLINK' not in files[ppcsv.PORTFOLIO_TRANSACTIONS]
    assert import_pp.read(files) == {k: data[k] for k in ("accounts", "events", "snapshots", "references")}
    assert export_pp.verify(data, files) == []


def test_an_account_id_that_looks_like_a_pp_account_name_still_round_trips():
    data = ledger()
    data["accounts"]["accounts"] = [{**ACCOUNTS[0], "id": "x (EUR)"}, ACCOUNTS[1]]
    data["accounts"]["openings"] = {"x (EUR)": OPENINGS["t212-1"]}
    data["events"] = [event("x (EUR)", "DEPOSIT", "2025-01-02", "1", currency="EUR", cash=Decimal(5))]
    assert export_pp.verify(data, export_pp.build(data)) == []


def test_events_keep_the_ledger_order_across_both_files():
    events = [ev("DEPOSIT", "2025-01-02", "z", cash="1"), ev("BUY", "2025-01-02", "a", quantity="1", cash="-1")]
    events += [ev("FEE", "2025-01-02", "m", cash="-1")]
    data = ledger(events)
    assert import_pp.read(export_pp.build(data))["events"] == events


def test_empty_ledger_still_produces_every_file():
    data = {"accounts": {"accounts": [], "openings": {}}, "events": [], "snapshots": [], "references": []}
    files = export_pp.build(data)
    assert set(files) == {
        ppcsv.SECURITIES,
        ppcsv.ACCOUNTS,
        ppcsv.ACCOUNT_TRANSACTIONS,
        ppcsv.PORTFOLIO_TRANSACTIONS,
        ppcsv.SNAPSHOTS,
        ppcsv.REFERENCES,
        ppcsv.README,
    }
    assert export_pp.verify(data, files) == []


def test_build_is_deterministic():
    data = ledger([ev("DEPOSIT", "2025-01-02", "1", cash="5")])
    assert export_pp.build(data) == export_pp.build(json.loads(json.dumps(data)))


def test_an_unknown_event_type_is_refused():
    with pytest.raises(PmError, match="cannot export event type"):
        export_pp.build(ledger([{**ev("DEPOSIT", "2025-01-02", "1"), "type": "MERGER"}]))


def test_verify_reports_sections_that_no_longer_match_the_ledger():
    data = ledger([ev("DEPOSIT", "2025-01-02", "1", cash="5"), ev("DEPOSIT", "2025-01-03", "2", cash="6")])
    files = export_pp.build(data)
    lines = files[ppcsv.ACCOUNT_TRANSACTIONS].splitlines()
    files[ppcsv.ACCOUNT_TRANSACTIONS] = "\n".join(lines[:-1]) + "\n"
    files[ppcsv.REFERENCES] = ppcsv.dumps(ppcsv.REFERENCE_COLUMNS, [])
    problems = export_pp.verify(data, files)
    assert [p.split()[0] for p in problems] == ["events", "references"]


def test_reader_refuses_missing_files():
    with pytest.raises(PmError, match="missing export file"):
        import_pp.read({})


def test_decimal_comma_export_keeps_the_ledger_columns_exact_and_still_round_trips():
    events = [ev("BUY", "2025-01-03", "2", quantity="2.5", cash="-101.5", fee="1.5", isin=ISIN, symbol="IWDA")]
    data = ledger(events)
    files = export_pp.build(data, decimal_comma=True)
    buy = rows(files, ppcsv.PORTFOLIO_TRANSACTIONS)[1]
    assert (buy["Value"], buy["Shares"], buy["Fees"]) == ("101,5", "2,5", "1,5")
    assert (buy["ledger_cash"], buy["ledger_quantity"]) == ("-101.5", "2.5")
    assert "--decimal-comma" in files[ppcsv.README]
    assert export_pp.verify(data, files) == []
    assert "--decimal-comma" not in export_pp.build(data)[ppcsv.README]
