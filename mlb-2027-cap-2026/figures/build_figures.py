#!/usr/bin/env python3
"""Build the in-article charts for mlb-2027-cap-2026.

fig-01-dodgers-stack: the Dodgers' 2027 payroll built up from Tucker and Ohtani to projected, against the cap.
fig-02-all-30: all 30 clubs, signed contracts solid and projected outlined, cap and floor lines.
fig-03-over-max: the eight players whose 2027 luxury-tax figures exceed 15% of the cap, with the 15% and 16% lines.
fig-04-over-265: the eighteen contracts running in 2027 worth more than the proposal's $265 million maximum.

Every number comes through model/recompute.py (which fails on any mismatch with the data) and is
asserted against draft.md and captions.md before any SVG is written.

Usage: build_figures.py [out_dir] [--final]
"""
import contextlib
import io
import re
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
FINAL = "--final" in sys.argv

NAVY, RED, PAPER = "#16284A", "#D4553D", "#F7F5F0"
MUTED, FAINT, PALE, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.40)", "rgba(22,40,74,0.18)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-dodgers-stack", "fig-02-all-30", "fig-03-over-max", "fig-04-over-265")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.fails
print(f"model: all checks pass; {len(R.X)} clubs")
CAP, FLOOR, X = R.CAP, R.FLOOR, R.X
LAD = X["LAD"]
tuck, oht = R.tuck, R.oht
signed_over = sorted((t for t in X if R.osig(t) > 0), key=lambda t: -R.osig(t))
proj_over = sorted((t for t in X if R.oproj(t) > 0), key=lambda t: -R.oproj(t))
under_floor = [t for t in X if X[t]["proj"] < FLOOR]
assert len(signed_over) == 5 and len(proj_over) == 8 and len(under_floor) == 12
tot_signed = sum(R.osig(t) for t in signed_over)
tot_proj = sum(R.oproj(t) for t in proj_over)
players = sorted(((p["player"], p["team"], R.pmap[p["player"]]) for p in R.a15), key=lambda x: -x[2])
assert len(players) == 8 and sum(v > R.lim16 for _, _, v in players) == 7
big = sorted(((c["player"], c["team"], R.money(c["value"]) / 1e6) for c in R.big), key=lambda x: -x[2])
assert len(big) == 18 and big[0][0] == "Juan Soto"
MAXT = R.MAXT
f1 = lambda v: f"${v:.1f} million"; f2 = lambda v: f"${v:.2f} million"; f3 = lambda v: f"${v:.3f} million"

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
DRAFT_PHRASES = (
    f"The Dodgers have {f2(LAD['guar'])} of signed deals on the 2027 books, {f1(LAD['guar'] - CAP)} over a {f1(CAP)} cap",
    f"On signed contracts the Dodgers are at {f2(LAD['signed'])}, {f1(R.osig('LAD'))} over",
    f"they're at {f2(LAD['proj'])}, {f1(R.oproj('LAD'))} over",
    f"Together that's {f2(tuck + oht)}, {100 * (tuck + oht) / CAP:.1f}% of the cap for two players",
    f"and the Padres by {f1(R.osig('SD'))}, {f1(tot_signed)} over in all", f"which makes eight clubs and {f1(tot_proj)}",
    f"At a {f1(CAP)} cap, 15% is {f3(R.lim15)} and 16% is {f3(R.lim16)}",
    f"Seven are over the higher one too; deGrom is the exception",
    f"Eighteen contracts still running in 2027 are worth more in total than ${MAXT:.0f} million, and Soto's ${big[0][2]:.0f} million is {big[0][2] / MAXT:.1f} times that",
    f"Twelve clubs project under the {f1(FLOOR)} floor",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"against the owners' proposed cap of {f1(CAP)}",
    f"Guaranteed contracts alone come to {f2(LAD['guar'])}, {f1(LAD['guar'] - CAP)} over",
    f"Kyle Tucker ({f3(tuck)}) and Shohei Ohtani ({f2(oht)}) are {f2(tuck + oht)} of that, {100 * (tuck + oht) / CAP:.1f}% of the cap",
    f"gives {f2(LAD['signed'])} on signed contracts, {f1(R.osig('LAD'))} over",
    f"take it to {f2(LAD['proj'])}, {f1(R.oproj('LAD'))} over",
    f"with the proposed cap of {f1(CAP)} and floor of {f1(FLOOR)}",
    f"Five clubs are over the cap on signed contracts, {f1(tot_signed)} in all; eight are over on projection, {f1(tot_proj)} in all. Twelve project under the floor",
    f"exceed 15% of the proposed cap ({f3(R.lim15)})", f"Seven also exceed 16% ({f3(R.lim16)})",
    f"Jacob deGrom, at {f1(R.pmap['Jacob deGrom'])}, is between the two lines", f"Kyle Tucker leads at {f3(tuck)}",
    f"The eighteen contracts still running in 2027 whose total value exceeds ${MAXT:.0f} million",
    f"Juan Soto's ${big[0][2]:.0f} million is {big[0][2] / MAXT:.1f} times the maximum",
    f"Kansas City holds Bobby Witt Jr.'s {f1(R.money(R.witt['value']) / 1e6)}",
)
for p in CAPTION_PHRASES:
    assert p in captions, f"captions.md no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print(f"draft ({len(DRAFT_PHRASES)} phrases) and captions ({len(CAPTION_PHRASES)} phrases) match the model; four slots exist")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, weight=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if weight:
            extra += f' font-weight="{weight}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke=None, sw=1):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"; svg.write_text("".join(self.parts))
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


def source(s, H, text):
    s.text(48, H - 14, text, 12, MUTED)


SPOTRAC = "Spotrac 2027 luxury-tax projections, read October 27, 2026"
CAPSRC = "cap: AP, October 24, 2026, and CBS Sports, May 28, 2026"


def fig_dodgers_stack(stem):
    title = f"The Dodgers are ${R.osig('LAD'):.1f}M over the 2027 cap on contracts already signed."
    sub1 = f"Dodgers 2027 luxury-tax payroll, $ millions, built up step by step, against the owners' proposed cap (${CAP:.1f}M)."
    steps = [  # label, start, end, fill, stroke, total label or None
        ("Kyle Tucker", 0, tuck, RED, None, f"${tuck:.3f}M"),
        ("Shohei Ohtani", tuck, tuck + oht, RED, None, f"${oht:.2f}M; the two: ${tuck + oht:.2f}M, {100 * (tuck + oht) / CAP:.1f}% of the cap"),
        ("Every other guaranteed deal", tuck + oht, LAD["guar"], NAVY, None,
         f"Guaranteed ${LAD['guar']:.2f}M, ${LAD['guar'] - CAP:.1f}M over"),
        ("Benefits, minor league, bonus pool", LAD["guar"], LAD["signed"], FAINT, None,
         f"Signed contracts ${LAD['signed']:.2f}M, ${R.osig('LAD'):.1f}M over"),
        ("Projected arb and pre-arb", LAD["signed"], LAD["proj"], PAPER, NAVY,
         f"Projected ${LAD['proj']:.2f}M, ${R.oproj('LAD'):.1f}M over"),
    ]
    assert abs(steps[-1][2] - (LAD["guar"] + LAD["fixed"] + LAD["arb"] + LAD["pre"])) < 1e-6
    X0, X1, VMAX = 300, 860, 420
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 150, 62, 36
    H = Y0 + PITCH * len(steps) + 88
    s = SVG(1200, H, title)
    header(s, title, sub1)
    bottom = Y0 + PITCH * len(steps) - 20
    for v in range(0, VMAX + 1, 50):
        s.line(xs(v), Y0 - 16, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"${v}M", 11, MUTED, anchor="middle")
    for i, (label, a, b, fill, stroke, total) in enumerate(steps):
        y = Y0 + i * PITCH
        s.text(X0 - 16, y + 23, label, 15, NAVY, anchor="end")
        if i:
            s.line(xs(a), y - PITCH + BH, xs(a), y, FAINT, 1)   # connector from the previous step
        s.rect(xs(a), y, xs(b) - xs(a), BH, fill, stroke=stroke, sw=1.5)
        s.text(xs(b) + 10, y + 23, total, 14, RED if b > CAP else NAVY)
    s.line(xs(CAP), Y0 - 22, xs(CAP), bottom, RED, 1.5, dash="5,4")
    col_head(s, xs(CAP), Y0 - 28, f"PROPOSED CAP ${CAP:.1f}M", anchor="middle", fill=RED)
    s.text(48, H - 32, f"Source: {SPOTRAC}, and the Dodgers' tax page (benefits $18.5M, minor league, pre-arb bonus pool); {CAPSRC}.", 12, MUTED)
    source(s, H, "Signed contracts: guaranteed deals plus the fixed items, nothing projected. Projected figures are Spotrac's estimates, not awarded salaries.")
    s.write(stem)


def fig_all_30(stem):
    title = f"Five clubs are over the cap on signed contracts. On projection, eight, ${tot_proj:.1f}M over."
    sub1 = f"2027 luxury-tax payroll, $ millions, all 30 clubs, against the proposed cap (${CAP:.1f}M) and floor (${FLOOR:.1f}M)."
    order = sorted(X, key=lambda t: -X[t]["proj"])
    X0, X1, Y0, Y1, VMAX = 90, 1150, 130, 460, 420
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 96
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 50):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}M", 11, MUTED, anchor="end")
    pitch = (X1 - X0) / 30
    BW = pitch * 0.66
    for i, t in enumerate(order):
        x = X[t]
        bx = X0 + i * pitch + (pitch - BW) / 2
        s.rect(bx, ys(x["signed"]), BW, Y1 - ys(x["signed"]), RED if t in signed_over else NAVY)
        if x["proj"] > x["signed"]:
            s.rect(bx, ys(x["proj"]), BW, ys(x["signed"]) - ys(x["proj"]), PAPER, stroke=NAVY, sw=1.2)
        s.text(bx + BW / 2, Y1 + 16, t, 10, RED if t in proj_over else MUTED, anchor="middle")
    for v, label in ((CAP, f"CAP ${CAP:.1f}M"), (FLOOR, f"FLOOR ${FLOOR:.1f}M")):
        s.line(X0, ys(v), X1, ys(v), RED, 1.5, dash="5,4")
        col_head(s, X1, ys(v) - 6, label, anchor="end", fill=RED)
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    s.text(48, Y1 + 46, f"Solid: signed contracts (red where they alone are over the cap: five clubs, ${tot_signed:.1f}M above it). Outlined: Spotrac's projected arbitration and pre-arb salaries.", 12, MUTED)
    s.text(48, Y1 + 64, f"Red labels: the eight clubs over on projection. Twelve clubs project under the floor. Rosters are incomplete in October.", 12, MUTED)
    source(s, H, f"Source: {SPOTRAC}; {CAPSRC}.")
    s.write(stem)


def fig_over_max(stem):
    title = f"Eight players already count more than 15% of the proposed cap in 2027."
    sub1 = f"2027 luxury-tax figure, $ millions, against 15% (${R.lim15:.3f}M) and 16% (${R.lim16:.3f}M) of the proposed ${CAP:.1f}M cap; red is the excess over 15%."
    X0, X1, VMAX = 330, 1000, 60
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 150, 44, 28
    H = Y0 + PITCH * len(players) + 66
    s = SVG(1200, H, title)
    header(s, title, sub1)
    bottom = Y0 + PITCH * len(players) - 12
    for v in range(0, VMAX + 1, 10):
        s.line(xs(v), Y0 - 10, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"${v}M", 11, MUTED, anchor="middle")
    for i, (name, team, v) in enumerate(players):
        y = Y0 + i * PITCH
        s.text(X0 - 16, y + 19, f"{name}, {team}", 15, NAVY, anchor="end")
        s.rect(xs(0), y, xs(R.lim15) - xs(0), BH, NAVY)
        s.rect(xs(R.lim15), y, xs(v) - xs(R.lim15), BH, RED)
        label = f"${v:.3f}M" if name == "Kyle Tucker" else (f"${v:.2f}M" if name in ("Shohei Ohtani", "Cody Bellinger") else f"${v:.1f}M")
        s.text(max(xs(v), xs(R.lim16)) + 10, y + 19, label, 14, NAVY)
    s.line(xs(R.lim15), Y0 - 22, xs(R.lim15), bottom, RED, 1.5, dash="5,4")
    s.line(xs(R.lim16), Y0 - 22, xs(R.lim16), bottom, NAVY, 1.5, dash="2,3")
    col_head(s, xs(R.lim15) - 6, Y0 - 28, "15%: CHANGING TEAMS", anchor="end", fill=RED)
    col_head(s, xs(R.lim16) + 6, Y0 - 28, "16%: CORNERSTONE RE-SIGNING", fill=NAVY)
    source(s, H, "Source: Spotrac 2027 player rankings by luxury tax, read October 27, 2026; limits: CBS Sports timeline, June 25 entry, and Sportsnaut, June 26, 2026.")
    s.write(stem)


def fig_over_265(stem):
    title = f"Eighteen contracts running in 2027 are bigger than the ${MAXT:.0f}M the proposal would allow."
    sub1 = f"Total contract value, $ millions, against the proposed ${MAXT:.0f}M maximum; red is the amount above it."
    X0, X1, VMAX = 330, 1060, 800
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 130, 26, 18
    H = Y0 + PITCH * len(big) + 66
    s = SVG(1200, H, title)
    header(s, title, sub1)
    bottom = Y0 + PITCH * len(big) - 4
    for v in range(0, VMAX + 1, 100):
        s.line(xs(v), Y0 - 8, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"${v}M", 11, MUTED, anchor="middle")
    for i, (name, team, v) in enumerate(big):
        y = Y0 + i * PITCH
        s.text(X0 - 14, y + 14, f"{name}, {team}", 13, NAVY, anchor="end")
        s.rect(xs(0), y, xs(MAXT) - xs(0), BH, NAVY)
        s.rect(xs(MAXT), y, xs(v) - xs(MAXT), BH, RED)
        s.text(xs(v) + 8, y + 14, f"${v:.0f}M" if v == round(v) else f"${v:.1f}M", 12, NAVY)
    s.line(xs(MAXT), Y0 - 16, xs(MAXT), bottom, RED, 1.5, dash="5,4")
    col_head(s, xs(MAXT), Y0 - 20, f"PROPOSED MAXIMUM ${MAXT:.0f}M", anchor="middle", fill=RED)
    source(s, H, "Source: Spotrac contracts by total value, read October 27, 2026, nominal totals; maximum: AP, October 24, 2026.")
    s.write(stem)


fig_dodgers_stack(KEYS[0]); fig_all_30(KEYS[1]); fig_over_max(KEYS[2]); fig_over_265(KEYS[3])
print("done ->", OUT)
