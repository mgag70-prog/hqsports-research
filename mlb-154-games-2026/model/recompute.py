"""
Recompute every figure in mlb-154-games-2026 from data/ and fail on any mismatch with the
numbers the outline and compute_notes.txt carry.

Inputs: data/attendance-2026-bref.csv, data/gate-per-game-2024-sportico.csv,
data/postseason-gate.csv, data/national-tv-deals.csv.

Run from the repo root:  python mlb-154-games-2026/model/recompute.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
HOME_DATES_NOW, HOME_DATES_PROPOSED, GAMES_NOW, GAMES_PROPOSED = 81, 77, 162, 154
LOST_DATES = HOME_DATES_NOW - HOME_DATES_PROPOSED
POOL_SHARE, CLUBS_SHARE_LATE, COMMISSIONER_SHARE = 0.60, 0.85, 0.15
ADDED_DS_GAMES = 8   # Games 6 and 7 in each of four best-of-seven Division Series
mismatches = []
checked = 0


def check(label, expected, computed, fmt):
    global checked
    checked += 1
    shown = fmt.format(computed)
    ok = shown == expected
    if not ok:
        mismatches.append((label, expected, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<52} expected {expected:>12}  computed {shown:>12}")


def load(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


att = load("attendance-2026-bref.csv")
gate = {r["club"]: float(r["gate_per_home_game_usd_m"]) for r in load("gate-per-game-2024-sportico.csv")}
post = {r["item"]: r["value"] for r in load("postseason-gate.csv")}
tv = load("national-tv-deals.csv")
assert len(att) == 30, len(att)
for r in att:
    assert int(r["four_dates"]) == LOST_DATES * int(r["per_game_2026"]), r["team"]
    assert int(r["dates"]) in (80, 81), r["team"]

print("ATTENDANCE, 2026 (Baseball-Reference)")
total = sum(int(r["attendance_2026"]) for r in att)
dates = sum(int(r["dates"]) for r in att)
per_game = total / dates
lost = sum(int(r["four_dates"]) for r in att)
check("Total attendance", "71,752,722", total, "{:,d}")
check("Per game (total / dates)", "29,540", per_game, "{:,.0f}")
check(f"Tickets from {LOST_DATES} fewer home dates per club", "3,545,372", lost, "{:,d}")
check("As a share of 2026 attendance, %", "4.94", 100 * lost / total, "{:.2f}")
by_team = {r["team"]: int(r["four_dates"]) for r in att}
check("Dodgers, 4 dates", "199,220", by_team["Los Angeles Dodgers"], "{:,d}")
check("Athletics, 4 dates", "39,468", by_team["Athletics"], "{:,d}")
ranked = sorted(by_team.items(), key=lambda kv: -kv[1])
assert ranked[0][0] == "Los Angeles Dodgers" and ranked[-1][0] == "Athletics"

print("\nGATE, 2024 per home game x 4 (Sportico)")
for club, exp in (("Los Angeles Dodgers", "17.16"), ("New York Yankees", "16.44"), ("Chicago Cubs", "13.00"),
                  ("Boston Red Sox", "11.72"), ("Houston Astros", "10.76"), ("Bottom of the league", "2.00")):
    check(f"{club}, 4 dates ($M)", exp, LOST_DATES * gate[club], "{:.2f}")

print("\nPOSTSEASON (Sportico Dec 2025; pool shares per MLB.com glossary; split per FanGraphs 2014)")
# The pool takes 50% of Wild Card gate and 60% of the other minimum games (MLB.com glossary), so one pool
# figure doesn't pin down the gate. Bound it: every pool game at 60% (low) and every pool game at 50% (high).
# The truth lies between; 8 of the 32 pool games were Wild Card games at 50%.
pool = float(post["players_pool_2025_usd"]) / 1e6
pool_games = int(post["pool_games_2025"])
wc_games = int(post["wild_card_pool_games_2025"])
POOL_SHARE_WC = float(post["pool_share_wild_card"])
assert POOL_SHARE == float(post["pool_share_ds_games_1_3"]) == float(post["pool_share_lcs_ws_games_1_4"])
assert POOL_SHARE_WC == 0.50 and 0 < wc_games < pool_games
BOUNDS = {"low": POOL_SHARE, "high": POOL_SHARE_WC}   # pool share applied to every pool game
implied_gate = {k: pool / v for k, v in BOUNDS.items()}
per_pool_game = {k: v / pool_games for k, v in implied_gate.items()}
added = {k: ADDED_DS_GAMES * v for k, v in per_pool_game.items()}
check("Players' pool 2025 ($M)", "128.2", pool, "{:.1f}")
check("Pool games", "32", pool_games, "{:d}")
check("  of which Wild Card games, pool at 50%", "8", wc_games, "{:d}")
for k, share, g, pg, a, c, cm in (("low", "60%", "213.7", "6.68", "53.4", "45.4", "8.0"),
                                  ("high", "50%", "256.4", "8.01", "64.1", "54.5", "9.6")):
    check(f"[{k}: all pool games at {share}] implied gate ($M)", g, implied_gate[k], "{:.1f}")
    check(f"[{k}] per pool game ($M), ESTIMATE", pg, per_pool_game[k], "{:.2f}")
    check(f"[{k}] {ADDED_DS_GAMES} added DS games ($M), best case", a, added[k], "{:.1f}")
    check(f"[{k}]   of which clubs, 85% ($M)", c, added[k] * CLUBS_SHARE_LATE, "{:.1f}")
    check(f"[{k}]   of which Commissioner, 15% ($M)", cm, added[k] * COMMISSIONER_SHARE, "{:.1f}")
    check(f"[{k}]   of which players' pool ($M)", "0.0", added[k] * 0, "{:.1f}")
assert "0% players' pool" in post["split_ds_games_4_plus"] and "85% two clubs" in post["split_ds_games_4_plus"]
assert "60% players' pool" in post["split_ds_games_1_3"] and "25% two clubs" in post["split_ds_games_1_3"]
assert "50% players' pool" in post["split_wc_games_1_2"] and "35% two clubs" in post["split_wc_games_1_2"]
dodger_loss = LOST_DATES * gate["Los Angeles Dodgers"]
ratio = {k: v / dodger_loss for k, v in added.items()}
check("Add-back / Dodgers' 4-date loss, low bound, rounded", "3", ratio["low"], "{:.0f}")
check("Add-back / Dodgers' 4-date loss, high bound, rounded", "4", ratio["high"], "{:.0f}")
print(f"       best-case add-back / Dodgers' 4-date loss: {ratio['low']:.2f} to {ratio['high']:.2f} (about three to four Dodger-sized losses)")

print("\nNATIONAL TV (listed; Apple excluded, not verified)")
tv_total = sum(float(r["annual_value_usd_m"]) for r in tv)
check("Annual value, all listed deals ($M)", "2,063.6", tv_total, "{:,.1f}")
assert all(r["term"].endswith("2028") for r in tv), "a listed deal does not end after 2028"
assert not any("Apple" in r["partner"] for r in tv)
for r in tv:
    print(f"       {r['partner']:<12} ${float(r['annual_value_usd_m']):>7.1f}M  {r['term']}")

print("\nPER GAME")
check("Pay per game, salaries unchanged, % more", "5.2", 100 * (GAMES_NOW / GAMES_PROPOSED - 1), "{:.1f}")
check("Home dates 81 -> 77, % change", "-4.9", 100 * (HOME_DATES_PROPOSED / HOME_DATES_NOW - 1), "{:.1f}")

print("\n" + (f"ALL {checked} FIGURES MATCH" if not mismatches else f"{len(mismatches)} MISMATCH(ES) in {checked} checks:"))
for label, e, c in mismatches:
    print(f"  {label}: expected {e}, computed {c}")
if mismatches:
    raise SystemExit(1)
