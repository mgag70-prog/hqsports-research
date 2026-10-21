#!/usr/bin/env python3
"""mlb-floor-2026: compare every club's 2026 Spotrac tax payroll (includes player benefits)
with the owners' proposed 2027 cap ($245.3M) and floor ($171.2M), and check the numbers the
draft uses. Writes data/2026-vs-cap-floor.csv. Fails loudly if anything drifts.
Run from repo root: python3 mlb-floor-2026/model/recompute.py"""
import csv, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / "data"
fails = []
def check(name, got, want, tol=0.05):
    ok = abs(got - want) <= tol if isinstance(want, (int, float)) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)

def money(s):
    s = (s or "").replace("$", "").replace(",", "").strip()
    return 0.0 if s in ("", "-") else float(s)

ctx = {r["key"]: r for r in csv.DictReader(open(D / "context.csv"))}
CAP = float(ctx["cap_2027"]["value"]); FLOOR = float(ctx["floor_2027"]["value"])
lines = open(D / "spotrac-tax-by-season.csv").read().splitlines()[1:]
tax = [r for r in csv.DictReader(lines) if r["season"] == "2026"]
check("clubs in 2026 tax table", len(tax), 30, 0)

post = {r["team"]: r for r in csv.DictReader(open(D / "postseason-2026.csv"))}
check("postseason clubs", len(post), 12, 0)

rows = []
for r in tax:
    p = money(r["Tax Payroll"]) / 1e6
    w, l = (int(x) for x in r["Record"].split("-"))
    status = "over cap" if p > CAP else ("under floor" if p < FLOOR else "inside")
    change = (CAP - p) if p > CAP else ((FLOOR - p) if p < FLOOR else 0.0)
    rows.append(dict(team=r["team"], tax_payroll_m=round(p, 2), wins=w, losses=l,
                     payroll_rank=int(r["Rank"]), status=status, change_to_comply_m=round(change, 2),
                     postseason=post.get(r["team"], {}).get("round_reached", "")))
rows.sort(key=lambda x: -x["tax_payroll_m"])
by = {x["team"]: x for x in rows}

# win ranks
wins_sorted = sorted(rows, key=lambda x: -x["wins"])
for i, x in enumerate(wins_sorted, 1): x["wins_rank"] = i

with open(D / "2026-vs-cap-floor.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

over = [x for x in rows if x["status"] == "over cap"]
under = [x for x in rows if x["status"] == "under floor"]
cut = sum(x["tax_payroll_m"] - CAP for x in over)
add = sum(FLOOR - x["tax_payroll_m"] for x in under)

print("\n-- headline facts --")
check("clubs over cap", len(over), 9, 0)
check("clubs under floor", len(under), 12, 0)
check("cut from over-cap clubs ($M)", round(cut, 1), 627.3)
check("added by under-floor clubs ($M)", round(add, 1), 548.3)
check("net change to players ($M)", round(add - cut, 1), -79.0)

check("MIL tax payroll", by["MIL"]["tax_payroll_m"], 154.71, 0.005)
check("MIL payroll rank", by["MIL"]["payroll_rank"], 19, 0)
check("MIL record", (by["MIL"]["wins"], by["MIL"]["losses"]), (103, 59))
check("MIL wins rank", by["MIL"]["wins_rank"], 1, 0)
check("MIL under floor by", round(FLOOR - by["MIL"]["tax_payroll_m"], 1), 16.5)
check("LAD tax payroll", by["LAD"]["tax_payroll_m"], 433.06, 0.005)
check("LAD record", (by["LAD"]["wins"], by["LAD"]["losses"]), (100, 62))
check("LAD wins rank", by["LAD"]["wins_rank"], 2, 0)
check("LAD over cap by", round(by["LAD"]["tax_payroll_m"] - CAP, 1), 187.8)
check("TB tax payroll", by["TB"]["tax_payroll_m"], 113.23, 0.005)
check("TB record", (by["TB"]["wins"], by["TB"]["losses"]), (98, 64))
check("TB wins rank", by["TB"]["wins_rank"], 3, 0)
check("TB under floor by", round(FLOOR - by["TB"]["tax_payroll_m"], 1), 58.0)
check("CLE tax payroll", by["CLE"]["tax_payroll_m"], 92.58, 0.005)
check("CLE payroll rank", by["CLE"]["payroll_rank"], 29, 0)
check("CLE record", (by["CLE"]["wins"], by["CLE"]["losses"]), (85, 77))
check("CLE under floor by", round(FLOOR - by["CLE"]["tax_payroll_m"], 1), 78.6)
check("final-four small three under floor", all(by[t]["status"] == "under floor" for t in ("MIL", "TB", "CLE")), True)
check("LAD minus MIL+TB+CLE ($M)", round(by["LAD"]["tax_payroll_m"] - sum(by[t]["tax_payroll_m"] for t in ("MIL","TB","CLE")), 1), 72.5)

# -- the pennants: both World Series clubs under the floor, and their payrolls together against the Dodgers' --
ws = sorted(t for t, r in post.items() if r["round_reached"] == "World Series")
check("World Series clubs", ws, ["MIL", "TB"])
check("both World Series clubs under floor", all(by[t]["status"] == "under floor" for t in ws), True)
check("LAD out in the LCS to MIL", (post["LAD"]["round_reached"], post["LAD"]["eliminated_by"]), ("LCS", "MIL"))
check("CLE out in the LCS to TB", (post["CLE"]["round_reached"], post["CLE"]["eliminated_by"]), ("LCS", "TB"))
check("ALCS result recorded", ctx["alcs_result"]["value"].startswith("Rays def. Guardians 4-2 (Game 6: Rays 7-3"), True)
ws_combined = round(sum(by[t]["tax_payroll_m"] for t in ws), 2)
check("World Series payrolls combined ($M)", ws_combined, 267.94, 0.005)
check("LAD minus World Series payrolls combined ($M)", round(by["LAD"]["tax_payroll_m"] - ws_combined, 1), 165.1)

# cross-check against MLB figures reported by CBS Oct 13 (within $1M)
for t in ("LAD", "MIL", "TB", "CLE"):
    ref = float(ctx[f"cbs_oct13_{t}_cbt"]["value"])
    check(f"{t} within $1M of CBS/MLB figure", abs(by[t]["tax_payroll_m"] - ref) <= 1.0, True)

post_under = [x["team"] for x in rows if x["postseason"] and x["status"] == "under floor"]
post_over = [x["team"] for x in rows if x["postseason"] and x["status"] == "over cap"]
print("postseason clubs under floor:", post_under, " over cap:", post_over)
w_over = sum(x["wins"] for x in over) / len(over); w_under = sum(x["wins"] for x in under) / len(under)
print(f"avg wins over-cap {w_over:.1f}, under-floor {w_under:.1f}")
print("over cap:", [(x['team'], x['tax_payroll_m']) for x in over])
print("under floor:", [(x['team'], x['tax_payroll_m'], x['wins']) for x in under])

# -- the rest of what the draft states --
print("\n-- draft facts --")
inside = [x for x in rows if x["status"] == "inside"]
check("clubs inside the lines", len(inside), 9, 0)
check("avg wins over-cap", round(w_over, 1), 88.3)
check("avg wins under-floor", round(w_under, 1), 80.0)
post_rows = [x for x in rows if x["postseason"]]
check("postseason over cap", len(post_over), 7, 0)
check("postseason under floor", len(post_under), 4, 0)
check("postseason under-floor clubs", sorted(post_under), ["CHW", "CLE", "MIL", "TB"])
check("postseason inside", [x["team"] for x in post_rows if x["status"] == "inside"], ["HOU"])
series = [(r["team"], r["eliminated_by"]) for r in post.values() if r["eliminated_by"]]
mixed = [(loser, winner) for loser, winner in series
         if {by[loser]["status"], by[winner]["status"]} == {"under floor", "over cap"}]
check("series between under-floor and over-cap clubs", sorted(mixed), sorted([("NYY", "TB"), ("SD", "MIL"), ("LAD", "MIL")]))
check("all three went to the under-floor club", all(by[w]["status"] == "under floor" for _, w in mixed), True)
check("NYM tax payroll", by["NYM"]["tax_payroll_m"], 359.48, 0.005)
check("NYM payroll rank", by["NYM"]["payroll_rank"], 2, 0)
check("NYM record", (by["NYM"]["wins"], by["NYM"]["losses"]), (74, 88))
check("NYM is the most expensive non-playoff club", max((x for x in rows if not x["postseason"]), key=lambda x: x["tax_payroll_m"])["team"], "NYM")
bottom4 = rows[-4:]
check("four cheapest clubs", [x["team"] for x in bottom4], ["TB", "STL", "CLE", "MIA"])
check("four cheapest: add to reach floor", [round(FLOOR - x["tax_payroll_m"], 1) for x in bottom4], [58.0, 62.4, 78.6, 86.8])
check("STL under floor by", round(FLOOR - by["STL"]["tax_payroll_m"], 1), 62.4)
check("MIA under floor by", round(FLOOR - by["MIA"]["tax_payroll_m"], 1), 86.8)
check("CHC tax payroll (disclosure)", by["CHC"]["tax_payroll_m"], 269.22, 0.005)
check("CHC over cap", by["CHC"]["status"], "over cap")
benefits_gap = float(ctx["benefits_per_club_cbs"]["value"]) - float(ctx["spotrac_player_benefits_TB_2026"]["value"])
check("benefits gap CBS minus Spotrac ($M)", benefits_gap, 5.0)
check("MIL still under floor after the gap ($M)", round(FLOOR - by["MIL"]["tax_payroll_m"] - benefits_gap, 1), 11.5)
check("over-cap count matches CBS May count", len(over), int(ctx["cbs_may_over_cap"]["value"]), 0)
check("under-floor count matches CBS May count", len(under), int(ctx["cbs_may_under_floor"]["value"]), 0)
check("CBS May net change ($M)", float(ctx["cbs_may_net_change"]["value"]), -18.7)
check("MLB claim ($M)", float(ctx["mlb_claim_net_change"]["value"]), 39.0)
check("union claim ($M)", float(ctx["union_claim_loss"]["value"]), 500.0)

# -- the draft's wording, built from the numbers above --
import re
def norm(t): return re.sub(r"\s+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
fm = lambda v: f"${v:.1f} million"
fp = lambda t: f"${by[t]['tax_payroll_m']:.2f} million"
u = lambda t: round(FLOOR - by[t]["tax_payroll_m"], 1)
rec = lambda t: f"{by[t]['wins']}-{by[t]['losses']}"
DRAFT_PHRASES = [
    f"a cap of {fm(CAP)} and a floor of {fm(FLOOR)}",
    f"The Dodgers spent {fp('LAD')}, the most in baseball, {fm(by['LAD']['tax_payroll_m'] - CAP)} over the cap",
    f"The Brewers, who swept them, spent {fp('MIL')}, {by['MIL']['payroll_rank']}th of 30, {fm(u('MIL'))} under the floor",
    f"The Rays spent {fp('TB')}, {by['TB']['payroll_rank']}th, {fm(u('TB'))} under it; the Guardians {fp('CLE')}, {by['CLE']['payroll_rank']}th, {fm(u('CLE'))} under",
    f"{fm(by['LAD']['tax_payroll_m'] - sum(by[t]['tax_payroll_m'] for t in ('MIL', 'TB', 'CLE')))} more than the other three combined",
    "Nine clubs were over the cap, twelve were under the floor, and nine sat between the lines",
    f"cut {fm(cut)} and the twelve under the floor would add {fm(add)}, so players as a group would be paid {fm(cut - add)} less",
    f"players gaining ${int(float(ctx['mlb_claim_net_change']['value']))} million", f"lose more than ${int(float(ctx['union_claim_loss']['value']))} million",
    f"a cut of {fm(-float(ctx['cbs_may_net_change']['value']))}",
    f"The nine over-cap clubs averaged {w_over:.1f} wins; the twelve under the floor averaged {w_under:.1f}",
    f"{fp('NYM')}, a {rec('NYM')} record", f"Milwaukee's {rec('MIL')}", f"Tampa Bay's {rec('TB')}", f"the Dodgers' {rec('LAD')}",
    "seven were over the cap, four were under the floor (the Brewers, Rays, Guardians and White Sox) and one, Houston, was in between",
    "Rays over Yankees in the Division Series, Brewers over Padres in the other one, Brewers over Dodgers for the pennant",
    "the Rays, Cardinals, Guardians and Marlins", "add " + ", ".join(fm(u(t)) for t in ("TB", "STL", "CLE")) + f" and {fm(u('MIA'))}",
    f"still under the floor by about {fm(u('MIL') - benefits_gap)}",
    "Under the floor. In the World Series.", f"${by['CHC']['tax_payroll_m']:.2f} million", "$18,000,000",
    "The Rays beat the Guardians 7-3 in Game 6 at Tropicana Field on October 19th and won the series four games to two",
    f"Add the two World Series payrolls together and you get ${ws_combined:.2f} million, {fm(by['LAD']['tax_payroll_m'] - ws_combined)} less than the Dodgers' {fp('LAD')} on its own",
    f"The floor would have told the Brewers to spend {fm(u('MIL'))} more on a team that won {by['MIL']['wins']} games",
    f"spend {fm(by['LAD']['tax_payroll_m'] - CAP)} less on one that won {by['LAD']['wins']}",
]
draft_path = ROOT / "draft.md"
if draft_path.exists():
    draft = norm(draft_path.read_text())
    for ph in DRAFT_PHRASES:
        check(f"draft says: {ph[:70]}", norm(ph) in draft, True)
    check("draft has no em dashes", draft.count("—"), 0, 0)
    check("draft has no [UPDATE] placeholder left", "[UPDATE" in draft, False)

# -- the thread: every post under 280 with the link as 23 characters, every number verbatim in the draft --
thread_path = ROOT / "x-thread.md"
if draft_path.exists() and thread_path.exists():
    NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
    posts = re.split(r"^## Post \d+.*$", thread_path.read_text(), flags=re.M)[1:]
    check("thread has six posts", len(posts), 6, 0)
    for i, body in enumerate(posts, 1):
        text = "\n".join(l for l in body.strip().splitlines() if not l.startswith("Attach:")).strip()
        length = len(text.replace("[URL]", "x" * 23))
        check(f"post {i} length {length} under 280", length <= 280, True)
        for fig in NUMBER.findall(text):
            if fig.strip() and fig not in ("280", "23") and norm(fig) not in draft:
                check(f"post {i} figure in draft: {fig}", False, True)
    check("thread has no em dashes", thread_path.read_text().count("—"), 0, 0)
    check("thread has no [UPDATE] placeholder left", "[UPDATE" in thread_path.read_text(), False)

if fails:
    print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print(f"\nALL CHECKS PASS ({sum(1 for _ in open(__file__)) and 'see above'})")
