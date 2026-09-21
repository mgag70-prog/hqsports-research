#!/usr/bin/env python3
"""Cover concepts for acc-distributions-2026. 1200x630 on navy.

Concept A adapts fig-02: five spread bars from a common origin, four off-white
and one red, fiscal years and printed spreads only.
Concept B adapts fig-03: three bars stepping down into the four-year band.

Every spread is recomputed from the published CSV (downloaded at run time if no
repo copy exists) and asserted against the draft's section 2 and section 3
tables before rendering.

Usage: build_cover.py [out_dir] [--final]
  --final renders concept A only and skips the feed and X previews.
"""
import csv
import io
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
CSV = REPO / "cfb-conference-distributions/cfb-conference-distributions.csv"
CSV_URL = "https://www.gridironhq.ai/data/cfb-conference-distributions.csv"
DRAFT = REPO / "acc-distributions-2026/draft.md"
REF_SVG = REPO / "cfb-roster-budgets-2026/figures/fig-02-top-eleven.svg"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv

NAVY, RED, PAPER, OFFWHITE = "#16284A", "#D4553D", "#F7F5F0", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

HEADLINE = ("The ACC paid its schools within $3.6 million of each other for four years. "
            "Then it started paying them for winning.")
# Line breaks only; no words changed. Asserted below.
LINES = ["The ACC paid its schools within $3.6 million",
         "of each other for four years. Then it started",
         "paying them for winning."]
assert " ".join(LINES) == HEADLINE
assert DRAFT.read_text().splitlines()[0] == f"# {HEADLINE}"

SOURCE_A = ("Source: ACC Form 990 filings, fiscal years ending June 30, 2021 through June 30, 2025, "
            "Schedule A, Part I, via ProPublica. Spreads calculated.")
SOURCE_B = ("Source: ACC Form 990, fiscal year ending June 30, 2025, via ProPublica; success-initiative schedule "
            "reconstructed by WRAL, August 17, 2025. Remainders and spreads calculated.")

# ---------------------------------------------------------------- data

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
assert sorted(full) == SEASONS and all(len(full[s]) == 14 for s in SEASONS)

SUCCESS = {
    "Clemson": 7_950_000, "Duke": 3_790_000, "Syracuse": 3_600_000, "Miami": 3_600_000,
    "North Carolina": 2_680_000, "Louisville": 2_270_000, "NC State": 1_980_000,
    "Georgia Tech": 1_860_000, "Pittsburgh": 1_800_000, "Boston College": 1_800_000,
    "Virginia Tech": 1_800_000, "Florida State": 120_000, "Wake Forest": 0, "Virginia": 0,
}
CLEMSON_TRAVEL = 3_000_000


def money(n):
    return f"${n:,}"


def spread(d):
    return max(d.values()) - min(d.values())


spreads = {s: spread(full[s]) for s in SEASONS}
band_lo = min(spreads[s] for s in SEASONS[:4])
band_hi = max(spreads[s] for s in SEASONS[:4])
d25 = full["2024-25"]
step1 = {k: d25[k] - SUCCESS[k] for k in d25}
step2 = dict(step1)
step2["Clemson"] -= CLEMSON_TRAVEL
steps = [spread(d25), spread(step1), spread(step2)]
assert steps[0] == spreads["2024-25"]
assert steps[0] - steps[1] == SUCCESS["Clemson"] and steps[1] - steps[2] == 1_330_056
assert band_lo <= steps[2] <= band_hi

# Assert against the draft's first two tables.
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
t_spread, t_recon = tables[0], tables[1]
assert t_spread[0] == ["Season", "Schools", "Top", "Bottom", "Spread"]
for cells, s in zip(t_spread[1:], SEASONS):
    assert cells[0] == s and cells[4] == money(spreads[s]), (cells, s, money(spreads[s]))
assert [c[1] for c in t_recon[1:]] == [money(steps[0]), money(steps[1]), money(steps[2]),
                                       f"{money(band_lo)} to {money(band_hi)}"], t_recon
print("cover data matches the draft's section 2 and section 3 tables")


# ---------------------------------------------------------------- svg

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self):
        self.bg, self.ink = NAVY, OFFWHITE
        self.muted = "rgba(242,238,230,0.62)"
        self.grid = "rgba(242,238,230,0.16)"
        self.band = "rgba(242,238,230,0.14)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(HEADLINE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{self.bg}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None, opacity=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None, rx=None):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        if rx:
            extra += f' rx="{rx}"'
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def eyebrow(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)

    def headline(self):
        for i, line in enumerate(LINES):
            self.text(56, 104 + i * 45, line, 40)

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(W), str(svg), "-o", str(png)], check=True)
        if not FINAL:
            for tag, w in (("feed", 600), ("x", 506)):
                subprocess.run(["magick", str(png), "-resize", f"{w}x", str(OUT / f"{stem}-{tag}.png")], check=True)
        print("wrote", stem)


# ---------------------------------------------------------------- concept A: five spread bars

def concept_a():
    c = Cover()
    c.eyebrow()
    c.headline()
    X0, X1 = 200, 1000
    V1 = 13_000_000
    xv = lambda v: X0 + v / V1 * (X1 - X0)
    y0, pitch, bar_h = 276, 58, 20
    for i, s in enumerate(SEASONS):
        y = y0 + i * pitch
        is_break = s == "2024-25"
        color = RED if is_break else c.ink
        c.text(56, y + 8, s, 22)
        c.rect(X0, y - bar_h / 2, xv(spreads[s]) - X0, bar_h, color, rx=4)
        c.text(xv(spreads[s]) + 14, y + 8, money(spreads[s]), 24 if is_break else 22, RED if is_break else c.ink)
    c.text(56, 590, "Top-to-bottom spread among the ACC's fourteen football members, by fiscal year. "
                    "2024-25 is the first year of the success initiative.", 14, c.muted)
    c.text(56, 616, SOURCE_A, 12, c.muted)
    c.write("cover-a-navy")


# ---------------------------------------------------------------- concept B: three bars into the band

def concept_b():
    c = Cover()
    c.eyebrow()
    c.headline()
    X0, X1 = 440, 1060
    V1 = 13_000_000
    xv = lambda v: X0 + v / V1 * (X1 - X0)
    labels = ["As filed, 2024-25", "Success payments removed", "Clemson's travel allowance removed"]
    y0, pitch, bar_h = 300, 86, 20
    y_top, y_bot = y0 - 46, y0 + 2 * pitch + 30
    bx0, bx1 = xv(band_lo), xv(band_hi)
    c.rect(bx0, y_top, bx1 - bx0, y_bot - y_top, c.band)
    c.text((bx0 + bx1) / 2, y_top - 10, "FOUR PRIOR YEARS", 12, c.muted, anchor="middle", spacing=1.8)
    for i, (label, v) in enumerate(zip(labels, steps)):
        y = y0 + i * pitch
        color = RED if i == 0 else c.ink
        c.text(420, y + 7, label, 19, anchor="end")
        c.rect(X0, y - bar_h / 2, xv(v) - X0, bar_h, color, rx=4)
        c.text(xv(v) + 14, y + 8, money(v), 24 if i == 0 else 22, color)
    c.text(56, 590, "The 2024-25 spread, as filed and after two subtractions, against the band of "
                    f"{money(band_lo)} to {money(band_hi)} the four prior years occupied.", 14, c.muted)
    c.text(56, 616, SOURCE_B, 12, c.muted)
    c.write("cover-b-navy")


concept_a()
if not FINAL:
    concept_b()
print("done ->", OUT)
