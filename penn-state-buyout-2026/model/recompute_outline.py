"""
Regenerate the offset table and every calculated figure in sections 3 and 5 of
penn-state-buyout-2026/outline.md from the data files, and compare each one with the
figure the outline carries.

Inputs:
  penn-state-buyout-2026/data/coach-contracts.csv         one row per contract year
  penn-state-buyout-2026/data/settlements-and-buyouts.csv settlement, buyouts, reported figures
  cfb-roster-budgets-2026/data/cfb-roster-budgets-2026.csv Penn State's roster budget range

The outline computes the offset year by year: Penn State owes its guaranteed pay for the
year minus Virginia Tech's guaranteed pay for the year, floored at zero. The draft carries
that as the second of two readings of the clause. The first reading sets one offset against
the whole remaining term. The TWO READINGS block generates both, with the 2025 stub, for
section 3 of draft.md; those figures are not in the outline, so nothing checks them here.

Run from the repo root:  python penn-state-buyout-2026/model/recompute_outline.py
"""
import csv
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
ROSTER_CSV = os.path.normpath(os.path.join(
    HERE, "..", "..", "cfb-roster-budgets-2026", "data", "cfb-roster-budgets-2026.csv"))

FIRED = date(2025, 10, 12)   # Fox Sports, October 12, 2025
HIRED = date(2025, 11, 17)   # Front Office Sports, November 17, 2025
mismatches = []
checked = 0


def check_text(label: str, outline: str, shown: str, raw: str = "") -> None:
    global checked
    checked += 1
    ok = shown == outline
    if not ok:
        mismatches.append((label, outline, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<52} outline {outline:>8}  computed {shown:>8}{raw}")


def check(label: str, outline: str, computed: float, fmt: str) -> None:
    check_text(label, outline, fmt.format(computed), f"  (raw {computed:.6f})")


def num(s: str) -> float | None:
    return float(s) if s != "" else None


def money(x: float) -> str:
    """$6.0M, $12.75M, $0: one decimal unless the figure needs two."""
    if x == 0:
        return "$0"
    return f"${x:.2f}M" if round(x * 100) % 10 else f"${x:.1f}M"


with open(os.path.join(DATA, "coach-contracts.csv"), newline="") as f:
    contracts = list(csv.DictReader(f))
with open(os.path.join(DATA, "settlements-and-buyouts.csv"), newline="") as f:
    settlements = {r["item"]: float(r["amount_millions"]) for r in csv.DictReader(f)}
with open(ROSTER_CSV, newline="") as f:
    roster = next(r for r in csv.DictReader(f) if r["school"] == "Penn State")

# Every row must carry a source URL and an as-of date, and components must sum to guaranteed.
for r in contracts:
    assert r["source_url"].startswith("https://") and r["as_of_date"], f"unsourced row: {r}"
    parts = [num(r[c]) for c in ("base_salary_millions", "supplemental_millions",
                                 "insurance_loan_millions")]
    if parts[0] is not None:
        assert abs(sum(p or 0 for p in parts) - float(r["guaranteed_millions"])) < 1e-9, \
            f"components do not sum to guaranteed: {r}"


def schedule(coach: str, school: str, period_type: str = "full_year") -> dict[int, float]:
    return {int(r["contract_year"]): float(r["guaranteed_millions"]) for r in contracts
            if r["coach"] == coach and r["school"] == school and r["period_type"] == period_type}


psu = schedule("James Franklin", "Penn State")
vt = schedule("James Franklin", "Virginia Tech")
campbell = schedule("Matt Campbell", "Penn State")
campbell_retention = {int(r["contract_year"]): float(r["retention_bonus_millions"])
                      for r in contracts if r["coach"] == "Matt Campbell"}
vt_stub = next(r for r in contracts if r["school"] == "Virginia Tech"
               and r["period_type"] == "partial_year")

assert sorted(psu) == list(range(2022, 2032)), "Franklin/Penn State rows are not 2022-2031"
assert sorted(vt) == list(range(2026, 2031)), "Franklin/Virginia Tech rows are not 2026-2030"
assert sorted(campbell) == list(range(2026, 2034)), "Campbell rows are not 2026-2033"

BUYOUT = settlements["franklin_buyout_at_firing"]
SETTLEMENT = settlements["franklin_settlement"]
ISU_BUYOUT = settlements["campbell_iowa_state_buyout"]
VT_REPORTED_TOTAL = settlements["franklin_virginia_tech_contract_total"]

print(f"Read {len(contracts)} contract rows, {len(settlements)} settlement rows, "
      f"Penn State roster ${roster['budget_low_millions']}M to ${roster['budget_high_millions']}M")

# ---------------- Section 3: the offset table ----------------
print("\nSECTION 3: offset table, year by year")
OUTLINE_TABLE = {  # year: (Virginia Tech, Penn State owes, Franklin's total)
    2026: ("$6.0M", "$2.0M", "$8.0M"),
    2027: ("$5.0M", "$3.0M", "$8.0M"),
    2028: ("$4.0M", "$4.0M", "$8.0M"),
    2029: ("$12.75M", "$0", "$12.75M"),
    2030: ("$13.25M", "$0", "$13.25M"),
}
table = {}
for y in sorted(vt):
    owed = max(0.0, psu[y] - vt[y])
    table[y] = (vt[y], owed, vt[y] + owed)
    for name, o, c in zip(("Virginia Tech", "Penn State owes", "Franklin's total"),
                          OUTLINE_TABLE[y], table[y]):
        check_text(f"{y} {name}", o, money(c))

print("\n  | Year | Virginia Tech | Penn State owes under the offset | Franklin's total |")
print("  |---|---|---|---|")
for y, (v, o, t) in table.items():
    print(f"  | {y} | {money(v)} | {money(o)} | {money(t)} |")

print("\nSECTION 3: figures around the table")
offset_total = sum(o for _, o, _ in table.values())
check("Offset total 2026-2030 ($M)", "9.0", offset_total, "{:.1f}")
check("Settlement in the settlements file ($M)", "9.0", SETTLEMENT, "{:.1f}")
check("Offset total minus settlement ($M)", "0.0", offset_total - SETTLEMENT, "{:.1f}")
flat_years = [y for y, (_, _, t) in table.items() if t == psu[y]]
check("Years where VT pay + offset = Penn State pay", "3", len(flat_years), "{:d}")
print(f"       those years: {flat_years}; Penn State guaranteed pay in each: "
      f"{sorted({money(psu[y]) for y in flat_years})}")
zero_years = [y for y, (_, o, _) in table.items() if o == 0]
print(f"       offset is zero in {zero_years}; Virginia Tech's low years are "
      f"{[y for y in vt if vt[y] < psu[y]]}")
vt_sum = sum(vt.values())
check("Virginia Tech yearly figures, summed 2026-2030 ($M)", "41.0", vt_sum, "{:.1f}")
check("Reported total minus yearly sum ($M)", "0.75", VT_REPORTED_TOTAL - vt_sum, "{:.2f}")
uncovered = [y for y in psu if y > max(vt)]
check("Penn State exposure in 2031, no offsetting job ($M)", "8.0",
      sum(psu[y] for y in uncovered), "{:.1f}")

# ---------------- Section 5: cost of the change against the roster ----------------
print("\nSECTION 5: cost of the coaching change")
check("Cash out: settlement + Iowa State buyout ($M)", "11.0", SETTLEMENT + ISU_BUYOUT, "{:.1f}")
check("Campbell 2026: guaranteed + retention ($M)", "9", campbell[2026] + campbell_retention[2026],
      "{:.0f}")
lo, hi = float(roster["budget_low_millions"]), float(roster["budget_high_millions"])
mid = float(roster["budget_mid_millions"])
check("Roster budget low ($M)", "29", lo, "{:.0f}")
check("Roster budget high ($M)", "32", hi, "{:.0f}")
print("  ratios to one year of roster budget (low end, midpoint, high end of the estimate):")
print(f"    reported buyout ${BUYOUT}M:  {BUYOUT / lo:.3f}  {BUYOUT / mid:.3f}  {BUYOUT / hi:.3f}")
print(f"    settlement ${SETTLEMENT}M:      {SETTLEMENT / lo:.3f}  {SETTLEMENT / mid:.3f}  "
      f"{SETTLEMENT / hi:.3f}")
claim_a = BUYOUT / hi > 1.5          # smallest ratio in the range still above 1.5
claim_b = SETTLEMENT / lo < 1 / 3    # largest ratio in the range still below a third
check_text("Buyout larger than 1.5 years of roster, whole range", "holds",
           "holds" if claim_a else "fails")
check_text("Settlement under a third of one year, whole range", "holds",
           "holds" if claim_b else "fails")

# ---------------- Extra: calculated figures outside sections 3 and 5 ----------------
print("\nEXTRA (sections 2 and 4, reported for completeness)")
check("Savings: reported buyout - settlement ($M)", "40.7", BUYOUT - SETTLEMENT, "{:.1f}")
check("Days from firing to Virginia Tech hire", "36", (HIRED - FIRED).days, "{:d}")
check("Campbell guaranteed, 2026-2033 ($M)", "70.5", sum(campbell.values()), "{:.1f}")
check("Campbell guaranteed + retention ($M)", "78.5",
      sum(campbell.values()) + sum(campbell_retention.values()), "{:.1f}")

# ---------------- Draft section 3: the 2025 stub and the two readings ----------------
print("\nTHE 2025 STUB (draft section 3; not in the outline)")
stub_start = date.fromisoformat(vt_stub["period_start"])
stub_end = date.fromisoformat(vt_stub["period_end"])
stub_days = (stub_end - stub_start).days + 1
stub_rate = float(vt_stub["guaranteed_millions"])
stub_by_days = stub_rate * stub_days / 365
stub_by_months = stub_rate * 1.5 / 12
print(f"  Virginia Tech pays the ${stub_rate}M rate pro rata, {stub_start} to {stub_end} "
      f"({stub_days} days)")
print(f"    by days:        ${stub_by_days:.3f}M -> contract total ${vt_sum + stub_by_days:.3f}M")
print(f"    by half-months: ${stub_by_months:.3f}M -> contract total ${vt_sum + stub_by_months:.3f}M "
      f"(reported: ${VT_REPORTED_TOTAL}M)")
days_left_2025 = (date(2025, 12, 31) - FIRED).days
psu_2025_rest = psu[2025] * days_left_2025 / 365
future = sum(psu[y] for y in psu if y >= 2026)
buyout_rebuilt = future + psu_2025_rest
print(f"  Penn State's guaranteed pay for the {days_left_2025} days left in 2025: "
      f"${psu_2025_rest:.3f}M")
print(f"  ${future:.1f}M for 2026-2031 plus that stub: ${buyout_rebuilt:.3f}M "
      f"(reported buyout: ${BUYOUT}M)")
retention = next(float(r["retention_bonus_millions"]) for r in contracts
                 if r["coach"] == "James Franklin" and r["school"] == "Penn State")
print(f"  Franklin's Penn State pay in a year he stayed through Dec. 31: ${psu[2025]:.1f}M guaranteed "
      f"+ ${retention:.1f}M retention = ${psu[2025] + retention:.1f}M")

print("\nTWO READINGS OF THE OFFSET CLAUSE (draft section 3; not in the outline)")
# Reading one: a single offset against everything Penn State owed for the rest of the term.
psu_thru_2030 = psu_2025_rest + sum(psu[y] for y in range(2026, 2031))
whole_thru_2030 = max(0.0, psu_thru_2030 - VT_REPORTED_TOTAL)
whole_total = buyout_rebuilt - VT_REPORTED_TOTAL
# Reading two: each period on its own, Penn State's rate minus Virginia Tech's, floored at zero.
gap_days = (stub_start - FIRED).days - 1
yby_unemployed = psu[2025] * gap_days / 365
yby_stub = (psu[2025] - stub_rate) * stub_days / 365
yby_2025 = yby_unemployed + yby_stub
yby_thru_2030 = yby_2025 + offset_total
print(f"  Penn State owed, firing through 2030:   ${psu_thru_2030:.3f}M")
print(f"  Virginia Tech contract, reported total: ${VT_REPORTED_TOTAL:.3f}M "
      f"(difference ${psu_thru_2030 - VT_REPORTED_TOTAL:.3f}M)")
print(f"  year by year, late 2025: {gap_days} days with no job ${yby_unemployed:.3f}M + {stub_days} days "
      f"at a ${psu[2025] - stub_rate:.1f}M-a-year gap ${yby_stub:.3f}M = ${yby_2025:.3f}M")
print()
print("  | | Whole-term offset | Year-by-year offset |")
print("  |---|---|---|")
print(f"  | Late 2025, after the firing | | ${yby_2025:.1f}M |")
print(f"  | 2026 through 2028 | | ${sum(table[y][1] for y in (2026, 2027, 2028)):.1f}M |")
print(f"  | 2029 and 2030 | | ${sum(table[y][1] for y in (2029, 2030)):.1f}M |")
print(f"  | Owed through 2030 | ${whole_thru_2030:.1f}M | ${yby_thru_2030:.1f}M |")
print(f"  | 2031, if he earns nothing that year | ${psu[2031]:.1f}M | ${psu[2031]:.1f}M |")
print(f"  | Total with nothing earned in 2031 | ${whole_total:.1f}M | ${yby_thru_2030 + psu[2031]:.1f}M |")
print()
print(f"  raw: whole-term ${whole_total:.3f}M; year-by-year ${yby_thru_2030:.3f}M through 2030, "
      f"${yby_thru_2030 + psu[2031]:.3f}M with all of 2031")
print(f"  settlement ${SETTLEMENT:.1f}M minus whole-term total: {SETTLEMENT - whole_total:+.3f} ($M)")
print(f"  settlement ${SETTLEMENT:.1f}M minus year-by-year through 2030: {SETTLEMENT - yby_thru_2030:+.3f} ($M)")
drop = BUYOUT - SETTLEMENT
print(f"  drop from the reported buyout that the clause alone produces: "
      f"whole-term ${BUYOUT - whole_total:.1f}M, year-by-year through 2030 ${BUYOUT - yby_thru_2030:.1f}M, "
      f"against the ${drop:.1f}M actual drop")
print(f"  Franklin's total, Virginia Tech + settlement: ${VT_REPORTED_TOTAL + SETTLEMENT:.2f}M; "
      f"reported buyout ${BUYOUT}M; difference {VT_REPORTED_TOTAL + SETTLEMENT - BUYOUT:+.2f} ($M)")

print("\n" + (f"ALL {checked} CALCULATED FIGURES MATCH THE OUTLINE" if not mismatches
              else f"{len(mismatches)} MISMATCH(ES) in {checked} checks:"))
for label, o, c in mismatches:
    print(f"  {label}: outline {o}, computed {c}")
print("\nOUTLINE STATEMENT THE DATA CONTRADICTS")
print(f"  Section 3 calls the ${VT_REPORTED_TOTAL - vt_sum:.2f}M gap between the yearly figures "
      f"and the ${VT_REPORTED_TOTAL}M total unexplained.")
print(f"  The 2025 stub accounts for it: ${stub_by_months:.2f}M at the ${stub_rate}M rate for "
      f"1.5 months.")
