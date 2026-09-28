#!/usr/bin/env python3
"""Build the in-article charts for pca-mvp-2026.

fig-01-season: two panels. FanGraphs WAR by season 2024-2026 as bars, 2026 in
red; and 2026 in runs above average, Off as one bar split into batting (Off minus
BsR, calculated) and baserunning, with Def as a separate bar, because BsR is
inside Off and the three are not additive.

fig-02-savings-curve: extension savings (NPV to 2026) as a function of true
talent entering 2027, 4 to 11 FanGraphs WAR, drawn from the September 14 model's
run() at $9.0M per win and 100% capture. The 6.5, 8.0 and 10.6 readings are dots
on the curve; his 2025 (5.4) and 2026 (10.6) seasons are red markers on the
talent axis with leaders up to the curve. 2025 meets the curve at the zero line.
fig-03-savings-split: control years against free agent years, net PV, at 6.5,
8.0 and 10.6, from components() in pca-mvp-2026/model/recompute_outline.py.
fig-04-war-scales: WAR by season 2024-2026, FanGraphs and Baseball Reference as
two separate lines on one axis.

The model is imported from pca-extension-2026/model/ inside a temp directory,
because importing it runs a Monte Carlo that writes files to the working
directory. Every figure, and the captions, are asserted against draft.md and
captions.md before any SVG is written.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and
falls back to Georgia, matching mlb-1994-base-rate-2026.

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to this script's directory; --final skips the 700px previews.
"""
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
PIECE = REPO / "pca-mvp-2026"
DRAFT = PIECE / "draft.md"
MODEL_DIR = REPO / "pca-extension-2026/model"
RECOMPUTE_DIR = PIECE / "model"
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
GRID = "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

DPW, CAPTURE = 9.0, 1.00
SEASONS = {2025: 5.4, 2026: 10.6}            # FanGraphs WAR, final
FG_WAR = {2024: 2.6, 2025: 5.4, 2026: 10.6}   # FanGraphs, final, read September 28, 2026
BR_WAR = {2024: 2.3, 2025: 5.9, 2026: 9.8}    # Baseball Reference, page updated Sept 27, read Sept 28
# 2026 FanGraphs components, runs above average. Off = batting runs + base running runs
# (FanGraphs library), so BsR sits inside Off; batting is calculated as Off minus BsR.
OFF, DEF, BSR = 57.7, 23.2, 8.3
BAT = round(OFF - BSR, 1)
RUNS_NOTE = "Runs, not WAR. About 10 runs equal one win (FanGraphs)."
READINGS = [  # (draft row label, chart label, talent)
    ("September 14 base case", "September 14 base case", 6.5),
    ("Two-season average of 5.4 and 10.6", "Two-season average", 8.0),
    ("2026 taken at face value", "2026 at face value", 10.6),
]
BEND_NOTE = ("the curve flattens slightly below 5.6 because the model floors "
             "free agent WAR at zero for ages 34 to 36")

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(RECOMPUTE_DIR))
_cwd = os.getcwd()
os.chdir(tempfile.mkdtemp(prefix="pca_mvp_fig_"))
try:
    with contextlib.redirect_stdout(io.StringIO()):
        import pca_model as M
        from pca_sensitivity import run
        from recompute_outline import components   # the function behind the draft's Section 5
finally:
    os.chdir(_cwd)


def savings(t):
    return run(t, DPW, CAPTURE)[1]


lo, hi = 3.0, 8.0
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (lo, mid) if savings(mid) > 0 else (mid, hi)
BREAKEVEN = (lo + hi) / 2

# the bend: talent at which free agent WAR hits the zero floor at ages 34, 35, 36
FLOORS = [round(-M.AGE_DELTA[a], 1) for a in (34, 35, 36)]
assert FLOORS == [4.2, 4.9, 5.6], FLOORS
assert abs((savings(11.0) - savings(6.0)) / 5 - (savings(6.0) - savings(5.6)) / 0.4) < 1e-6  # linear above 5.6
assert (savings(5.6) - savings(5.0)) / 0.6 < (savings(6.0) - savings(5.6)) / 0.4 - 1         # flatter below

# --------------------------------------------------------------------------
# Assert against the draft
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
table = [[c.strip() for c in l.strip().strip("|").split("|")] for l in draft.splitlines() if l.startswith("|")]
table = {r[0]: r for r in table if len(r) == 4 and r[1][:1].isdigit()}
rows = [("His 2025 season", 5.4)] + [(d, t) for d, _, t in READINGS]
for label, t in rows:
    gross, save, _ = run(t, DPW, CAPTURE)
    want = [label, f"{t}", f"${save:.1f}M", f"${gross:.1f}M"]
    assert table.get(label) == want, f"draft table mismatch: {table.get(label)} vs {want}"
ts = [t for _, t in rows]
slopes = [(savings(b) - savings(a)) / (b - a) for a, b in zip(ts, ts[1:])]
for phrase in (f"you get {BREAKEVEN:.3f} wins",
               f"from ${min(slopes):.1f} million to ${max(slopes):.1f} million per win",
               f"His 2025 season on FanGraphs was {SEASONS[2025]}"):
    assert phrase in draft, f"draft no longer says: {phrase}"
print(f"draft matches model: table (4 rows), breakeven {BREAKEVEN:.3f}, slopes, 2025 fWAR")

# fig-03: the Section 5 split
SPLIT = {t: components(t) for _, _, t in READINGS}
S65, S80, S106 = (SPLIT[t] for t in (6.5, 8.0, 10.6))
for phrase in (f"${S65['control']:.1f} million net for 2027 through 2030, against ${S65['fa']:.1f} million for 2031 and 2032",
               f"tied at ${S80['control']:.1f} million each",
               f"the free agent years lead, ${S106['fa']:.1f} million to ${S106['control']:.1f} million",
               f"the control years also absorb the ${M.SIGNING_BONUS:.0f} million signing bonus"):
    assert phrase in draft, f"draft no longer says: {phrase}"
assert f"{S80['control']:.1f}" == f"{S80['fa']:.1f}", "8.0 is no longer a tie at one decimal"
assert S65["control"] > S65["fa"] and S106["fa"] > S106["control"]
print("draft matches recompute_outline.components(): Section 5 split at 6.5, 8.0, 10.6")

# fig-04: WAR on both scales
fw = FG_WAR
assert (f"his WAR went from {fw[2024]} in 2024 to {fw[2025]} in 2025 and {fw[2026]} this season"
        in draft), "Section 1 no longer gives fWAR 2024-26"
for phrase in (f"Baseball Reference has him at {BR_WAR[2024]} in 2024, {BR_WAR[2025]} in 2025 and {BR_WAR[2026]} in 2026",
               f"The last two average {(BR_WAR[2025] + BR_WAR[2026]) / 2:.2f}",
               f"savings at ${savings((BR_WAR[2025] + BR_WAR[2026]) / 2):.1f} million"):
    assert phrase in draft, f"draft no longer says: {phrase}"
assert FG_WAR[2025] < BR_WAR[2025] and FG_WAR[2026] > BR_WAR[2026]   # the fig-04 title's claim
print("draft matches WAR on both scales: FanGraphs 2024-26, Baseball Reference 2024-26, 7.85 average")

# fig-01: the season, and 2026's components with BsR inside Off
assert BAT == 49.4
for phrase in (f"{OFF} runs above average on offense this year and {DEF} on defense",
               f"The offense figure already contains his {BSR} runs of baserunning",
               f"batting alone comes to {BAT} runs",
               f"{BAT} batting runs this year, his offense figure less its baserunning"):
    assert phrase in draft, f"draft no longer says: {phrase}"
for additive in ("| 2026 components |", "Off 57.7, Def 23.2, BsR 8.3", "an Off of 57.7"):
    assert additive not in draft, f"draft still lists the components as if additive: {additive}"
ratios = (fw[2025] / fw[2024], fw[2026] / fw[2025])
assert all(1.9 < r < 2.1 for r in ratios), ratios        # the fig-01 title's "doubled twice"
assert BAT > DEF + BSR                                   # "most ... above average came from the bat"
print(f"draft matches fig-01: fWAR 2024-26, Off {OFF} = batting {BAT} + BsR {BSR}, Def {DEF}, "
      f"no additive listing")

# captions
captions = CAPTIONS.read_text()
assert BEND_NOTE[0].upper() + BEND_NOTE[1:] in captions and "26.3 million" not in captions
assert RUNS_NOTE in captions or RUNS_NOTE.rstrip(".") in captions
for key in ("fig-01-season", "fig-02-savings-curve", "fig-03-savings-split", "fig-04-war-scales"):
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
print("captions carry the bend clause, the runs note, no $26.3M figure, and all four draft slots")

# --------------------------------------------------------------------------
# SVG helpers (house style, shared with mlb-1994-base-rate-2026)
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


def money(v):
    if v == 0:
        return "$0"
    return f"−${-v:.0f}M" if v < 0 else f"${v:.0f}M"

# --------------------------------------------------------------------------
# Fig 02: extension savings by true talent
# --------------------------------------------------------------------------

def fig_savings_curve(stem):
    title = "The extension's breakeven lands on his 2025 season."
    sub1 = ("Extension savings, present value to 2026, by true talent entering 2027 "
            "(FanGraphs WAR). Only talent varies.")
    sub2 = (f"${DPW:.1f}M per win, 100% free agent capture, the September 14 model unchanged. "
            f"Breakeven: {BREAKEVEN:.3f}.")
    X0, X1, T0, T1 = 130, 1080, 4.0, 11.0
    Y0, Y1, VMIN, VMAX = 190, 590, -40, 160
    xs = lambda t: X0 + (X1 - X0) * (t - T0) / (T1 - T0)
    ys = lambda v: Y1 - (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
    H = Y1 + 118
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 158, "EXTENSION SAVINGS, PRESENT VALUE TO 2026")

    for v in range(VMIN, VMAX + 1, 40):
        if v != 0:
            s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 14, ys(v) + 5, money(v), 13, MUTED, anchor="end")
    s.line(X0, ys(0), X1 + 12, ys(0), NAVY, 1.5)
    for t in range(int(T0), int(T1) + 1):
        s.text(xs(t), Y1 + 24, str(t), 13, MUTED, anchor="middle")
    col_head(s, X0, Y1 + 76, "TRUE TALENT ENTERING 2027, FANGRAPHS WAR")

    # the curve, straight from run() at 0.05-win steps
    n = int(round((T1 - T0) / 0.05))
    pts = [(xs(T0 + i * 0.05), ys(savings(T0 + i * 0.05))) for i in range(n + 1)]
    s.poly(pts, NAVY, 3)

    # muted note under the zero line; ends short of the 2026 leader so the two don't cross.
    # The bend is described in the caption only.
    s.text(xs(SEASONS[2026]) - 14, ys(0) + 22, "below zero, the extension costs the Cubs money", 13, MUTED,
           anchor="end")

    # his seasons: red markers on the talent axis, dotted leaders up to the curve
    for yr, t in SEASONS.items():
        x, y = xs(t), ys(savings(t))
        s.line(x, Y1, x, y + 8, RED, 1.5, dash="2 4")
        s.line(x, Y1 - 6, x, Y1 + 6, RED, 2.5)
        s.text(x, Y1 + 48, f"{yr}: {t}", 14, RED, anchor="middle", halo=True)

    # 2025 meets the curve at the zero line
    x25, y25 = xs(SEASONS[2025]), ys(savings(SEASONS[2025]))
    s.circle(x25, y25, 8, "none", stroke=RED, sw=2)
    s.text(x25 - 14, y25 - 14, f"breakeven {BREAKEVEN:.3f}", 14, RED, anchor="end", halo=True)

    # the model readings: navy dots, labeled upper left
    for _, label, t in READINGS:
        x, y = xs(t), ys(savings(t))
        s.circle(x, y, 5.5, NAVY)
        s.text(x - 12, y - 12, f"{label}, ${savings(t):.1f}M", 14, NAVY, anchor="end", halo=True)

    s.text(48, H - 14, "Model: pca-extension-2026, run September 28, 2026. WAR: FanGraphs, final. "
                       "Savings calculated.", 12, MUTED)
    s.write(stem)


fig_savings_curve("fig-02-savings-curve")

# --------------------------------------------------------------------------
# Fig 01: the season. WAR by season, and 2026's components in runs
# --------------------------------------------------------------------------

def fig_season(stem):
    title = "His WAR doubled twice. Most of 2026's value above average came from the bat."
    sub1 = "Left: FanGraphs WAR by season. Right: his 2026 on FanGraphs, in runs above average."
    sub2 = "FanGraphs counts baserunning inside offense, so it's drawn as part of the offense bar, not added to it."
    Y0, Y1 = 196, 546
    H = Y1 + 104
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    # ---- left panel: WAR by season
    LX0, LX1, WMAX = 110, 540, 12
    wy = lambda v: Y1 - (Y1 - Y0) * v / WMAX
    col_head(s, 48, 166, "FANGRAPHS WAR")
    for v in range(0, WMAX + 1, 2):
        s.line(LX0, wy(v), LX1, wy(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(LX0 - 14, wy(v) + 5, str(v), 13, MUTED, anchor="end")
    years = sorted(FG_WAR)
    gw, bw = (LX1 - LX0) / len(years), 96
    for i, yr in enumerate(years):
        cx = LX0 + gw * (i + 0.5)
        col = RED if yr == 2026 else NAVY
        s.rect(cx - bw / 2, wy(FG_WAR[yr]), bw, Y1 - wy(FG_WAR[yr]), col)
        s.text(cx, wy(FG_WAR[yr]) - 10, f"{FG_WAR[yr]}", 17, col, anchor="middle")
        s.text(cx, Y1 + 26, str(yr), 15, NAVY, anchor="middle")

    # ---- right panel: 2026 components, runs above average
    RX0, RX1, RMAX = 680, 1150, 60
    ry = lambda v: Y1 - (Y1 - Y0) * v / RMAX
    col_head(s, 630, 166, "2026, RUNS ABOVE AVERAGE")
    for v in range(0, RMAX + 1, 10):
        s.line(RX0, ry(v), RX1, ry(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(RX0 - 14, ry(v) + 5, str(v), 13, MUTED, anchor="end")
    bw = 110
    ox, dx = RX0 + 60, RX0 + 280
    # Off: one bar, batting below, baserunning on top, one total
    s.rect(ox, ry(BAT), bw, Y1 - ry(BAT), NAVY)
    s.rect(ox, ry(OFF), bw, ry(BAT) - ry(OFF), FAINT)
    s.line(ox, ry(BAT), ox + bw, ry(BAT), PAPER, 2)
    s.text(ox + bw / 2, (ry(BAT) + Y1) / 2 - 4, "batting", 14, PAPER, anchor="middle")
    s.text(ox + bw / 2, (ry(BAT) + Y1) / 2 + 16, f"{BAT}", 16, PAPER, anchor="middle")
    s.text(ox + bw + 12, (ry(OFF) + ry(BAT)) / 2 + 5, f"baserunning {BSR}", 14, NAVY)
    s.text(ox + bw / 2, ry(OFF) - 10, f"{OFF}", 17, NAVY, anchor="middle")
    s.text(ox + bw / 2, Y1 + 26, "Offense (Off)", 15, NAVY, anchor="middle")
    # Def: a separate bar
    s.rect(dx, ry(DEF), bw, Y1 - ry(DEF), MUTED)
    s.text(dx + bw / 2, ry(DEF) - 10, f"{DEF}", 17, NAVY, anchor="middle")
    s.text(dx + bw / 2, Y1 + 26, "Defense (Def)", 15, NAVY, anchor="middle")
    split = RUNS_NOTE.index(" About")
    s.text(RX1, ry(46), RUNS_NOTE[:split], 13, MUTED, anchor="end")
    s.text(RX1, ry(46) + 18, RUNS_NOTE[split + 1:], 13, MUTED, anchor="end")

    s.text(48, H - 32, "Source: FanGraphs, final, read September 28, 2026. Batting runs calculated as "
                       "Off minus BsR; per the FanGraphs library, Off is batting runs plus base running runs.",
           12, MUTED)
    s.text(48, H - 14, "Def includes the positional adjustment. WAR also counts replacement-level and league "
                       "adjustments not shown here.", 12, MUTED)
    s.write(stem)


fig_season("fig-01-season")

# --------------------------------------------------------------------------
# Fig 03: control years against free agent years
# --------------------------------------------------------------------------

def fig_savings_split(stem):
    title = "The better he is, the more of the savings sit in the free agent years."
    sub1 = ("Extension savings by source, present value to 2026, at three readings of true talent "
            "entering 2027 (FanGraphs WAR).")
    sub2 = f"${DPW:.1f}M per win, 100% free agent capture, the September 14 model unchanged."
    X0, X1 = 130, 1080
    Y0, Y1, VMAX = 206, 566, 80
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    BW, GAP = 104, 14
    H = Y1 + 136
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)

    # key
    s.rect(48, 128, 18, 12, NAVY)
    s.text(74, 139, "Control years, 2027-2030, net of the 2027 loss and the $5M signing bonus", 14, NAVY)
    s.rect(640, 128, 18, 12, RED)
    s.text(666, 139, "Free agent years bought out, 2031-2032", 14, NAVY)
    col_head(s, 48, 180, "EXTENSION SAVINGS, PRESENT VALUE TO 2026")

    for v in range(0, VMAX + 1, 20):
        s.line(X0, ys(v), X1, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 14, ys(v) + 5, money(v), 13, MUTED, anchor="end")

    gw = (X1 - X0) / len(READINGS)
    for i, (_, label, t) in enumerate(READINGS):
        cx = X0 + gw * (i + 0.5)
        for x, v, col in ((cx - GAP / 2 - BW, SPLIT[t]["control"], NAVY), (cx + GAP / 2, SPLIT[t]["fa"], RED)):
            s.rect(x, ys(v), BW, Y1 - ys(v), col)
            s.text(x + BW / 2, ys(v) - 10, f"${v:.1f}M", 15, col, anchor="middle")
        s.text(cx, Y1 + 30, f"{t}", 18, NAVY, anchor="middle")
        s.text(cx, Y1 + 52, label, 13, MUTED, anchor="middle")
    col_head(s, X0, Y1 + 88, "TRUE TALENT ENTERING 2027, FANGRAPHS WAR")

    s.text(48, H - 14, "Model: pca-extension-2026, run September 28, 2026, via pca-mvp-2026/model/recompute_outline.py. "
                       "Savings calculated.", 12, MUTED)
    s.write(stem)


fig_savings_split("fig-03-savings-split")

# --------------------------------------------------------------------------
# Fig 04: WAR by season on both scales
# --------------------------------------------------------------------------

def fig_war_scales(stem):
    title = "FanGraphs rates his 2025 lower and his 2026 higher than Baseball Reference."
    sub1 = "Wins above replacement by season, each site on its own scale. The two are never averaged together."
    sub2 = "FanGraphs is the scale used throughout this piece."
    YEARS = sorted(FG_WAR)
    X0, X1 = 200, 820
    Y0, Y1, VMAX = 170, 520, 12
    xs = lambda yr: X0 + (X1 - X0) * (yr - YEARS[0]) / (YEARS[-1] - YEARS[0])
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 96
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 146, "WINS ABOVE REPLACEMENT")

    for v in range(0, VMAX + 1, 2):
        s.line(X0 - 40, ys(v), X1 + 40, ys(v), NAVY if v == 0 else GRID, 1.5 if v == 0 else 1)
        s.text(X0 - 54, ys(v) + 5, str(v), 13, MUTED, anchor="end")
    for yr in YEARS:
        s.text(xs(yr), Y1 + 26, str(yr), 15, NAVY, anchor="middle")

    fg = [(xs(y), ys(FG_WAR[y])) for y in YEARS]
    br = [(xs(y), ys(BR_WAR[y])) for y in YEARS]
    s.poly(br, FAINT, 2, dash="6 5")
    s.poly(fg, NAVY, 3)
    for (x, y) in br:
        s.circle(x, y, 5, PAPER, stroke=FAINT, sw=2)
    for (x, y) in fg:
        s.circle(x, y, 5.5, NAVY)

    # values: whichever scale is higher that season is labeled above its dot, the other below
    for yr in YEARS:
        x = xs(yr)
        fg_hi = FG_WAR[yr] > BR_WAR[yr]
        for v, col, above in ((FG_WAR[yr], NAVY, fg_hi), (BR_WAR[yr], MUTED, not fg_hi)):
            s.text(x, ys(v) + (-14 if above else 24), f"{v}", 15, col, anchor="middle", halo=True)

    # line labels at the right end
    yr = YEARS[-1]
    s.text(xs(yr) + 22, ys(FG_WAR[yr]) + 5, "FanGraphs", 15, NAVY)
    s.text(xs(yr) + 22, ys(BR_WAR[yr]) + 5, "Baseball Reference", 15, MUTED)

    s.text(48, H - 14, "Source: FanGraphs, final, read September 28, 2026. Baseball Reference, "
                       "page updated September 27, 2026, read September 28, 2026.", 12, MUTED)
    s.write(stem)


fig_war_scales("fig-04-war-scales")
print("done ->", OUT)
