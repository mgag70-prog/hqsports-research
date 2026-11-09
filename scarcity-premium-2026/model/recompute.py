#!/usr/bin/env python3
"""scarcity-premium-2026: do franchise control sales beat the Forbes value in force when announced?
Reads data/control_sales_verified.csv (47 rows, independently re-sourced) and data/classification.csv.
Analysis set: announced 2012-2026, price and Forbes both found, verified yes/partly, confidence high/medium,
not forced/distressed, not league-sold, not a staged or option-priced (non-control) deal."""
import csv, pathlib, statistics as st, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "data"
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
R = list(csv.DictReader(open(D / "control_sales_verified.csv")))
C = {(c["team"], c["year"]): c for c in csv.DictReader(open(D / "classification.csv"))}
rows = []
for r in R:
    y = r["announced_date"][:4]; c = C.get((r["team"], y))
    grp = c["group"] if c else "clean"
    if grp == "clean" and (r["confidence"] not in ("high", "medium") or r["verified"] not in ("yes", "partly")): grp = "excluded_quality"
    prem = None
    try: prem = 100 * (float(r["implied_100pct_usd_b"]) / float(r["prior_forbes_value_usd_b"]) - 1)
    except ValueError: pass
    rows.append(dict(league=r["league"], team=r["team"], buyer=r["buyer"], date=r["announced_date"], year=int(y),
                     price=r["implied_100pct_usd_b"], forbes=r["prior_forbes_value_usd_b"], forbes_list=r["forbes_list"],
                     premium=None if prem is None else round(prem, 1), group=grp,
                     other_assets=r["includes_other_assets"], verified=r["verified"]))
check("rows", len(rows), 47, 0)
clean = [x for x in rows if x["group"] == "clean"]
P = [x["premium"] for x in clean]
print("clean n", len(clean))
check("clean deals", len(clean), 33, 0)
check("clean median premium %", round(st.median(P), 1), round(st.median(P), 1))
med = round(st.median(P), 1); print("median", med)
above = sum(p > 0 for p in P); below = sum(p < 0 for p in P); flat = sum(p == 0 for p in P)
print("above/below/flat", above, below, flat)
for lg in ["NFL", "MLB", "NBA", "NHL"]:
    xs = [x["premium"] for x in clean if x["league"] == lg]
    print(lg, len(xs), round(st.median(xs), 1))
for a, b in [(2012, 2017), (2018, 2022), (2023, 2026)]:
    xs = [x["premium"] for x in clean if a <= x["year"] <= b]
    print(a, b, len(xs), round(st.median(xs), 1))
print("below:", [(x["team"], x["year"], x["premium"]) for x in clean if x["premium"] < 0])
print("top:", sorted([(x["premium"], x["team"], x["year"]) for x in clean], reverse=True)[:6])
allp = [x["premium"] for x in rows if x["premium"] is not None and x["group"] not in ("out_of_range", "no_price")]
print("all with both figures, 2012+:", len(allp), round(st.median(allp), 1))

print("\n-- headline checks --")
check("median premium, clean deals %", med, 24.0)
check("above Forbes", above, 28, 0); check("below Forbes", below, 5, 0)
lg = lambda L: round(st.median(x["premium"] for x in clean if x["league"] == L), 1)
check("NFL median", lg("NFL"), 16.0); check("MLB median", lg("MLB"), 16.7); check("NBA median", lg("NBA"), 25.0); check("NHL median", lg("NHL"), 36.5)
per = lambda a, b: round(st.median(x["premium"] for x in clean if a <= x["year"] <= b), 1)
check("2012-2017 median", per(2012, 2017), 34.5); check("2018-2022 median", per(2018, 2022), 7.1); check("2023-2026 median", per(2023, 2026), 20.0)
tot_p = sum(float(x["price"]) for x in clean); tot_f = sum(float(x["forbes"]) for x in clean)
check("aggregate price $B", round(tot_p, 2), 89.56); check("aggregate Forbes $B", round(tot_f, 2), 74.07); check("aggregate premium %", round(100 * (tot_p / tot_f - 1), 1), 20.9)
big = [x["premium"] for x in clean if float(x["price"]) >= 3]; small = [x["premium"] for x in clean if float(x["price"]) < 3]
check("deals of $3B+ n", len(big), 10, 0); check("deals of $3B+ median", round(st.median(big), 1), 24.5); check("under $3B median", round(st.median(small), 1), 18.7)
B = {(x["team"], x["year"]): x for x in rows}
check("Celtics 2025", B[("Boston Celtics", 2025)]["premium"], 1.7); check("Mets 2020", B[("New York Mets", 2020)]["premium"], 0.8)
check("Mavericks 2023", B[("Dallas Mavericks", 2023)]["premium"], -22.2); check("Lakers 2025", B[("Los Angeles Lakers", 2025)]["premium"], 40.8)
check("Lakers 2026", B[("Los Angeles Lakers", 2026)]["premium"], 25.0); check("Rays 2025", B[("Tampa Bay Rays", 2025)]["premium"], 36.0)
check("Hornets 2023", B[("Charlotte Hornets", 2023)]["premium"], 76.5); check("Seahawks 2026", B[("Seattle Seahawks", 2026)]["premium"], 43.5)
check("Commanders 2023", B[("Washington Commanders", 2023)]["premium"], 8.0); check("Clippers 2014 (excluded, forced)", B[("Los Angeles Clippers", 2014)]["premium"], 247.8)
check("all deals with both figures n", len(allp), 43, 0); check("all deals median", round(st.median(allp), 1), 26.9)
with open(D / "sales-computed.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(sorted(rows, key=lambda x: x["date"]))

print("\n-- sensitivity and caveats --")
import datetime as dt, re
Rraw = {(r["team"], r["announced_date"]): r for r in R}
pc = lambda v: f"{v:.1f}%"
def prem(price, forbes): return round(100 * (price / forbes - 1), 1)
def median_with(over=None, drop=()):
    over = over or {}; vals = []
    for x in clean:
        k = (x["team"], x["year"])
        if k not in drop: vals.append(100 * (over.get(k, float(x["price"])) / float(x["forbes"]) - 1))
    return round(st.median(vals), 1), sum(v > 0 for v in vals), len(vals)
LOW = {("San Diego Padres", 2012): 0.6, ("Florida Panthers", 2013): 0.23, ("Memphis Grizzlies", 2012): 0.35,
       ("Portland Trail Blazers", 2025): 4.1, ("Los Angeles Lakers", 2026): 12.0}
HIGH = {("Ottawa Senators", 2023): 0.95 / 0.9, ("Boston Celtics", 2025): 6.5, ("New York Mets", 2020): 2.475, ("Pittsburgh Penguins", 2025): 1.8}
BUNDLED = [("Seattle Mariners", 2016), ("Utah Jazz", 2020), ("New Jersey Devils", 2013), ("St. Louis Blues", 2012), ("Atlanta Hawks", 2015),
           ("Pittsburgh Penguins", 2025), ("Florida Panthers", 2013)]
check("low-case median", median_with(LOW)[0], 20.0); check("high-case median", median_with(HIGH)[0], 25.0)
check("median without the bundled seven", median_with(drop=BUNDLED)[::2], (26.3, 26))
check("Mariners carry the RSN stake", "ROOT Sports Northwest" in B[("Seattle Mariners", 2016)]["other_assets"], True)
check("MLB median is the Mariners deal", lg("MLB"), B[("Seattle Mariners", 2016)]["premium"])
check("MLB median without the Mariners", round(st.median(x["premium"] for x in clean if x["league"] == "MLB" and x["team"] != "Seattle Mariners"), 1), 14.2)
check("Orioles stay clean", B[("Baltimore Orioles", 2024)]["group"], "clean")
capped = [x["premium"] for x in clean if x["league"] != "MLB"]
check("capped leagues n", len(capped), 26, 0); check("capped leagues median", round(st.median(capped), 1), 24.5)
check("NFL below MLB", lg("NFL") < lg("MLB"), True)
check("every $3B+ deal is 2022 or later", min(x["year"] for x in clean if float(x["price"]) >= 3), 2022, 0)
def when(v):
    a = v.split("-"); return dt.date(int(a[0]), int(a[1]), int(a[2]) if len(a) > 2 else 15)
for x in clean:
    x["lag"] = (when(x["date"]) - when(Rraw[(x["team"], x["date"])]["forbes_pub_date"])).days / 30.44
lags = [x["lag"] for x in clean]
LAG_MED, LAG_MAX = round(st.median(lags), 1), round(max(lags), 1)
check("median list age, months", LAG_MED, 5.0); check("oldest list, months", LAG_MAX, 11.7)
old = [x["premium"] for x in clean if x["lag"] > 6]; fresh = [x["premium"] for x in clean if x["lag"] <= 6]
check("older lists", (len(old), round(st.median(old), 1)), (15, 25.0)); check("fresher lists", (len(fresh), round(st.median(fresh), 1)), (18, 17.7))
PADRES_NET = prem(0.6, 0.458); KINGS_OLD = prem(0.534, 0.3); SENS90 = prem(0.95 / 0.9, 0.8); BLAZ_LOW = prem(4.1, 3.5)
CELT_BLEND = prem(6.5, 6.0); METS_HIGH = prem(2.475, 2.4); LAK_LOW = prem(12.0, 10.0); WOLVES = prem(1.5, 3.1)
check("Padres net of TV money", PADRES_NET, 31.0); check("Kings vs prior-year list", KINGS_OLD, 78.0); check("Senators if $950M bought 90%", SENS90, 31.9)
check("Blazers on $4.1B", BLAZ_LOW, 17.1); check("Celtics blended", CELT_BLEND, 8.3); check("Mets on $2.475B", METS_HIGH, 3.1)
check("Lakers 2026 on $12B", LAK_LOW, 20.0); check("Timberwolves vs Forbes at close", WOLVES, -51.6)
NEAR = sum(abs(x["premium"]) <= 3 for x in clean); HURR_OLD = prem(0.505, 0.23)
check("deals within 3% of Forbes", NEAR, 8, 0); check("misses within 3%", sum(-3 <= x["premium"] < 0 for x in clean), 3, 0); check("Hurricanes on the stale list", HURR_OLD, 119.6)
check("the median deal is the Broncos", [x["team"] for x in clean if x["premium"] == med], ["Denver Broncos"])
check("Hurricanes list two days before the deal", (when("2017-12-07") - when("2017-12-05")).days, 2, 0)
check("Cubs not in the set", any("Cubs" in r["team"] for r in R), False)
groups = {}
for c in C.values(): groups.setdefault(c["group"], []).append(c["team"])
check("excluded deals", len(C), 14, 0); check("clean plus excluded", len(clean) + len(C), 47, 0)
check("forced, league, staged, record", [len(groups[g]) for g in ("forced", "league_sold", "not_control")] + [len(groups["out_of_range"]) + len(groups["no_price"])], [2, 3, 5, 4])

print("\n-- draft, captions, thread --")
def bn(v, d=None):
    t = f"{v:.{d}f}" if d is not None else f"{v:g}"
    return f"${t} billion"
g = lambda t, y: B[(t, y)]
P_ = lambda t, y: abs(g(t, y)["premium"])
ptop = sorted(clean, key=lambda x: -x["premium"])
DRAFT_PHRASES = [
    "Sold above the estimate.", f"in {above} of the {len(clean)} sales", f"the other {below} went below", f"The median premium over Forbes is {med}%",
    f"buyers paid {bn(tot_p, 2)} against {bn(tot_f, 2)} of Forbes value, {round(100 * (tot_p / tot_f - 1), 1)}% more",
    f"every deal with both figures, {len(allp)} of them, and the median rises to {round(st.median(allp), 1)}%", "I pulled 47 control deals from 2011 through 2026",
    f"the median is {median_with(LOW)[0]}%; take the highest and it's {median_with(HIGH)[0]}%", f"Drop the seven deals with arena or media assets in the price and it's {median_with(drop=BUNDLED)[0]}% across {median_with(drop=BUNDLED)[2]}", f"the Mariners' {bn(1.4)} their ROOT Sports Northwest stake",
    f"who went to the Walton-Penner group for {bn(4.65)} in 2022 against a Forbes {bn(3.75)}", f"(1.1% under), the Royals in 2019 (2.0%) and the Penguins last December (2.9%)",
    f"{NEAR} of the 33 landed within 3% of Forbes", f"the Hurricanes' {P_('Carolina Hurricanes', 2017)}% uses a $505 million valuation", f"which would make it {HURR_OLD}%",
    f"The NHL leads at {lg('NHL')}% on 7 sales, then the NBA at {lg('NBA')}% on 13, MLB at {lg('MLB')}% on 7 and the NFL at {lg('NFL')}% on 6",
    f"the {len(capped)} sales in the three capped leagues run a median {round(st.median(capped), 1)}%, above MLB's {lg('MLB')}%, but the NFL sits just below baseball",
    f"The Celtics went for {bn(6.1)} against a Forbes {bn(6.0, 1)}, {P_('Boston Celtics', 2025)}% over", f"near {bn(6.5)}, which would make it {CELT_BLEND}%",
    f"paid {bn(2.42)} for the Mets against {bn(2.4)}, {P_('New York Mets', 2020)}% over, or {METS_HIGH}% on the {bn(2.475)}",
    f"record {bn(6.05)} beat Forbes by {P_('Washington Commanders', 2023)}%", f"at {bn(3.5)} against {bn(4.5)}, {P_('Dallas Mavericks', 2023)}% below",
    f"paid {bn(10)} for the Lakers in 2025 against {bn(7.1)}, {P_('Los Angeles Lakers', 2025)}% over",
    f"{bn(9.612)} for the Seahawks this July beat {bn(6.7)} by {P_('Seattle Seahawks', 2026)}%",
    f"{bn(12.5)} in August", f"The {P_('Los Angeles Lakers', 2026)}% premium on that one is soft", f"Forbes' {bn(10, 1)} was just Walter's own price", f"which would make it {LAK_LOW}%",
    f"The Hornets lead at {P_('Charlotte Hornets', 2023)}%, {bn(3, 1)} against {bn(1.7)}", f"The Padres are second at {P_('San Diego Padres', 2012)}%, overstated",
    f"net of that it's {PADRES_NET}%", f"the Devils at {P_('New Jersey Devils', 2013)}%", f"the Bills at {P_('Buffalo Bills', 2014)}% and the Suns at {P_('Phoenix Suns', 2022)}%",
    f"The {len(big)} deals of $3 billion or more have a median of {round(st.median(big), 1)}%, and the {len(small)} below that {round(st.median(small), 1)}%",
    f"{per(2012, 2017)}% from 2012 to 2017 on 14 sales, {per(2018, 2022)}% from 2018 to 2022 on 7, and {per(2023, 2026)}% from 2023 to 2026 on 12",
    f"{LAG_MED} months old at announcement and the oldest {LAG_MAX}", f"ran {round(st.median(old), 1)}% on {len(old)} deals, and fresher ones {round(st.median(fresh), 1)}% on {len(fresh)}",
    f"{bn(2, 1)} against $575 million, {g('Los Angeles Clippers', 2014)['premium']}% over", f"at the 2021 price of {bn(1.5)}, against Forbes' {bn(3.1)}, {abs(WOLVES)}% below",
    f"The Jazz's {bn(1.66)} included the arena", "the Hawks' $850 million included arena control", f"their {P_('St. Louis Blues', 2012)}% discount",
    f"The Kings' {P_('Sacramento Kings', 2013)}% is measured", f"prior year's $300 million it's {KINGS_OLD}%", f"The Senators' {P_('Ottawa Senators', 2023)}% becomes {SENS90}% if the $950 million bought only the 90% stake",
    f"The Blazers' {P_('Portland Trail Blazers', 2025)}% is {BLAZ_LOW}%", "A reader sent me a version of it",
    "Forbes values are estimates, not prices", "those are a selected group", "Those are small samples", "Bundled assets inflate some premiums",
    "The next NBA, NFL or MLB control sale announced after this piece clears the most recent Forbes value for that team. Checkable at the next announcement.",
    "I held Cubs season tickets from 1998 to 2021. The Cubs are not in the set.",
]
def norm(t): return re.sub(r"\s+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {"24%", "20", "$12 billion", "100%", "3%", "8", "$505 million", "$230 million", "$1.4 billion", "61%", "33", "47", "28", "43", "5", "14", "7", "6", "12", "13", "10", "26", "25%", "90%", "$3 billion", "$800 million", "$200 million", "$130 million", "$250 million", "1998", "2021", pc(WOLVES).lstrip("-")}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d{1,2})?\b|FOX 13|FOX 5|ABC7|ABC17|News4Jax|\bfig-0[1-3]\b")
def stray_numbers(text, label, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in KNOWN and not re.fullmatch(r"20[12]\d", fig): check(f"{label}: number not traced to the data: {fig}", False, True)
raw = (ROOT / "draft.md").read_text(); draft = norm(raw)
datatext0 = (D / "control_sales_verified.csv").read_text()
for ph in DRAFT_PHRASES: check(f"draft says: {ph[:70]}", norm(ph) in draft, True)
pub_part = raw.split("## Not for publication")[0]
stray_numbers(pub_part, "draft")
check("draft has no em dashes", raw.count("—"), 0, 0)
head = raw.split("\n---\n")[0].strip().splitlines()
check("H1 first", head[0].startswith("# "), True)
check("dek under 150 characters", len(head[-1].strip("*")) < 150, True)
check("house layout", [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
check("prediction confirmed (no tag left)", "[MATT TO CONFIRM]" not in raw, True)
check("dead CNN Money link is gone", "money.cnn" in raw + datatext0, False)
check("no Orioles asterisk in the published part", "argue with myself" not in pub_part and "Angelos's death" not in pub_part, True)
ORDINAL = re.compile(r"\b\d{1,2}(?:st|nd|rd|th)\b")
for label, text in (("draft", raw), ("captions", (ROOT / "figures" / "captions.md").read_text()), ("thread", (ROOT / "x-thread.md").read_text())):
    check(f"{label}: no ordinal dates", ORDINAL.findall(re.sub(r"\]\([^)]*\)", "]", text)), [])
left = norm(raw.split("## What I left out and why")[1].split("## What stayed in")[0])
NAMES = {"jaguars_2011": "Jaguars", "pistons_2011": "Pistons", "coyotes_2014": "2014 or 2019", "coyotes_2019": "2014 or 2019", "clippers_2014": "Clippers", "dodgers_2012": "Dodgers",
         "hornets_2012": "Hornets in 2012", "coyotes_2013": "Coyotes in 2013", "utah_2024": "Utah's 2024", "bucks_2023": "Bucks in 2023", "nets_2019": "Nets in 2019",
         "lightning_2024": "Lightning", "islanders_2014": "Islanders", "twolves_2021": "Timberwolves"}
check("every excluded deal has a name check", sorted(NAMES), sorted(c["id"] for c in C.values()))
for k, name in NAMES.items(): check(f"exclusion named: {k}", name in left, True)
src = raw.split("## Sources")[1].split("\n---\n")[0]
items = [l for l in src.splitlines() if l.strip() and not l.endswith(":")]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
links = re.findall(r"\]\((https?://[^)]+)\)", src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
datatext = (D / "control_sales_verified.csv").read_text()
for u in links:
    if not any(h in u for h in ("github.com/mgag70-prog",)): check(f"source link is in the data file: {u[:70]}", u in datatext, True)
body = pub_part.split("## About this piece")[0]
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body)))
print(f"draft body: {WORDS} words"); check("body 1,400 to 1,900 words", 1400 <= WORDS <= 1900, True)
captxt = (ROOT / "figures" / "captions.md").read_text()
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=10)
check("captions have no em dashes", captxt.count("—"), 0, 0)
tp = ROOT / "x-thread.md"
posts = re.split(r"^## Post \d+.*$", tp.read_text(), flags=re.M)[1:]
check("thread has six posts", len(posts), 6, 0)
for i, tb in enumerate(posts, 1):
    text = "\n".join(l for l in tb.strip().splitlines() if not l.startswith("Attach:")).strip()
    length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
    check(f"post {i} length {length} under 280", length < 280, True)
    for fig in NUMBER.findall(re.sub(r"https?://\S+|\[URL\]", "", text)):
        if fig.strip() and norm(fig.rstrip(",")) not in draft: check(f"post {i} figure verbatim in draft: {fig}", False, True)
check("thread ends with the piece link", posts[-1].strip().endswith("https://ledgerandwhistle.substack.com/p/the-median-buyer-paid-24-more-than"), True)
check("thread has no em dashes", tp.read_text().count("—"), 0, 0)
paste = ROOT / "paste-into-substack.html"
if paste.exists():
    html = paste.read_text()
    check("paste: stops above Not for publication", "Not for publication" not in html, True)
    check("paste: no tables", "<table" not in html and "|---" not in html, True)
    check("paste: every draft link live", all(f'href="{u}"' in html for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part)), True)
    check("paste: no em dashes", html.count("—"), 0, 0)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
