#!/usr/bin/env python3
"""Build the in-article charts for cbb-revenue-share-2026.

fig-01-share-paid: share of each conference's men's basketball roster paid any revenue share (four power conferences
                   and everyone else), labeled with the median rostered player.
fig-02-paid-range: among paid men's basketball players, the bottom-quarter, median, top-quarter and top-tenth lines
                   by conference, showing the SEC's high floor.

Every number comes through model/recompute.py (which exits on any mismatch with the data or the draft) and is
asserted against draft.md and captions.md before any SVG is written. Writes SVG and a 1200px PNG.

Usage: build_figures.py [out_dir]
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

NAVY, RED, PAPER = "#16284A", "#D4553D", "#F7F5F0"
NAVY_SOFT, RED_SOFT = "rgba(22,40,74,0.45)", "rgba(212,85,61,0.45)"
MUTED, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-share-paid", "fig-02-paid-range")
SOURCE = "Source: College Sports Commission, School Revenue Share Compensation Report, accessed November 17, 2026."

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R  # exits non-zero if any check fails
assert not R.fails
MBB, NON, SH = R.MBB, R.NON, R.SH
ORDER = ["Big 12 Conference", "Atlantic Coast Conference", "Big Ten Conference", "Southeastern Conference"]
ROWS = [(R.SH[c], R.n(MBB, c, "without_zero"), R.n(MBB, c, "with_zero"), R.p(MBB, c, "with_zero", "p50")) for c in ORDER]
ROWS.append(("Outside the four", R.n(MBB, NON, "without_zero"), R.n(MBB, NON, "with_zero"), R.p(MBB, NON, "with_zero", "p50")))
assert [(r[0], round(100 * r[1] / r[2], 1), r[3]) for r in ROWS] == [
    ("Big 12", 79.0, 100000), ("ACC", 61.2, 38000), ("Big Ten", 59.4, 48000), ("SEC", 45.1, 0), ("Outside the four", 62.8, 8500)]
PAID = {R.SH[c]: [R.p(MBB, c, "without_zero", k) for k in ("p25", "p50", "p75", "p90")] for c in ORDER}
assert PAID == {"Big 12": [54000, 150500, 350000, 662500], "ACC": [50000, 225000, 440000, 648000],
                "Big Ten": [80000, 187500, 397500, 559500], "SEC": [117500, 175000, 322000, 599500]}

draft, captions = R.norm(DRAFT.read_text()), R.norm(CAPTIONS.read_text())
for ph in ("The Big 12 paid 79.0% of its men's basketball players, 196 of 248", "The SEC paid 45.1%, 114 of 253",
           "roughly three in four paid SEC players got at least $117,500", "Outside them it was 62.8%, 2,303 of 3,667"):
    assert ph in draft, f"draft no longer says: {ph}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print("draft and captions match the model; two slots exist")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def money(v):
    return "$0" if v == 0 else f"${v:,}"


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", weight=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if weight:
            extra += f' font-weight="{weight}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill):
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def circle(self, x, y, r, fill, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="2"' if stroke else ""
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{extra}/>')

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(png)], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


def header(s, title, *subs):
    s.text(48, 46, title, 28)
    for i, sub in enumerate(subs):
        s.text(48, 76 + i * 22, sub, 17, MUTED)


def fig_share(stem):
    title = "The SEC paid fewer than half of its men's basketball players."
    sub = "Share of each roster paid any revenue share, July 1, 2025 to April 6, 2026. Right: the median rostered player."
    X0, X1, Y0, BH, GAP = 230, 900, 140, 44, 22
    H = Y0 + len(ROWS) * (BH + GAP) + 92
    s = SVG(1200, H, title)
    header(s, title, sub)
    xs = lambda v: X0 + (X1 - X0) * v / 100
    for v in range(0, 101, 25):
        s.line(xs(v), Y0 - 12, xs(v), H - 70, GRID, 1)
        s.text(xs(v), H - 52, f"{v}%", 11, MUTED, anchor="middle")
    s.line(xs(50), Y0 - 12, xs(50), H - 70, NAVY_SOFT, 1.2, dash="4 4")
    s.text(xs(50) + 6, Y0 - 16, "half the roster", 12, MUTED)
    s.text(1140, Y0 - 16, "Median player", 13, MUTED, anchor="end")
    for i, (name, paid, roster, med) in enumerate(ROWS):
        y = Y0 + i * (BH + GAP) + (14 if i == len(ROWS) - 1 else 0)
        sec = name == "SEC"
        other = i == len(ROWS) - 1
        fill = RED if sec else (NAVY_SOFT if other else NAVY)
        if other:
            s.line(48, y - 15, 1152, y - 15, GRID, 1)
        s.rect(X0, y, xs(100 * paid / roster) - X0, BH, fill)
        s.text(X0 - 14, y + BH / 2 + 6, name, 17, NAVY, anchor="end")
        s.text(xs(100 * paid / roster) - 10, y + BH / 2 - 1, f"{100 * paid / roster:.1f}%", 17, PAPER, anchor="end")
        s.text(xs(100 * paid / roster) - 10, y + BH / 2 + 15, f"{paid:,} of {roster:,}", 12, PAPER, anchor="end")
        s.text(1140, y + BH / 2 + 8, money(med), 22, RED if sec else NAVY, anchor="end")
    s.text(48, H - 30, "Counts are rostered players. Percentiles by conference, not totals.", 12, MUTED)
    s.text(48, H - 12, SOURCE, 12, MUTED)
    s.write(stem)


def fig_range(stem):
    title = "The SEC paid fewer players, but its paid floor is the highest of the four."
    sub = "Men's basketball players who got paid. Dots: bottom-quarter line, median, top-quarter line, top-tenth line."
    X0, X1, Y0, ROW, VMAX = 170, 1130, 170, 78, 700000
    H = Y0 + len(ORDER) * ROW + 70
    s = SVG(1200, H, title)
    header(s, title, sub)
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for v in range(0, VMAX + 1, 100000):
        s.line(xs(v), Y0 - 30, xs(v), Y0 + len(ORDER) * ROW - 30, GRID, 1)
        s.text(xs(v), Y0 + len(ORDER) * ROW - 12, "$0" if v == 0 else f"${v // 1000}K", 11, MUTED, anchor="middle")
    marks = ("Bottom quarter", "Median", "Top quarter", "Top tenth")
    for i, c in enumerate(ORDER):
        name = R.SH[c]
        vals = PAID[name]
        y = Y0 + i * ROW
        col = RED if name == "SEC" else NAVY
        s.text(X0 - 20, y + 6, name, 17, NAVY, anchor="end")
        s.line(xs(vals[0]), y, xs(vals[3]), y, RED_SOFT if name == "SEC" else NAVY_SOFT, 6)
        for j, v in enumerate(vals):
            s.circle(xs(v), y, 8 if j == 1 else 6, PAPER if j != 1 else col, stroke=col)
        s.text(xs(vals[0]), y + 26, money(vals[0]), 12, col, anchor="middle", weight="bold" if name == "SEC" else None)
        s.text(xs(vals[1]), y - 14, money(vals[1]), 12, col, anchor="middle")
        s.text(xs(vals[3]), y + 26, money(vals[3]), 12, col, anchor="middle")
        if i == 0:
            for j, v in enumerate(vals):
                s.text(xs(v), y - 38 if j != 1 else y - 30, marks[j], 11, MUTED, anchor="middle")
    s.text(48, H - 30, "Lines are percentiles of paid players by conference: about a quarter of paid players got the bottom-quarter line or less.", 12, MUTED)
    s.text(48, H - 12, SOURCE, 12, MUTED)
    s.write(stem)


fig_share(KEYS[0]); fig_range(KEYS[1])
print("done ->", OUT)
