# Formulas and statuses

All arithmetic uses `Decimal`; results are quantized to 10 decimals in JSON and rounded for display.

## Values

- Wealth on a date = cash + positions at price, converted to EUR with the ECB reference rate of that date
  (prior business day for weekends and holidays, up to 10 days back). Statement-provided FX rates are used
  when ECB data is missing for that day. Portfolio wealth is the sum over all investment accounts on the
  latest date where every tracked account has a valuation (the common date).
- Investment accounts without any rate for their last date are listed under `excluded` and left out, never
  zeroed.
- Between two statements of a snapshot account, values are interpolated: known flows at their dates and the
  remaining gain spread linearly in time.

## Returns

- **Time-weighted return (TWR)**: the period is split at each external cash flow (deposit, withdrawal);
  sub-period returns are chained. A sub-period with zero starting value is unavailable.
- **XIRR**: annualised money-weighted return on dated flows plus the ending value, over the window of the
  row (the same dates as its TWR and period return). Windows under 28 days show `n/a (<28d)`, because annualising
  a short span is misleading.
- **Risk windows**: from inception (all complete calendar months) and the latest 12 consecutive complete calendar
  months (a gap, a month with no TWR or a first month that does not start on day 1 gives n/a). Volatility is the
  sample standard deviation of monthly TWR times the square root of 12 and needs 3 months; CAGR of the 12-month
  window is the chained monthly TWR. CAGR per year uses only full calendar years starting on 1 January.
- **Volatility vs CAGR quadrant**: volatility of 12 % or more and CAGR of 8 % or more count as high, giving Holy
  Grail, Engine Room, Safe Haven or Danger Zone. The reference boxes by asset type are an approximate guide.
- **Realized P&L**: FIFO lots; opening positions have no cost basis, so realized P&L is partial for lots
  acquired before the first statement (`realized_status`).
- **FX effect**: the part of the EUR change explained by exchange-rate movement on foreign-currency value.
- Periods: `inception`, `month YYYY-MM`, `year YYYY`, `ytd YYYY`.

## Statuses

| Marker | Meaning |
| --- | --- |
| (none) | complete: derived from dated records |
| `~` | approximate: flows estimated (snapshot or value-only account) or interpolated values |
| `n/a` | unavailable: not enough data (no start value, no price, no rate) |

## Costs

Ex-post cost reports (`upvest_expost`) give service, product and inducement costs per instrument and total
cost against average valuation; fees in ledger accounts come from `FEE` events.

## Reconciliation

The ledger wins on conflict. Checks compare ledger quantities and cash with the latest statement, ledger
sells and dividends with the broker P&L statement for the same period, and quantity changes with the annual
tax statement. Every difference is a check row with expected, actual and level.
