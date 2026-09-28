# Runtime: Python >=3.10, stdlib only; imported by stats.py. Recurrence buckets and insight candidates; Decimal only.
import statistics
from datetime import date
from decimal import Decimal
from itertools import pairwise

from ledger import LedgerError

BANDS = [("Daily", Decimal(3)), ("Weekly", Decimal(10)), ("Monthly", Decimal(45)),
         ("Quarterly", Decimal(135)), ("Yearly", Decimal(430))]
BUCKETS = [b for b, _ in BANDS] + ["One-off"]
INFERABLE = {"Quarterly", "Yearly"}
MIN_ROWS = 3
TOP = 5
ZERO = Decimal(0)
# insight thresholds (amounts in the analysis currency); override with stats.py --threshold key=value
THRESHOLDS = {"small-row": Decimal("15.00"), "small-total": Decimal("100.00"), "large-share": Decimal("0.02"),
              "subscription-max": Decimal("20.00"), "price-rise": Decimal("1.05")}
STABLE_SHARE = Decimal("0.20")
GAP_SHARE = Decimal("0.25")
GAP_MIN_DAYS = Decimal(4)
ACTIVE_SLACK = Decimal("1.5")
YEAR_DAYS = Decimal("365.25")
CENT = Decimal("0.01")
# default days between charges when a bucket is assigned to a one-off title
PERIODS = {"Weekly": Decimal(7), "Monthly": Decimal("30.44"), "Quarterly": Decimal("91.31"),
           "Yearly": YEAR_DAYS}
# hidden-spending kinds; the title -> kind map (hidden.json) is written by the LLM per analysis
HIDDEN_KINDS = ["cash", "card", "provider", "fees"]


def to_date(ts: str) -> date:
    return date(int(ts[:4]), int(ts[5:7]), int(ts[8:10]))


def median_gap(rows: list):
    dates = sorted(to_date(r.timestamp) for r in rows)
    gaps = [(b - a).days for a, b in pairwise(dates)]
    return Decimal(str(statistics.median(gaps))) if gaps else None


def bucket_for(gap) -> str:
    if gap is None:
        return "One-off"
    for name, limit in BANDS:
        if gap <= limit:
            return name
    return "One-off"


def group_by_title(rows: list) -> dict:
    groups = {}
    for r in rows:
        groups.setdefault(r.title, []).append(r)
    return groups


def classify_titles(rows: list, assign: dict) -> dict:
    """Return {title: (bucket, median_gap, inferred)}."""
    for title, bucket in assign.items():
        if bucket not in INFERABLE:
            raise LedgerError(f"--assign {title!r}: only {sorted(INFERABLE)} can be inferred")
    result = {}
    for title, group in group_by_title(rows).items():
        gap = median_gap(group) if len(group) >= MIN_ROWS else None
        bucket, inferred = bucket_for(gap), False
        if bucket == "One-off" and title in assign:
            bucket, inferred = assign[title], True
        result[title] = (bucket, gap, inferred)
    return result


def _split(values: list) -> dict:
    credits = sum((v for v in values if v > 0), ZERO)
    debits = sum((v for v in values if v < 0), ZERO)
    return {"credits": credits, "debits": debits, "net": credits + debits}


def recurrence(rows: list, assign: dict) -> dict:
    titles = classify_titles(rows, assign)
    groups = group_by_title(rows)
    buckets = []
    for name in BUCKETS:
        members = []
        for title, (bucket, gap, inferred) in titles.items():
            if bucket == name:
                values = [r.value for r in groups[title]]
                members.append({"title": title, "rows": len(values), "total": sum(values, ZERO),
                                "median_gap_days": gap, "inferred": inferred})
        members.sort(key=lambda m: (-abs(m["total"]), m["title"]))
        values = [r.value for m in members for r in groups[m["title"]]]
        other = members[TOP:]
        entry = {"bucket": name, "rows": len(values), **_split(values), "top": members[:TOP],
                 "other_credits": sum((m["total"] for m in other if m["total"] > 0), ZERO),
                 "other_debits": sum((m["total"] for m in other if m["total"] < 0), ZERO),
                 "other_groups": len(other)}
        buckets.append(entry)
    grand = sum((r.value for r in rows), ZERO)
    covered = sum((b["net"] for b in buckets), ZERO)
    return {"buckets": buckets, "grand_total": grand, "buckets_total": covered, "ok": covered == grand}


def expenditure(rows: list) -> Decimal:
    return -sum((r.value for r in rows if r.flow == "Expenditure"), ZERO)


def _regular(gaps: list, gap: Decimal) -> bool:
    tolerance = max(gap * GAP_SHARE, GAP_MIN_DAYS)
    return sum(abs(g - gap) <= tolerance for g in gaps) * 2 >= len(gaps)


def _recurring_item(label: str, group: list, assigned, ends: dict):
    occurrences = {}  # same-day debits (e.g. two memberships) count as one charge
    for r in group:
        day = to_date(r.timestamp)
        occurrences[day] = occurrences.get(day, ZERO) - r.value
    dates = sorted(occurrences)
    gaps = [Decimal((b - a).days) for a, b in pairwise(dates)]
    gap = Decimal(str(statistics.median(gaps))) if len(dates) >= MIN_ROWS else None
    bucket, inferred = bucket_for(gap), False
    if bucket == "One-off" and assigned:
        bucket, inferred, gap = assigned, True, PERIODS[assigned]
    if bucket not in PERIODS or not (inferred or _regular(gaps, gap)):
        return None
    if abs(gap - PERIODS[bucket]) <= PERIODS[bucket] * GAP_SHARE:
        gap = PERIODS[bucket]
    amounts = [occurrences[d] for d in dates]
    typical = statistics.median(amounts)
    in_band = [a for a in amounts if abs(a - typical) <= typical * STABLE_SHARE]
    if len(in_band) * 2 < len(amounts):
        return None
    first, last = amounts[0], amounts[-1]
    files = sorted({getattr(r, "file", "") for r in group})
    as_of = max(ends.get(f, ends[""]) for f in files)
    since = (as_of - dates[-1]).days
    active = since <= gap * ACTIVE_SLACK
    current = last if abs(last - typical) <= typical * STABLE_SHARE else typical
    common = lambda key: statistics.mode(getattr(r, key) for r in group)
    return {"label": label, "title": group[0].title, "category": common("category"),
            "relevance": common("relevance"), "bucket": bucket, "inferred": inferred, "gap_days": gap,
            "rows": len(group), "charges": len(dates), "paid": sum(in_band, ZERO),
            "title_paid": sum(amounts, ZERO), "typical_amount": typical,
            "first_amount": first, "last_amount": last, "price_change": last != first,
            "first_date": dates[0].isoformat(), "last_date": dates[-1].isoformat(), "as_of": as_of.isoformat(),
            "days_since_last": since, "status": "active" if active else "stopped",
            "per_year": (current * YEAR_DAYS / gap).quantize(CENT) if active else ZERO,
            "files": [f for f in files if f]}


def recurring(rows: list, assign: dict, ends: dict) -> dict:
    """Recurring charges: Expenditure debits repeating Weekly..Yearly at regular gaps with a stable amount, per
    title or per title and exact amount (several subscriptions under one merchant). Same-day debits form one
    charge; paid sums the charges within 20% of the typical amount (title_paid sums all). ends maps file ->
    coverage end of its account ("" = default); active = last charge within 1.5 gaps of that end."""
    for title, bucket in assign.items():
        if bucket not in INFERABLE:
            raise LedgerError(f"--assign {title!r}: only {sorted(INFERABLE)} can be inferred")
    items = []
    for title, group in group_by_title([r for r in rows if r.flow == "Expenditure" and r.value < 0]).items():
        item = _recurring_item(title, group, assign.get(title), ends)
        if item:
            items.append(item)
            continue
        by_amount = {}
        for r in group:
            by_amount.setdefault(r.value, []).append(r)
        for value, same in by_amount.items():
            item = _recurring_item(f"{title} ({-value})", same, None, ends)
            if item:
                items.append(item)
    items.sort(key=lambda i: (i["status"] != "active", -i["per_year"], -i["paid"], i["label"]))
    active = [i for i in items if i["status"] == "active"]
    stopped = [i for i in items if i["status"] == "stopped"]
    per_year = sum((i["per_year"] for i in active), ZERO)
    return {"items": items, "totals": {
        "items": len(items), "paid_in_period": sum((i["paid"] for i in items), ZERO),
        "active": len(active), "active_paid_in_period": sum((i["paid"] for i in active), ZERO),
        "active_per_year": per_year, "active_per_month": (per_year / 12).quantize(CENT),
        "stopped": len(stopped), "stopped_paid_in_period": sum((i["paid"] for i in stopped), ZERO)}}


def check_hidden(hidden: dict) -> dict:
    if not isinstance(hidden, dict) or any(k not in HIDDEN_KINDS for k in hidden.values()):
        raise LedgerError(f"hidden map must be {{\"Title\": kind}} with kind in {HIDDEN_KINDS}")
    return hidden


def limits_with(overrides: dict) -> dict:
    bad = set(overrides) - set(THRESHOLDS)
    if bad:
        raise LedgerError(f"unknown threshold(s) {sorted(bad)}; known: {sorted(THRESHOLDS)}")
    return {**THRESHOLDS, **overrides}


def insights(rows: list, hidden_map: dict | None = None, overrides: dict | None = None) -> dict:
    """hidden_map: {title: cash|card|provider|fees} decided by the LLM; overrides: THRESHOLDS keys."""
    lim = limits_with(overrides or {})
    hidden_map = check_hidden(hidden_map or {})
    spend = [r for r in rows if r.flow == "Expenditure"]
    total = expenditure(rows)
    groups = group_by_title(spend)
    small, large, subscriptions, price_rises = [], [], [], []
    for title, group in groups.items():
        net = -sum((r.value for r in group), ZERO)
        debits = [r for r in group if r.value < 0]
        if debits and all(-r.value <= lim["small-row"] for r in debits) and net >= lim["small-total"]:
            small.append({"title": title, "rows": len(debits), "total": net, "average": (net / len(debits))})
        if total > 0 and net >= total * lim["large-share"]:
            large.append({"title": title, "rows": len(group), "total": net,
                          "relevance": sorted({r.relevance or "Unclassified" for r in group})})
        if len(debits) >= MIN_ROWS:
            ordered = sorted(debits, key=lambda r: r.timestamp)
            bucket = bucket_for(median_gap(debits))
            if bucket == "Monthly" and all(-r.value <= lim["subscription-max"] for r in debits):
                subscriptions.append({"title": title, "rows": len(debits), "total": net})
            first, last = -ordered[0].value, -ordered[-1].value
            if bucket in ("Monthly", "Quarterly", "Yearly") and first > 0 and last >= first * lim["price-rise"]:
                price_rises.append({"title": title, "first": first, "last": last,
                                    "since": ordered[0].timestamp[:10], "until": ordered[-1].timestamp[:10]})
    hidden = {}
    for kind in HIDDEN_KINDS:
        matched = [r for r in spend if hidden_map.get(r.title) == kind]
        hidden[kind] = {"rows": len(matched), "total": -sum((r.value for r in matched), ZERO),
                        "titles": sorted({r.title for r in matched})[:10]}
    missing = sorted(set(hidden_map) - set(groups))
    hidden["subscriptions"] = sorted(subscriptions, key=lambda s: -s["total"])
    hidden["price_rises"] = price_rises
    key = lambda s: (-s["total"], s["title"])
    return {"expenditures": total, "small_but_adds_up": sorted(small, key=key),
            "large": sorted(large, key=key), "hidden": hidden, "hidden_titles_not_found": missing,
            "thresholds": lim}
