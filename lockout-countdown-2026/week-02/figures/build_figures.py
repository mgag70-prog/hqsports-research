#!/usr/bin/env python3
"""Build the in-article charts for lockout-countdown-2026/week-02.

fig-01-2021-vs-2026-dollars: November 2021's committed free-agent dollars against reported 2026 dollars through November 10.
fig-02-top50-predictions: MLB Trade Rumors' top 50 predictions as a running total, Skubal's share in red, November 2021 as a line.
fig-03-calendar: the strip from November 11 to December 9.

Every number comes through model/recompute.py (which exits on any mismatch with the data or the draft) and
is asserted against draft.md and captions.md before any SVG is written. Writes SVG and a 1200px PNG.

Usage: build_figures.py [out_dir]
"""
import contextlib
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
MUTED, FAINT, GRID = "rgba(22,40,74,0.62)", "rgba(22,40,74,0.40)", "rgba(22,40,74,0.13)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-2021-vs-2026-dollars", "fig-02-top50-predictions", "fig-03-calendar")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R  # exits non-zero if any check fails
assert not R.fails
N21, KNOWN, T, SK, CROSS, DAYS = R.N21, R.known, R.T, R.SK, R.CROSS, R.DAYS
TOP = [(int(r["rank"]), r["player"], float(r["total_mm"])) for r in R.top]
assert (round(N21 / 1000, 1), KNOWN, round(T / 1000, 2), SK, CROSS, DAYS) == (1.7, 11.0, 2.38, 425.0, 19, 20)

draft, captions = R.norm(DRAFT.read_text()), R.norm(CAPTIONS.read_text())
for p in (f"is $11 million, {R.PCT21} of what clubs committed in November 2021", f"the first {CROSS} names on the list pass the 2021 total",
          f"Tarik Skubal is {R.SKP} of it on his own"):
    assert p in draft, f"draft no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print("draft and captions match the model; three slots exist")


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


def source(s, H, text):
    s.text(48, H - 14, text, 12, MUTED)


def fig_dollars(stem):
    title = f"November 2021: ${N21 / 1000:.1f} billion. November 2026 so far: ${KNOWN:.0f} million reported."
    sub = "Free-agent dollars committed before the lockout. 2026 counts reported terms only, through November 10."
    H = 360
    s = SVG(1200, H, title)
    header(s, title, sub)
    X0, X1, VMAX = 330, 1130, 1800
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for v in range(0, VMAX + 1, 300):
        s.line(xs(v), 128, xs(v), 286, GRID, 1)
        s.text(xs(v), 304, f"${v / 1000:.1f}B" if v else "$0", 11, MUTED, anchor="middle")
    rows = ((f"November 2021, committed", "CBS Sports count", N21, NAVY, f"${N21 / 1000:.1f}B"),
            ("November 2026, reported", "through November 10", KNOWN, RED, f"${KNOWN:.0f}M, {R.PCT21} of 2021: Pagán, one year"))
    for i, (l1, l2, v, fill, lab) in enumerate(rows):
        y = 142 + i * 74
        s.rect(X0, y, max(xs(v) - X0, 2), 46, fill)
        s.text(X0 - 14, y + 21, l1, 16, NAVY, anchor="end")
        s.text(X0 - 14, y + 40, l2, 13, MUTED, anchor="end")
        inside = xs(v) - X0 > 200
        s.text(xs(v) - 12 if inside else xs(v) + 10, y + 29, lab, 15, PAPER if inside else fill, anchor="end" if inside else "start")
    s.line(X0, 128, X0, 286, NAVY, 1.5)
    source(s, H, "Source: CBS Sports, December 2, 2021; MLB Trade Rumors, November 10, 2026. Signings without reported terms count as zero.")
    s.write(stem)


def fig_top50(stem):
    title = f"MLB Trade Rumors' predictions pass November 2021's total by No. {CROSS}."
    sub = f"Running total of the top 50 predicted contracts by rank, $ millions. Red: Tarik Skubal's ${SK:.0f}M, {R.SKP} of ${T / 1000:.2f}B."
    X0, X1, Y0, Y1, VMAX = 90, 1150, 130, 470, 2500
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 92
    s = SVG(1200, H, title)
    header(s, title, sub)
    for v in range(0, VMAX + 1, 500):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v:,}M", 11, MUTED, anchor="end")
    pitch = (X1 - X0) / len(TOP)
    bw = pitch * 0.7
    run = 0.0
    for rank, _, v in TOP:
        run += v
        bx = X0 + (rank - 1) * pitch + (pitch - bw) / 2
        s.rect(bx, ys(run), bw, ys(SK) - ys(run), NAVY if rank <= CROSS else FAINT)
        s.rect(bx, ys(SK), bw, Y1 - ys(SK), RED)
        if rank in (1, 10, CROSS, 30, 40, 50):
            s.text(bx + bw / 2, Y1 + 18, str(rank), 11, NAVY if rank == CROSS else MUTED, anchor="middle")
    s.line(X0, ys(N21), X1, ys(N21), NAVY, 1.5, dash="5,4")
    s.text(X0 + 8, ys(N21) - 8, f"NOVEMBER 2021, COMMITTED: ${N21 / 1000:.1f}B", 12, NAVY, spacing=1.6)
    s.text(X1, ys(T) - 10, f"All 50: ${T / 1000:.2f}B", 14, NAVY, anchor="end")
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    s.text(X0, Y1 + 36, "Rank on MLB Trade Rumors' top 50", 12, MUTED)
    s.text(48, Y1 + 58, "MLBTR predictions, November 2, for the whole offseason, not for the 20 days before the agreement expires.", 12, MUTED)
    source(s, H, "Source: MLB Trade Rumors, November 2, 2026; CBS Sports, December 2, 2021.")
    s.write(stem)


def fig_calendar(stem):
    title = f"{DAYS} days left: November 11 to the December 1 expiration."
    sub = "The signing window opened November 2; a lockout is expected December 2."
    D0, D1, END = date(2026, 11, 11), date(2026, 12, 9), date(2026, 12, 1)
    A0, A1 = 70, 1130
    span = (D1 - D0).days + 1
    xs = lambda d: A0 + (A1 - A0) * (d - D0).days / span
    xe = lambda d: A0 + (A1 - A0) * ((d - D0).days + 1) / span
    AX, H = 276, 470
    s = SVG(1200, H, title)
    header(s, title, sub)
    s.rect(xs(D0), AX - 26, xe(END) - xs(D0), 26, RED)
    s.text((xs(D0) + xe(END)) / 2, AX - 8, f"SIGNING WINDOW: {DAYS} DAYS LEFT", 13, PAPER, anchor="middle", spacing=1.8)
    lock0 = date(2026, 12, 2)
    s.rect(xs(lock0), AX - 26, xe(D1) - xs(lock0), 26, NAVY)
    s.text((xs(lock0) + xe(D1)) / 2, AX - 8, "LOCKOUT EXPECTED", 12, PAPER, anchor="middle", spacing=1.2)
    s.line(A0, AX, A1, AX, NAVY, 1.5)
    for i in range(span):
        d = date.fromordinal(D0.toordinal() + i)
        tall = d.weekday() == 0
        s.line(xs(d), AX, xs(d), AX + (10 if tall else 5), NAVY if tall else FAINT, 1)
        if tall:
            s.text(xs(d), AX + 24, d.strftime("%b ") + str(d.day), 12, MUTED, anchor="middle")
    above = (
        ((f"This piece: {DAYS} days left", "Nov 11"), date(2026, 11, 11), 86, "start"),
        (("Qualifying-offer deadline", f"Nov 17, ${R.V('qo_value'):.2f}M, eight players"), date(2026, 11, 17), 150, "start"),
        (("Non-tender deadline", "Nov 20"), date(2026, 11, 20), 86, "start"),
        (("Agreement expires", "Dec 1, 11:59 p.m. ET"), END, 150, "end"),
    )
    below = (
        (("Rule 5 protection", "Nov 17, 6 p.m. ET"), date(2026, 11, 17), None, 62, "start"),
        (("Winter Meetings, most expect cancellation", "Dec 7-9, San Diego"), date(2026, 12, 7), date(2026, 12, 9), 62, "end"),
    )
    for (l1, l2), a, up, anchor in above:
        x = (xs(a) + xe(a)) / 2
        top = AX - 26 - up + 36
        s.line(x, AX - 26, x, top, NAVY, 1)
        tx = x + 6 if anchor == "start" else x - 6
        s.text(tx, top + 11, l1, 14, NAVY, anchor=anchor)
        s.text(tx, top + 28, l2, 13, MUTED, anchor=anchor)
    for (l1, l2), a, b, down, anchor in below:
        x = xe(b) if anchor == "end" else (xs(a) + xe(a)) / 2
        s.line(x, AX, x, AX + down + 8, NAVY, 1)
        if b:
            s.rect(xs(a), AX + 1, xe(b) - xs(a), 6, NAVY)
        tx = x + 6 if anchor == "start" else x - 6
        s.text(tx, AX + down + 8, l1, 14, NAVY, anchor=anchor)
        s.text(tx, AX + down + 25, l2, 13, MUTED, anchor=anchor)
    source(s, H, "Source: Just Baseball, October 13, 2026; AP, November 2, 2026; ESPN, November 3, 2026.")
    s.write(stem)


fig_dollars(KEYS[0]); fig_top50(KEYS[1]); fig_calendar(KEYS[2])
print("done ->", OUT)
