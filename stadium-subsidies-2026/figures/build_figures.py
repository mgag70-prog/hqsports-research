#!/usr/bin/env python3
"""Build the in-article charts for stadium-subsidies-2026.

fig-01-the-bill: the 38 projects, public and private dollars, sorted by public dollars.
fig-02-share-rising: public share of each new venue, opened 2015-2026 vs under construction or approved, with medians.
fig-03-team-values: public money for each subsidized team's venue as a share of the team's Forbes value.
fig-04-open-asks: the failed and pending asks in data/asks.csv, what was sought and what happened.

Every number comes through model/recompute.py (which fails on any mismatch with the data) and is
asserted against draft.md and captions.md before any SVG is written.

Usage: build_figures.py [out_dir] [--final]
"""
import contextlib
import io
import re
import statistics
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
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-the-bill", "fig-02-share-rising", "fig-03-team-values", "fig-04-open-asks")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.fails
print(f"model: all checks pass; {len(R.P)} projects")
P, byid, V, AS = R.P, R.byid, R.V, R.AS
VERIFY = (PIECE / "data/research/verification.md").read_text()
pub, tot = R.pub, R.tot
subs, newo, newp = R.subs, R.newo, R.newp
med_subs = statistics.median(p["share"] for p in subs)
med_o, med_p = statistics.median(p["share"] for p in newo), statistics.median(p["share"] for p in newp)
assert (len(P), len(subs), len(newo), len(newp)) == (38, 30, 14, 9)
valued = sorted((i for i in V if i in byid and byid[i]["public"] > 0), key=lambda i: -R.pv(i))
assert len(valued) == 16 and valued[:2] == ["royals", "rays"]
bn, mn, pc = R.bn, R.mn, R.pc

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
DRAFT_PHRASES = (
    f"Together they cost {bn(tot)}. State, county and city governments put in {bn(pub)} of that, {pc(100 * pub / tot)}",
    f"the median public share is {pc(med_subs)}",
    f"the median public share is {pc(med_o)} across {len(newo)} buildings",
    f"Among the nine new venues now under construction or approved, it's {pc(med_p)}",
    f"is {pc(R.pv('royals'))} of the", f"for the Rays is {pc(R.pv('rays'))} of the team's",
    "The Bears are the biggest open question",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
CAPTION_PHRASES = (
    f"All {len(P)} projects in the set, {bn(tot)} of building, sorted by public dollars",
    f"Public money totals {bn(pub)}, {pc(100 * pub / tot)} of the cost",
    f"the median public share is {pc(med_o)} for the {len(newo)} that opened from 2015 through 2026 and {pc(med_p)} for the nine under construction or approved",
    f"The Thunder's arena, at {pc(byid['thunder']['share'])}, is the highest",
    f"from the Royals at {pc(R.pv('royals'))} and the Rays at {pc(R.pv('rays'))}",
    f"to the Raiders at {pc(R.pv('raiders'))}",
    "Ten asks from data/asks.csv",
)
for p in CAPTION_PHRASES:
    assert p in captions, f"captions.md no longer says: {p}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft and f"figures/{key}.png" in draft, key
print(f"draft ({len(DRAFT_PHRASES)} phrases) and captions ({len(CAPTION_PHRASES)} phrases) match the model; four slots exist")


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

    def circle(self, x, y, r, fill, stroke=None):
        extra = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{extra}/>')

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


def source(s, H, text):
    s.text(48, H - 14, text, 12, MUTED)


SRC = "Source: data/projects.csv (one cited report per project; headline deals verified a second time), recomputed by model/recompute.py."


def label(p):
    team = p["team"].replace("Los Angeles Rams and Chargers", "Rams and Chargers").replace("Philadelphia 76ers and Flyers", "76ers and Flyers")
    team = team.replace("Detroit Pistons and Red Wings", "Pistons and Red Wings").replace("Washington Wizards and Capitals", "Wizards and Capitals")
    return team + (" (renovation)" if p["kind"] == "renovation" else "")


def fig_the_bill(stem):
    title = f"Taxpayers put {bn(pub)} into {len(P)} stadium and arena deals."
    sub1 = f"Total cost by project, $ millions: public money in red, the rest in navy. {len(R.by['private'])} were privately financed."
    order = sorted(P, key=lambda p: (-p["public"], -p["total"]))
    X0, X1, VMAX = 330, 1080, 5000
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 140, 24, 16
    bottom = Y0 + PITCH * len(order)
    H = bottom + 92
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 500):
        s.line(xs(v), Y0 - 10, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"${v:,}M", 11, MUTED, anchor="middle")
    col_head(s, X0, Y0 - 16, "PUBLIC", fill=RED)
    col_head(s, X0 + 70, Y0 - 16, "PRIVATE", fill=NAVY)
    for i, p in enumerate(order):
        y = Y0 + i * PITCH
        s.text(X0 - 12, y + 12.5, label(p), 12.5, NAVY, anchor="end")
        s.rect(xs(0), y, xs(p["public"]) - xs(0), BH, RED)
        s.rect(xs(p["public"]), y, xs(p["total"]) - xs(p["public"]), BH, NAVY)
        tag = "private" if p["public"] == 0 else f"{p['share']:.1f}% public"
        s.text(xs(p["total"]) + 8, y + 12.5, tag, 11.5, RED if p["share"] > 50 else MUTED)
    s.text(48, H - 32, "Public: state, county and city construction money as reported; interest, maintenance, lost property tax and land not counted unless noted. Nominal dollars.", 12, MUTED)
    source(s, H, SRC)
    s.write(stem)


def fig_share_rising(stem):
    title = f"New venues still to open ask the public for more: median {med_p:.1f}% public, up from {med_o:.1f}%."
    sub1 = "Public share of each new venue's cost. Each dot is one venue; the red tick is the median."
    rows = (("OPENED 2015-2026", newo, med_o), ("UNDER CONSTRUCTION OR APPROVED", newp, med_p))
    X0, X1 = 120, 1120
    xs = lambda v: X0 + (X1 - X0) * v / 100
    Y = (265, 545)
    H = 690
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, 101, 10):
        s.line(xs(v), 150, xs(v), 640, GRID, 1)
        s.text(xs(v), 658, f"{v}%", 11, MUTED, anchor="middle")
    s.line(xs(50), 150, xs(50), 640, FAINT, 1, dash="2,3")
    for (name, ps, med), y in zip(rows, Y):
        col_head(s, X0, y - 90, f"{name}: {len(ps)} VENUES, MEDIAN {med:.1f}%", fill=NAVY)
        s.line(X0, y, X1, y, PALE, 1)
        placed = []
        for p in sorted(ps, key=lambda p: p["share"]):
            x = xs(p["share"])
            s.circle(x, y, 7, RED if p["share"] > 50 else NAVY)
            lane = next(k for k in range(10) if all(abs(x - px) > 95 or pk != k for px, pk in placed))
            placed.append((x, lane))
            ly = y + (24 + 16 * (lane // 2)) * (1 if lane % 2 == 0 else -1) + (4 if lane % 2 == 0 else 0)
            s.text(x, ly, p["team"].split()[-1] if p["id"] not in ("rams_chargers", "lca") else {"rams_chargers": "Rams/Chargers", "lca": "Pistons/Red Wings"}[p["id"]], 11, MUTED, anchor="middle")
        s.line(xs(med), y - 22, xs(med), y + 22, RED, 3)
    source(s, H, "New venues only; renovations excluded. Source: data/projects.csv, recomputed by model/recompute.py. Nine is a small sample: one deal moving shifts the median.")
    s.write(stem)


def fig_team_values(stem):
    title = f"In baseball, the public's share approaches the team's own value: Royals {R.pv('royals'):.1f}%, Rays {R.pv('rays'):.1f}%."
    sub1 = "Public money for the team's venue as a share of the team's Forbes value, subsidized teams with a Forbes value."
    X0, X1, VMAX = 330, 1060, 80
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 140, 34, 22
    bottom = Y0 + PITCH * len(valued)
    H = bottom + 84
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 10):
        s.line(xs(v), Y0 - 10, xs(v), bottom, GRID, 1)
        s.text(xs(v), bottom + 18, f"{v}%", 11, MUTED, anchor="middle")
    for i, tid in enumerate(valued):
        y = Y0 + i * PITCH
        p, v = byid[tid], V[tid]
        s.text(X0 - 12, y + 16, f"{v['team']} ({v['league']})", 14, NAVY, anchor="end")
        s.rect(xs(0), y, xs(R.pv(tid)) - xs(0), BH, RED if v["league"] == "MLB" else NAVY)
        s.text(xs(R.pv(tid)) + 8, y + 16, f"{R.pv(tid):.1f}%  (${p['public']:,.0f}M of a ${float(v['forbes_value_b']):g}B team)", 12.5, NAVY)
    s.text(48, H - 32, "Red: MLB. Forbes values are estimates, not sale prices: NFL list September 9, 2026; NBA October 16, 2026; MLB March 20, 2026. Wizards value only for the Capital One Arena deal.", 12, MUTED)
    source(s, H, "Source: data/team-values.csv and data/projects.csv, recomputed by model/recompute.py.")
    s.write(stem)


ASKS = (  # id, team, what was asked, what happened (each figure here is checked against the row below)
    ("bears_lakefront", "Bears", "Chicago lakefront dome: $2.4B public of $4.75B", "Shelved May 16 2025"),
    ("bears_hammond", "Bears", "Hammond, Ind.: about $1B of district tax revenue (state estimate)", "SB 27 signed Feb 26, 2026; board advanced Hammond Jun 5"),
    ("bears_illinois", "Bears", "Illinois stadium authority, Arlington Heights favored", "Crain's reports a near-deal, Oct 29, 2026; nothing announced"),
    ("broncos", "Broncos", "Burnham Yard: 'entirely privately funded'", "About $140M city viaducts and $19.4M state track work committed"),
    ("salt_lake", "MLB expansion, Salt Lake", "Up to $900M state money", "Only if an MLB team arrives by mid-2032"),
    ("chiefs_royals_jackson", "Chiefs and Royals", "Jackson County sales tax extension", "Failed Apr 2, 2024, 58% no; Kansas then took the Chiefs"),
    ("caps_wizards_va", "Capitals and Wizards", "Virginia arena: $1.5B public of $2B", "Died Mar 27, 2024; DC committed $515M"),
    ("rays_gasplant", "Rays", "St. Petersburg ballpark: $600M public of $1.3B", "Rays withdrew Mar 13, 2025"),
    ("coyotes_tempe", "Coyotes", "Tempe Entertainment District", "Voters said no, 56%, May 16, 2023; team moved to Utah in 2024"),
    ("chargers_sd", "Chargers", "San Diego Measure C", "43% yes, needed two-thirds; team moved to Los Angeles"),
)


def ask_figures_ok(i, *texts):
    """Every figure in the table text has to be a number in that asks.csv row (dollar asks also in $ billions)
    or in the verification.md item the row cites (verified-N)."""
    a = AS[i]
    cited = "".join(re.findall(rf"^{n}\. .*$", VERIFY, re.M)[0] for n in re.findall(r"verified-(\d+)", a["check"]))
    nums = {float(x) for x in re.findall(r"\d+(?:\.\d+)?", (" ".join(a.values()) + " " + cited).replace(",", ""))}
    nums |= {float(a[f]) / 1000 for f in ("public_ask_m", "total_cost_m") if a[f]}
    for t in texts:
        for fig in re.findall(r"\d+(?:\.\d+)?", t.replace(",", "")):
            assert float(fig) in nums, f"{i}: {fig} not in its asks.csv row"


def fig_open_asks(stem):
    assert len(ASKS) == len(R.A) and {a[0] for a in ASKS} == set(AS)
    for i, _, ask, outcome in ASKS:
        ask_figures_ok(i, ask, outcome)
    title = "What's still being asked, and what happened to the asks that failed."
    sub1 = "Every failed or pending ask in data/asks.csv: the Bears first, then the other open asks, then the ones that failed."
    COLS = (48, 250, 690)
    Y0, PITCH = 160, 46
    H = Y0 + PITCH * len(ASKS) + 50
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for x, h in zip(COLS, ("TEAM", "THE ASK", "WHAT HAPPENED")):
        col_head(s, x, Y0 - 20, h)
    s.line(48, Y0 - 10, 1152, Y0 - 10, NAVY, 1.5)
    for k, (i, team, ask, outcome) in enumerate(ASKS):
        y = Y0 + k * PITCH
        pending = AS[i]["status"] == "proposed" or i == "bears_lakefront"
        if k % 2 == 0:
            s.rect(48, y - 4, 1104, PITCH, "rgba(22,40,74,0.05)")
        s.text(COLS[0], y + 24, team, 15, RED if AS[i]["status"] == "proposed" else NAVY)
        s.text(COLS[1], y + 24, ask, 14, NAVY)
        s.text(COLS[2], y + 24, outcome, 14, NAVY if pending else MUTED)
    s.line(48, Y0 + PITCH * len(ASKS) - 4, 1152, Y0 + PITCH * len(ASKS) - 4, NAVY, 1)
    source(s, H, "Red: still proposed. Source: data/asks.csv; each row cites its report.")
    s.write(stem)


fig_the_bill(KEYS[0]); fig_share_rising(KEYS[1]); fig_team_values(KEYS[2]); fig_open_asks(KEYS[3])
print("done ->", OUT)
