#!/usr/bin/env python3
"""pca-mvp-award-2026: what Pete Crow-Armstrong's MVP pays, and who pays it. Checks the data, then asserts every
number and key phrase in draft.md, figures/captions.md and x-thread.md the way lockout-countdown-2026/week-02 does.
Run from anywhere; exits 1 on any failure. Source-title and quote checks read raw/ (local only) and are skipped,
with a note, when a page isn't there."""
import csv, html, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PREDICTION_CONFIRMED = True   # flip to True when Matt confirms "What I expect" and the tag comes out of draft.md
fails = []
def check(name, got, want, tol=0.005):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) else got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (want {want})")
    if not ok: fails.append(name)
c = {r["key"]: r for r in csv.DictReader(open(ROOT / "data" / "context.csv"))}
V = lambda k: float(c[k]["value"])
POOL, SAL, EST, SK = V("pool_total"), V("pca_2026_salary"), V("pca_pool_estimate"), V("skenes_record")
AWARD, MIN, BONUS, S27 = V("mvp_award_bonus"), V("league_min_2026"), V("signing_bonus"), V("salary_2027")
OFFER, ASK, AW25, PER = V("pool_mlb_offer"), V("pool_union_ask"), V("awards_2025_total"), V("pool_per_team")
CLUBS = 30

print("-- data --")
check("pool estimate / 2026 salary (x)", round(EST / SAL, 1), 4.0, 0.0)
check("MVP bonus / 2026 salary (x)", round(AWARD / SAL, 1), 2.8, 0.0)
check("WAR share part of estimate $M", round(EST - AWARD, 2), 1.06, 0.0)
check("WAR share is 'a bit over $1 million' (NSB: more than $1M)", 1.0 < EST - AWARD < 1.1, True)
check("estimate beats Skenes by $M", round(EST - SK, 2), 0.12, 0.0)
check("PCA estimate share of $50M pool %", round(100 * EST / POOL, 1), 7.1, 0.0)
check("Cubs' 1/30 share of PCA's payout $K", round(1000 * EST / CLUBS), 119, 0)
check("30 clubs x roughly $1.67M is the $50M pool", round(CLUBS * PER), POOL, 0.5)
check("2026 pay: salary + signing bonus + pool estimate $M", round(SAL + BONUS + EST, 2), 9.45, 0.0)
check("2027 salary vs 2026 salary (x)", round(S27 / SAL, 1), 11.2, 0.0)
check("2026 salary over league minimum $K", round(1000 * (SAL - MIN)), 114, 0)
check("MLB pool offer vs current %", round(100 * (OFFER / POOL - 1)), 30, 0)
check("union pool ask vs current (x)", round(ASK / POOL, 1), 3.6, 0.0)
check("MVP bonus share of $50M pool %", round(100 * AWARD / POOL, 1), 5.0, 0.0)
check("escalator max total $M", V("escalator_max_2031") + V("escalator_max_2032"), 18.0, 0.0)
check("2025 award money share of pool %", round(100 * AW25 / POOL, 1), 25.5, 0.0)
check("pool estimate vs his 2025 pool payout (x)", round(EST / V("pca_pool_2025"), 1), 3.0, 0.0)
MID = (OFFER + ASK) / 2
check("midpoint of the two pool offers $M", MID, 122.5, 0.0)
check("MVP won (context.csv filled)", c["mvp_result"]["value"].startswith("Pete Crow-Armstrong, NL MVP, unanimous"), True)
check("first-place votes", int(V("mvp_first_place")), 30, 0)
check("contract total $M", V("contract_total"), 115.0, 0)

print("\n-- draft --")
m = lambda v: f"${v:,.0f} million" if v == int(v) else f"${v:,.2f} million".replace(".50 million", ".5 million")
d0 = lambda v: f"${round(v * 1e6):,}"
COVER = f"{d0(SAL)}. Most Valuable."
LATE_SEPT, SEPT14 = c["prior_mvp_piece"]["url"], c["prior_extension_piece"]["url"]
WEEK2 = "https://ledgerandwhistle.substack.com/p/20-days-left-and-the-mlb-free-agent"
CUBS_FA = dict(re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+) \((\d+)\)", c["cubs_fa_in_top50"]["value"]))
DRAFT_PHRASES = [
    f"# Pete Crow-Armstrong was paid {d0(SAL)} to win the MVP. The bonus comes from a pool both sides are fighting over.",
    f"The MVP adds {m(AWARD)} from baseball's pre-arbitration pool. MLB offered to grow the pool to {m(OFFER)}; the union wants {m(ASK)}.",
    f"won the National League MVP unanimously Thursday night with all {int(V('mvp_first_place'))} first-place votes, Jesse Rogers reported for ESPN",
    "Shohei Ohtani finished second and Brice Turang third",
    f"Crow-Armstrong hit {c['pca_line']['value'].split(',')[0]} with 45 home runs and 41 stolen bases",
    "he's the Cubs' first MVP since Kris Bryant in 2016",
    'ESPN called it "the first season in which both MVP winners and both Cy Young winners were unanimous."',
    f"[in September]({LATE_SEPT})",
    f"He played 2026 for {d0(SAL)}, which is {d0(SAL - MIN)} above the {d0(MIN)} league minimum.",
    f"The six-year, {m(V('contract_total'))} extension he signed in March doesn't start until 2027",
    f"It triggers {m(AWARD)} from the pre-arbitration bonus pool, the {m(POOL)} fund the 2022 labor deal created",
    f"Every club pays in roughly {m(PER)}, and players who've signed early extensions still collect, MLB Trade Rumors reported",
    f"That {m(AWARD)} alone is {AWARD / SAL:.1f} times his salary.",
    f"his {V('pca_jwar')} jWAR is {V('pca_jwar_share')}% of that group's total",
    f"Matthew Trueblood of North Side Baseball ran the numbers on November 5 and got around {m(EST)}: the MVP's {m(AWARD)} plus a bit over $1 million for WAR",
    "so treat that as North Side Baseball's estimate until it does",
    f"the payout is {EST / SAL:.1f} times his salary and {100 * EST / POOL:.1f}% of the whole pool, about {EST / V('pca_pool_2025'):.1f} times the {d0(V('pca_pool_2025'))} he drew from it in 2025, and about ${round(EST - SK, 2) * 1e6:,.0f} more than Paul Skenes's record {d0(SK)} last year",
    f"All {CLUBS} clubs do, in roughly equal shares",
    f"the Cubs' part of his payout is about one-thirtieth, roughly ${round(1000 * EST / CLUBS)},000, and the other {CLUBS - 1} clubs cover the rest",
    f"Add the pool money to his salary and the {m(BONUS)} signing bonus, and his 2026 pay comes to about {m(round(SAL + BONUS + EST, 2))}, not counting a small playoff share",
    f"Next year his salary alone is {m(S27)}, {S27 / SAL:.1f} times this year's.",
    f"\n{COVER}\n",
    f"MLB's November 3 offer raised it to {m(OFFER)}, {round(100 * (OFFER / POOL - 1))}% more than now, Jeff Passan reported for ESPN; the union's counter is {m(ASK)}, {ASK / POOL:.1f} times the current pool",
    f"In July, the AP described the union's version as {m(ASK)} next year with $15 million annual increases",
    f"[Week 2 of the lockout countdown]({WEEK2})",
    f"Clubs paid {m(AW25)} in award bonuses in 2025, {100 * AW25 / POOL:.1f}% of the {m(POOL)}, and Trueblood expects a record number of award bonuses this year",
    f"The MVP bonus by itself is {100 * AWARD / POOL:.1f}% of the pool.",
    "Neither side's proposal, as reported, says what an MVP would collect from a bigger pool, and I'm not going to guess",
    "One union proposal cuts the other way for a player in his spot. The AP reported in July that the union wants players signed to multiyear contracts made ineligible starting next year. As I read that",
    "This year's award counts for none of his contract escalators. Those begin with 2027 voting",
    f"each MVP from 2027 through 2030 adds {m(V('escalator_mvp'))} to his 2031 base, each from 2027 through 2031 adds {m(V('escalator_mvp'))} to his 2032 base",
    f"The most they can add is {m(V('escalator_max_2031'))} in 2031 and {m(V('escalator_max_2032'))} in 2032, which I put at ${V('escalator_pv'):.1f} million in present value at 6% in the September piece",
    "because he leaves the pre-arbitration bracket after this season",
    f"[The September 14 model]({SEPT14}) had 2027 as a ${V('model_2027_loss'):.1f} million loss for the Cubs against no extension",
    "I won't redo either one here",
    f"Seiya Suzuki (No. {CUBS_FA['Seiya Suzuki']}), Ian Happ (No. {CUBS_FA['Ian Happ']}) and Shota Imanaga (No. {CUBS_FA['Shota Imanaga']})",
    "Three of his teammates are free agents on MLB Trade Rumors' top 50",
    "the Cubs signed the extension, and the Pirates, Brewers and Cardinals help pay his MVP bonus",
    "What the Cubs commit around an MVP still on a pre-arbitration salary is the next piece.",
    f"The next agreement's pre-arbitration pool lands below ${MID:.1f} million, the midpoint of the two offers, closer to MLB's {m(OFFER)} than the union's {m(ASK)}",
    f"The {m(EST)} pool payout is North Side Baseball's estimate, published November 5",
    f"about ${EST - AWARD:.2f} million for WAR is arithmetic on that estimate",
    f"The Cubs' ${round(1000 * EST / CLUBS)},000 is arithmetic on equal club contributions of roughly {m(PER)}, as MLB Trade Rumors reports them",
    "*Disclosure: I held Cubs season tickets from 1998 to 2021.*",
]
def norm(t): return re.sub(r"[ \t]+", " ", t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'))
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?(?:\s?(?:million|billion|%))?")
KNOWN = set()
for ph in DRAFT_PHRASES: KNOWN |= {x.rstrip(",") for x in NUMBER.findall(ph)}
KNOWN |= {"2026", "2025", "100", "30", "2.5"}
DATED = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:-\d{1,2})?\b|"
                   r"\bfig-0[1-2]\b|\[MATT TO CONFIRM\]")
ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b")
def stray_numbers(text, label, least=20):
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "[]", text)       # linked titles and their targets are other people's words
    body = DATED.sub("", norm("\n".join(l for l in text.splitlines() if not l.startswith("![") and "captions.md, fig-" not in l and not l.startswith("**fig-"))))
    scanned = [f.rstrip(",") for f in NUMBER.findall(body)]
    check(f"{label}: numbers scanned", len(scanned) > least, True)
    for fig in scanned:
        if fig not in KNOWN: check(f"{label}: number not traced to the data: {fig}", False, True)
raw = (ROOT / "draft.md").read_text(); draft = norm(raw)
for ph in DRAFT_PHRASES: check(f"draft says: {ph.strip()[:70]}", norm(ph) in draft, True)
pub_part = raw.split("## Not for publication")[0]
body = pub_part.split("## About this piece")[0]
stray_numbers(pub_part, "draft")
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
check("no 'third time' unanimity claim", re.search(r"third time", pub_part, re.I) is None, True)
check("no unsourced unanimous-count claim (context.csv unanimous_count isn't in ESPN's text)", "25" not in re.findall(r"(?<![\d.])\d+(?![\d.])", body), True)
for p in re.split(r"\n\s*\n", body):
    if "$3.56 million" in p: check(f"$3.56 million paragraph labels the estimate: {p[:40]}", "estimate" in p, True)
check("the $119,000 is labeled arithmetic in About", "The Cubs' $119,000 is arithmetic" in pub_part, True)
check("earlier models not repeated", all(x not in pub_part for x in ("$28.6", "5.397", "$136.4", "$68.0", "$19.1", "$9.4 million")), True)
check("no amount guessed for an MVP under a bigger pool", re.search(r"(would|could) (get|collect|receive) (about |roughly )?\$", body) is None, True)
for name, url in (("late-Sept piece", LATE_SEPT), ("Sept 14 piece", SEPT14), ("week 2 countdown", WEEK2)):
    check(f"body links the {name} once", body.count(f"]({url})"), 1, 0)
src = raw.split("## Sources")[1].split("\n---\n")[0]
items = [l for l in src.splitlines() if l.strip()]
check("Sources: every line a bulleted link", all(l.startswith("- ") and "](http" in l for l in items), True)
check("Sources: every item but the repo line has a date", all(re.search(r", \w+ \d{1,2}, \d{4}$", l) for l in items if "GitHub" not in l), True)
links = re.findall(r"\]\((https?://[^)]+)\)", src)
check("Sources: no duplicate links", len(links), len(set(links)), 0)
known_urls = {r["url"] for r in c.values()}
house = ("ledgerandwhistle.substack.com", "github.com/mgag70-prog")
for u in links:
    if not any(h in u for h in house): check(f"source link is in the data files: {u[:70]}", u in known_urls, True)
for u in re.findall(r"\]\((https?://[^)]+)\)", pub_part.split("## Sources")[0]):
    check(f"body link is listed in Sources: {u[:60]}", u in links, True)
WORDS = len(re.findall(r"\b[\w'.$%,-]+\b", re.sub(r"!\[.*?\]\(.*?\)|\*\[Caption.*?\]\*", "", body.split("\n---\n", 1)[1])))
print(f"draft body: {WORDS} words"); check("body 900 to 1,200 words", 900 <= WORDS <= 1200, True)

print("\n-- source titles and quotes against the fetched pages in raw/ --")
RAW_PAGES = {"espn.com/mlb/story/_/id/50466186": "espn-mvp-nov12", "mlb.com/news/2026-bbwaa": "mlb-finalists",
             "northsidebaseball.com": "nsb", "espn.com/mlb/story/_/id/49440234": "espn-pool-jul24",
             "paul-skenes-tops": "skenes-mlbtr", "espn.com/mlb/story/_/id/50370860": "espn-offer-nov3",
             "top-50-free-agents": "mlbtr-top50", "signalhunterai": "sh-sept14",
             "if-pete-crow-armstrong": "lw-late-sept", "20-days-left": "lw-week02"}
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
QUOTES = {"espn-mvp-nov12": ["the first season in which both MVP winners and both Cy Young winners were unanimous",
                             "earned all 30 first-place votes", "first since Kris Bryant in 2016"],
          "nsb": ["a salary of $894,000", "10.2 jWAR", "3.2% of the total jWAR", "around $3.56 million",
                  "record number of awards bonuses", "can't earn bonuses via the same system again"],
          "espn-pool-jul24": ["$12.75 million last year", "$180 million next year followed by $15 million annual hikes",
                              "players signed to multiyear contracts become ineligible", "final figure of $1,206,207"],
          "espn-offer-nov3": ["a $65 million pre-arbitration bonus pool", "a $180 million pre-arbitration bonus pool", "$780,000"],
          "skenes-mlbtr": ["roughly $1.67MM", "even if they have signed an early-career extension", "$3,436,343"]}
for name, quotes in QUOTES.items():
    page = ROOT / "raw" / f"{name}.html"
    if not page.exists(): print(f"skip (no raw/{name}.html)"); continue
    text = norm(html.unescape(re.sub(r"<[^>]+>", "", page.read_text(errors="ignore"))))
    for q in quotes: check(f"raw/{name} says: {q[:55]}", norm(q) in text, True)

print("\n-- captions --")
captxt = (ROOT / "figures" / "captions.md").read_text()
for ph in (f"Pete Crow-Armstrong's 2026 pay, about {m(round(SAL + BONUS + EST, 2))}: his {d0(SAL)} salary, the {m(BONUS)} signing bonus",
           f"North Side Baseball's estimate of his pre-arbitration pool payout, {m(EST)}, split into {m(AWARD)} for the MVP and about ${EST - AWARD:.2f} million for WAR",
           "The pool figure is an estimate until MLB releases the final list", f"his 2027 salary, {m(S27)}, {S27 / SAL:.1f} times this year's",
           f"{m(POOL)} under the current agreement, {m(OFFER)} in MLB's November 3 offer, {round(100 * (OFFER / POOL - 1))}% more, and {m(ASK)} in the union's counter, {ASK / POOL:.1f} times the current pool",
           f"the {m(AW25)} clubs paid in award bonuses in 2025, {100 * AW25 / POOL:.1f}% of the pool"):
    check(f"captions say: {ph[:60]}", norm(ph) in norm(captxt), True)
stray_numbers("\n".join(l for l in captxt.splitlines() if l and not l.startswith("**") and not l.startswith("#")), "captions", least=8)
check("captions have no em dashes", captxt.count("—"), 0, 0)
check("captions have no ordinals", ORDINAL.findall(captxt), [])
for key in ("fig-01-pay-stack", "fig-02-pool"):
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
    if "$3.56 million" in text: check(f"post {i} labels the $3.56 million an estimate", "estimate" in text, True)
PUBLISHED = "https://ledgerandwhistle.substack.com/p/pete-crow-armstrong-was-paid-894000"
check("thread ends with the cover line and the published link", posts[-1].strip().endswith(f"{COVER}\n{PUBLISHED}"), True)
check("thread has no [URL] placeholder left", "[URL]" not in thread, True)
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
