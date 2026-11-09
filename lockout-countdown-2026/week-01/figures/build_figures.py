#!/usr/bin/env python3
"""Build the in-article charts for lockout-countdown-2026/week-01.

fig-01-2026-vs-2028-lines: all 30 clubs' 2026 tax payrolls against the 2028 cap, floor and 90% line.
fig-02-2027-vs-2028-lines: all 30 clubs' 2027 payrolls, signed solid and projected outlined, against the same lines.
fig-03-calendar: the strip from November 2 to December 9 with the 30-day signing window.

Every number comes through model/recompute.py (which fails on any mismatch with the data) and is
asserted against draft.md and captions.md before any SVG is written. Writes SVG and a 1200px PNG.

Usage: build_figures.py [out_dir]
"""
import contextlib
import csv
import io
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PIECE = Path(__file__).resolve().parents[1]
REPO = PIECE.parents[1]
DRAFT, CAPTIONS = PIECE / "draft.md", PIECE / "figures/captions.md"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

NAVY, RED, PAPER = "#16284A", "#D4553D", "#F7F5F0"
MUTED, FAINT, PALE, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.40)", "rgba(22,40,74,0.18)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-2026-vs-2028-lines", "fig-02-2027-vs-2028-lines", "fig-03-calendar")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.fails
CAP, FLOOR, F90 = R.CAP, R.FL, R.F90
PAY26 = R.pay26
P27 = {r["team"]: (float(r["signed_basis_m"]), float(r["projected_m"])) for r in R.b}
over26, under26 = set(R.new_over), set(R.new_under)
over27, under27 = R.proj_over, R.proj_under
signed_over27 = {t for t, _ in R.os27}
under90_27 = sum(1 for t in under27 if P27[t][1] < F90)
assert len(PAY26) == 30 and len(P27) == 30
assert (len(over26), len(under26), len(over27), len(under27), under90_27) == (8, 12, 7, 12, 9)
assert all(PAY26[t] < F90 for t in under26) and signed_over27 == {"LAD", "NYM", "NYY", "PHI"}
assert R.WINDOW == 30 and R.DAYS_LEFT == 26 and R.ctx["qo_count"]["value"] == "8" and R.ctx["qo_decisions"]["value"] == "November 17"
m1 = lambda v: f"${v:.1f} million"; m2 = lambda v: f"${v:.2f} million"

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
DRAFT_PHRASES = (
    f"Cubs and Padres, {m1(R.OVER)} above the line in all", f"Cleveland and Miami, {m1(R.UNDER)} below it",
    f"its {m2(PAY26['ATL'])} sits {m2(R.ATL_GAP)} below the new cap",
    f"put {len(over27)} clubs over the 2028 cap, {len(under27)} under the floor and {under90_27} under the 90% line",
    f"November 2nd to December 1st: {R.WINDOW} days, counting both ends",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"projected 2028 cap of {m1(CAP)}, floor of {m1(FLOOR)} and 90% line of {m2(F90)}",
    f"Eight clubs are over the cap, {m1(R.OVER)} in all; twelve are under the floor, {m1(R.UNDER)} in all, and all 12 are also under the 90% line",
    f"Atlanta, at {m2(PAY26['ATL'])}, is {m2(R.ATL_GAP)} under the cap",
    f"On projection, {len(over27)} clubs are over the cap, {len(under27)} are under the floor and {under90_27} are under the 90% line",
    f"the Dodgers project {m1(P27['LAD'][1] - CAP)} over",
    f"runs November 2 to December 1, {R.WINDOW} days counting both ends; on November 5, {R.DAYS_LEFT} days remain",
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
        subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(png)], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


def header(s, title, *subs):
    s.text(48, 46, title, 28)
    for i, sub in enumerate(subs):
        s.text(48, 76 + i * 22, sub, 17, MUTED)


def col_head(s, x, y, label, anchor="start", fill=MUTED):
    s.text(x, y, label, 12, fill, anchor=anchor, spacing=1.8)


def source(s, H, text):
    s.text(48, H - 14, text, 12, MUTED)


X0, X1, Y0, Y1, VMAX = 90, 1150, 130, 470, 450
ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
LINES = ((CAP, f"2028 CAP ${CAP:.1f}M", 6), (FLOOR, f"2028 FLOOR ${FLOOR:.1f}M", -6), (F90, f"90% LINE ${F90:.2f}M", 15))


def frame(s):
    for v in range(0, VMAX + 1, 50):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}M", 11, MUTED, anchor="end")


def draw_lines(s):
    for v, label, dy in LINES:
        dash = "5,4" if v != F90 else "2,3"
        s.line(X0, ys(v), X1, ys(v), RED if v != F90 else NAVY, 1.5, dash=dash)
    for v, label, dy in LINES:
        col_head(s, X1, ys(v) - 6 if dy == 6 else ys(v) + (dy if dy > 0 else -6), label, anchor="end", fill=RED if v != F90 else NAVY)
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)


def fig_2026(stem):
    title = "On 2026 payrolls, eight clubs top the 2028 cap and twelve miss the floor."
    sub = f"2026 luxury-tax payroll, $ millions, all 30 clubs, against the owners' projected 2028 lines. The same twelve missed the old floor."
    order = sorted(PAY26, key=lambda t: -PAY26[t])
    H = Y1 + 92
    s = SVG(1200, H, title)
    header(s, title, sub)
    frame(s)
    pitch = (X1 - X0) / 30
    bw = pitch * 0.66
    for i, t in enumerate(order):
        bx = X0 + i * pitch + (pitch - bw) / 2
        hit = t in over26 or t in under26
        s.rect(bx, ys(PAY26[t]), bw, Y1 - ys(PAY26[t]), RED if hit else (NAVY if t == "ATL" else FAINT))
        s.text(bx + bw / 2, Y1 + 16, t, 10, RED if hit else MUTED, anchor="middle")
    draw_lines(s)
    ax = X0 + order.index("ATL") * pitch + pitch / 2
    s.line(ax, ys(PAY26["ATL"]) - 6, ax, ys(312), NAVY, 1)
    s.text(ax - 2, ys(345), f"Atlanta, ${PAY26['ATL']:.2f}M: ${R.ATL_GAP:.2f}M under the new cap", 13, NAVY)
    s.text(ax - 2, ys(345) + 17, f"The only club that left the old list", 13, MUTED)
    s.text(48, Y1 + 44, f"Red: over the cap (${R.OVER:.1f}M in all) or under the floor (${R.UNDER:.1f}M in all). All 12 are also under the 90% line.", 12, MUTED)
    source(s, H, "Source: 2026 tax payrolls, Ledger & Whistle floor piece; lines: ESPN, November 3, 2026.")
    s.write(stem)


def fig_2027(stem):
    title = "On 2027 projections, seven clubs top the 2028 cap and twelve miss the floor."
    sub = "2027 luxury-tax payroll, $ millions, all 30 clubs, against the owners' projected 2028 lines. The names shift from 2026."
    order = sorted(P27, key=lambda t: -P27[t][1])
    H = Y1 + 108
    s = SVG(1200, H, title)
    header(s, title, sub)
    frame(s)
    pitch = (X1 - X0) / 30
    bw = pitch * 0.66
    for i, t in enumerate(order):
        signed, proj = P27[t]
        bx = X0 + i * pitch + (pitch - bw) / 2
        s.rect(bx, ys(signed), bw, Y1 - ys(signed), RED if t in signed_over27 else NAVY)
        if proj > signed:
            s.rect(bx, ys(proj), bw, ys(signed) - ys(proj), PAPER, stroke=NAVY, sw=1.2)
        s.text(bx + bw / 2, Y1 + 16, t, 10, RED if t in over27 or t in under27 else MUTED, anchor="middle")
    draw_lines(s)
    s.text(48, Y1 + 44, "Solid: signed contracts (red where they alone are over the cap: LAD, NYY, PHI, NYM). Outlined: Spotrac's projected arbitration and pre-arb salaries.", 12, MUTED)
    s.text(48, Y1 + 62, f"Red labels: the {len(over27)} clubs over the cap and the {len(under27)} under the floor on projection; {under90_27} of those are under the 90% line. Rosters are incomplete.", 12, MUTED)
    source(s, H, "Source: Spotrac 2027 projections, read October 27, 2026; lines: ESPN, November 3, 2026.")
    s.write(stem)


def fig_calendar(stem):
    title = f"The window to sign with a new club runs {R.WINDOW} days, November 2 to December 1."
    sub = f"Counting both ends. On November 5, {R.DAYS_LEFT} days remain until the agreement expires."
    D0, D1 = date(2026, 11, 2), date(2026, 12, 9)
    A0, A1 = 70, 1130
    span = (D1 - D0).days + 1
    xs = lambda d: A0 + (A1 - A0) * (d - D0).days / span
    xe = lambda d: A0 + (A1 - A0) * ((d - D0).days + 1) / span
    AX, H = 276, 470
    s = SVG(1200, H, title)
    header(s, title, sub)
    win1 = date(2026, 12, 1)
    s.rect(xs(D0), AX - 26, xe(win1) - xs(D0), 26, RED)
    s.text((xs(D0) + xe(win1)) / 2, AX - 8, f"{R.WINDOW}-DAY SIGNING WINDOW", 13, PAPER, anchor="middle", spacing=1.8)
    lock0 = date(2026, 12, 2)
    s.rect(xs(lock0), AX - 26, xe(D1) - xs(lock0), 26, NAVY)
    s.text((xs(lock0) + xe(D1)) / 2, AX - 8, "LOCKOUT EXPECTED", 12, PAPER, anchor="middle", spacing=1.2)
    s.line(A0, AX, A1, AX, NAVY, 1.5)
    d = D0
    for i in range(span):
        d = date.fromordinal(D0.toordinal() + i)
        tall = d.weekday() == 0
        s.line(xs(d), AX, xs(d), AX + (10 if tall else 5), NAVY if tall else FAINT, 1)
        if tall:
            s.text(xs(d), AX + 24, d.strftime("%b ") + str(d.day), 12, MUTED, anchor="middle")
    above = (  # label lines, first day, last day, height of the label above the bar
        (("Free agency opens", "Nov 2, 5 p.m. ET"), date(2026, 11, 2), None, 150, "start"),
        ((f"This piece: {R.DAYS_LEFT} days left", "Nov 5"), date(2026, 11, 5), None, 86, "start"),
        (("Qualifying-offer deadline", f"Nov 17, ${R.V('qo_value')}M, eight players"), date(2026, 11, 17), None, 150, "start"),
        (("Non-tender deadline", "Nov 20"), date(2026, 11, 20), None, 86, "start"),
        (("Agreement expires", "Dec 1, 11:59 p.m. ET"), win1, None, 150, "end"),
    )
    below = (
        (("GM Meetings", "Nov 9-12, Las Vegas"), date(2026, 11, 9), date(2026, 11, 12), 62, "start"),
        (("Rule 5 protection", "Nov 17, 6 p.m. ET"), date(2026, 11, 17), None, 62, "start"),
        (("Winter Meetings, most expect cancellation", "Dec 7-9, San Diego; Rule 5 draft at risk"), date(2026, 12, 7), date(2026, 12, 9), 62, "end"),
    )
    for (l1, l2), a, b, up, anchor in above:
        x = (xs(a) + xe(a)) / 2
        top = AX - 26 - up + 36
        s.line(x, AX - 26, x, top, NAVY, 1)
        if b:
            s.rect(xs(a), AX - 26 - 6, xe(b) - xs(a), 6, NAVY)
        tx = x + 6 if anchor == "start" else x - 6
        s.text(tx, top + 11, l1, 14, NAVY, anchor=anchor)
        s.text(tx, top + 28, l2, 13, MUTED, anchor=anchor)
    for (l1, l2), a, b, down, anchor in below:
        x = xe(b) if anchor == "end" else ((xs(a) + xe(b)) / 2 if b else (xs(a) + xe(a)) / 2)
        s.line(x, AX, x, AX + down + 8, NAVY, 1)
        if b:
            s.rect(xs(a), AX + 1, xe(b) - xs(a), 6, NAVY)
        tx = x + 6 if anchor == "start" else x - 6
        s.text(tx, AX + down + 8, l1, 14, NAVY, anchor=anchor)
        s.text(tx, AX + down + 25, l2, 13, MUTED, anchor=anchor)
    source(s, H, "Source: Just Baseball, October 13, 2026; NBC Sports, October 30, 2026; AP, November 2, 2026; ESPN, November 3, 2026.")
    s.write(stem)


fig_2026(KEYS[0]); fig_2027(KEYS[1]); fig_calendar(KEYS[2])
print("done ->", OUT)
