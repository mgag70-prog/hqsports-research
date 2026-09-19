#!/usr/bin/env python3
"""Cover concepts for big-ten-spending-2026, adapted from fig-02a.

Every rank, record, budget, and gap is recomputed from the records CSV with the
shared-rank rule and asserted against the draft's first table before rendering.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
CSV = REPO / "big-ten-spending-2026/data/big-ten-records-2024-2025.csv"
DRAFT = REPO / "big-ten-spending-2026/draft.md"
REF_SVG = REPO / "cfb-roster-budgets-2026/figures/fig-02-top-eleven.svg"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "covers"
OUT.mkdir(parents=True, exist_ok=True)

NAVY, RED, PAPER, OFFWHITE = "#16284A", "#D4553D", "#F7F5F0", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

HEADLINE = ("In the Big Ten, money explains the top three teams and the bottom one. "
            "For the other fourteen it explains nothing.")
# Line breaks only; no words changed. Asserted below.
LINES_WIDE = ["In the Big Ten, money explains the top three teams",
              "and the bottom one. For the other fourteen",
              "it explains nothing."]
LINES_NARROW = ["In the Big Ten, money",
                "explains the top three teams",
                "and the bottom one.",
                "For the other fourteen",
                "it explains nothing."]
assert " ".join(LINES_WIDE) == HEADLINE and " ".join(LINES_NARROW) == HEADLINE

SOURCE = "Source: The Athletic, September 16, 2026 (budgets); Sports Reference, 2024 and 2025 (records). Ranks and gaps calculated."

# ---------------------------------------------------------------- data

def comp_rank(vals):
    s = sorted(vals, reverse=True)
    return [s.index(v) + 1 for v in vals], [s.count(v) > 1 for v in vals]


rows = []
with CSV.open() as fh:
    for r in csv.DictReader(fh):
        rows.append({"team": r["school"], "w": int(r["wins_2yr"]), "l": int(r["losses_2yr"]),
                     "lo": int(r["budget_low_millions"]), "hi": int(r["budget_high_millions"]),
                     "mid": float(r["budget_mid_millions"])})
rr, rt = comp_rank([r["w"] / (r["w"] + r["l"]) for r in rows])
br, bt = comp_rank([r["mid"] for r in rows])
for r, a, at, c, ct in zip(rows, rr, rt, br, bt):
    r.update({"rec_rank": a, "rec_lbl": f"T{a}" if at else str(a),
              "bud_rank": c, "bud_lbl": f"T{c}" if ct else str(c),
              "gap": c - a, "record": f'{r["w"]}-{r["l"]}', "budget": f'${r["lo"]}-{r["hi"]}M'})
by = {r["team"]: r for r in rows}
ordered = sorted(rows, key=lambda r: (r["rec_rank"], r["team"]))

# Assert against the draft's first table (rank, team, record, budget, payroll rank).
tbl = []
for line in DRAFT.read_text().splitlines():
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-") or cells[0] == "#":
            continue
        tbl.append(cells)
    elif tbl:
        break
assert len(tbl) == 18
for cells, r in zip(tbl, ordered):
    want = [r["rec_lbl"], r["team"], r["record"], cells[3], r["budget"], r["bud_lbl"]]
    assert cells == want, f"{cells} vs {want}"
print("cover data matches the draft's section 2 table, 18 rows")

KEY = ["Indiana", "Oregon", "Ohio State", "Illinois", "Iowa", "Minnesota", "Purdue"]
omitted = [r["team"] for r in ordered if r["team"] not in KEY]
assert len(omitted) == 11


def gap_label(g):
    return "0" if g == 0 else f"{g:+d}"


# ---------------------------------------------------------------- svg

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self, ground):
        self.dark = ground == "navy"
        self.bg = NAVY if self.dark else PAPER
        self.ink = PAPER if self.dark else NAVY
        base = "247,245,240" if self.dark else "22,40,74"
        self.muted = f"rgba({base},0.62)"
        self.grid = f"rgba({base},0.16)"
        self.connect = f"rgba({base},0.38)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(HEADLINE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{self.bg}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None, opacity=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def circle(self, cx, cy, r, fill, stroke=None, sw=0, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

    def dashed(self, x1, x2, y):
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{self.ink}" '
                          f'stroke-width="1.5" stroke-dasharray="3 6" opacity="0.5"/>')

    def eyebrow(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)

    def dumbbell(self, y, r, rx, dot=7, num=16, ghost=False, neg_right=False):
        op = 0.3 if ghost else None
        xa, xb = rx(r["rec_rank"]), rx(r["bud_rank"])
        if xa != xb:
            self.rect(min(xa, xb), y - 1.5, abs(xb - xa), 3, self.connect, opacity=op)
        if r["gap"] != 0:
            self.circle(xa, y, dot, self.ink, opacity=op)
        elif not ghost:
            self.circle(xb, y, dot + 4.5, "none", self.ink, 2.5)
        self.circle(xb, y, dot + 2, self.bg)
        self.circle(xb, y, dot, RED, opacity=op)
        if ghost:
            return
        lbl = gap_label(r["gap"])
        if r["gap"] > 0:
            self.text(xb + dot + 8, y + num * 0.36, lbl, num)
        elif r["gap"] < 0 and neg_right:
            self.text(xa + dot + 8, y + num * 0.36, lbl, num)
        elif r["gap"] < 0:
            self.text(xb - dot - 8, y + num * 0.36, lbl, num, anchor="end")
        else:
            self.text(xb + dot + 12, y + num * 0.36, lbl, num)

    def legend(self, x, y):
        self.circle(x + 6, y - 5, 6, self.ink)
        self.text(x + 18, y, "record rank", 14, self.muted)
        self.circle(x + 118, y - 5, 6, RED)
        self.text(x + 130, y, "payroll rank", 14, self.muted)
        self.text(x + 236, y, "number: payroll rank minus record rank", 14, self.muted)

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(W), str(svg), "-o", str(png)], check=True)
        if not FINAL:
            for tag, w in (("feed", 600), ("x", 506)):
                subprocess.run(["magick", str(png), "-resize", f"{w}x", str(OUT / f"{stem}-{tag}.png")], check=True)
        print("wrote", stem)


# ---------------------------------------------------------------- concept A: seven rows under the headline

def concept_a(ground):
    c = Cover(ground)
    c.eyebrow()
    for i, line in enumerate(LINES_WIDE):
        c.text(56, 104 + i * 45, line, 40)
    X1, X18 = 560, 1000
    rx = lambda rank: X1 + (rank - 1) * (X18 - X1) / 17
    y0, pitch = 262, 37
    ys = {}
    seq = [by[t] for t in KEY]
    for i, r in enumerate(seq):
        y = y0 + i * pitch + (28 if r["team"] == "Purdue" else 0)
        ys[r["team"]] = y
    y_top, y_bot = y0 - 20, ys["Purdue"] + 20
    for t in (1, 5, 10, 15, 18):
        c.rect(rx(t) - 0.5, y_top, 1, y_bot - y_top, c.grid)
        c.text(rx(t), y_bot + 18, str(t), 13, c.muted, anchor="middle")
    c.text(56, y_top - 6, "RANK", 12, c.muted, spacing=1.8)
    c.text(X1, y_top - 6, "RECORD RANK AGAINST PAYROLL RANK, 1 TO 18", 12, c.muted, spacing=1.8)
    c.text(1144, y_top - 6, "BUDGET", 12, c.muted, spacing=1.8, anchor="end")
    for r in seq:
        y = ys[r["team"]]
        c.text(56, y + 7, r["rec_lbl"], 18)
        c.text(104, y + 7, r["team"], 22)
        c.text(262, y + 7, r["record"], 18, c.muted)
        c.dumbbell(y, r, rx)
        c.text(1144, y + 7, r["budget"], 18, anchor="end")
    ye = (ys["Minnesota"] + ys["Purdue"]) / 2
    c.dashed(56, 1144, ye)
    c.rect(300, ye - 9, 600, 18, c.bg)
    c.text(600, ye + 4, "eleven of the eighteen not shown; every rank and position is unchanged", 13, c.muted, anchor="middle")
    c.legend(56, 590)
    c.text(56, 616, SOURCE, 12, c.muted)
    c.write(f"cover-a-{ground}")


# ---------------------------------------------------------------- concept B: headline left, all eighteen as a spine

def concept_b(ground):
    c = Cover(ground)
    c.eyebrow()
    for i, line in enumerate(LINES_NARROW):
        c.text(56, 104 + i * 45, line, 40)
    X1, X18 = 790, 1130
    rx = lambda rank: X1 + (rank - 1) * (X18 - X1) / 17
    y0, pitch = 74, 25.5
    y_of = lambda i: y0 + i * pitch
    y_top, y_bot = y0 - 14, y_of(17) + 14
    for t in (1, 5, 10, 15, 18):
        c.rect(rx(t) - 0.5, y_top, 1, y_bot - y_top, c.grid)
        c.text(rx(t), y_bot + 18, str(t), 13, c.muted, anchor="middle")
    c.text(1144, y_bot + 40, "ALL EIGHTEEN PROGRAMS, SEVEN NAMED", 12, c.muted, spacing=1.8, anchor="end")
    for i, r in enumerate(ordered):
        y = y_of(i)
        key = r["team"] in KEY
        c.dumbbell(y, r, rx, dot=5.5, num=14, ghost=not key, neg_right=True)
        if key:
            c.text(770, y + 5, f'{r["team"]}  {r["rec_lbl"]}', 15, anchor="end")
    c.legend(56, 590)
    c.text(56, 616, SOURCE, 12, c.muted)
    c.write(f"cover-b-{ground}")


FINAL = "--final" in sys.argv  # finals: concept A on navy only, no feed or X previews
if FINAL:
    concept_a("navy")
else:
    for g in ("navy", "paper"):
        concept_a(g)
        concept_b(g)
print("done ->", OUT)
