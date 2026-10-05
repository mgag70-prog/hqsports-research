"""
Recompute every growth rate, total change, MLB/NHL ratio and index value in
mlb-cap-valuations-2026/outline.md from data/forbes-avg-team-value.csv, and compare each
one with the figure the outline carries.

Growth rates are compound annual rates between Forbes list years. The index for fig-01 is
each league's average value divided by its 2004 list value, times 100. Ratios divide the
MLB average by the NHL average for the same list year.

Run from the repo root:  python mlb-cap-valuations-2026/model/recompute_outline.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "forbes-avg-team-value.csv")
mismatches = []
checked = 0


def check(label, outline, computed, fmt):
    global checked
    checked += 1
    shown = fmt.format(computed)
    ok = shown == outline
    if not ok:
        mismatches.append((label, outline, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<56} outline {outline:>9}  computed {shown:>9}  (raw {computed:.6f})")


def cagr(a, b, n):
    return (b / a) ** (1 / n) - 1


with open(DATA, newline="") as f:
    rows = list(csv.DictReader(f))
value = {(r["league"], int(r["list_year"])): float(r["avg_value_musd"]) for r in rows}
multiple = {(r["league"], int(r["list_year"])): float(r["multiple_stated"]) for r in rows if r["multiple_stated"]}
revenue = {(r["league"], int(r["list_year"])): float(r["avg_revenue_musd"]) for r in rows if r["avg_revenue_musd"]}
nhl = {y: v for (lg, y), v in value.items() if lg == "NHL"}
mlb = {y: v for (lg, y), v in value.items() if lg == "MLB"}
for r in rows:
    assert r["source"].startswith("https://"), f"row without a source URL: {r}"
assert sorted(nhl) == [1999, 2000, 2004] + list(range(2006, 2026)), sorted(nhl)   # no 2005 list: no 2004-05 season
assert sorted(mlb) == [1999, 2000, 2002] + list(range(2004, 2027)), sorted(mlb)
print(f"Read {len(rows)} rows: NHL lists {min(nhl)}-{max(nhl)}, MLB lists {min(mlb)}-{max(mlb)}")

# ---------------- Section 1: the gap today ----------------
print("\nSECTION 1: the gap the owners point at")
check("MLB average, 2026 list ($B)", "2.9", mlb[2026] / 1000, "{:.1f}")
check("MLB multiple, 2026 list", "7.0", multiple[("MLB", 2026)], "{:.1f}")
check("NHL multiple, 2025 list (Forbes rounds to 9x)", "8.9", multiple[("NHL", 2025)], "{:.1f}")

# ---------------- Section 2: before and after the 2005 cap ----------------
print("\nSECTION 2: the NHL in 2005")
check("NHL 1999 list ($M)", "135", nhl[1999], "{:.0f}")
check("NHL 2004 list ($M)", "163", nhl[2004], "{:.0f}")
check("NHL growth 1999-2004, % a year", "3.84", 100 * cagr(nhl[1999], nhl[2004], 5), "{:.2f}")
check("MLB 1999 list ($M)", "220.2", mlb[1999], "{:.1f}")
check("MLB 2004 list ($M)", "295", mlb[2004], "{:.0f}")
check("MLB growth 1999-2004, % a year", "6.02", 100 * cagr(mlb[1999], mlb[2004], 5), "{:.2f}")
check("NHL 2011 list ($M)", "240", nhl[2011], "{:.0f}")
check("NHL change 2004-2011, %", "47.2", 100 * (nhl[2011] / nhl[2004] - 1), "{:.1f}")
check("NHL growth 2004-2011, % a year", "5.68", 100 * cagr(nhl[2004], nhl[2011], 7), "{:.2f}")
check("MLB 2011 list ($M)", "523", mlb[2011], "{:.0f}")
check("MLB change 2004-2011, %", "77.3", 100 * (mlb[2011] / mlb[2004] - 1), "{:.1f}")
check("MLB growth 2004-2011, % a year", "8.52", 100 * cagr(mlb[2004], mlb[2011], 7), "{:.2f}")
check("MLB/NHL ratio, 2004 list", "1.81", mlb[2004] / nhl[2004], "{:.2f}")
check("MLB/NHL ratio, 2011 list", "2.18", mlb[2011] / nhl[2011], "{:.2f}")
check("MLB multiple, 2011 list", "2.5", multiple[("MLB", 2011)], "{:.1f}")
check("NHL multiple, 2012 list", "2.5", multiple[("NHL", 2012)], "{:.1f}")
print(f"       gap in annual growth after the cap: {100 * (cagr(mlb[2004], mlb[2011], 7) - cagr(nhl[2004], nhl[2011], 7)):.2f} points; "
      f"before it: {100 * (cagr(mlb[1999], mlb[2004], 5) - cagr(nhl[1999], nhl[2004], 5)):.2f} points")

# ---------------- Section 3: the catch-up ----------------
print("\nSECTION 3: when hockey caught up")
check("NHL 2012 list ($M)", "282", nhl[2012], "{:.0f}")
check("NHL 2025 list ($B)", "2.2", nhl[2025] / 1000, "{:.1f}")
check("NHL growth 2012-2025, % a year", "17.12", 100 * cagr(nhl[2012], nhl[2025], 13), "{:.2f}")
check("MLB 2012 list ($M)", "605", mlb[2012], "{:.0f}")
check("MLB 2025 list ($B)", "2.6", mlb[2025] / 1000, "{:.1f}")
check("MLB growth 2012-2025, % a year", "11.87", 100 * cagr(mlb[2012], mlb[2025], 13), "{:.2f}")
check("MLB/NHL ratio, 2020 list", "2.83", mlb[2020] / nhl[2020], "{:.2f}")
check("MLB/NHL ratio, 2025 list", "1.18", mlb[2025] / nhl[2025], "{:.2f}")
ratio = {y: mlb[y] / nhl[y] for y in nhl if y in mlb}
peak = max(ratio, key=ratio.get)
check("List year of the peak ratio", "2020", peak, "{:d}")
for y, o in ((2012, "2.5"), (2014, "4.0"), (2022, "5.6"), (2024, "8.5"), (2025, "8.9")):
    check(f"NHL multiple, {y} list", o, multiple[("NHL", y)], "{:.1f}")

# ---------------- Figures: the series the charts will draw ----------------
print("\nSERIES: index (2004 list = 100) and MLB/NHL ratio by list year")
print("  year   NHL $M   MLB $M   NHL idx   MLB idx   MLB/NHL")
for y in sorted(set(nhl) | set(mlb)):
    n, m = nhl.get(y), mlb.get(y)
    ni = f"{100 * n / nhl[2004]:7.1f}" if n else "       "
    mi = f"{100 * m / mlb[2004]:7.1f}" if m else "       "
    r = f"{m / n:6.2f}" if n and m else "      "
    print(f"  {y}  {n if n else '':>7}  {m if m else '':>7}   {ni}   {mi}    {r}")
print("\n  stated revenue multiples: " + "; ".join(f"{lg} {y}: {v}x" for (lg, y), v in sorted(multiple.items())))
print("  multiples implied by value/revenue where both are published: "
      + "; ".join(f"{lg} {y}: {value[(lg, y)] / rev:.1f}x" for (lg, y), rev in sorted(revenue.items())))

print("\n" + (f"ALL {checked} FIGURES MATCH THE OUTLINE" if not mismatches
              else f"{len(mismatches)} MISMATCH(ES) in {checked} checks:"))
for label, o, c in mismatches:
    print(f"  {label}: outline {o}, computed {c}")
