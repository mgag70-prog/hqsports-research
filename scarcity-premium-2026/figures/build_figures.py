#!/usr/bin/env python3
"""Build the in-article charts for scarcity-premium-2026.

fig-01-premium-by-deal: the 33 clean sales ranked by premium over Forbes, colored by league.
fig-02-by-league: each sale's premium by league, with the league median and n.
fig-03-by-period: each sale's premium by period, with the period median and n.

Every number comes through model/recompute.py (which fails on any mismatch with the data) and is
asserted against draft.md and captions.md before any SVG is written. Writes SVG and a 1200px PNG.

Usage: build_figures.py [out_dir]
"""
import contextlib
import io
import re
import statistics as st
import subprocess
import sys
from pathlib import Path

PIECE = Path(__file__).resolve().parents[1]
REPO = PIECE.parent
DRAFT, CAPTIONS = PIECE / "draft.md", PIECE / "figures/captions.md"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

NAVY, RED, PAPER = "#16284A", "#D4553D", "#F7F5F0"
SLATE, OCHRE = "#6F83A6", "#B8893B"
MUTED, FAINT, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.40)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-premium-by-deal", "fig-02-by-league", "fig-03-by-period")
LEAGUE_COLOR = {"NHL": RED, "NBA": NAVY, "MLB": OCHRE, "NFL": SLATE}

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.fails
CLEAN = sorted(R.clean, key=lambda x: -x["premium"])
assert len(CLEAN) == 33 and R.above == 28 and R.below == 5 and R.med == 24.0
LEAGUES = [(lg, [x for x in CLEAN if x["league"] == lg]) for lg in ("NHL", "NBA", "MLB", "NFL")]
PERIODS = [(f"{a} to {b}", [x for x in CLEAN if a <= x["year"] <= b]) for a, b in ((2012, 2017), (2018, 2022), (2023, 2026))]
med = lambda xs: round(st.median(x["premium"] for x in xs), 1)
assert [(len(xs), med(xs)) for _, xs in LEAGUES] == [(7, 36.5), (13, 25.0), (7, 16.7), (6, 16.0)]
assert [(len(xs), med(xs)) for _, xs in PERIODS] == [(14, 34.5), (7, 7.1), (12, 20.0)]

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
league_line = ", ".join(f"{lg} {med(xs)}% on {len(xs)}" + (" sales" if i == 0 else "") for i, (lg, xs) in enumerate(LEAGUES))
DRAFT_PHRASES = (
    f"in {R.above} of the {len(CLEAN)} sales", f"The median premium over Forbes is {R.med}%",
    f"The NHL leads at {med(LEAGUES[0][1])}% on 7 sales", f"{med(PERIODS[0][1])}% from 2012 to 2017 on 14 sales, {med(PERIODS[1][1])}% from 2018 to 2022 on 7, and {med(PERIODS[2][1])}% from 2023 to 2026 on 12",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"All {len(CLEAN)} clean control sales", f"The median is {R.med}%; {R.above} sold above Forbes and {R.below} below",
    f"The Padres' {CLEAN[1]['premium']}% includes $200 million of TV money", league_line,
    f"{med(PERIODS[0][1])}% from 2012 to 2017 on 14 sales, {med(PERIODS[1][1])}% from 2018 to 2022 on 7, and {med(PERIODS[2][1])}% from 2023 to 2026 on 12",
)
for p in CAPTION_PHRASES:
    assert p in captions, f"captions.md no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print(f"draft ({len(DRAFT_PHRASES)} phrases) and captions ({len(CAPTION_PHRASES)} phrases) match the model; three slots exist")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill):
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def dot(self, x, y, r, fill):
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" fill-opacity="0.72"/>')

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"; svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(png)], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


def header(s, title, sub):
    s.text(48, 46, title, 28)
    s.text(48, 76, sub, 17, MUTED)


def source(s, H, text):
    s.text(48, H - 14, text, 12, MUTED)


SRC = "Source: reported sale prices; Forbes values in force at announcement, as listed under Sources. Forbes values are estimates."
VMIN, VMAX = -30, 80


def fig_deals(stem):
    title = "Buyers beat the Forbes value in 28 of 33 control sales."
    sub = "Premium over the Forbes value in force at announcement, %, clean sales, 2012 to 2026."
    X0, X1, Y0, PITCH, BH = 300, 1110, 150, 23, 15
    xs = lambda v: X0 + (X1 - X0) * (v - VMIN) / (VMAX - VMIN)
    bottom = Y0 + PITCH * len(CLEAN)
    H = bottom + 76
    s = SVG(1200, H, title)
    header(s, title, sub)
    lx = 48
    for lg, c in LEAGUE_COLOR.items():
        s.rect(lx, 104, 14, 14, c)
        s.text(lx + 20, 116, lg, 13, NAVY)
        lx += 74
    for v in range(VMIN, VMAX + 1, 10):
        s.line(xs(v), Y0 - 8, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"{v:+d}%" if v else "0%", 11, MUTED, anchor="middle")
    s.line(xs(R.med), Y0 - 22, xs(R.med), bottom, RED, 1.5, dash="5,4")
    s.text(xs(R.med) + 6, Y0 - 12, f"MEDIAN +{R.med}%", 12, RED, spacing=1.8)
    for i, x in enumerate(CLEAN):
        y = Y0 + i * PITCH
        p = x["premium"]
        name = x["team"].replace("Los Angeles ", "LA ").replace("Portland Trail Blazers", "Portland Blazers")
        s.text(X0 - 10 if p >= 0 else xs(p) - 10, y + 12, f"{name} {x['year']}", 13, NAVY, anchor="end")
        a, b = sorted((xs(0), xs(p)))
        s.rect(a, y, max(b - a, 1), BH, LEAGUE_COLOR[x["league"]])
        s.text(b + 7 if p >= 0 else xs(0) + 7, y + 12, f"{p:+.1f}%", 12, NAVY)
    s.line(xs(0), Y0 - 8, xs(0), bottom, NAVY, 1.5)
    s.text(48, bottom + 44, f"The Padres' figure includes $200 million of TV money; net of it, +{R.PADRES_NET}%.", 12, MUTED)
    source(s, H, SRC)
    s.write(stem)


def strip(stem, title, sub, groups, color):
    X0, X1, Y0, ROW = 250, 1130, 130, 92
    xs = lambda v: X0 + (X1 - X0) * (v - VMIN) / (VMAX - VMIN)
    bottom = Y0 + ROW * len(groups)
    H = bottom + 62
    s = SVG(1200, H, title)
    header(s, title, sub)
    for v in range(VMIN, VMAX + 1, 10):
        s.line(xs(v), Y0, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"{v:+d}%" if v else "0%", 11, MUTED, anchor="middle")
    s.line(xs(0), Y0, xs(0), bottom, NAVY, 1.5)
    for i, (label, deals) in enumerate(groups):
        y = Y0 + ROW * i + ROW / 2
        m = med(deals)
        s.text(48, y - 2, label, 18, NAVY)
        s.text(48, y + 18, f"{len(deals)} sales", 13, MUTED)
        order = sorted(deals, key=lambda x: x["premium"])
        last = {}
        for x in order:
            px = xs(x["premium"])
            lane = next(k for k in (0, -1, 1, -2, 2, -3, 3) if px - last.get(k, -99) >= 12)
            last[lane] = px
            s.dot(px, y + lane * 11, 6, color(x))
        s.line(xs(m), y - 36, xs(m), y + 36, RED, 2.5)
        s.text(xs(m) + 6, y - 26, f"{m:+.1f}%", 15, RED)
    source(s, H, SRC)
    s.write(stem)


fig_deals(KEYS[0])
strip(KEYS[1], "The NHL's median premium leads. The samples are small.",
      "Each dot is one clean sale; the red line is the league median. Premium over Forbes, %.", LEAGUES, lambda x: LEAGUE_COLOR[x["league"]])
strip(KEYS[2], "Premiums were highest early, fell, then came back partway.",
      "Each dot is one clean sale; the red line is the period median. Premium over Forbes, %.", PERIODS, lambda x: NAVY)
print("done ->", OUT)
