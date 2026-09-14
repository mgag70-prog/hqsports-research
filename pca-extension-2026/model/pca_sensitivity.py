import pca_model as M

SEASONS = M.SEASONS
AGE = M.AGE
CONTRACT = M.CONTRACT
STATUS = M.STATUS
AGE_DELTA = M.AGE_DELTA


def run(talent, dpw2027, capture, infl=0.03, disc=0.06):
    def dpw(y):
        return dpw2027 * (1 + infl) ** (y - 2027)

    fa_years = list(range(2031, 2031 + M.FA_TERM))
    fa_total = sum(max(0.0, talent + AGE_DELTA[29 + (y - 2031)]) * dpw(y) for y in fa_years)
    fa_aav = fa_total * capture / M.FA_TERM

    gross = save = 0.0
    for y in SEASONS:
        war = talent + AGE_DELTA[AGE[y]]
        value = war * dpw(y)
        if STATUS[y] == "pre-arb":
            counter = M.PRE_ARB_SALARY
        elif STATUS[y].startswith("arb"):
            counter = M.ARB_SHARE[STATUS[y]] * value
        else:
            counter = fa_aav
        d = (1 + disc) ** (y - 2026)
        gross += (value - CONTRACT[y]) / d
        save += (counter - CONTRACT[y]) / d
    return gross - M.SIGNING_BONUS, save - M.SIGNING_BONUS, fa_aav


print("Two-way sensitivity: EXTENSION SAVINGS, NPV $M (capture = 1.00)")
print(f"{'talent/$WAR':<12}" + "".join(f"{d:>9.0f}" for d in [7, 8, 9, 10, 11, 12, 13]))
for t in [4.5, 5.5, 6.5, 7.5, 8.5]:
    line = f"{t:<12.1f}"
    for d in [7, 8, 9, 10, 11, 12, 13]:
        line += f"{run(t, d, 1.00)[1]:>9.0f}"
    print(line)

print()
print("Two-way sensitivity: GROSS SURPLUS VALUE, NPV $M")
print(f"{'talent/$WAR':<12}" + "".join(f"{d:>9.0f}" for d in [7, 8, 9, 10, 11, 12, 13]))
for t in [4.5, 5.5, 6.5, 7.5, 8.5]:
    line = f"{t:<12.1f}"
    for d in [7, 8, 9, 10, 11, 12, 13]:
        line += f"{run(t, d, 1.00)[0]:>9.0f}"
    print(line)

print()
print("Market capture sensitivity (talent 6.5, $/WAR 9.0)")
for c in [0.80, 0.90, 1.00, 1.10, 1.20, 1.30]:
    g, s, aav = run(6.5, 9.0, c)
    print(f"  capture {c:.2f}  FA AAV ${aav:>5.1f}M   extension savings NPV ${s:>6.1f}M")

print()
print("Breakeven search: FA AAV at which extension savings NPV = 0 (talent 6.5, $/WAR 9.0)")
lo, hi = 0.0, 2.0
for _ in range(60):
    mid = (lo + hi) / 2
    if run(6.5, 9.0, mid)[1] > 0:
        hi = mid
    else:
        lo = mid
print(f"  capture {lo:.3f} -> FA AAV ${run(6.5, 9.0, lo)[2]:.1f}M")
