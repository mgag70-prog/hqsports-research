#!/usr/bin/env python3
"""lockout-countdown-2026 week 1: MLB's Nov 3 proposal moved the cap to 2028 ($258.2M cap, $180.2M floor,
90% floor flexibility). Lay the 2028 lines over 2026 actual tax payrolls (mlb-floor-2026) and 2027
projected/signed payrolls (mlb-2027-cap-2026), and check ESPN's counts. Then assert every number and key
phrase in draft.md, captions and x-thread.md, the way stadium-subsidies-2026 does. Run from repo root."""
import csv, pathlib, re, sys
from datetime import date, timedelta
ROOT = pathlib.Path(__file__).resolve().parents[1]; REPO = ROOT.parents[1]
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
ctx = {r["key"]: r for r in csv.DictReader(open(ROOT / "data" / "context.csv"))}
CAP = float(ctx["cap_2028"]["value"]); FL = float(ctx["floor_2028"]["value"])
F90 = FL * float(ctx["floor_flex_pct"]["value"]) / 100
OLDCAP = float(ctx["cap_2027_old"]["value"]); OLDFL = float(ctx["floor_2027_old"]["value"])
a = list(csv.DictReader(open(REPO / "mlb-floor-2026" / "data" / "2026-vs-cap-floor.csv")))
b = list(csv.DictReader(open(REPO / "mlb-2027-cap-2026" / "data" / "2027-vs-cap.csv")))
def lines(rows, key):
    over = sorted([(r["team"], float(r[key])) for r in rows if float(r[key]) > CAP], key=lambda x: -x[1])
    under = sorted([(r["team"], float(r[key])) for r in rows if float(r[key]) < FL], key=lambda x: x[1])
    return over, under
o26, u26 = lines(a, "tax_payroll_m")
check("2026 payrolls over the 2028 cap", len(o26), int(ctx["espn_ceiling_count"]["value"]), 0)
check("2026 payrolls under the 2028 floor", len(u26), int(ctx["espn_floor_count"]["value"]), 0)
check("Brewers among them", "MIL" in [t for t, _ in u26], True)
check("2026: $M over the 2028 cap", round(sum(p - CAP for _, p in o26), 1), 511.8)
check("2026: $M under the 2028 floor", round(sum(FL - p for _, p in u26), 1), 656.3)
check("90% of the 2028 floor", round(F90, 2), 162.18)
check("2026: all 12 also under 90%", sum(1 for _, p in u26 if p < F90), 12, 0)
o27, u27 = lines(b, "projected_m")
check("2027 projected over the 2028 cap", len(o27), 7, 0)
check("2027 projected under the 2028 floor", len(u27), 12, 0)
check("2027 projected under 90% of floor", sum(1 for _, p in u27 if p < F90), 9, 0)
os27, _ = lines(b, "signed_basis_m")
check("2027 signed over the 2028 cap", sorted(t for t, _ in os27), ["LAD", "NYM", "NYY", "PHI"])
by = {r["team"]: r for r in b}
check("Brewers 2027 projected vs 2028 floor ($M above)", round(float(by["MIL"]["projected_m"]) - FL, 2), 12.21)
check("cap moved up $M", round(CAP - OLDCAP, 1), 12.9)
check("floor moved up $M", round(FL - OLDFL, 1), 9.0)
check("Dodgers 2027 projected over the 2028 cap", round(float(by["LAD"]["projected_m"]) - CAP, 1), 135.6)
print("2026 over:", o26); print("2026 under:", u26); print("2027 proj over:", o27); print("2027 proj under:", u27)

print("\n-- old lines against new, 2026 payrolls --")
pay26 = {r["team"]: float(r["tax_payroll_m"]) for r in a}
old_over = sorted(t for t, p in pay26.items() if p > OLDCAP); old_under = sorted(t for t, p in pay26.items() if p < OLDFL)
new_over = sorted(t for t, _ in o26); new_under = sorted(t for t, _ in u26)
check("old lines: clubs over", len(old_over), 9, 0)
check("old lines: clubs under", len(old_under), 12, 0)
check("clubs caught by the old lines", len(old_over) + len(old_under), 21, 0)
check("the 20 are all on the old list", set(new_over + new_under) <= set(old_over + old_under), True)
check("the only club that left", sorted(set(old_over + old_under) - set(new_over + new_under)), ["ATL"])
check("no club joined", sorted(set(new_over + new_under) - set(old_over + old_under)), [])
check("same twelve under", old_under == new_under, True)
ATL_GAP = round(CAP - pay26["ATL"], 2)
check("Atlanta under the new cap by $M", ATL_GAP, 0.68, 0.001)
UP_CAP = 100 * (CAP / OLDCAP - 1); UP_FL = 100 * (FL / OLDFL - 1)
check("cap rose %", round(UP_CAP, 1), 5.3, 0); check("floor rose %", round(UP_FL, 1), 5.3, 0)
check("floor as % of cap, old", round(100 * OLDFL / OLDCAP, 1), 69.8, 0); check("floor as % of cap, new", round(100 * FL / CAP, 1), 69.8, 0)
OVER = sum(p - CAP for _, p in o26); UNDER = sum(FL - p for _, p in u26); UNDER90 = sum(F90 - p for _, p in u26)
OLD_CUT = sum(pay26[t] - OLDCAP for t in old_over); OLD_ADD = sum(OLDFL - pay26[t] for t in old_under)
check("old lines: net to players $M (floor piece: $79.0M less)", round(OLD_CUT - OLD_ADD, 1), 79.0)
check("to reach the 90% line $M", round(UNDER90, 1), 440.0)
check("new lines: floor adds more than cap removes $M", round(UNDER - OVER, 1), 144.4)
check("new lines at 90%: cap removes more $M", round(OVER - UNDER90, 1), 71.8)
proj_over = {t for t, _ in o27}; proj_under = {t for t, _ in u27}
check("2027 over: joins", sorted(proj_over - set(new_over)), ["HOU"])
check("2027 over: drop out", sorted(set(new_over) - proj_over), ["CHC", "TOR"])
check("2027 under: join", sorted(proj_under - set(new_under)), ["KC", "LAA"])
check("2027 under: climb out", sorted(set(new_under) - proj_under), ["MIL", "MIN"])
MIL = by["MIL"]
check("Brewers clear the floor on signed plus arbitration", float(MIL["signed_basis_m"]) + float(MIL["arb_projected_m"]) > FL, True)
check("Brewers signed alone under the floor", float(MIL["signed_basis_m"]) < FL, True)

print("\n-- calendar --")
D = date
PUB, CBA = D(2026, 11, 5), D(2026, 12, 1)
WIN0, WIN1 = D(2026, 11, 2), D(2026, 12, 1)
DAYS_LEFT = (CBA - PUB).days; WINDOW = (WIN1 - WIN0).days + 1
check("days left, Nov 5 to Dec 1", DAYS_LEFT, int(ctx["days_left_from_nov5"]["value"]), 0)
check("signing window, Nov 2 to Dec 1, counting both ends", WINDOW, 30, 0)
check("signing window, elapsed", (WIN1 - WIN0).days, 29, 0)
check("publication is a Thursday", PUB.strftime("%A"), "Thursday")
check("proposal date is a Tuesday", D(2026, 11, 3).strftime("%A"), "Tuesday")
LOCK = (D(2022, 3, 10) - D(2021, 12, 2)).days + 1
check("2021-22 lockout, counting both ends", LOCK, int(ctx["lockout_2021_days"]["value"]), 0)
WS = D(2026, 10, 28)
check("free agency opens five days after the World Series", WS + timedelta(5), WIN0)
check("qualifying-offer deadline from AP", ctx["qo_decisions"]["value"], "November 17")
check("players who got the offer", int(ctx["qo_count"]["value"]), 8, 0)
check("offers went out on a Monday, November 2", D(2026, 11, 2).strftime("%A"), "Monday")
check("next countdown is a Wednesday", D(2026, 11, 11).strftime("%A"), "Wednesday")

print("\n-- draft, captions, thread --")
m1 = lambda v: f"${v:.1f} million"; m2 = lambda v: f"${v:.2f} million"
V = lambda k: ctx[k]["value"]
pay = lambda t: float(by[t]["projected_m"])
QUOTE = V("union_quote")
DRAFT_PHRASES = [
    f"catches 20 of the same 21 teams", "26 days. Same lines.",
    f"on Tuesday, November 3rd, and pushed its salary cap back a year, to 2028", "the luxury-tax thresholds wouldn't change for 2027",
    f"The cap goes from {m1(OLDCAP)} to a projected {m1(CAP)}, up {m1(CAP - OLDCAP)}",
    f"the floor goes from {m1(OLDFL)} to {m1(FL)}, up {m1(FL - OLDFL)}", "on a 50-50 split of projected 2028 revenue",
    f"Each rose {UP_CAP:.1f}%, which leaves the floor at {100 * FL / CAP:.1f}% of the cap",
    f"as little as {V('floor_flex_pct')}% of it in a given year, {m2(F90)}",
    f"${V('cbt_to_players')} million of luxury-tax proceeds in cash", f"about ${V('cbt_to_players_now')} million",
    f"a ${int(V('min_salary_mlb')):,} minimum salary (some players would get $1 million)", f"a ${V('prearb_pool_mlb')} million pre-arbitration pool",
    f"would lose more than ${V('union_loss')} billion over the life of the proposal", f'"{QUOTE}."',
    f"a ${V('union_cbt')} million base tax threshold, a ${V('union_min')} million minimum (up from $780,000) and a ${V('union_prearb')} million pre-arbitration pool, which is $50 million today",
    "ESPN counted eight clubs above the new ceiling and twelve below the new floor, the Brewers among them",
    f"Cubs and Padres, {m1(OVER)} above the line in all", f"Cleveland and Miami, {m1(UNDER)} below it",
    f"nine clubs were over and the same twelve were under", f"its {m2(pay26['ATL'])} sits {m2(ATL_GAP)} below the new cap",
    f"all {len(u26)} were below {m2(F90)} too", f"reaching the 90% line takes {m1(UNDER90)} in any year they all use it",
    f"took {m1(OLD_CUT - OLD_ADD)} away from players as a group", f"by {m1(UNDER - OVER)}, unless all twelve stop at 90%, and then it's {m1(OVER - UNDER90)} the other way",
    f"put {len(o27)} clubs over the 2028 cap, {len(u27)} under the floor and {sum(1 for _, p in u27 if p < F90)} under the 90% line",
    "Houston joins the top group while Toronto and the Cubs drop out", "the Angels and Royals slide under the floor as the Brewers and Twins climb over it",
    f"the Dodgers, Yankees, Phillies and Mets over {m1(CAP)}, and the Dodgers project {m1(pay('LAD') - CAP)} over",
    f"project at {m2(pay('MIL'))} for 2027, {m2(pay('MIL') - FL)} above the 2028 floor, and {m1(float(MIL['arb_projected_m']))} of the total is arbitration salaries",
    "Free agency opened at 5 p.m. ET on November 2nd", "The GM Meetings run November 9-12 in Las Vegas",
    f"eight players got the ${V('qo_value')} million qualifying offer on November 2nd and have until November 17th to answer", "by 6 p.m. ET on November 17th", "the non-tender deadline is November 20th",
    "| Next dates | Qualifying-offer deadline November 17th; Rule 5 protection November 17th; non-tender November 20th |", "Next week's countdown runs Wednesday, November 11th.",
    "expires at 11:59 p.m. ET on December 1st", "December 7-9 Winter Meetings in San Diego",
    f"November 2nd to December 1st: {WINDOW} days, counting both ends",
    f"ran from December 2, 2021 to March 10, 2022, {LOCK} days counting both ends", "Opening Day moved back from March 31st",
    f"Losing {V('tv_60_games')} or more games would extend most national TV contracts by a year",
    f"| Days left | {DAYS_LEFT} |", "| Last proposal | MLB, November 3 |",
    "No new agreement by 11:59 p.m. ET on December 1, and the owners lock out the players on December 2. Checkable December 2.",
    "I held Cubs season tickets from 1998 to 2021", f"The Cubs are among the {len(o26)} over, at {m2(pay26['CHC'])}",
]
def norm(t): return re.sub(r"\s+", " ", t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {str(n) for n in (len(o26), len(u26), len(o27), len(u27), 21, 20, DAYS_LEFT, WINDOW, LOCK)}
KNOWN |= {V("qo_count"), V("tv_60_games"), "162", "40", "2021-22", "2026-27", m1(CAP), m1(FL), "90%", "1998", "2021", "2022", "2026", "2027", "2028"}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:st|nd|rd|th)?(?:-\d{1,2})?\b|"
                   r"\b\d{1,2}(?::\d\d)? p\.m\.|Rule 5|Week 1|\bfig-0[1-3]\b")
def stray_numbers(text, label, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in KNOWN: check(f"{label}: number not traced to the data: {fig}", False, True)
draft_path = ROOT / "draft.md"
raw = draft_path.read_text(); draft = norm(raw)
for ph in DRAFT_PHRASES: check(f"draft says: {ph[:70]}", norm(ph) in draft, True)
pub_part = raw.split("## Not for publication")[0]
stray_numbers(pub_part, "draft")
check("draft has no em dashes", raw.count("\u2014"), 0, 0)
head = raw.split("\n---\n")[0].strip().splitlines()
check("H1 first", head[0].startswith("# "), True)
check("dek under 150 characters", len(head[-1].strip("*")) < 150, True)
check("house layout: About, Sources, Not for publication in order",
      [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
check("prediction confirmed (no tag left)", "[MATT TO CONFIRM]" not in raw, True)
check("no stale qualifying-offer range", "11-15" not in raw.split("## Not for publication")[0], True)
check("April 14 stays out of the published part", "April 14" not in pub_part, True)
check("no trade claim on the window", "sign or trade" not in pub_part, True)
src = raw.split("## Sources")[1].split("---")[0]
items = [l for l in src.splitlines() if l.strip()]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
links = re.findall(r"\]\((https?://[^)]+)\)", src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
ctx_urls = {r["url"] for r in ctx.values()}
house = ("ledgerandwhistle.substack.com", "github.com/mgag70-prog")
for u in links:
    if not any(h in u for h in house): check(f"source link is in context.csv: {u[:70]}", u in ctx_urls, True)
body = pub_part.split("## About this piece")[0]
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body)))
print(f"draft body: {WORDS} words"); check("body 1,000 to 1,400 words", 1000 <= WORDS <= 1400, True)

captxt = (ROOT / "figures" / "captions.md").read_text()
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=10)
check("captions have no em dashes", captxt.count("\u2014"), 0, 0)

thread_path = ROOT / "x-thread.md"
posts = re.split(r"^## Post \d+.*$", thread_path.read_text(), flags=re.M)[1:]
check("thread has six posts", len(posts), 6, 0)
for i, tbody in enumerate(posts, 1):
    text = "\n".join(l for l in tbody.strip().splitlines() if not l.startswith("Attach:")).strip()
    length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
    check(f"post {i} length {length} under 280", length < 280, True)
    for fig in NUMBER.findall(re.sub(r"https?://\S+|\[URL\]", "", text)):
        if fig.strip() and norm(fig.rstrip(",")) not in draft:
            check(f"post {i} figure verbatim in draft: {fig}", False, True)
check("thread ends with the piece link", posts[-1].strip().endswith("https://ledgerandwhistle.substack.com/p/26-days-left-the-owners-moved-their"), True)
check("thread has no em dashes", thread_path.read_text().count("\u2014"), 0, 0)

paste = ROOT / "paste-into-substack.html"
if paste.exists():
    html = paste.read_text()
    check("paste: stops above Not for publication", "Not for publication" not in html, True)
    check("paste: no tables", "<table" not in html and "|---" not in html, True)
    check("paste: every draft link live", all(f'href="{u}"' in html for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part)), True)
    check("paste: no em dashes", html.count("\u2014"), 0, 0)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
