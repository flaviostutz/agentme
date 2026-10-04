# Institutions and layouts

Each adapter in `scripts/institutions/` has `NAME`, `KIND`, `detect(doc)` and `parse(doc, answers)`. `KIND` is
`ledger` (transactions, replayed by the accounting), `snapshot` (positions at a date) or `reference` (extra
facts used only for checks and costs). A layout that no adapter detects becomes an unresolved `file-unsupported`
record; a detected layout that no longer parses becomes `file-layout-drift`.

| Adapter | Document | Kind | What it yields |
| --- | --- | --- | --- |
| `revolut_statement` | Revolut Securities account statement (per currency block) | ledger | deposits, buys, sells, dividends, fees; start and end snapshots; cash-residual check |
| `revolut_pnl` | Revolut profit and loss statement | reference | per-sale cost, proceeds, P&L; summary used to check ledger sells and dividends |
| `trading212` | Trading 212 activity statement | ledger | executed trades, deposits, dividends, cash breakdown, open positions; derived opening |
| `upvest_snapshot` | Upvest securities account statement | snapshot | positions with price and value at the statement date; total and count checks |
| `upvest_tax` | Upvest annual tax statement | reference | transactions and dividends per year; quantity-change checks between statements |
| `upvest_expost` | Upvest ex-post cost report | reference | service, product and inducement costs per instrument; total check |
| `bb_portfolio` | Banco do Brasil portfolio report | snapshot (value-only) | position values at both ends of the period, period entries and exits; cover-total check |
| `bb_informe` | Banco do Brasil annual income report | reference | year-end balances and income per section |

## Account modes

- `transactions`: full events; positions and cash are replayed. Opening quantity = latest reported quantity
  minus the net quantity of all events (negative opening is an error).
- `snapshot`: positions only; flows are estimated from quantity changes between statements and marked
  approximate.
- `value-only`: only values and period entries and exits are known; flows are approximate.

## Checks

Every adapter returns check rows `{name, expected, actual, level}` with level `ok`, `warn` or `fail`. A failed
check rejects the file (unresolved `rejected-file`) unless the user accepts its sha256 prefix. Rounding
tolerance grows with the number of rows summed. The Revolut cash residual warns up to
`max(1, 0.5% of the statement total)` and fails above.

## Adding an institution

Add `scripts/institutions/<name>.py` with the four members, register it in `registry.py`, build fictitious
layout lines in `samples_test.py`, and test detection, parsing, each check and the layout-drift error beside
the adapter. Never put real statements, names or numbers in tests.
