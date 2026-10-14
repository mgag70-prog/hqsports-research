#!/usr/bin/env python3
"""Build the in-article charts for illinois-revenue-sharing-2026.

fig-01-peer-table: six Big Ten schools, what each has disclosed about revenue sharing (data/peers.csv).
fig-02-category-44: the Category 44 line of the NCAA form, by program, as a table graphic.
fig-03-revenue-expenses: FY2024 and FY2025 revenue and expenses, surplus labeled.
fig-04-surplus-by-program: FY2025 surplus or deficit by program, diverging bars.

Every number comes through model/recompute.py (which fails on any mismatch with the report text)
and is asserted against draft.md and captions.md before any SVG is written.

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
RED_TINT = "rgba(212,85,61,0.12)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-peer-table", "fig-02-category-44", "fig-03-revenue-expenses", "fig-04-surplus-by-program")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.mismatches
print(f"model: {R.checked} checks pass")
M = 1e6
rev = {fy: R.S[(fy, "total_operating_revenues")] for fy in (2024, 2025)}
exp = {fy: R.S[(fy, "total_operating_expenses")] for fy in (2024, 2025)}
net = {fy: R.S[(fy, "excess_revenues_over_expenses")] for fy in (2024, 2025)}
rev_growth = 100 * (rev[2025]["total"] / rev[2024]["total"] - 1)
exp_growth = 100 * (exp[2025]["total"] / exp[2024]["total"] - 1)
PROGRAMS = (("football", "Football"), ("mens_basketball", "Men's basketball"), ("womens_basketball", "Women's basketball"),
            ("other_sports", "Other sports"), ("non_program_specific", "Not program-specific"))
two = (net[2025]["football"] + net[2025]["mens_basketball"]) / M
rest = (net[2025]["womens_basketball"] + net[2025]["other_sports"] + net[2025]["non_program_specific"]) / M
surplus = net[2025]["total"] / M
cap_mult, gap = R.cap / surplus, R.cap - surplus
PEER = {(r["school"], r["item"]): r for r in R.peers}
OSU_REV = int(PEER[("Ohio State", "fy25_total_operating_revenues")]["value"]) / M
IU_REV = int(PEER[("Indiana", "fy25_total_operating_revenues")]["value"]) / M

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
fm = lambda v: f"${v:.1f} million"
DRAFT_PHRASES = (
    f"ran a surplus of {fm(surplus)} in fiscal 2025, on {fm(rev[2025]['total'] / M)} of revenue against {fm(exp[2025]['total'] / M)} of expenses; the year before, {fm(net[2024]['total'] / M)}",
    f"Revenue grew {rev_growth:.1f}% and expenses grew {exp_growth:.1f}%",
    f"Ohio State's revenue was ${OSU_REV:.1f} million, {OSU_REV / (rev[2025]['total'] / M):.1f} times Illinois's. Indiana's was ${IU_REV:.1f} million.",
    f"Football cleared {fm(net[2025]['football'] / M)} on {fm(rev[2025]['football'] / M)} of revenue, up {100 * (rev[2025]['football'] / rev[2024]['football'] - 1):.1f}% in a year; men's basketball cleared {fm(net[2025]['mens_basketball'] / M)}. Together, {fm(two)}.",
    f"Everything else lost it back, ${-rest:.1f} million in all: women's basketball {fm(-net[2025]['womens_basketball'] / M)}, the other sports {fm(-net[2025]['other_sports'] / M)}, and {fm(-net[2025]['non_program_specific'] / M)} of expense not tied to any program",
    f"working with the same {fm(R.cap)} cap as Ohio State",
    "The FY2024 expense categories run from 20 to 41A", "The FY2025 form runs to 44, and Category 44 is \"Institutional NIL Revenue Share\"",
    "on page 16, defined and totaled; on page 94, by program", "on page 74 as a twelve-sport table",
    "Every cell is zero or blank, at all three schools.",
    "Six schools. Zero dollars by sport. The full count: three percentages for football (Michigan, Indiana, Illinois), four lists of sports, zero dollar figures by sport",
    "Ohio State committed $18 million to athletes in four sports", "the remaining $2.5 million of the cap going to 91 added scholarships",
    "budgeted $20.5 million for FY2026, projected $18.0 million actually spent, and budgeted $21.32 million for FY2027",
    "budgeted $20,000,000 for FY2026, financed in part by a $12,063,922 internal loan, and $21,320,000 for FY2027 against a projected athletics deficit of $10,555,220",
    "Iowa's regents budgeted $20.5 million, then $21.32 million", "football would get 70% to 75% of a $20.5 million budget in year one",
    "record $336,077,887 of revenue",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"Revenue rose from {fm(rev[2024]['total'] / M)} to {fm(rev[2025]['total'] / M)}, {rev_growth:.1f}%; expenses rose from {fm(exp[2024]['total'] / M)} to {fm(exp[2025]['total'] / M)}, {exp_growth:.1f}%",
    f"The surplus went from {fm(net[2024]['total'] / M)} to {fm(surplus)}",
    f"Ohio State's FY2025 revenue was ${OSU_REV:.1f} million and Indiana's ${IU_REV:.1f} million",
    f"Football cleared {fm(net[2025]['football'] / M)} and men's basketball {fm(net[2025]['mens_basketball'] / M)}, {fm(two)} together",
    f"Women's basketball lost {fm(-net[2025]['womens_basketball'] / M)}, the other sports {fm(-net[2025]['other_sports'] / M)}, and expenses not tied to any program ran {fm(-net[2025]['non_program_specific'] / M)}",
    "$0 in every column, because payments began July 1, 2025", "its sport rows are blank and its subtotals read 0", "The FY2024 form had no Category 44",
    "Ohio State's $18 million is payments; the other $2.5 million of its cap went to scholarships", "Michigan's regents projected $18.0 million actually spent",
    "No school in the group has published dollars by sport",
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

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

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


def fig_revenue_expenses(stem):
    title = f"Revenue grew {rev_growth:.1f}% in FY2025 and expenses {exp_growth:.1f}%, so the surplus stayed near $5 million."
    sub1 = "Illinois athletics' operating revenue and expenses, $ millions, from the NCAA financial reports the department posts."
    X0, Y0, Y1, VMAX = 120, 140, 440, 200
    ys = lambda v: Y1 - (Y1 - Y0) * v / VMAX
    H = Y1 + 112            # room under the FY labels so the source line doesn't crowd them
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 50):
        s.line(X0, ys(v), 1150, ys(v), GRID, 1)
        s.text(X0 - 10, ys(v) + 4, f"${v}M", 11, MUTED, anchor="end")
    s.line(X0, Y1, 1150, Y1, NAVY, 1.5)
    BW, GAPB = 150, 24
    for i, fy in enumerate((2024, 2025)):
        gx = 260 + i * 460
        r, e, n = rev[fy]["total"] / M, exp[fy]["total"] / M, net[fy]["total"] / M
        s.rect(gx, ys(r), BW, Y1 - ys(r), NAVY)
        s.rect(gx + BW + GAPB, ys(e), BW, Y1 - ys(e), FAINT)
        s.text(gx + BW / 2, ys(r) - 10, f"${r:.1f}M", 15, NAVY, anchor="middle")
        s.text(gx + BW + GAPB + BW / 2, ys(e) - 10, f"${e:.1f}M", 15, MUTED, anchor="middle")
        col_head(s, gx + BW / 2, Y1 + 22, "REVENUE", anchor="middle")
        col_head(s, gx + BW + GAPB + BW / 2, Y1 + 22, "EXPENSES", anchor="middle")
        s.text(gx + BW + GAPB / 2, Y1 + 50, f"FY{fy}", 17, NAVY, anchor="middle")
        # Surplus: the sliver between the two bar tops.
        s.rect(gx + BW + GAPB, ys(r), BW, ys(e) - ys(r), RED)
        s.text(gx + 2 * BW + GAPB + 12, ys(r) + 5, f"surplus ${n:.1f}M", 14, RED)
    s.text(48, H - 14, "Source: NCAA MFRS reports, FY2024 (posted January 23, 2025) and FY2025 (posted January 29, 2026), total operating revenues and expenses.", 12, MUTED)
    s.write(stem)


def fig_surplus_by_program(stem):
    title = f"Football and men's basketball cleared ${two:.1f}M in FY2025. Everything else lost ${-rest:.1f}M."
    sub1 = f"Operating surplus or deficit by program, $ millions, FY2025. Net for the department: ${surplus:.1f} million."
    X0, X1, VMIN, VMAX = 150, 1100, -30, 45
    xs = lambda v: X0 + (X1 - X0) * (v - VMIN) / (VMAX - VMIN)
    Y0, PITCH, BH = 150, 56, 32
    H = Y0 + PITCH * 6 + 70
    s = SVG(1200, H, title)
    header(s, title, sub1)
    rows = [(label, net[2025][k] / M) for k, label in PROGRAMS] + [("Department, net", surplus)]
    for i, (label, v) in enumerate(rows):
        y = Y0 + i * PITCH
        if i == 5:
            s.line(X0, y - 10, X1, y - 10, GRID, 1)
        col = NAVY if v >= 0 else RED
        s.text(xs(0) - 14 if v >= 0 else xs(0) + 14, y + 21, label, 14, NAVY, anchor="end" if v >= 0 else "start")
        s.rect(min(xs(0), xs(v)), y, abs(xs(v) - xs(0)), BH, col)
        s.text(xs(v) + (10 if v >= 0 else -10), y + 21, f"{'+' if v >= 0 else '-'}${abs(v):.1f}M", 15, col, anchor="start" if v >= 0 else "end")
    s.line(xs(0), Y0 - 10, xs(0), Y0 + PITCH * 6 - 10, NAVY, 1.5)
    y_ax = Y0 + PITCH * 6 - 6
    for v in range(VMIN, VMAX + 1, 15):
        s.text(xs(v), y_ax + 14, f"{'-' if v < 0 else ''}${abs(v)}M", 12, MUTED, anchor="middle")
    s.text(48, H - 14, "Source: NCAA MFRS report, FY2025, page 94, excess (deficiencies) of revenues over expenses by program.", 12, MUTED)
    s.write(stem)


def fig_category_44(stem):
    title = "The form has a line for revenue sharing by program. FY2025 reads zero."
    sub1 = "Category 44, \"Institutional NIL Revenue Share,\" of the NCAA financial report, as Illinois filed it for FY2025, by program."
    rows = [label for _, label in PROGRAMS] + ["Total"]
    cells = [R.cat44[k] for k, _ in PROGRAMS] + [R.cat44["total"]]
    assert all(c == 0 for c in cells) and len(R.sports) == 13
    X = [48, 620, 900]
    HEAD_Y, HEAD_H, ROW_H = 130, 40, 46
    H = HEAD_Y + HEAD_H + ROW_H * len(rows) + 106
    s = SVG(1200, H, title)
    header(s, title, sub1)
    s.rect(48, HEAD_Y, 1104, HEAD_H, NAVY)
    for x, label in zip(X, ("PROGRAM", "FY2025, AS FILED", "FY2026")):
        s.text(x + (20 if x == 48 else 0), HEAD_Y + 26, label, 12, PAPER, spacing=1.8)
    for i, (label, v) in enumerate(zip(rows, cells)):
        y = HEAD_Y + HEAD_H + i * ROW_H
        if label == "Total":
            s.line(48, y, 1152, y, NAVY, 1.5)
        s.line(48, y + ROW_H, 1152, y + ROW_H, GRID, 1)
        s.text(68, y + 29, label, 16, NAVY)
        s.text(X[1], y + 29, f"${v:,d}", 16, NAVY)
        s.text(X[2], y + 29, "to be posted", 16, RED)
    y = HEAD_Y + HEAD_H + ROW_H * len(rows)
    s.text(48, y + 32, "Payments began July 1, 2025, the first day of FY2026, so the FY2025 line is empty. The form also carries a twelve-sport table (page 74), baseball through", 12, MUTED)
    s.text(48, y + 50, "wrestling, men's and women's columns; its sport rows are blank and its subtotals read 0. The FY2024 form had no Category 44.", 12, MUTED)
    s.text(48, H - 32, "Source: NCAA MFRS report, FY2025, pages 16, 74 and 94. FY2026: the October 12, 2026 FOIA response says the report \"will be posted on this page when they become available.\"", 12, MUTED)
    s.text(48, H - 14, "Ohio State's and Indiana's FY2025 reports carry the same zero row. Values as filed with the NCAA; not legal or financial advice.", 12, MUTED)
    s.write(stem)


def fig_peer_table(stem):
    title = "Six Big Ten schools, three football percentages, zero dollar figures by sport."
    sub1 = "What each school has put on the record about revenue sharing, as of October 13, 2026. Totals are budgets or AD statements, not results."
    v = lambda school, item: PEER[(school, item)]["value"]
    assert v("Ohio State", "fy25_mfrs_public") == "yes" and v("Illinois", "fy25_mfrs_public") == "yes" and v("Indiana", "fy25_mfrs_public") == "records request"
    osu_total = f"${float(v('Ohio State', 'rev_share_2025_26_usd_m')):.1f}M payments + ${float(v('Ohio State', 'scholarships_2025_26_usd_m')):.1f}M scholarships"
    rows = [
        ("Ohio State", "Yes, with Jan. 30, 2026 release", osu_total, "Four sports named; no dollars", NAVY),
        ("Michigan", "Not found (EADA only)", f"${float(v('Michigan', 'rev_share_fy26_budget_usd_m')):.1f}M budget; ${float(v('Michigan', 'rev_share_fy26_projection_usd_m')):.1f}M projected", "About 75% football, per AD; no dollars", NAVY),
        ("Michigan State", "Not found", f"${float(v('Michigan State', 'rev_share_fy26_budget_usd_m')):.1f}M budget, ${int(v('Michigan State', 'internal_loan_fy26_usd')) / M:.1f}M of it an internal loan", "None found", NAVY),
        ("Iowa", "Not found", f"${float(v('Iowa', 'rev_share_fy26_budget_usd_m')):.1f}M budget", "Four sports named; no dollars", NAVY),
        ("Indiana", "Via records request (IPM)", f"${float(v('Indiana', 'rev_share_2025_26_usd_m')):.1f}M, per AD", "Football 70 to 75%, per AD; no dollars", NAVY),
        ("Illinois", "Yes, every year since FY2018", f"${float(v('Illinois', 'rev_share_2025_26_usd_m')):.1f}M, per AD; FOIA for the split denied", "In the 75-15-5-5 range, per AD; no dollars", RED),
    ]
    assert [r[0] for r in rows] == ["Ohio State", "Michigan", "Michigan State", "Iowa", "Indiana", "Illinois"]
    X = [48, 230, 540, 860]
    HEAD_Y, HEAD_H, ROW_H = 130, 40, 50
    H = HEAD_Y + HEAD_H + ROW_H * len(rows) + 92
    s = SVG(1200, H, title)
    header(s, title, sub1)
    s.rect(48, HEAD_Y, 1104, HEAD_H, NAVY)
    for x, label in zip(X, ("SCHOOL", "FY2025 NCAA REPORT PUBLIC?", "2025-26 REVENUE-SHARING TOTAL", "SPLIT BY SPORT")):
        s.text(x + (20 if x == 48 else 0), HEAD_Y + 26, label, 12, PAPER, spacing=1.8)
    for i, (school, pub, total, split, ink) in enumerate(rows):
        y = HEAD_Y + HEAD_H + i * ROW_H
        if ink == RED:
            s.rect(48, y, 1104, ROW_H, RED_TINT); s.rect(48, y, 4, ROW_H, RED)
        s.line(48, y + ROW_H, 1152, y + ROW_H, GRID, 1)
        s.text(68, y + 31, school, 16, ink)
        s.text(X[1], y + 31, pub, 14, ink)
        s.text(X[2], y + 31, total, 14, ink)
        s.text(X[3], y + 31, split, 14, ink)
    y = HEAD_Y + HEAD_H + ROW_H * len(rows)
    s.text(48, y + 30, "Ohio State: Bjork, June 12, 2025 (\"Numbers create narratives\"). Michigan: regents, June 25, 2026; Manuel, June 2025. Michigan State and Iowa: trustees and regents budgets, 2025. Indiana: Dolson to IndyStar, 2025.", 12, MUTED)
    s.text(48, y + 48, "Illinois: Whitman, June 26, 2025 (\"We're not going to share the actual numbers\"); FOIA 26-2759 denied October 12, 2026. Every cell's source, date and quote: data/peers.csv.", 12, MUTED)
    s.text(48, H - 14, "Michigan, Michigan State and Iowa report their NCAA figures to the NCAA but no public copy was found; Indiana's reached the public through Indiana Public Media's records request.", 12, MUTED)
    s.write(stem)


fig_peer_table(KEYS[0]); fig_category_44(KEYS[1]); fig_revenue_expenses(KEYS[2]); fig_surplus_by_program(KEYS[3])
print("done ->", OUT)
