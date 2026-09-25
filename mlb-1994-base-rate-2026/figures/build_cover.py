#!/usr/bin/env python3
"""Substack cover for mlb-1994-base-rate-2026. 1200x630 on navy.

The recovery count is the image: three stoppages side by side, each with the
number of seasons per-game attendance took to get back above the last full
season before it. 1972 and 1981 in off-white, 1994-95 in red and largest. Under
each number, a sparkline of the same indexed line as fig-02, on one shared
scale, so the widths and depths compare honestly. No headline; the Substack
title carries it.

The three counts are recomputed from the attendance CSV (Baseball Reference,
Major League year-by-year totals, retrieved September 24, 2026) and asserted
against the expected 2, 2, 13 and against the draft's base-rate table before
rendering.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and
falls back to Georgia, to match pieces 2 through 5. This piece joins the later
Caslon batch re-render (see big12-distributions-2026/figures/build_cover.py).

Usage: build_cover.py [out_dir] [--previews] [--no-spark]
  out_dir defaults to this script's directory. --previews also writes the
  600px feed and 506px X-card downsamples. --no-spark drops the sparklines.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
PIECE = REPO / "mlb-1994-base-rate-2026"
DRAFT = PIECE / "draft.md"
DATA = PIECE / "data/mlb-attendance-1970-2026.csv"
REF_SVG = REPO / "payouts-vs-rosters-2026/figures/cover-a-navy.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
PREVIEWS = "--previews" in sys.argv
SPARK = "--no-spark" not in sys.argv

NAVY, RED, OFFWHITE = "#16284A", "#D4553D", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

TITLE = "Baseball's first two strikes recovered in two years. The one over a salary cap took thirteen."
assert DRAFT.read_text().splitlines()[0] == f"# {TITLE}"
EYEBROW = "MLB ATTENDANCE AFTER A STOPPAGE"
CAPTION = ("Seasons until per-game attendance got back above the last full season before each stoppage. "
           "1994-95 is measured from 1993; from the 1994 pace, it's 12.")
SOURCE = "Source: Baseball Reference, Major League year-by-year totals, retrieved September 24, 2026. Indexes calculated."

STOPPAGES = [  # (label, baseline season, season the drop is measured in, expected seasons to recover)
    ("1972", 1971, 1972, 2),
    ("1981", 1980, 1981, 2),
    ("1994-95", 1993, 1995, 13),
]
WORDS = {2: "two", 13: "thirteen"}

# ---------------------------------------------------------------- data

rows = {int(r["year"]): r for r in csv.DictReader(DATA.open())}
pg = {y: int(r["attendance_per_game"]) for y, r in rows.items()}
YEARS = sorted(pg)
assert [y for y in range(1970, 2027) if y not in pg] == [2020]

rec = []
for label, base, drop_yr, expected in STOPPAGES:
    back = next(y for y in YEARS if y > drop_yr and pg[y] > pg[base])
    seasons = back - base
    assert seasons == expected, (label, seasons, expected)
    span = seasons if seasons > 2 else 4   # the short lines run through season 4, as in fig-02
    rec.append({"label": label, "base": base, "drop_yr": drop_yr, "back": back, "seasons": seasons,
                "drop": (pg[drop_yr] / pg[base] - 1) * 100,
                "index": [pg[base + k] / pg[base] * 100 for k in range(span + 1)]})
back_pace = next(y for y in YEARS if y > 1994 and pg[y] > pg[1994])
assert back_pace - 1994 == 12

# against the draft's base-rate table
table = [[c.strip() for c in l.strip().strip("|").split("|")] for l in DRAFT.read_text().splitlines() if l.startswith("|")]
table = [r for r in table if not set("".join(r)) <= set("-")]
assert table[0][3] == "First year above that season", table[0]
for cells, r in zip(table[1:], rec):
    assert cells[2] == f"{r['drop']:.1f}% in {r['drop_yr']}", cells
    assert cells[3] == f"{r['back']}, {WORDS[r['seasons']]} years after {r['base']}", cells
assert f"comes out at twelve years, also to {back_pace}" in DRAFT.read_text()
print("cover counts match the CSV and the draft's base-rate table:", [r["seasons"] for r in rec])

# ---------------------------------------------------------------- svg


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self):
        self.ink = OFFWHITE
        self.muted = "rgba(242,238,230,0.62)"
        self.grid = "rgba(242,238,230,0.22)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(TITLE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke, sw):
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"/>')

    def poly(self, pts, stroke, sw):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                          f'stroke-linejoin="round" stroke-linecap="round"/>')

    def circle(self, cx, cy, r, fill):
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')

    def frame(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)
        self.text(56, 100, EYEBROW, 20, self.muted, spacing=3)
        self.text(56, 590, CAPTION, 14, self.muted)
        self.text(56, 616, SOURCE, 12, self.muted)

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(W), str(svg), "-o", str(png)], check=True)
        for tag, w in (("feed", 600), ("x", 506)) if PREVIEWS else ():
            subprocess.run(["magick", str(png), "-resize", f"{w}x", str(OUT / f"{stem}-{tag}.png")], check=True)
        print("wrote", stem)


# ---------------------------------------------------------------- the cover

c = Cover()
c.frame()
COLS = [56, 336, 616]              # left edge of each column; 1994-95 gets the wide right-hand column
NUM_SIZE = {2: 200, 13: 270}
# Rendered Georgia ink box at those sizes, measured with rsvg-convert: (left bearing, right edge).
# Georgia's figures are old-style, so the 2 sits at x-height and the 3 in 13 descends 49px.
NUM_INK = {2: (10, 103), 13: (17, 252)}
BASE_Y = 380                        # shared baseline for the three numbers
PX_PER_SEASON, IMIN, IMAX = 38, 78, 106
SP_TOP, SP_H = 468, 80              # sparkline band, clear of the 3's descender
ys = lambda v: SP_TOP + SP_H * (IMAX - v) / (IMAX - IMIN)
for r, x0 in zip(rec, COLS):
    col = RED if r["seasons"] > 2 else c.ink
    c.text(x0, 190, r["label"], 30, col)
    left, right = NUM_INK[r["seasons"]]
    c.text(x0 - left, BASE_Y, str(r["seasons"]), NUM_SIZE[r["seasons"]], col)
    c.text(x0 - left + right + 16, BASE_Y, "seasons", 26, col)
    if SPARK:
        pts = [(x0 + k * PX_PER_SEASON, ys(v)) for k, v in enumerate(r["index"])]   # one x scale for all three
        c.line(x0, ys(100), pts[-1][0] + 12, ys(100), c.grid, 1.5)
        c.poly(pts, col, 4)
        c.circle(*pts[r["seasons"]], 7, col)
c.write("cover-a-navy")
print("done ->", OUT)
