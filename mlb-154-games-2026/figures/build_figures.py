#!/usr/bin/env python3
"""Build the in-article charts for mlb-154-games-2026.

fig-01-tickets-lost: four-date ticket losses, all 30 clubs, sorted bars.
fig-02-lose-vs-add: Dodgers, Cubs and bottom-club four-date gate losses beside the best-case
postseason add-back for all 30 clubs.
fig-03-postseason-split: the gate split by game as a table graphic.
fig-04-tv-deals: national TV deals by partner, annual value, with 2029 marked.

Every number comes through model/recompute.py (which fails on any mismatch with the data
files) and is asserted against draft.md and captions.md before any SVG is written.

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
KEYS = ("fig-01-tickets-lost", "fig-02-lose-vs-add", "fig-03-postseason-split", "fig-04-tv-deals")

sys.path.insert(0, str(PIECE / "model"))
with contextlib.redirect_stdout(io.StringIO()):
    import recompute as R
assert not R.mismatches
LOSS = {"Dodgers": R.LOST_DATES * R.gate["Los Angeles Dodgers"], "Cubs": R.LOST_DATES * R.gate["Chicago Cubs"],
        "bottom": R.LOST_DATES * R.gate["Bottom of the league"]}
# Add-back bounds: every pool game at 60% (low) and every pool game at 50% (high); see recompute.py.
LO, HI = R.added["low"], R.added["high"]
LO_PG, HI_PG = R.per_pool_game["low"], R.per_pool_game["high"]
LO_GATE, HI_GATE = R.implied_gate["low"], R.implied_gate["high"]
print(f"model: {R.checked} checks pass")

draft, captions = DRAFT.read_text(), CAPTIONS.read_text()
m = lambda v: f"{v:,d}"
DRAFT_PHRASES = (
    f"drew {m(R.total)} fans in 2026, {R.per_game:,.0f} a game over {m(R.dates)} home dates",
    f"the league loses {m(R.lost)} tickets a season, {100 * R.lost / R.total:.2f}% of this year's count",
    f"The Dodgers lose the most, {m(R.by_team['Los Angeles Dodgers'])} tickets; the Athletics the fewest, {m(R.by_team['Athletics'])}",
    f"about ${LOSS['Dodgers']:.2f} million of gate for the Dodgers, ${R.LOST_DATES * R.gate['New York Yankees']:.2f} million for the Yankees, "
    f"${LOSS['Cubs']:.2f} million for the Cubs, ${R.LOST_DATES * R.gate['Boston Red Sox']:.2f} million for the Red Sox, "
    f"${R.LOST_DATES * R.gate['Houston Astros']:.2f} million for the Astros, and about ${LOSS['bottom']:.2f} million",
    f"If every pool game paid 60%, a ${R.pool:.1f} million pool implies ${LO_GATE:.1f} million of gate across the {R.pool_games} pool games, about ${LO_PG:.2f} million a game; "
    f"if every pool game paid 50%, ${HI_GATE:.1f} million and about ${HI_PG:.2f} million a game. The truth sits between, since {R.wc_games} of the {R.pool_games} were Wild Card games at 50%",
    f"Eight added Division Series games at those averages is ${LO:.1f} million to ${HI:.1f} million of gate",
    f"${LO * R.CLUBS_SHARE_LATE:.1f} million to ${HI * R.CLUBS_SHARE_LATE:.1f} million of that goes to the clubs, ${LO * R.COMMISSIONER_SHARE:.1f} million to ${HI * R.COMMISSIONER_SHARE:.1f} million to the Commissioner's Office, and nothing to the players' pool",
    f"is ${LO:.1f} million to ${HI:.1f} million for all 30 clubs together",
    "50% of the gate from the Wild Card games, 60% from the first three Division Series games and the first four of each LCS and the World Series",
    "in a Wild Card game, 50% goes to the players' pool and 35% to the two clubs",
    f"run to ${R.tv_total:,.1f} million a year",
    f"{100 * (R.GAMES_NOW / R.GAMES_PROPOSED - 1):.1f}% more pay per game played",
    "On 81 home dates, 40 games can be canceled with no refund owed under that clause. On 77, it's 36.",
    "about three to four Dodger-sized losses",
)
for p in DRAFT_PHRASES:
    assert p in draft, f"draft no longer says: {p}"
assert round(LO / LOSS["Dodgers"]) == 3 and round(HI / LOSS["Dodgers"]) == 4
CAPTION_PHRASES = (
    f"The Dodgers lose the most, {m(R.by_team['Los Angeles Dodgers'])}, and the Athletics the fewest, {m(R.by_team['Athletics'])}; the league loses {m(R.lost)} tickets, {100 * R.lost / R.total:.2f}% of the {m(R.total)}",
    f"the Dodgers ${LOSS['Dodgers']:.2f} million, the Cubs ${LOSS['Cubs']:.2f} million, and about ${LOSS['bottom']:.2f} million",
    f"The add-back, ${LO:.1f} million to ${HI:.1f} million, is the best case for all 30 clubs combined: eight games at ${LO_PG:.2f} million to ${HI_PG:.2f} million each, the 2025 average across the {R.pool_games} pool games",
    f"${LO * R.CLUBS_SHARE_LATE:.1f} million to ${HI * R.CLUBS_SHARE_LATE:.1f} million of that reaches the clubs",
    "The Commissioner's Office takes 15% of every game", "In the two Wild Card games, 50% goes to the players' pool and 35% to the two clubs",
    "60% goes to the players' pool and 25% to the two clubs", "0% goes to the pool and 85% to the clubs", "A third Wild Card game's split isn't in the sources",
    f"Together, ${R.tv_total:,.1f} million a year",
) + tuple(f"{r['partner'].split('/')[0]} " + (f"${float(r['annual_value_usd_m']):,.1f} million" if r["partner"] == "Fox" else f"${float(r['annual_value_usd_m']):,.0f} million") for r in R.tv if r["partner"] in ("Fox", "Turner/TBS"))
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


SHORT = {"Arizona Diamondbacks": "Diamondbacks", "Athletics": "Athletics", "Atlanta Braves": "Braves", "Baltimore Orioles": "Orioles",
         "Boston Red Sox": "Red Sox", "Chicago Cubs": "Cubs", "Chicago White Sox": "White Sox", "Cincinnati Reds": "Reds",
         "Cleveland Guardians": "Guardians", "Colorado Rockies": "Rockies", "Detroit Tigers": "Tigers", "Houston Astros": "Astros",
         "Kansas City Royals": "Royals", "Los Angeles Angels": "Angels", "Los Angeles Dodgers": "Dodgers", "Miami Marlins": "Marlins",
         "Milwaukee Brewers": "Brewers", "Minnesota Twins": "Twins", "New York Mets": "Mets", "New York Yankees": "Yankees",
         "Philadelphia Phillies": "Phillies", "Pittsburgh Pirates": "Pirates", "San Diego Padres": "Padres", "San Francisco Giants": "Giants",
         "Seattle Mariners": "Mariners", "St. Louis Cardinals": "Cardinals", "Tampa Bay Rays": "Rays", "Texas Rangers": "Rangers",
         "Toronto Blue Jays": "Blue Jays", "Washington Nationals": "Nationals"}


def fig_tickets_lost(stem):
    title = f"Four fewer home dates is {m(R.lost)} fewer tickets a year, {100 * R.lost / R.total:.2f}% of 2026 attendance."
    sub1 = "Tickets each club loses from four home dates at its own 2026 per-game attendance, all 30 clubs."
    X0, X1, VMAX = 190, 1120, 200000
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH = 150, 20
    H = Y0 + PITCH * 30 + 60
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for v in range(0, VMAX + 1, 50000):
        s.line(xs(v), Y0 - 6, xs(v), Y0 + PITCH * 30, GRID, 1)
        s.text(xs(v), Y0 - 12, f"{v // 1000}k", 11, MUTED, anchor="middle")
    for i, (team, v) in enumerate(R.ranked):
        y = Y0 + i * PITCH
        col = RED if team in ("Los Angeles Dodgers", "Chicago Cubs", "Athletics") else NAVY
        s.text(X0 - 10, y + 13, SHORT[team], 12, NAVY, anchor="end")
        s.rect(X0, y + 3, xs(v) - X0, PITCH - 7, col)
        s.text(xs(v) + 6, y + 13, m(v), 11, col)
    s.text(48, H - 14, "Source: Baseball-Reference, 2026 attendance. Four-date figures are per-game attendance times four. Calculated.", 12, MUTED)
    s.write(stem)


def fig_lose_vs_add(stem):
    title = "The best-case postseason add-back is about three to four Dodger-sized gate losses."
    sub1 = "Four lost home dates at 2024 gate per game (Sportico), against eight added Division Series games at the 2025 pool-game average."
    sub2 = f"The add-back is a range of estimates: ${LO_PG:.2f}M a game if every pool game paid the pool 60%, ${HI_PG:.2f}M if every one paid 50%."
    losses = [("Dodgers, four dates lost", LOSS["Dodgers"]), ("Cubs, four dates lost", LOSS["Cubs"]),
              ("A bottom-of-league club, four dates lost", LOSS["bottom"])]
    X0, X1, VMAX = 400, 1080, 70
    xs = lambda v: X0 + (X1 - X0) * v / VMAX
    Y0, PITCH, BH = 176, 64, 34
    H = Y0 + PITCH * 4 + 96
    s = SVG(1200, H, title)
    header(s, title, sub1, sub2)
    col_head(s, 48, 152, "GATE, $ MILLIONS")
    for i, (label, v) in enumerate(losses):
        y = Y0 + i * PITCH
        s.text(X0 - 14, y + 22, label, 14, NAVY, anchor="end")
        s.rect(X0, y, xs(v) - X0, BH, NAVY)
        s.text(xs(v) + 10, y + 22, f"${v:.2f}M", 15, NAVY)
    # Range bar: solid red to the low bound, tinted red on to the high bound, both ends labeled.
    y = Y0 + 3 * PITCH
    s.text(X0 - 14, y + 22, "Best-case add-back, all 30 clubs", 14, NAVY, anchor="end")
    s.rect(X0, y, xs(LO) - X0, BH, RED)
    s.rect(xs(LO), y, xs(HI) - xs(LO), BH, RED_TINT, stroke=RED)
    s.text(xs(LO) - 6, y + 22, f"${LO:.1f}M", 15, PAPER, anchor="end")
    s.text(xs(HI) + 10, y + 22, f"to ${HI:.1f}M", 15, RED)
    s.text(X0, y + BH + 18, f"${LO * R.CLUBS_SHARE_LATE:.1f}M to ${HI * R.CLUBS_SHARE_LATE:.1f}M to clubs, "
           f"${LO * R.COMMISSIONER_SHARE:.1f}M to ${HI * R.COMMISSIONER_SHARE:.1f}M to the Commissioner, $0 to the players' pool", 12, MUTED)
    y_ax = Y0 + PITCH * 4 - 6
    s.line(X0, y_ax, X1, y_ax, NAVY, 1.5)
    for v in range(0, VMAX + 1, 10):
        s.text(xs(v), y_ax + 20, f"${v}M", 12, MUTED, anchor="middle")
    s.text(48, H - 14, "Source: Sportico, May 30, 2025 (2024 gate per home game) and December 2025 (2025 players' pool); MLB.com glossary (pool shares); FanGraphs, October 7, 2014 (split). Estimates.", 12, MUTED)
    s.write(stem)


def fig_postseason_split(stem):
    title = "Games past a series' minimum fund no players' pool. Games 6 and 7 would be two more."
    sub1 = "How postseason gate is split, per FanGraphs (2014), MLB.com's glossary (pool shares) and Sportico (the 2025 pool). Not the agreement's text."
    rows = [("Wild Card, Games 1 and 2", "15%", "50%", "35%", False),
            ("Division Series, Games 1 to 3", "15%", "60%", "25%", False), ("Division Series, Games 4 and 5", "15%", "0%", "85%", False),
            ("Division Series, Games 6 and 7 (proposed)", "15%", "0%", "85%", True),
            ("LCS and World Series, Games 1 to 4", "15%", "60%", "25%", False), ("LCS and World Series, Games 5 to 7", "15%", "0%", "85%", False)]
    X = [48, 560, 760, 960]
    HEAD_Y, HEAD_H, ROW_H = 130, 40, 46
    H = HEAD_Y + HEAD_H + ROW_H * len(rows) + 88
    s = SVG(1200, H, title)
    header(s, title, sub1)
    assert any(r[0].startswith("Wild Card") and r[2] == "50%" for r in rows) and not any("Game 3" in r[0] for r in rows)
    s.rect(48, HEAD_Y, 1104, HEAD_H, NAVY)
    for x, label in zip(X, ("GAME", "COMMISSIONER'S OFFICE", "PLAYERS' POOL", "THE TWO CLUBS")):
        s.text(x + (20 if x == 48 else 0), HEAD_Y + 26, label, 12, PAPER, spacing=1.8)
    for i, (game, c, p, k, proposed) in enumerate(rows):
        y = HEAD_Y + HEAD_H + i * ROW_H
        if proposed:
            s.rect(48, y, 1104, ROW_H, RED_TINT); s.rect(48, y, 4, ROW_H, RED)
        s.line(48, y + ROW_H, 1152, y + ROW_H, GRID, 1)
        ink = RED if proposed else NAVY
        s.text(68, y + 29, game, 16, ink)
        for x, v in zip(X[1:], (c, p, k)):
            s.text(x, y + 29, v, 16, RED if (proposed and v == "0%") else ink)
    s.text(48, H - 50, "A third Wild Card game's split isn't in the sources, so no row is shown for it.", 12, MUTED)
    s.text(48, H - 32, "Source: FanGraphs, Wendy Thurm, October 7, 2014; MLB.com glossary, Postseason Share; Sportico, December 2025 (pool games: two WC, three DS, four LCS, four WS).", 12, MUTED)
    s.text(48, H - 14, f"The 2025 pool: ${R.pool:.1f}M. Attributed to those reports, not to the CBA text. Not legal or financial advice.", 12, MUTED)
    s.write(stem)


def fig_tv_deals(stem):
    title = f"${R.tv_total / 1000:.2f} billion a year of national television, every deal ending after 2028."
    sub1 = "Listed annual value by partner. The 154-game season would start in 2029, the first year of the next deals. Apple's deal isn't verified and is left out."
    X0, X1, Y0 = 220, 1000, 170
    years = list(range(2022, 2031))
    xs = lambda y: X0 + (X1 - X0) * (y - years[0]) / (years[-1] - years[0])
    PITCH, BH = 54, 30
    H = Y0 + PITCH * len(R.tv) + 90
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for y in years:
        s.line(xs(y), Y0 - 10, xs(y), Y0 + PITCH * len(R.tv) - 10, GRID, 1)
        s.text(xs(y), Y0 - 16, str(y), 11, MUTED, anchor="middle")
    for i, r in enumerate(R.tv):
        y = Y0 + i * PITCH
        a, b = (int(v) for v in r["term"].split("-"))
        s.text(X0 - 14, y + 20, r["partner"], 15, NAVY, anchor="end")
        s.rect(xs(a), y, xs(b + 1) - xs(a), BH, NAVY)
        v = float(r["annual_value_usd_m"])
        s.text(xs(b + 1) + 10, y + 20, f"${v:,.1f}M a year" if r["partner"] == "Fox" else f"${v:,.0f}M a year", 14, NAVY)
    s.line(xs(2029), Y0 - 30, xs(2029), Y0 + PITCH * len(R.tv), RED, 1.5, dash="4 5")
    s.text(xs(2029) + 6, Y0 - 34, "154 games would start", 12, RED)
    s.text(xs(2029), Y0 - 16, "2029", 11, RED, anchor="middle")
    s.text(48, H - 14, "Source: Sportico, 2020 (Fox, Turner); Axios, November 19 and 20, 2025, and Boardroom, November 26, 2025 (ESPN, NBC, Netflix). Values as listed, not as booked.", 12, MUTED)
    s.write(stem)


fig_tickets_lost(KEYS[0]); fig_lose_vs_add(KEYS[1]); fig_postseason_split(KEYS[2]); fig_tv_deals(KEYS[3])
print("done ->", OUT)
