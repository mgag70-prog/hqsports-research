#!/usr/bin/env python3
"""cbb-revenue-share-2026: who gets paid in men's basketball, by conference, from the College Sports
Commission's School Revenue Share Compensation Report (scraped Nov 17, 2026). Checks the data (and the CSV
against the raw scrape when raw/ is present), then asserts every number and key phrase in draft.md,
figures/captions.md and x-thread.md the way pca-mvp-award-2026 does. Run from anywhere; exits 1 on any failure."""
import csv, html, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PREDICTION_CONFIRMED = True   # flip to True when Matt confirms "What I expect" and the tag comes out of draft.md
fails = []
def check(name, got, want, tol=0.05):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
R = list(csv.DictReader(open(ROOT / "data" / "csc-revshare.csv")))
c = {r["key"]: r for r in csv.DictReader(open(ROOT / "data" / "context.csv"))}
def get(sport, conf, cohort, pos="All"):
    return [r for r in R if r["sport"] == sport and r["conference"] == conf and r["cohort"] == cohort and r["position"] == pos][0]
A4 = ["Atlantic Coast Conference", "Big 12 Conference", "Big Ten Conference", "Southeastern Conference"]
SH = {"Atlantic Coast Conference": "ACC", "Big 12 Conference": "Big 12", "Big Ten Conference": "Big Ten", "Southeastern Conference": "SEC"}
MBB, WBB, NON = "Men's Basketball", "Women's Basketball", "Non-A4 Conferences"
check("rows", len(R), 68, 0)

print("\n-- CSV against the raw scrape --")
scrape = ROOT / "raw" / "csc-revshare-scrape.json"
if not scrape.exists():
    print("skip (no raw/csc-revshare-scrape.json)")
else:
    money = lambda s: "" if s.strip() in ("-", "") else str(int(s.replace("$", "").replace(",", "")))
    seen = 0
    for t in json.load(open(scrape)):
        sport = ("Men's " if t["g"] == "mens" else "Women's ") + t["sport"] if t["sport"] == "Basketball" else t["sport"]
        pos = t["pos"] or "All"
        conf = None
        for row in t["rows"][1:]:
            if t["sport"] == "Basketball":
                conf, n = re.match(r"(.+) \(n=([\d,]+)\)", row[0]).groups(); cells = row[1:]
                cohort = "with_zero" if t["zero"].startswith("With ") else "without_zero"
            else:
                if not row[0].startswith("With"): conf, row = row[0], row[1:]
                cohort = "with_zero" if row[0].startswith("With ") else "without_zero"
                n, cells = re.search(r"n=([\d,]+)", row[0])[1], row[1:]
            r = get(sport, conf, cohort, pos)
            got = [r["n"]] + [r[k] for k in ("p90", "p75", "p50", "p25", "p10")]
            want = [n.replace(",", "")] + [money(x) for x in cells]
            if got != want: check(f"CSV matches scrape: {sport} {pos} {conf} {cohort}", got, want)
            seen += 1
    check("scrape rows matched against the CSV", seen, len(R), 0)

print("\n-- men's basketball, share of roster paid, medians --")
def n(sport, conf, cohort, pos="All"): return int(get(sport, conf, cohort, pos)["n"])
def p(sport, conf, cohort, k, pos="All"): return int(get(sport, conf, cohort, pos)[k])
paid = {x: 100 * n(MBB, x, "without_zero") / n(MBB, x, "with_zero") for x in A4}
for x in A4:
    print(f"{SH[x]}: roster {n(MBB, x, 'with_zero')}, paid {n(MBB, x, 'without_zero')} ({paid[x]:.1f}%), median all {p(MBB, x, 'with_zero', 'p50')}, "
          f"median paid {p(MBB, x, 'without_zero', 'p50')}, p25 paid {p(MBB, x, 'without_zero', 'p25')}, p90 all {p(MBB, x, 'with_zero', 'p90')}")
check("SEC MBB % paid", round(paid["Southeastern Conference"], 1), 45.1, 0)
check("Big 12 MBB % paid", round(paid["Big 12 Conference"], 1), 79.0, 0)
check("Big Ten MBB % paid", round(paid["Big Ten Conference"], 1), 59.4, 0)
check("ACC MBB % paid", round(paid["Atlantic Coast Conference"], 1), 61.2, 0)
check("SEC pays the smallest MBB share, Big 12 the largest", (min(paid, key=paid.get), max(paid, key=paid.get)), ("Southeastern Conference", "Big 12 Conference"))
check("SEC MBB unpaid share over half ('more than half')", 100 - paid["Southeastern Conference"] > 50, True)
check("SEC MBB median (with $0)", p(MBB, "Southeastern Conference", "with_zero", "p50"), 0, 0)
check("Big 12 MBB median (with $0)", p(MBB, "Big 12 Conference", "with_zero", "p50"), 100000, 0)
check("SEC MBB paid-only median", p(MBB, "Southeastern Conference", "without_zero", "p50"), 175000, 0)
check("SEC MBB paid-only 25th pct (highest of A4)", p(MBB, "Southeastern Conference", "without_zero", "p25") == max(p(MBB, x, "without_zero", "p25") for x in A4), True)
check("Big 12 MBB paid-only median lowest of A4", p(MBB, "Big 12 Conference", "without_zero", "p50") == min(p(MBB, x, "without_zero", "p50") for x in A4), True)
check("SEC MBB 90th pct (with $0) lowest of A4", p(MBB, "Southeastern Conference", "with_zero", "p90") == min(p(MBB, x, "with_zero", "p90") for x in A4), True)
check("Big 12 MBB 90th pct (with $0) highest of A4", p(MBB, "Big 12 Conference", "with_zero", "p90") == max(p(MBB, x, "with_zero", "p90") for x in A4), True)
check("paid-only 90th pct order: Big 12, ACC, SEC, Big Ten", [SH[x] for x in sorted(A4, key=lambda x: -p(MBB, x, "without_zero", "p90"))], ["Big 12", "ACC", "SEC", "Big Ten"])
w4 = sum(n(MBB, x, "with_zero") for x in A4); p4 = sum(n(MBB, x, "without_zero") for x in A4)
check("A4 MBB roster n", w4, 1055, 0); check("A4 MBB paid n", p4, 644, 0); check("A4 MBB % paid", round(100 * p4 / w4, 1), 61.0, 0)
NONP = 100 * n(MBB, NON, "without_zero") / n(MBB, NON, "with_zero")
check("Non-A4 MBB % paid", round(NONP, 1), 62.8, 0)
check("Non-A4 pays a larger share than the A4 together ('a little more likely')", 0 < NONP - 100 * p4 / w4 < 3, True)
check("Non-A4 MBB paid-only median", p(MBB, NON, "without_zero", "p50"), 33000, 0)

print("\n-- women's basketball --")
wpaid = {x: 100 * n(WBB, x, "without_zero") / n(WBB, x, "with_zero") for x in A4}
for x in A4: print(SH[x], round(wpaid[x], 1), get(WBB, x, "with_zero")["p50"])
check("Big Ten WBB % paid", round(wpaid["Big Ten Conference"], 1), 79.4, 0)
check("SEC WBB % paid", round(wpaid["Southeastern Conference"], 1), 46.0, 0)
check("Big Ten largest, SEC smallest WBB share", (max(wpaid, key=wpaid.get), min(wpaid, key=wpaid.get)), ("Big Ten Conference", "Southeastern Conference"))
check("Big Ten WBB median (with $0)", p(WBB, "Big Ten Conference", "with_zero", "p50"), 31000, 0)
check("SEC WBB median (with $0)", p(WBB, "Southeastern Conference", "with_zero", "p50"), 0, 0)
ww4 = sum(n(WBB, x, "with_zero") for x in A4); wp4 = sum(n(WBB, x, "without_zero") for x in A4)
check("Big Ten WBB paid median highest of A4", p(WBB, "Big Ten Conference", "without_zero", "p50") == max(p(WBB, x, "without_zero", "p50") for x in A4), True)
check("A4 WBB % paid", round(100 * wp4 / ww4, 1), 64.7, 0)

print("\n-- football, A4, all positions --")
fw = sum(int(r["n"]) for r in R if r["sport"] == "Football" and r["conference"] == "A4 Conferences" and r["cohort"] == "with_zero")
fp = sum(int(r["n"]) for r in R if r["sport"] == "Football" and r["conference"] == "A4 Conferences" and r["cohort"] == "without_zero")
check("A4 football roster n", fw, 7743, 0); check("A4 football paid n", fp, 5817, 0); check("A4 football % paid", round(100 * fp / fw, 1), 75.1, 0)
QB90, B12_90 = p("Football", "A4 Conferences", "with_zero", "p90", "Quarterback"), p(MBB, "Big 12 Conference", "with_zero", "p90")
check("A4 QB 90th pct", QB90, 1266500, 0)
check("A4 QB 90th vs Big 12 MBB 90th (x)", round(QB90 / B12_90, 1), 2.2, 0)
CAP = float(c["cap_2025_26"]["value"]); check("cap $M", CAP, 20.5, 0)

print("\n-- draft --")
d = lambda v: f"${int(v):,}"
pct = lambda x: f"{x:.1f}%"
def of(sport, x): return f"{n(sport, x, 'without_zero'):,} of {n(sport, x, 'with_zero'):,}"
B12, ACC, B10, SEC = A4[1], A4[0], A4[2], A4[3]
ILL = c["illinois_piece"]["url"]
COVER = "$0 for the median player."
PRED = "When the CSC publishes 2026-27 basketball numbers, the SEC is again the power conference that pays the smallest share of its men's basketball roster."
DRAFT_PHRASES = [
    f"# More than half the SEC's men's basketball players had no revenue-share payment by April 6. In the Big 12, the median player got {d(p(MBB, B12, 'with_zero', 'p50'))}.",
    f"*Every school worked under the same ${CAP} million cap. The four power conferences split basketball money in very different ways.*",
    "The College Sports Commission runs CAPS, the College Athlete Payment System, where schools record the revenue-share payments they make to athletes",
    f"Illinois [denied my records request]({ILL}) for what it paid athletes by sport",
    "What the report gives is percentiles, not totals.",
    "For men's basketball it covers payments made from July 1, 2025 to April 6, 2026; anything due after April 6 isn't in it.",
    "The tables stop at the conference, so no single school shows up.",
    f"Each of those schools worked under a ${CAP} million revenue-share cap for 2025-26, Ministry of Sport reported",
    "the report doesn't say how any of them divided it between sports",
    f"The Big 12 paid {pct(paid[B12])} of its men's basketball players, {of(MBB, B12)}. The ACC paid {pct(paid[ACC])} ({of(MBB, ACC)}) and the Big Ten {pct(paid[B10])} ({of(MBB, B10)}). The SEC paid {pct(paid[SEC])}, {of(MBB, SEC)}, so more than half the league's rostered players had no revenue-share payment recorded by April 6.",
    f"The median rostered Big 12 player got {d(p(MBB, B12, 'with_zero', 'p50'))}, the Big Ten's got {d(p(MBB, B10, 'with_zero', 'p50'))} and the ACC's {d(p(MBB, ACC, 'with_zero', 'p50'))}.",
    f"In the SEC, where fewer than half were paid, the middle of the roster lands on a zero: {COVER}",
    f"roughly three in four paid SEC players got at least {d(p(MBB, SEC, 'without_zero', 'p25'))}, against {d(p(MBB, B10, 'without_zero', 'p25'))} in the Big Ten, {d(p(MBB, B12, 'without_zero', 'p25'))} in the Big 12 and {d(p(MBB, ACC, 'without_zero', 'p25'))} in the ACC",
    f"Its paid median is {d(p(MBB, SEC, 'without_zero', 'p50'))}.",
    f"spreading money across most of its roster at a paid median of {d(p(MBB, B12, 'without_zero', 'p50'))}, the lowest of the four",
    f"The line a player had to clear to be in the top tenth was {d(p(MBB, B12, 'with_zero', 'p90'))} in the Big 12, {d(p(MBB, ACC, 'with_zero', 'p90'))} in the ACC and {d(p(MBB, B10, 'with_zero', 'p90'))} in the Big Ten. In the SEC it was {d(p(MBB, SEC, 'with_zero', 'p90'))}.",
    f"Among paid players alone, the SEC's top-tenth line is {d(p(MBB, SEC, 'without_zero', 'p90'))}, ahead of the Big Ten's {d(p(MBB, B10, 'without_zero', 'p90'))}.",
    f"Its paid median, {d(p(WBB, B10, 'without_zero', 'p50'))}, was the highest of the four, too.",
    f"Across the four power conferences, {pct(100 * p4 / w4)} of men's basketball players got paid, {p4:,} of {w4:,}. Outside them it was {pct(NONP)}, {of(MBB, NON)}, so a player in a smaller conference was a little more likely to get something.",
    f"the median paid player outside the four got {d(p(MBB, NON, 'without_zero', 'p50'))}",
    f"Power-conference football paid, or scheduled payments to, {pct(100 * fp / fw)} of its rostered players in 2026, {fp:,} of {fw:,} across positions.",
    f"At quarterback, the line for the top tenth was {d(QB90)}, {QB90 / B12_90:.1f} times the highest basketball figure above, the Big 12's {d(B12_90)}.",
    "Football counts payments made or scheduled in calendar 2026, and the CSC says that during the season CAPS treats virtually all contingent performance incentives as scheduled payments",
    "Basketball counts payments made through April 6. That's why I'm comparing shares and percentiles here and not adding anything up.",
    "My read is the SEC's basketball numbers look like a football-first league spending its cap where its money comes from. The data doesn't show school budgets",
    f"the Big Ten, which paid {pct(wpaid[B10])} of its women's players, {of(WBB, B10)}, with a median rostered player at {d(p(WBB, B10, 'with_zero', 'p50'))}.",
    f"The SEC paid {pct(wpaid[SEC])} ({of(WBB, SEC)}), the smallest share of the four again, and its median rostered player got {d(p(WBB, SEC, 'with_zero', 'p50'))}.",
    "Payments due after April 6 are missing, so an SEC school that pays late in the year would look smaller here than it is.",
    "The report also leaves out scholarships, cost-of-attendance stipends and Alston payments, and third-party NIL deals sit in a separate NIL Go report.",
    PRED + (" [MATT TO CONFIRM]" if not PREDICTION_CONFIRMED else ""),
    "scraped from its interactive tables on November 17, 2026 into data/csc-revshare.csv",
    "100 athletes for the top and bottom tenth, 40 for the quarters, 10 for the median",
    'The share paid is the "Without $0" cohort divided by the "With $0" cohort.',
    "*Disclosure: I'm an Illinois basketball and football fan, not an alum.*",
]
CAPTION_PHRASES = [
    f"Big 12 {pct(paid[B12])} ({of(MBB, B12)}), ACC {pct(paid[ACC])} ({of(MBB, ACC)}), Big Ten {pct(paid[B10])} ({of(MBB, B10)}), SEC {pct(paid[SEC])} ({of(MBB, SEC)}), and {pct(NONP)} ({of(MBB, NON)}) outside the four power conferences",
    f"{d(p(MBB, B12, 'with_zero', 'p50'))} in the Big 12, {d(p(MBB, ACC, 'with_zero', 'p50'))} in the ACC, {d(p(MBB, B10, 'with_zero', 'p50'))} in the Big Ten, {d(p(MBB, SEC, 'with_zero', 'p50'))} in the SEC and {d(p(MBB, NON, 'with_zero', 'p50'))} outside the four",
    "Percentiles by conference, not totals.",
    f"The SEC's bottom-quarter line, {d(p(MBB, SEC, 'without_zero', 'p25'))}, is the highest of the four (Big Ten {d(p(MBB, B10, 'without_zero', 'p25'))}, Big 12 {d(p(MBB, B12, 'without_zero', 'p25'))}, ACC {d(p(MBB, ACC, 'without_zero', 'p25'))}); its paid median is {d(p(MBB, SEC, 'without_zero', 'p50'))}",
    f"the Big 12 leads at {d(p(MBB, B12, 'without_zero', 'p90'))}, then the ACC at {d(p(MBB, ACC, 'without_zero', 'p90'))}, the SEC at {d(p(MBB, SEC, 'without_zero', 'p90'))} and the Big Ten at {d(p(MBB, B10, 'without_zero', 'p90'))}",
    "from July 1, 2025 to April 6, 2026", "Payments made July 1, 2025 to April 6, 2026.",
]
def norm(t): return re.sub(r"[ \t]+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {"0", "2026", "2025"}     # "$0" in the cohort names ("With $0"); report years
CAP_KNOWN = KNOWN | {x.rstrip(",") for ph in CAPTION_PHRASES for x in NUMBER.findall(ph)}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:-\d{1,2})?\b|"
                   r"\bfig-0[1-2]\b|\[MATT TO CONFIRM\]|\bBig 12\b")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b")
def stray_numbers(text, label, known, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in known: check(f"{label}: number not traced to the data: {fig}", False, True)
raw = (ROOT / "draft.md").read_text(); draft = norm(raw)
for ph in DRAFT_PHRASES: check(f"draft says: {ph.strip()[:70]}", norm(ph) in draft, True)
pub_part = raw.split("## Not for publication")[0]
body = pub_part.split("## About this piece")[0]
stray_numbers(pub_part, "draft", KNOWN)
check("draft has no em dashes", raw.count("—"), 0, 0)
check("draft has no ordinals", ORDINAL.findall(raw), [])
head = raw.split("\n---\n")[0].strip().splitlines()
check("H1 first", head[0].startswith("# "), True)
DEK = head[-1].strip("*"); print(f"dek: {len(DEK)} characters")
check("dek under 150 characters", len(DEK) < 150, True)
check("house layout: About, Sources, Not for publication in order",
      [h for h in re.findall(r"^## (.+)$", raw, re.M) if h in ("About this piece", "Sources", "Not for publication")], ["About this piece", "Sources", "Not for publication"])
check("prediction tag " + ("removed (confirmed)" if PREDICTION_CONFIRMED else "kept until Matt confirms"),
      pub_part.count("[MATT TO CONFIRM]"), 0 if PREDICTION_CONFIRMED else 1, 0)
check("cover line appears once in the published part", pub_part.count(COVER), 1, 0)
check("body links the Illinois piece once", body.count(f"]({ILL})"), 1, 0)
check("basketball window stated in the body", "July 1, 2025 to April 6, 2026" in body, True)
check("football window stated in the body", "made or scheduled in calendar 2026" in body, True)
check("no totals implied: no 'total', 'combined' or 'in all' in the body", re.search(r"\b(total|totals|combined|in all|altogether|spent \$)\b", body.replace("not totals", "").replace("No totals, and no schools", "")) is None, True)
check("no dollar figure carries 'million' except the cap", set(re.findall(r"\$[\d.,]+ (?:million|billion)", body)), {f"${CAP} million"})
check("no football-basketball sum or dollar comparison beyond the stated ratio", re.search(r"(more|less) than (the )?(basketball|football)", body) is None, True)
check("judgment is labeled as a read", "My read is" in body, True)
check("no 'last season' claim for basketball", "last season" not in pub_part, True)
src = raw.split("## Sources")[1].split("\n---\n")[0]
items = [l for l in src.splitlines() if l.strip()]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
check("Sources: every item but the repo line has a date", all(re.search(r", (accessed )?\w+ \d{1,2}, \d{4}$", l) for l in items if "GitHub" not in l), True)
links = re.findall(r"\]\((https?://[^)]+)\)", src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
known_urls = {r["url"] for r in c.values()}
for u in links:
    if "github.com/mgag70-prog" not in u: check(f"source link is in the data files: {u[:70]}", u in known_urls, True)
for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part.split("## Sources")[0]):
    check(f"body link is listed in Sources: {u[:60]}", u in links, True)
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body.split("\n---\n", 1)[1])))
print(f"draft body: {WORDS} words"); check("body 800 to 1,100 words", 800 <= WORDS <= 1100, True)

print("\n-- source titles and quotes against the fetched pages in raw/ --")
RAW_PAGES = {"school-revenue-share-compensation-report": "csc-revshare-live", "compensation-reports/": "csc-index-live",
             "ministryofsport.com": "ministry", "no-big-ten-school": "lw-illinois"}
def page_titles(page):
    t = page.read_text(errors="ignore")
    found = re.findall(r"<title[^>]*>([^<]*)</title>|og:title\" content=\"([^\"]*)\"|<h1[^>]*>(?:<[^>]+>)*([^<]+)", t)
    return {html.unescape(x).strip() for g in found for x in g if x.strip()}
for line in items:
    mt = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", line)
    key = next((k for k in RAW_PAGES if k in mt[2]), None)
    if not key: continue
    page = ROOT / "raw" / f"{RAW_PAGES[key]}.html"
    if not page.exists(): print(f"skip (no raw/{page.name}): {mt[1][:50]}"); continue
    titles = {norm(x) for x in page_titles(page)}
    check(f"title matches live page: {mt[1][:55]}", any(norm(mt[1]) == x or x.startswith(norm(mt[1]) + " -") for x in titles), True)
QUOTES = {"csc-revshare-live": ["For Men's and Women's Basketball, this report includes payments made between 7/1/25 - 4/6/26",
                                "For Football, this report includes payments made or scheduled between 1/1/26 - 12/31/26",
                                "100 student-athletes for the 90th and 10th percentiles, 40 for the 75th and 25th percentiles, and 10 for the 50th percentile",
                                "College Athlete Payment System (CAPS)"],
          "csc-index-live": ["CAPS treats virtually all contingent \"performance incentive\" promises in revenue-sharing contracts as scheduled payments",
                             "such as scholarships, cost-of-attendance stipends, or Alston payments",
                             "The 50th percentile is the median", "The data may be updated as additional information is received"],
          "ministry": ["cap of USD20.5 million", "per school for the 2025-26 academic year"],
          "lw-illinois": ["the University of Illinois denied my records request for what it paid athletes by sport"]}
for name, quotes in QUOTES.items():
    page = ROOT / "raw" / f"{name}.html"
    if not page.exists(): print(f"skip (no raw/{name}.html)"); continue
    text = re.sub(r"\s+", " ", norm(html.unescape(re.sub(r"<[^>]+>", " ", page.read_text(errors="ignore")))).replace("–", "-"))
    for q in quotes: check(f"raw/{name} says: {q[:55]}", norm(q) in text, True)

print("\n-- captions --")
captxt = (ROOT / "figures" / "captions.md").read_text()
for ph in CAPTION_PHRASES: check(f"captions say: {ph[:60]}", norm(ph) in norm(captxt), True)
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", CAP_KNOWN, least=8)
check("captions have no em dashes", captxt.count("—"), 0, 0)
check("captions have no ordinals", ORDINAL.findall(captxt), [])
for key in ("fig-01-share-paid", "fig-02-paid-range"):
    check(f"{key}: caption, slot and image path in draft", f"**{key}**" in captxt and f"captions.md, {key}]" in raw and f"figures/{key}.png" in raw, True)

print("\n-- thread --")
thread = (ROOT / "x-thread.md").read_text()
posts = re.split(r"^## Post \d+.*$", thread, flags=re.M)[1:]
check("thread has five posts", len(posts), 5, 0)
for i, tbody in enumerate(posts, 1):
    text = "\n".join(l for l in tbody.strip().splitlines() if not l.startswith("Attach:")).strip()
    length = len(re.sub(r"https?://\S+|\[URL\]", "x" * 23, text))
    check(f"post {i} length {length} under 280", length < 280, True)
    for fig in NUMBER.findall(re.sub(r"https?://\S+|\[URL\]", "", text)):
        if fig.strip() and norm(fig.rstrip(",")) not in draft:
            check(f"post {i} figure verbatim in draft: {fig}", False, True)
check("thread ends with the cover line and the piece link", posts[-1].strip().endswith(f"{COVER}\nhttps://ledgerandwhistle.substack.com/p/more-than-half-the-secs-mens-basketball"), True)
check("thread states both windows", "made or scheduled in calendar 2026" in thread and "through April 6" in thread, True)
check("thread has no em dashes", thread.count("—"), 0, 0)
check("thread has no ordinals", ORDINAL.findall(thread), [])
check("thread has no hashtags", re.search(r"(^|\s)#\w", "\n".join(posts)) is None, True)

paste = ROOT / "paste-into-substack.html"
if paste.exists():
    print("\n-- paste page --")
    page = paste.read_text()
    check("paste: stops above Not for publication", "Not for publication" not in page and "Alternate titles" not in page, True)
    check("paste: every draft link live", all(f'href="{u}"' in page for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part)), True)
    check("paste: no em dashes", page.count("—"), 0, 0)
    check("paste: two figure slots", page.count("[Insert image: figures/fig-0"), 2, 0)
    check("paste: cover line present", html.escape(COVER, quote=False) in page, True)
if fails: print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
