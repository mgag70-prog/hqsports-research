#!/usr/bin/env python3
"""Build the in-article charts for wrigley-season-tickets-2026.

fig-01-per-seat: price per seat, 1998-2021, nominal, as two line segments with a gap
at 2004 where the seats changed. Hollow markers for rounded years, solid for exact.
fig-02-real-total: the Section 105 four-seat total in 2021 dollars, 2004-2021, with a
rule at 2015, the rounded years shaded, and the two compound rates labeled.
fig-03-price-vs-cpi: one pair of bars for 2004-2015 as a compound annual rate, then
paired bars for each exact year 2016-2021, the seats' nominal change beside CPI's.
fig-04-stat-tiles: Section 105 price per seat at 2004, 2015 and 2021, as three tiles.
The 1998-2003 seats were Section 213 and their totals may include parking and playoff
strips, so no figure compares them with Section 105, and a guard fails the build if
"upper deck" is attached to Matt's own seats anywhere in the draft's own-seat passages,
the captions or the charts.

Every value comes from model/recompute_outline.py, which reads the two CSVs in data/.
All of its outline checks must pass, and every value drawn is asserted against draft.md
and captions.md before any SVG is written.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and falls
back to Georgia, matching the other pieces.

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to this script's directory; --final skips the 700px previews.
"""
import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

PIECE = Path(__file__).resolve().parents[1]
REPO = PIECE.parent
DRAFT = PIECE / "draft.md"
CAPTIONS = PIECE / "figures/captions.md"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv

NAVY = "#16284A"
RED = "#D4553D"
PAPER = "#F7F5F0"
MUTED = "rgba(22,40,74,0.62)"
FAINT = "rgba(22,40,74,0.40)"
PALE = "rgba(22,40,74,0.18)"
GRID = "rgba(22,40,74,0.13)"
SHADE = "rgba(22,40,74,0.06)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
HATCH = ('<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" '
         f'patternTransform="rotate(45)"><rect width="7" height="7" fill="{PAPER}"/>'
         f'<rect width="2.5" height="7" fill="{NAVY}" fill-opacity="0.5"/></pattern>'
         '<pattern id="hatchgray" width="7" height="7" patternUnits="userSpaceOnUse" '
         f'patternTransform="rotate(45)"><rect width="7" height="7" fill="{PAPER}"/>'
         f'<rect width="2.5" height="7" fill="{NAVY}" fill-opacity="0.22"/></pattern></defs>')
KEYS = ("fig-01-per-seat", "fig-02-real-total", "fig-03-price-vs-cpi", "fig-04-stat-tiles")

# --------------------------------------------------------------------------
# Model: the same module that checks the outline against the CSVs
# --------------------------------------------------------------------------

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute_outline as R
assert not R.mismatches, f"recompute_outline.py reports mismatches: {R.mismatches}"

YEARS = R.years
total, seats, cpi, exact = R.total, R.seats, R.cpi, R.exact
per_seat = {y: total[y] / seats[y] for y in YEARS}
real = {y: R.real(y) for y in YEARS}
chg = {y: 100 * (total[y] / total[y - 1] - 1) for y in YEARS if y > 2004}
cpi_chg = {y: 100 * (cpi[y] / cpi[y - 1] - 1) for y in YEARS if y > 1998}
R1 = 100 * R.cagr(real[2004], real[2015], 11)
R2 = 100 * R.cagr(real[2015], real[2021], 6)
N1 = 100 * R.cagr(total[2004], total[2015], 11)
C1 = 100 * R.cagr(cpi[2004], cpi[2015], 11)
C2 = 100 * R.cagr(cpi[2015], cpi[2021], 6)
PER_DATE = per_seat[2021] / R.HOME_DATES
print(f"model: {R.checked} outline checks pass; real rates {R1:.1f}% and {R2:.1f}% a year")

# --------------------------------------------------------------------------
# Assert against the draft and the captions
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
captions = CAPTIONS.read_text()
money = lambda v: f"${v:,.2f}" if round(v * 100) % 100 else f"${v:,.0f}"
DRAFT_PHRASES = (
    f"${total[1998]:,.0f} for the season, {money(per_seat[1998])} a seat",
    f"${total[2003]:,.0f}, {money(per_seat[2003])} a seat",
    f"${total[2004]:,.0f}, which is {money(per_seat[2004])} a seat",
    f"the four cost ${total[2015]:,.0f}, or {money(per_seat[2015])} a seat",
    "may include parking and playoff strips",
    f"${total[2021]:,.0f}: {money(per_seat[2021])} a seat, or about ${PER_DATE:.2f} a seat for each of the "
    f"{R.HOME_DATES} home dates",
    f"That's {N1:.1f}% a year before inflation; CPI over the same eleven years ran {C1:.1f}% a year",
    f"from ${real[2004]:,.0f} to ${real[2015]:,.0f}, up {100 * (real[2015] / real[2004] - 1):.1f}% in total, "
    f"or {R1:.1f}% a year",
    f"from ${real[2015]:,.0f} in 2015 to ${real[2021]:,.0f} in 2021, up {100 * (real[2021] / real[2015] - 1):.1f}%, "
    f"or {R2:.1f}% a year",
    f"CPI ran {C2:.1f}% a year over those six years, against {C1:.1f}% a year",
    f"{chg[2016]:.1f}% for 2016, {chg[2017]:.1f}% for 2017, {chg[2018]:.1f}% for 2018, {chg[2019]:.1f}% for 2019, "
    f"{chg[2020]:.1f}% for 2020 and {chg[2021]:.1f}% for 2021",
    f"from ${total[2015]:,.0f} to ${total[2016]:,.2f}, both exact",
    f"rose {13.0:.1f}% in the first 11 and {100 * (real[2021] / real[2015] - 1):.1f}% in the last six",
)
for phrase in DRAFT_PHRASES:
    assert phrase in draft, f"draft no longer says: {phrase}"
lo, hi = total[2004] - 1000, total[2004] + 1000
sens = (f"between {100 * R.cagr(hi, total[2015], 11):.1f}% and {100 * R.cagr(lo, total[2015], 11):.1f}% a year "
        f"before inflation and between {100 * R.cagr(R.real(2004, hi), real[2015], 11):.1f}% and "
        f"{100 * R.cagr(R.real(2004, lo), real[2015], 11):.1f}% a year after it")
assert sens in draft, f"draft no longer says: {sens}"
assert "4.0%" not in draft, "the 2015-over-rounded-2014 figure is back in the draft"
own_seats = draft.split("## Eleven years")[0]          # construction note, section 1, fig-01 and fig-04 alt text
assert "upper deck" not in own_seats.lower(), "the draft calls Matt's 1998-2003 seats 'upper deck' again"
assert "cheaper per seat" not in draft, "the draft compares Section 213 per-seat prices with Section 105"
assert "upper deck" not in captions.lower(), "captions.md attaches 'upper deck' to Matt's seats"
for y in range(2005, 2016):   # whole tokens only, so 13.0% doesn't trip the 3.0% of 2005
    assert not re.search(r"(?<![\d.$])" + re.escape(f"{chg[y]:.1f}%"), draft), \
        f"draft quotes a rounded-year change: {y} ({chg[y]:.1f}%)"
print(f"draft matches the model: {len(DRAFT_PHRASES) + 1} phrases, no single-year figure before 2016")

CAPTION_PHRASES = (
    f"cost {money(per_seat[2004])} each in 2004, from a total I rounded; {money(per_seat[2015])} each in 2015, "
    f"the first year with an exact invoice; and {money(per_seat[2021])} each in 2021, which works out to about "
    f"${PER_DATE:.2f} a seat for each of the {R.HOME_DATES} home dates",
    "may include parking and playoff strips",
    f"Section 213 went from {money(per_seat[1998])} to {money(per_seat[2003])} and Section 105 from "
    f"{money(per_seat[2004])} to {money(per_seat[2021])}",
    f"From ${real[2004]:,.0f} in 2004 to ${real[2015]:,.0f} in 2015 is {R1:.1f}% a year; from there to "
    f"${real[2021]:,.0f} in 2021 is {R2:.1f}% a year",
    f"at {N1:.1f}% a year against {C1:.1f}% for CPI",
    f"{chg[2016]:.1f}%, {chg[2017]:.1f}%, {chg[2018]:.1f}%, {chg[2019]:.1f}%, {chg[2020]:.1f}% and {chg[2021]:.1f}%, "
    f"against CPI that never ran above {max(cpi_chg[y] for y in range(2016, 2022)):.1f}% in any of those years",
)
for phrase in CAPTION_PHRASES:
    assert phrase in captions, f"captions.md no longer says: {phrase}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
print(f"captions match the model ({len(CAPTION_PHRASES)} phrases) and all four draft slots exist")

# --------------------------------------------------------------------------
# SVG helpers (house style, shared with pca-mvp-2026)
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}{HATCH}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, halo=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if halo:
            extra += f' stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def circle(self, cx, cy, r, fill, stroke=None, sw=0):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def poly(self, pts, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                          f'stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def write(self, stem):
        self.parts.append("</svg>")
        assert "upper deck" not in "".join(self.parts).lower(), f"{stem} labels Matt's seats 'upper deck'"
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(self.w), str(svg), "-o", str(png)], check=True)
        if not FINAL:
            subprocess.run(["magick", str(png), "-resize", "700x", str(OUT / f"{stem}-700.png")], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


def header(s, title, *subs):
    s.text(48, 46, title, 28)
    for i, sub in enumerate(subs):
        s.text(48, 76 + i * 22, sub, 17, MUTED)


def col_head(s, x, y, label, anchor="start", fill=MUTED):
    s.text(x, y, label, 12, fill, anchor=anchor, spacing=1.8)


def marker(s, x, y, year, r=5.5):
    """Solid for an exact invoice, hollow for a rounded total."""
    if year in exact:
        s.circle(x, y, r, NAVY)
    else:
        s.circle(x, y, r, PAPER, stroke=NAVY, sw=2)


def legend_markers(s, x, y):
    s.circle(x + 6, y - 4, 5.5, PAPER, stroke=NAVY, sw=2)
    s.text(x + 20, y, "rounded total", 14, NAVY)
    s.circle(x + 150, y - 4, 5.5, NAVY)
    s.text(x + 164, y, "exact invoice", 14, NAVY)

# --------------------------------------------------------------------------
# Fig 01: price per seat, two segments
# --------------------------------------------------------------------------

def fig_per_seat(stem):
    title = "Two seats in Section 213, then four in Section 105: the price per seat, 1998 to 2021."
    sub1 = ("Price per seat in the dollars of each year. The line breaks where the seats changed; "
            "the Section 213 totals may include parking and playoff strips.")
    sub2 = "Hollow markers are totals I rounded; solid markers, from 2015 on, are exact invoices."
    X0, X1 = 120, 1110
    Y0, Y1, VMAX = 196, 536, 10000
    xs = lambda y: X0 + (X1 - X0) * (y - 1998) / (2021 - 1998)
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 100
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 150, "PRICE PER SEAT, NOMINAL")
    legend_markers(s, 820, 150)

    for v in range(0, VMAX + 1, 2000):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 14, ys(v) + 5, "$0" if v == 0 else f"${v // 1000:,}k", 13, MUTED, anchor="end")
    for y in range(1998, 2022, 2):
        s.text(xs(y), Y1 + 26, str(y), 13, MUTED, anchor="middle")

    upper = [y for y in YEARS if seats[y] == 2]
    lower = [y for y in YEARS if seats[y] == 4]
    s.poly([(xs(y), ys(per_seat[y])) for y in upper], NAVY, 2.5)
    s.poly([(xs(y), ys(per_seat[y])) for y in lower], NAVY, 2.5)
    for y in YEARS:
        marker(s, xs(y), ys(per_seat[y]), y)
    s.line(xs(2003.5), Y0 - 10, xs(2003.5), Y1, FAINT, 1.5, dash="4 5")

    s.text(xs(1998) + 2, ys(per_seat[1998]) - 16, f"{money(per_seat[1998])}", 14, NAVY, halo=True)
    s.text(xs(2003) - 6, ys(per_seat[2003]) - 16, f"{money(per_seat[2003])}", 14, NAVY, anchor="end", halo=True)
    s.text(xs(2004) + 10, ys(per_seat[2004]) + 24, f"{money(per_seat[2004])}", 14, NAVY, halo=True)
    s.text(xs(2021) - 10, ys(per_seat[2021]) - 16, f"{money(per_seat[2021])}", 14, NAVY, anchor="end", halo=True)
    s.text(xs(2000.5), Y0 + 8, "Two seats, Section 213", 14, MUTED, anchor="middle")
    s.text(xs(2012), Y0 + 8, "Four seats, Section 105 field box", 14, MUTED, anchor="middle")

    s.text(48, H - 14, "Source: my season-ticket invoices, 1998 through 2021. Totals through 2014 rounded by me; "
                       "2015 on exact.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 02: the four-seat total in 2021 dollars
# --------------------------------------------------------------------------

def fig_real_total(stem):
    title = f"The same four seats in 2021 dollars: {R1:.1f}% a year for eleven years, then {R2:.1f}% a year for six."
    sub1 = "Section 105 four-seat season total, 2004 to 2021, restated with BLS CPI-U annual averages."
    sub2 = "Years before 2015 are rounded totals, shaded here, and read from their endpoints only."
    X0, X1 = 130, 1110
    Y0, Y1, VMIN, VMAX = 196, 536, 20000, 40000
    xs = lambda y: X0 + (X1 - X0) * (y - 2004) / (2021 - 2004)
    ys = lambda v: Y1 - (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
    H = Y1 + 100
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 150, "FOUR-SEAT SEASON TOTAL, 2021 DOLLARS")
    legend_markers(s, 820, 150)

    s.rect(xs(2004) - 12, Y0 - 10, xs(2014.5) - xs(2004) + 12, Y1 - Y0 + 10, SHADE)
    for v in range(VMIN, VMAX + 1, 5000):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 14, ys(v) + 5, f"${v // 1000}k", 13, MUTED, anchor="end")
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    for y in (*range(2004, 2021, 2), 2021):
        s.text(xs(y), Y1 + 26, str(y), 13, MUTED, anchor="middle")

    s.line(xs(2015), Y0 - 10, xs(2015), Y1, RED, 1.5, dash="4 5")
    s.text(xs(2015) + 8, Y0 + 6, "2015: first exact invoice", 13, RED)

    pts = [y for y in YEARS if y >= 2004]
    s.poly([(xs(y), ys(real[y])) for y in pts], NAVY, 2.5)
    for y in pts:
        marker(s, xs(y), ys(real[y]), y)

    # the two rates, each written over its own stretch of the line
    s.text(xs(2009.5), ys(real[2015]) - 76, f"{R1:.1f}% a year, 2004 to 2015", 16, NAVY, anchor="middle", halo=True)
    s.text(xs(2009.5), ys(real[2015]) - 54, f"CPI {C1:.1f}% a year", 13, MUTED, anchor="middle", halo=True)
    s.text(xs(2018.6), ys(28600), f"{R2:.1f}% a year, 2015 to 2021", 16, RED, anchor="middle", halo=True)
    s.text(xs(2018.6), ys(27300), f"CPI {C2:.1f}% a year", 13, MUTED, anchor="middle", halo=True)
    s.text(xs(2004) + 6, ys(real[2004]) + 24, f"${real[2004]:,.0f}", 14, NAVY, halo=True)
    s.text(xs(2015) - 10, ys(real[2015]) + 46, f"${real[2015]:,.0f}", 14, NAVY, anchor="end", halo=True)
    s.text(xs(2021) - 6, ys(real[2021]) - 16, f"${real[2021]:,.0f}", 14, NAVY, anchor="end", halo=True)

    s.text(48, H - 14, "Source: my invoices; BLS CPI-U annual averages, 1982-84=100. Real figures and rates calculated.",
           12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 03: price change against CPI change
# --------------------------------------------------------------------------

def fig_price_vs_cpi(stem):
    title = "After 2015 the seats rose faster than inflation every year."
    sub1 = "Change in the four-seat total (navy) beside the change in CPI-U (gray)."
    sub2 = "Left: 2004 to 2015 as one compound annual rate, because those totals are rounded. Right: each exact year."
    X0, X1 = 110, 1130
    Y0, Y1, VMAX = 196, 536, 16
    groups = ["2004-2015"] + list(range(2016, 2022))
    gw = (X1 - X0 - 60) / len(groups)              # 60px of air between the period pair and the years
    bw = gw * 0.34
    xs = lambda g: X0 + gw * (groups.index(g) + 0.5) + (0 if g == "2004-2015" else 60)
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 110
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 150, "CHANGE, PERCENT")
    s.rect(820, 140, 14, 12, NAVY)
    s.text(840, 151, "four-seat total", 14, NAVY)
    s.rect(960, 140, 14, 12, PALE)
    s.text(980, 151, "CPI-U", 14, NAVY)

    for v in range(0, VMAX + 1, 2):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 14, ys(v) + 5, f"{v}%", 13, MUTED, anchor="end")

    def pair(g, v, c):
        x = xs(g)
        s.rect(x - bw - 1.5, ys(v), bw, Y1 - ys(v), NAVY)
        s.rect(x + 1.5, ys(c), bw, Y1 - ys(c), PALE)
        s.text(x - bw / 2 - 1.5, ys(v) - 8, f"{v:.1f}%", 12, NAVY, anchor="middle")
        s.text(x + bw / 2 + 1.5, ys(c) - 8, f"{c:.1f}%", 12, MUTED, anchor="middle")

    pair("2004-2015", N1, C1)
    s.text(xs("2004-2015"), Y1 + 26, "2004-2015", 13, NAVY, anchor="middle")
    s.text(xs("2004-2015"), Y1 + 44, "a year, compound", 12, MUTED, anchor="middle")
    sep = xs("2004-2015") + gw / 2 + 30
    s.line(sep, Y0 - 10, sep, Y1 + 50, FAINT, 1.5, dash="4 5")
    for y in range(2016, 2022):
        pair(y, chg[y], cpi_chg[y])
        s.text(xs(y), Y1 + 26, str(y), 13, NAVY, anchor="middle")
    s.text((xs(2018) + xs(2019)) / 2, Y1 + 44, "year over year, exact invoices", 12, MUTED,
           anchor="middle")

    s.text(48, H - 14, "Source: my invoices; BLS CPI-U annual averages. Changes calculated. The 2004-2015 pair is a "
                       "compound annual rate between two endpoints, the 2004 total being rounded.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 04: four tiles
# --------------------------------------------------------------------------

def fig_stat_tiles(stem):
    title = "Section 105, price per seat at three points."
    sub1 = "Four field box seats, nominal dollars. The 2004 figure comes from a total I rounded; 2015 and 2021 are exact."
    H = 420
    s = SVG(1200, H, title)
    header(s, title, sub1)
    tiles = [
        (2004, "Four seats, Section 105", "rounded total"),
        (2015, "Four seats, Section 105", "exact; the first exact invoice"),
        (2021, "Four seats, Section 105", f"exact; about ${PER_DATE:.2f} per home date"),
    ]
    X0, X1, TY, TH = 48, 1152, 128, 230
    gap = 18
    tw = (X1 - X0 - gap * (len(tiles) - 1)) / len(tiles)
    for i, (y, what, note) in enumerate(tiles):
        x = X0 + i * (tw + gap)
        accent = RED if y == 2021 else NAVY
        s.rect(x, TY, tw, TH, SHADE)
        s.rect(x, TY, tw, 4, accent)
        col_head(s, x + 22, TY + 44, str(y), fill=accent)
        s.text(x + 22, TY + 112, money(per_seat[y]), 40, accent)
        s.text(x + 22, TY + 142, "a seat", 15, MUTED)
        s.text(x + 22, TY + 180, what, 14, NAVY)
        s.text(x + 22, TY + 202, note, 12, MUTED)
    s.text(48, H - 14, "Source: my season-ticket invoices. Per-seat and per-date figures calculated.", 12, MUTED)
    s.write(stem)


fig_per_seat(KEYS[0])
fig_real_total(KEYS[1])
fig_price_vs_cpi(KEYS[2])
fig_stat_tiles(KEYS[3])
print("done ->", OUT)
