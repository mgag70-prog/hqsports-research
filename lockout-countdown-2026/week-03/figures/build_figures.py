#!/usr/bin/env python3
"""Build the in-article charts for lockout-countdown-2026/week-03.

fig-01-payrolls: all 30 clubs' 2026 luxury-tax payrolls, sorted, Dodgers and Marlins labeled, Brewers in red at No. 19.
fig-02-leagues:  the widest payroll spread each league's rules allow (NFL, NBA with and without the second apron, NHL)
                 against MLB's actual top-to-bottom 5.13.

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
REPO = PIECE.parents[1]
DRAFT, CAPTIONS = PIECE / "draft.md", PIECE / "figures/captions.md"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

NAVY, RED, PAPER = "#16284A", "#D4553D", "#F7F5F0"
NAVY_SOFT = "rgba(22,40,74,0.45)"
MUTED, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-payrolls", "fig-02-leagues")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R  # exits non-zero if any check fails
assert not R.fails
P, RATIO, MED, MIL_RANK = R.P, R.RATIO, R.MED, R.MIL_RANK
assert (P[0], P[-1], RATIO, round(MED, 1), MIL_RANK) == ((433.06, "LAD"), (84.36, "MIA"), 5.13, 210.4, 19)
LEAGUES = [("NFL", "cap over cash floor", R.NFL), ("NBA", "cap over minimum", R.NBA),
           ("NBA", "second apron over minimum", R.NBA2), ("NHL", "upper over lower limit", R.NHL)]
assert [x[2] for x in LEAGUES] == [1.11, 1.11, 1.49, 1.35]

draft, captions = R.norm(DRAFT.read_text()), R.norm(CAPTIONS.read_text())
for ph in ("That's 5.13 times as much, a gap of $348.7 million", "won the World Series with the No. 19 payroll",
           "1.35 times", "1.49 times the minimum", "which puts the rule at 1.11 times"):
    assert ph in draft, f"draft no longer says: {ph}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print("draft and captions match the model; two slots exist")

SOURCE1 = "Source: Spotrac 2026 luxury-tax payrolls, including $18 million of benefits per club, via Ledger & Whistle's floor piece."
SOURCE2 = "Source: NFL-NFLPA CBA Art. 12 Sec. 9(b); Pro Football Rumors, Feb. 27, 2026; NBA, June 30, 2026; NHL, May 6, 2026; Spotrac."
NAMES = {"LAD": "Dodgers", "MIA": "Marlins", "MIL": "Brewers"}
LABEL_AT = {"MIL": 168, "MIA": 132}   # $M heights clear of the neighbouring bars the label spans


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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


def fig_payrolls(stem):
    title = "The Dodgers spent 5.13 times what the Marlins did."
    sub = "2026 luxury-tax payroll, all 30 clubs, $ millions. Red: the World Series champion Brewers, No. 19."
    X0, X1, Y0, Y1, VMAX = 70, 1150, 130, 560, 450
    H = Y1 + 70
    s = SVG(1200, H, title)
    header(s, title, sub)
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    for v in range(0, VMAX + 1, 100):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}", 12, MUTED, anchor="end")
    s.line(X0, ys(MED), X1, ys(MED), NAVY_SOFT, 1.2, dash="4 4")
    s.text(X1, ys(MED) - 6, f"Median ${MED:.1f} million", 13, MUTED, anchor="end")
    step = (X1 - X0) / len(P)
    for i, (pay, team) in enumerate(P):
        x = X0 + i * step + 3
        fill = RED if team == "MIL" else NAVY
        s.rect(x, ys(pay), step - 6, Y1 - ys(pay), fill)
        s.text(x + (step - 6) / 2, Y1 + 16, team, 10, MUTED, anchor="middle")
        if team in NAMES:   # labels sit above the shorter bars beside them: Dodgers over its own bar, the other two raised
            label = f"{NAMES[team]} ${pay:.2f}M"
            if team == "LAD":
                s.text(x, ys(pay) - 8, label, 13, fill, weight="bold")
            else:
                ly = ys(LABEL_AT[team])
                s.line(x + (step - 6) / 2, ys(pay) - 3, x + (step - 6) / 2, ly + 4, fill, 1)
                s.text(x if team == "MIL" else x + step - 6, ly, label, 13, fill, anchor="start" if team == "MIL" else "end", weight="bold")
    s.text(48, H - 30, "Spread: top over bottom, not a total. Payrolls include benefits, as the luxury tax counts them.", 12, MUTED)
    s.text(48, H - 12, SOURCE1, 12, MUTED)
    s.write(stem)


def fig_leagues(stem):
    title = "No other league's rules allow a spread near baseball's."
    sub = "Highest allowed payroll over lowest required, by each league's current rules. MLB: actual 2026 top over bottom."
    X0, X1, Y0, BH, GAP, VMAX = 330, 1100, 140, 46, 20, 6
    rows = LEAGUES + [("MLB", "Dodgers over Marlins, actual", RATIO)]
    H = Y0 + len(rows) * (BH + GAP) + 96
    s = SVG(1200, H, title)
    header(s, title, sub)
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for v in range(0, VMAX + 1):
        s.line(xs(v), Y0 - 12, xs(v), H - 82, GRID, 1)
        s.text(xs(v), H - 64, f"{v}x", 11, MUTED, anchor="middle")
    s.line(xs(1), Y0 - 12, xs(1), H - 82, NAVY_SOFT, 1.2, dash="4 4")
    s.text(xs(1) + 6, Y0 - 16, "1x: every club equal", 12, MUTED)
    for i, (lg, what, r) in enumerate(rows):
        mlb = lg == "MLB"
        y = Y0 + i * (BH + GAP) + (14 if mlb else 0)
        if mlb:
            s.line(48, y - 17, 1152, y - 17, GRID, 1)
        s.rect(X0, y, xs(r) - X0, BH, RED if mlb else NAVY)
        s.text(X0 - 14, y + BH / 2 - 2, lg, 18, NAVY, anchor="end", weight="bold")
        s.text(X0 - 14, y + BH / 2 + 16, what, 12, MUTED, anchor="end")
        s.text(xs(r) + 10, y + BH / 2 + 7, f"{r:.2f}x", 20, RED if mlb else NAVY)
    s.text(48, H - 40, "League ratios are rule limits, not what clubs spent. The NFL floor is 90% of the caps in cash over 2024-2026; the NBA cap is soft.", 12, MUTED)
    s.text(48, H - 22, SOURCE2, 12, MUTED)
    s.write(stem)


fig_payrolls(KEYS[0]); fig_leagues(KEYS[1])
print("done ->", OUT)
