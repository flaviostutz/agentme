# Report template

Write the report to `.tmp/<id>/report.md` in the user's language. Every number comes from a `stats.py`,
`validate.py` or `ground.py` output; never compute totals by hand. Show money as `1,234.56 <currency>`, with
the currency from the `currency` field of the `stats.py` output, and the number format of the user's language.
Show IBANs and account numbers as the last 4 digits only. Name private persons only when the user did.

```markdown
# Transactions analysis <period start> to <period end>

> Personal insights, not regulated financial advice.

## Inputs & accounts
| Account | Bank | Type | Period | Files | Rows | Opening | Closing |
Notes: own-account transfers paired, pseudo-accounts (e.g. shared-expense apps) and how they were treated,
months of the period an account does not cover.

## Summary
3 to 5 bullets: income, expenditures, savings rate (savings / income), biggest driver, one main action.

## Money flow
Income = Savings + Expenditures, with the numbers from `stats.py flow`.
| Flow | Amount | Share of income |
Savings split: put aside (Savings rows) and kept in accounts (balance change). Refunds: rows and total.

## Insights
### Relevance breakdown
| Relevance | Amount | % of expenditures | Top 6 titles |
### Small but adds up
Titles whose debits are all small but whose total is large (`stats.py insights`).
### Hidden spending
Cash, card settlements, payment providers, fees, small subscriptions, price rises, trials that became paid.
### Actions
3 to 6 actions tailored to the user's context, each with a yearly estimate from `stats.py estimate`.

## Recurring charges
Source: `stats.py recurring` (add `--assign '{"Title": "Yearly"}'` for known one-off subscriptions).
Totals line: <active> active charges, <active_per_year> per year (<active_per_month> per month);
<stopped> stopped charges, <stopped_paid_in_period> paid before they stopped.
### Active
| Title | Category | Relevance | Frequency | Typical | Last | Price change | Paid in period | Per year | Last charge |
### Stopped
| Title | Category | Frequency | Typical | Paid in period | Last charge |
Rules:
- Status is relative to the end of the account's coverage (`as_of`), not today.
- Drop coincidental groups (e.g. a café visited at regular gaps) from the tables only after you name them in
  one line below the table; keep habits that repeat often (e.g. a daily coffee) if they are material.
- Flag trials that became paid (first amount much lower than last), price rises, and charges above the
  typical amount.

## Totals per category
| Category | Flow | Relevance | Rows | Total |

## Recurrence
| Bucket | Rows | Debits | Credits | Top titles |

## Data quality
- Grounding: rows grounded per file, source-only lines reviewed, module checks, balance chains.
- Unverified rows: files transcribed from images or scans (`normalizer: llm-image`), with rows and total.
- Normalizers: files read by a module, a mapping, or the LLM path.
- Skipped: input files (unsupported, duplicate, encrypted) and rows (other currencies, outside the period,
  dropped duplicates), each with the count and reason.
- Validation warnings, positive Expenditure rows (refunds), continuity gaps, changed thresholds.
- Research: titles classified from web findings, with their source URLs.
- Assumptions and rows the user marked Unknown.

## Retention
The analysis files are in `.tmp/<id>/` (copies of the statements, normalized files, answers, research cache,
this report). Delete the folder when done; keep `answers.json` and `research/cache.json` to reuse them later.
```
