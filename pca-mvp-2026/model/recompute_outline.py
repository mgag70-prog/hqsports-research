"""
Recompute every model figure in pca-mvp-2026/outline.md sections 2-5 by importing the
September 14 model from pca-extension-2026/model/, unchanged. Only true talent varies;
$/WAR stays 9.0 and market capture stays 1.00.

Importing the model has side effects: pca_sensitivity prints its tables, and pca_model
runs a 100,000-path Monte Carlo and writes mc_gross.npy, mc_save.npy and base_case.json
to the working directory. Both imports happen inside a throwaway temp directory with
stdout suppressed, so nothing in pca-extension-2026/model/ is touched.

Run from the repo root:  python pca-mvp-2026/model/recompute_outline.py
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "pca-extension-2026", "model"))
sys.path.insert(0, MODEL_DIR)

_orig_cwd = os.getcwd()
_scratch = tempfile.mkdtemp(prefix="pca_mvp_import_")
os.chdir(_scratch)
try:
    with contextlib.redirect_stdout(io.StringIO()):
        import pca_model as M
        from pca_sensitivity import run
finally:
    os.chdir(_orig_cwd)

DPW = 9.0
CAPTURE = 1.00
mismatches = []


def check(label, outline, computed, fmt):
    shown = fmt.format(computed)
    ok = shown == outline
    if not ok:
        mismatches.append((label, outline, shown))
    print(f"  {'OK  ' if ok else 'DIFF'} {label:<48} outline {outline:>10}  computed {shown:>10}"
          f"  (raw {computed:.6f})")


def savings_split(talent):
    """Year-by-year savings NPV, mirroring run() line for line, plus its FA AAV."""
    _, _, fa_aav = run(talent, DPW, CAPTURE)
    years = []
    for y in M.SEASONS:
        dpw = DPW * (1 + M.WAR_INFLATION) ** (y - 2027)
        value = (talent + M.AGE_DELTA[M.AGE[y]]) * dpw
        if M.STATUS[y] == "pre-arb":
            counter = M.PRE_ARB_SALARY
        elif M.STATUS[y].startswith("arb"):
            counter = M.ARB_SHARE[M.STATUS[y]] * value
        else:
            counter = fa_aav
        years.append((y, M.STATUS[y], value, counter, M.CONTRACT[y],
                      M.pv(counter - M.CONTRACT[y], y)))
    return years


print(f"Model imported from {MODEL_DIR}")
print(f"Import side effects went to {_scratch}")
print(f"Model constants: discount {M.DISCOUNT}, inflation {M.WAR_INFLATION}, "
      f"pre-arb {M.PRE_ARB_SALARY}, arb {M.ARB_SHARE}, FA term {M.FA_TERM}, "
      f"signing bonus {M.SIGNING_BONUS}")

# ---------------- Section 2: escalator exposure ----------------
print("\nSECTION 2: maximum MVP escalator exposure")
mvp_2031 = 2.0 * len(range(2027, 2031))   # $2M per MVP, 2027-2030
mvp_2032 = 2.0 * len(range(2027, 2032))   # $2M per MVP, 2027-2031
esc_pv = M.pv(mvp_2031, 2031) + M.pv(mvp_2032, 2032)
check("Max added to 2031 base ($M)", "8.0", mvp_2031, "{:.1f}")
check("Max added to 2032 base ($M)", "10.0", mvp_2032, "{:.1f}")
check("PV to 2026 at 6% via M.pv() ($M)", "13.0", esc_pv, "{:.1f}")

# ---------------- Section 3: the four readings ----------------
print("\nSECTION 3: table from run(talent, 9.0, 1.00)")
READINGS = [  # talent, outline savings, outline surplus, outline FA AAV
    (5.4, "0.1", "153.7", "24.4"),
    (6.5, "28.6", "205.9", "36.5"),
    (8.0, "68.0", "277.1", "53.4"),
    (10.6, "136.4", "400.6", "82.7"),
]
results = {}
for t, o_save, o_gross, o_aav in READINGS:
    gross, save, aav = run(t, DPW, CAPTURE)
    results[t] = (gross, save, aav)
    check(f"talent {t}: extension savings NPV", o_save, save, "{:.1f}")
    check(f"talent {t}: surplus value NPV", o_gross, gross, "{:.1f}")
    check(f"talent {t}: counterfactual FA AAV", o_aav, aav, "{:.1f}")

print("\n  | Reading (fWAR) | True talent | Extension savings (NPV) | Surplus value (NPV) | FA AAV |")
print("  |---|---|---|---|---|")
labels = {5.4: "His 2025 season", 6.5: "September 14 base case",
          8.0: "Two-season average of 5.4 and 10.6", 10.6: "2026 taken at face value"}
for t, (g, s, a) in results.items():
    print(f"  | {labels[t]} | {t} | ${s:.1f}M | ${g:.1f}M | ${a:.1f}M |")

# ---------------- Section 4: breakeven and slope ----------------
print("\nSECTION 4: breakeven by bisection on talent, per-win slope")
lo, hi = 3.0, 8.0
assert run(lo, DPW, CAPTURE)[1] < 0 < run(hi, DPW, CAPTURE)[1], "bracket does not straddle zero"
for _ in range(80):
    mid = (lo + hi) / 2
    if run(mid, DPW, CAPTURE)[1] > 0:
        hi = mid
    else:
        lo = mid
breakeven = (lo + hi) / 2
check("Breakeven true talent (savings NPV = 0)", "5.397", breakeven, "{:.3f}")
print(f"  savings at breakeven: {run(breakeven, DPW, CAPTURE)[1]:.2e}")

ts = [t for t, *_ in READINGS]
slopes = []
for a, b in zip(ts, ts[1:]):
    slope = (results[b][1] - results[a][1]) / (b - a)
    slopes.append(slope)
    print(f"  slope {a} -> {b}: ${slope:.2f}M per win")
print(f"  outline claim: 'roughly $26M to $27M per win in this range'; "
      f"computed range ${min(slopes):.2f}M to ${max(slopes):.2f}M")

# ---------------- Section 5: control vs free agent split at 8.0 ----------------
print("\nSECTION 5: savings split at talent 8.0")
years = savings_split(8.0)
print(f"  {'Year':<6}{'Status':<12}{'Value':>9}{'No ext.':>9}{'Paid':>7}{'PV savings':>12}")
for y, status, value, counter, paid, pv_s in years:
    print(f"  {y:<6}{status:<12}{value:>9.1f}{counter:>9.1f}{paid:>7.1f}{pv_s:>12.1f}")
control = sum(r[5] for r in years if r[0] <= 2030) - M.SIGNING_BONUS
arb_only = sum(r[5] for r in years if r[1].startswith("arb"))
fa = sum(r[5] for r in years if r[0] >= 2031)
total = run(8.0, DPW, CAPTURE)[1]
assert abs(control + fa - total) < 1e-9, "split does not reconcile with run()"
print(f"  control years 2027-2030 (incl. -$5M signing bonus): ${control:.1f}M")
print(f"    of which arbitration 2028-2030:                   ${arb_only:.1f}M")
print(f"    2027 (pre-arb) PV:                                ${years[0][5]:.1f}M")
print(f"  bought-out FA years 2031-2032:                      ${fa:.1f}M")
print(f"  total (reconciles with run()):                      ${total:.1f}M")
print(f"  2027 still a loss: {years[0][5] < 0}")
print(f"  larger share: {'control years' if control > fa else 'free agent years'} "
      f"({max(control, fa) / total:.0%} of total)")
print(f"  2027 nominal loss (paid minus pre-arb renewal): "
      f"${M.CONTRACT[2027] - M.PRE_ARB_SALARY:.1f}M")


def components(talent):
    ys = savings_split(talent)
    return {"control": sum(r[5] for r in ys if r[0] <= 2030) - M.SIGNING_BONUS,
            "arb": sum(r[5] for r in ys if r[1].startswith("arb")),
            "fa": sum(r[5] for r in ys if r[0] >= 2031)}


comp = {t: components(t) for t in (6.5, 8.0, 10.6)}
for ref in (6.5, 10.6):
    c = comp[ref]
    print(f"  for reference at {ref}: control ${c['control']:.1f}M "
          f"(arbitration ${c['arb']:.1f}M), FA ${c['fa']:.1f}M")
print("  per-win change in savings NPV by source:")
for a, b in ((6.5, 8.0), (8.0, 10.6)):
    d_arb = (comp[b]["arb"] - comp[a]["arb"]) / (b - a)
    d_fa = (comp[b]["fa"] - comp[a]["fa"]) / (b - a)
    print(f"    {a} -> {b}: arbitration years ${d_arb:.2f}M/win, FA years ${d_fa:.2f}M/win")

# ---------------- Section 6 figure (outside the 2-5 scope, reported for completeness) ----------------
print("\nSECTION 6 (extra): Baseball Reference two-season average")
check("talent 7.85: extension savings NPV", "64.0", run(7.85, DPW, CAPTURE)[1], "{:.1f}")

print("\n" + ("ALL FIGURES MATCH" if not mismatches else f"{len(mismatches)} MISMATCH(ES):"))
for label, o, c in mismatches:
    print(f"  {label}: outline {o}, computed {c}")
