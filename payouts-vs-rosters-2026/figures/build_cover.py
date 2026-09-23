#!/usr/bin/env python3
"""Cover concepts for payouts-vs-rosters-2026. 1200x630 on navy.

Concept A adapts fig-02: pairs of near-identical filed checks (off-white bars)
against estimated roster ranges (red ranges) on one dollar axis. A1 carries all
four pairs; A2 carries two.
Concept B adapts fig-05: three schools, full-width check bar against a small
roster range, ratio numeral large, caveat on the cover.

Every figure is recomputed from the live distributions CSV and the roster
budgets CSV and asserted against draft.md's tables and prose before rendering.

Concept A2 is the chosen cover. Concept B is kept reproducible but is not used:
at X card size its caveat line crops and the 100.7% reads as football taking the
whole check, the misreading the piece exists to prevent.

Usage: build_cover.py [out_dir] [--final] [--concept a1|a2|b]
  out_dir defaults to ./covers next to this script. --final renders A2 only, as
  cover-a-navy, into the script's own directory, and skips the feed and X previews.
"""
import csv
import io
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path("/Users/mattgray/code/hqsports-research")
ROSTER_CSV = REPO / "cfb-roster-budgets-2026/data/cfb-roster-budgets-2026.csv"
DRAFT = REPO / "payouts-vs-rosters-2026/draft.md"
REF_SVG = REPO / "cfb-roster-budgets-2026/figures/fig-02-top-eleven.svg"
CSV_URL = "https://www.gridironhq.ai/data/cfb-conference-distributions.csv"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
FINAL = "--final" in sys.argv
OUT = Path(args[0]) if args else (Path(__file__).parent if FINAL else Path(__file__).parent / "covers")
OUT.mkdir(parents=True, exist_ok=True)
CONCEPT = sys.argv[sys.argv.index("--concept") + 1] if "--concept" in sys.argv else None

NAVY, RED, PAPER, OFFWHITE = "#16284A", "#D4553D", "#F7F5F0", "#F2EEE6"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
W, H = 1200, 630

HEADLINE = "Miami and Duke got conference checks $14,349 apart. Miami's roster costs three times Duke's."
# Line breaks only; no words changed. Asserted below.
LINES = ["Miami and Duke got conference checks",
         "$14,349 apart. Miami's roster costs",
         "three times Duke's."]
assert " ".join(LINES) == HEADLINE
assert DRAFT.read_text().splitlines()[0] == f"# {HEADLINE}"

SOURCE = ("Source: Form 990 filings, fiscal years ending in 2025, via ProPublica (checks, exact); "
          "The Athletic, September 16, 2026 (roster budgets, estimated ranges; midpoints calculated).")
ALIAS = {"Pitt": "Pittsburgh", "Oklahoma St.": "Oklahoma State", "Michigan St.": "Michigan State",
         "Mississippi St.": "Mississippi State"}

# ---------------------------------------------------------------- data

with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
    dist_text = resp.read().decode("utf-8")
print("downloaded", CSV_URL)
dist = {}
with io.StringIO(dist_text) as fh:
    for r in csv.DictReader(fh):
        if r["season"] == "2024-25" and r["measure"] == "distribution":
            dist[r["school"]] = {"pay": int(r["amount"]), "share": r["share_type"], "conf": r["conference"]}
by = {}
with ROSTER_CSV.open() as fh:
    for r in csv.DictReader(fh):
        name = ALIAS.get(r["school"], r["school"])
        d = dist[name]
        lo, hi = int(r["budget_low_millions"]), int(r["budget_high_millions"])
        by[name] = {"school": name, "conf": d["conf"], "share": d["share"], "pay": d["pay"],
                    "lo": lo, "hi": hi, "mid": (lo + hi) / 2, "ratio": (lo + hi) / 2 * 1e6 / d["pay"]}


def money(n):
    return f"${n:,}"


def rng(r):
    return f"${r['lo']}-{r['hi']}M"


PAIRS = [("Miami", "Duke"), ("Arkansas", "LSU"), ("Texas Tech", "Colorado"), ("USC", "Purdue")]
pairs = []
for a, b in PAIRS:
    A, B = by[a], by[b]
    assert A["conf"] == B["conf"] and A["share"] == B["share"] == "full"
    pairs.append({"a": A, "b": B, "conf": A["conf"], "gap": abs(A["pay"] - B["pay"])})
B_SCHOOLS = ["Texas Tech", "Miami", "Boston College"]

# Assert against the draft: pairs table, Miami/Duke prose, and the ratio tables.
tables, cur = [], []
for line in DRAFT.read_text().splitlines():
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-"):
            continue
        cur.append(cells)
    elif cur:
        tables.append(cur)
        cur = []
t_pairs, t_top, t_bot = tables[0], tables[3], tables[4]
assert t_pairs[0] == ["Pair", "Conference", "Payouts", "Gap", "Roster budgets"]
for cells, p in zip(t_pairs[1:], pairs[1:]):
    want = [f"{p['a']['school']} and {p['b']['school']}", p["conf"],
            f"{money(p['a']['pay'])} and {money(p['b']['pay'])}", money(p["gap"]), f"{rng(p['a'])} and {rng(p['b'])}"]
    assert cells == want, (cells, want)
text = DRAFT.read_text()
md = pairs[0]
for phrase in (f"Miami received {money(md['a']['pay'])}", f"Duke received {money(md['b']['pay'])}",
               f"The gap is {money(md['gap'])}", f"is ${md['a']['lo']}-{md['a']['hi']} million",
               f"Duke's is ${md['b']['lo']}-{md['b']['hi']} million"):
    assert phrase in text, phrase
ratio_cells = {c[0]: c for c in t_top[1:] + t_bot[1:]}
for name in B_SCHOOLS:
    r = by[name]
    assert ratio_cells[name] == [name, r["conf"], rng(r), f"${r['mid']:.1f}M", money(r["pay"]), f"{r['ratio'] * 100:.1f}%"], name
print("cover data matches the draft's pairs table, Miami/Duke prose, and ratio tables")


# ---------------------------------------------------------------- svg

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cover:
    def __init__(self):
        self.ink = OFFWHITE
        self.muted = "rgba(242,238,230,0.62)"
        self.grid = "rgba(242,238,230,0.16)"
        self.est = "rgba(212,85,61,0.45)"
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                      f'font-family="{FONT}"><title>{esc(HEADLINE)}</title>{FONT_STYLE}',
                      f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']

    def text(self, x, y, s, size, fill=None, anchor="start", spacing=None, opacity=None):
        fill = fill or self.ink
        extra = "" if anchor == "start" else f' text-anchor="{anchor}"'
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None, rx=None):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        if rx:
            extra += f' rx="{rx}"'
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def eyebrow(self):
        self.text(56, 52, "LEDGER & WHISTLE", 15, RED, spacing=2.7)

    def headline(self):
        for i, line in enumerate(LINES):
            self.text(56, 104 + i * 45, line, 40)

    def filed_bar(self, x0, x1, y, h):
        self.rect(x0, y - h / 2, x1 - x0, h, self.ink, rx=3)

    def est_range(self, xlo, xhi, xmid, y, h):
        self.rect(xlo, y - h / 2, xhi - xlo, h, self.est, rx=3)
        self.rect(xlo, y - h / 2, 2, h, RED)
        self.rect(xhi - 2, y - h / 2, 2, h, RED)
        self.rect(xmid - 1, y - h / 2 - 3, 2, h + 6, RED)

    def key(self, y, x=56):
        """Two-item key in place of the in-article legend: the mark, then four words."""
        self.rect(x, y - 8, 22, 7, self.ink, rx=2)
        self.text(x + 30, y, "FILED CHECK, FORM 990", 12, self.muted, spacing=1.8)
        x2 = x + 30 + 200
        self.est_range(x2, x2 + 28, x2 + 16, y - 4.5, 7)
        self.text(x2 + 38, y, "ESTIMATED ROSTER RANGE, THE ATHLETIC", 12, "rgba(212,85,61,0.85)", spacing=1.8)

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


# ---------------------------------------------------------------- concept A: pairs on one axis

def concept_a(stem, which, row_h, bar_h, pair_gap, y0, name_size, num_size, key_y, caption):
    c = Cover()
    c.eyebrow()
    c.headline()
    X0, X1, VMAX = 250, 880, 80_000_000
    xv = lambda v: X0 + v / VMAX * (X1 - X0)
    c.key(key_y)
    y = y0
    for gi, p in enumerate(which):
        if gi:
            c.rect(56, y - pair_gap / 2, 1088, 1, c.grid)
        for r in (p["a"], p["b"]):
            yc = y + row_h / 2
            c.text(56, yc + name_size * 0.35, r["school"], name_size)
            c.filed_bar(X0, xv(r["pay"]), yc - bar_h * 0.75, bar_h)
            c.est_range(xv(r["lo"] * 1e6), xv(r["hi"] * 1e6), xv(r["mid"] * 1e6), yc + bar_h * 0.85, bar_h)
            c.text(900, yc + num_size * 0.35, money(r["pay"]), num_size)
            c.text(1144, yc + num_size * 0.35, rng(r), num_size, RED, anchor="end")
            y += row_h
        y += pair_gap
    c.text(56, 590, caption, 14, c.muted)
    c.text(56, 616, SOURCE, 12, c.muted)
    c.write(stem)


if CONCEPT in (None, "a1") and not FINAL:
    concept_a("cover-a1-navy", pairs, row_h=31, bar_h=8, pair_gap=12, y0=250, name_size=17, num_size=16, key_y=234,
              caption="Four pairs on the same conference contract. Off-white is the filed check; red is the estimated roster range, "
                      "tick at the midpoint. Full-share schools, 2024-25 checks against 2026 rosters.")
if CONCEPT in (None, "a2"):
    concept_a("cover-a-navy" if FINAL else "cover-a2-navy", pairs[:2], row_h=56, bar_h=13, pair_gap=32, y0=266, name_size=24, num_size=22, key_y=246,
              caption="Two pairs on the same conference contract. Off-white is the filed check; red is the estimated roster range, "
                      "tick at the midpoint. Full-share schools, 2024-25 checks against 2026 rosters.")


# ---------------------------------------------------------------- concept B: the ratio, three schools

def concept_b(stem):
    c = Cover()
    c.eyebrow()
    c.headline()
    X0, X1, VMAX = 300, 960, 80_000_000
    xv = lambda v: X0 + v / VMAX * (X1 - X0)
    c.key(246)
    y0, pitch, bar_h = 296, 84, 14
    for i, name in enumerate(B_SCHOOLS):
        r = by[name]
        y = y0 + i * pitch
        if i:
            c.rect(56, y - pitch / 2 + 4, 1088, 1, c.grid)
        c.text(56, y + 2, r["school"], 24)
        c.text(56, y + 24, f"{money(r['pay'])} check, {rng(r)} roster", 13, c.muted)
        c.filed_bar(X0, xv(r["pay"]), y - bar_h * 0.75, bar_h)
        c.est_range(xv(r["lo"] * 1e6), xv(r["hi"] * 1e6), xv(r["mid"] * 1e6), y + bar_h * 0.85, bar_h)
        c.text(1144, y + 14, f"{r['ratio'] * 100:.1f}%", 40, RED if r["ratio"] >= 1 else c.ink, anchor="end")
    c.text(56, 590, "Roster budget as a share of the conference check. The check funds every sport in the department; "
                    "the roster is football players only. A scale comparison, not a share of a budget.", 14, c.muted)
    c.text(56, 616, SOURCE, 12, c.muted)
    c.write(stem)


if CONCEPT in (None, "b") and not FINAL:
    concept_b("cover-b-navy")
print("done ->", OUT)
