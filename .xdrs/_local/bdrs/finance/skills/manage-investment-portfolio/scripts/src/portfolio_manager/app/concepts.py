"""Concept taxonomy rendered as reports/concepts.md; every report links its terms here via link()."""

import re
from typing import NamedTuple

GROUPS = ("Value", "Flows", "Returns", "Risk", "Profit and loss", "Data quality", "Periods and projections")
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
        "investment-account",
        "Value",
        "Investment account",
        "A brokerage or bank account that holds your cash and securities and sends you its own statements.",
        "Each one has its own cash and positions. Use this to see where your money sits.",
        "Trading 212 in EUR and Upvest in EUR are two investment accounts; wealth adds both.",
    ),
    Concept(
        "security",
        "Value",
        "Security",
        "Something you hold in an investment account, such as a share, fund, ETF or bond, identified by its ISIN.",
        "Positions are listed per security. Use this to see what you own behind each account.",
        "IE00B4L5Y983 is the ISIN of one ETF that can be held in two accounts at once.",
    ),
    Concept(
        "cash-positions",
        "Value",
        "Cash and positions",
        "Cash is money waiting in the account; positions are the securities you hold, valued at their latest price.",
        "Together they make the account value. Use this to see how much of your wealth is invested.",
        "An account with 200 EUR cash and 800 EUR of ETFs is worth 1,000 EUR.",
        r"$V = cash + \sum q \cdot p$",
    ),
    Concept(
        "weight",
        "Value",
        "Weight",
        "Share of one open position in the total value of all open positions.",
        "Shows concentration. Use this to spot a position that dominates your portfolio.",
        "A 2,500 EUR position among 10,000 EUR of open positions has a weight of 25 %.",
        r"$w = \frac{V_{position}}{\sum V_{positions}}$",
    ),
    Concept(
        "wealth",
        "Value",
        "Wealth",
        "Sum of all tracked investment account values in EUR on the common date.",
        "Shows what you own in total across investment accounts. Use this to track your net worth.",
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
        "Chained return of the securities themselves, ignoring the timing of your deposits.",
        "Shows how what you hold performed. Use this to judge the securities, not your timing.",
        "Value 100 grows to 110, you deposit 100, then 210 grows to 220.5: 10 % and 5 % chain to 15.5 %.",
        r"$TWR = \prod_k \frac{V_k - F_k}{V_{k-1}} - 1$",
    ),
    Concept(
        "xirr",
        "Returns",
        "XIRR (actual)",
        "Your real return given the dates of every deposit and withdrawal, over the window of the row.",
        "Shows what you earned considering when you added money. Use this to judge your own decisions.",
        "Investing 100 EUR in January and 100 EUR in June can give a different result than TWR if markets moved in between.",
        r"$V_0 (1+r)^{T} + \sum_k F_k (1+r)^{T-t_k} = V_1$ and the shown value is $(1+r)^{T}-1$.",
    ),
    Concept(
        "window",
        "Returns",
        "Window",
        "The length of the row's own period, in months. TWR, XIRR and period return of that row all cover exactly this span.",
        "Tells how long the results of a row cover. Use this to avoid comparing a 1 month result with a 12 month one.",
        "A row for year 2026 (to date) ending in June shows 6mon, and a full year shows 12mon.",
    ),
    Concept(
        "cagr",
        "Returns",
        "CAGR",
        "TWR since inception scaled to one year; shown only with 12 months or more of history.",
        "Lets long histories be compared with yearly rates. Use this to compare your result with an annual target.",
        "A TWR of 21 % over two years gives a CAGR of about 10 %.",
        r"$CAGR = (1 + TWR)^{365/d} - 1$ with $d$ the days of history.",
    ),
    Concept(
        "benchmark",
        "Returns",
        "Benchmark",
        "A market fund or index ETF used as a yardstick, converted to EUR, whose return since the window start sits next to your TWR.",
        "Shows whether your choices beat a simple alternative. Use this to judge if your picking pays off.",
        "Your TWR of 6 % against 8 % for a world ETF means the benchmark did better.",
    ),
    Concept(
        "wealth-bridge",
        "Returns",
        "Wealth bridge",
        "Start value plus money added, income, fees and taxes, FX effect and market effect gives the end value.",
        "Explains where the change in wealth came from. Use this to see how much was your saving versus markets.",
        "Start 10,000 + added 2,000 + income 200 - costs 50 + FX 30 + market 620 = 12,800 EUR.",
        r"$V_{end} = V_{start} + F + I - C + FX + M$",
    ),
    Concept(
        "volatility",
        "Risk",
        "Volatility",
        "Spread of the monthly TWR returns scaled to a year; needs at least three complete months.",
        "Shows how bumpy the ride was. Use this to compare how much risk different periods carried.",
        "Monthly returns that vary by about 3 points around their mean give an annual volatility near 10 %.",
        r"$\sigma = s_{monthly} \cdot \sqrt{12}$",
    ),
    Concept(
        "drawdown",
        "Risk",
        "Maximum drawdown",
        "Largest fall of the chained monthly TWR from an earlier peak to a later low.",
        "Shows the worst temporary loss you lived through. Use this to check that you can stand such a fall.",
        "A return index peaking at 120 and falling to 96 has a drawdown of 20 %.",
        r"$DD = \min_t \left(\frac{I_t}{\max_{s \le t} I_s} - 1\right)$",
    ),
    Concept(
        "best-worst-month",
        "Risk",
        "Best and worst month",
        "Highest and lowest TWR among the complete calendar months.",
        "Shows the range of single-month results. Use this to see what a bad month can look like.",
        "A best month of +6.1 % in 2025-11 and a worst month of -4.3 % in 2025-03.",
    ),
    Concept(
        "contribution",
        "Profit and loss",
        "Contribution",
        "Result of one security in the window: value change minus money put in, plus income received.",
        "Shows which securities made or lost the money. Use this to find your main winners and losers.",
        "A fund worth 1,000 EUR at the start and 1,500 at the end, with 200 bought and 30 of dividends, contributed 330 EUR.",
        r"$C = V_{end} - V_{start} - (buys - sells) + income$",
    ),
    Concept(
        "trailing-yield",
        "Profit and loss",
        "Trailing income yield",
        "Dividends and interest received in the last 12 months divided by today's value of the open positions.",
        "Shows the cash income your holdings produce. Use this to compare it with other sources of income.",
        "300 EUR received over 12 months on 10,000 EUR of open positions gives 3 %.",
        r"$y = \frac{income_{12m}}{V_{positions}}$",
    ),
    Concept(
        "dividends-interest",
        "Profit and loss",
        "Dividends and interest",
        "Cash paid to you by securities or accounts, before and after withholding.",
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
        "How long a security was held inside a period, in months.",
        "Tells the span behind a security result. Use this to compare securities bought at different times.",
        "A security bought in April and shown at year end has a held window of about 9 months.",
    ),
    Concept(
        "last-12-months",
        "Periods and projections",
        "Last 12 months",
        "The window from one year before the common date to that date; shorter, and labelled, when the history is shorter.",
        "Gives a recent view independent of calendar years. Use this to compare your current pace with older years.",
        "With a common date of 2026-06-30 the window starts on 2025-06-30; with 7 months of history the label says 7mon.",
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
        "Shows what a past rate would give over a year. Use this to compare pace across investment accounts, not to forecast.",
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


def render(before: list | None = None) -> str:
    """The concepts page; `before` lines (navigation, status) go right under the title."""
    out = [
        "# Concepts",
        "",
        *(before or []),
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
