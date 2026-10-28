#!/usr/bin/env python3
"""mlb-2027-cap-2026: how far over the owners' proposed 2027 cap ($245.3M) clubs already are on
Spotrac's 2027 luxury-tax projections (fetched Oct 27, 2026), and which existing contracts exceed the
proposed individual limits. Run from repo root: python3 mlb-2027-cap-2026/model/recompute.py"""
import csv, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "data"
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
def money(s):
    s = (s or "").replace("$", "").replace(",", "").strip()
    return 0.0 if s in ("", "-") else float(s)
def read(name):
    lines = open(D / name).read().splitlines()[1:]
    return list(csv.DictReader(lines))
ctx = {r["key"]: r for r in csv.DictReader(open(D / "context.csv"))}
CAP = float(ctx["cap_2027"]["value"]); FLOOR = float(ctx["floor_2027"]["value"])
tax = read("spotrac-2027-tax.csv"); check("clubs", len(tax), 30, 0)
rows = []
for r in tax:
    proj = money(r["Tax Payroll"]) / 1e6
    guar = money(r["Active"]) / 1e6
    arb = money(r["Arbitration Projected"]) / 1e6
    pre = money(r["Pre-Arbitration Projected"]) / 1e6
    fixed = proj - guar - arb - pre        # benefits, minor league, pre-arb bonus pool
    signed = guar + fixed                  # signed contracts plus the fixed items, no projections
    rows.append(dict(team=r["team"], projected_m=round(proj, 2), guaranteed_m=round(guar, 2), arb_projected_m=round(arb, 2),
                     prearb_projected_m=round(pre, 2), fixed_items_m=round(fixed, 2), signed_basis_m=round(signed, 2),
                     over_cap_projected_m=round(proj - CAP, 2), over_cap_signed_m=round(signed - CAP, 2), roster=int(r["Roster"])))
rows.sort(key=lambda x: -x["projected_m"])
with open(D / "2027-vs-cap.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
by = {x["team"]: x for x in rows}
over_p = [x for x in rows if x["projected_m"] > CAP]; over_s = [x for x in rows if x["signed_basis_m"] > CAP]
under_p = [x for x in rows if x["projected_m"] < FLOOR]
print("\n-- clubs --")
check("over cap, projected", len(over_p), 8, 0)
check("over cap, projected, $M above", round(sum(x["projected_m"] - CAP for x in over_p), 1), 539.1)
check("over cap, signed contracts only", len(over_s), 5, 0)
check("over cap signed-only teams", sorted(x["team"] for x in over_s), sorted(["LAD", "NYY", "PHI", "NYM", "SD"]))
check("over cap signed-only, $M above", round(sum(x["signed_basis_m"] - CAP for x in over_s), 1), 249.6)
check("LAD projected", by["LAD"]["projected_m"], 393.81, 0.005)
check("LAD over cap projected", round(by["LAD"]["projected_m"] - CAP, 1), 148.5)
check("LAD guaranteed", by["LAD"]["guaranteed_m"], 355.84, 0.005)
check("LAD guaranteed alone over cap", round(by["LAD"]["guaranteed_m"] - CAP, 1), 110.5)
check("LAD fixed items", by["LAD"]["fixed_items_m"], 22.92, 0.01)
print("projected under floor:", len(under_p), [x["team"] for x in under_p])
print("signed-basis over cap (from cent-rounded rows; exact gaps below):", [(x["team"], x["signed_basis_m"]) for x in over_s])
print("projected over cap:", [(x["team"], x["projected_m"], round(x["projected_m"] - CAP, 1)) for x in over_p])
for t in ("MIL", "TB"): print(t, by[t])

print("\n-- players --")
pl = read("spotrac-2027-player-tax.csv")
lim15 = CAP * 0.15; lim16 = CAP * 0.16
check("15% of cap ($M)", round(lim15, 3), 36.795, 0.001)
check("16% of cap ($M)", round(lim16, 3), 39.248, 0.001)
a15 = [p for p in pl if money(p["luxury_tax_2027"]) / 1e6 > lim15]
a16 = [p for p in pl if money(p["luxury_tax_2027"]) / 1e6 > lim16]
check("players above 15% of cap", len(a15), 8, 0)
check("players above 16% of cap", len(a16), 7, 0)
print("above 15%:", [(p["player"], p["team"], money(p["luxury_tax_2027"]) / 1e6) for p in a15])
check("Tucker 2027 tax", money(next(p for p in pl if p["player"] == "Kyle Tucker")["luxury_tax_2027"]) / 1e6, 57.195, 0.001)
check("Ohtani 2027 tax", money(next(p for p in pl if p["player"] == "Shohei Ohtani")["luxury_tax_2027"]) / 1e6, 46.081476, 0.000001)
ct = read("spotrac-top-contracts.csv")
MAXT = float(ctx["max_contract_total"]["value"])
big = [c for c in ct if money(c["value"]) / 1e6 > MAXT and int(c["end"]) >= 2027]
check("running contracts above $265M total", len(big), 18, 0)
print("above $265M:", [(c["player"], c["team"], money(c["value"]) / 1e6) for c in big])
check("Soto value", money(next(c for c in ct if c["player"] == "Juan Soto")["value"]) / 1e6, 765.0, 0.001)

# -- exact dollars: the rows above are rounded to cents before subtracting, which can flip a tenth --
print("\n-- exact figures for the draft --")
X = {}
for r in tax:
    proj = money(r["Tax Payroll"]) / 1e6; guar = money(r["Active"]) / 1e6
    arb = money(r["Arbitration Projected"]) / 1e6; pre = money(r["Pre-Arbitration Projected"]) / 1e6
    X[r["team"]] = dict(proj=proj, guar=guar, arb=arb, pre=pre, fixed=proj - guar - arb - pre, signed=proj - arb - pre)
osig = lambda t: X[t]["signed"] - CAP
oproj = lambda t: X[t]["proj"] - CAP
uflo = lambda t: FLOOR - X[t]["proj"]
check("PHI signed over cap, exact ($M)", round(osig("PHI"), 2), 41.95, 0.005)
check("PHI signed over cap rounds to 42.0, not the outline's 41.9", f"{osig('PHI'):.1f}", "42.0")
check("signed-only over total, exact", round(sum(osig(t) for t in X if osig(t) > 0), 1), 249.6)
check("projected over total, exact", round(sum(oproj(t) for t in X if oproj(t) > 0), 1), 539.1)
check("signed-only order by gap", sorted((t for t in X if osig(t) > 0), key=lambda t: -osig(t)), ["LAD", "PHI", "NYY", "NYM", "SD"])
check("projected-only additions", sorted(t for t in X if oproj(t) > 0 and osig(t) <= 0), ["BOS", "HOU", "TOR"])
under_floor = [t for t in X if X[t]["proj"] < FLOOR]
check("projected under floor", len(under_floor), 12, 0)
check("TB under floor", "TB" in under_floor and "CLE" in under_floor and "MIL" not in under_floor, True)
check("MIL clears the floor only with projections", X["MIL"]["proj"] > FLOOR > X["MIL"]["signed"], True)
benefits = float(ctx["spotrac_2027_benefits_LAD"]["value"])
bonus_pool = money(re.search(r"pre-arb bonus pool (\$[\d,]+)", ctx["spotrac_2027_benefits_LAD"]["note"]).group(1)) / 1e6
minor = X["LAD"]["fixed"] - benefits - bonus_pool
check("LAD minor league line, fixed items less benefits and bonus pool ($M)", round(minor, 4), 2.75, 0.0001)
check("CHC under cap (disclosure)", X["CHC"]["proj"] < CAP, True)
tuck = money(next(p for p in pl if p["player"] == "Kyle Tucker")["luxury_tax_2027"]) / 1e6
oht = money(next(p for p in pl if p["player"] == "Shohei Ohtani")["luxury_tax_2027"]) / 1e6
check("Tucker + Ohtani ($M)", round(tuck + oht, 2), 103.28, 0.001)
check("Tucker + Ohtani share of cap (%)", round(100 * (tuck + oht) / CAP, 1), 42.1)
check("Tucker share of cap (%)", round(100 * tuck / CAP, 1), 23.3)
oht_aav = money(next(c for c in ct if c["player"] == "Shohei Ohtani")["aav"]) / 1e6
check("Ohtani nominal AAV ($M)", oht_aav, 70.0, 0.001)
soto_total = money(next(c for c in ct if c["player"] == "Juan Soto")["value"]) / 1e6
check("Soto total over max", round(soto_total / MAXT, 1), 2.9)
big_teams = [c["team"] for c in big]
check("contracts over $265M: three each for LAD, NYY, SD", [big_teams.count(t) for t in ("LAD", "NYY", "SD")], [3, 3, 3])
check("no other club holds more than two", max(big_teams.count(t) for t in set(big_teams) - {"LAD", "NYY", "SD"}), 2, 0)
witt = next(c for c in big if c["player"] == "Bobby Witt Jr.")
check("Witt is KC's one", (witt["team"], big_teams.count("KC")), ("KC", 1))
pmap = {p["player"]: money(p["luxury_tax_2027"]) / 1e6 for p in pl}
a15_names = [p["player"] for p in a15]
check("deGrom is the one between 15% and 16%", [n for n in a15_names if pmap[n] <= lim16], ["Jacob deGrom"])
check("max switch total vs context ($M)", float(ctx["max_switch_total"]["value"]), 202.0)
NHL = float(ctx["nhl_2005_rollback"]["value"])
check("NHL rollback (%)", NHL, 24.0)

# -- the draft's wording, built from the numbers above --
def norm(t): return re.sub(r"\s+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
f1 = lambda v: f"${v:.1f} million"; f2 = lambda v: f"${v:.2f} million"; f3 = lambda v: f"${v:.3f} million"
def ctx_says(key, *bits):
    for b in bits: check(f"context {key} has {b!r}", b in ctx[key]["value"] + " " + ctx[key]["note"], True)
ctx_says("cba_expires", "11:59 p.m. ET", "December 1, 2026"); ctx_says("spring_training", "February 9, 2027"); ctx_says("opening_day", "March 24, 2027")
ctx_says("ws_game1", "Brewers 3, Rays 2", "Oct 23", "Milwaukee")
ctx_says("ws_status", "Brewers lead 3-1", "Game 1 Brewers 3-2, Oct 23", "Game 2 Brewers 5-4, Oct 24", "Game 3 Brewers 10-1, Oct 26",
         "Game 4 Rays 4-3 in 12 innings, Oct 27", "Game 5 Wednesday Oct 28, 8 p.m. ET, at Tampa Bay")
ws_scores = {int(g): sc for g, sc in re.findall(r"Game (\d) \w+ (\d+-\d+)", ctx["ws_status"]["value"])}
check("World Series: Brewers won games 1 to 3, Rays game 4", re.findall(r"Game \d (\w+) \d", ctx["ws_status"]["value"]), ["Brewers"] * 3 + ["Rays"])
ctx_says("manfred_quote", "Once every 40 years is not enough.")
ctx_says("manfred_quote2", "It's not that no small market can win, it's just that it's pretty rare."); ctx_says("meyer_quote", "nuclear bomb")
ctx_says("existing_contracts_treatment", "Not mentioned is what to do about teams like the Los Angeles Dodgers and New York Mets")
ctx_says("max_rules_scope", "raises capped at 5%"); ctx_says("max_cornerstone_pct", "Cornerstone Player")
ctx_says("cap_2027", "based on luxury tax payroll figures"); ctx_says("mlb_clubs_decrease", "8")
DRAFT_PHRASES = [
    f"${round(osig('LAD'))} million over a 2027 salary cap",
    f"The owners' proposed 2027 cap is {f1(CAP)}", f"a combined {f1(sum(oproj(t) for t in X if oproj(t) > 0))} over",
    f"The Cubs' projected 2027 payroll is {f2(X['CHC']['proj'])}, {f1(CAP - X['CHC']['proj'])} under the cap",
    f"The Dodgers have {f2(X['LAD']['guar'])} of signed deals on the 2027 books, {f1(X['LAD']['guar'] - CAP)} over a {f1(CAP)} cap",
    f"{f1(benefits)} of player benefits, {f2(minor)} of minor league salaries and a ${bonus_pool * 1e6:,.0f} bonus pool",
    f"On signed contracts the Dodgers are at {f2(X['LAD']['signed'])}, {f1(osig('LAD'))} over",
    f"they're at {f2(X['LAD']['proj'])}, {f1(oproj('LAD'))} over",
    f"Kyle Tucker counts {f3(tuck)}", f"Shohei Ohtani counts {f2(oht)}", f"Spotrac lists at ${oht_aav:.0f} million a year",
    f"Together that's {f2(tuck + oht)}, {100 * (tuck + oht) / CAP:.1f}% of the cap for two players, and Tucker alone is {100 * tuck / CAP:.1f}% of it",
    "five clubs are over the cap: " + ", ".join(f"the {n} by {f1(osig(t))}" for n, t in (("Dodgers", "LAD"), ("Phillies", "PHI"), ("Yankees", "NYY"), ("Mets", "NYM")))
        + f" and the Padres by {f1(osig('SD'))}, {f1(sum(osig(t) for t in X if osig(t) > 0))} over in all",
    f"Boston ({f1(oproj('BOS'))} over), Houston ({f1(oproj('HOU'))}) and Toronto ({f1(oproj('TOR'))}), which makes eight clubs and {f1(sum(oproj(t) for t in X if oproj(t) > 0))}",
    f"to {f1(oproj('NYY'))}, because Spotrac expects them to pay {f2(X['NYY']['arb'])} in arbitration salaries",
    "Over the cap. Before the offseason.", "eight clubs' payrolls would decrease under the cap",
    f"starting at {ctx['max_switch_pct']['value']}% of the cap, which comes to ${float(ctx['max_switch_total']['value']):.0f} million",
    f"starting at {ctx['max_cornerstone_pct']['value']}%", f"largest contract the proposal allows at ${MAXT:.0f} million", "Raises would be capped at 5% a year",
    f"At a {f1(CAP)} cap, 15% is {f3(lim15)} and 16% is {f3(lim16)}",
    "Tucker (" + f3(pmap["Kyle Tucker"]) + "), Juan Soto (" + f1(pmap["Juan Soto"]) + "), Ohtani (" + f2(pmap["Shohei Ohtani"]) + "), Cody Bellinger ("
        + f2(pmap["Cody Bellinger"]) + "), Bo Bichette and Zack Wheeler (" + f1(pmap["Bo Bichette"]) + " each), Aaron Judge (" + f1(pmap["Aaron Judge"])
        + ") and Jacob deGrom (" + f1(pmap["Jacob deGrom"]) + ")",
    f"Eighteen contracts still running in 2027 are worth more in total than ${MAXT:.0f} million, and Soto's ${soto_total:.0f} million is {soto_total / MAXT:.1f} times that",
    "The Dodgers, Yankees and Padres hold three of the eighteen each", f"Bobby Witt Jr.'s {f1(money(witt['value']) / 1e6)}",
    f"every existing contract was cut {NHL:.0f}%",
    f"The Rays, at a projected {f2(X['TB']['proj'])}, are {f1(uflo('TB'))} under it; the Guardians, at {f2(X['CLE']['proj'])}, are {f1(uflo('CLE'))} under",
    f"Their projected {f2(X['MIL']['proj'])} clears the floor, and {f1(X['MIL']['arb'])} of it is projected arbitration salaries; on signed contracts alone they're at {f2(X['MIL']['signed'])}",
    f"Twelve clubs project under the {f1(FLOOR)} floor", f"a {f1(osig('LAD'))} problem on the Dodgers' desk",
    f"The Padres are the soft one: {f1(osig('SD'))} over on signed contracts", f"It would have to rise past {f2(X['LAD']['signed'])} to clear the Dodgers",
    "Going into Game 5, the Brewers lead the World Series three games to one",
    f"They won {ws_scores[1]} in Milwaukee on October 23, {ws_scores[2]} the next night and {ws_scores[3]} on October 26, and the Rays stayed alive on October 27 with a {ws_scores[4]} win in 12 innings",
    "Game 5 is tonight, Wednesday, October 28, at 8 p.m. ET in Tampa Bay",
    "If the next agreement includes a hard cap, based on what is being reported, it includes a transition rule",
    f"The Phillies' signed-contracts gap is {f1(osig('PHI'))}, not the outline's $41.9 million: the exact figure is {f2(osig('PHI'))}",
]
# every number in the body (above "Not for publication") has to be one of these, each built from the model or context.csv
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = {f1(v) for v in (CAP, FLOOR, benefits, osig("SD"), oproj("BOS"), oproj("HOU"), oproj("TOR"), oproj("NYY"), uflo("TB"), uflo("CLE"),
                         X["LAD"]["guar"] - CAP, CAP - X["CHC"]["proj"], X["MIL"]["arb"], money(witt["value"]) / 1e6)}
KNOWN |= {f1(osig(t)) for t in ("LAD", "PHI", "NYY", "NYM")} | {f1(oproj("LAD")), f1(sum(osig(t) for t in X if osig(t) > 0)), f1(sum(oproj(t) for t in X if oproj(t) > 0))}
KNOWN |= {f2(v) for v in (X["CHC"]["proj"], X["LAD"]["guar"], X["LAD"]["signed"], X["LAD"]["proj"], minor, oht, tuck + oht, X["NYY"]["arb"],
                         X["TB"]["proj"], X["CLE"]["proj"], X["MIL"]["proj"], X["MIL"]["signed"])}
KNOWN |= {f3(tuck), f3(lim15), f3(lim16), f"${round(osig('LAD'))} million", f"${bonus_pool * 1e6:,.0f}", f"${oht_aav:.0f} million"}
KNOWN |= {f1(pmap[n]) for n in ("Juan Soto", "Bo Bichette", "Aaron Judge", "Jacob deGrom")} | {f2(pmap["Cody Bellinger"])}
KNOWN |= {f"{100 * (tuck + oht) / CAP:.1f}%", f"{100 * tuck / CAP:.1f}%", f"{soto_total / MAXT:.1f}", f"${soto_total:.0f} million", f"${MAXT:.0f} million",
          f"${float(ctx['max_switch_total']['value']):.0f} million", f"{ctx['max_switch_pct']['value']}%", f"{ctx['max_cornerstone_pct']['value']}%", "5%", f"{NHL:.0f}%"}
KNOWN |= {"2026", "2027"}                                   # the seasons
KNOWN |= set(ws_scores.values())                            # World Series scores, from context.csv ws_status
# day-of-month, the 11:59 deadline, Game 1's score and Manfred's "40 years" pass only in that wording (context.csv, checked above);
# a bare small number anywhere else fails
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}\b|"
                   r"Game [1-7]\b|11:59 p\.m\.|8 p\.m\. ET|in 12 innings|Once every 40 years|All 30 clubs")
KNOWN |= {"1998", "2021"}                                   # disclosure, on record in mlb-154-games-2026 and mlb-lockout-2026
KNOWN |= {"2004-05", "2005", "1994", "1984"}                # mlb-cap-valuations-2026/draft.md (NHL season, cap year; NFL and NBA cap years)
def stray_numbers(text, label, known=KNOWN):
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = NUMBER.findall(body)
    check(f"{label}: numbers scanned", len(scanned) > 20, True)
    for fig in scanned:
        fig = fig.rstrip(",")
        if fig and fig not in known: check(f"{label}: number not traced to the model: {fig}", False, True)
draft_path = ROOT / "draft.md"
if draft_path.exists():
    raw = draft_path.read_text(); draft = norm(raw)
    for ph in DRAFT_PHRASES:
        check(f"draft says: {ph[:70]}", norm(ph) in draft, True)
    stray_numbers(raw.split("## Not for publication")[0], "draft")
    check("draft has no em dashes", raw.count("—"), 0, 0)
    check("draft has no [UPDATE] marker left", raw.count("[UPDATE"), 0, 0)
    check("prediction confirmed (no [MATT TO CONFIRM] left in the body)", "[MATT TO CONFIRM" not in raw.split("## What this predicts")[1].split("---")[0], True)
    body_words = len(re.findall(r"\b[\w'.$%,-]+\b", raw.split("## Not for publication")[0]))
    print(f"draft body: about {body_words} words")

# -- captions: same number rule, no em dashes --
cap_path = ROOT / "figures" / "captions.md"
if cap_path.exists():
    captxt = cap_path.read_text()
    stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**")), "captions")
    check("captions have no em dashes", captxt.count("—"), 0, 0)

# -- the thread: six posts, every one under 280 with the link as 23 characters, every number verbatim in the draft --
thread_path = ROOT / "x-thread.md"
if draft_path.exists() and thread_path.exists():
    posts = re.split(r"^## Post \d+.*$", thread_path.read_text(), flags=re.M)[1:]
    check("thread has six posts", len(posts), 6, 0)
    for i, body in enumerate(posts, 1):
        text = "\n".join(l for l in body.strip().splitlines() if not l.startswith("Attach:")).strip()
        length = len(text.replace("[URL]", "x" * 23))
        check(f"post {i} length {length} under 280", length <= 280, True)
        for fig in NUMBER.findall(text):
            if fig.strip() and norm(fig) not in draft:
                check(f"post {i} figure in draft: {fig}", False, True)
    check("thread ends with the [URL] placeholder", posts[-1].strip().endswith("[URL]"), True)
    check("thread has no em dashes", thread_path.read_text().count("—"), 0, 0)

if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
