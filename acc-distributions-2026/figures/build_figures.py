#!/usr/bin/env python3
"""Build the three in-article charts for acc-distributions-2026.

Every number is recomputed from the published distributions CSV plus WRAL's
August 17, 2025 success-initiative schedule, and asserted against the three
markdown tables in draft.md before any SVG is written.

The CSV is the one published with Parts 1 and 2 at
https://www.gridironhq.ai/data/cfb-conference-distributions.csv. If a copy isn't
checked in at cfb-conference-distributions/, the script downloads it at run time.

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to the directory this script lives in; --final skips the 700px previews.
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
CSV = REPO / "cfb-conference-distributions/cfb-conference-distributions.csv"
DRAFT = REPO / "acc-distributions-2026/draft.md"
REF_SVG = REPO / "cfb-roster-budgets-2026/figures/fig-02-top-eleven.svg"
CSV_URL = "https://www.gridironhq.ai/data/cfb-conference-distributions.csv"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv

NAVY = "#16284A"
RED = "#D4553D"
PAPER = "#F7F5F0"
OFFWHITE = "#F2EEE6"
MUTED = "rgba(22,40,74,0.62)"
GRID = "rgba(22,40,74,0.13)"
BAND = "rgba(22,40,74,0.09)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

SOURCE_990 = ("Source: ACC Form 990 filings, fiscal years ending June 30, 2021 through June 30, 2025, Schedule A, Part I, "
              "via ProPublica. Spreads calculated.")
SOURCE_990_YOY = "Source: ACC Form 990, fiscal years ending June 30, 2024 and June 30, 2025, Schedule A, Part I, via ProPublica. Changes and median calculated."
SOURCE_990_WRAL = ("Source: ACC Form 990, fiscal year ending June 30, 2025, via ProPublica; success-initiative schedule "
                   "reconstructed by WRAL, August 17, 2025. Remainders and spreads calculated.")

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

if CSV.exists():
    csv_text = CSV.read_text()
else:
    with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
        csv_text = resp.read().decode("utf-8")
    print("downloaded", CSV_URL)

full = {}
with io.StringIO(csv_text) as fh:
    for r in csv.DictReader(fh):
        if r["conference"] == "ACC" and r["share_type"] == "full" and r["school"] != "Notre Dame":
            full.setdefault(r["season"], {})[r["school"]] = int(r["amount"])
SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
assert list(sorted(full)) == SEASONS
for s in SEASONS:
    assert len(full[s]) == 14, (s, len(full[s]))

# WRAL, August 17, 2025: first-year success-initiative payments, full-share schools.
SUCCESS = {
    "Clemson": 7_950_000, "Duke": 3_790_000, "Syracuse": 3_600_000, "Miami": 3_600_000,
    "North Carolina": 2_680_000, "Louisville": 2_270_000, "NC State": 1_980_000,
    "Georgia Tech": 1_860_000, "Pittsburgh": 1_800_000, "Boston College": 1_800_000,
    "Virginia Tech": 1_800_000, "Florida State": 120_000, "Wake Forest": 0, "Virginia": 0,
}
CLEMSON_TRAVEL = 3_000_000
assert set(SUCCESS) == set(full["2024-25"])


def money(n):
    return f"-${-n:,}" if n < 0 else f"${n:,}"


def signed(n):
    return f"+${n:,}" if n >= 0 else f"-${-n:,}"


def spread_row(d):
    top = max(d, key=d.get)
    bot = min(d, key=d.get)
    return {"top": top, "top_v": d[top], "bot": bot, "bot_v": d[bot], "spread": d[top] - d[bot]}


spreads = {s: spread_row(full[s]) for s in SEASONS}
band_lo = min(spreads[s]["spread"] for s in SEASONS[:4])
band_hi = max(spreads[s]["spread"] for s in SEASONS[:4])

d25 = full["2024-25"]
step1 = {k: d25[k] - SUCCESS[k] for k in d25}
step2 = dict(step1)
step2["Clemson"] -= CLEMSON_TRAVEL
steps = [spread_row(d25), spread_row(step1), spread_row(step2)]
drop1 = steps[0]["spread"] - steps[1]["spread"]
drop2 = steps[1]["spread"] - steps[2]["spread"]
assert drop1 == SUCCESS["Clemson"], drop1
assert steps[0]["top"] == steps[1]["top"] == "Clemson" and steps[0]["bot"] == steps[1]["bot"] == "Wake Forest"
assert SUCCESS["Wake Forest"] == 0
assert steps[2]["top"] == "Syracuse" and steps[2]["bot"] == "Wake Forest"
assert drop2 == 1_330_056, drop2
assert band_lo <= steps[2]["spread"] <= band_hi

d24 = full["2023-24"]
yoy = sorted(({"school": k, "prev": d24[k], "cur": d25[k], "chg": d25[k] - d24[k]} for k in d25),
             key=lambda r: -r["chg"])
median_chg = int(st.median(r["chg"] for r in yoy))
assert median_chg == 2_099_651

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
assert len(T) == 3, f"expected 3 tables in draft, found {len(T)}"
t_spread, t_recon, t_yoy = T
assert t_spread[0] == ["Season", "Schools", "Top", "Bottom", "Spread"], t_spread[0]
assert t_recon[0] == ["Step", "Top-to-bottom spread"], t_recon[0]
assert t_yoy[0] == ["School", "2023-24", "2024-25", "Change"], t_yoy[0]

for cells, s in zip(t_spread[1:], SEASONS):
    r = spreads[s]
    want = [s, "14", money(r["top_v"]), money(r["bot_v"]), money(r["spread"])]
    assert cells == want, f"spread table mismatch: draft {cells} vs computed {want}"
assert len(t_spread) == 6

want_recon = [
    ["As filed, 2024-25", money(steps[0]["spread"])],
    ["Minus itemized success payments", money(steps[1]["spread"])],
    [f"Also minus Clemson's {money(CLEMSON_TRAVEL)} playoff travel allowance", money(steps[2]["spread"])],
    ["For reference, 2020-21 through 2023-24", f"{money(band_lo)} to {money(band_hi)}"],
]
assert t_recon[1:] == want_recon, f"reconciliation table mismatch: {t_recon[1:]} vs {want_recon}"

assert len(t_yoy) == 15
for cells, r in zip(t_yoy[1:], yoy):
    want = [r["school"], money(r["prev"]), money(r["cur"]), signed(r["chg"])]
    assert cells == want, f"yoy table mismatch: draft {cells} vs computed {want}"

draft_text = DRAFT.read_text()
for phrase in (f"Median change: {signed(median_chg)}.",
               f"Clemson's remainder still sits {money(step1['Clemson'] - st.median(v for k, v in step1.items() if k != 'Clemson'))} above the median",
               "Syracuse is on top of the adjusted table and Wake Forest is on the bottom"):
    assert phrase in draft_text, f"draft no longer says: {phrase}"
print("draft tables match recomputation: 5 + 4 + 14 rows; drops", money(drop1), money(drop2))

# --------------------------------------------------------------------------
# SVG helpers
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

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, opacity=None, style=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if style:
            extra += f' font-style="{style}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None, rx=None):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        if rx:
            extra += f' rx="{rx}"'
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
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


def header(s, title, subtitle):
    s.text(48, 46, title, 28)
    s.text(48, 76, subtitle, 17, MUTED)


def col_head(s, x, y, label, anchor="start"):
    s.text(x, y, label, 12, MUTED, anchor=anchor, spacing=1.8)


def m_label(v):
    """$35M style tick label."""
    return f"${v / 1_000_000:.0f}M"


# --------------------------------------------------------------------------
# fig-02: five-year spread as floating range bars on a dollar axis
# --------------------------------------------------------------------------

def spread_chart(stem):
    title = "Four flat years, then one policy change"
    subtitle = ("Top-to-bottom spread among the ACC's fourteen football members, by fiscal year. "
                "2024-25 is the first year of the success initiative.")
    X0, X1 = 330, 940
    V0, V1 = 34_000_000, 56_000_000
    xv = lambda v: X0 + (v - V0) / (V1 - V0) * (X1 - X0)
    RH, Y0 = 74, 160
    n = len(SEASONS)
    y_last = Y0 + (n - 1) * RH
    y_axis_lbl = y_last + 56
    H = y_axis_lbl + 62
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 108, "FISCAL YEAR")
    col_head(s, X0, 108, "LOWEST TO HIGHEST FULL-SHARE DISTRIBUTION")
    col_head(s, 1152, 108, "SPREAD", anchor="end")
    for t in range(35_000_000, 56_000_000, 5_000_000):
        s.rect(xv(t) - 0.5, 124, 1, y_last + 30 - 124, GRID)
        s.text(xv(t), y_axis_lbl, m_label(t), 13, MUTED, anchor="middle")
    for i, season in enumerate(SEASONS):
        r = spreads[season]
        y = Y0 + i * RH
        is_break = season == "2024-25"
        color = RED if is_break else NAVY
        s.text(48, y + 7, season, 21)
        xa, xb = xv(r["bot_v"]), xv(r["top_v"])
        s.rect(xa, y - 6, xb - xa, 12, color, rx=4)
        # bottom school, left of the bar
        s.text(xa - 12, y + 1, r["bot"], 16, anchor="end")
        s.text(xa - 12, y + 19, money(r["bot_v"]), 12, MUTED, anchor="end")
        # top school, right of the bar
        s.text(xb + 12, y + 1, r["top"], 16)
        s.text(xb + 12, y + 19, money(r["top_v"]), 12, MUTED)
        s.text(1152, y + 7, money(r["spread"]), 21 if is_break else 19, color if is_break else NAVY, anchor="end")
        if i:
            s.rect(48, y - RH / 2, 1104, 1, GRID)
    s.text(48, H - 14, SOURCE_990, 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# fig-03: reconciliation as a step-down onto the four-year band
# --------------------------------------------------------------------------

def recon_chart(stem):
    title = "Take the success payments out and the spread steps back into its band"
    subtitle = "The 2024-25 top-to-bottom spread, as filed and after two subtractions, against the four prior years."
    X0, X1 = 300, 1060
    V0, V1 = 0, 13_000_000
    xv = lambda v: X0 + (v - V0) / (V1 - V0) * (X1 - X0)
    RH, Y0 = 108, 186
    y_last = Y0 + 2 * RH
    y_axis_lbl = y_last + 78
    H = y_axis_lbl + 44
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 108, "STEP")
    col_head(s, X0, 108, "TOP-TO-BOTTOM SPREAD")
    y_plot_top, y_plot_bot = 124, y_last + 56
    for t in range(0, 13_000_000, 3_000_000):
        s.rect(xv(t) - 0.5, y_plot_top, 1, y_plot_bot - y_plot_top, GRID)
        s.text(xv(t), y_axis_lbl, m_label(t) if t else "$0", 13, MUTED, anchor="middle")
    # the band
    bx0, bx1 = xv(band_lo), xv(band_hi)
    s.rect(bx0, y_plot_top, bx1 - bx0, y_plot_bot - y_plot_top, BAND)
    s.text((bx0 + bx1) / 2, y_plot_top + 16, "FOUR PRIOR YEARS", 12, MUTED, anchor="middle", spacing=1.8)
    s.text((bx0 + bx1) / 2, y_plot_top + 34, f"{money(band_lo)} to {money(band_hi)}", 12, MUTED, anchor="middle")

    rows = [
        ("As filed, 2024-25",
         [f"{steps[0]['top']} on top, {steps[0]['bot']} on the bottom."],
         RED),
        ("Each school's itemized success payment removed",
         [f"Spread falls by {money(drop1)}, Clemson's own payment. Clemson stays on top; Wake Forest, at the bottom, received nothing."],
         NAVY),
        (f"Clemson's {money(CLEMSON_TRAVEL)} travel allowance removed",
         [f"Spread falls by {money(drop2)} because Syracuse becomes the top school. Inference from reconciliation: the filing discloses no travel line."],
         NAVY),
    ]
    for i, (label, notes, color) in enumerate(rows):
        y = Y0 + i * RH
        r = steps[i]
        s.text(48, y - 22, label, 19)
        xa, xb = xv(0), xv(r["spread"])
        s.rect(xa, y - 7, xb - xa, 14, color, rx=4)
        s.text(xb + 12, y + 7, money(r["spread"]), 21 if i == 0 else 19, color if i == 0 else NAVY)
        for j, note in enumerate(notes):
            s.text(48, y + 34 + j * 18, note, 13, MUTED)
        if i:
            s.rect(48, y - RH / 2 - 6, 1104, 1, GRID)
    s.text(48, H - 14, SOURCE_990_WRAL, 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# fig-05: year over year, diverging bars from a zero line
# --------------------------------------------------------------------------

def yoy_chart(stem):
    title = "Three schools got less in a record year"
    subtitle = "Change in distribution from 2023-24 to 2024-25, fourteen full-share schools, ordered by change."
    V0, V1 = -3_000_000, 10_000_000
    X0, X1 = 380, 800
    xv = lambda v: X0 + (v - V0) / (V1 - V0) * (X1 - X0)
    xz = xv(0)
    RH, Y0 = 40, 158
    n = len(yoy)
    y_last = Y0 + (n - 1) * RH
    y_axis_lbl = y_last + 48
    H = y_axis_lbl + 62
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 108, "SCHOOL")
    col_head(s, xz, 108, "CHANGE, 2023-24 TO 2024-25", anchor="middle")
    col_head(s, 1032, 108, "2023-24", anchor="end")
    col_head(s, 1152, 108, "2024-25", anchor="end")
    y_plot_top, y_plot_bot = 124, y_last + 26
    for t in range(-2_000_000, 10_000_001, 2_000_000):
        if t == 0:
            continue
        s.rect(xv(t) - 0.5, y_plot_top, 1, y_plot_bot - y_plot_top, GRID)
        lbl = f"{'-' if t < 0 else '+'}${abs(t) // 1_000_000}M"
        s.text(xv(t), y_axis_lbl, lbl, 13, MUTED, anchor="middle")
    s.rect(xz - 0.75, y_plot_top, 1.5, y_plot_bot - y_plot_top, NAVY, opacity=0.55)
    s.text(xz, y_axis_lbl, "0", 13, MUTED, anchor="middle")
    xm = xv(median_chg)
    s.line(xm, y_plot_top, xm, y_plot_bot, NAVY, 1.5, dash="4 5", opacity=0.5)
    s.text(xm + 8, y_plot_top + 12, f"median {signed(median_chg)}", 12, MUTED)
    for i, r in enumerate(yoy):
        y = Y0 + i * RH
        neg = r["chg"] < 0
        color = RED if neg else NAVY
        s.text(48, y + 7, r["school"], 20, color)
        xa, xb = sorted((xz, xv(r["chg"])))
        s.rect(xa, y - 6, xb - xa, 12, color, rx=4)
        if neg:
            s.text(xa - 10, y + 6, signed(r["chg"]), 16, color, anchor="end")
        else:
            s.text(xb + 10, y + 6, signed(r["chg"]), 16, NAVY)
        s.text(1032, y + 6, money(r["prev"]), 15, MUTED, anchor="end")
        s.text(1152, y + 6, money(r["cur"]), 15, MUTED, anchor="end")
    s.text(48, H - 14, SOURCE_990_YOY, 12, MUTED)
    s.write(stem)


spread_chart("fig-02-five-year-spread")
recon_chart("fig-03-reconciliation")
yoy_chart("fig-05-year-over-year")
