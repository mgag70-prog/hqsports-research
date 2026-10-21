#!/usr/bin/env python3
"""Build the in-article charts for mlb-floor-2026.

fig-01-final-four: the four LCS clubs' 2026 tax payrolls against the proposed cap and floor.
fig-02-all-30: all 30 clubs sorted by tax payroll, cap and floor lines, the final four in red.
fig-03-wins-vs-payroll: wins against tax payroll, cap and floor as vertical lines, playoff clubs filled.
fig-04-change-to-comply: what each club would cut or add to sit inside the lines, diverging bars.

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
KEYS = ("fig-01-final-four", "fig-02-all-30", "fig-03-wins-vs-payroll", "fig-04-change-to-comply")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.fails
print(f"model: all checks pass; {len(R.rows)} clubs")
CAP, FLOOR, rows, by = R.CAP, R.FLOOR, R.rows, R.by
FOUR = ("LAD", "MIL", "TB", "CLE")
NAMES = {"LAD": "Dodgers", "MIL": "Brewers", "TB": "Rays", "CLE": "Guardians", "NYM": "Mets", "STL": "Cardinals",
         "MIA": "Marlins", "HOU": "Astros", "CHW": "White Sox"}
cut, add = R.cut, R.add
under = lambda t: FLOOR - by[t]["tax_payroll_m"]
over = lambda t: by[t]["tax_payroll_m"] - CAP
fm = lambda v: f"${v:.1f} million"
fp = lambda t: f"${by[t]['tax_payroll_m']:.2f} million"

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
DRAFT_PHRASES = (
    f"a cap of {fm(CAP)} and a floor of {fm(FLOOR)}",
    f"The Dodgers spent {fp('LAD')}, the most in baseball, {fm(over('LAD'))} over the cap",
    f"spent {fp('MIL')}, 19th of 30, {fm(under('MIL'))} under the floor",
    f"The Rays spent {fp('TB')}, 27th, {fm(under('TB'))} under it; the Guardians {fp('CLE')}, 29th, {fm(under('CLE'))} under",
    f"cut {fm(cut)} and the twelve under the floor would add {fm(add)}, so players as a group would be paid {fm(cut - add)} less",
    f"The nine over-cap clubs averaged {R.w_over:.1f} wins; the twelve under the floor averaged {R.w_under:.1f}",
    f"{fp('NYM')}, a 74-88 record",
    "the Rays, Cardinals, Guardians and Marlins", f"add {fm(under('TB'))}, {fm(under('STL'))}, {fm(under('CLE'))} and {fm(under('MIA'))}",
    "Under the floor. In the World Series.",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"cap of {fm(CAP)} and floor of {fm(FLOOR)}",
    f"The Dodgers, {fp('LAD')}, were {fm(over('LAD'))} over the cap; the Brewers, {fp('MIL')}, were {fm(under('MIL'))} under the floor; the Rays, {fp('TB')}, {fm(under('TB'))} under; the Guardians, {fp('CLE')}, {fm(under('CLE'))} under",
    "Nine clubs were over the cap, twelve under the floor and nine between", "the Brewers rank 19th and the Guardians 29th",
    f"would cut {fm(cut)} from the nine over the cap and add {fm(add)} at the twelve under the floor, {fm(cut - add)} less for players in all",
    f"The nine over-cap clubs averaged {R.w_over:.1f} wins and the twelve under-floor clubs {R.w_under:.1f}",
    f"The Mets, {fp('NYM')} and 74-88", f"Cuts, in red, total {fm(cut)} across nine clubs, {fm(over('LAD'))} of it the Dodgers'",
    f"the Marlins at {fm(under('MIA'))}, the Guardians at {fm(under('CLE'))}, the Cardinals at {fm(under('STL'))} and the Rays at {fm(under('TB'))}",
    f"The Brewers' addition is {fm(under('MIL'))}",
)
for p in CAPTION_PHRASES:
    assert p in captions, f"captions.md no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
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

    def rect(self, x, y, w, h, fill, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def circle(self, x, y, r, fill, stroke=None, sw=1.5):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{extra}/>')

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


def lines_source(s, H):
    s.text(48, H - 14, "Source: Spotrac team tax tracker, end of the 2026 regular season, read October 19, 2026, including player benefits; cap and floor: CBS Sports, May 28, 2026. 2027 lines over 2026 payrolls.", 12, MUTED)


def fig_final_four(stem):
    title = f"Three of the final four were under the floor. The Dodgers were ${over('LAD'):.1f}M over the cap."
    sub1 = f"2026 luxury-tax payroll, $ millions, of the four LCS clubs, against the owners' proposed 2027 cap (${CAP:.1f}M) and floor (${FLOOR:.1f}M)."
    X0, X1, VMAX = 230, 1050, 450
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 150, 66, 40
    H = Y0 + PITCH * 4 + 78
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 50):
        s.line(xs(v), Y0 - 16, xs(v), Y0 + PITCH * 4 - 20, GRID, 1)
        s.text(xs(v), Y0 + PITCH * 4 - 2, f"${v}M", 11, MUTED, anchor="middle")
    assert all(by[t]["status"] == "under floor" for t in ("MIL", "TB", "CLE")) and by["LAD"]["status"] == "over cap"
    for i, t in enumerate(FOUR):
        y = Y0 + i * PITCH
        p, w, l = by[t]["tax_payroll_m"], by[t]["wins"], by[t]["losses"]
        col = RED if t == "LAD" else NAVY
        s.text(X0 - 16, y + 18, NAMES[t], 17, NAVY, anchor="end")
        s.text(X0 - 16, y + 36, f"{w}-{l}, payroll rank {by[t]['payroll_rank']}", 12, MUTED, anchor="end")
        s.rect(X0, y, xs(p) - X0, BH, col)
        if t == "LAD":   # the bar runs nearly to the edge, so its label sits inside it
            s.text(xs(p) - 12, y + 26, f"${p:.2f}M, ${over(t):.1f}M over the cap", 14, PAPER, anchor="end")
        else:
            s.text(xs(p) + 10, y + 26, f"${p:.2f}M, ${under(t):.1f}M under the floor", 14, col)
    for v, label in ((FLOOR, f"FLOOR ${FLOOR:.1f}M"), (CAP, f"CAP ${CAP:.1f}M")):
        s.line(xs(v), Y0 - 22, xs(v), Y0 + PITCH * 4 - 20, RED, 1.5, dash="5,4")
        col_head(s, xs(v), Y0 - 28, label, anchor="middle", fill=RED)
    lines_source(s, H)
    s.write(stem)


def fig_all_30(stem):
    title = "Nine clubs over the cap, twelve under the floor, both pennant winners among the twelve."
    sub1 = f"2026 luxury-tax payroll, $ millions, all 30 clubs, against the proposed 2027 cap (${CAP:.1f}M) and floor (${FLOOR:.1f}M). The four LCS clubs in red."
    assert len(R.over) == 9 and len(R.under) == 12 and len([x for x in rows if x["status"] == "inside"]) == 9
    X0, X1, Y0, Y1, VMAX = 90, 1150, 130, 460, 450
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 92
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 50):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}M", 11, MUTED, anchor="end")
    pitch = (X1 - X0) / 30
    BW = pitch * 0.66
    for i, x in enumerate(rows):
        t = x["team"]
        col = RED if t in FOUR else (NAVY if x["status"] == "over cap" else (FAINT if x["status"] == "inside" else PALE))
        bx = X0 + i * pitch + (pitch - BW) / 2
        s.rect(bx, ys(x["tax_payroll_m"]), BW, Y1 - ys(x["tax_payroll_m"]), col)
        s.text(bx + BW / 2, Y1 + 16, t, 10, RED if t in FOUR else MUTED, anchor="middle")
    for v, label in ((CAP, f"CAP ${CAP:.1f}M"), (FLOOR, f"FLOOR ${FLOOR:.1f}M")):
        s.line(X0, ys(v), X1, ys(v), RED, 1.5, dash="5,4")
        col_head(s, X1, ys(v) - 6, label, anchor="end", fill=RED)
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    s.text(48, Y1 + 46, f"Over the cap, navy: nine clubs, ${cut:.1f}M above it in all. Between the lines, gray: nine. Under the floor, pale: twelve, ${add:.1f}M below it in all. Net, ${cut - add:.1f}M less for players if every club moved inside.", 12, MUTED)
    lines_source(s, H)
    s.write(stem)


def fig_wins_vs_payroll(stem):
    title = f"Over the cap, {R.w_over:.1f} wins on average. Under the floor, {R.w_under:.1f}, and the best record in baseball."
    sub1 = "Regular-season wins against 2026 luxury-tax payroll, $ millions, all 30 clubs. Filled points made the postseason; the four LCS clubs in red."
    X0, X1, Y0, Y1 = 110, 1140, 120, 470
    PMIN, PMAX, WMIN, WMAX = 50, 450, 55, 105
    xs = lambda v: X0 + (X1 - X0) * (v - PMIN) / (PMAX - PMIN)
    ys = lambda w: Y1 - (Y1 - Y0) * (w - WMIN) / (WMAX - WMIN)
    H = Y1 + 94
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for w in range(60, WMAX + 1, 10):
        s.line(X0, ys(w), X1, ys(w), GRID, 1)
        s.text(X0 - 10, ys(w) + 4, str(w), 11, MUTED, anchor="end")
    for v in range(100, PMAX + 1, 50):
        s.text(xs(v), Y1 + 18, f"${v}M", 11, MUTED, anchor="middle")
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    col_head(s, X0 - 10, Y0 - 12, "WINS", anchor="end")
    for v, label in ((FLOOR, f"FLOOR ${FLOOR:.1f}M"), (CAP, f"CAP ${CAP:.1f}M")):
        s.line(xs(v), Y0 - 6, xs(v), Y1, RED, 1.5, dash="5,4")
        col_head(s, xs(v), Y0 - 12, label, anchor="middle", fill=RED)
    assert by["MIL"]["wins_rank"] == 1 and by["LAD"]["wins_rank"] == 2 and by["TB"]["wins_rank"] == 3
    labels = {"MIL": (10, -10), "TB": (10, -10), "CLE": (12, 40), "LAD": (-10, -10), "NYM": (-10, 18)}
    for x in rows:
        t, p, w = x["team"], x["tax_payroll_m"], x["wins"]
        four = t in FOUR
        if x["postseason"]:
            s.circle(xs(p), ys(w), 7, RED if four else NAVY)
        else:
            s.circle(xs(p), ys(w), 6, PAPER, stroke=MUTED)
        if t in labels:
            dx, dy = labels[t]
            s.text(xs(p) + dx, ys(w) + dy + (4 if dy > 0 else 0), f"{NAMES[t]} {w}-{x['losses']}, ${p:.2f}M", 13,
                   RED if four else NAVY, anchor="start" if dx > 0 else "end")
    s.text(48, Y1 + 48, "Postseason: twelve clubs; seven over the cap, four under the floor (Brewers, Rays, Guardians, White Sox), one between (Astros). Series results: CBS Sports bracket, October 18, 2026.", 12, MUTED)
    lines_source(s, H)
    s.write(stem)


def fig_change_to_comply(stem):
    title = f"To fit the lines, nine clubs cut ${cut:.1f}M and twelve add ${add:.1f}M. Players net ${cut - add:.1f}M less."
    sub1 = "What each club would have cut (red, left) or added (navy, right) in 2026 to sit inside the proposed 2027 cap and floor, $ millions."
    moving = [x for x in rows if x["status"] != "inside"]
    moving.sort(key=lambda x: x["change_to_comply_m"])
    assert len(moving) == 21 and abs(sum(-x["change_to_comply_m"] for x in moving if x["change_to_comply_m"] < 0) - cut) < 0.05
    assert abs(sum(x["change_to_comply_m"] for x in moving if x["change_to_comply_m"] > 0) - add) < 0.05
    X0, X1, VMIN, VMAX = 120, 1100, -200, 100
    xs = lambda v: X0 + (X1 - X0) * (v - VMIN) / (VMAX - VMIN)
    Y0, PITCH, BH = 118, 24, 16
    H = Y0 + PITCH * len(moving) + 84
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(VMIN, VMAX + 1, 50):
        s.line(xs(v), Y0 - 8, xs(v), Y0 + PITCH * len(moving), GRID, 1)
        s.text(xs(v), Y0 + PITCH * len(moving) + 16, f"{'-' if v < 0 else '+' if v > 0 else ''}${abs(v)}M", 11, MUTED, anchor="middle")
    for i, x in enumerate(moving):
        y = Y0 + i * PITCH
        v, t = x["change_to_comply_m"], x["team"]
        col = RED if v < 0 else NAVY
        s.rect(min(xs(0), xs(v)), y, abs(xs(v) - xs(0)), BH, col)
        name = NAMES.get(t, t)
        s.text(xs(0) + (10 if v < 0 else -10), y + 13, name, 12, NAVY, anchor="start" if v < 0 else "end")
        s.text(xs(v) + (-8 if v < 0 else 8), y + 13, f"{'-' if v < 0 else '+'}${abs(v):.1f}M", 12, col, anchor="end" if v < 0 else "start")
    s.line(xs(0), Y0 - 8, xs(0), Y0 + PITCH * len(moving), NAVY, 1.5)
    s.text(xs(-100), Y0 - 16, f"NINE CLUBS CUT ${cut:.1f}M", 12, RED, anchor="middle", spacing=1.8)
    s.text(xs(50), Y0 - 16, f"TWELVE CLUBS ADD ${add:.1f}M", 12, NAVY, anchor="middle", spacing=1.8)
    lines_source(s, H)
    s.write(stem)


fig_final_four(KEYS[0]); fig_all_30(KEYS[1]); fig_wins_vs_payroll(KEYS[2]); fig_change_to_comply(KEYS[3])
print("done ->", OUT)
