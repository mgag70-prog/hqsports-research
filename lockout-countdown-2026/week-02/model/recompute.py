#!/usr/bin/env python3
"""lockout-countdown-2026 week 2: the free-agent market against November 2021. Data checks only; Claude Code
extends this to assert every number and key phrase in draft.md, captions and x-thread.md. Run from anywhere."""
import csv, pathlib, re, sys
from datetime import date
ROOT = pathlib.Path(__file__).resolve().parents[1]
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
ctx = {r["key"]: r for r in csv.DictReader(open(ROOT / "data" / "context.csv"))}
top = list(csv.DictReader(open(ROOT / "data" / "mlbtr-top50.csv")))
sig = list(csv.DictReader(open(ROOT / "data" / "signings.csv")))
V = lambda k: float(ctx[k]["value"])
check("top 50 rows", len(top), 50, 0)
check("ranks 1-50 complete", sorted(int(r["rank"]) for r in top), list(range(1, 51)))
T = sum(float(r["total_mm"]) for r in top)
check("top 50 predicted $M", round(T, 2), V("top50_total"), 0.001)
check("top 50 predicted $B", round(T / 1000, 2), 2.38, 0)
SK = float(top[0]["total_mm"]); check("Skubal predicted $M", SK, 425.0, 0)
check("Skubal share of top 50 %", round(100 * SK / T, 1), 17.8, 0)
check("top 50 without Skubal $B", round((T - SK) / 1000, 2), 1.96, 0)
check("top 10 predicted $M", sum(float(r["total_mm"]) for r in top[:10]), 1254.0, 0)
nine = [r for r in top if float(r["total_mm"]) >= 100]; check("predicted nine-figure deals", len(nine), 5, 0)
check("predicted nine-figure names", [r["player"] for r in nine], ["Tarik Skubal", "Trevor Rogers", "Freddy Peralta", "Seiya Suzuki", "Randy Arozarena"])
N21 = V("nov2021_total"); check("Nov 2021 committed $B", round(N21 / 1000, 1), 1.7, 0)
check("top 50 prediction vs Nov 2021, ratio", round(T / N21, 2), 1.39, 0)
check("Rangers 2021 share of Nov 2021 %", round(100 * V("nov2021_rangers") / N21, 1), 32.8, 0)
check("Seager + Semien $M", V("nov2021_seager") + V("nov2021_semien"), 500.0, 0)
pg = [r for r in sig if r["player"] == "Emilio Pagan"][0]
check("Pagan $M", float(pg["value_m"]), V("pagan_value"), 0)
check("Pagan rank in MLBTR top 50", int(pg["mlbtr_rank"]), 35, 0)
check("Pagan predicted $M", float([r for r in top if r["rank"] == "35"][0]["total_mm"]), 20.0, 0)
check("Pagan above declined option $M", V("pagan_value") - V("pagan_option_declined"), 1.0, 0)
check("Pagan vs Nov 2021 %", round(100 * V("pagan_value") / N21, 2), 0.64, 0)
known = sum(float(r["value_m"]) for r in sig if r["value_m"])
check("reported $M committed through Nov 10", known, 11.0, 0)
check("signings with reported terms", sum(1 for r in sig if r["value_m"]), 1, 0)
check("days left Nov 11 -> Dec 1", (date(2026, 12, 1) - date(2026, 11, 11)).days, int(V("days_left_from_nov11")), 0)
check("window day of Pagan (Nov 2 = day 1)", (date(2026, 11, 10) - date(2026, 11, 2)).days + 1, 9, 0)
check("window days elapsed through Nov 11 (Nov 2 = day 1)", (date(2026, 11, 11) - date(2026, 11, 2)).days + 1, 10, 0)
check("window length both ends", (date(2026, 12, 1) - date(2026, 11, 2)).days + 1, 30, 0)
check("2021 window Nov 3 -> Dec 1 both ends", (date(2021, 12, 1) - date(2021, 11, 3)).days + 1, 29, 0)
check("Nov 17 is a Tuesday", date(2026, 11, 17).strftime("%A"), "Tuesday")
check("Nov 18 is a Wednesday (week 3)", date(2026, 11, 18).strftime("%A"), "Wednesday")
check("QO total if all 8 accept $M", round(8 * V("qo_value"), 1), 185.2, 0)

print("\n-- figures derived for the draft --")
run = 0.0
for r in top:
    run += float(r["total_mm"])
    if run > N21: CROSS = int(r["rank"]); CROSS_RUN = run; break
check("running total passes Nov 2021 at rank", CROSS, 19, 0)
check("running total at rank 19 $M", round(CROSS_RUN, 1), 1724.0, 0)
check("names without Skubal", len(top) - 1, 49, 0)
check("Nov 11 is a Wednesday", date(2026, 11, 11).strftime("%A"), "Wednesday")
check("Nov 3 is a Tuesday", date(2026, 11, 3).strftime("%A"), "Tuesday")
check("8 qualifying-offer players", int(V("qo_count")), 8, 0)
check("Pagan rank in the CSV is the Pagan prediction", [r["prediction"] for r in top if r["rank"] == "35"][0], ctx["pagan_mlbtr_prediction"]["value"])
check("Skubal prediction text", top[0]["prediction"], ctx["skubal_prediction"]["value"])
CUBS = {r["player"]: int(r["rank"]) for r in top if r["player"] in ("Seiya Suzuki", "Ian Happ", "Shota Imanaga")}
check("Cubs in the top 50 (context.csv)", CUBS, {"Seiya Suzuki": 4, "Ian Happ": 17, "Shota Imanaga": 21})
unreported = [r["player"] for r in sig if not r["value_m"]]
check("signings without reported terms", unreported, ["Robert Stock", "Ryan Weiss"])

print("\n-- draft, captions, thread --")
b1 = lambda v: f"${v / 1000:.1f} billion"; b2 = lambda v: f"${v / 1000:.2f} billion"; m0 = lambda v: f"${v:,.0f} million"
DAYS = int(V("days_left_from_nov11")); PAG = V("pagan_value")
PCT21 = f"{100 * PAG / N21:.2f}%"; SKP = f"{100 * SK / T:.1f}%"; RATIO = f"{T / N21:.2f}"
COVER = f"{DAYS} days. {m0(PAG)}."
WEEK1 = ctx["week1_prediction"]["url"]
DRAFT_PHRASES = [
    f"# {DAYS} days left, and the MLB free-agent market has moved {m0(PAG)}.",
    f"teams committed {b1(N21)} in November. Nine days into this window, the first significant deal is one year.",
    "MLB's last offer came on Tuesday, November 3, when it pushed its salary cap back to 2028, and the union rejected it the same day",
    "I looked again on November 9 and again today and found no new proposal and no counter",
    f"[Last week's countdown]({WEEK1})",
    f"The agreement expires at 11:59 p.m. ET on December 1, {DAYS} days from today.",
    f"in November 2021, clubs committed more than {b1(N21)} to free agents before the December 2 lockout",
    f"{['Zero','One','Two','Three','Four','Five'][int(V('nov2021_ninefigure'))]} of those contracts reached nine figures",
    f"The Rangers alone spent ${V('nov2021_rangers'):.1f} million, {100 * V('nov2021_rangers') / N21:.1f}% of the total, on Corey Seager (10 years, {m0(V('nov2021_seager'))}), Marcus Semien (7 years, {m0(V('nov2021_semien'))}) and Jon Gray",
    f"Free agency opened at 5 p.m. ET on November 2, and {ctx['fa_count']['value']} players hit the market",
    "Then on November 10, day 9 of the 30-day window, the Tigers agreed with reliever Emilio Pagán on a one year deal worth about $11 million, Jon Heyman reported",
    '"this year\'s first significant move on the free agent market."',
    f"Pagán had turned down a {m0(V('pagan_option_declined'))} player option with Cincinnati", f"paid him about {m0(PAG - V('pagan_option_declined'))} more",
    f"its prediction was two years and {m0(float([r for r in top if r['rank'] == '35'][0]['total_mm']))}, No. {pg['mlbtr_rank']} on its top 50",
    "Ryan Weiss to the Padres on one year with a club option, and Robert Stock to the Mets",
    f"the reported total through November 10 is {m0(known)}, {PCT21} of what clubs committed in November 2021",
    f"\n{COVER}\n",
    f"MLB Trade Rumors' top 50, published November 2, adds up to {b2(T)}, {RATIO} times November 2021, and the first {CROSS} names on the list pass the 2021 total by themselves",
    f"Tarik Skubal is {SKP} of it on his own, predicted at nine years and {m0(SK)}; take him out and the other {len(top) - 1} come to {b2(T - SK)}",
    f"There are five predicted nine-figure deals (Skubal, Trevor Rogers, Freddy Peralta, Seiya Suzuki and Randy Arozarena), the same count as November 2021",
    f"Those are predictions for the whole offseason, not for the next {DAYS} days",
    "He's hoping to get a deal done before the lockout, Heyman reported, and the Mets have a meeting with him set for next week",
    "Dodgers general manager Brandon Gomes says his club expects to meet with him",
    f'"{ctx["wary_quote"]["value"]}"', f'"{ctx["deadline_quote"]["value"]}"',
    "If a cap arrives in 2028, every long contract signed this month is a bet on rules nobody has agreed to",
    f"The {int(V('qo_count'))} players who got the ${V('qo_value'):.2f} million qualifying offer have until Tuesday, November 17 to answer".replace("The 8 players", "The eight players"),
    "by 6 p.m. ET the same day", "The non-tender deadline is November 20",
    "the December 7-9 Winter Meetings in San Diego",
    f"| Days left | {DAYS} |", "| Last proposal | MLB, November 3 |", "| Union's last counter | As reported November 3 |",
    f"| Reported free-agent dollars | {m0(known)} |",
    "| Next dates | Qualifying-offer deadline November 17; Rule 5 protection November 17; non-tender November 20 |",
    "Next week's countdown runs Wednesday, November 18.",
    f"Clubs commit less to free agents before the lockout than the {b1(N21)} they committed in November 2021. Checkable December 2",
    "Last week's call stands: no new agreement by 11:59 p.m. ET on December 1, and a lockout on December 2.",
    "A signing without reported terms counts as zero", "which left out Javier Báez's $140 million deal, made official December 1",
    "MLB Trade Rumors' top 50 are predictions for the full offseason",
    "I held Cubs season tickets from 1998 to 2021",
    f"Seiya Suzuki (No. {CUBS['Seiya Suzuki']}), Ian Happ (No. {CUBS['Ian Happ']}) and Shota Imanaga (No. {CUBS['Shota Imanaga']})",
]
def norm(t): return re.sub(r"[ \t]+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {"1998", "2021", "2026", "2028", "50", "30", str(DAYS), str(CROSS), "35", "11"}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:-\d{1,2})?\b|"
                   r"\b\d{1,2}(?::\d\d)? p\.m\.|Rule 5|Week 2|\bfig-0[1-3]\b")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b")
def stray_numbers(text, label, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in KNOWN: check(f"{label}: number not traced to the data: {fig}", False, True)
draft_path = ROOT / "draft.md"
raw = draft_path.read_text(); draft = norm(raw)
for ph in DRAFT_PHRASES: check(f"draft says: {ph.strip()[:70]}", norm(ph) in draft, True)
pub_part = raw.split("## Not for publication")[0]
stray_numbers(pub_part, "draft")
check("draft has no em dashes", raw.count("—"), 0, 0)
check("draft has no ordinals", ORDINAL.findall(raw), [])
head = raw.split("\n---\n")[0].strip().splitlines()
check("H1 first", head[0].startswith("# "), True)
DEK = head[-1].strip("*"); print(f"dek: {len(DEK)} characters")
check("dek under 150 characters", len(DEK) < 150, True)
check("house layout: About, Sources, Not for publication in order",
      [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
check("prediction confirmed (no tag left)", pub_part.count("[MATT TO CONFIRM]"), 0, 0)
check("cover line appears once in the published part", pub_part.count(COVER), 1, 0)
check("2021 window length not stated", re.search(r"29 days|29-day", pub_part) is None, True)
check("no GM Meetings claim for the Skubal meetings", "GM Meetings" not in pub_part and "this week" not in pub_part, True)
LINES11 = [l for l in pub_part.split("## About this piece")[0].splitlines() if "$11 million" in l]
check("every $11 million line is the H1, the cover line, Pagan's deal or says reported",
      [l[:50] for l in LINES11 if not (l.startswith("# ") or l == COVER or "Pagán on one year" in l or "eported" in l)], [])
check("week 1's offer numbers not repeated", all(x not in pub_part for x in ("$258.2", "$180.2", "$162.18", "$245.3", "$171.2")), True)
src = raw.split("## Sources")[1].split("---")[0]
items = [l for l in src.splitlines() if l.strip()]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
links = re.findall(r"\]\((https?://[^)]+)\)", src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
known_urls = {r["url"] for r in ctx.values()} | {r["url"] for r in sig}
house = ("ledgerandwhistle.substack.com", "github.com/mgag70-prog")
for u in links:
    if not any(h in u for h in house): check(f"source link is in the data files: {u[:70]}", u in known_urls, True)
for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part.split("## Sources")[0]):
    check(f"body link is listed or house: {u[:60]}", u in links or any(h in u for h in house), True)
body = pub_part.split("## About this piece")[0]
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body)))
print(f"draft body: {WORDS} words"); check("body 800 to 1,100 words", 800 <= WORDS <= 1100, True)

captxt = (ROOT / "figures" / "captions.md").read_text()
for ph in (f"more than {b1(N21)} in November 2021", f"against {m0(known)} in reported terms in 2026 through November 10, {PCT21} of it",
           f"Red is Tarik Skubal's predicted {m0(SK)}, {SKP} of the {b2(T)} total", f"which the running total passes at No. {CROSS}",
           f"not for the {DAYS} days before the agreement expires", f"With {DAYS} days left, the agreement expires at 11:59 p.m. ET on December 1"):
    check(f"captions say: {ph[:60]}", ph in norm(captxt), True)
KNOWN |= {"50", "1.7", str(CROSS)}
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=8)
check("captions have no em dashes", captxt.count("—"), 0, 0)
check("captions have no ordinals", ORDINAL.findall(captxt), [])

thread_path = ROOT / "x-thread.md"
thread = thread_path.read_text()
posts = re.split(r"^## Post \d+.*$", thread, flags=re.M)[1:]
check("thread has five posts", len(posts), 5, 0)
for i, tbody in enumerate(posts, 1):
    text = "\n".join(l for l in tbody.strip().splitlines() if not l.startswith("Attach:")).strip()
    length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
    check(f"post {i} length {length} under 280", length < 280, True)
    for fig in NUMBER.findall(re.sub(r"https?://\S+|\[URL\]", "", text)):
        if fig.strip() and norm(fig.rstrip(",")) not in draft:
            check(f"post {i} figure verbatim in draft: {fig}", False, True)
check("thread ends with the cover line and the piece link", posts[-1].strip().endswith(f"{COVER}\nhttps://ledgerandwhistle.substack.com/p/20-days-left-and-the-mlb-free-agent"), True)
check("thread has no em dashes", thread.count("—"), 0, 0)
check("thread has no ordinals", ORDINAL.findall(thread), [])
check("thread has no hashtags", re.search(r"(^|\s)#\w", "\n".join(posts)) is None, True)

paste = ROOT / "paste-into-substack.html"
if paste.exists():
    html = paste.read_text()
    check("paste: stops above Not for publication", "Not for publication" not in html, True)
    check("paste: no tables", "<table" not in html and "|---" not in html, True)
    check("paste: every draft link live", all(f'href="{u}"' in html for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part)), True)
    check("paste: no em dashes", html.count("—"), 0, 0)
    check("paste: three figure slots", html.count("[Insert image: figures/fig-0"), 3, 0)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
