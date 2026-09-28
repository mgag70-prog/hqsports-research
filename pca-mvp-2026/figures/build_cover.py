#!/usr/bin/env python3
"""Substack cover for pca-mvp-2026. 1200x630 on navy.

Adapted from fig-02: the same savings curve, drawn from the September 14 model's
run() at $9.0M per win and 100% capture, reduced to the two points that carry
the piece. His 2025 season (5.4 fWAR) sits on the zero line, where the extension
breaks even; his 2026 season (10.6) sits far up the curve. The 6.5 and 8.0
readings are left off; every value shown is unchanged from fig-02. No headline;
the Substack title carries it.

The model is imported from pca-extension-2026/model/ inside a temp directory,
because importing it runs a Monte Carlo that writes files to the working
directory. Values are asserted against the draft before rendering.

Font: rendered with rsvg-convert, which ignores the embedded Libre Caslon and
falls back to Georgia, matching mlb-1994-base-rate-2026.

Usage: build_cover.py [out_dir] [--previews]
  out_dir defaults to this script's directory. --previews also writes the
  600px feed and 506px X-card downsamples.
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
REF_SVG = REPO / "payouts-vs-rosters-2026/figures/cover-a-navy.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
PREVIEWS = "--previews" in sys.argv

NAVY, RED, OFFWHITE = "#16284A", "#D4553D", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

draft = DRAFT.read_text()
TITLE = draft.splitlines()[0].removeprefix("# ")
assert TITLE == "If Pete Crow-Armstrong were still the 2025 player, his extension would break even. He isn't."
EYEBROW = "PETE CROW-ARMSTRONG'S EXTENSION, BY TRUE TALENT"
DPW, CAPTURE = 9.0, 1.00
SEASONS = {2025: 5.4, 2026: 10.6}            # FanGraphs WAR, final

# ---------------------------------------------------------------- model

sys.path.insert(0, str(MODEL_DIR))
_cwd = os.getcwd()
os.chdir(tempfile.mkdtemp(prefix="pca_mvp_cover_"))
try:
    with contextlib.redirect_stdout(io.StringIO()):
        from pca_sensitivity import run
finally:
    os.chdir(_cwd)


def savings(t):
    return run(t, DPW, CAPTURE)[1]


lo, hi = 3.0, 8.0
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (lo, mid) if savings(mid) > 0 else (mid, hi)
BREAKEVEN = (lo + hi) / 2
S25, S26 = savings(SEASONS[2025]), savings(SEASONS[2026])

for phrase in (f"you get {BREAKEVEN:.3f} wins",
               f"the deal would be a wash, ${S25:.1f} million in the Cubs' favor",
               f"| 2026 taken at face value | {SEASONS[2026]} | ${S26:.1f}M |",
               f"| 2025 | {SEASONS[2025]} |", f"| 2026 | {SEASONS[2026]} |"):
    assert phrase in draft, f"draft no longer says: {phrase}"
print(f"cover values match the model and the draft: breakeven {BREAKEVEN:.3f}, "
      f"2025 ${S25:.1f}M, 2026 ${S26:.1f}M")

CAPTION = (f"Extension savings, present value to 2026, by true talent entering 2027 (FanGraphs WAR). "
           f"Zero at {BREAKEVEN:.3f}.")
SOURCE = ("Model: pca-extension-2026, run September 28, 2026, $9.0M per win, 100% free agent capture. "
          "WAR: FanGraphs, final.")

# ---------------------------------------------------------------- svg


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self):
        self.ink = OFFWHITE
        self.muted = "rgba(242,238,230,0.62)"
        self.grid = "rgba(242,238,230,0.22)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(TITLE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def poly(self, pts, stroke, sw):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                          f'stroke-linejoin="round" stroke-linecap="round"/>')

    def circle(self, cx, cy, r, fill, stroke=None, sw=0):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

    def frame(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)
        self.text(56, 100, EYEBROW, 20, self.muted, spacing=3)
        self.text(56, 590, CAPTION, 14, self.muted)
        self.text(56, 616, SOURCE, 12, self.muted)

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(W), str(svg), "-o", str(png)], check=True)
        for tag, w in (("feed", 600), ("x", 506)) if PREVIEWS else ():
            subprocess.run(["magick", str(png), "-resize", f"{w}x", str(OUT / f"{stem}-{tag}.png")], check=True)
        print("wrote", stem)


# ---------------------------------------------------------------- the cover

c = Cover()
c.frame()
X0, X1, T0, T1 = 110, 1110, 4.0, 11.0
Y0, Y1, VMIN, VMAX = 150, 540, -40, 160
xs = lambda t: X0 + (X1 - X0) * (t - T0) / (T1 - T0)
ys = lambda v: Y1 - (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)

# zero line, the only axis
c.line(X0, ys(0), X1, ys(0), c.grid, 1.5)
c.text(X0 - 12, ys(0) + 5, "$0", 16, c.muted, anchor="end")

# the curve, straight from run() at 0.05-win steps
n = int(round((T1 - T0) / 0.05))
c.poly([(xs(T0 + i * 0.05), ys(savings(T0 + i * 0.05))) for i in range(n + 1)], c.ink, 4)

# 2025: on the zero line, label block above it
x25, y25 = xs(SEASONS[2025]), ys(S25)
c.circle(x25, y25, 11, "none", stroke=RED, sw=3.5)
c.line(x25, 372, x25, y25 - 16, RED, 1.5, dash="2 5")
c.text(X0, 250, f"2025 · {SEASONS[2025]} fWAR", 24, RED)
c.text(X0, 322, f"${S25:.1f}M", 72, RED)
c.text(X0, 356, "roughly a wash", 20, c.muted)

# 2026: far up the curve, label block below it, right-aligned
x26, y26 = xs(SEASONS[2026]), ys(S26)
c.circle(x26, y26, 9, RED)
c.line(x26, y26 + 16, x26, 286, RED, 1.5, dash="2 5")
c.text(X1, 312, f"2026 · {SEASONS[2026]} fWAR", 24, RED, anchor="end")
c.text(X1, 384, f"${S26:.1f}M", 72, RED, anchor="end")
c.text(X1, 418, "2026 at face value, a ceiling", 20, c.muted, anchor="end")

c.write("cover-a-navy")
print("done ->", OUT)
