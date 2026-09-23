#!/usr/bin/env python3
"""Build the four in-article charts for payouts-vs-rosters-2026.

Every number is recomputed from the published distributions CSV (audited Form
990 filings) and the roster budgets CSV (The Athletic's estimated ranges), then
asserted against the five markdown tables and the Miami/Duke sentences in
draft.md before any SVG is written.

The distributions CSV is the one published with Parts 1, 2, and 3 at
https://www.gridironhq.ai/data/cfb-conference-distributions.csv. It is
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
ROSTER_CSV = REPO / "cfb-roster-budgets-2026/data/cfb-roster-budgets-2026.csv"
DRAFT = REPO / "payouts-vs-rosters-2026/draft.md"
REF_SVG = REPO / "cfb-roster-budgets-2026/figures/fig-02-top-eleven.svg"
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
EST_FILL = "rgba(212,85,61,0.38)"   # estimated-range fill: red at reduced opacity
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

LEGEND_FILED = "conference distribution, Form 990 filing, fiscal years ending in 2025, exact"
LEGEND_EST = "roster budget, The Athletic's estimated range, September 16, 2026; tick is the midpoint, calculated"
SOURCE_LINE = ("Source: Form 990 filings, fiscal years ending in 2025, Schedule A, Part I, via ProPublica (distributions); "
               "The Athletic, September 16, 2026 (roster budgets). Gaps, spreads, correlations, midpoints, and ratios calculated.")

# Roster CSV spellings -> distributions CSV spellings.
ALIAS = {"Pitt": "Pittsburgh", "Oklahoma St.": "Oklahoma State", "Michigan St.": "Michigan State",
         "Mississippi St.": "Mississippi State"}
CONFS = ["SEC", "Big 12", "ACC", "Big Ten"]

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
    dist_text = resp.read().decode("utf-8")
print("downloaded", CSV_URL)

dist = {}
with io.StringIO(dist_text) as fh:
    for r in csv.DictReader(fh):
        if r["season"] == "2024-25" and r["measure"] == "distribution":
            dist[r["school"]] = {"pay": int(r["amount"]), "share": r["share_type"], "conf": r["conference"]}

rows = []
with ROSTER_CSV.open() as fh:
    for r in csv.DictReader(fh):
        name = ALIAS.get(r["school"], r["school"])
        d = dist[name]
        lo, hi = int(r["budget_low_millions"]), int(r["budget_high_millions"])
        mid = (lo + hi) / 2
        assert mid == float(r["budget_mid_millions"]), name
        rows.append({"school": name, "conf": d["conf"], "share": d["share"], "pay": d["pay"],
                     "lo": lo, "hi": hi, "mid": mid, "ratio": mid * 1e6 / d["pay"]})
assert len(rows) == 68
by = {r["school"]: r for r in rows}
full = [r for r in rows if r["share"] == "full"]
assert len(full) == 56
byc = {c: [r for r in full if r["conf"] == c] for c in CONFS}
assert {c: len(v) for c, v in byc.items()} == {"SEC": 14, "Big 12": 12, "ACC": 14, "Big Ten": 16}


def avg_ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den


def spearman(a, b):
    return pearson(avg_ranks(a), avg_ranks(b))


def money(n):
    return f"${n:,}"


def rng(r):
    return f"${r['lo']}-{r['hi']}M"


def mid_m(r):
    return f"${r['mid']:.1f}M"


PAIRS = [("Miami", "Duke"), ("Arkansas", "LSU"), ("Texas Tech", "Colorado"), ("USC", "Purdue")]
pairs = []
for a, b in PAIRS:
    A, B = by[a], by[b]
    assert A["conf"] == B["conf"] and A["share"] == B["share"] == "full"
    pairs.append({"a": A, "b": B, "conf": A["conf"], "gap": abs(A["pay"] - B["pay"])})

spreads = []
for c in CONFS:
    rs = byc[c]
    ps = max(r["pay"] for r in rs) - min(r["pay"] for r in rs)
    ms = max(r["mid"] for r in rs) - min(r["mid"] for r in rs)
    spreads.append({"conf": c, "n": len(rs), "pay_spread": ps, "mid_spread": int(ms * 1e6), "ratio": ms * 1e6 / ps})
assert [s["ratio"] for s in spreads] == sorted((s["ratio"] for s in spreads), reverse=True)

rho = {c: spearman([r["pay"] for r in byc[c]], [r["mid"] for r in byc[c]]) for c in CONFS}
rho_all = spearman([r["pay"] for r in full], [r["mid"] for r in full])
rho_order = sorted(CONFS, key=lambda c: -rho[c])

by_ratio = sorted(full, key=lambda r: -r["ratio"])
top4, bot4 = by_ratio[:4], list(reversed(by_ratio[-4:]))

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
assert len(T) == 5, f"expected 5 tables in draft, found {len(T)}"
t_pairs, t_spreads, t_rho, t_top, t_bot = T
assert t_pairs[0] == ["Pair", "Conference", "Payouts", "Gap", "Roster budgets"], t_pairs[0]
assert t_spreads[0] == ["Conference", "Full-share schools", "Payout spread", "Roster spread (midpoint)", "Ratio"], t_spreads[0]
assert t_rho[0] == ["Conference", "n", "Correlation"], t_rho[0]
assert t_top[0] == t_bot[0] == ["School", "Conference", "Roster (range)", "Roster (midpoint)", "Payout", "Ratio"]

for cells, p in zip(t_pairs[1:], pairs[1:]):
    want = [f"{p['a']['school']} and {p['b']['school']}", p["conf"],
            f"{money(p['a']['pay'])} and {money(p['b']['pay'])}", money(p["gap"]),
            f"{rng(p['a'])} and {rng(p['b'])}"]
    assert cells == want, f"pairs table mismatch: draft {cells} vs computed {want}"
for cells, s in zip(t_spreads[1:], spreads):
    want = [s["conf"], str(s["n"]), money(s["pay_spread"]), money(s["mid_spread"]), f"{s['ratio']:.2f}x"]
    assert cells == want, f"spreads table mismatch: draft {cells} vs computed {want}"
for cells, c in zip(t_rho[1:], rho_order):
    want = [c, str(len(byc[c])), f"{rho[c]:.3f}"]
    assert cells == want, f"correlation table mismatch: draft {cells} vs computed {want}"
for tbl, rs in ((t_top, top4), (t_bot, bot4)):
    for cells, r in zip(tbl[1:], rs):
        want = [r["school"], r["conf"], rng(r), mid_m(r), money(r["pay"]), f"{r['ratio'] * 100:.1f}%"]
        assert cells == want, f"ratio table mismatch: draft {cells} vs computed {want}"

draft_text = DRAFT.read_text()
md = pairs[0]
for phrase in (f"Miami received {money(md['a']['pay'])}", f"Duke received {money(md['b']['pay'])}",
               f"The gap is {money(md['gap'])}",
               f"Miami's estimated roster budget for 2026 is ${md['a']['lo']}-{md['a']['hi']} million",
               f"Duke's is ${md['b']['lo']}-{md['b']['hi']} million",
               f"the correlation is {rho_all:.3f}"):
    assert phrase in draft_text, f"draft no longer says: {phrase}"
print("draft tables match recomputation: 3 pairs + Miami/Duke prose, 4 spreads, 4 correlations, 4 + 4 ratios")

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

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, opacity=None, halo=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if halo:
            extra += f' stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
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

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

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


def header(s, title, subtitle, subtitle2=None):
    s.text(48, 46, title, 28)
    s.text(48, 76, subtitle, 17, MUTED)
    if subtitle2:
        s.text(48, 98, subtitle2, 17, MUTED)


def col_head(s, x, y, label, anchor="start", fill=MUTED):
    s.text(x, y, label, 12, fill, anchor=anchor, spacing=1.8)


def filed_bar(s, x0, x1, y, h=9):
    """Solid navy bar from the origin: a filed figure."""
    s.rect(x0, y - h / 2, x1 - x0, h, NAVY, rx=2)


def est_range(s, xlo, xhi, xmid, y, h=10):
    """Red range at reduced opacity with solid caps and a solid midpoint tick: an estimate."""
    s.rect(xlo, y - h / 2, xhi - xlo, h, EST_FILL, rx=2)
    s.rect(xlo, y - h / 2, 2, h, RED)
    s.rect(xhi - 2, y - h / 2, 2, h, RED)
    s.rect(xmid - 1, y - h / 2 - 3, 2, h + 6, RED)


def est_range_v(s, x, ylo, yhi, ymid, w=6):
    """Vertical version for the scatter panels."""
    s.rect(x - w / 2, yhi, w, ylo - yhi, EST_FILL, rx=2)
    s.rect(x - w / 2, yhi, w, 2, RED)
    s.rect(x - w / 2, ylo - 2, w, 2, RED)
    s.rect(x - w / 2 - 3, ymid - 1, w + 6, 2, RED)


def legend(s, y, filed_mark="bar"):
    x = 48
    if filed_mark == "bar":
        s.rect(x, y - 9, 22, 8, NAVY, rx=2)
        s.text(x + 30, y, LEGEND_FILED, 13, MUTED)
    else:
        s.text(x, y, "position across: " + LEGEND_FILED, 13, MUTED)
    y2 = y + 22
    est_range(s, x, x + 30, x + 17, y2 - 5, h=8)
    s.text(x + 38, y2, ("range up: " if filed_mark != "bar" else "") + LEGEND_EST, 13, MUTED)


def dollar_axis(s, x0, x1, vmax, y_top, y_bottom, y_label, step):
    """Shared dollar axis, 0 to vmax (in dollars), gridlines every `step` dollars."""
    v = 0
    while v <= vmax + 1:
        x = x0 + (x1 - x0) * v / vmax
        s.rect(x - 0.5, y_top, 1, y_bottom - y_top, GRID)
        s.text(x, y_label, f"${v // 1_000_000}M", 13, MUTED, anchor="middle")
        v += step


# --------------------------------------------------------------------------
# Fig 02: same check, different roster
# --------------------------------------------------------------------------

def fig_pairs(stem):
    title = "Same check, different roster"
    subtitle = "Four pairs of schools on the same conference contract. The filed checks nearly match; the estimated rosters don't."
    X0, X1, VMAX = 330, 820, 80_000_000
    RH, GROUP_GAP, Y0 = 46, 30, 152
    SEC_H = 26  # section label height inside each group
    group_h = SEC_H + 2 * RH + GROUP_GAP
    y_last = Y0 + (len(pairs) - 1) * group_h + SEC_H + RH + RH / 2  # centre of the last row
    y_axis_lbl = y_last + 34
    y_legend = y_axis_lbl + 36
    H = y_legend + 22 + 44
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 118, "SCHOOL")
    col_head(s, X0, 118, "CONFERENCE CHECK AND ROSTER BUDGET, $0 TO $80M")
    col_head(s, 850, 118, "FILED, FORM 990")
    col_head(s, 1152, 118, "ESTIMATED RANGE", anchor="end")
    dollar_axis(s, X0, X1, VMAX, 130, y_last + 18, y_axis_lbl, 20_000_000)
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for gi, p in enumerate(pairs):
        yg = Y0 + gi * group_h
        if gi:
            s.rect(48, yg - GROUP_GAP / 2 - 6, 1104, 1, GRID)
        label = f"{p['a']['school'].upper()} AND {p['b']['school'].upper()}, {p['conf'].upper()}: CHECKS {money(p['gap'])} APART"
        col_head(s, 48, yg + 4, label, fill=RED if gi == 0 else MUTED)
        for i, r in enumerate((p["a"], p["b"])):
            y = yg + SEC_H + i * RH + RH / 2
            s.text(48, y + 7, r["school"], 21)
            filed_bar(s, X0, xs(r["pay"]), y - 8)
            est_range(s, xs(r["lo"] * 1e6), xs(r["hi"] * 1e6), xs(r["mid"] * 1e6), y + 9)
            s.text(850, y + 6, money(r["pay"]), 17)
            s.text(1152, y + 6, rng(r), 17, anchor="end")
    legend(s, y_legend)
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


fig_pairs("fig-02-pairs")

# --------------------------------------------------------------------------
# Fig 03: spreads by conference
# --------------------------------------------------------------------------

def fig_spreads(stem):
    title = "It holds across all four conferences"
    subtitle = "Top-to-bottom spread among full-share schools: the filed check against the estimated roster budget on midpoints."
    X0, X1, VMAX = 330, 940, 40_000_000
    RH, Y0 = 88, 168
    y_last = Y0 + (len(spreads) - 1) * RH
    y_axis_lbl = y_last + 62
    y_legend = y_axis_lbl + 36
    H = y_legend + 22 + 44
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 118, "CONFERENCE")
    col_head(s, X0, 118, "SPREAD, HIGHEST MINUS LOWEST, $0 TO $40M")
    col_head(s, 1152, 118, "ROSTER SPREAD OVER PAYOUT SPREAD", anchor="end")
    dollar_axis(s, X0, X1, VMAX, 130, y_last + 44, y_axis_lbl, 10_000_000)
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for i, sp in enumerate(spreads):
        y = Y0 + i * RH
        if i:
            s.rect(48, y - RH / 2 + 4, 1104, 1, GRID)
        s.text(48, y + 4, sp["conf"], 24)
        s.text(48, y + 26, f"{sp['n']} full-share schools", 14, MUTED)
        s.text(X0 - 12, y - 8, "checks, filed", 12, MUTED, anchor="end")
        s.text(X0 - 12, y + 18, "rosters, estimated", 12, MUTED, anchor="end")
        filed_bar(s, X0, xs(sp["pay_spread"]), y - 12, h=11)
        s.text(xs(sp["pay_spread"]) + 10, y - 7, money(sp["pay_spread"]), 15)
        # roster spread is a single value on midpoints: reduced-opacity red with solid caps, no midpoint tick
        s.rect(X0, y + 8, xs(sp["mid_spread"]) - X0, 11, EST_FILL, rx=2)
        s.rect(X0, y + 8, 2, 11, RED)
        s.rect(xs(sp["mid_spread"]) - 2, y + 8, 2, 11, RED)
        s.text(xs(sp["mid_spread"]) + 10, y + 18, money(sp["mid_spread"]), 15)
        s.text(1152, y + 10, f"{sp['ratio']:.2f}x", 26, RED if i == 0 else NAVY, anchor="end")
    legend(s, y_legend)
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


fig_spreads("fig-03-spreads")

# --------------------------------------------------------------------------
# Fig 04: correlation, four scatter panels
# --------------------------------------------------------------------------

NAMED = {"Miami", "Duke", "Arkansas", "LSU", "Texas Tech", "Colorado", "USC", "Purdue",
         "Boston College", "Illinois", "Iowa"}
LABEL_LEFT = {"Colorado", "Purdue", "USC"}   # label on the left where the right side is crowded
X_SPAN = 18_000_000   # every panel spans exactly $18M of payout so horizontal scale is honest across panels
Y_MAX = 55_000_000


def fig_scatter(stem):
    title = "Inside a conference, the check doesn't predict the roster"
    sub1 = "Each full-share school at its filed check (across) and its estimated roster range (up). Every panel spans $18M across."
    sub2 = f"Spearman rank correlation per conference. Across all 56 schools together it's {rho_all:.3f}, which mostly reflects conference membership."
    PW, PH = 520, 300
    PX = [48, 632]
    PY = [186, 186 + PH + 96]
    H = PY[1] + PH + 168
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    panels = [("ACC", 0, 0), ("SEC", 0, 1), ("Big 12", 1, 0), ("Big Ten", 1, 1)]
    for conf, col, row in panels:
        rs = byc[conf]
        x0, y0 = PX[col], PY[row]
        x1, y1 = x0 + PW, y0 + PH
        lo_pay = min(r["pay"] for r in rs)
        hi_pay = max(r["pay"] for r in rs)
        centre = (lo_pay + hi_pay) / 2
        xmin = centre - X_SPAN / 2
        xs = lambda v: x0 + 40 + (PW - 60) * (v - xmin) / X_SPAN
        ys = lambda v: y1 - (PH - 30) * v / Y_MAX
        s.text(x0, y0 - 30, conf, 22)
        s.text(x0 + (len(conf) * 12) + 14, y0 - 30, f"{len(rs)} schools", 14, MUTED)
        s.text(x1, y0 - 30, f"Spearman {rho[conf]:.3f}", 18, RED if conf == "ACC" else NAVY, anchor="end")
        for v in (0, 25_000_000, 50_000_000):
            s.rect(x0 + 40, ys(v) - 0.5, PW - 60, 1, GRID)
            s.text(x0 + 32, ys(v) + 4, f"${v // 1_000_000}M", 13, MUTED, anchor="end")
        tick = (int(xmin // 5_000_000) + 1) * 5_000_000
        while tick < xmin + X_SPAN:
            s.rect(xs(tick) - 0.5, ys(Y_MAX), 1, y1 - ys(Y_MAX), GRID)
            s.text(xs(tick), y1 + 18, f"${tick // 1_000_000}M", 13, MUTED, anchor="middle")
            tick += 5_000_000
        s.text(x0 + 40, y1 + 40, "ACROSS: FILED CHECK, FORM 990, $18M WINDOW", 11, MUTED, spacing=1.6)
        s.text(x0, y0 - 8, "UP: ESTIMATED ROSTER RANGE, THE ATHLETIC", 11, MUTED, spacing=1.6)
        # marks, then labels with simple vertical de-collision
        labels = []
        for r in rs:
            x = xs(r["pay"])
            est_range_v(s, x, ys(r["lo"] * 1e6), ys(r["hi"] * 1e6), ys(r["mid"] * 1e6))
            if r["school"] in NAMED:
                labels.append([x, ys(r["mid"] * 1e6), r["school"]])
        labels.sort(key=lambda l: l[1])
        for i in range(1, len(labels)):
            if labels[i][1] - labels[i - 1][1] < 18:
                labels[i][1] = labels[i - 1][1] + 18
        for x, y, name in labels:
            left = name in LABEL_LEFT or x > x1 - 120
            anchor, dx = ("end", -10) if left else ("start", 10)
            s.text(x + dx, y + 5, name, 16, NAVY, anchor=anchor, halo=True)
    legend(s, H - 84, filed_mark="range")
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


fig_scatter("fig-04-correlation")

# --------------------------------------------------------------------------
# Fig 05: the ratio, and what it doesn't mean
# --------------------------------------------------------------------------

def fig_ratio(stem):
    title = "The ratio, and what it doesn't mean"
    sub1 = "Roster budget as a percentage of the conference check, highest four and lowest four of the 56 full-share schools."
    sub2 = "The check funds every sport in the department; the roster is football players only. A scale comparison, not a share."
    X0, X1, VMAX = 330, 780, 80_000_000
    RH, SEC_H, SEC_GAP, Y0 = 50, 28, 34, 176
    y_bot0 = Y0 + SEC_H + 4 * RH + SEC_GAP
    y_last = y_bot0 + SEC_H + 3 * RH + RH / 2
    y_axis_lbl = y_last + 36
    y_legend = y_axis_lbl + 36
    H = y_legend + 22 + 44
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 140, "SCHOOL")
    col_head(s, X0, 140, "CONFERENCE CHECK AND ROSTER BUDGET, $0 TO $80M")
    col_head(s, 810, 140, "FILED, FORM 990")
    col_head(s, 960, 140, "ESTIMATED")
    col_head(s, 1152, 140, "RATIO", anchor="end")
    dollar_axis(s, X0, X1, VMAX, 152, y_last + 18, y_axis_lbl, 20_000_000)
    xs = lambda v: X0 + (X1 - X0) * v / VMAX

    def section(label, y, fill):
        s.rect(48, y - 6, 1104, 1, GRID)
        col_head(s, 48, y + 12, label, fill=fill)

    for label, y_sec, rs, fill in (("HIGHEST FOUR", Y0, top4, RED), ("LOWEST FOUR", y_bot0, bot4, MUTED)):
        section(label, y_sec, fill)
        for i, r in enumerate(rs):
            y = y_sec + SEC_H + i * RH + RH / 2
            s.text(48, y + 3, r["school"], 20)
            s.text(48, y + 21, r["conf"], 13, MUTED)
            filed_bar(s, X0, xs(r["pay"]), y - 8)
            est_range(s, xs(r["lo"] * 1e6), xs(r["hi"] * 1e6), xs(r["mid"] * 1e6), y + 9)
            s.text(810, y + 6, money(r["pay"]), 17)
            s.text(960, y + 6, rng(r), 17)
            s.text(1152, y + 8, f"{r['ratio'] * 100:.1f}%", 24, RED if r["ratio"] >= 1 else NAVY, anchor="end")
    legend(s, y_legend)
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


fig_ratio("fig-05-ratio")
print("done ->", OUT)
