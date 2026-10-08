"""Deterministic SVG waterfall chart (no timestamps, fixed number formats, XML-escaped labels, explicit white background)."""

from decimal import Decimal
from xml.sax.saxutils import escape, quoteattr

WIDTH, HEIGHT = 760, 360
LEFT, RIGHT, TOP, BOTTOM = 70, 20, 50, 70
COLORS = {"total": "#1f4e79", "up": "#2e7d32", "down": "#c62828"}


def _fmt(v: Decimal) -> str:
    return f"{v:,.0f}"


def _levels(steps: list) -> list:
    """(low, high, kind) per step: totals start at the axis, deltas float on the running level."""
    out, level = [], Decimal(0)
    for _label, amount, kind in steps:
        if kind == "total":
            out.append((Decimal(0), amount, "total"))
            level = amount
        else:
            out.append((min(level, level + amount), max(level, level + amount), "up" if amount >= 0 else "down"))
            level += amount
    return out


def waterfall(title: str, steps: list) -> str:
    """steps: [(label, Decimal amount, 'total'|'delta')]; the axis starts below the lowest bar edge when that helps."""
    bars = _levels(steps)
    lows = [b[0] for b in bars if b[2] != "total"] + [steps[0][1], steps[-1][1]]
    highs = [b[1] for b in bars]
    top, floor = max(highs), min(lows)
    span = top - floor or Decimal(1)
    axis_min = max(Decimal(0), floor - span / 4) if floor > 0 else floor
    axis_max = top + span / 10
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
    slot = plot_w // len(steps)

    def y(v: Decimal) -> int:
        return round(TOP + plot_h - float((v - axis_min) / (axis_max - axis_min)) * plot_h)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f"role=\"img\" aria-label={quoteattr(title)}>",
        f"<title>{escape(title)}</title>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        f'<text x="{WIDTH // 2}" y="24" text-anchor="middle" font-family="sans-serif" font-size="16" '
        f'fill="#222222">{escape(title)}</text>',
        f'<line x1="{LEFT}" y1="{y(axis_min)}" x2="{WIDTH - RIGHT}" y2="{y(axis_min)}" stroke="#888888"/>',
    ]
    if axis_min > 0:
        parts.append(
            f'<text x="{LEFT}" y="{TOP - 8}" font-family="sans-serif" font-size="11" fill="#666666">'
            f"axis starts at {escape(_fmt(axis_min))}</text>"
        )
    for i, ((label, amount, _kind), (low, high, kind)) in enumerate(zip(steps, bars, strict=True)):
        x = LEFT + i * slot + slot // 6
        w = slot - slot // 3
        y_top, y_bottom = y(max(high, axis_min)), y(max(low, axis_min))
        text = _fmt(amount) if kind == "total" else f"{amount:+,.0f}"
        parts += [
            f'<rect x="{x}" y="{y_top}" width="{w}" height="{max(y_bottom - y_top, 1)}" fill="{COLORS[kind]}"/>',
            f'<text x="{x + w // 2}" y="{y_top - 6}" text-anchor="middle" font-family="sans-serif" font-size="12" '
            f'fill="#222222">{escape(text)}</text>',
            f'<text x="{x + w // 2}" y="{HEIGHT - BOTTOM + 20}" text-anchor="middle" font-family="sans-serif" '
            f'font-size="12" fill="#222222">{escape(label)}</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
