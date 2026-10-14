"""
Recompute every figure in illinois-revenue-sharing-2026 from the raw report text and the data
files, and fail on any mismatch.

Inputs: data/mfrs-summary.csv (each row cites the raw text line it came from), data/context.csv,
raw/FY25_NCAA_report.txt, raw/FY24_NCAA_report.txt (pdftotext -layout of the posted PDFs),
raw/FOIA-26-2759-response.txt (pdftotext -layout of the denial letter), data/peers.csv and the
source texts in raw/peers/ that its quotes are checked against.

Run from the repo root:  python illinois-revenue-sharing-2026/model/recompute.py
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "..")
COLS = ("football", "mens_basketball", "womens_basketball", "other_sports", "non_program_specific", "total")
mismatches = []
checked = 0


def check(label, expected, computed, fmt):
    global checked
    checked += 1
    shown = fmt.format(computed)
    ok = shown == expected
    if not ok:
        mismatches.append((label, expected, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<58} expected {expected:>14}  computed {shown:>14}")


def read(path):
    with open(os.path.join(PIECE, path), encoding="utf-8") as f:
        return f.read()


def load(name):
    with open(os.path.join(PIECE, "data", name), newline="") as f:
        return list(csv.DictReader(f))


def dollars(line):
    """Every $-amount on a report line, in order, as signed integers."""
    return [int(s.replace("$", "").replace(",", "")) for s in re.findall(r"-?\$[\d,]+", line)]


summary = load("mfrs-summary.csv")
ctx = {r["item"]: r["value"] for r in load("context.csv")}
texts = {}
S = {}
print("MFRS SUMMARY ROWS AGAINST THE CITED RAW LINES")
for r in summary:
    path, n = r["source_file"], int(r["source_line"])
    lines = texts.setdefault(path, read(path).split("\n"))
    found = dollars(lines[n - 1])
    claimed = [int(r[c]) for c in COLS]
    check(f"FY{r['fiscal_year']} {r['item']} (line {n})", str(claimed), found, "{}")
    S[(int(r["fiscal_year"]), r["item"])] = dict(zip(COLS, claimed))

print("\nARITHMETIC INSIDE EACH YEAR")
for fy in (2025, 2024):
    rev, exp, net = S[(fy, "total_operating_revenues")], S[(fy, "total_operating_expenses")], S[(fy, "excess_revenues_over_expenses")]
    for c in COLS:
        check(f"FY{fy} {c}: revenue - expenses = excess", f"{net[c]:,d}", rev[c] - exp[c], "{:,d}")
    check(f"FY{fy} programs sum to total revenue", f"{rev['total']:,d}", sum(rev[c] for c in COLS[:-1]), "{:,d}")
    check(f"FY{fy} programs sum to total expenses", f"{exp['total']:,d}", sum(exp[c] for c in COLS[:-1]), "{:,d}")
rev25, rev24 = S[(2025, "total_operating_revenues")]["total"], S[(2024, "total_operating_revenues")]["total"]
exp25, exp24 = S[(2025, "total_operating_expenses")]["total"], S[(2024, "total_operating_expenses")]["total"]
net25, net24 = S[(2025, "excess_revenues_over_expenses")], S[(2024, "excess_revenues_over_expenses")]

print("\nYEAR OVER YEAR")
check("Revenue FY25 ($M)", "194.8", rev25 / 1e6, "{:.1f}")
check("Revenue FY24 ($M)", "174.1", rev24 / 1e6, "{:.1f}")
check("Revenue growth FY24 to FY25, %", "11.9", 100 * (rev25 / rev24 - 1), "{:.1f}")
check("Revenue growth, $M", "20.7", (rev25 - rev24) / 1e6, "{:.1f}")
check("Expenses FY25 ($M)", "189.9", exp25 / 1e6, "{:.1f}")
check("Expenses FY24 ($M)", "169.5", exp24 / 1e6, "{:.1f}")
check("Expense growth FY24 to FY25, %", "12.0", 100 * (exp25 / exp24 - 1), "{:.1f}")
check("Surplus FY25 ($M)", "4.9", net25["total"] / 1e6, "{:.1f}")
check("Surplus FY24 ($M)", "4.6", net24["total"] / 1e6, "{:.1f}")
check("Surplus FY25 as % of revenue", "2.5", 100 * net25["total"] / rev25, "{:.1f}")

print("\nFY25 BY PROGRAM ($M)")
for c, exp_s in zip(COLS, ("38.7", "16.7", "-4.9", "-25.4", "-20.2", "4.9")):
    check(f"FY25 excess, {c}", exp_s, net25[c] / 1e6, "{:.1f}")
check("Football + men's basketball surplus ($M)", "55.3", (net25["football"] + net25["mens_basketball"]) / 1e6, "{:.1f}")
check("Everything else, net ($M)", "-50.4", (net25["womens_basketball"] + net25["other_sports"] + net25["non_program_specific"]) / 1e6, "{:.1f}")
check("Football revenue FY25 ($M)", "87.9", S[(2025, "total_operating_revenues")]["football"] / 1e6, "{:.1f}")
check("Football revenue growth FY24 to FY25, %", "27.9", 100 * (S[(2025, "total_operating_revenues")]["football"] / S[(2024, "total_operating_revenues")]["football"] - 1), "{:.1f}")

print("\nCATEGORY 44, INSTITUTIONAL NIL REVENUE SHARE")
fy25, fy24 = read("raw/FY25_NCAA_report.txt"), read("raw/FY24_NCAA_report.txt")
cat44 = S[(2025, "cat44_institutional_nil_revenue_share")]
check("FY25 summary row, all six cells", "[0, 0, 0, 0, 0, 0]", [cat44[c] for c in COLS], "{}")
assert "Total of Categories 20-44." in fy25, "FY25 expenses no longer total categories 20-44"
assert "Total of Categories 20-41A." in fy24 and "Institutional NIL" not in fy24 and "Revenue Share" not in fy24, "FY24 form carries Category 44"
check("FY25 mentions of 'Institutional NIL' (pp. 16, 74, 94)", "6", fy25.count("Institutional NIL"), "{:d}")
check("FY24 mentions of 'Institutional NIL'", "0", fy24.count("Institutional NIL"), "{:d}")
# The by-sport table on page 74: header, 12 sport rows plus Others, Subtotal, two 'not related' lines, Total.
lines25 = fy25.split("\n")
start = next(i for i, l in enumerate(lines25) if "Expenses by Object of" in l and "Institutional NIL" in l)
block = lines25[start:start + 20]
sports = [l.strip() for l in block if l.strip() and not any(k in l for k in ("Expenses by Object", "Revenue Share", "Subtotal", "Expenses Not Related", "Specific Teams", "Total Expenses"))]
SPORTS = ["Baseball", "Basketball", "Football", "Golf", "Gymnastics", "Soccer", "Softball", "Swimming and Diving", "Tennis", "Track and Field, X-Country", "Volleyball", "Wrestling", "Others"]
check("FY25 by-sport table rows", str(SPORTS), sports, "{}")
assert all(not re.search(r"\d", s) for s in sports), "a sport row in the Category 44 table carries a figure"
subtotal = next(l for l in block if "Subtotal All Teams" in l)
total = next(l for l in block if "Total Expenses" in l)
check("FY25 by-sport subtotal (men, women, not allocated)", "['0', '0', '0']", re.findall(r"\d[\d,]*", subtotal), "{}")
check("FY25 by-sport total (men, women, not allocated)", "['0', '0', '0']", re.findall(r"\d[\d,]*", total), "{}")
pages25 = fy25.split("\f")
check("Page of the FY25 by-sport Category 44 table", "74", next(i for i, p in enumerate(pages25, 1) if "Expenses by Object of" in p and "Institutional NIL" in p), "{:d}")
check("Page of the FY25 summary Category 44 row", "94", next(i for i, p in enumerate(pages25, 1) if re.search(r"^44\s+Institutional NIL(\s+\$0){6}\s*$", p, re.M)), "{:d}")
check("FY25 report pages", "94", max(int(m) for m in re.findall(r"Page \d+ of (\d+)", fy25)), "{:d}")

print("\nTHE MONEY QUESTION (cap and estimates)")
cap = float(ctx["revenue_share_cap_2025_26"])
lo, hi = float(ctx["athletic_illinois_estimate_low"]), float(ctx["athletic_illinois_estimate_high"])
check("Revenue-sharing cap 2025-26 ($M)", "20.5", cap, "{:.1f}")
check("FY25 surplus as % of the cap", "23.9", 100 * net25["total"] / 1e6 / cap, "{:.1f}")
check("Cap minus FY25 surplus ($M)", "15.6", cap - net25["total"] / 1e6, "{:.1f}")
check("Cap as multiple of FY25 surplus", "4.2", cap / (net25["total"] / 1e6), "{:.1f}")
check("The Athletic estimate for Illinois, low ($M)", "19", lo, "{:.0f}")
check("The Athletic estimate for Illinois, high ($M)", "23", hi, "{:.0f}")
check("Cap as % of FY25 revenue", "10.5", 100 * cap / (rev25 / 1e6), "{:.1f}")
check("Cap as % of FY25 expenses", "10.8", 100 * cap / (exp25 / 1e6), "{:.1f}")

print("\nTHE LETTER (quotes checked against raw/FOIA-26-2759-response.txt)")
# A hyphenated word broken across lines ("revenue-\n sharing") is rejoined before whitespace is collapsed.
letter = re.sub(r"\s+", " ", re.sub(r"-\n\s*", "-", read("raw/FOIA-26-2759-response.txt")).replace("“", '"').replace("”", '"').replace("’", "'").replace("–", "-").replace("…", "..."))
QUOTES = (
    "Trade secrets and commercial or financial information obtained from a person or business where the trade secrets or commercial or financial information are furnished under a claim that they are proprietary, privileged or confidential, and that, or where, disclosure of the trade secrets or commercial or financial information would cause competitive harm to the person or business",
    "Given the institution-specific discretion in allocating revenue-sharing payments across sports and between student-athletes, the requested information is inextricably linked to the competitive strategies of the University.",
    "The release of these records would cause competitive harm by allowing other institutions to learn, replicate and/or exploit University of Illinois allocation strategies and priorities.",
    "Information exempt from disclosure under Section 40 of the Student-Athlete Endorsement Rights Act.",
    "Information written, produced, collected, assembled, or otherwise maintained by a postsecondary educational institution that includes, reveals, or otherwise relates to the terms of an existing or proposed student-athlete publicity rights agreement.",
    "a public body is not required to copy a public record that is published on the public body's website",
    "A search for 2026 NCAA Membership Financial Reporting System (MFRS) reports was conducted; no records could be located.",
    "2026 NCAA MFRS reports will be posted on this page when they become available.",
    "You have a right under the law to seek a review of this response by the Public Access Counselor (PAC) in the Office of the Attorney General.",
    "Points 1 and 2 of your request are denied",
    "Re: FOIA Request 26-2759",
    "October 12, 2026",
    "received in my office October 5, 2026",
)
for q in QUOTES:
    ok = q in letter
    checked += 1
    if not ok:
        mismatches.append(("letter quote", q[:60], "NOT FOUND"))
    print(f"  {'OK  ' if ok else 'DIFF'} letter says: {q[:88]}{'...' if len(q) > 88 else ''}")
assert "140/7(1)(g)" in letter and "140/7.5(sss)" in letter and "5 ILCS 140/8.5" in letter


print("\nPEERS (data/peers.csv; every quote checked against raw/peers/<quote_file>)")
peers = load("peers.csv")
def norm(t):
    return re.sub(r"\s+", " ", t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"'))
for r in peers:
    if not r["quote"]:
        continue
    text = norm(read(os.path.join("raw", "peers", r["quote_file"])))
    ok = norm(r["quote"]) in text
    checked += 1
    if not ok:
        mismatches.append((f"peer quote {r['school']} {r['item']}", r["quote"][:50], "NOT FOUND"))
    print(f"  {'OK  ' if ok else 'DIFF'} {r['school']:<15} {r['item']:<34} {r['quote'][:60]}")
P = {(r["school"], r["item"]): r["value"] for r in peers}
check("Ohio State FY25 revenue ($M)", "336.1", int(P[("Ohio State", "fy25_total_operating_revenues")]) / 1e6, "{:.1f}")
check("Indiana FY25 revenue ($M)", "183.4", int(P[("Indiana", "fy25_total_operating_revenues")]) / 1e6, "{:.1f}")
check("Illinois FY25 revenue ($M), same figure as mfrs-summary", "194.8", int(P[("Illinois", "fy25_total_operating_revenues")]) / 1e6, "{:.1f}")
assert int(P[("Illinois", "fy25_total_operating_revenues")]) == rev25
check("Ohio State revenue / Illinois revenue", "1.7", int(P[("Ohio State", "fy25_total_operating_revenues")]) / rev25, "{:.1f}")
check("Illinois revenue / Indiana revenue", "1.06", rev25 / int(P[("Indiana", "fy25_total_operating_revenues")]), "{:.2f}")
check("Ohio State payments + scholarships ($M)", "20.5", float(P[("Ohio State", "rev_share_2025_26_usd_m")]) + float(P[("Ohio State", "scholarships_2025_26_usd_m")]), "{:.1f}")
check("Michigan State FY27 deficit ($M)", "10.6", int(P[("Michigan State", "fy27_athletics_deficit_usd")]) / 1e6, "{:.1f}")
check("Michigan State FY26 internal loan ($M)", "12.1", int(P[("Michigan State", "internal_loan_fy26_usd")]) / 1e6, "{:.1f}")
check("Michigan FY26 projection as % of its budget", "87.8", 100 * float(P[("Michigan", "rev_share_fy26_projection_usd_m")]) / float(P[("Michigan", "rev_share_fy26_budget_usd_m")]), "{:.1f}")
assert P[("Ohio State", "fy25_cat44")] == P[("Indiana", "fy25_cat44")] == "0"
assert all(P[(s, "fy25_mfrs_public")] == "not found" for s in ("Michigan", "Michigan State", "Iowa"))
assert P[("Illinois", "trustees_rev_share_total")] == "not found"
schools = sorted({r["school"] for r in peers})
check("Schools in the comparison", "6", len(schools), "{:d}")
check("Schools whose FY25 NCAA report is public on their own site", "2", sum(P[(s, "fy25_mfrs_public")] == "yes" for s in schools), "{:d}")
check("Schools that have published revenue sharing in dollars by sport", "0", sum(P[(s, "by_sport_dollars")] not in ("none", "none found", "percent only", "percent range only") for s in schools), "{:d}")
check("Schools that gave a percentage for football", "3", sum(P[(s, "by_sport_dollars")] in ("percent only", "percent range only") for s in schools), "{:d}")

print("\n" + (f"ALL {checked} FIGURES MATCH" if not mismatches else f"{len(mismatches)} MISMATCH(ES) in {checked} checks:"))
for label, e, c in mismatches:
    print(f"  {label}: expected {e}, computed {c}")
if mismatches:
    raise SystemExit(1)
