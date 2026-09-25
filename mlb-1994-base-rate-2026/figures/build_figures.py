#!/usr/bin/env python3
"""Build the two in-article charts for mlb-1994-base-rate-2026.

fig-02-recovery replaces the base-rate table: each stoppage indexed to the last
full season before it (1971, 1980, 1993) at 100, against seasons after that
baseline, with the season each line first gets back above 100 marked.
fig-05-long-view is new, for "Where baseball stands going in": per-game
attendance 1970 through 2026, stoppages and expansions marked, 2020 left as a
gap, 2021 as an unconnected hollow point, 2026 as a season in progress.

Every value is recomputed from the attendance CSV (Baseball Reference, Major
League year-by-year totals, retrieved September 24, 2026) and asserted against
the draft's table and prose before any SVG is written.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and
falls back to Georgia, to match pieces 2 through 5. This piece joins the later
Caslon batch re-render (see big12-distributions-2026/figures/build_cover.py).

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to this script's directory; --final skips the 700px previews.
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
GRID = "rgba(22,40,74,0.13)"
RED_TINT = "rgba(212,85,61,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

RETRIEVED = "September 24, 2026"
SRC_BR = f"Baseball Reference, Major League year-by-year totals, retrieved {RETRIEVED}"
AP_GAMES = {1994: 669, 1995: 252}      # AP chronology, regular-season games lost
GAMES_LOST = {1972: 86, 1981: 712, 1994: sum(AP_GAMES.values())}
STOPPAGES = [  # (label, baseline season, season the drop is measured in, games lost)
    ("1972 strike", 1971, 1972, GAMES_LOST[1972]),
    ("1981 strike", 1980, 1981, GAMES_LOST[1981]),
    ("1994-95 strike", 1993, 1995, GAMES_LOST[1994]),
]
WORDS = {2: "two", 12: "twelve", 13: "thirteen"}

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

rows = {int(r["year"]): r for r in csv.DictReader(DATA.open())}
pg = {y: int(r["attendance_per_game"]) for y, r in rows.items()}
teams = {y: int(r["teams"]) for y, r in rows.items()}
for y, r in rows.items():  # the per-game column is total attendance over games, truncated
    assert abs(int(r["total_attendance"]) / int(r["games"]) - pg[y]) < 1, y
YEARS = sorted(pg)
assert YEARS[0] == 1970 and YEARS[-1] == 2026 and 2020 not in pg
assert [y for y in range(1970, 2027) if y not in pg] == [2020]
assert "COVID" in rows[2021]["note"]


def pct(a, b):
    return (a / b - 1) * 100


def first_above(level, after):
    return next(y for y in YEARS if y > after and pg[y] > level)


rec = []
for label, base, drop_yr, games in STOPPAGES:
    back = first_above(pg[base], drop_yr)
    rec.append({"label": label, "base": base, "drop_yr": drop_yr, "games": games,
                "drop": pct(pg[drop_yr], pg[base]), "back": back, "seasons": back - base})
assert [r["seasons"] for r in rec] == [2, 2, 13]
back_pace = first_above(pg[1994], 1994)
assert back_pace == 2006 and back_pace - 1994 == 12

PEAK_YR = max(pg, key=pg.get)
assert PEAK_YR == 2007 and all(pg[y] < pg[PEAK_YR] for y in YEARS if y > PEAK_YR)
gap_pace, gap_peak = pct(pg[2026], pg[1994]), pct(pg[2026], pg[PEAK_YR])
EXPANSIONS = [b for a, b in zip(YEARS, YEARS[1:]) if teams[b] > teams[a]]
assert EXPANSIONS == [1977, 1993, 1998], EXPANSIONS
jump_1993 = pct(pg[1993], pg[1992])

# --------------------------------------------------------------------------
# Assert against the draft
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
table = [[c.strip() for c in l.strip().strip("|").split("|")] for l in draft.splitlines() if l.startswith("|")]
table = [r for r in table if not set("".join(r)) <= set("-")]
assert table[0] == ["Stoppage", "Games lost", "Drop from the last full season before", "First year above that season"], table[0]
for cells, r in zip(table[1:], rec):
    want = [r["label"], str(r["games"]), f"{r['drop']:.1f}% in {r['drop_yr']}",
            f"{r['back']}, {WORDS[r['seasons']]} years after {r['base']}"]
    assert cells == want, f"base-rate table mismatch: draft {cells} vs computed {want}"
assert len(table) == 4

for phrase in (f"counts {GAMES_LOST[1994]}: {AP_GAMES[1994]} regular-season games in 1994 and {AP_GAMES[1995]} in 1995",
               f"{GAMES_LOST[1994]} games by the AP's count, {AP_GAMES[1994]} in 1994 and {AP_GAMES[1995]} in 1995",
               f"comes out at {WORDS[back_pace - 1994]} years, also to {back_pace}",
               f"running at {pg[1994]:,} when the players walked out",
               f"until {rec[2]['back']}, when it reached {pg[rec[2]['back']]:,}",
               f"peaked the next year at {pg[PEAK_YR]:,}",
               f"drawing {pg[2026]:,} per game, which is {-gap_pace:.1f}% below the 1994 pre-strike pace "
               f"and {-gap_peak:.1f}% below the 2007 peak",
               f"from {teams[1992]} teams to {teams[1993]} that year, and per-game attendance jumped "
               f"{jump_1993:.1f}%, from {pg[1992]:,} to {pg[1993]:,}",
               f"from {teams[1997]} teams to {teams[1998]} in 1998"):
    assert phrase in draft, f"draft no longer says: {phrase}"
print("draft matches recomputation: base-rate table (3 rows) and 9 prose figures")

# --------------------------------------------------------------------------
# SVG helpers (house style, shared with the distributions pieces)
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, halo=False, italic=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if halo:
            extra += f' stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if italic:
            extra += ' font-style="italic"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke=None, sw=0, dash=None):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
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


# --------------------------------------------------------------------------
# Fig 02: recovery, indexed to the last full season before each stoppage
# --------------------------------------------------------------------------

def fig_recovery(stem):
    title = "Two strikes were gone in two seasons. The third took thirteen."
    sub1 = "Per-game attendance, each stoppage indexed to the last full season before it. Zoomed axis: it does not start at zero."
    sub2 = (f"1994-95 is indexed to 1993. Against the 1994 pace instead, recovery takes "
            f"{back_pace - 1994} seasons, also to {back_pace}.")
    X0, X1, NMAX = 120, 1000, 13
    Y0, Y1, IMIN, IMAX = 170, 560, 78, 110
    xs = lambda k: X0 + (X1 - X0) * k / NMAX
    ys = lambda v: Y1 - (Y1 - Y0) * (v - IMIN) / (IMAX - IMIN)
    H = Y1 + 110
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 148, "INDEX, LAST FULL SEASON BEFORE THE STOPPAGE = 100")
    for v in range(80, 111, 5):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 14, ys(v) + 5, str(v), 13, MUTED, anchor="end")
    s.line(X0, ys(100), X1 + 20, ys(100), NAVY, 1.5)
    for k in range(NMAX + 1):
        s.text(xs(k), Y1 + 24, str(k), 13, MUTED, anchor="middle")
    col_head(s, X0, Y1 + 52, "SEASONS AFTER THE LAST FULL SEASON BEFORE THE STOPPAGE")

    styles = {1971: (FAINT, 2.5), 1980: (NAVY, 2.5), 1993: (RED, 3.5)}
    for r in rec:
        base = r["base"]
        col, sw = styles[base]
        span = r["seasons"] if base == 1993 else 4
        pts = [(xs(k), ys(pg[base + k] / pg[base] * 100)) for k in range(span + 1)]
        s.poly(pts, col, sw)
        for x, y in pts:
            s.circle(x, y, 4, col)
        r["pts"] = pts

    r72, r81, r94 = rec
    # the 1994-95 drop at its low point; the two small drops ride in the end labels
    x, y = r94["pts"][2]
    s.text(x, y + 26, f"{r94['drop']:.1f}% in 1995", 14, RED, anchor="middle", halo=True)
    x, y = r94["pts"][1]
    s.text(x - 8, y - 14, "1994 pace at the strike", 12, RED, anchor="end", halo=True)
    # the two short lines, labeled at their ends
    for r, col in ((r72, MUTED), (r81, NAVY)):
        x, y = r["pts"][-1]
        s.text(x + 12, y + 5, f"{r['label']}, {r['games']} games lost, {r['drop']:.1f}% in {r['drop_yr']}", 14, col, halo=True)
    s.text(xs(5.15), ys(86.2), f"{r94['label']}, {r94['games']} games lost (AP count)", 15, RED, halo=True)
    # where each line gets back above 100
    x2 = xs(2)
    y2 = min(r72["pts"][2][1], r81["pts"][2][1])
    s.circle(x2, r72["pts"][2][1], 8, "none", stroke=NAVY, sw=1.5)
    s.circle(x2, r81["pts"][2][1], 8, "none", stroke=NAVY, sw=1.5)
    s.text(x2, ys(108.4), f"both back above 100 in 2 seasons: {r72['back']} and {r81['back']}", 13, NAVY,
           anchor="middle", halo=True)
    x13, y13 = r94["pts"][-1]
    s.circle(x13, y13, 9, "none", stroke=RED, sw=2)
    s.text(x13, y13 - 18, f"back above 100 in {r94['seasons']} seasons: {r94['back']}", 13, RED,
           anchor="end", halo=True)
    s.text(48, H - 14, f"Source: {SRC_BR}. Games lost: 1994-95 is the AP's count. Indexes calculated.", 12, MUTED)
    s.write(stem)


fig_recovery("fig-02-recovery")

# --------------------------------------------------------------------------
# Fig 05: the long view, 1970 through 2026
# --------------------------------------------------------------------------

def fig_long_view(stem):
    title = "Attendance peaked in 2007 and hasn't been back."
    sub1 = "MLB per-game attendance by season, 1970 through 2026. Zoomed axis: it does not start at zero."
    X0, X1, YR0, YR1 = 120, 1000, 1970, 2026
    Y0, Y1, VMIN, VMAX = 176, 560, 12_000, 34_000
    xs = lambda yr: X0 + (X1 - X0) * (yr - YR0) / (YR1 - YR0)
    ys = lambda v: Y1 - (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
    step = xs(1) - xs(0)
    H = Y1 + 120
    s = SVG(1200, H, title)
    header(s, title, sub1)
    col_head(s, 48, 120, "ATTENDANCE PER GAME")
    for v in range(12_000, 34_001, 4_000):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 14, ys(v) + 5, f"{v:,}", 13, MUTED, anchor="end")
    for yr in range(1970, 2027, 5):
        s.text(xs(yr), Y1 + 24, str(yr), 13, MUTED, anchor="middle")

    # stoppages that cost games: red-tinted columns
    for a, b, lab in ((1972, 1972, "1972 STRIKE"), (1981, 1981, "1981 STRIKE"), (1994, 1995, "1994-95 STRIKE")):
        s.rect(xs(a) - step / 2, Y0 - 12, xs(b) - xs(a) + step, Y1 - Y0 + 12, RED_TINT)
        s.text((xs(a) + xs(b)) / 2, Y0 - 20, lab, 11, RED, anchor="middle", spacing=1.4)
    # the 2021-22 lockout, no games lost: one thin dashed line between the 2021 and 2022 seasons
    s.line(xs(2021.5), Y0 - 12, xs(2021.5), Y1, RED, 1, dash="3 3")
    s.text(xs(2021.5), Y0 - 34, "2021-22 LOCKOUT", 11, RED, anchor="end", spacing=1.4)
    s.text(xs(2021.5), Y0 - 20, "NO GAMES LOST", 11, RED, anchor="end", spacing=1.4)

    # reference lines for 2026
    for v, lab in ((pg[PEAK_YR], f"2007 peak, {pg[PEAK_YR]:,}"), (pg[1994], f"1994 pace, {pg[1994]:,}")):
        s.line(xs(1994) if v == pg[1994] else xs(PEAK_YR), ys(v), X1 + 12, ys(v), NAVY, 1, dash="5 4")
        s.text(X1 + 18, ys(v) + 5, lab, 13, NAVY)

    # expansions: a dotted leader from the axis to the season's point
    for yr in EXPANSIONS:
        s.line(xs(yr), Y1, xs(yr), ys(pg[yr]) + 8, FAINT, 1, dash="1 3")
        s.text(xs(yr), Y1 - 8, f"{teams[yr - 1]}→{teams[yr]}", 11, MUTED, anchor="middle", halo=True)
    col_head(s, X0, Y1 + 52, "DOTTED LEADERS MARK EXPANSION SEASONS, TEAMS BEFORE AND AFTER")

    # the series: 1970-2019 solid, gap for 2020, 2021 alone and hollow, 2022-2025 solid, 2026 in progress
    seg1 = [(xs(y), ys(pg[y])) for y in YEARS if y <= 2019]
    seg2 = [(xs(y), ys(pg[y])) for y in YEARS if 2022 <= y <= 2025]
    s.poly(seg1, NAVY, 2.5)
    s.poly(seg2, NAVY, 2.5)
    s.poly([seg2[-1], (xs(2026), ys(pg[2026]))], NAVY, 2.5, dash="4 4")
    s.circle(xs(2021), ys(pg[2021]), 5, PAPER, stroke=NAVY, sw=2)
    s.text(xs(2021) - 10, ys(pg[2021]) + 5, f"2021, capacity limits early in season: {pg[2021]:,}", 13, MUTED,
           anchor="end", halo=True)
    # 2020: centered in the gap between the 2019 and 2021 points, no leader
    y_gap = (ys(pg[2019]) + ys(pg[2021])) / 2
    s.text(xs(2020), y_gap - 3, "2020", 11, MUTED, anchor="middle")
    s.text(xs(2020), y_gap + 11, "no fans", 11, MUTED, anchor="middle")
    s.circle(xs(2026), ys(pg[2026]), 6, PAPER, stroke=NAVY, sw=2.5)
    s.text(X1 + 18, ys(pg[2026]) + 5, f"2026, in progress, {pg[2026]:,}", 13, NAVY)
    s.text(X1 + 18, ys(pg[2026]) + 23, f"{gap_pace:.1f}% vs 1994 pace", 13, RED)
    s.text(X1 + 18, ys(pg[2026]) + 41, f"{gap_peak:.1f}% vs 2007 peak", 13, RED)
    s.circle(xs(PEAK_YR), ys(pg[PEAK_YR]), 5, NAVY)

    # the 1993 expansion note, where the jump is
    x93, y93 = xs(1993), ys(pg[1993])
    s.circle(x93, y93, 5, NAVY)
    nx, ny = xs(1978.5), ys(33_000)
    s.text(nx, ny, f"1993: {teams[1992]} to {teams[1993]} teams, per game up {jump_1993:.1f}%,", 13, NAVY, halo=True)
    s.text(nx, ny + 18, f"from {pg[1992]:,} to {pg[1993]:,}. The 1994-95 baseline", 13, NAVY, halo=True)
    s.text(nx, ny + 36, "starts on an expansion bump.", 13, NAVY, halo=True)
    s.line(nx + 330, ny + 30, x93 - 7, y93 - 4, FAINT, 1)

    s.text(48, H - 32, f"Source: {SRC_BR}. 2020 excluded by the source; no fans were admitted. "
                       f"2026 is a season in progress.", 12, MUTED)
    s.text(48, H - 14, "Gaps against the 1994 pace and the 2007 peak calculated.", 12, MUTED)
    s.write(stem)


fig_long_view("fig-05-long-view")
print("done ->", OUT)
