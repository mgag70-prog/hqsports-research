#!/usr/bin/env python3
"""Build the in-article charts for pca-mvp-award-2026.

fig-01-pay-stack: Crow-Armstrong's 2026 pay (salary, signing bonus, pool estimate split into award and WAR share)
                  against his 2027 salary.
fig-02-pool: the pre-arbitration bonus pool now ($50M, 2025 award money shaded), MLB's offer and the union's ask.

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
KEYS = ("fig-01-pay-stack", "fig-02-pool")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R  # exits non-zero if any check fails
assert not R.fails
SAL, BONUS, EST, AWARD, S27 = R.SAL, R.BONUS, R.EST, R.AWARD, R.S27
POOL, OFFER, ASK, AW25 = R.POOL, R.OFFER, R.ASK, R.AW25
WAR = round(EST - AWARD, 2)
TOTAL = round(SAL + BONUS + EST, 2)
assert (SAL, BONUS, EST, AWARD, WAR, TOTAL, S27) == (0.894, 5.0, 3.56, 2.5, 1.06, 9.45, 10.0)
assert (POOL, OFFER, ASK, AW25) == (50.0, 65.0, 180.0, 12.75)

draft, captions = R.norm(DRAFT.read_text()), R.norm(CAPTIONS.read_text())
for p in ("his 2026 pay comes to about $9.45 million", "Next year his salary alone is $10 million",
          "MLB's November 3 offer raised it to $65 million", "the union's counter is $180 million",
          "Clubs paid $12.75 million in award bonuses in 2025, 25.5% of the $50 million"):
    assert p in draft, f"draft no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print("draft and captions match the model; two slots exist")


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


def fig_pay(stem):
    title = f"An MVP season for ${SAL * 1000:,.0f},000 in salary, about ${TOTAL:.2f} million in all."
    sub = "Crow-Armstrong's 2026 pay beside his 2027 salary. Red is the pool payout, North Side Baseball's estimate."
    H = 420
    s = SVG(1200, H, title)
    header(s, title, sub)
    X0, X1, VMAX = 250, 1140, 11
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    for v in range(0, VMAX + 1):
        s.line(xs(v), 150, xs(v), 340, GRID, 1)
        s.text(xs(v), 358, f"${v}M" if v else "$0", 11, MUTED, anchor="middle")
    # 2026 row: salary, signing bonus, MVP award, WAR share (estimate)
    y, bh = 172, 58
    segs = ((SAL, NAVY, "Salary", f"${SAL * 1000:,.0f}K"),
            (BONUS, NAVY_SOFT, "Signing bonus", f"${BONUS:.0f}M"),
            (AWARD, RED, "MVP award, pool", f"${AWARD}M"),
            (WAR, RED_SOFT, "WAR", f"~${WAR:.2f}M"))
    left = 0.0
    for i, (v, fill, label, amount) in enumerate(segs):
        x0, x1 = xs(left), xs(left + v)
        s.rect(x0, y, x1 - x0, bh, fill)
        mid = (x0 + x1) / 2
        if i == 0:   # too narrow to label inside: label above, left-aligned
            s.text(x0 + 6, y - 22, label, 13, NAVY)
            s.text(x0 + 6, y - 7, amount, 13, MUTED)
        else:
            s.text(mid, y + bh / 2 - 3, label, 13, PAPER, anchor="middle")
            s.text(mid, y + bh / 2 + 15, amount, 13, PAPER, anchor="middle")
        left += v
    s.text(xs(TOTAL) + 10, y + bh / 2 + 6, f"${TOTAL:.2f}M", 16, NAVY)
    s.text(X0 - 14, y + 26, "2026", 17, NAVY, anchor="end")
    s.text(X0 - 14, y + 46, "paid and estimated", 13, MUTED, anchor="end")
    # pool bracket under the red segments
    px0, px1 = xs(SAL + BONUS), xs(SAL + BONUS + EST)
    s.line(px0, y + bh + 6, px1, y + bh + 6, RED, 1.5)
    s.text((px0 + px1) / 2, y + bh + 22, f"Pool estimate ${EST:.2f}M", 12, RED, anchor="middle")
    # 2027 row
    y2 = 272
    s.rect(X0, y2, xs(S27) - X0, bh, NAVY)
    s.text(xs(S27) - 12, y2 + bh / 2 + 6, f"${S27:.0f}M, {S27 / SAL:.1f} times his 2026 salary", 15, PAPER, anchor="end")
    s.text(X0 - 14, y2 + 26, "2027", 17, NAVY, anchor="end")
    s.text(X0 - 14, y2 + 46, "salary", 13, MUTED, anchor="end")
    s.line(X0, 150, X0, 340, NAVY, 1.5)
    s.text(48, H - 36, "A small 2026 playoff share is not counted. The pool estimate stands until MLB releases the final list.", 12, MUTED)
    source(s, H, "Source: North Side Baseball, November 5, 2026; AP via ESPN, July 24, 2026; ESPN, November 12, 2026.")
    s.write(stem)


def fig_pool(stem):
    title = f"The pre-arbitration pool: ${POOL:.0f} million now, ${OFFER:.0f} million offered, ${ASK:.0f} million asked."
    sub = f"$ millions. In red: the ${AW25} million clubs paid in award bonuses in 2025, {100 * AW25 / POOL:.1f}% of the pool."
    X0, X1, Y0, Y1, VMAX = 110, 1150, 140, 470, 200
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 80
    s = SVG(1200, H, title)
    header(s, title, sub)
    for v in range(0, VMAX + 1, 50):
        s.line(X0, ys(v), X1, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}M", 11, MUTED, anchor="end")
    bars = ((POOL, NAVY, "Current agreement", "since 2022"),
            (OFFER, NAVY_SOFT, "MLB offer", f"November 3, {round(100 * (OFFER / POOL - 1))}% more"),
            (ASK, NAVY, "Union counter", f"{ASK / POOL:.1f} times the current pool"))
    pitch = (X1 - X0) / len(bars)
    bw = pitch * 0.46
    for i, (v, fill, l1, l2) in enumerate(bars):
        bx = X0 + i * pitch + (pitch - bw) / 2
        s.rect(bx, ys(v), bw, Y1 - ys(v), fill)
        if i == 0:
            s.rect(bx, ys(AW25), bw, Y1 - ys(AW25), RED)
            s.text(bx + bw + 10, ys(AW25 / 2) + 4, f"2025 award money ${AW25}M", 12, RED)
        s.text(bx + bw / 2, ys(v) - 10, f"${v:.0f}M", 18, NAVY, anchor="middle")
        s.text(bx + bw / 2, Y1 + 22, l1, 15, NAVY, anchor="middle")
        s.text(bx + bw / 2, Y1 + 40, l2, 12, MUTED, anchor="middle")
    s.line(X0, Y1, X1, Y1, NAVY, 1.5)
    source(s, H, "Source: ESPN, November 3, 2026; AP via ESPN, July 24, 2026.")
    s.write(stem)


fig_pay(KEYS[0]); fig_pool(KEYS[1])
print("done ->", OUT)
