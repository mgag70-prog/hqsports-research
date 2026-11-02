#!/usr/bin/env python3
"""stadium-subsidies-2026: public vs private money in major-league stadium and arena projects
opened 2015-2026, under construction, or approved (USD projects with both figures known), plus the
asks that failed or are pending. Run from repo root: python3 stadium-subsidies-2026/model/recompute.py"""
import csv, pathlib, statistics, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "data"
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})"); 
    if not ok: fails.append(name)
P = list(csv.DictReader(open(D / "projects.csv")))
for p in P:
    p["total"] = float(p["total_cost_m"]); p["public"] = float(p["public_m"])
    p["private"] = p["total"] - p["public"]; p["share"] = 100 * p["public"] / p["total"]
    p["cls"] = "private" if p["public"] == 0 else ("majority public" if p["share"] > 50 else "minority public")
check("projects", len(P), len(P), 0)
print("projects:", len(P))
pub = sum(p["public"] for p in P); tot = sum(p["total"] for p in P)
print(f"total cost ${tot:,.1f}M, public ${pub:,.1f}M ({100*pub/tot:.1f}%)")
by = {}
for p in P: by.setdefault(p["cls"], []).append(p)
for k, v in by.items(): print(k, len(v), [x["id"] for x in v])
subs = [p for p in P if p["public"] > 0]
print("median public share among subsidized:", round(statistics.median(p["share"] for p in subs), 1), "n", len(subs))
print("median public share all:", round(statistics.median(p["share"] for p in P), 1))
for lg in ["NFL", "MLB", "NBA", "NHL"]:
    xs = [p for p in P if p["league"].startswith(lg) or ("/" in p["league"] and lg in p["league"])]
    if xs: print(lg, len(xs), "public $M", round(sum(x["public"] for x in xs), 1), "median share", round(statistics.median(x["share"] for x in xs), 1))
for st in ["opened", "under construction", "approved"]:
    xs = [p for p in P if p["status"] == st]
    print(st, len(xs), "public", round(sum(x["public"] for x in xs), 1), "median share", round(statistics.median(x["share"] for x in xs), 1))
pipeline = [p for p in P if p["status"] in ("under construction", "approved")]
print("pipeline public $M", round(sum(p["public"] for p in pipeline), 1), "n", len(pipeline))
print("\nranked by public $:")
for p in sorted(P, key=lambda p: -p["public"])[:12]: print(f"  {p['id']:12} public {p['public']:7.1f} of {p['total']:7.1f}  {p['share']:5.1f}%  {p['status']}")
print("ranked by share (subsidized):")
for p in sorted(subs, key=lambda p: -p["share"])[:8]: print(f"  {p['id']:12} {p['share']:5.1f}%")
refs = [p for p in P if p["referendum"] != "none"]
print("projects with a public vote:", [(p["id"], p["referendum"]) for p in refs])
with open(D / "projects-computed.csv", "w", newline="") as f:
    cols = ["id", "league", "team", "venue", "kind", "status", "open_year", "total_cost_m", "public_m", "private", "share", "cls", "referendum"]
    w = csv.writer(f); w.writerow(cols[:9] + ["private_m", "public_share_pct", "funding_class", "referendum"])
    for p in sorted(P, key=lambda p: -p["public"]):
        w.writerow([p[c] for c in cols[:9]] + [round(p["private"], 1), round(p["share"], 1), p["cls"], p["referendum"]])

print("\n-- headline checks --")
check("projects", len(P), 38, 0)
check("total cost $M", round(tot, 1), 49469.1)
check("public $M", round(pub, 1), 18336.5)
check("public share of total %", round(100 * pub / tot, 1), 37.1)
check("private projects", len(by["private"]), 8, 0)
check("private projects cost $M", round(sum(p["total"] for p in by["private"]), 1), 12000.0)
check("majority-public projects", len(by["majority public"]), 17, 0)
check("median share among subsidized", round(statistics.median(p["share"] for p in subs), 1), 60.0)
check("pipeline public $M", round(sum(p["public"] for p in pipeline), 1), 13524.5)
check("pipeline projects", len(pipeline), 19, 0)
newo = [p for p in P if p["kind"] == "new" and p["status"] == "opened"]
newp = [p for p in P if p["kind"] == "new" and p["status"] in ("under construction", "approved")]
check("new venues opened: median public share", round(statistics.median(p["share"] for p in newo), 1), 37.8)
check("new venues in the pipeline: median public share", round(statistics.median(p["share"] for p in newp), 1), 60.0)
check("new venues opened n", len(newo), 14, 0); check("new venues pipeline n", len(newp), 9, 0)
nflnew = [p for p in P if p["league"] == "NFL" and p["kind"] == "new" and p["status"] != "opened"]
check("four NFL stadiums in the pipeline, public $M", round(sum(p["public"] for p in nflnew), 1), 5005.0)
byid = {p["id"]: p for p in P}
check("Thunder share %", round(byid["thunder"]["share"], 1), 94.4)
check("Chiefs public", byid["chiefs"]["public"], 1800.0)
check("Titans public", byid["titans"]["public"], 1260.0)
check("Bills share %", round(byid["bills"]["share"], 1), 40.5)
check("Commanders share %", round(byid["commanders"]["share"], 1), 29.7)
check("Rays share %", round(byid["rays"]["share"], 1), 37.1)
check("Royals share %", round(byid["royals"]["share"], 1), 60.0)
check("projects with a public vote", sorted(p["id"] for p in P if p["referendum"] != "none"), ["rangers", "spurs", "thunder"])
voted = sum(byid[i]["public"] for i in ("rangers", "thunder", "spurs"))
check("voted deals share of all public $ %", round(100 * voted / pub, 1), 11.7)
check("voted pipeline deals share of pipeline public $ %", round(100 * (byid["thunder"]["public"] + byid["spurs"]["public"]) / sum(p["public"] for p in pipeline), 1), 12.2)
A = list(csv.DictReader(open(D / "asks.csv")))
check("asks rows", len(A), 10, 0)

print("\n-- team values (Forbes) --")
V = {v["id"]: v for v in csv.DictReader(open(D / "team-values.csv"))}
def pv(i): return round(byid[i]["public"] / 1000 / float(V[i]["forbes_value_b"]) * 100, 1)
check("Royals public as % of Forbes value", pv("royals"), 69.5)
check("Rays public as % of Forbes value", pv("rays"), 51.5)
check("Chiefs public as % of Forbes value", pv("chiefs"), 20.5)
check("Titans public as % of Forbes value", pv("titans"), 14.8)
check("Thunder public as % of Forbes value", pv("thunder"), 17.3)
def mult(i): return round(float(V[i]["forbes_value_b"]) / float(V[i]["purchase_price_b"]), 1)
check("Browns value / price paid 2012", mult("browns"), 8.6)
check("Bills value / price paid 2014", mult("bills"), 5.8)
check("Jaguars value / estimated price 2011", mult("jaguars"), 10.6)
check("Commanders value / price paid 2023", mult("commanders"), 1.6)
check("Thunder value / price paid 2006 (Sonics)", mult("thunder"), 14.0)
check("Rays: Forbes value equals 2025 price", float(V["rays"]["forbes_value_b"]), float(V["rays"]["purchase_price_b"]))
check("Ballmer net worth $B", float(V["clippers"]["owner_net_worth_b"]), 156.0)
print("\n-- more figures the draft uses --")
import re
E = {e["key"]: e for e in csv.DictReader(open(D / "evidence.csv"))}
AS = {a["id"]: a for a in A}
def ev(k): return E[k]["value"]
def bn(m, d=1): return f"${m / 1000:.{d}f} billion"          # $ millions in, "$1.8 billion" out
def mn(m, d=0): return f"${m:,.{d}f} million"
def pc(v, d=1): return f"{v:.{d}f}%"
def num(s): return float(re.search(r"[\d.]+", s.replace(",", "")).group())
def caveat_says(i, *bits):
    for b in bits: check(f"{i} caveat has {b!r}", b in byid[i]["caveat"], True)
private = by["private"]
check("public share of the voted Rangers deal: about 60% yes", "about 60% yes (Nov 8, 2016)" in byid["rangers"]["referendum"], True)
for i in ("brewers", "dbacks", "athletics"): print(i, "public as % of Forbes value", pv(i))
check("Brewers public as % of Forbes value", pv("brewers"), 26.3); check("Diamondbacks", pv("dbacks"), 25.5); check("Athletics", pv("athletics"), 19.0)
nfl_vals = [float(v["forbes_value_b"]) for v in V.values() if v["league"] == "NFL"]
check("every NFL team in the table is worth $8B or more", min(nfl_vals) >= 8, True)
newp_years = sorted(int(p["open_year"]) for p in newp)
check("new pipeline venues open 2027 to 2032", (newp_years[0], newp_years[-1]), (2027, 2032))
renos = {i: round(byid[i]["share"], 1) for i in ("brewers", "panthers", "grizzlies", "sharks", "lightning", "bengals", "pacers")}
check("renovation shares", renos, {"brewers": 82.0, "panthers": 81.2, "grizzlies": 90.9, "sharks": 76.5, "lightning": 76.0, "bengals": 74.5, "pacers": 81.9})
jc = re.search(r"\(([\d,]+) to ([\d,]+)\)", AS["chiefs_royals_jackson"]["outcome"])
jno, jyes = num(jc.group(1)), num(jc.group(2))
check("Jackson County: 58% no from the count", round(100 * jno / (jno + jyes)), 58, 0)
check("Jackson County: 42% yes from the count", round(100 * jyes / (jno + jyes)), 42, 0)
broncos = re.findall(r"\$([\d.]+)M", AS["broncos"]["outcome"])
check("Broncos public infrastructure about $159M", round(sum(map(float, broncos))), 159, 0)
check("biggest checks in order", [p["id"] for p in sorted(P, key=lambda p: -p["public"])[:4]], ["chiefs", "titans", "royals", "commanders"])
check("Thunder is the highest public share", max(subs, key=lambda p: p["share"])["id"], "thunder")
caveat_says("raiders", "$750M bond principal becomes about $1.35B", "through 2048"); caveat_says("lca", "about $713M")
caveat_says("royals", "about $1.117B with interest", "Apr 6 2027", "58% no", "about $540M implied, not final")
caveat_says("pacers", "about $800M public over 25 years"); caveat_says("jaguars", "+ $150M maintenance")
caveat_says("bills", "60,108 seats, down from 71,608", "maintenance over 30 years"); caveat_says("rays", "$180M state money for a college campus")
caveat_says("commanders", "federal land transfer"); caveat_says("rams_chargers", "$200M league loan"); caveat_says("cubs", "up to $75M")
caveat_says("clippers", "land came from the city"); caveat_says("warriors", "public transit"); caveat_says("kraken", "city owns the building")
caveat_says("browns", "state $600M blocked by a preliminary injunction (Mar 2026")
check("Chargers 43% yes, two-thirds", all(b in AS["chargers_sd"]["outcome"] for b in ("43% yes", "two-thirds")), True)
check("Coyotes 56% no, moved 2024", all(b in AS["coyotes_tempe"]["outcome"] for b in ("56% no", "Utah in 2024")), True)
check("Virginia ask $1.5B died Mar 27 2024, DC $515M", (AS["caps_wizards_va"]["public_ask_m"], "Mar 27, 2024" in AS["caps_wizards_va"]["outcome"], byid["monumental"]["public"]), ("1500", True, 515.0))
check("Bears lakefront $2.4B of $4.75B, May 16 2025", (AS["bears_lakefront"]["public_ask_m"], AS["bears_lakefront"]["total_cost_m"], AS["bears_lakefront"]["outcome"]), ("2400", "4750", "shelved May 16 2025"))
check("Bears Hammond SB 27, Feb 26 2026, Oct 14 2026", all(b in AS["bears_hammond"]["outcome"] for b in ("SB 27 signed Feb 26, 2026", "~$1B", "Oct 14, 2026")), True)
check("Salt Lake up to $900M by mid-2032", "up to $900M state money, only if an MLB team arrives by mid-2032" in AS["salt_lake"]["outcome"], True)
for k, v in (("referendum_pass_rate", "58"), ("elected_pass_rate", "96"), ("proposals_to_voters", "6 of 39"), ("studies_130", "130"), ("igm_agree", "24 of 34"),
             ("igm_weighted", "83"), ("cv_share_13", "13"), ("cobb_shortfall", "15"), ("ntj_federal_loss", "4.3"), ("propheter_2022", "654.3"),
             ("propheter_pv", "18"), ("propheter_schools", "7.5"), ("brown_local_rev", "85"), ("brown_luxury", "623"), ("brown_value", "35"),
             ("illinois_poll", "58 to 32"), ("bradbury_decade_1990s", "72"), ("bradbury_decade_2010s", "47"), ("bradbury_decade_2020s", "38"),
             ("bradbury_median_cost_2010s", "605"), ("bradbury_six_subsidy_total", "5.74")):
    check(f"evidence {k}", ev(k), v)
check("NTJ: 57 stadiums since 2000", "57 stadiums built or renovated since 2000" in E["ntj_federal_loss"]["what_it_measures"], True)
check("Propheter: 105 venues, 2022", "105 venues would have owed in 2022" in E["propheter_2022"]["what_it_measures"], True)
check("Brown: seven teams, 1990s", "seven teams; 1990s data" in E["brown_value"]["what_it_measures"], True)
check("proposals 2005-2017", "2005-2017" in E["proposals_to_voters"]["what_it_measures"], True)
check("IGM: 1 disagreed, 2017", "1 disagreed" in E["igm_agree"]["what_it_measures"] and "2017" in E["igm_agree"]["what_it_measures"], True)

def own(i, f): return float(V[i][f])
DRAFT_PHRASES = [
    f"Taxpayers have committed {bn(sum(p['public'] for p in pipeline))} to {len(pipeline)} stadiums and arenas that haven't opened yet",
    f"Across {len(P)} recent stadium and arena deals, taxpayers put in {bn(pub)}",
    f"Together they cost {bn(tot)}. State, county and city governments put in {bn(pub)} of that, {pc(100 * pub / tot)}",
    f"Eight of the {len(P)} were privately financed, {bn(sum(p['total'] for p in private))} of building between them",
    f"The other {len(subs)} took public money, and among those {len(subs)} the median public share is {pc(statistics.median(p['share'] for p in subs))}; {len(by['majority public'])} of them are majority public",
    f"Kansas is putting about {bn(byid['chiefs']['public'])} in STAR bonds into a {bn(byid['chiefs']['total'], 0)} Chiefs stadium, {pc(byid['chiefs']['share'], 0)} of the cost",
    f"putting {bn(byid['titans']['public'], 2)} into the Titans' new stadium, also {pc(byid['titans']['share'], 0)}",
    f"about {bn(byid['royals']['public'], 2)} into a Royals ballpark, {pc(byid['royals']['share'], 0)} again",
    f"committed about {bn(byid['commanders']['public'])} to the Commanders, only {pc(byid['commanders']['share'])} of a {bn(byid['commanders']['total'])} project",
    f"the Rays at {mn(byid['rays']['public'])} ({pc(byid['rays']['share'])}), the Bills at {mn(byid['bills']['public'])} ({pc(byid['bills']['share'])}) and the Thunder at {mn(byid['thunder']['public'])}, which is {pc(byid['thunder']['share'])} of their arena",
    f"fell from about {ev('bradbury_decade_1990s')}% in the 1990s to {ev('bradbury_decade_2010s')}% in the 2010s and {ev('bradbury_decade_2020s')}% in the 2020s",
    f"reached ${ev('bradbury_median_cost_2010s')} million in the 2010s, in 2024 dollars",
    f"the median public share is {pc(statistics.median(p['share'] for p in newo))} across {len(newo)} buildings",
    f"Among the nine new venues now under construction or approved, it's {pc(statistics.median(p['share'] for p in newp))}",
    f"These nine open from {newp_years[0]} to {newp_years[-1]}",
    f"carry {bn(sum(p['public'] for p in nflnew))} of public money between them. Bradbury counts ${ev('bradbury_six_subsidy_total')} billion across the six newest NFL stadiums",
    f"the Brewers' repairs at {pc(renos['brewers'])}, the Panthers at {pc(renos['panthers'])}, the Grizzlies at {pc(renos['grizzlies'])}, the Sharks at {pc(renos['sharks'])}, the Lightning at {pc(renos['lightning'])} and the Bengals at {pc(renos['bengals'])}",
    f"The Pacers' renovation, which opened in {byid['pacers']['open_year']}, was {pc(renos['pacers'])} public",
    f"it's {len(pipeline)} projects carrying {bn(sum(p['public'] for p in pipeline))} of public money",
    f"Nevada's {mn(byid['raiders']['public'])} of bond principal for the Raiders' stadium becomes about $1.35 billion in total payments through 2048",
    f"Detroit's {mn(byid['lca']['public'])} for Little Caesars Arena costs about $713 million",
    f"Kansas City's $600 million for the Royals comes to about $1.117 billion with interest",
    f"105 major-league venues would have owed ${ev('propheter_2022')} million more in property tax in 2022 alone, about ${ev('propheter_pv')} billion in present value",
    f"about ${ev('propheter_schools')} billion of it would have gone to K-12 schools",
    f"Tax-exempt bonds for 57 stadiums built or renovated since 2000 cost the Treasury ${ev('ntj_federal_loss')} billion in lost revenue",
    f"(H.R. 2434 and S. 1192)",
    f"shows {mn(byid['pacers']['public'])} of public capital, but the public side comes to about $800 million over 25 years",
    f"The Jaguars' {mn(byid['jaguars']['public'])} is unusual in that it already includes $150 million for maintenance",
    f"for the Bills over 30 years aren't in their {mn(byid['bills']['public'])}",
    f"$180 million of state money for a college campus on the Rays' site isn't in their {mn(byid['rays']['public'])}",
    f"elected bodies approve {ev('elected_pass_rate')}% of stadium proposals put to them, while only {ev('referendum_pass_rate')}% of stadium referendums pass",
    "Of 39 new-stadium proposals from 2005 to 2017, six went to voters",
    "San Diego's Measure C got 43% yes in 2016 when it needed two-thirds", "56% no, and the team moved to Utah in 2024",
    f"58% to 42%; Kansas then committed about {bn(byid['chiefs']['public'])}",
    f"When Virginia's {bn(float(AS['caps_wizards_va']['public_ask_m']))} arena plan for the Capitals and Wizards died on March 27, 2024, D.C. committed {mn(byid['monumental']['public'])}",
    f"covers more than {ev('studies_130')} studies over more than 30 years",
    f"{ev('igm_agree')} who voted agreed", f"agreement was {ev('igm_weighted')}%", f"about {ev('cv_share_13')}% of construction cost",
    f"a public share far below the {pc(statistics.median(p['share'] for p in subs))} median above",
    f"Truist Park leaves the county about ${ev('cobb_shortfall')} million a year short",
    "opposed public money for a Bears stadium %s%% to %s%%" % tuple(ev("illinois_poll").split(" to ")),
    "the Rangers' Globe Life Field (about 60% yes, 2016), the Thunder's new arena (71% yes, 2023) and the Spurs' downtown arena (52% yes on Bexar County's Prop B, 2025)",
    f"Those three deals account for {pc(100 * voted / pub)} of the public money",
    f"Among the {len(pipeline)} projects still to open, the Thunder and Spurs deals are {pc(100 * (byid['thunder']['public'] + byid['spurs']['public']) / sum(p['public'] for p in pipeline))}",
    f"{pc(byid['thunder']['share'])} public, about {mn(byid['thunder']['public'])} toward a cost of at least {mn(byid['thunder']['total'])}",
    f"is {pc(pv('royals'))} of the {bn(own('royals', 'forbes_value_b') * 1000, 2)} Forbes says the team is worth",
    f"Tampa's {mn(byid['rays']['public'])} for the Rays is {pc(pv('rays'))} of the team's {bn(own('rays', 'forbes_value_b') * 1000)} value",
    f"in {V['rays']['purchase_year']}", f"The Brewers' {mn(byid['brewers']['public'])} is {pc(pv('brewers'))} of their value, the Diamondbacks' {pc(pv('dbacks'))} and the Athletics' {pc(pv('athletics'))}",
    f"the Chiefs' public money is {pc(pv('chiefs'))} of their value, the Thunder's {pc(pv('thunder'))} and the Titans' {pc(pv('titans'))}",
    f"bought the Browns for {bn(own('browns', 'purchase_price_b') * 1000, 2)} in {V['browns']['purchase_year']}, and Forbes now puts them at {bn(own('browns', 'forbes_value_b') * 1000)}, {mult('browns')} times",
    f"paid {bn(own('bills', 'purchase_price_b') * 1000)} for the Bills in {V['bills']['purchase_year']}; it's {bn(own('bills', 'forbes_value_b') * 1000, 2)} now, {mult('bills')} times",
    f"estimated {bn(own('jaguars', 'purchase_price_b') * 1000, 2)} for the Jaguars in {V['jaguars']['purchase_year']} has become {bn(own('jaguars', 'forbes_value_b') * 1000, 2)}, {mult('jaguars')} times",
    f"paid {bn(own('thunder', 'purchase_price_b') * 1000, 2)} for the Sonics in {V['thunder']['purchase_year']}, and the Thunder are valued at {bn(own('thunder', 'forbes_value_b') * 1000)}, {mult('thunder')} times",
    f"paid {bn(own('commanders', 'purchase_price_b') * 1000, 2)} for the Commanders in {V['commanders']['purchase_year']}, and three years later Forbes has them at {bn(own('commanders', 'forbes_value_b') * 1000)}, {mult('commanders')} times",
    "Every NFL team in my table is valued at $8 billion or more", "Public money. Private stadium.",
    f"raised local revenue {ev('brown_local_rev')}% and luxury-box revenue {ev('brown_luxury')}%, with franchise values up {ev('brown_value')}% on average",
    "seats 60,108, down from 71,608", f'"{ev("matheson_quote")}."',
    f"David Tepper is worth {bn(own('panthers', 'owner_net_worth_b') * 1000)} and got {mn(byid['panthers']['public'])} from Charlotte",
    f"The Hunt family is worth {bn(own('chiefs', 'owner_net_worth_b') * 1000)}, a figure for the whole family",
    f"Steve Ballmer (${own('clippers', 'owner_net_worth_b'):.0f} billion) and Stan Kroenke ({bn(own('rams_chargers', 'owner_net_worth_b') * 1000)})",
    f"Amy Adams Strunk is worth {bn(own('titans', 'owner_net_worth_b') * 1000)} while Forbes values her Titans at {bn(own('titans', 'forbes_value_b') * 1000)}",
    f"Mark Davis is worth {bn(own('raiders', 'owner_net_worth_b') * 1000)} and the Raiders {bn(own('raiders', 'forbes_value_b') * 1000)}",
    "a ${:.0f} million league loan".format(float(re.search(r'\$(\d+)M league loan', byid['rams_chargers']['caveat']).group(1))),
    "worth up to $75 million approved", f"about ${broncos[0].split('.')[0]} million of voter-approved bonds for viaducts, and the state spent ${broncos[1]} million moving freight tracks nearby: about $159 million",
    f"asked for {bn(float(AS['bears_lakefront']['public_ask_m']))} of public money toward {bn(float(AS['bears_lakefront']['total_cost_m']), 2)}, was shelved on May 16, 2025",
    "Indiana's SB 27, signed February 26, 2026", "about $1 billion of district tax revenue", "Then, on October 29, Crain's Chicago Business columnist Greg Hinz reported that the Bears were nearing a deal to stay in Illinois", "lawmakers could vote as soon as November",
    "the state's $600 million for the Browns is blocked pending litigation, under a preliminary injunction from March 2026",
    "up to $900 million of state money waiting for a ballpark, available only if Major League Baseball puts a team there by mid-2032",
    "a charter question on stadium funding on April 6, 2027",
]
def norm(t): return re.sub(r"\s+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
# every number in the body has to be one of these: the strings the phrases above are built from, plus the counts and dates below
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {str(n) for n in (len(P), len(subs), len(by["majority public"]), len(newo), len(pipeline))}
KNOWN |= {bn(pub), pc(byid["thunder"]["share"]), pc(statistics.median(p["share"] for p in subs)), pc(statistics.median(p["share"] for p in newp)),
          pc(statistics.median(p["share"] for p in newo)), bn(sum(p["public"] for p in pipeline)), pc(100 * voted / pub)}
KNOWN |= {"60%", "71%", "52%", "1990s", "2024 dollars"}                     # vote shares and Bradbury's units, checked above
KNOWN |= {pc(pv("raiders"))}                                              # captions, fig-03: the smallest ratio
KNOWN |= {"1998", "2021"}                                                  # disclosure, on record in mlb-154-games-2026 and mlb-lockout-2026
YEARS = set(re.findall(r"(?<!\d)(?:19|20)\d\d(?!\d)", "".join(open(f).read() for f in [*D.glob("*.csv"), D / "research" / "verification.md"])))
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}\b|K-12|SB 27|"
                   r"H\.R\. 2434|S\. 1192|\bfig-0[1-4]\b|Fox 32|NewsChannel 5|News4Jax|KCTV5|ABC15")   # bill numbers and outlet names
def stray_numbers(text, label, known=KNOWN, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in known and not (re.fullmatch(r"(?:19|20)\d\d", fig) and fig in YEARS):
            check(f"{label}: number not traced to the data: {fig}", False, True)
draft_path = ROOT / "draft.md"
if draft_path.exists():
    raw = draft_path.read_text(); draft = norm(raw)
    for ph in DRAFT_PHRASES:
        check(f"draft says: {ph[:70]}", norm(ph) in draft, True)
    pub_part = raw.split("## Not for publication")[0]
    stray_numbers(pub_part, "draft")
    check("draft has no em dashes", raw.count("—"), 0, 0)
    head = raw.split("\n---\n")[0].strip().splitlines()
    check("H1 first", head[0].startswith("# "), True)
    check("dek under 150 characters", len(head[-1].strip("*")) < 150, True)
    check("house layout: About, Sources, Not for publication in order",
          [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
    check("prediction confirmed (no tag left)", "[MATT TO CONFIRM]" not in raw.split("## What I expect")[1].split("---")[0], True)
    for ph in ("voters approved it with 71% of the vote", "They're estimates, not sale prices", "I can't tell you the stadiums caused those gains",
               '"Private" still covers some public help'):
        check(f"fairness line: {ph}", ph in draft, True)
    src = raw.split("## Sources")[1].split("---")[0]
    links = re.findall(r"\]\((https?://[^)]+)\)", src)
    check("Sources: no duplicate links", len(links), len(set(links)), 0)
    data_urls = {r["source"] for r in P} | {r["source"] for r in A} | {u for e in E.values() for u in e.values() if u and u.startswith("http")} | {v["source"] for v in V.values()}
    data_urls |= set(re.findall(r"https?://[^\s;)|]+", (D / "research" / "verification.md").read_text()))
    for u in links:
        if "github.com/mgag70-prog" not in u: check(f"source link is in the data files: {u[:70]}", u in data_urls, True)
    body = pub_part.split("## About this piece")[0]
    words = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body)))
    print(f"draft body: {words} words"); check("body 2,200 to 2,800 words", 2200 <= words <= 2800, True)

cap_path = ROOT / "figures" / "captions.md"
if cap_path.exists():
    captxt = cap_path.read_text()
    stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=10)
    check("captions have no em dashes", captxt.count("—"), 0, 0)

thread_path = ROOT / "x-thread.md"
if draft_path.exists() and thread_path.exists():
    posts = re.split(r"^## Post \d+.*$", thread_path.read_text(), flags=re.M)[1:]
    check("thread has six posts", len(posts), 6, 0)
    for i, body in enumerate(posts, 1):
        text = "\n".join(l for l in body.strip().splitlines() if not l.startswith("Attach:")).strip()
        length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
        check(f"post {i} length {length} under 280", length < 280, True)
        for fig in NUMBER.findall(re.sub(r"https?://\S+", "", text)):
            if fig.strip() and norm(fig.rstrip(",")) not in draft:
                check(f"post {i} figure verbatim in draft: {fig}", False, True)
    check("thread ends with the piece link", posts[-1].strip().endswith("https://ledgerandwhistle.substack.com/p/taxpayers-have-committed-135-billion"), True)
    check("thread has no em dashes", thread_path.read_text().count("—"), 0, 0)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
