#!/usr/bin/env python3
"""Build the five in-article charts for big-ten-spending-2026.

Every number is recomputed from the records CSV with the shared-rank rule and
asserted against the markdown tables in draft.md before any SVG is written.
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
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "drafts"
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv  # finals: variant A only, no 700px previews

NAVY = "#16284A"
RED = "#D4553D"
PAPER = "#F7F5F0"
OFFWHITE = "#F2EEE6"
MUTED = "rgba(22,40,74,0.62)"
GRID = "rgba(22,40,74,0.13)"
CONNECT = "rgba(22,40,74,0.30)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)

SOURCE_LINE = ("Source: The Athletic, September 16, 2026 (budgets); Sports Reference, 2024 and 2025 seasons "
               "(records). Ranks and gaps calculated. A rank marked T is shared.")

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

def comp_rank(vals, higher_better=True):
    """Shared (competition) ranks: ties take the best rank, next rank skipped."""
    s = sorted(vals, reverse=higher_better)
    ranks = [s.index(v) + 1 for v in vals]
    tied = [s.count(v) > 1 for v in vals]
    return ranks, tied


def rank_label(r, tied):
    return f"T{r}" if tied else str(r)


def gap_label(g):
    return "0" if g == 0 else f"{g:+d}"


def pct(w, l):
    return f"{w / (w + l):.3f}"[1:]  # ".931"


rows = []
with CSV.open() as fh:
    for r in csv.DictReader(fh):
        rows.append({
            "team": r["school"],
            "w": int(r["wins_2yr"]), "l": int(r["losses_2yr"]),
            "pw": int(r["p4_wins"]), "pl": int(r["p4_losses"]),
            "lo": int(r["budget_low_millions"]), "hi": int(r["budget_high_millions"]),
            "mid": float(r["budget_mid_millions"]),
        })

wp = [r["w"] / (r["w"] + r["l"]) for r in rows]
pp = [r["pw"] / (r["pw"] + r["pl"]) for r in rows]
rr, rt = comp_rank(wp)
pr, pt = comp_rank(pp)
br, bt = comp_rank([r["mid"] for r in rows])
for r, a, at, b, bt_, c, ct in zip(rows, rr, rt, pr, pt, br, bt):
    r.update({
        "rec_rank": a, "rec_tied": at, "rec_lbl": rank_label(a, at),
        "p4_rank": b, "p4_tied": bt_, "p4_lbl": rank_label(b, bt_),
        "bud_rank": c, "bud_tied": ct, "bud_lbl": rank_label(c, ct),
        "gap_rec": c - a, "gap_p4": c - b,
        "record": f'{r["w"]}-{r["l"]}', "p4_record": f'{r["pw"]}-{r["pl"]}',
        "win_pct": pct(r["w"], r["l"]), "p4_pct": pct(r["pw"], r["pl"]),
        "budget": f'${r["lo"]}-{r["hi"]}M',
    })
by = {r["team"]: r for r in rows}
by_rec = sorted(rows, key=lambda r: (r["rec_rank"], r["team"]))
by_p4 = sorted(rows, key=lambda r: (r["p4_rank"], r["team"]))

# --------------------------------------------------------------------------
# Assert against the draft
# --------------------------------------------------------------------------

def draft_tables():
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
    if cur:
        tables.append(cur)
    return tables


T = draft_tables()
assert len(T) == 5, f"expected 5 tables in draft, found {len(T)}"
t_overall, t_p4, t_over, t_under, t_fired = T
assert t_overall[0] == ["#", "Team", "2-yr", "Win%", "Budget", "Payroll rank"], t_overall[0]
assert t_p4[0] == ["#", "Team", "P4 record", "P4 win%", "Payroll rank", "Gap"], t_p4[0]
assert t_over[0] == t_under[0] == ["Team", "Record rank", "P4 rank", "Payroll rank", "Gap (record)", "Gap (P4)"]
assert t_fired[0] == ["Program", "Payroll rank", "Record rank", "What happened"]

for cells, r in zip(t_overall[1:], by_rec):
    want = [r["rec_lbl"], r["team"], r["record"], r["win_pct"], r["budget"], r["bud_lbl"]]
    assert cells == want, f"overall table mismatch: draft {cells} vs computed {want}"
for cells, r in zip(t_p4[1:], by_p4):
    want = [r["p4_lbl"], r["team"], r["p4_record"], r["p4_pct"], r["bud_lbl"], gap_label(r["gap_p4"])]
    assert cells == want, f"P4 table mismatch: draft {cells} vs computed {want}"
for tbl in (t_over, t_under):
    for cells in tbl[1:]:
        r = by[cells[0]]
        want = [r["team"], r["rec_lbl"], r["p4_lbl"], r["bud_lbl"], gap_label(r["gap_rec"]), gap_label(r["gap_p4"])]
        assert cells == want, f"gap table mismatch: draft {cells} vs computed {want}"
fired = []
for cells in t_fired[1:]:
    r = by[cells[0]]
    assert [cells[1], cells[2]] == [r["bud_lbl"], r["rec_lbl"]], f"firings table mismatch {cells}"
    fired.append((r, cells[3]))
over_teams = [c[0] for c in t_over[1:]]
under_teams = [c[0] for c in t_under[1:]]

# Facts quoted on chart 5's ghosted rows, checked against the draft text.
draft_text = DRAFT.read_text()
for phrase in ("Purdue, Iowa, and Minnesota, the three cheapest rosters in the conference, all kept their coaches",
               "tied for sixth and tied for eighth",
               "Michigan parted with Sherrone Moore for cause",
               "Purdue kept Barry Odom after his first season in 2025",
               "Iowa and Minnesota kept Ferentz and Fleck"):
    assert phrase in draft_text, f"draft no longer says: {phrase}"
cheapest = sorted(rows, key=lambda r: r["bud_rank"])[-3:]
assert {r["team"] for r in cheapest} == {"Purdue", "Iowa", "Minnesota"}
print("draft tables match recomputation: 18 + 18 + 3 + 6 + 3 rows")

# --------------------------------------------------------------------------
# SVG helpers
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                          f'viewBox="0 0 {w} {h}" font-family="{FONT}">')
        self.parts.append(f"<title>{esc(title)}</title>{FONT_STYLE}")
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, opacity=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, opacity=None):
        extra = f' opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
        png = OUT / f"{stem}.png"
        subprocess.run(["rsvg-convert", "-w", str(self.w), str(svg), "-o", str(png)], check=True)
        if not FINAL:
            small = OUT / f"{stem}-700.png"
            subprocess.run(["magick", str(png), "-resize", "700x", str(small)], check=True)
        print("wrote", svg.name, png.name, f"({self.w}x{self.h})")


# Shared rank axis
X_RANK1, X_RANK18 = 440, 880
PX_PER_RANK = (X_RANK18 - X_RANK1) / 17


def rx(rank):
    return X_RANK1 + (rank - 1) * PX_PER_RANK


def header(s, title, subtitle):
    s.text(48, 46, title, 28)
    s.text(48, 76, subtitle, 17, MUTED)


def col_head(s, x, y, label, anchor="start"):
    s.text(x, y, label, 12, MUTED, anchor=anchor, spacing=1.8)


def rank_axis(s, y_top, y_bottom, y_label, ticks=(1, 5, 10, 15, 18)):
    for t in ticks:
        s.rect(rx(t) - 0.5, y_top, 1, y_bottom - y_top, GRID)
        s.text(rx(t), y_label, str(t), 13, MUTED, anchor="middle")


def dumbbell(s, y, rec_rank, bud_rank, gap, show_navy=True, ghost=False, from_x=None):
    """Navy dot = record rank, red dot = payroll rank, numeral = gap."""
    op = 0.45 if ghost else None
    xa = rx(rec_rank) if from_x is None else from_x
    xb = rx(bud_rank)
    if xa != xb:
        s.rect(min(xa, xb), y - 1.5, abs(xb - xa), 3, CONNECT, opacity=op)
    if show_navy and gap != 0:
        s.circle(xa, y, 7, NAVY, opacity=op)
    if gap == 0 and show_navy:
        s.circle(xb, y, 11.5, "none", NAVY, 2.5, opacity=op)  # ring: ranks coincide
    s.circle(xb, y, 9, PAPER)
    s.circle(xb, y, 7, RED, opacity=op)
    lbl = gap_label(gap)
    if gap > 0:
        s.text(xb + 14, y + 6, lbl, 16, NAVY, opacity=op)
    elif gap < 0:
        s.text(xb - 14, y + 6, lbl, 16, NAVY, anchor="end", opacity=op)
    else:
        s.text(xb + 18, y + 6, lbl, 16, NAVY, opacity=op)


def legend(s, y, show_navy=True, rec_label="record rank", show_match=True):
    x = 48
    if show_navy:
        s.circle(x + 6, y - 4, 6, NAVY)
        s.text(x + 18, y, rec_label, 13, MUTED)
        x += 18 + int(len(rec_label) * 6.6) + 26
    s.circle(x + 6, y - 4, 6, RED)
    s.text(x + 18, y, "payroll rank", 13, MUTED)
    x += 122
    if show_navy and show_match:
        s.circle(x + 6, y - 4, 6, RED)
        s.circle(x + 6, y - 4, 9.5, "none", NAVY, 2)
        s.text(x + 20, y, "ranks match", 13, MUTED)
        x += 124
    s.text(x, y, f"number: payroll rank minus {rec_label}; positive means the team finished higher than it spent", 13, MUTED)


def tie_brackets(s, ordered, key_rank, key_lbl, y_of, x_label=48, x_br=88):
    """Rank label per row; tied groups get one label and a bracket spanning the rows."""
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1][key_rank] == ordered[i][key_rank]:
            j += 1
        if j > i:
            ya, yb = y_of(i), y_of(j)
            s.text(x_label, (ya + yb) / 2 + 7, ordered[i][key_lbl], 19)
            s.rect(x_br, ya - 12, 2, (yb - ya) + 24, NAVY)
            s.rect(x_br, ya - 12, 8, 2, NAVY)
            s.rect(x_br, yb + 10, 8, 2, NAVY)
        else:
            s.text(x_label, y_of(i) + 7, ordered[i][key_lbl], 19)
        i = j + 1


# --------------------------------------------------------------------------
# Charts 1 and 2: the 18-row tables
# --------------------------------------------------------------------------

def eighteen_rows(stem, title, subtitle, ordered, rank_key, lbl_key, rec_key, pct_key, gap_key,
                  rec_head, show_navy=True, rec_label="record rank"):
    RH, Y0 = 42, 146
    n = len(ordered)
    y_last = Y0 + (n - 1) * RH
    y_axis_lbl = y_last + 46
    y_legend = y_axis_lbl + 34
    H = y_legend + 40
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 104, "RANK")
    col_head(s, 104, 104, "TEAM")
    col_head(s, 266, 104, rec_head)
    if show_navy:
        col_head(s, X_RANK1, 104, "RANK AXIS, 1 (BEST) TO 18")
    else:
        col_head(s, X_RANK1, 104, "PAYROLL RANK, 1 TO 18. DOTTED LINE IS " + rec_head.split(",")[0].replace(" RECORD", "") + " RECORD RANK")
    col_head(s, 936, 104, "BUDGET")
    col_head(s, 1152, 104, "PAYROLL RANK", anchor="end")
    rank_axis(s, 118, y_last + 24, y_axis_lbl)
    y_of = lambda i: Y0 + i * RH
    if not show_navy:
        s.line(rx(ordered[0][rank_key]), y_of(0), rx(ordered[-1][rank_key]), y_of(n - 1), NAVY, 1.5,
               dash="4 5", opacity=0.45)
    tie_brackets(s, ordered, rank_key, lbl_key, y_of)
    for i, r in enumerate(ordered):
        y = y_of(i)
        s.text(104, y + 7, r["team"], 21)
        s.text(266, y + 7, r[rec_key], 19)
        s.text(340, y + 7, r[pct_key], 16, MUTED)
        dumbbell(s, y, r[rank_key], r["bud_rank"], r[gap_key], show_navy=show_navy)
        s.text(936, y + 7, r["budget"], 19)
        s.text(1152, y + 7, r["bud_lbl"], 19, anchor="end")
    legend(s, y_legend, show_navy, rec_label=rec_label)
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


eighteen_rows(
    "fig-02a-overall-record",
    "Two-year record against payroll rank, all 18",
    "2024 and 2025 combined, bowls and playoffs included. Rows ordered by record; red is where the payroll ranks.",
    by_rec, "rec_rank", "rec_lbl", "record", "win_pct", "gap_rec", "2-YR RECORD, WIN%")
if not FINAL: eighteen_rows(
    "fig-02a-overall-record-nonavy",
    "Two-year record against payroll rank, all 18",
    "2024 and 2025 combined, bowls and playoffs included. Rows ordered by record; red is where the payroll ranks.",
    by_rec, "rec_rank", "rec_lbl", "record", "win_pct", "gap_rec", "2-YR RECORD, WIN%", show_navy=False)
eighteen_rows(
    "fig-02b-power4-record",
    "The same two years, Power 4 games only",
    "ACC, Big Ten, Big 12, SEC, and Notre Dame opponents, title games and playoffs included. Rows ordered by Power 4 record.",
    by_p4, "p4_rank", "p4_lbl", "p4_record", "p4_pct", "gap_p4", "P4 RECORD, WIN%", rec_label="Power 4 record rank")
if not FINAL: eighteen_rows(
    "fig-02b-power4-record-nonavy",
    "The same two years, Power 4 games only",
    "ACC, Big Ten, Big 12, SEC, and Notre Dame opponents, title games and playoffs included. Rows ordered by Power 4 record.",
    by_p4, "p4_rank", "p4_lbl", "p4_record", "p4_pct", "gap_p4", "P4 RECORD, WIN%", show_navy=False, rec_label="Power 4 record rank")

# --------------------------------------------------------------------------
# Charts 3 and 4: over- and underperformers, two rows per team
# --------------------------------------------------------------------------

def gap_chart(stem, title, subtitle, teams):
    RH, GAP, Y0 = 30, 22, 150
    group_h = 2 * RH + GAP
    n = len(teams)
    y_last = Y0 + (n - 1) * group_h + RH
    y_axis_lbl = y_last + 44
    y_legend = y_axis_lbl + 34
    H = y_legend + 40
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 104, "TEAM")
    col_head(s, 268, 104, "CUT")
    col_head(s, X_RANK1, 104, "RANK AXIS, 1 TO 18")
    col_head(s, 916, 104, "RECORD RANK")
    col_head(s, 1040, 104, "PAYROLL")
    col_head(s, 1152, 104, "GAP", anchor="end")
    rank_axis(s, 118, y_last + 22, y_axis_lbl)
    for gi, name in enumerate(teams):
        r = by[name]
        y1 = Y0 + gi * group_h
        y2 = y1 + RH
        s.text(48, (y1 + y2) / 2 + 7, r["team"], 21)
        if gi:
            s.rect(48, y1 - RH / 2 - GAP / 2, 1104, 1, GRID)
        for y, cut, rk, lbl, gap in ((y1, "Overall", r["rec_rank"], r["rec_lbl"], r["gap_rec"]),
                                     (y2, "Power 4", r["p4_rank"], r["p4_lbl"], r["gap_p4"])):
            s.text(268, y + 5, cut, 14, MUTED)
            dumbbell(s, y, rk, r["bud_rank"], gap)
            s.text(916, y + 6, lbl, 17)
            s.text(1040, y + 6, r["bud_lbl"], 17)
            s.text(1152, y + 6, gap_label(gap), 17, anchor="end")
    legend(s, y_legend, show_match=False)
    s.text(48, H - 14, SOURCE_LINE, 12, MUTED)
    s.write(stem)


gap_chart("fig-04-overperformers",
          "The programs that beat their payroll",
          "Three of the four cheapest rosters in the Big Ten. Payroll rank minus record rank, on both cuts of the data.",
          over_teams)
gap_chart("fig-05-underperformers",
          "The programs that lose to their payroll",
          "Same gap, other direction. Negative means the team finished lower than it spent.",
          under_teams)

# --------------------------------------------------------------------------
# Chart 5: the firings, with the three cheapest programs ghosted beneath
# --------------------------------------------------------------------------

def firings_chart(stem):
    title = "The firings came from the middle"
    subtitle = "Three performance firings out of 2025, and the three cheapest rosters, which all kept their coaches."
    RH, Y0 = 74, 168
    kept = [(by["Purdue"], "Kept Barry Odom. 3-21, 18th in the conference."),
            (by["Iowa"], "Kept Kirk Ferentz. 17-9, tied for sixth."),
            (by["Minnesota"], "Kept P.J. Fleck. 16-10, tied for eighth.")]
    SECTION_GAP = 44
    y_kept0 = Y0 + 3 * RH + SECTION_GAP
    y_last = y_kept0 + 2 * RH
    y_axis_lbl = y_last + 62
    y_legend = y_axis_lbl + 34
    H = y_legend + 40
    s = SVG(1200, H, title)
    header(s, title, subtitle)
    col_head(s, 48, 104, "PROGRAM")
    col_head(s, X_RANK1, 104, "RANK AXIS, 1 TO 18")
    col_head(s, 1000, 104, "PAYROLL")
    col_head(s, 1152, 104, "RECORD", anchor="end")
    rank_axis(s, 118, y_last + 40, y_axis_lbl)

    def section(label, y):
        s.rect(48, y, 1104, 1, GRID)
        s.text(48, y + 20, label, 12, RED if "FIRED" in label else MUTED, spacing=1.8)

    section("FIRED FOR PERFORMANCE. MICHIGAN'S CHANGE WAS FOR CAUSE AND IS EXCLUDED", Y0 - 44)
    for i, (r, what) in enumerate(fired):
        y = Y0 + i * RH
        s.text(48, y + 7, r["team"], 21)
        dumbbell(s, y, r["rec_rank"], r["bud_rank"], r["gap_rec"])
        s.text(1000, y + 7, r["bud_lbl"], 19)
        s.text(1152, y + 7, r["rec_lbl"], 19, anchor="end")
        s.text(48, y + 32, what, 15, MUTED)
    section("KEPT THEIR COACHES: THE THREE CHEAPEST ROSTERS", y_kept0 - 44)
    for i, (r, what) in enumerate(kept):
        y = y_kept0 + i * RH
        s.text(48, y + 7, r["team"], 21, NAVY, opacity=0.55)
        dumbbell(s, y, r["rec_rank"], r["bud_rank"], r["gap_rec"], ghost=True)
        s.text(1000, y + 7, r["bud_lbl"], 19, NAVY, opacity=0.55)
        s.text(1152, y + 7, r["rec_lbl"], 19, anchor="end", opacity=0.55)
        s.text(48, y + 32, what, 15, MUTED)
    legend(s, y_legend)
    s.text(48, H - 14, SOURCE_LINE + " Franklin buyout: Associated Press, October 12, 2025.", 12, MUTED)
    s.write(stem)


firings_chart("fig-06-firings")
print("done ->", OUT)
