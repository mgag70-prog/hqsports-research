#!/usr/bin/env python3
"""Build the in-article charts for penn-state-buyout-2026.

fig-01-buyout-schedule: what Penn State owed Franklin at the firing, by contract year.
Seven bars: the 80-day 2025 stub and six $8.0M years, 2026-2031. The bar sum
($49.75M, calculated) is labeled next to the reported $49.7M.

fig-02-two-readings: two panels. Top, on one scale: the reported buyout and the
settlement. Bottom, zoomed to $0-$20M: what the offset clause alone leaves under each
reading, solid for the amount owed whatever happens in 2031 and hatched for 2031
itself, with the settlement as a red line.

fig-03-against-roster: the reported buyout, the roster budget estimate drawn as a
range, the cash out for the coaching change and Campbell's 2026 pay, on one scale.

Every value comes from model/recompute_outline.py, which reads the two CSVs in data/
and the roster budgets CSV. The outline checks must all pass, and every value drawn
is asserted against draft.md and captions.md before any SVG is written.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and
falls back to Georgia, matching the other pieces.

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
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
HATCH = ('<defs><pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" '
         f'patternTransform="rotate(45)"><rect width="9" height="9" fill="{PAPER}"/>'
         f'<rect width="3.5" height="9" fill="{NAVY}" fill-opacity="0.55"/></pattern></defs>')
KEYS = ("fig-01-buyout-schedule", "fig-02-two-readings", "fig-03-against-roster")

# --------------------------------------------------------------------------
# Model: the same module that generates the draft's figures from the CSVs
# --------------------------------------------------------------------------

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute_outline as R
assert not R.mismatches, f"recompute_outline.py reports mismatches: {R.mismatches}"

STUB, STUB_DAYS = R.psu_2025_rest, R.days_left_2025
YEARS = list(range(2026, 2032))
BAR_SUM = STUB + sum(R.psu[y] for y in YEARS)
assert abs(BAR_SUM - R.buyout_rebuilt) < 1e-9
GAP = R.BUYOUT - R.SETTLEMENT
WHOLE_FIRM, WHOLE_MAX = R.whole_thru_2030, R.whole_total
YBY_FIRM, YBY_MAX = R.yby_thru_2030, R.yby_thru_2030 + R.psu[2031]
CASH_OUT = R.SETTLEMENT + R.ISU_BUYOUT
CAMPBELL_G, CAMPBELL_R = R.campbell[2026], R.campbell_retention[2026]
LO, HI = R.lo, R.hi
print(f"model: {R.checked} outline checks pass; bar sum ${BAR_SUM:.3f}M, whole-term ${WHOLE_MAX:.3f}M, "
      f"year-by-year ${YBY_FIRM:.3f}M to ${YBY_MAX:.3f}M")

# --------------------------------------------------------------------------
# Assert against the draft and the captions
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
captions = CAPTIONS.read_text()
assert WHOLE_FIRM < 0.05, WHOLE_FIRM                      # "about $0" through 2030
assert all(R.psu[y] == R.psu[2026] for y in YEARS)        # six equal bars

FIG01 = (f"plus the last {STUB_DAYS} days of 2025",
         f"worth ${sum(R.psu[y] for y in YEARS):.1f} million",
         f"that stub comes to ${STUB:.2f} million and the total to ${BAR_SUM:.2f} million; "
         f"the reported figure was ${R.BUYOUT} million",
         f"guaranteed him ${R.psu[2026]:.1f} million a year")
FIG02 = (f"the gap is ${GAP:.1f} million",
         f"| Owed through 2030 | about $0 | ${YBY_FIRM:.1f}M |",
         f"| 2031, if he earns nothing that year | ${R.psu[2031]:.1f}M | ${R.psu[2031]:.1f}M |",
         f"| Total with nothing earned in 2031 | ${WHOLE_MAX:.1f}M | ${YBY_MAX:.1f}M |",
         f"| Settlement | ${R.SETTLEMENT:.1f}M | ${R.SETTLEMENT:.1f}M |",
         f"maximum possible exposure was ${WHOLE_MAX:.1f} million, so the ${R.SETTLEMENT:.1f} million "
         f"settlement was about ${R.SETTLEMENT - WHOLE_MAX:.1f} million above it",
         f"the settlement was about ${YBY_FIRM - R.SETTLEMENT:.1f} million below the least Penn State "
         f"could have owed")
FIG03 = (f"the ${R.SETTLEMENT:.1f} million settlement plus the ${R.ISU_BUYOUT:.1f} million to Iowa State, "
         f"${CASH_OUT:.1f} million",
         f"${CAMPBELL_G:.1f} million guaranteed plus the ${CAMPBELL_R:.1f} million retention bonus, "
         f"${CAMPBELL_G + CAMPBELL_R:.1f} million",
         f"at ${LO:.0f} million to ${HI:.0f} million",
         f"equals {R.BUYOUT / HI:.2f} to {R.BUYOUT / LO:.2f} years of that roster",
         f"The settlement is {R.SETTLEMENT / HI:.0%} to {R.SETTLEMENT / LO:.0%} of one year")
for phrase in FIG01 + FIG02 + FIG03:
    assert phrase in draft, f"draft no longer says: {phrase}"
print(f"draft matches the model: {len(FIG01)} fig-01 phrases, {len(FIG02)} fig-02, {len(FIG03)} fig-03")

CAPTION_PHRASES = (
    f"the {STUB_DAYS} days left in 2025 for another ${STUB:.2f} million",
    f"The bars sum to ${BAR_SUM:.2f} million, calculated; the figure reported at the time was ${R.BUYOUT} million",
    f"the buyout as reported, ${R.BUYOUT} million, and the ${R.SETTLEMENT:.1f} million settlement, "
    f"a gap of ${GAP:.1f} million (calculated)",
    f"leaves about $0 through 2030 and at most ${WHOLE_MAX:.1f} million",
    f"it leaves ${YBY_FIRM:.1f} million through 2030 and at most ${YBY_MAX:.1f} million",
    f"${LO:.0f} million to ${HI:.0f} million, from The Athletic",
    f"is ${CASH_OUT:.1f} million, the ${R.SETTLEMENT:.1f} million settlement plus ${R.ISU_BUYOUT:.1f} million "
    f"to Iowa State",
    f"is ${CAMPBELL_G + CAMPBELL_R:.1f} million, ${CAMPBELL_G:.1f} million guaranteed plus a "
    f"${CAMPBELL_R:.1f} million retention bonus",
    f"equals {R.BUYOUT / HI:.2f} to {R.BUYOUT / LO:.2f} years of the roster estimate",
    f"the settlement is {R.SETTLEMENT / HI:.0%} to {R.SETTLEMENT / LO:.0%} of one year",
)
for phrase in CAPTION_PHRASES:
    assert phrase in captions, f"captions.md no longer says: {phrase}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
print(f"captions match the model ({len(CAPTION_PHRASES)} phrases) and all three draft slots exist")

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

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

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


def money(v):
    """$8.0M, $1.75M: one decimal unless the figure needs two."""
    return f"${v:.2f}M" if round(v * 100) % 10 else f"${v:.1f}M"


def x_axis(s, xs, y, ticks, x0, x1):
    s.line(x0, y, x1, y, NAVY, 1.5)
    for t in ticks:
        s.line(xs(t), y, xs(t), y + 5, NAVY, 1)
        s.text(xs(t), y + 22, "$0" if t == 0 else f"${t}M", 13, MUTED, anchor="middle")

# --------------------------------------------------------------------------
# Fig 01: the buyout as it was quoted
# --------------------------------------------------------------------------

def fig_buyout_schedule(stem):
    title = f"The ${R.BUYOUT} million was ${R.psu[2026]:.0f} million a year through 2031, plus the rest of 2025."
    sub1 = "What Penn State owed James Franklin on the day it fired him, October 12, 2025, by contract year."
    sub2 = "Guaranteed pay only: base salary, supplemental pay and the life insurance loan."
    X0, X1 = 120, 850
    Y0, Y1, VMAX = 196, 516, 10
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 110
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 166, "OWED FOR EACH YEAR")

    for v in range(0, VMAX + 1, 2):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 14, ys(v) + 5, "$0" if v == 0 else f"${v}M", 13, MUTED, anchor="end")

    bars = [("2025", f"last {STUB_DAYS} days", STUB)] + [(str(y), "", R.psu[y]) for y in YEARS]
    gw, bw = (X1 - X0) / len(bars), 70
    for i, (label, sub, v) in enumerate(bars):
        cx = X0 + gw * (i + 0.5)
        s.rect(cx - bw / 2, ys(v), bw, Y1 - ys(v), NAVY)
        s.text(cx, ys(v) - 10, money(v), 16, NAVY, anchor="middle")
        s.text(cx, Y1 + 26, label, 15, NAVY, anchor="middle")
        if sub:
            s.text(cx, Y1 + 45, sub, 12, MUTED, anchor="middle")

    # the two totals, side by side with their provenance
    tx = 905
    col_head(s, tx, 250, "REPORTED AT THE FIRING")
    s.text(tx, 308, f"${R.BUYOUT}M", 54, RED)
    col_head(s, tx, 372, "THE SEVEN BARS, SUMMED")
    s.text(tx, 414, f"${BAR_SUM:.2f}M", 34, NAVY)
    s.text(tx, 440, "calculated", 14, MUTED)

    s.text(48, H - 32, "Source: contract terms, Onward State (October 8, 2025) and Front Office Sports "
                       "(October 13, 2025). Reported buyout, Front Office Sports (November 17, 2025).", 12, MUTED)
    s.text(48, H - 14, "The 2025 bar is calculated by day count.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 02: reported, the two readings, settled
# --------------------------------------------------------------------------

def fig_two_readings(stem):
    title = "The settlement falls between the two readings of the clause."
    sub1 = ("Top: the buyout as reported and the settlement, on one scale. "
            "Bottom: what the offset clause alone leaves Penn State owing.")
    sub2 = "Solid: owed whatever happens in 2031. Hatched: 2031 itself, owed only if Franklin earns nothing that year."
    X0, X1 = 300, 1010
    BH = 30
    H = 610
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    # ---- top panel: $0 to $50M
    top = lambda v: X0 + (X1 - X0) * v / 50
    col_head(s, 48, 150, "REPORTED AND PAID")
    y_rep, y_set, y_ax = 166, 212, 258
    s.text(X0 - 16, y_rep + 20, "Buyout as reported", 15, NAVY, anchor="end")
    s.rect(X0, y_rep, top(R.BUYOUT) - X0, BH, NAVY)
    s.text(top(R.BUYOUT) + 10, y_rep + 20, f"${R.BUYOUT}M", 16, NAVY)
    s.text(X0 - 16, y_set + 20, "Settlement", 15, NAVY, anchor="end")
    s.rect(X0, y_set, top(R.SETTLEMENT) - X0, BH, RED)
    s.text(top(R.SETTLEMENT) + 10, y_set + 20, f"${R.SETTLEMENT:.1f}M", 16, RED)
    # the gap, as a measured span on the settlement row
    gx0, gx1, gy = top(R.SETTLEMENT) + 78, top(R.BUYOUT), y_set + BH / 2
    s.line(gx0, gy, gx1, gy, FAINT, 1.5)
    for gx in (gx0, gx1):
        s.line(gx, gy - 7, gx, gy + 7, FAINT, 1.5)
    s.text((gx0 + gx1) / 2, gy - 9, f"${GAP:.1f}M less, calculated", 14, MUTED, anchor="middle")
    x_axis(s, top, y_ax, range(0, 51, 10), X0, X1)

    # ---- zoom guides from the top axis ($0 and $20M) to the bottom panel's ends
    y_zoom = 340
    s.line(top(0), y_ax + 30, X0, y_zoom, GRID, 1.5, dash="3 4")
    s.line(top(20), y_ax + 30, X1, y_zoom, GRID, 1.5, dash="3 4")

    # ---- bottom panel: $0 to $20M
    bot = lambda v: X0 + (X1 - X0) * v / 20
    col_head(s, 48, y_zoom + 26, "THE CLAUSE ALONE, FIRST $20M")
    y_whole, y_yby, y_ax2 = 388, 454, 520
    xset = bot(R.SETTLEMENT)

    s.text(X0 - 16, y_whole + 13, "One offset against", 15, NAVY, anchor="end")
    s.text(X0 - 16, y_whole + 31, "the whole term", 15, NAVY, anchor="end")
    s.rect(bot(WHOLE_FIRM), y_whole, bot(WHOLE_MAX) - bot(WHOLE_FIRM), BH, "url(#hatch)", stroke=NAVY)
    s.text(xset + 14, y_whole + 13, f"at most ${WHOLE_MAX:.1f}M, all of it 2031", 14, NAVY)
    s.text(xset + 14, y_whole + 31, "about $0 through 2030", 13, MUTED)

    s.text(X0 - 16, y_yby + 13, "Year by year", 15, NAVY, anchor="end")
    s.text(X0 - 16, y_yby + 31, "late 2025 through 2030, then 2031", 12, MUTED, anchor="end")
    s.rect(X0, y_yby, bot(YBY_FIRM) - X0, BH, NAVY)
    s.rect(bot(YBY_FIRM) + 2, y_yby, bot(YBY_MAX) - bot(YBY_FIRM) - 2, BH, "url(#hatch)", stroke=NAVY)
    s.text(X0 + 12, y_yby + 20, f"${YBY_FIRM:.1f}M through 2030", 14, PAPER)
    s.text(bot(YBY_MAX) + 10, y_yby + 20, f"at most ${YBY_MAX:.1f}M", 14, NAVY)

    # the settlement, one red line through both readings
    s.line(xset, y_whole - 22, xset, y_ax2, PAPER, 5)
    s.line(xset, y_whole - 22, xset, y_ax2, RED, 2.5)
    s.text(xset, y_whole - 30, f"Settlement, ${R.SETTLEMENT:.1f}M", 14, RED, anchor="middle")
    x_axis(s, bot, y_ax2, range(0, 21, 5), X0, X1)

    s.text(48, H - 32, "Source: Front Office Sports (clause, October 13, 2025; buyout, November 17, 2025), WSLS "
                       "(Virginia Tech terms, November 21, 2025), CBS Sports (settlement, November 17, 2025).",
           12, MUTED)
    s.text(48, H - 14, "Both readings calculated from the published salary schedules. Nothing published says "
                       "which one the two sides used.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 03: the coaching change against the roster
# --------------------------------------------------------------------------

def fig_against_roster(stem):
    title = "As reported, a year and a half of roster. As paid, under a third of one."
    sub1 = "Penn State football, four amounts on one scale. The roster budget is an estimate, so it's drawn as a range."
    sub2 = (f"The reported buyout is {R.BUYOUT / HI:.2f} to {R.BUYOUT / LO:.2f} years of the roster estimate; "
            f"the settlement is {R.SETTLEMENT / HI:.0%} to {R.SETTLEMENT / LO:.0%} of one year.")
    X0, X1 = 300, 1010
    BH, PITCH, Y0 = 30, 70, 160
    xs = lambda v: X0 + (X1 - X0) * v / 50
    y_ax = Y0 + PITCH * 4 - 10
    H = y_ax + 104
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    def label(row, main, sub):
        y = Y0 + PITCH * row
        s.text(X0 - 16, y + 13, main, 15, NAVY, anchor="end")
        s.text(X0 - 16, y + 31, sub, 12, MUTED, anchor="end")
        return y

    y = label(0, "Buyout as reported", "Front Office Sports")
    s.rect(X0, y, xs(R.BUYOUT) - X0, BH, NAVY)
    s.text(xs(R.BUYOUT) + 10, y + 20, f"${R.BUYOUT}M", 16, NAVY)

    y = label(1, "2026 roster budget", "The Athletic's estimate")
    s.rect(X0, y, xs(LO) - X0, BH, PALE)
    s.rect(xs(LO), y, xs(HI) - xs(LO), BH, FAINT)
    for cap in (LO, HI):
        s.line(xs(cap), y - 4, xs(cap), y + BH + 4, NAVY, 2)
    s.text(xs(HI) + 10, y + 20, f"${LO:.0f}M to ${HI:.0f}M", 16, NAVY)

    y = label(2, "Cash out for the change", "calculated")
    s.rect(X0, y, xs(R.SETTLEMENT) - X0, BH, RED)
    s.rect(xs(R.SETTLEMENT) + 2, y, xs(CASH_OUT) - xs(R.SETTLEMENT) - 2, BH, NAVY)
    s.text(xs(CASH_OUT) + 10, y + 20, f"${CASH_OUT:.1f}M", 16, NAVY)
    s.text(xs(CASH_OUT) + 78, y + 20, f"settlement ${R.SETTLEMENT:.1f}M + Iowa State ${R.ISU_BUYOUT:.1f}M", 13, MUTED)

    y = label(3, "Campbell's 2026 pay", "calculated")
    s.rect(X0, y, xs(CAMPBELL_G) - X0, BH, NAVY)
    s.rect(xs(CAMPBELL_G) + 2, y, xs(CAMPBELL_G + CAMPBELL_R) - xs(CAMPBELL_G) - 2, BH, FAINT)
    s.text(xs(CAMPBELL_G + CAMPBELL_R) + 10, y + 20, f"${CAMPBELL_G + CAMPBELL_R:.1f}M", 16, NAVY)
    s.text(xs(CAMPBELL_G + CAMPBELL_R) + 68, y + 20,
           f"guaranteed ${CAMPBELL_G:.1f}M + retention ${CAMPBELL_R:.1f}M", 13, MUTED)

    x_axis(s, xs, y_ax, range(0, 51, 10), X0, X1)

    s.text(48, H - 32, "Source: Front Office Sports (buyout), CBS Sports (settlement), WPSU and StateCollege.com "
                       "(Campbell, Iowa State), The Athletic (roster estimate, September 16, 2026).", 12, MUTED)
    s.text(48, H - 14, "Totals and ratios calculated. Campbell's 2026 figure assumes the retention bonus pays "
                       "for 2026; no payment date is published.", 12, MUTED)
    s.write(stem)


fig_buyout_schedule(KEYS[0])
fig_two_readings(KEYS[1])
fig_against_roster(KEYS[2])
print("done ->", OUT)
