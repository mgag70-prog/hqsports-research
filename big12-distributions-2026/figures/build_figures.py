#!/usr/bin/env python3
"""Build the three in-article charts for big12-distributions-2026.

Every number is recomputed from the published distributions CSV (Form 990
filings via ProPublica), then asserted against the four markdown tables and the
load-bearing sentences in draft.md before any SVG is written.

The CSV is the one published with Parts 1 through 3 at
https://www.gridironhq.ai/data/cfb-conference-distributions.csv and is
downloaded at run time so the charts always run on the live file.

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to ./drafts next to this script; --final skips the 700px previews.
"""
import csv
import io
import re
import statistics as st
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
DRAFT = REPO / "big12-distributions-2026/draft.md"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
CSV_URL = "https://www.gridironhq.ai/data/cfb-conference-distributions.csv"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path(__file__).parent / "drafts"
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv

NAVY = "#16284A"
RED = "#D4553D"
PAPER = "#F7F5F0"
OFFWHITE = "#F2EEE6"
MUTED = "rgba(22,40,74,0.62)"
GRID = "rgba(22,40,74,0.13)"
BAND = "rgba(22,40,74,0.08)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
BREAK = "2024-25"
TRAVEL = 3_000_000          # announced playoff travel allowance, per game
PRIZE_BID = 4_000_000       # announced prize money for a first-round bid
PRIZE_TITLE_RUN = 20_000_000  # announced prize money for Ohio State's four-game run, before travel
PLAYOFF_GAMES = {"Indiana": 1, "Penn State": 3, "Ohio State": 4}

SRC_990 = "Form 990 filings, fiscal years ending June 30, 2021 through June 30, 2025, Schedule A, Part I, via ProPublica"

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
    dist_text = resp.read().decode("utf-8")
print("downloaded", CSV_URL)

rows = []
with io.StringIO(dist_text) as fh:
    for r in csv.DictReader(fh):
        if r["measure"] == "distribution":
            rows.append({"school": r["school"], "conf": r["conference"], "season": r["season"],
                         "amount": int(r["amount"]), "share": r["share_type"]})


def full(conf, season):
    return sorted([r for r in rows if r["conf"] == conf and r["season"] == season and r["share"] == "full"],
                  key=lambda r: -r["amount"])


def money(n):
    return f"${n:,}"


def signed(n):
    return ("+" if n > 0 else "-") + money(abs(n))


# Big 12, 2024-25: twelve full-share schools, the top two, and the band of ten.
b12 = full("Big 12", BREAK)
assert len(b12) == 12
b12_spread = b12[0]["amount"] - b12[-1]["amount"]
ten = b12[2:]
band_hi, band_lo = ten[0]["amount"], ten[-1]["amount"]
band = band_hi - band_lo
ten_median = st.median(r["amount"] for r in ten)
# The median of ten sits between two values, so the premiums carry a half-dollar; the draft rounds half up.
half_up = lambda x: int(x + 0.5)
prem = {r["school"]: half_up(r["amount"] - ten_median) for r in b12[:2]}
assert set(prem) == {"Arizona State", "Iowa State"}

# Spreads by season, both conferences, with the school on top for the Big 12.
def spreads(conf):
    out = []
    for sea in SEASONS:
        f = full(conf, sea)
        top_amt = f[0]["amount"]
        tops = [r["school"] for r in f if r["amount"] == top_amt]
        out.append({"season": sea, "n": len(f), "spread": top_amt - f[-1]["amount"],
                    "top": " and ".join(tops) + (", tied" if len(tops) > 1 else "")})
    return out


sp12, spbt = spreads("Big 12"), spreads("Big Ten")

# Big Ten, 2024-25: median of the full-share schools that played no playoff game, and the premiums.
bt = full("Big Ten", BREAK)
assert len(bt) == 16
non = [r["amount"] for r in bt if r["school"] not in PLAYOFF_GAMES]
assert len(non) == 13
bt_median = int(st.median(non))
prem_bt = []
for school, games in PLAYOFF_GAMES.items():
    amt = next(r["amount"] for r in bt if r["school"] == school)
    p = amt - bt_median
    prem_bt.append({"school": school, "games": games, "premium": p, "per_game": p / games,
                    "vs_travel": p / games - TRAVEL})
# Per-game figures are rounded to the dollar, as the draft prints them (Penn State's carries a 33-cent remainder).
for p in prem_bt:
    p["per_game"] = half_up(p["per_game"])
    p["vs_travel"] = p["per_game"] - TRAVEL

# --------------------------------------------------------------------------
# Assert against the draft
# --------------------------------------------------------------------------

def draft_tables():
    tables, cur = [], []
    for line in DRAFT.read_text().splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-"):
                continue
            cur.append(cells)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


T = draft_tables()
assert len(T) == 4, f"expected 4 tables in draft, found {len(T)}"
t_twelve, t_sp12, t_spbt, t_prem = T
assert t_twelve[0] == ["School", "2024-25"], t_twelve[0]
assert t_sp12[0] == ["Season", "Schools", "Spread", "Top"], t_sp12[0]
assert t_spbt[0] == ["Season", "Schools", "Spread"], t_spbt[0]
assert t_prem[0] == ["School", "Playoff games", "Premium over median", "Per game"], t_prem[0]

for cells, r in zip(t_twelve[1:], b12):
    want = [r["school"], money(r["amount"])]
    assert cells == want, f"twelve-school table mismatch: draft {cells} vs computed {want}"
assert len(t_twelve) - 1 == 12
for cells, s in zip(t_sp12[1:], sp12):
    want = [s["season"], str(s["n"]), money(s["spread"]), s["top"]]
    assert cells == want, f"Big 12 spread table mismatch: draft {cells} vs computed {want}"
for cells, s in zip(t_spbt[1:], spbt):
    want = [s["season"], str(s["n"]), money(s["spread"])]
    assert cells == want, f"Big Ten spread table mismatch: draft {cells} vs computed {want}"
for cells, p in zip(t_prem[1:], prem_bt):
    want = [p["school"], str(p["games"]), money(p["premium"]), money(p["per_game"])]
    assert cells == want, f"premium table mismatch: draft {cells} vs computed {want}"

draft_text = DRAFT.read_text()
indiana = prem_bt[0]
for phrase in (f"Top to bottom is {money(b12_spread)}",
               f"sit within {money(band)} of each other",
               f"came in {money(prem['Arizona State'])} above the median",
               f"came in {money(prem['Iowa State'])} above",
               f"find their median: {money(bt_median)}",
               f"The gap between those two figures is {money(-indiana['vs_travel'])}",
               f"by {money(prem_bt[1]['vs_travel'])} and {money(prem_bt[2]['vs_travel'])} respectively",
               f"a {money(TRAVEL)} travel allowance per game",
               f"carry {money(PRIZE_BID)} for the bid",
               f"is {money(PRIZE_TITLE_RUN)} before travel"):
    assert phrase in draft_text, f"draft no longer says: {phrase}"
print("draft tables match recomputation: 12 schools, 5 + 5 spreads, 3 premiums; 10 prose figures found")

# --------------------------------------------------------------------------
# SVG helpers (house style, shared with the ACC and payouts figures)
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                          f'viewBox="0 0 {w} {h}" font-family="{FONT}">')
        self.parts.append(f"<title>{esc(title)}</title>{FONT_STYLE}")
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, opacity=None, halo=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if halo:
            extra += f' stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None, rx=None, stroke=None, sw=0):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        if rx:
            extra += f' rx="{rx}"'
        if stroke:
            extra += f' stroke="{stroke}" stroke-width="{sw}"'
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

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
            small = OUT / f"{stem}-700.png"
            subprocess.run(["magick", str(png), "-resize", "700x", str(small)], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


def header(s, title, subtitle, subtitle2=None):
    s.text(48, 46, title, 28)
    s.text(48, 76, subtitle, 17, MUTED)
    if subtitle2:
        s.text(48, 98, subtitle2, 17, MUTED)


def col_head(s, x, y, label, anchor="start", fill=MUTED):
    s.text(x, y, label, 12, fill, anchor=anchor, spacing=1.8)


def axis(s, x0, x1, vmin, vmax, y_top, y_bottom, y_label, step, fmt):
    v = vmin
    while v <= vmax + 1:
        x = x0 + (x1 - x0) * (v - vmin) / (vmax - vmin)
        s.rect(x - 0.5, y_top, 1, y_bottom - y_top, GRID)
        s.text(x, y_label, fmt(v), 13, MUTED, anchor="middle")
        v += step


def m_label(v):
    return f"${v // 1_000_000}M"


# --------------------------------------------------------------------------
# Fig 02: twelve schools, the band of ten, and the two above it
# --------------------------------------------------------------------------

def fig_twelve(stem):
    title = f"Ten schools inside {money(band)}, and two above them"
    subtitle = "The Big 12's twelve full-share distributions for 2024-25, ranked. Zoomed axis: the bars do not start at zero."
    X0, X1, VMIN, VMAX = 330, 800, 36_000_000, 44_000_000
    RH, Y0 = 40, 158
    y_last = Y0 + 11 * RH
    y_axis_lbl = y_last + 42
    H = y_axis_lbl + 26 + 44
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 118, "SCHOOL")
    col_head(s, X0, 118, "FULL-SHARE DISTRIBUTION, $36M TO $44M")
    col_head(s, 1152, 118, "FILED, FORM 990", anchor="end")
    xs = lambda v: X0 + (X1 - X0) * (v - VMIN) / (VMAX - VMIN)
    axis(s, X0, X1, VMIN, VMAX, 130, y_last + 22, y_axis_lbl, 2_000_000, m_label)
    # the band of ten: a shaded block spanning the lowest to the highest of the ten
    s.rect(xs(band_lo), 130, xs(band_hi) - xs(band_lo), y_last + 22 - 130, BAND)
    col_head(s, (xs(band_lo) + xs(band_hi)) / 2, 144, f"TEN SCHOOLS WITHIN {money(band)}", anchor="middle")
    # median of the ten, drawn but not valued: the draft prints the premiums, not the median
    s.line(xs(ten_median), 150, xs(ten_median), y_last + 22, NAVY, 1, dash="4 4")
    s.text(xs(ten_median), y_last + 18, "median of the ten", 11, MUTED, anchor="middle", halo=True)
    for i, r in enumerate(b12):
        y = Y0 + i * RH
        above = r["school"] in prem
        s.text(48, y + 6, r["school"], 20, RED if above else NAVY)
        x = xs(r["amount"])
        s.rect(X0, y - 0.5, x - X0, 1, GRID)
        s.circle(x, y, 7, RED if above else NAVY)
        if above:
            s.text(x + 16, y + 6, f"{signed(prem[r['school']])} over the median of the ten", 15, RED, halo=True)
        s.text(1152, y + 6, money(r["amount"]), 17, RED if above else NAVY, anchor="end")
    s.text(48, H - 14, f"Source: Big 12 Form 990, fiscal year ending June 30, 2025, Schedule A, Part I, via ProPublica. "
                       f"Band, median, and premiums calculated.", 12, MUTED)
    s.write(stem)


fig_twelve("fig-02-twelve-schools")

# --------------------------------------------------------------------------
# Fig 03: five seasons of spreads, both conferences on one axis
# --------------------------------------------------------------------------

def fig_spreads(stem):
    title = "The Big Ten was flatter than the Big 12 ever was, until 2024-25"
    subtitle = "Top-to-bottom spread among full-share schools, by season, drawn from a common origin. 2024-25 in red."
    X0, X1, VMAX = 330, 940, 16_000_000
    GH, Y0 = 92, 166       # group height per season, two bars each
    y_last = Y0 + 4 * GH + 34
    y_axis_lbl = y_last + 40
    H = y_axis_lbl + 26 + 44
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 118, "SEASON")
    col_head(s, X0, 118, "SPREAD, HIGHEST MINUS LOWEST FULL SHARE, $0 TO $16M")
    col_head(s, 1152, 118, "SPREAD", anchor="end")
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    axis(s, X0, X1, 0, VMAX, 130, y_last + 8, y_axis_lbl, 4_000_000, m_label)
    for i, sea in enumerate(SEASONS):
        y = Y0 + i * GH
        if i:
            s.rect(48, y - 30, 1104, 1, GRID)
        brk = sea == BREAK
        s.text(48, y + 12, sea, 24, RED if brk else NAVY)
        for j, (name, sp) in enumerate((("Big Ten", spbt[i]), ("Big 12", sp12[i]))):
            yy = y + j * 30
            col = RED if brk else NAVY
            s.text(X0 - 12, yy + 5, f"{name}, {sp['n']} schools", 13, MUTED, anchor="end")
            w = max(xs(sp["spread"]) - X0, 2)
            s.rect(X0, yy - 5, w, 11, col, rx=2)
            tail = money(sp["spread"])
            if name == "Big 12":
                tail += f"   {sp['top']} on top"
            s.text(X0 + w + 10, yy + 5, tail, 14, col if name == "Big Ten" or brk else NAVY)
            s.text(1152, yy + 5, money(sp["spread"]), 15, col, anchor="end")
    s.text(48, H - 14, f"Source: Big Ten and Big 12 {SRC_990}. Spreads calculated.", 12, MUTED)
    s.write(stem)


fig_spreads("fig-03-two-conference-spreads")

# --------------------------------------------------------------------------
# Fig 04: the correction. Per game against the travel allowance, then totals against prize money.
# --------------------------------------------------------------------------

def fig_correction(stem):
    title = "The Big Ten's playoff premium is a travel allowance, not prize money"
    sub1 = f"Premium over the median of the thirteen Big Ten full-share schools that played no playoff game, {money(bt_median)}."
    sub2 = f"Above: per game, against the {money(TRAVEL)} travel allowance. Below: totals, against what prize money alone would add."
    # Panel A: per game
    AX0, AX1, AVMAX = 330, 860, 4_000_000
    RH, AY0 = 62, 190
    a_last = AY0 + 2 * RH
    a_axis_lbl = a_last + 42
    # Panel B: totals
    BY_HEAD = a_axis_lbl + 58
    BX0, BX1, BVMAX = 330, 940, 20_000_000
    BY0 = BY_HEAD + 46
    b_last = BY0 + 2 * RH
    b_axis_lbl = b_last + 42
    y_legend = b_axis_lbl + 40
    H = y_legend + 24 + 62
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    # ---- Panel A ----
    col_head(s, 48, 140, "SCHOOL")
    col_head(s, AX0, 140, "PREMIUM PER PLAYOFF GAME, $0 TO $4M")
    col_head(s, 955, 140, "PER GAME")
    col_head(s, 1152, 140, "VS TRAVEL", anchor="end")
    xa = lambda v: AX0 + (AX1 - AX0) * v / AVMAX
    axis(s, AX0, AX1, 0, AVMAX, 152, a_last + 22, a_axis_lbl, 1_000_000, m_label)
    xt = xa(TRAVEL)
    s.line(xt, 152, xt, a_last + 22, RED, 2)
    s.text(xt, 166, "TRAVEL ALLOWANCE, $3,000,000 PER GAME", 11, RED, anchor="middle", spacing=1.6, halo=True)
    for i, p in enumerate(prem_bt):
        y = AY0 + i * RH
        s.text(48, y + 3, p["school"], 20)
        s.text(48, y + 21, f"{p['games']} playoff game{'s' if p['games'] > 1 else ''}", 13, MUTED)
        x = xa(p["per_game"])
        s.rect(AX0, y - 5, min(x, xt) - AX0, 11, NAVY, rx=2)
        if x > xt:
            s.rect(xt, y - 5, x - xt, 11, RED, rx=2)
        else:
            # the shortfall: a red gap between the bar and the line
            s.rect(x, y - 8, xt - x, 17, RED, opacity=0.35)
        s.text(955, y + 6, money(p["per_game"]), 17)
        s.text(1152, y + 6, signed(p["vs_travel"]), 17, RED, anchor="end")
    s.text(xt - 6, AY0 + 24, f"{money(-indiana['vs_travel'])} short of the allowance", 13, RED, anchor="end", halo=True)

    # ---- Panel B ----
    s.rect(48, BY_HEAD - 26, 1104, 1, GRID)
    col_head(s, 48, BY_HEAD, "SCHOOL")
    col_head(s, BX0, BY_HEAD, "TOTAL PREMIUM, $0 TO $20M")
    col_head(s, 1152, BY_HEAD, "TOTAL PREMIUM", anchor="end")
    xb = lambda v: BX0 + (BX1 - BX0) * v / BVMAX
    axis(s, BX0, BX1, 0, BVMAX, BY_HEAD + 12, b_last + 22, b_axis_lbl, 5_000_000, m_label)
    prize = {"Indiana": (PRIZE_BID, "prize money for the bid, if passed through"),
             "Ohio State": (PRIZE_TITLE_RUN, "prize money for the title run, before travel, if passed through")}
    for i, p in enumerate(prem_bt):
        y = BY0 + i * RH
        s.text(48, y + 3, p["school"], 20)
        s.text(48, y + 21, f"{p['games']} playoff game{'s' if p['games'] > 1 else ''}", 13, MUTED)
        # travel allowance blocks, one per game, drawn as an outline behind the bar
        for g in range(p["games"]):
            s.rect(xb(g * TRAVEL), y - 9, xb(TRAVEL) - xb(0), 19, OFFWHITE, stroke=GRID, sw=1)
        s.rect(BX0, y - 5, xb(p["premium"]) - BX0, 11, NAVY, rx=2)
        s.text(1152, y + 6, money(p["premium"]), 17, anchor="end")
        if p["school"] in prize:
            v, lab = prize[p["school"]]
            s.circle(xb(v), y, 7, PAPER, stroke=RED, sw=2)
            anchor, dx = ("end", -14) if v >= BVMAX else ("start", 14)
            s.text(xb(v) + dx, y - 12, lab, 12, RED, anchor=anchor, halo=True)
        else:
            s.text(xb(p["premium"]) + 12, y + 5, "no prize figure stated for a three-game run", 12, MUTED, halo=True)
    # legend
    s.rect(48, y_legend - 9, 22, 8, NAVY, rx=2)
    s.text(78, y_legend, "filed premium over the non-playoff median, Form 990, calculated", 13, MUTED)
    s.rect(48, y_legend + 13, 22, 10, OFFWHITE, stroke=GRID, sw=1)
    s.text(78, y_legend + 22, f"one {money(TRAVEL)} travel allowance per game, announced College Football Playoff figure", 13, MUTED)
    s.circle(700, y_legend + 18, 6, PAPER, stroke=RED, sw=2)
    s.text(714, y_legend + 22, "prize money alone, announced CFP figure, if passed through", 13, MUTED)
    s.text(48, H - 32, "Source: Big Ten Form 990, fiscal year ending June 30, 2025, Schedule A, Part I, via ProPublica. "
                       "Travel allowance and prize amounts are announced College Football Playoff figures.", 12, MUTED)
    s.text(48, H - 14, "Median, premiums, and per-game figures calculated; per-game figures rounded to the dollar.", 12, MUTED)
    s.write(stem)


fig_correction("fig-04-correction")
print("done ->", OUT)
