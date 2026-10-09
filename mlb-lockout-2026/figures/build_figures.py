#!/usr/bin/env python3
"""Build the in-article charts for mlb-lockout-2026.

fig-01-club-grid: 30 tiles, one per club, grouped and colored by category.
fig-02-lockout-table: the four lockout clauses as a table graphic.
fig-03-refund-clocks: every stated deadline, who owes it, how many days.
fig-04-cubs-line: the Cubs' 41-game threshold on an 81-game and a 77-game home schedule.

Every count, name, day figure and quote comes from data/club-terms.csv, and each is asserted
against draft.md and captions.md before any SVG is written. The 81 and 77 home-game schedules
and the 41-game threshold are constants here; 40 and 36 are computed from them.

Usage: build_figures.py [out_dir] [--final]
  out_dir defaults to this script's directory; --final skips the 700px previews.
"""
import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

PIECE = Path(__file__).resolve().parents[1]
REPO = PIECE.parent
DRAFT = PIECE / "draft.md"
CAPTIONS = PIECE / "figures/captions.md"
DATA = PIECE / "data/club-terms.csv"
REF_SVG = REPO / "acc-distributions-2026/figures/fig-02-five-year-spread.svg"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(args[0]) if args else Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv

NAVY = "#16284A"
RED = "#D4553D"
PAPER = "#F7F5F0"
MUTED = "rgba(22,40,74,0.62)"
FAINT = "rgba(22,40,74,0.40)"
PALE = "rgba(22,40,74,0.18)"
GRID = "rgba(22,40,74,0.13)"
SHADE = "rgba(22,40,74,0.06)"
RED_TINT = "rgba(212,85,61,0.12)"
FONT = "Libre Caslon Text, Georgia, serif"
FONT_STYLE = re.search(r"<style>.*?</style>", REF_SVG.read_text(), re.S).group(0)
KEYS = ("fig-01-club-grid", "fig-02-lockout-table", "fig-03-refund-clocks", "fig-04-cubs-line")

HOME_GAMES_NOW, HOME_GAMES_PROPOSED, CUBS_LINE = 81, 77, 41
NAMES = {"cubs": "Cubs", "reds": "Reds", "dbacks": "Diamondbacks", "yankees": "Yankees", "brewers": "Brewers",
         "royals": "Royals", "giants": "Giants", "angels": "Angels", "phillies": "Phillies", "braves": "Braves",
         "bluejays": "Blue Jays", "cardinals": "Cardinals", "tigers": "Tigers", "marlins": "Marlins",
         "dodgers": "Dodgers", "twins": "Twins", "whitesox": "White Sox", "rockies": "Rockies",
         "mariners": "Mariners", "padres": "Padres", "orioles": "Orioles", "astros": "Astros", "redsox": "Red Sox",
         "pirates": "Pirates", "guardians": "Guardians", "nationals": "Nationals", "rays": "Rays",
         "rangers": "Rangers", "mets": "Mets", "athletics": "Athletics"}
GROUPS = [  # label, categories, color
    ("Names a lockout", ("L_KEEP", "L_PRORATA", "L_CREDIT", "L_NOLIAB"), RED),
    ("Credit or refund for canceled games", ("CR",), NAVY),
    ("Club or league decides", ("DISC",), FAINT),
    ("Sales final, or no clause on the page", ("FINAL",), PALE),
    ("No public terms found", ("NONE",), None),
]

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

with DATA.open(newline="") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 30 and len({r["club"] for r in rows}) == 30
by = {r["club"]: r for r in rows}
cat = Counter(r["category"] for r in rows)
group_count = {label: sum(cat[c] for c in cats) for label, cats, _ in GROUPS}
lockout = [r for r in rows if r["names_lockout"] == "yes"]
assert len(lockout) == 4 and group_count["Names a lockout"] == 4
assert group_count["Credit or refund for canceled games"] == 7 and group_count["Club or league decides"] == 10
assert group_count["Sales final, or no clause on the page"] == 7 and group_count["No public terms found"] == 2
assert sum(group_count.values()) == 30
# deadlines, from the refund_timing column
CLOCKS = [("Angels", "fan", 30), ("Giants", "fan", 30), ("Reds", "club", 60), ("Blue Jays", "club", 60)]
assert "thirty (30) days" in by["angels"]["quote"] and "thirty (30) days" in by["giants"]["quote"]
assert "60-days" in by["reds"]["quote"] and "sixty (60) days" in by["bluejays"]["quote"]
assert by["angels"]["refund_timing"].startswith("fan must") and by["giants"]["refund_timing"].startswith("fan must")
assert by["reds"]["refund_timing"].startswith("refund within 60") and by["bluejays"]["refund_timing"].startswith("as soon as 60")
NO_CLOCK = 30 - len(CLOCKS)
assert NO_CLOCK == 26
assert "41" in by["cubs"]["canceled_game_remedy"]
CAN_CANCEL_NOW, CAN_CANCEL_PROPOSED = HOME_GAMES_NOW - CUBS_LINE, HOME_GAMES_PROPOSED - CUBS_LINE
assert (CAN_CANCEL_NOW, CAN_CANCEL_PROPOSED) == (40, 36)
# the shortened quotes drawn in fig-02 must be substrings of the CSV quotes
SHORT = {"reds": "refunded within 60-days of the confirmed cancellation of games",
         "dbacks": "a credit that can be applied to future Club games",
         "cubs": "retained by Club and applied to the following Season",
         "yankees": "obligated to settle or vote to settle any strike, lockout or work stoppage"}
for club, q in SHORT.items():
    assert q in by[club]["quote"], club
print(f"data: 30 clubs; groups {group_count}; clocks {len(CLOCKS)}, none {NO_CLOCK}; Cubs line {CUBS_LINE}: "
      f"{CAN_CANCEL_NOW} and {CAN_CANCEL_PROPOSED}")

# --------------------------------------------------------------------------
# Assert against the draft and captions
# --------------------------------------------------------------------------

draft = DRAFT.read_text()
captions = CAPTIONS.read_text()
DRAFT_PHRASES = (
    "Four of them mention a lockout or strike at all. Seven more promise a credit or refund",
    "The other 19 leave it to the club, say sales are final, or have no public terms",
    "Ten clubs leave the remedy to themselves or to the league",
    "Seven say sales are final or have no canceled-game clause on the public page",
    "Two clubs, the Mets and Athletics, have no public season-ticket terms",
    f"A baseball season has {HOME_GAMES_NOW} home games", f"whether {CUBS_LINE} of them are played",
    f"up to {CAN_CANCEL_NOW} home games can be canceled", f"154 games from 2029, which is {HOME_GAMES_PROPOSED} home dates",
    f"allows {CAN_CANCEL_PROPOSED} cancellations",
    "The Angels and Giants give the fan 30 days to ask. The Reds give themselves 60 days to pay. The Blue Jays say \"as soon as\" 60 days. The other 26 clubs state no payment clock",
) + tuple(r["quote"] for r in lockout) + (by["angels"]["quote"], by["giants"]["quote"], by["bluejays"]["quote"],
                                           by["tigers"]["quote"], by["marlins"]["quote"], by["redsox"]["quote"])
for phrase in DRAFT_PHRASES:
    assert phrase in draft, f"draft no longer says: {phrase}"
for club in NAMES.values():
    assert club in draft, f"draft never names the {club}"
print(f"draft matches the data: {len(DRAFT_PHRASES)} phrases, all 30 club names")

CAPTION_PHRASES = (
    "Four name a lockout or strike: the Cubs, Reds, Diamondbacks and Yankees. Seven promise a credit or refund",
    "Ten leave the remedy to the club or the league, seven say sales are final or have no canceled-game clause on the public page, and two",
    f"fewer than {CUBS_LINE} home games are played", "give the fan 30 days", "give themselves 60 days", "The other 26 clubs state no payment clock",
    f"On the {HOME_GAMES_NOW}-game home schedule, that leaves {CAN_CANCEL_NOW} games", f"On the {HOME_GAMES_PROPOSED}-game home schedule",
    f"the same line allows {CAN_CANCEL_PROPOSED}",
)
for phrase in CAPTION_PHRASES:
    assert phrase in captions, f"captions.md no longer says: {phrase}"
for key in KEYS:
    assert f"**{key}**" in captions and f"captions.md, {key}]" in draft, key
print(f"captions match the data ({len(CAPTION_PHRASES)} phrases) and all four draft slots exist")

# --------------------------------------------------------------------------
# SVG helpers (house style)
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'font-family="{FONT}"><title>{esc(title)}</title>{FONT_STYLE}']
        self.rect(0, 0, w, h, PAPER)

    def text(self, x, y, s, size, fill=NAVY, anchor="start", spacing=None, italic=False):
        extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
        if spacing:
            extra += f' letter-spacing="{spacing}"'
        if italic:
            extra += ' font-style="italic"'
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke=None, sw=1):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def write(self, stem):
        self.parts.append("</svg>")
        svg = OUT / f"{stem}.svg"
        svg.write_text("".join(self.parts))
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


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]

# --------------------------------------------------------------------------
# Fig 01: the grid
# --------------------------------------------------------------------------

def fig_club_grid(stem):
    title = "Four teams' contracts mention a lockout. One promises cash back on a clock."
    sub1 = "All 30 clubs by what their public season-ticket or ticket terms say about canceled games, read October 8, 2026."
    order = []
    for label, cats, color in GROUPS:
        order += [(r, label, color) for r in rows if r["category"] in cats]
    assert len(order) == 30
    COLS, TW, TH, GAP = 6, 172, 56, 12
    X0, Y0 = 48, 176
    H = Y0 + 5 * (TH + GAP) + 40
    s = SVG(1200, H, title)
    header(s, title, sub1)
    # legend
    x = 48
    for label, _, color in GROUPS:
        n = group_count[label]
        if color:
            s.rect(x, 124, 14, 12, color)
        else:
            s.rect(x, 124, 14, 12, PAPER, stroke=FAINT)
        s.text(x + 20, 135, f"{label} ({n})", 13, NAVY)
        x += 20 + len(f"{label} ({n})") * 5.9 + 18
    for i, (r, label, color) in enumerate(order):
        cx, cy = X0 + (i % COLS) * (TW + GAP), Y0 + (i // COLS) * (TH + GAP)
        if color:
            s.rect(cx, cy, TW, TH, color)
            ink = PAPER if color in (RED, NAVY) else NAVY
        else:
            s.rect(cx, cy, TW, TH, PAPER, stroke=FAINT)
            ink = MUTED
        s.text(cx + 14, cy + 34, NAMES[r["club"]], 17, ink)
    s.text(48, H - 14, "Source: each club's posted terms, URLs in data/club-terms.csv. Grouping is my reading of the "
                       "public page; individual and premium contracts can differ.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 02: the four lockout clauses
# --------------------------------------------------------------------------

def fig_lockout_table(stem):
    title = "The four clauses that name a lockout, best to worst for the fan."
    sub1 = "What each club's public season-ticket terms say happens to your money. Quotes verbatim, cut to the operative words."
    table = [
        ("Reds", "Fees cut pro rata per canceled game; credit, or refund on written request", "Club pays within 60 days", SHORT["reds"]),
        ("Diamondbacks", "Credit toward future games; no refund", "None stated", SHORT["dbacks"]),
        ("Cubs", f"Under {CUBS_LINE} home games: club keeps fees for next season. {CUBS_LINE} or more: no refund for canceled games", "None stated", SHORT["cubs"]),
        ("Yankees", "Not liable for force majeure; tickets not refundable; no remedy stated", "None stated", SHORT["yankees"]),
    ]
    X = [48, 215, 585, 780]
    HEAD_Y, HEAD_H, ROW_H = 130, 40, 96
    H = HEAD_Y + HEAD_H + ROW_H * 4 + 70
    s = SVG(1200, H, title)
    header(s, title, sub1)
    s.rect(48, HEAD_Y, 1104, HEAD_H, NAVY)
    for x, label in zip(X, ("CLUB", "WHAT HAPPENS TO YOUR MONEY", "DEADLINE", "THE WORDS")):
        s.text(x + (20 if x == 48 else 0), HEAD_Y + 26, label, 12, PAPER, spacing=1.8)
    for i, (club, money, clock, quote) in enumerate(table):
        y = HEAD_Y + HEAD_H + i * ROW_H
        if club == "Reds":
            s.rect(48, y, 1104, ROW_H, RED_TINT)
            s.rect(48, y, 4, ROW_H, RED)
        s.line(48, y + ROW_H, 1152, y + ROW_H, GRID, 1)
        s.text(68, y + 36, club, 18, RED if club == "Reds" else NAVY)
        for j, line in enumerate(wrap(money, 44)):
            s.text(X[1], y + 30 + j * 20, line, 14, NAVY)
        s.text(X[2], y + 30, clock, 14, RED if club == "Reds" else MUTED)
        for j, line in enumerate(wrap(f"“{quote}”", 52)):
            s.text(X[3], y + 30 + j * 20, line, 13, NAVY, italic=True)
    s.text(48, H - 32, "Source: Cubs, Reds, Diamondbacks and Yankees season-ticket terms as posted October 8, 2026 "
                       "(data/club-terms.csv). My reading of the language, not legal advice.", 12, MUTED)
    s.text(48, H - 14, "The Cubs' terms also say invoice payments stay due on schedule during a lockout.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 03: refund clocks
# --------------------------------------------------------------------------

def fig_refund_clocks(stem):
    title = f"Where a deadline exists, it usually runs against the fan. {NO_CLOCK} clubs state none."
    sub1 = "Every payment or request deadline in the 30 clubs' public terms, and who it binds."
    X0, X1, VMAX = 300, 1000, 90
    xs = lambda d: X0 + (X1 - X0) * d / VMAX
    Y0, PITCH, BH = 170, 62, 30
    H = Y0 + PITCH * 4 + 110
    s = SVG(1200, H, title)
    header(s, title, sub1)
    s.rect(48, 128, 14, 12, RED)
    s.text(68, 139, "the fan must act", 14, NAVY)
    s.rect(220, 128, 14, 12, NAVY)
    s.text(240, 139, "the club must pay", 14, NAVY)
    notes = {"Angels": "to request a refund, or it is \"forever waived\"", "Giants": "to request a refund instead of a credit",
             "Reds": "to refund, from the league confirming the cancellation", "Blue Jays": "\"in as soon as\" 60 days from the game date"}
    for i, (club, who, days) in enumerate(CLOCKS):
        y = Y0 + i * PITCH
        col = RED if who == "fan" else NAVY
        s.text(X0 - 16, y + 21, club, 15, NAVY, anchor="end")
        s.rect(X0, y, xs(days) - X0, BH, col)
        s.text(xs(days) + 10, y + 21, f"{days} days", 15, col)
        s.text(xs(days) + 90, y + 21, notes[club], 13, MUTED)
    y_ax = Y0 + PITCH * 4 - 10
    s.line(X0, y_ax, X1, y_ax, NAVY, 1.5)
    for d in (0, 30, 60, 90):
        s.text(xs(d), y_ax + 22, str(d), 12, MUTED, anchor="middle")
    s.text(X0, y_ax + 58, f"The other {NO_CLOCK} clubs state no clock of any kind.", 15, NAVY)
    s.text(48, H - 14, "Source: data/club-terms.csv, each club's posted terms read October 8, 2026.", 12, MUTED)
    s.write(stem)


# --------------------------------------------------------------------------
# Fig 04: the Cubs' 41-game line
# --------------------------------------------------------------------------

def fig_cubs_line(stem):
    title = f"The Cubs' line is {CUBS_LINE} home games: {CAN_CANCEL_NOW} can be canceled with no refund owed."
    sub1 = f"Home games in a season, and what the Cubs' terms owe for canceled ones. Below {CUBS_LINE}, fees roll to next season; at {CUBS_LINE} or more, nothing."
    X0, X1, VMAX = 300, 1110, HOME_GAMES_NOW
    xs = lambda g: X0 + (X1 - X0) * g / VMAX
    Y0, PITCH, BH = 176, 110, 40
    H = Y0 + PITCH * 2 + 70
    s = SVG(1200, H, title)
    header(s, title, sub1)
    for i, (label, sub, games, can) in enumerate(((f"{HOME_GAMES_NOW} home games", "the 162-game schedule", HOME_GAMES_NOW, CAN_CANCEL_NOW),
                                                  (f"{HOME_GAMES_PROPOSED} home games", "MLB's October 8 proposal, from 2029", HOME_GAMES_PROPOSED, CAN_CANCEL_PROPOSED))):
        y = Y0 + i * PITCH
        s.text(X0 - 16, y + 18, label, 15, NAVY, anchor="end")
        s.text(X0 - 16, y + 36, sub, 12, MUTED, anchor="end")
        s.rect(X0, y, xs(CUBS_LINE) - X0, BH, NAVY)
        s.rect(xs(CUBS_LINE) + 2, y, xs(games) - xs(CUBS_LINE) - 2, BH, RED)
        s.text(X0 + 12, y + 26, f"{CUBS_LINE} played: a full season", 14, PAPER)
        s.text(xs(CUBS_LINE) + 14, y + 26, f"{can} can be canceled, no refund", 14, PAPER)
    s.line(xs(CUBS_LINE), Y0 - 16, xs(CUBS_LINE), Y0 + PITCH + BH + 12, NAVY, 1.5, dash="4 5")
    s.text(xs(CUBS_LINE), Y0 - 24, f"{CUBS_LINE}-game line", 13, NAVY, anchor="middle")
    y_ax = Y0 + PITCH + BH + 24
    s.line(X0, y_ax, X1, y_ax, NAVY, 1.5)
    for g in (0, 20, 41, 60, 77, 81):
        s.text(xs(g), y_ax + 20, str(g), 12, MUTED, anchor="middle")
    s.text(48, H - 14, f"Source: Cubs season-ticket terms, October 8, 2026 (the {CUBS_LINE}-game threshold). The {CAN_CANCEL_NOW} and "
                       f"{CAN_CANCEL_PROPOSED} are arithmetic. My reading, not legal advice.", 12, MUTED)
    s.write(stem)


fig_club_grid(KEYS[0])
fig_lockout_table(KEYS[1])
fig_refund_clocks(KEYS[2])
fig_cubs_line(KEYS[3])
print("done ->", OUT)
