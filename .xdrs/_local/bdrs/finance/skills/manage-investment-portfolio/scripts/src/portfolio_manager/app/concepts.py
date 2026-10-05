"""Concept taxonomy rendered as reports/concepts.md; every report links its terms here via link()."""

import re
from typing import NamedTuple

GROUPS = ("Value", "Flows", "Returns", "Profit and loss", "Data quality", "Periods and projections")
MAX_WORDS = {"summary": 30, "useful": 30, "example": 50, "formula": 40}


class Concept(NamedTuple):
    key: str
    group: str
    name: str
    summary: str
    useful: str
    example: str
    formula: str = ""


CONCEPTS = (
    Concept(
        "wealth",
        "Value",
        "Wealth",
        "Sum of all tracked account values in EUR on the common date.",
        "Shows what you own in total across banks and brokers. Use this to track your net worth.",
        "Revolut 4,000 + Trading 212 1,000 + Upvest 9,000 EUR give a wealth of 14,000 EUR.",
        r"$W_t = \sum_i V_{i,t} \cdot fx_{i,t}$ with $V$ the account value and $fx$ the EUR rate.",
    ),
    Concept(
        "common-date",
        "Value",
        "Common date",
        "Latest day on which every tracked account has a valuation.",
        "Avoids adding values observed on different days. Use this to read the headline wealth consistently.",
        "One account last valued on 2026-06-30 and another on 2026-10-04 give a common date of 2026-06-30.",
        r"$t_c = \min_i t_i^{last}$",
    ),
    Concept(
        "cost-basis",
        "Value",
        "Cost basis",
        "What you paid for the units you still hold, including fees.",
        "Separates paid money from market gains. Use this to know how much of a position is profit.",
        "Buying 10 units at 5 EUR plus 1 EUR fee gives a cost basis of 51 EUR.",
        r"$B = \sum_{lots} (q \cdot p + fee)$",
    ),
    Concept(
        "interpolation",
        "Value",
        "Interpolation",
        "Values between two statement dates are estimated on a straight line and marked with ~.",
        "Explains why some period-end values are estimates. Use this to know which numbers rest on estimates.",
        "Quarterly snapshots on 03-31 (100) and 06-30 (110) give an interpolated 05-31 value of about 106.7.",
        r"$V_t = V_a + (V_b - V_a)\,\frac{t-a}{b-a}$",
    ),
    Concept(
        "observation-dates",
        "Value",
        "Observation dates",
        "The days on which an account really reported a value, as opposed to estimated days.",
        "Shows how fresh each account is. Use this to spot accounts that are stale compared with the others.",
        "A Trading 212 statement from 2026-10-02 and an Upvest report from 2026-06-30 have different observation dates.",
    ),
    Concept(
        "deposits-withdrawals",
        "Flows",
        "Deposits and withdrawals",
        "Money you moved into or out of an account, as seen in statements.",
        "Separates your contributions from market results. Use this to see how much you really invested.",
        "A transfer of 500 EUR into Revolut is a deposit; a transfer of 200 EUR back to your bank is a withdrawal.",
    ),
    Concept(
        "late-start",
        "Flows",
        "Late-start account",
        "An account whose first valuation comes after the portfolio started; its opening value counts as an inflow.",
        "Prevents a newly tracked account from looking like a market gain. Use this to understand jumps in net flows.",
        "An account first reported at 8,000 EUR on 2026-01-01 adds 8,000 EUR of inflow that day.",
    ),
    Concept(
        "net-flows",
        "Flows",
        "Net flows",
        "Deposits minus withdrawals inside a period, valued in EUR.",
        "Shows how much of the wealth change came from you. Use this to separate savings from performance.",
        "Deposits of 1,000 and withdrawals of 300 EUR in a month give net flows of 700 EUR.",
        r"$F = \sum deposits - \sum withdrawals$",
    ),
    Concept(
        "fx-effect",
        "Returns",
        "FX effect",
        "Part of the gain caused only by the exchange rate of a non-EUR account.",
        "Shows how currency moves changed your EUR result. Use this to tell market gains from currency gains.",
        "A 1,000 USD account worth 1,000 USD at 0.90 then 0.95 EUR per USD gains 50 EUR from FX alone.",
        r"$FX = V_{end} \cdot (fx_{end} - fx_{start})$",
    ),
    Concept(
        "gain",
        "Returns",
        "Gain",
        "End value minus start value minus net flows, in EUR.",
        "Shows the money you made or lost in a period. Use this to compare results in euros, not percentages.",
        "Start 1,000, end 1,350 and net flows 300 give a gain of 50 EUR.",
        r"$G = V_{end} - V_{start} - F$",
    ),
    Concept(
        "period-return",
        "Returns",
        "Period return",
        "Gain divided by the start value plus time-weighted flows (Modified Dietz).",
        "Gives a quick return for periods where exact daily values are missing. Use this to sanity-check TWR and XIRR.",
        "Start 100, end 160 and a deposit of 50 halfway give 10 / (100 + 25) = 8 %.",
        r"$R = \frac{G}{V_{start} + \sum F_k \cdot w_k}$ with $w_k$ the share of the period left after flow $k$.",
    ),
    Concept(
        "twr",
        "Returns",
        "TWR (natural)",
        "Chained return of the assets themselves, ignoring the timing of your deposits.",
        "Shows how what you hold performed. Use this to judge the assets, not your timing.",
        "Value 100 grows to 110, you deposit 100, then 210 grows to 220.5: 10 % and 5 % chain to 15.5 %.",
        r"$TWR = \prod_k \frac{V_k - F_k}{V_{k-1}} - 1$",
    ),
    Concept(
        "xirr",
        "Returns",
        "XIRR (actual)",
        "Your real return given the dates of every deposit and withdrawal, over the XIRR window.",
        "Shows what you earned considering when you added money. Use this to judge your own decisions.",
        "Investing 100 EUR in January and 100 EUR in June can give a different result than TWR if markets moved in between.",
        r"$V_0 (1+r)^{T} + \sum_k F_k (1+r)^{T-t_k} = V_1$ and the shown value is $(1+r)^{T}-1$.",
    ),
    Concept(
        "xirr-window",
        "Returns",
        "XIRR window",
        "The span used for XIRR: at most the last 12 months of the row, or the full history for inception.",
        "Tells how long the XIRR result covers. Use this to avoid comparing a 3 month result with a 12 month one.",
        "A row for year 2026 (to date) ending in June may show a 9mon window if the history started in September.",
    ),
    Concept(
        "dividends-interest",
        "Profit and loss",
        "Dividends and interest",
        "Cash paid to you by assets or accounts, before and after withholding.",
        "Shows income that does not depend on selling. Use this to compare income across accounts.",
        "A 12 EUR dividend with 3 EUR withholding adds 9 EUR of net income.",
    ),
    Concept(
        "fees-taxes",
        "Profit and loss",
        "Fees and taxes",
        "Costs charged by the institution and taxes withheld, taken from statements.",
        "Shows what the investments cost you. Use this to compare brokers and spot expensive accounts.",
        "Trading fees of 4 EUR and a 2 EUR tax add up to 6 EUR of costs.",
    ),
    Concept(
        "fee-drag",
        "Profit and loss",
        "Fee/tax drag",
        "Fees plus taxes divided by the average account value.",
        "Shows how much costs eat from the balance. Use this to compare costs between accounts of different size.",
        "Fees and taxes of 6 EUR on an average value of 1,000 EUR give a drag of 0.6 %.",
        r"$drag = \frac{fees + taxes}{(V_{start} + V_{end})/2}$",
    ),
    Concept(
        "income-yield",
        "Profit and loss",
        "Income yield",
        "Dividends plus interest divided by the average account value.",
        "Shows the cash income an account produced. Use this to compare income with growth.",
        "Income of 30 EUR on an average value of 1,000 EUR gives a yield of 3 %.",
        r"$yield = \frac{dividends + interest}{(V_{start} + V_{end})/2}$",
    ),
    Concept(
        "realized-pl",
        "Profit and loss",
        "Realized P&L",
        "Profit or loss of units already sold, computed against the lot cost.",
        "Shows what you locked in. Use this to see which sales made or lost money.",
        "Selling 10 units at 7 EUR that cost 5 EUR each realizes 20 EUR.",
        r"$P_r = \sum (p_{sell} - p_{cost}) \cdot q$",
    ),
    Concept(
        "unrealized-pl",
        "Profit and loss",
        "Unrealized P&L",
        "Profit or loss of units you still hold, at the latest known price.",
        "Shows paper gains that can still change. Use this to see how much of your profit depends on prices.",
        "10 units bought at 5 EUR and priced at 6 EUR show 10 EUR of unrealized profit.",
        r"$P_u = \sum (p_{last} - p_{cost}) \cdot q$",
    ),
    Concept(
        "coverage-gap",
        "Data quality",
        "Coverage gap",
        "A stretch of days with no statement for an account, found when the input is checked.",
        "Shows where results may miss events. Use this to decide whether to add a statement or accept the gap.",
        "A transaction account with statements for January and March but not February has a February gap.",
    ),
    Concept(
        "reconciliation",
        "Data quality",
        "Reconciliation checks",
        "Comparisons between statement totals and what the ledger computed.",
        "Show whether the ledger agrees with your institutions. Use this to find parsing or missing-data problems.",
        "Opening cash plus transactions should equal ending cash; a difference of 2.40 EUR raises a warning.",
    ),
    Concept(
        "status",
        "Data quality",
        "Status marks",
        "Each number is complete, interpolated (~), approximate (~) or unavailable (n/a).",
        "Tells how much to trust a number. Use this to ignore n/a values and treat ~ values as estimates.",
        "A month-end value taken between two quarterly snapshots is marked ~; a missing value shows n/a, never 0.",
    ),
    Concept(
        "trust",
        "Data quality",
        "How far to trust",
        "A table of accounts with flow quality, latest date and coverage gaps.",
        "Summarizes the weak spots behind the headline numbers. Use this to decide which figures need checking.",
        "An account with estimated flows and an unconfirmed gap deserves a manual look at its statements.",
    ),
    Concept(
        "unresolved",
        "Data quality",
        "Unresolved records",
        "Statement items the tools could not classify, listed until you answer them.",
        "Shows data that does not yet count correctly. Use this to know what to answer before trusting totals.",
        "A transfer without a clear type stays unresolved until you mark it as deposit or internal move.",
    ),
    Concept(
        "first-day",
        "Periods and projections",
        "First day",
        "First included day of a period: the day after the start value date.",
        "Removes doubt about which days a row covers. Use this to read row boundaries as inclusive.",
        "A row with first day 2026-01-01 starts from the closing value of 2025-12-31.",
    ),
    Concept(
        "held-window",
        "Periods and projections",
        "Held window",
        "How long an asset was held inside a period, in months.",
        "Tells the span behind an asset result. Use this to compare assets bought at different times.",
        "An asset bought in April and shown at year end has a held window of about 9 months.",
    ),
    Concept(
        "partial-period",
        "Periods and projections",
        "Partial period",
        "A month or year still running, marked (to date) and covering only days with data.",
        "Prevents a half year from looking like a full one. Use this to read year-to-date rows as incomplete.",
        "Year 2026 (to date) ending 2026-06-30 covers six months only.",
    ),
    Concept(
        "projection",
        "Periods and projections",
        "Projection (extrapolated)",
        "Past results scaled to a year; only in projections.md and never a prediction.",
        "Shows what a past rate would give over a year. Use this to compare pace across banks, not to forecast.",
        "A 2 % return over 120 days scales to about 6.2 % a year.",
        r"$r_{year} = (1 + r)^{365/d} - 1$",
    ),
)


def slug(text: str) -> str:
    return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9 \-]", "", text.lower()).strip())


def concept(key: str) -> Concept:
    for c in CONCEPTS:
        if c.key == key:
            return c
    msg = f"unknown concept {key}"
    raise KeyError(msg)


def link(key: str, label: str | None = None) -> str:
    c = concept(key)
    return f"[{label or c.name}](concepts.md#{slug(c.name)})"


def render() -> str:
    out = [
        "# Concepts",
        "",
        "Plain-language taxonomy of every term used in the reports. Formulas use EUR values unless noted.",
        "",
    ]
    for group in GROUPS:
        out += [f"## {group}", ""]
        for c in sorted((c for c in CONCEPTS if c.group == group), key=lambda c: c.name.lower()):
            out += [f"### {c.name}", "", c.summary, "", f"Useful to: {c.useful}", "", f"Example: {c.example}", ""]
            if c.formula:
                out += [f"Formula: {c.formula}", ""]
    return "\n".join(out)
