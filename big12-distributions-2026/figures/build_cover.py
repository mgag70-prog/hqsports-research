#!/usr/bin/env python3
"""Substack cover for big12-distributions-2026. 1200x630 on navy.

Adapts fig-03 (five seasons of full-share spreads, common origin, 2024-25 in
red) with the ACC in place of the Big Ten, so the chart names the same two
conferences as the headline. Two panels on one scale, ACC on the left and
Big 12 on the right, in the headline's order.
Red is 2024-25, the first twelve-team playoff, for both conferences.

Concepts B (butterfly) and C (fig-03's ten grouped rows) were mocked up and
not chosen; C's conference labels were unreadable at X card size.

Every spread is recomputed from the published CSV and asserted against the
draft's Big 12 spread table and its ACC sentence before rendering.

Font rendering (checked 2026-09-24): rsvg-convert ignores the base64-embedded
Libre Caslon Text in FONT_STYLE and falls back to Georgia. A test string
rendered with the @font-face block and with it removed came out pixel-identical,
and both matched a plain Georgia render. Headless Chrome honors the embedded
font. So every SVG here shows Caslon in a browser while its PNG shows Georgia.
Across the published pieces, the PNGs for big-ten-spending-2026,
acc-distributions-2026, payouts-vs-rosters-2026 and this piece are
pixel-identical to a fresh rsvg render (Georgia). The five PNGs in
cfb-roster-budgets-2026 are pixel-identical to a headless Chrome render
(Caslon) and have no committed build script. Georgia is kept for now for
consistency; the fix is to re-render the back catalogue through headless Chrome.

The batch re-render targets Libre Caslon, not Georgia. Piece 1
(cfb-roster-budgets-2026) is already correct. Pieces 2 through 5
(big-ten-spending-2026, acc-distributions-2026, payouts-vs-rosters-2026, and
big12-distributions-2026) are the ones that drifted and get re-rendered.
Roster budgets needs a build script written for it, since it has none.

Usage: build_cover.py [out_dir] [--previews]
  out_dir defaults to this script's directory. --previews also writes the
  600px feed and 506px X-card downsamples.
"""
import csv
import io
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
DRAFT = REPO / "big12-distributions-2026/draft.md"
REF_SVG = REPO / "payouts-vs-rosters-2026/figures/cover-a-navy.svg"
CSV_URL = "https://www.gridironhq.ai/data/cfb-conference-distributions.csv"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
PREVIEWS = "--previews" in sys.argv
OUT.mkdir(parents=True, exist_ok=True)

NAVY, RED, OFFWHITE = "#16284A", "#D4553D", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

HEADLINE = "The ACC started paying its schools for winning. The Big 12 just stopped."
# Line breaks only; no words changed. Asserted below.
LINES = ["The ACC started paying its schools for winning.",
         "The Big 12 just stopped."]
assert " ".join(LINES) == HEADLINE
assert DRAFT.read_text().splitlines()[0] == f"# {HEADLINE}"

SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
BREAK = "2024-25"
CONFS = ["Big 12", "ACC"]
SOURCE = ("Source: Big 12 and ACC Form 990 filings, fiscal years ending June 30, 2021 through June 30, 2025, "
          "Schedule A, Part I, via ProPublica. Spreads calculated.")
CAPTION = ("Top-to-bottom spread among each conference's full-share schools, by fiscal year, one scale. "
           "2024-25 in red: the first twelve-team playoff.")

# ---------------------------------------------------------------- data

with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
    csv_text = resp.read().decode("utf-8")
print("downloaded", CSV_URL)

full = {}
with io.StringIO(csv_text) as fh:
    for r in csv.DictReader(fh):
        if r["measure"] != "distribution" or r["share_type"] != "full" or r["conference"] not in CONFS:
            continue
        # Notre Dame is a non-football member; Part 3 counts the ACC's football members only.
        if r["school"] == "Notre Dame":
            continue
        full.setdefault(r["conference"], {}).setdefault(r["season"], {})[r["school"]] = int(r["amount"])

spreads = {c: {s: max(full[c][s].values()) - min(full[c][s].values()) for s in SEASONS} for c in CONFS}
counts = {c: {s: len(full[c][s]) for s in SEASONS} for c in CONFS}
assert all(counts["ACC"][s] == 14 for s in SEASONS)
assert [counts["Big 12"][s] for s in SEASONS] == [10, 10, 10, 10, 12]


def money(n):
    return f"${n:,}"


# Assert against the draft: the Big 12 spread table, and the ACC sentence (twice in the draft).
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
t_sp12 = tables[1]
assert t_sp12[0] == ["Season", "Schools", "Spread", "Top"], t_sp12[0]
for cells, s in zip(t_sp12[1:], SEASONS):
    assert cells[:3] == [s, str(counts["Big 12"][s]), money(spreads["Big 12"][s])], (cells, s)
acc_band = max(spreads["ACC"][s] for s in SEASONS[:4])
acc_sentence = f"from four years inside {money(acc_band)} to {money(spreads['ACC'][BREAK])}"
assert DRAFT.read_text().count(acc_sentence) == 2, acc_sentence
assert "The ACC introduced its success initiative in 2024-25" in DRAFT.read_text()
print("cover data matches the draft's Big 12 spread table and both ACC spread sentences")
for c in CONFS:
    print(" ", c, [money(spreads[c][s]) for s in SEASONS])

# ---------------------------------------------------------------- svg


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self):
        self.ink = OFFWHITE
        self.muted = "rgba(242,238,230,0.62)"
        self.grid = "rgba(242,238,230,0.16)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(HEADLINE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, rx=None):
        extra = f' rx="{rx}"' if rx else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def frame(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)
        for i, line in enumerate(LINES):
            self.text(56, 104 + i * 45, line, 40)
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


VMAX = 13_000_000  # same ceiling as the ACC cover; the widest bar is the ACC's $12.3M


def color(c, s):
    return RED if s == BREAK else c.ink


# ---------------------------------------------------------------- A: two panels


def concept_a():
    c = Cover()
    c.frame()
    panels = {"ACC": 196, "Big 12": 676}   # headline order: ACC first
    assert HEADLINE.index("ACC") < HEADLINE.index("Big 12")
    span = 300
    xv = lambda x0, v: x0 + v / VMAX * span
    y0, pitch, bar_h = 290, 56, 20
    for conf, x0 in panels.items():
        c.text(x0, 238, conf.upper(), 17, c.ink, spacing=2.4)
        c.rect(x0, 252, 1, y0 + 4 * pitch + 22 - 252, c.grid)
    for i, s in enumerate(SEASONS):
        y = y0 + i * pitch
        c.text(56, y + 8, s, 22, color(c, s))
        for conf, x0 in panels.items():
            v = spreads[conf][s]
            c.rect(x0, y - bar_h / 2, xv(x0, v) - x0, bar_h, color(c, s), rx=4)
            c.text(xv(x0, v) + 12, y + 7, money(v), 20, color(c, s))
    c.write("cover-a-navy")


concept_a()
print("done ->", OUT)
