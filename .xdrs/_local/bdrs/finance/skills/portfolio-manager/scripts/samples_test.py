# Runtime: pytest helper (no tests); builds fictitious statement layouts as line lists for every adapter. No real data.
"""Synthetic statements. Each builder returns pages (list of line lists) that mimic the structure an adapter reads."""

ACCOUNT = "ACC0005731"
ISIN_A = "IE00B4L5Y983"


def revolut_statement(extra_tx: list | None = None, cash_end: str = "€100.50") -> list:
    """Alpha fund: top-up 200, buy 2 @ 50, dividend 1, custody fee 0.50; ending cash 100.50, positions 110."""
    tx = [
        "02 Jan 2025 10:00:00 GMT", "Cash top-up", "€200.00", "€0.00", "€0.00",
        "03 Jan 2025 10:00:00 GMT", "ABC", "Trade - Market", "2", "€50.00", "Buy", "€100.00", "€0.00", "€0.00",
        "15 Jan 2025 10:00:00 GMT", "ABC", "Dividend", "€1.00", "€0.00", "€0.00",
        "20 Jan 2025 10:00:00 GMT", "Custody fee", "-€0.50", "€0.00", "€0.00",
        *(extra_tx or []),
    ]
    return [[
        "Revolut Securities", "Account Statement", "Account number", ACCOUNT, "Period", "01 Jan 2025 - 31 Jan 2025",
        "Generated on the 01 Feb 2025",
        "EUR Account summary", "Positions Value", "€0.00", "€110.00", "Cash value*", "€0.00", cash_end, "Total", "€0.00", "€210.50",
        "Portfolio breakdown", "Symbol", "Company", "ISIN", "Quantity Price Value", "% of Portfolio",
        "ABC", "Alpha Fund", ISIN_A, "2 €55.00 €110.00", "52.3%", "Positions Value",
        "EUR Transactions", "Date", "Symbol", "Type", "Quantity", "Price", "Side", "Value", "Fees", "Commission", *tx,
        "Glossary",
        "USD Account summary", "Positions Value", "$0.00", "$0.00", "Cash value*", "$0.00", "$0.00", "Total", "$0.00", "$0.00",
        "% of Portfolio", "Positions Value", "USD Transactions",
    ]]


def revolut_pnl() -> list:
    return [[
        "EUR Profit and Loss Statement", "Account number", ACCOUNT, "Period", "01 Jan 2025 - 31 Jan 2025", "Sells Summary",
        "Gross Proceeds", "€150.00", "Cost Basis", "€100.00", "Gross PnL", "€50.00", "Net other income", "€0.00",
        "Date acquired", "Date sold", "Symbol", "Security name", "ISIN", "Country", "Quantity", "Cost basis", "Gross proceeds", "Gross PnL", "Fees",
        "2024-12-01", "2025-01-10", "ABC", "Alpha Fund", ISIN_A, "IE", "1",
        "€100.00", "€150.00", "€50.00", "€0.00", "€100.00", "€150.00", "€50.00", "€0.00", "Rate 1", "Rate 1",
        "Other income & fees", "Dividends", "€0.00",
    ]]


def trading212(deposit: str = "€1,000.00", account_value: str = "€1,010.85") -> list:
    return [[
        "Trading 212", "Activity statement", "Account ID: ABC1234", "covering from 01.01.2025 00:00 (UTC) to 31.01.2025 23:59 (UTC)",
        "Deposits", deposit, "Withdrawals", "€0.00", "Dividends", "€0.85", "Interest on cash", "€0.00", "Account value", account_value,
        "Invest account - executed trades",
        "2025-01-02 10:00:00", "ABC", ISIN_A, "ORD1", "Buy", "2", "€50.00", "€100.00", "-", "-", "-", "-", "-", "-", "-", "€100.00",
        "Invest account - open positions summary",
        "ABC", ISIN_A, "2", "€50.00", "€55.00", "-", "-", "-", "-", "€110.00",
        "Invest account - cash breakdown", "EUR cash", "€900.85",
        "Invest account - transactions and dividends",
        "2025-01-01 09:00:00", "Deposit", "€1,000.00",
        "Dividends",
        "ABC", ISIN_A, "Alpha Fund", "2", "15.01.2025 12:00:00", "x", "€1.00", "x", "€0.15", "1", "€0.85",
    ], ["1/1", "Trading 212 EU GmbH receives fees"]]


def upvest_snapshot(total: str = "525.00 EUR", count: str = "1", german_tail: bool = True) -> list:
    page = [
        "Upvest Securities", "Securities account statement as of 30.06.2025", "Securities account number", "ACC0005731-1",
        "10.5 / unit(s)", "Alpha Fund", "ISIN (WKN)", f"{ISIN_A} (A0RPWH)", "Price", "50.00", "EUR", "Value", "525.00", "EUR",
        "Number of positions", count, "Total value", total,
    ]
    if german_tail:
        page += ["Depotauszug per 30.06.2025", "7 / Stück(e)", "Total value", "999.00 EUR"]
    return [page]


def upvest_tax(year: str = "2025") -> list:
    return [[
        "Upvest Securities", "Annual tax statement", f"all transactions which took place on your account in {year}",
        "Securities account number", "ACC0005731-1", "Transactions Transactions",
        f"15/03/{year} Buy 50.00 EUR Alpha Fund ISIN: {ISIN_A} 2.00 100.00 EUR 0.00 EUR",
        "Dividend Distributions",
        f"20/ 06/ {year} 2.00 0.50 EUR Alpha Fund ISIN: {ISIN_A} withholding 0.10 EUR 1.00 EUR",
        "Kontomitteilung", "ignored german copy",
    ]]


def upvest_expost(total_cost: str = "5.00") -> list:
    return [[
        "Upvest Securities", "Ex-post cost report", "Securities account number", "ACC0005731-1", "Covered period: 01/01/2025-31/12/2025",
        "Average account valuation: 1,000.00 EUR", f"Costs decreased by {total_cost} EUR over the year, which corresponds to 0.50 %",
        ISIN_A, "Alpha Fund", "1.00", "3.00", "1.00", "Ex-post-Kosteninformation", ISIN_A, "9.00", "9.00", "9.00",
    ]]


def bb_portfolio(end_total: str = "R$ 1.600,00") -> list:
    return [[
        "PORTFÓLIO DE INVESTIMENTOS", "bb.com.br", "Agência/Conta", "0001 CC 41930", "Período:", "01/01/2025 até", "31/01/2025",
        "Saldo Bruto:", end_total,
        "TOTAL", "R$ 1.500,00", "R$ 200,00", "R$ 100,00", "R$ 1.600,00",
        "Distribuição da carteira", "Renda Fixa", "Alocação por ativo",
        "CDB TESTE", "R$ 1.000,00", "R$ 200,00", "R$ 100,00", "R$ 1.100,00", "R$ 0,00", "R$ 0,00", "68,75%",
        "POUPANCA OURO", "R$ 500,00", "R$ 0,00", "R$ 0,00", "R$ 500,00", "R$ 0,00", "R$ 0,00", "31,25%",
        "Liquidez da carteira",
    ]]


def bb_informe() -> list:
    return [[
        "Informe de Rendimentos Financeiros", "Ano Calendário 2025", "Conta Nome", "41930 TITULAR FICTICIO",
        "01. Rendimentos isentos", "CDB TESTE   1.000,00   1.100,00   50,00", "03. Conta corrente", "SALDO CC   10,00   20,00",
        "04. Cartões", "CARTAO   1,00   2,00",
    ]]
