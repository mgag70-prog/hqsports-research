#!/usr/bin/env python3
"""Build the in-article charts for mlb-cap-valuations-2026.

fig-01-indexed: average team value indexed to the 2004 list = 100, NHL and MLB, with the
2005 cap marked. Two panels: the full run, and 1999-2012 at a readable scale.
fig-02-ratio: MLB average value divided by NHL average value, by list year, with four
events marked and the four labeled points from the draft.
fig-03-growth: compound annual growth before (1999-2004) and after (2004-2011) the cap,
paired bars for NHL and MLB, with the gap written between each pair.
fig-04-multiples: revenue multiples on Forbes' 2026 lists (MLB, NHL, NFL, NBA) and the
2011-12 point where MLB and NHL were both 2.5x.

Every value comes from model/recompute_outline.py, which reads data/forbes-avg-team-value.csv,
except the NBA and NFL multiples, which are constants from the same Forbes March 20, 2026
article the CSV cites for MLB. All outline checks must pass, and every drawn value and label
is asserted against draft.md and captions.md before any SVG is written.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and falls back
to Georgia, matching the other pieces.

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
KEYS = ("fig-01-indexed", "fig-02-ratio", "fig-03-growth", "fig-04-multiples")

# Forbes, March 20, 2026: the other leagues' average multiples, quoted in the same sentence as MLB's 7.0x.
OTHER_MULTIPLES = {"NBA": 12.9, "NFL": 10.7}
NHL_ROUNDED = 9          # Forbes' rounding of the 8.9x on its December 2025 NHL list
NFL_2026 = 13.4          # Forbes' September 9, 2026 NFL list, after the March article

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute_outline as R
assert not R.mismatches, f"recompute_outline.py reports mismatches: {R.mismatches}"

nhl, mlb, mult = R.nhl, R.mlb, R.multiple
basis = {(r["league"], int(r["list_year"])): r["value_basis"] for r in R.rows}
soft = {k for k, b in basis.items() if b.startswith("calc") or b.startswith("secondary")}
idx_nhl = {y: 100 * v / nhl[2004] for y, v in nhl.items()}
idx_mlb = {y: 100 * v / mlb[2004] for y, v in mlb.items()}
ratio = {y: mlb[y] / nhl[y] for y in nhl if y in mlb}
G = {"NHL pre": 100 * R.cagr(nhl[1999], nhl[2004], 5), "MLB pre": 100 * R.cagr(mlb[1999], mlb[2004], 5),
     "NHL post": 100 * R.cagr(nhl[2004], nhl[2011], 7), "MLB post": 100 * R.cagr(mlb[2004], mlb[2011], 7)}
GAP_PRE, GAP_POST = G["MLB pre"] - G["NHL pre"], G["MLB post"] - G["NHL post"]
assert round(mult[("NHL", 2025)]) == NHL_ROUNDED
print(f"model: {R.checked} outline checks pass; growth {G}")

# --------------------------------------------------------------------------
# Assert against the draft and the captions
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
captions = CAPTIONS.read_text()
m = lambda v: f"${v:,.0f} million" if v < 1000 else f"${v / 1000:.1f} billion"
DRAFT_PHRASES = (
    f"from ${nhl[1999]:.0f} million to ${nhl[2004]:.0f} million, {G['NHL pre']:.2f}% a year",
    f"from ${mlb[1999]:.1f} million to ${mlb[2004]:.0f} million, {G['MLB pre']:.2f}% a year",
    f"from ${nhl[2004]:.0f} million to ${nhl[2011]:.0f} million, up {100 * (nhl[2011] / nhl[2004] - 1):.1f}%, or {G['NHL post']:.2f}% a year",
    f"from ${mlb[2004]:.0f} million to ${mlb[2011]:.0f} million, up {100 * (mlb[2011] / mlb[2004] - 1):.1f}%, or {G['MLB post']:.2f}% a year",
    f"{GAP_PRE:.2f} points before the cap, {GAP_POST:.2f} after it",
    f"worth {ratio[2004]:.2f} times the average hockey team on the 2004 lists and {ratio[2011]:.2f} times on the 2011 lists",
    f"peaked at {ratio[2020]:.2f} on the 2020 lists and fell to {ratio[2025]:.2f} by 2025",
    f"from {m(nhl[2012])} to {m(nhl[2025])}, {100 * R.cagr(nhl[2012], nhl[2025], 13):.2f}% a year",
    f"from {m(mlb[2012])} to {m(mlb[2025])} over the same lists, {100 * R.cagr(mlb[2012], mlb[2025], 13):.2f}% a year",
    f"{mult[('NHL', 2012)]:.1f} times revenue on the 2012 list, {mult[('NHL', 2014)]:.1f} on the 2014 list, "
    f"{mult[('NHL', 2022)]:.1f} on the 2022 list, {mult[('NHL', 2024)]:.1f} on the 2024 list and {mult[('NHL', 2025)]:.1f} on the 2025 list",
    f"{m(mlb[2026])}, {mult[('MLB', 2026)]:.1f} times revenue. The NBA's average multiple was {OTHER_MULTIPLES['NBA']}, "
    f"the NFL's {OTHER_MULTIPLES['NFL']}, the NHL's {NHL_ROUNDED}",
    f"baseball at {mult[('MLB', 2011)]:.1f} times revenue on its March 2011 list",
    f"rounded up from {mult[('NHL', 2025)]:.1f}, and the football figure is from its August 2025 list; "
    f"Forbes' September 9, 2026 NFL list has since put the NFL at {NFL_2026}x",
    f"dips to {ratio[2014]:.2f} on the 2014 lists and jumps back to {ratio[2015]:.2f} on the 2015 lists",
    f"{100 * (nhl[2014] / nhl[2013] - 1):.1f}% jump in average value on its 2014 list",
)
for phrase in DRAFT_PHRASES:
    assert phrase in draft, f"draft no longer says: {phrase}"
assert max(ratio, key=ratio.get) == 2020 and all(idx_mlb[y] > idx_nhl[y] for y in range(2006, 2013)), "fig-01 claim"
# the title: "the last league to get one grew slower than baseball for seven years" is the 2004-2011 comparison
H1 = draft.splitlines()[0].removeprefix("# ")
assert H1 == "Baseball's owners want a salary cap. The last league to get one grew slower than baseball for seven years.", H1
assert "seven years" in H1 and 2011 - 2004 == 7 and G["NHL post"] < G["MLB post"], "title claim"
assert "from the 2004 lists to the 2011 lists" in draft and "No other major league has adopted a cap inside Forbes' valuation record" in draft
print(f"draft matches the model: {len(DRAFT_PHRASES)} phrases; MLB index above NHL on every list 2006-2012")

CAPTION_PHRASES = (
    f"MLB {mult[('MLB', 2026)]:.1f}x, NHL {NHL_ROUNDED}x, NFL {OTHER_MULTIPLES['NFL']}x, NBA {OTHER_MULTIPLES['NBA']}x",
    f"The NHL figure is from Forbes' December 2025 hockey list, {mult[('NHL', 2025)]:.1f}x rounded to {NHL_ROUNDED}x",
    f"Forbes' September 9, 2026 NFL list now puts the NFL at {NFL_2026}x",
    f"baseball at {mult[('MLB', 2011)]:.1f}x on its March 2011 list and hockey at {mult[('NHL', 2012)]:.1f}x on its 2012 list",
    f"hockey grew {G['NHL pre']:.2f}% a year and baseball {G['MLB pre']:.2f}%, a gap of {GAP_PRE:.2f} points",
    f"hockey grew {G['NHL post']:.2f}% a year and baseball {G['MLB post']:.2f}%, a gap of {GAP_POST:.2f} points",
    f"hockey's index reaches {idx_nhl[2025]:,.0f} and baseball's {idx_mlb[2026]:,.0f}",
    f"It was {ratio[2004]:.2f} on the 2004 lists, {ratio[2011]:.2f} on the 2011 lists, {ratio[2020]:.2f} at the peak on the 2020 lists, "
    f"and {ratio[2025]:.2f} on the 2025 lists",
    f"The dip to {ratio[2014]:.2f} in 2014 and the rebound to {ratio[2015]:.2f} in 2015",
)
for phrase in CAPTION_PHRASES:
    assert phrase in captions, f"captions.md no longer says: {phrase}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
print(f"captions match the model ({len(CAPTION_PHRASES)} phrases) and all four draft slots exist")

# --------------------------------------------------------------------------
# SVG helpers (house style)
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, halo=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if halo:
            extra += f' stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill):
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>')

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


def marker(s, x, y, key, color, r=4.5):
    if key in soft:
        s.circle(x, y, r, PAPER, stroke=color, sw=2)
    else:
        s.circle(x, y, r, color)


def series(s, xs, ys, league, data, color, years):
    pts = [(xs(y), ys(data[y])) for y in years if y in data]
    s.poly(pts, color, 2.5)
    for y in years:
        if y in data:
            marker(s, xs(y), ys(data[y]), (league, y), color)


def legend(s, x, y):
    s.line(x, y - 4, x + 22, y - 4, RED, 2.5)
    s.text(x + 30, y, "NHL", 14, NAVY)
    s.line(x + 80, y - 4, x + 102, y - 4, NAVY, 2.5)
    s.text(x + 110, y, "MLB", 14, NAVY)
    s.circle(x + 176, y - 4, 4.5, PAPER, stroke=NAVY, sw=2)
    s.text(x + 188, y, "computed or secondary figure", 13, MUTED)

# --------------------------------------------------------------------------
# Fig 01: indexed, two panels
# --------------------------------------------------------------------------

def fig_indexed(stem):
    title = "For the seven years after hockey's cap, baseball's values grew faster."
    sub1 = "Forbes' average team value, each league indexed to its 2004 list = 100. Right: the same series, 1999 to 2012, at a readable scale."
    sub2 = "No hockey point for 2005: there was no 2004-05 season."
    Y0, Y1 = 196, 536
    H = Y1 + 100
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    legend(s, 48, 150)

    def panel(X0, X1, y_lo, y_hi, years, step, head, ticks):
        xs = lambda y: X0 + (X1 - X0) * (y - years[0]) / (years[-1] - years[0])
        ys = lambda v: Y1 - (Y1 - Y0) * (v - y_lo) / (y_hi - y_lo)
        col_head(s, X0 - 60, 180, head)
        for v in range(y_lo, y_hi + 1, step):
            s.line(X0, ys(v), X1, ys(v), NAVY if v == 100 else GRID, 1.5 if v == 100 else 1)
            s.text(X0 - 12, ys(v) + 5, f"{v:,}", 12, MUTED, anchor="end")
        for y in ticks:
            s.text(xs(y), Y1 + 24, str(y), 12, MUTED, anchor="middle")
        s.line(xs(2005), Y0 - 6, xs(2005), Y1 + 4, RED, 1.5, dash="4 5")
        return xs, ys

    # left: the full run
    xs, ys = panel(120, 640, 0, 1400, list(range(1999, 2027)), 200, "INDEX, 2004 LIST = 100", range(2000, 2027, 5))
    s.text(xs(2005) + 6, Y0 + 4, "2005 cap", 12, RED)
    series(s, xs, ys, "NHL", idx_nhl, RED, range(1999, 2026))
    series(s, xs, ys, "MLB", idx_mlb, NAVY, range(1999, 2027))
    s.text(xs(2025) - 8, ys(idx_nhl[2025]) + 4, f"NHL {idx_nhl[2025]:,.0f}", 13, RED, anchor="end", halo=True)
    s.text(xs(2026) + 8, ys(idx_mlb[2026]) + 4, f"MLB {idx_mlb[2026]:,.0f}", 13, NAVY, halo=True)

    # right: 1999-2012, the cap window
    xs, ys = panel(760, 1150, 60, 220, list(range(1999, 2013)), 40, "SAME INDEX, 1999 TO 2012", (2000, 2004, 2008, 2012))
    s.rect(xs(2004), Y0, xs(2011) - xs(2004), Y1 - Y0, SHADE)
    s.text((xs(2004) + xs(2011)) / 2, Y0 + 16, "seven years after the cap", 12, MUTED, anchor="middle")
    s.text(xs(2005) + 6, Y0 + 36, "2005 cap", 12, RED)
    series(s, xs, ys, "NHL", idx_nhl, RED, range(1999, 2013))
    series(s, xs, ys, "MLB", idx_mlb, NAVY, range(1999, 2013))
    s.text(xs(2011) + 8, ys(idx_mlb[2011]) + 4, f"MLB {idx_mlb[2011]:.0f}", 13, NAVY, halo=True)
    s.text(xs(2011) + 8, ys(idx_nhl[2011]) + 4, f"NHL {idx_nhl[2011]:.0f}", 13, RED, halo=True)

    s.text(48, H - 14, "Source: Forbes average team values by list year (data/forbes-avg-team-value.csv). Index calculated.",
           12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 02: the ratio
# --------------------------------------------------------------------------

def fig_ratio(stem):
    title = "The gap widened under hockey's cap and closed in the years of hockey's TV deals."
    sub1 = "Average MLB team value divided by average NHL team value, by Forbes list year."
    sub2 = "The 2014 dip and 2015 rebound are mostly Forbes changing its method for the two leagues in different years."
    X0, X1 = 110, 1110
    Y0, Y1, VMIN, VMAX = 196, 536, 1.0, 3.0
    years = sorted(ratio)
    xs = lambda y: X0 + (X1 - X0) * (y - 1999) / (2025 - 1999)
    ys = lambda v: Y1 - (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
    H = Y1 + 100
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 160, "MLB AVERAGE VALUE / NHL AVERAGE VALUE")

    for v in (1.0, 1.5, 2.0, 2.5, 3.0):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 1.0 else GRID, 1.5 if v == 1.0 else 1)
        s.text(X0 - 12, ys(v) + 5, f"{v:.1f}x", 12, MUTED, anchor="end")
    for y in range(2000, 2026, 5):
        s.text(xs(y), Y1 + 24, str(y), 12, MUTED, anchor="middle")

    events = [(2005, "2005 cap"), (2013.9, "Rogers deal, Nov. 2013"), (2021.3, "ESPN and Turner, 2021"),
              (2023.2, "Diamond Sports Ch. 11, Mar. 2023")]
    for i, (x, label) in enumerate(events):
        s.line(xs(x), Y0 - 6, xs(x), Y1, RED if i == 0 else FAINT, 1.5, dash="4 5")
        if i == 3:   # the last mark sits near the right edge: a short label on its own row
            s.text(xs(x) + 6, Y0 + 40, "Diamond Ch. 11, Mar. 2023", 12, MUTED)
        else:
            s.text(xs(x) + 6, Y0 + 4 + (i % 2) * 18, label, 12, RED if i == 0 else MUTED)

    pts = [(xs(y), ys(ratio[y])) for y in years]
    s.poly(pts, NAVY, 2.5)
    for y in years:
        soft_pt = ("NHL", y) in soft or ("MLB", y) in soft
        s.circle(xs(y), ys(ratio[y]), 4.5, PAPER if soft_pt else NAVY, stroke=NAVY if soft_pt else None, sw=2)
    for y, dy, anchor in ((2004, -14, "middle"), (2011, -14, "middle"), (2020, -14, "middle"), (2025, 26, "end")):
        s.circle(xs(y), ys(ratio[y]), 6, RED)
        s.text(xs(y), ys(ratio[y]) + dy, f"{ratio[y]:.2f}", 14, RED, anchor=anchor, halo=True)
    s.text(xs(2014.5), ys(min(ratio[2014], ratio[2015])) + 34, "method change", 12, MUTED, anchor="middle", halo=True)

    s.text(48, H - 14, "Source: Forbes average team values by list year (data/forbes-avg-team-value.csv). Ratio calculated. "
                       "Hollow markers use a computed or secondary average.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 03: growth before and after
# --------------------------------------------------------------------------

def fig_growth(stem):
    title = "Both leagues grew faster after 2004. Baseball pulled further ahead."
    sub1 = "Compound annual growth in Forbes' average team value, over the five lists before the cap and the seven after it."
    X0, X1 = 130, 1080
    Y0, Y1, VMAX = 176, 516, 10
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 120
    s = SVG(1200, H, title)
    header(s, title, sub1)
    col_head(s, 48, 150, "GROWTH, PERCENT A YEAR")
    for v in range(0, VMAX + 1, 2):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 12, ys(v) + 5, f"{v}%", 12, MUTED, anchor="end")
    BW, GAP = 120, 16
    for i, (label, sub, a, b, gap) in enumerate((
            ("1999 to 2004 lists", "five years before the cap", G["NHL pre"], G["MLB pre"], GAP_PRE),
            ("2004 to 2011 lists", "seven years after the cap", G["NHL post"], G["MLB post"], GAP_POST))):
        cx = X0 + (X1 - X0) * (i + 0.5) / 2
        for x, v, col, name in ((cx - GAP / 2 - BW, a, RED, "NHL"), (cx + GAP / 2, b, NAVY, "MLB")):
            s.rect(x, ys(v), BW, Y1 - ys(v), col)
            s.text(x + BW / 2, ys(v) - 10, f"{v:.2f}%", 15, col, anchor="middle")
            s.text(x + BW / 2, Y1 + 24, name, 14, NAVY, anchor="middle")
        s.text(cx, Y1 + 56, label, 15, NAVY, anchor="middle")
        s.text(cx, Y1 + 76, sub, 12, MUTED, anchor="middle")
        s.text(cx, ys(max(a, b)) - 36, f"gap {gap:.2f} points", 13, MUTED, anchor="middle")
    s.text(48, H - 14, "Source: Forbes average team values by list year (data/forbes-avg-team-value.csv). Growth rates calculated.",
           12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 04: multiples
# --------------------------------------------------------------------------

def fig_multiples(stem):
    title = "Seven years into hockey's cap, the two leagues sold at the same multiple. They don't now."
    sub1 = "Left: average team value as a multiple of revenue, the four leagues as Forbes cited them in March 2026. Right: MLB and NHL fifteen years earlier."
    sub2 = (f"NHL: December 2025 list, {mult[('NHL', 2025)]:.1f}x rounded to {NHL_ROUNDED}x. NFL: August 2025 list; "
            f"Forbes' September 9, 2026 list puts the NFL at {NFL_2026}x.")
    H = 520
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    rows = [("MLB", mult[("MLB", 2026)], f"{mult[('MLB', 2026)]:.1f}x", RED),
            ("NHL", NHL_ROUNDED, f"{NHL_ROUNDED}x", NAVY),
            ("NFL", OTHER_MULTIPLES["NFL"], f"{OTHER_MULTIPLES['NFL']}x", NAVY),
            ("NBA", OTHER_MULTIPLES["NBA"], f"{OTHER_MULTIPLES['NBA']}x", NAVY)]
    X0, X1, VMAX = 160, 700, 14
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    col_head(s, 48, 160, "AS CITED BY FORBES, MARCH 20, 2026")
    for i, (name, v, label, col) in enumerate(rows):
        y = 190 + i * 60
        s.text(X0 - 14, y + 23, name, 15, NAVY, anchor="end")
        s.rect(X0, y, xs(v) - X0, 34, col)
        s.text(xs(v) + 10, y + 23, label, 16, col)
    s.line(X0, 430, X1, 430, NAVY, 1.5)
    for v in range(0, VMAX + 1, 2):
        s.text(xs(v), 452, f"{v}x", 12, MUTED, anchor="middle")

    X2, X3 = 900, 1130
    xs2 = lambda v: X2 + (X3 - X2) * v / VMAX
    col_head(s, 820, 160, "2011 AND 2012 LISTS")
    for i, (name, v, label, when) in enumerate((("MLB", mult[("MLB", 2011)], f"{mult[('MLB', 2011)]:.1f}x", "March 2011 list"),
                                                ("NHL", mult[("NHL", 2012)], f"{mult[('NHL', 2012)]:.1f}x", "2012 list"))):
        y = 190 + i * 60
        s.text(X2 - 14, y + 23, name, 15, NAVY, anchor="end")
        s.rect(X2, y, xs2(v) - X2, 34, PALE)
        s.text(xs2(v) + 10, y + 16, label, 16, NAVY)
        s.text(xs2(v) + 10, y + 32, when, 11, MUTED)
    s.line(X2, 430, X3, 430, NAVY, 1.5)
    for v in range(0, VMAX + 1, 7):
        s.text(xs2(v), 452, f"{v}x", 12, MUTED, anchor="middle")
    s.text(820, 330, "Seven years into hockey's cap,", 13, MUTED)
    s.text(820, 348, "the two leagues sold at the same multiple.", 13, MUTED)

    s.text(48, H - 14, "Source: Forbes, March 20, 2026 (MLB, NBA, NFL, NHL); Forbes NHL lists, December 2025 and November 2014 "
                       "(the 2012 multiple as stated there); Forbes MLB list, March 2011; Forbes NFL lists, August 28, 2025 and September 9, 2026.", 12, MUTED)
    s.write(stem)


fig_indexed(KEYS[0])
fig_ratio(KEYS[1])
fig_growth(KEYS[2])
fig_multiples(KEYS[3])
print("done ->", OUT)
