#!/usr/bin/env python3
"""lockout-countdown-2026 week 3: test MLB's 'widest payroll gap in sports' on 2026 luxury-tax payrolls, against the
spread other leagues' rules allow, plus free-agent dollars and qualifying-offer outcomes through November 17.
Asserts every number and key phrase in draft.md, figures/captions.md and x-thread.md. Run from anywhere."""
import csv, pathlib, re, statistics, sys
from datetime import date
ROOT = pathlib.Path(__file__).resolve().parents[1]; REPO = ROOT.parents[1]
fails = []
def check(name, got, want, tol=0.005):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
c = {r["key"]: r for r in csv.DictReader(open(ROOT / "data" / "context.csv"))}
V = lambda k: float(c[k]["value"])
P = sorted(((float(r["tax_payroll_m"]), r["team"]) for r in csv.DictReader(open(REPO / "mlb-floor-2026" / "data" / "2026-vs-cap-floor.csv"))), reverse=True)
check("clubs", len(P), 30, 0)
check("top payroll LAD $M", P[0], (433.06, "LAD"))
check("bottom payroll MIA $M", P[-1], (84.36, "MIA"))
RATIO = round(P[0][0] / P[-1][0], 2); check("top/bottom ratio", RATIO, 5.13, 0)
GAP = round(P[0][0] - P[-1][0], 2); check("top minus bottom $M", GAP, 348.70, 0)
MIL_RANK = [t for _, t in P].index("MIL") + 1
check("Brewers payroll rank", MIL_RANK, int(c["mil_payroll_rank_claim"]["value"]), 0)
check("Brewers payroll $M", dict((t, p) for p, t in P)["MIL"], V("mil_payroll"), 0)
check("Brewers in the bottom half", MIL_RANK > 15, True)
MED = round(statistics.median(p for p, _ in P), 3); check("median payroll $M", MED, 210.385, 0)
top5 = sum(p for p, _ in P[:5]); bot5 = sum(p for p, _ in P[-5:])
T5 = round(top5 / bot5, 2); check("top 5 / bottom 5 ratio", T5, 3.43, 0)
check("top 5 $M", round(top5, 2), 1772.43, 0); check("bottom 5 $M", round(bot5, 2), 516.57, 0)
DAYS = (date(2026, 12, 1) - date(2026, 11, 18)).days
check("days left Nov 18 -> Dec 1", DAYS, int(V("days_left_from_nov18")), 0)
check("Nov 25 is a Wednesday (week 4)", date(2026, 11, 25).strftime("%A"), "Wednesday")
check("Nov 18 is a Wednesday", date(2026, 11, 18).strftime("%A"), "Wednesday")

print("\n-- other leagues (rules, not payrolls) --")
NFL = round(1 / (V("nfl_min_cash_pct") / 100), 2); check("NFL cap / cash floor", NFL, 1.11, 0)
NBA = round(V("nba_cap_2026_27") / V("nba_min_team_salary_2026_27"), 2); check("NBA cap / minimum", NBA, 1.11, 0)
NBA2 = round(V("nba_second_apron_2026_27") / V("nba_min_team_salary_2026_27"), 2); check("NBA second apron / minimum", NBA2, 1.49, 0)
NHL = round(V("nhl_upper_2026_27") / V("nhl_lower_2026_27"), 2); check("NHL upper / lower", NHL, 1.35, 0)
check("every league's widest rule ratio is under half of MLB's actual spread", max(NFL, NBA, NBA2, NHL) < RATIO / 2, True)
check("MLB spread over NBA second-apron ratio", round(RATIO / NBA2, 2), 3.44, 0)

print("\n-- free agents and qualifying offers --")
FA = {k: V(k) for k in c if k.startswith("fa_")}
check("five deals with reported terms", len(FA), 5, 0)
TOT = round(sum(FA.values()), 2); check("reported $M through Nov 17", TOT, V("reported_fa_dollars_nov17"), 0)
check("reported $M through Nov 15 (outline) + May", round(V("reported_fa_dollars_nov15") + FA["fa_may"], 2), TOT, 0)
PCT = f"{100 * TOT / V('nov2021_total'):.2f}%"; check("vs Nov 2021", PCT, "9.29%")
QA = c["qo_accepted"]["value"].split("; "); QD = c["qo_declined"]["value"].split("; ")
check("qualifying offers: 2 accepted + 6 declined = 8", (len(QA), len(QD), len(QA) + len(QD)), (2, 6, 8))
QO2 = round(2 * V("qo_value"), 2); check("two accepted QOs $M", QO2, 46.3, 0)
check("total if accepted QOs were counted $M", round(TOT + QO2, 2), 205.05, 0)
check("NFL early-1990s award tripled", round(3 * 543 / 1000, 2), 1.63, 0)

print("\n-- draft, captions, thread --")
m2 = lambda v: f"${v:,.2f} million"
COVER = f"{DAYS} days. {RATIO:.2f} times."
W1 = c["week1_lines"]["url"]; W2 = c["week2_call"]["url"]; FLOOR = c["payroll_source"]["url"]
DRAFT_PHRASES = [
    f"# {DAYS} days left, and MLB took its salary-cap case to fans. Its biggest claim checks out on payroll.",
    f"*MLB says baseball has the widest payroll gap in sports. On 2026 payrolls the top club spent {RATIO:.2f} times the bottom one.*",
    "MLB's last offer came on November 3, and the union rejected it the same day, MLB Trade Rumors reported",
    "I checked again on November 16 and November 17 and found no new proposal and no counter",
    f"The agreement expires at 11:59 p.m. ET on December 1, {DAYS} days from today.",
    f"[Week 1]({W1})", f"[week 2]({W2})",
    f'"Level the Playing Field" campaign, MLB released a five-minute video, "{c["mlb_video"]["value"]},"',
    "with Morgan Sword, its executive vice president of baseball operations",
    "It's pinned on MLB's X account and had passed 1.7 million impressions there when Eric Fisher wrote it up for Front Office Sports on November 16",
    f'"{c["sword_quote"]["value"]}"', f'"{c["meyer_quote"]["value"]}."', f'"{c["taillon"]["value"]}."',
    f"[the floor piece]({FLOOR})",
    f"the Dodgers spent ${P[0][0]:.2f} million and the Marlins ${P[-1][0]:.2f} million. That's {RATIO:.2f} times as much, a gap of ${GAP:.1f} million",
    f"the top five payrolls together came to {T5:.2f} times the bottom five", f"The median club spent ${MED:.1f} million.",
    f"\n{COVER}\n",
    f"Milwaukee, MLB's smallest media market, won the World Series with the No. {MIL_RANK} payroll, Sword says, and the data agrees: ${V('mil_payroll'):.2f} million, No. {MIL_RANK} of 30",
    f"this year's champion came out of the bottom half of a league with a {RATIO:.2f}-to-1 spread",
    f"from a lower limit of ${V('nhl_lower_2026_27'):.1f} million to an upper limit of ${V('nhl_upper_2026_27'):.1f} million, {NHL:.2f} times",
    f"The NBA's salary cap is ${V('nba_cap_2026_27'):.3f} million against a minimum team salary of ${V('nba_min_team_salary_2026_27'):.3f} million, {NBA:.2f} times",
    f"the realistic ceiling is the second apron at ${V('nba_second_apron_2026_27'):.3f} million, {NBA2:.2f} times the minimum",
    f"The NFL set its 2026 cap at ${V('nfl_cap_2026'):.1f} million, and its floor is in cash: each club has to spend {V('nfl_min_cash_pct'):.0f}% of the caps across 2024-2026 combined, which puts the rule at {NFL:.2f} times, measured over three seasons",
    "My read: Sword's line holds.", "Where the video overreaches is the next step, that a cap is the fix.",
    f"Week 1 found the owners' delayed lines still catch [{c['week1_lines']['value']}]({W1}) their May lines did",
    "MLB has started planning for the union to file a disclaimer of interest during a lockout, Jared Diamond reported in The Wall Street Journal",
    "as Anthony Franco summarized it for MLB Trade Rumors on November 12", '"the nuclear option."',
    "The union has never done it", "the Curt Flood Act of 1998 opens the door", "deep into a lockout",
    "In the early 1990s a jury found the NFL had broken antitrust law", "awarded players $543,000 in damages, tripled to $1.63 million", "In 2011 a trial court lifted the NFL lockout with an injunction, and the Eighth Circuit reversed it.",
    f"By my count, clubs have committed {m2(TOT)} in reported contract terms through November 17, across five deals",
    f"Emilio Pagán to the Tigers for about ${FA['fa_pagan']:.0f} million, Evan Phillips to the Braves for ${FA['fa_phillips']:.0f} million over three years, Jake Bauers to the Red Sox for ${FA['fa_bauers']:.0f} million over four, Tim Hill back to the Yankees for {m2(FA['fa_hill'])}, and on November 17 Dustin May to the White Sox for ${FA['fa_may']:.1f} million over three",
    f"That's {PCT} of what clubs committed in November 2021.",
    f"David Bednar (Yankees) and Ryan Jeffers (Twins) took the one-year ${V('qo_value'):.2f} million offer",
    "Bauers had already turned his down by signing in Boston, and Randy Arozarena, Brandon Lowe, Trevor Rogers, Adrián Morejón and Seiya Suzuki declined",
    f"I've left the two accepted offers, ${QO2:.1f} million together, out of the free-agent total, since neither player went to market.",
    f"| Days left | {DAYS} |", "| Last proposal | MLB, November 3 |", "| Union's last counter | As reported November 3 |",
    f"| Reported free-agent dollars | {m2(TOT)} |",
    "| Next dates | Non-tender November 20; expiration 11:59 p.m. ET December 1; Winter Meetings December 7-9 at risk |",
    "Next week's countdown runs Wednesday, November 25, the last one before the deadline.",
    "The MLBPA does not file a disclaimer of interest before April 1, 2027.",
    "no new agreement by 11:59 p.m. ET on December 1, and clubs commit less to free agents before the lockout than the $1.7 billion they committed in November 2021",
    "which include $18 million of benefits for every club", "the NFL floor is cash spending measured over 2024-2026",
    f"{m2(TOT)} is the least clubs have committed", "Days left counts from November 18 to December 1.",
    "I held Cubs season tickets from 1998 to 2021", "Seiya Suzuki, one of the players who declined a qualifying offer, was last with the Cubs",
]
def LINKS(t): return re.findall(r"\]\((https?://\S+?)\)(?=[,.]?(?:\s|$))", t, re.M)
def norm(t): return re.sub(r"[ \t]+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",.") for x in NUMBER.findall(ph)}
KNOWN |= {"30", "2026", "2021", "1998", "13", "5.13", "19", "2026-27"}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:-\d{1,2})?(?:, \d{4})?\b|"
                   r"\b\d{1,2}(?::\d\d)? p\.m\.|Week 3|\bfig-0[1-2]\b|\bweeks? [12]\b|Week [12]\b")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b")
def stray_numbers(text, label, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",.") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in KNOWN: check(f"{label}: number not traced to the data: {fig}", False, True)
raw = (ROOT / "draft.md").read_text(); draft = norm(raw)
for ph in DRAFT_PHRASES: check(f"draft says: {ph.strip()[:70]}", norm(ph) in draft, True)
pub = raw.split("## Not for publication")[0]
stray_numbers(pub, "draft")
check("draft has no em dashes", raw.count("—"), 0, 0)
check("draft has no ordinals", ORDINAL.findall(raw), [])
head = raw.split("\n---\n")[0].strip().splitlines()
check("H1 first", head[0].startswith("# "), True)
DEK = head[-1].strip("*"); print(f"dek: {len(DEK)} characters"); check("dek under 150 characters", len(DEK) < 150, True)
check("house layout: About, Sources, Not for publication in order",
      [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
TAGS = pub.count("[MATT TO CONFIRM]")
check("prediction confirmed: no [MATT TO CONFIRM] tag left", TAGS, 0, 0)
check("cover line appears once in the published part", pub.count(COVER), 1, 0)
check("median written as $210.4 million, not $210.385", "210.385" not in pub and "$210.4 million" in pub, True)
check("no other league figure estimated: every league number is in context.csv",
      all(s in pub for s in ("$301.2 million", "90%", "$164.961 million", "$148.465 million", "$221.686 million", "$104.0 million", "$76.9 million")), True)
check("no stale outline total", "$106.25" not in pub and "106 million" not in pub, True)
check("week 1's offer numbers not repeated", all(x not in pub for x in ("$258.2", "$180.2", "$162.18", "$245.3", "$171.2")), True)
check("week 2's 2021 breakdown not repeated", all(x not in pub for x in ("$561.2", "Seager", "Semien", "$2.38 billion")), True)
src = raw.split("## Sources")[1].split("---")[0]
items = [l for l in src.splitlines() if l.strip()]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
links = LINKS(src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
known_urls = {r["url"] for r in c.values()}
house = ("ledgerandwhistle.substack.com", "github.com/mgag70-prog")
for u in links:
    if not any(h in u for h in house): check(f"source link is in context.csv: {u[:70]}", u in known_urls, True)
for u in LINKS(pub.split("## Sources")[0]):
    check(f"body link is listed or house: {u[:60]}", u in links or any(h in u for h in house), True)
body = pub.split("## About this piece")[0]
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body)))
print(f"draft body: {WORDS} words"); check("body 850 to 1,150 words", 850 <= WORDS <= 1150, True)

captxt = (ROOT / "figures" / "captions.md").read_text()
for ph in (f"The Dodgers' ${P[0][0]:.2f} million is {RATIO:.2f} times the Marlins' ${P[-1][0]:.2f} million, a gap of ${GAP:.1f} million",
           f"the median club spent ${MED:.1f} million", f"with the No. {MIL_RANK} payroll, ${V('mil_payroll'):.2f} million",
           f"the 2026 cap of ${V('nfl_cap_2026'):.1f} million over a cash floor of 90% of the caps, measured across 2024-2026, {NFL:.2f} times",
           f"the ${V('nba_cap_2026_27'):.3f} million cap over the ${V('nba_min_team_salary_2026_27'):.3f} million minimum team salary, {NBA:.2f} times, or {NBA2:.2f} times with the ${V('nba_second_apron_2026_27'):.3f} million second apron",
           f"the ${V('nhl_upper_2026_27'):.1f} million upper limit over the ${V('nhl_lower_2026_27'):.1f} million lower limit, {NHL:.2f} times",
           f"MLB: the Dodgers over the Marlins, {RATIO:.2f} times"):
    check(f"captions say: {ph[:60]}", ph in norm(captxt), True)
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=10)
check("captions have no em dashes", captxt.count("—"), 0, 0)
check("captions have no ordinals", ORDINAL.findall(captxt), [])

thread = (ROOT / "x-thread.md").read_text()
posts = re.split(r"^## Post \d+.*$", thread, flags=re.M)[1:]
check("thread has five posts", len(posts), 5, 0)
for i, tbody in enumerate(posts, 1):
    text = "\n".join(l for l in tbody.strip().splitlines() if not l.startswith("Attach:")).strip()
    length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
    check(f"post {i} length {length} under 280", length < 280, True)
    for fig in NUMBER.findall(re.sub(r"https?://\S+|\[URL\]", "", text)):
        if fig.strip() and norm(fig.rstrip(",.")) not in draft:
            check(f"post {i} figure verbatim in draft: {fig}", False, True)
check("thread ends with the cover line and the piece link", posts[-1].strip().endswith(f"{COVER}\nhttps://ledgerandwhistle.substack.com/p/13-days-left-and-mlb-took-its-salary"), True)
check("thread has no em dashes", thread.count("—"), 0, 0)
check("thread has no ordinals", ORDINAL.findall(thread), [])
check("thread has no hashtags", re.search(r"(^|\s)#\w", "\n".join(posts)) is None, True)

paste = ROOT / "paste-into-substack.html"
if paste.exists():
    html = paste.read_text()
    check("paste: stops above Not for publication", "Not for publication" not in html, True)
    check("paste: no markdown table", "|---" not in html, True)
    check("paste: every draft link live", all(f'href="{u}"' in html for u in LINKS(pub)), True)
    check("paste: no em dashes", html.count("—"), 0, 0)
    check("paste: two figure slots", html.count("[Insert image: figures/fig-0"), 2, 0)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
