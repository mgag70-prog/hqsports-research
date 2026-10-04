"""
Recompute every figure in wrigley-season-tickets-2026/outline.md from the two data files
and compare each one with the figure the outline carries.

Inputs:
  wrigley-season-tickets-2026/data/cubs-season-tickets.csv   one row per season, Matt's invoices
  wrigley-season-tickets-2026/data/cpi-u-annual.csv          BLS CPI-U annual averages

Real figures are in 2021 dollars: nominal x CPI(2021) / CPI(year). Growth rates are
compound annual rates between endpoints. Totals before 2015 are rounded by the owner, so
the script reports single-year changes only from 2016 on and shows how far the 2004-2015
rate moves if the 2004 total is off by $1,000 either way.

Run from the repo root:  python wrigley-season-tickets-2026/model/recompute_outline.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
BASE_YEAR = 2021
HOME_DATES = 81
mismatches = []
checked = 0


def check(label, outline, computed, fmt):
    global checked
    checked += 1
    shown = fmt.format(computed)
    ok = shown == outline
    if not ok:
        mismatches.append((label, outline, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<54} outline {outline:>12}  computed {shown:>12}"
          f"  (raw {computed:.6f})")


with open(os.path.join(DATA, "cubs-season-tickets.csv"), newline="") as f:
    rows = {int(r["year"]): r for r in csv.DictReader(f)}
with open(os.path.join(DATA, "cpi-u-annual.csv"), newline="") as f:
    cpi = {int(r["year"]): float(r["cpi_u_annual_avg"]) for r in csv.DictReader(f)}

years = sorted(rows)
assert years == list(range(1998, 2022)), "invoice rows are not 1998-2021"
assert all(y in cpi for y in years), "CPI is missing a season"
total = {y: float(rows[y]["season_total"]) for y in years}
seats = {y: int(rows[y]["seats"]) for y in years}
playoff = {y: float(rows[y]["playoff_total"]) for y in years if rows[y]["playoff_total"]}
exact = {y for y in years if rows[y]["precision"].startswith("exact")}
assert exact == set(range(2015, 2022)), f"exact rows are {sorted(exact)}"
assert all(seats[y] == 2 for y in range(1998, 2004)) and all(seats[y] == 4 for y in range(2004, 2022))


def real(y, amount=None):
    """An amount from year y in BASE_YEAR dollars."""
    return (total[y] if amount is None else amount) * cpi[BASE_YEAR] / cpi[y]


def cagr(a, b, n):
    return (b / a) ** (1 / n) - 1


print(f"Read {len(years)} seasons, CPI {min(cpi)}-{max(cpi)}, real figures in {BASE_YEAR} dollars")

# ---------------- Section 1: the seats and the numbers ----------------
print("\nSECTION 1: per-seat prices")
check("1998 total", "8,000", total[1998], "{:,.0f}")
check("1998 per seat", "4,000", total[1998] / seats[1998], "{:,.0f}")
check("2003 total", "10,000", total[2003], "{:,.0f}")
check("2003 per seat", "5,000", total[2003] / seats[2003], "{:,.0f}")
check("2004 total", "16,500", total[2004], "{:,.0f}")
check("2004 per seat", "4,125", total[2004] / seats[2004], "{:,.0f}")
check("2021 total", "38,751", total[2021], "{:,.0f}")
check("2021 per seat", "9,687.75", total[2021] / seats[2021], "{:,.2f}")
check("2021 per seat per home date", "119.60", total[2021] / seats[2021] / HOME_DATES, "{:.2f}")
check("2015 playoff tickets", "7,510", playoff[2015], "{:,.0f}")
check("2016 playoff tickets", "8,430", playoff[2016], "{:,.0f}")
assert sorted(playoff) == [2015, 2016], f"playoff purchases in {sorted(playoff)}"
print("       playoff tickets bought in 2015 and 2016 only")

# ---------------- Section 2: 2004 to 2015 ----------------
print("\nSECTION 2: 2004 to 2015, eleven years")
n1 = 2015 - 2004
check("2015 total (exact)", "23,398", total[2015], "{:,.0f}")
check("Nominal growth 2004-2015, % a year", "3.2", 100 * cagr(total[2004], total[2015], n1), "{:.1f}")
check("CPI 2004-2015, % a year", "2.1", 100 * cagr(cpi[2004], cpi[2015], n1), "{:.1f}")
check("2004 total in 2021 dollars", "23,669", real(2004), "{:,.0f}")
check("2015 total in 2021 dollars", "26,750", real(2015), "{:,.0f}")
check("Real growth 2004-2015, total %", "13.0", 100 * (real(2015) / real(2004) - 1), "{:.1f}")
check("Real growth 2004-2015, % a year", "1.1", 100 * cagr(real(2004), real(2015), n1), "{:.1f}")
print("       rounded-year moves, not for publication: "
      + ", ".join(f"{y} {100 * (total[y] / total[y - 1] - 1):+.1f}%" for y in range(2005, 2016)))

print("\n  sensitivity: the 2004 total is rounded; the rate if it were off by $1,000")
for delta in (-1000, 0, 1000):
    base = total[2004] + delta
    print(f"    2004 = ${base:,.0f}: nominal {100 * cagr(base, total[2015], n1):.1f}% a year, "
          f"real {100 * cagr(real(2004, base), real(2015), n1):.1f}% a year, "
          f"real total {100 * (real(2015) / real(2004, base) - 1):.1f}%")

# ---------------- Section 3: 2015 to 2021 ----------------
print("\nSECTION 3: 2015 to 2021, six years")
n2 = 2021 - 2015
check("Real growth 2015-2021, total %", "44.9", 100 * (real(2021) / real(2015) - 1), "{:.1f}")
check("Real growth 2015-2021, % a year", "6.4", 100 * cagr(real(2015), real(2021), n2), "{:.1f}")
check("CPI 2015-2021, % a year", "2.3", 100 * cagr(cpi[2015], cpi[2021], n2), "{:.1f}")
OUTLINE_YEARLY = {2016: "15.1", 2017: "8.1", 2018: "8.4", 2019: "4.9", 2020: "8.2", 2021: "8.3"}
for y, o in OUTLINE_YEARLY.items():
    check(f"{y} nominal change, %", o, 100 * (total[y] / total[y - 1] - 1), "{:.1f}")
check("2016 total (exact)", "26,924.80", total[2016], "{:,.2f}")
print("       year-by-year real change, 2021 dollars: "
      + ", ".join(f"{y} {100 * (real(y) / real(y - 1) - 1):+.1f}%" for y in range(2016, 2022)))
print("       year-by-year CPI change: "
      + ", ".join(f"{y} {100 * (cpi[y] / cpi[y - 1] - 1):+.1f}%" for y in range(2016, 2022)))
print(f"       nominal 2015-2021: {100 * cagr(total[2015], total[2021], n2):.1f}% a year; "
      f"the two real rates differ by {100 * (cagr(real(2015), real(2021), n2) - cagr(real(2004), real(2015), n1)):.1f} points")

# ---------------- Section 4: 2020 ----------------
print("\nSECTION 4: 2020")
check("2020 billed", "35,790", total[2020], "{:,.0f}")
check("2020 change, %", "8.2", 100 * (total[2020] / total[2019] - 1), "{:.1f}")

# ---------------- Section 5: the total ----------------
print("\nSECTION 5: 1998 to 2021")
check("Season tickets paid, before refunds", "491,330.80", sum(total.values()), "{:,.2f}")
check("Playoff tickets paid", "15,940", sum(playoff.values()), "{:,.0f}")
print(f"       of which the 2020 season later refunded: ${total[2020]:,.0f}; "
      f"net of that refund ${sum(total.values()) - total[2020]:,.2f}")

# ---------------- Figures: the series the charts will draw ----------------
print("\nSERIES for the figures")
print("  year  seats  nominal      per seat   real(2021$)   nominal chg   CPI chg")
for y in years:
    chg = f"{100 * (total[y] / total[y - 1] - 1):+6.1f}%" if y > 1998 and seats[y] == seats[y - 1] else "      "
    cchg = f"{100 * (cpi[y] / cpi[y - 1] - 1):+5.1f}%" if y > 1998 else "     "
    flag = "" if y in exact else "  rounded"
    print(f"  {y}  {seats[y]}      {total[y]:>10,.2f}  {total[y] / seats[y]:>9,.2f}  {real(y):>11,.0f}   {chg}      {cchg}{flag}")

print("\n" + (f"ALL {checked} FIGURES MATCH THE OUTLINE" if not mismatches
              else f"{len(mismatches)} MISMATCH(ES) in {checked} checks:"))
for label, o, c in mismatches:
    print(f"  {label}: outline {o}, computed {c}")
