"""Deterministic SVG charts: wealth waterfall and volatility vs CAGR quadrant (no timestamps, fixed number formats, XML-escaped labels, explicit white background)."""

from decimal import Decimal
from xml.sax.saxutils import escape, quoteattr

from portfolio_manager.app import quadrant as quad

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
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
            f'role="img" aria-label={quoteattr(title)}>'
        ),
        f"<title>{escape(title)}</title>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        (
            f'<text x="{WIDTH // 2}" y="24" text-anchor="middle" font-family="sans-serif" font-size="16" '
            f'fill="#222222">{escape(title)}</text>'
        ),
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
            (
                f'<text x="{x + w // 2}" y="{y_top - 6}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="12" fill="#222222">{escape(text)}</text>'
            ),
            (
                f'<text x="{x + w // 2}" y="{HEIGHT - BOTTOM + 20}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="12" fill="#222222">{escape(label)}</text>'
            ),
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


QW, QH = 640, 480
QLEFT, QRIGHT, QTOP, QBOTTOM = 70, 20, 50, 60
FILLS = {"holy-grail": "#e8f5e9", "engine-room": "#e3f2fd", "safe-haven": "#eceff1", "danger-zone": "#ffebee"}
NAME_COLORS = {"holy-grail": "#2e7d32", "engine-room": "#1565c0", "safe-haven": "#455a64", "danger-zone": "#c62828"}
GRID, EDGE = "#cccccc", "#666666"
BOLD = ' font-weight="bold"'


def _text(
    x: int, y: int, text: str, *, size: int = 12, anchor: str = "start", fill: str = "#222222", extra: str = ""
) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="sans-serif" font-size="{size}" '
        f'fill="{fill}"{extra}>{escape(text)}</text>'
    )


def _tick(v: Decimal, last: bool) -> str:
    return f"{v * 100:.0f}%" + ("+" if last else "")


def _quadrant_names(left: int, right: int, top: int, bottom: int, mid_x: int) -> list:
    """The four quadrant names in the corners that no reference box covers."""
    q = quad.QUADRANTS
    spots = {
        "holy-grail": (left + 8, top + 18, "start"),
        "engine-room": (right - 8, top + 18, "end"),
        "safe-haven": (mid_x - 8, bottom - 8, "end"),
        "danger-zone": (right - 8, bottom - 8, "end"),
    }
    return [
        _text(x, y, q[k].name, size=14, anchor=anchor, fill=NAME_COLORS[k], extra=BOLD)
        for k, (x, y, anchor) in spots.items()
    ]


def quadrant(title: str, volatility: Decimal, cagr: Decimal) -> str:
    """Volatility (x) vs CAGR (y) on calibrated axes: four quadrants, grey dashed reference boxes and the portfolio dot.

    Values beyond the axes are drawn on the edge; the label always carries the real numbers.
    """
    plot_w, plot_h = QW - QLEFT - QRIGHT, QH - QTOP - QBOTTOM
    left, right, top, bottom = QLEFT, QLEFT + plot_w, QTOP, QTOP + plot_h
    mid_x, mid_y = left + plot_w // 2, top + plot_h // 2

    def px(v: Decimal) -> int:
        return round(left + float(quad.position(v, quad.VOL_TICKS)) * plot_w)

    def py(v: Decimal) -> int:
        return round(bottom - float(quad.position(v, quad.CAGR_TICKS)) * plot_h)

    cells = {
        "holy-grail": (left, top, mid_x - left, mid_y - top),
        "engine-room": (mid_x, top, right - mid_x, mid_y - top),
        "safe-haven": (left, mid_y, mid_x - left, bottom - mid_y),
        "danger-zone": (mid_x, mid_y, right - mid_x, bottom - mid_y),
    }
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{QW}" height="{QH}" viewBox="0 0 {QW} {QH}" '
            f'role="img" aria-label={quoteattr(title)}>'
        ),
        f"<title>{escape(title)}</title>",
        f'<rect width="{QW}" height="{QH}" fill="#ffffff"/>',
        _text(QW // 2, 24, title, size=16, anchor="middle"),
        *[f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{FILLS[k]}"/>' for k, (x, y, w, h) in cells.items()],
    ]
    for i, v in enumerate(quad.VOL_TICKS):
        x = px(v)
        parts += [
            f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{GRID}"/>',
            _text(x, bottom + 18, _tick(v, i == len(quad.VOL_TICKS) - 1), size=11, anchor="middle"),
        ]
    for i, v in enumerate(quad.CAGR_TICKS):
        y = py(v)
        parts += [
            f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="{GRID}"/>',
            _text(left - 8, y + 4, _tick(v, i == len(quad.CAGR_TICKS) - 1), size=11, anchor="end"),
        ]
    parts += [
        f'<line x1="{mid_x}" y1="{top}" x2="{mid_x}" y2="{bottom}" stroke="{EDGE}" stroke-width="2"/>',
        f'<line x1="{left}" y1="{mid_y}" x2="{right}" y2="{mid_y}" stroke="{EDGE}" stroke-width="2"/>',
        *_quadrant_names(left, right, top, bottom, mid_x),
    ]
    for ref in quad.REFERENCES:
        x0, x1, y0, y1 = px(ref.vol_from), px(ref.vol_to), py(ref.cagr_to), py(ref.cagr_from)
        label_y = y1 - 5 if ref.cagr_to >= quad.CAGR_TICKS[-1] else y0 + 12
        parts += [
            (
                f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" '
                'stroke="#888888" stroke-dasharray="4 3"/>'
            ),
            _text(x0 + 4, label_y, f"ref: {ref.label}", size=10, fill="#777777"),
        ]
    cx, cy = px(volatility), py(cagr)
    near_right = cx > left + plot_w * 0.55
    label = f"You: CAGR {cagr * 100:.1f} %, volatility {volatility * 100:.1f} %"
    parts += [
        f'<circle cx="{cx}" cy="{cy}" r="7" fill="#1f4e79" stroke="#ffffff" stroke-width="2"/>',
        _text(
            cx - 12 if near_right else cx + 12,
            cy - 12 if cy > top + 34 else cy + 22,
            label,
            anchor="end" if near_right else "start",
            extra=BOLD,
        ),
        _text(left + plot_w // 2, QH - 14, "Volatility (annualised, std dev of monthly returns)", anchor="middle"),
        _text(
            18,
            mid_y,
            "CAGR (annualised TWR)",
            anchor="middle",
            extra=f' transform="rotate(-90 18 {mid_y})"',
        ),
        "</svg>",
    ]
    return "\n".join(parts) + "\n"
