"""
Pete Crow-Armstrong extension valuation model.
Separates (A) gross surplus value from (B) savings attributable to the extension decision.
All dollars in millions.
"""
import numpy as np

# ---------------- Known contract facts (AP / MLB.com / Spotrac, March 2026) ----------------
SEASONS = [2027, 2028, 2029, 2030, 2031, 2032]
AGE = {2027: 25, 2028: 26, 2029: 27, 2030: 28, 2031: 29, 2032: 30}
CONTRACT = {2027: 10.0, 2028: 10.0, 2029: 10.0, 2030: 20.0, 2031: 30.0, 2032: 30.0}
SIGNING_BONUS = 5.0          # paid by May 15, 2026
BASE_YEAR = 2026

# Control status absent the extension (service time 1.170 as of Jan 2026 -> FA after 2030)
STATUS = {2027: "pre-arb", 2028: "arb1", 2029: "arb2", 2030: "arb3",
          2031: "free agent", 2032: "free agent"}

# ---------------- Assumptions (editable levers) ----------------
TRUE_TALENT_2027 = 6.5       # regressed true-talent WAR going into age 25
AGE_DELTA = {25: 0.0, 26: 0.3, 27: 0.3, 28: -0.1, 29: -0.7, 30: -1.4,
             31: -2.1, 32: -2.8, 33: -3.5, 34: -4.2, 35: -4.9, 36: -5.6}
DOLLARS_PER_WAR_2027 = 9.0
WAR_INFLATION = 0.03
DISCOUNT = 0.06
PRE_ARB_SALARY = 1.0         # 2027 renewal absent extension
ARB_SHARE = {"arb1": 0.25, "arb2": 0.40, "arb3": 0.60}
FA_TERM = 8                  # hypothetical free agent deal, ages 29-36
MARKET_CAPTURE = 1.00        # share of projected value an elite FA actually captures


def dollars_per_war(year):
    return DOLLARS_PER_WAR_2027 * (1 + WAR_INFLATION) ** (year - 2027)


def projected_war(year, talent=TRUE_TALENT_2027):
    return talent + AGE_DELTA[AGE.get(year, 29 + (year - 2031))]


def pv(amount, year):
    return amount / (1 + DISCOUNT) ** (year - BASE_YEAR)


# ---------------- Counterfactual free agent AAV for 2031-2032 ----------------
fa_years = list(range(2031, 2031 + FA_TERM))
fa_ages = {y: 29 + (y - 2031) for y in fa_years}
fa_war = {y: TRUE_TALENT_2027 + AGE_DELTA[fa_ages[y]] for y in fa_years}
fa_total_value = sum(max(0.0, fa_war[y]) * dollars_per_war(y) for y in fa_years)
FA_AAV = fa_total_value * MARKET_CAPTURE / FA_TERM

# ---------------- Deterministic year-by-year build ----------------
rows = []
for y in SEASONS:
    war = projected_war(y)
    dpw = dollars_per_war(y)
    value = war * dpw
    if STATUS[y] == "pre-arb":
        counter = PRE_ARB_SALARY
    elif STATUS[y].startswith("arb"):
        counter = ARB_SHARE[STATUS[y]] * value
    else:
        counter = FA_AAV
    actual = CONTRACT[y]
    rows.append({
        "year": y, "age": AGE[y], "status": STATUS[y], "war": war, "dpw": dpw,
        "value": value, "actual": actual, "counter": counter,
        "gross_surplus": value - actual, "savings": counter - actual,
    })

gross_nom = sum(r["gross_surplus"] for r in rows) - SIGNING_BONUS
save_nom = sum(r["savings"] for r in rows) - SIGNING_BONUS
gross_npv = sum(pv(r["gross_surplus"], r["year"]) for r in rows) - SIGNING_BONUS
save_npv = sum(pv(r["savings"], r["year"]) for r in rows) - SIGNING_BONUS

control_save_npv = sum(pv(r["savings"], r["year"]) for r in rows if r["year"] <= 2030) - SIGNING_BONUS
fa_save_npv = sum(pv(r["savings"], r["year"]) for r in rows if r["year"] >= 2031)

cost_npv = sum(pv(r["actual"], r["year"]) for r in rows) + SIGNING_BONUS
counter_npv = sum(pv(r["counter"], r["year"]) for r in rows)

print("=" * 78)
print("DETERMINISTIC BASE CASE")
print("=" * 78)
print(f"{'Yr':<5}{'Age':<5}{'Status':<12}{'WAR':>6}{'$/WAR':>8}{'Value':>9}"
      f"{'Paid':>9}{'No ext.':>10}{'Savings':>10}")
for r in rows:
    print(f"{r['year']:<5}{r['age']:<5}{r['status']:<12}{r['war']:>6.1f}"
          f"{r['dpw']:>8.2f}{r['value']:>9.1f}{r['actual']:>9.1f}"
          f"{r['counter']:>10.1f}{r['savings']:>10.1f}")
print()
print(f"Hypothetical free agent AAV for 2031-32 (8yr, ages 29-36): ${FA_AAV:,.1f}M")
print(f"Total projected WAR 2027-2032: {sum(r['war'] for r in rows):.1f}")
print()
print(f"Contract cost, nominal:                 ${sum(CONTRACT.values()) + SIGNING_BONUS:,.1f}M")
print(f"Contract cost, NPV to {BASE_YEAR} @ {DISCOUNT:.0%}:       ${cost_npv:,.1f}M")
print(f"Counterfactual cost, NPV:               ${counter_npv:,.1f}M")
print()
print(f"A. Gross surplus value  nominal:        ${gross_nom:,.1f}M")
print(f"A. Gross surplus value  NPV:            ${gross_npv:,.1f}M")
print(f"B. Extension savings    nominal:        ${save_nom:,.1f}M")
print(f"B. Extension savings    NPV:            ${save_npv:,.1f}M")
print(f"   of which control years 2027-2030:    ${control_save_npv:,.1f}M")
print(f"   of which bought-out FA 2031-2032:    ${fa_save_npv:,.1f}M")

# ---------------- Monte Carlo ----------------
rng = np.random.default_rng(1908)
N = 100_000

talent0 = rng.normal(TRUE_TALENT_2027, 1.1, N)
alive = np.ones(N, dtype=bool)
talent = talent0.copy()

gross_paths = np.zeros(N)
save_paths = np.zeros(N)
war_totals = np.zeros(N)

for y in SEASONS:
    talent = talent + rng.normal(0, 0.35, N)
    ended = rng.random(N) < 0.008
    alive = alive & ~ended

    injured = rng.random(N) < 0.10
    pt = np.where(injured, rng.uniform(0.30, 0.70, N), rng.uniform(0.88, 1.0, N))

    war = np.maximum(0.0, rng.normal(talent + AGE_DELTA[AGE[y]], 1.3, N)) * pt * alive
    war_totals += war

    dpw = dollars_per_war(y)
    value = war * dpw

    if STATUS[y] == "pre-arb":
        counter = np.full(N, PRE_ARB_SALARY)
    elif STATUS[y].startswith("arb"):
        counter = ARB_SHARE[STATUS[y]] * value
    else:
        # FA AAV scales with realized talent trajectory entering free agency
        counter = FA_AAV * np.clip(talent / TRUE_TALENT_2027, 0.15, 2.0) * alive

    disc = (1 + DISCOUNT) ** (y - BASE_YEAR)
    gross_paths += (value - CONTRACT[y]) / disc
    save_paths += (counter - CONTRACT[y]) / disc

gross_paths -= SIGNING_BONUS
save_paths -= SIGNING_BONUS

def band(a):
    return np.percentile(a, [10, 25, 50, 75, 90])

print()
print("=" * 78)
print(f"MONTE CARLO ({N:,} paths), NPV to {BASE_YEAR}, $ millions")
print("=" * 78)
for label, arr in [("Total WAR 2027-2032", war_totals),
                   ("A. Gross surplus value", gross_paths),
                   ("B. Extension savings", save_paths)]:
    p10, p25, p50, p75, p90 = band(arr)
    print(f"{label:<26} P10 {p10:>8.1f}  P25 {p25:>8.1f}  P50 {p50:>8.1f}"
          f"  P75 {p75:>8.1f}  P90 {p90:>8.1f}")
print()
print(f"P(extension saves the Cubs money): {(save_paths > 0).mean():.1%}")
print(f"P(gross surplus positive):         {(gross_paths > 0).mean():.1%}")

np.save("mc_gross.npy", gross_paths)
np.save("mc_save.npy", save_paths)
import json
json.dump({"rows": rows, "fa_aav": FA_AAV, "gross_npv": gross_npv, "save_npv": save_npv,
           "control_save_npv": control_save_npv, "fa_save_npv": fa_save_npv,
           "cost_npv": cost_npv, "counter_npv": counter_npv},
          open("base_case.json", "w"), indent=1)
