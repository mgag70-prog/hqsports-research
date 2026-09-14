import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BLUE = "#0E3386"
RED = "#CC3433"
GREEN = "#1B7F4B"
GREY = "#9AA3AE"
INK = "#1B1F24"

base = json.load(open("../model/base_case.json"))
rows = base["rows"]
years = [r["year"] for r in rows]
paid = [r["actual"] for r in rows]
counter = [r["counter"] for r in rows]
savings = [r["savings"] for r in rows]
labels = [f"{r['year']}\nage {r['age']}\n{r['status']}" for r in rows]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.edgecolor": "#D7DBE0",
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
    "mathtext.default": "regular",
})
def _fmt(v, p=None):
    return ("-" if v < 0 else "") + "\\${:,.0f}M".format(abs(v))
money = FuncFormatter(_fmt)

# ---------------- Chart 1 ----------------
fig, ax = plt.subplots(figsize=(11, 6.6))
fig.subplots_adjust(top=0.80, bottom=0.20)
x = np.arange(len(years))
w = 0.38

ax.bar(x - w / 2, paid, w, label="Paid under the extension", color=BLUE)
ax.bar(x + w / 2, counter, w, label="Cost with no extension (modeled)", color=GREY)

for i, s in enumerate(savings):
    top = max(paid[i], counter[i])
    color = RED if s < 0 else GREEN
    sign = "+" if s > 0 else "-"
    ax.text(x[i], top + 1.4, "{}\\${:,.1f}M".format(sign, abs(s)), ha="center", va="bottom",
            fontsize=12, fontweight="bold", color=color)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("\\$ millions", fontsize=11)
ax.yaxis.set_major_formatter(money)
ax.set_ylim(0, 46)
ax.legend(frameon=False, fontsize=11, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", color="#E9ECEF")
ax.set_axisbelow(True)

fig.text(0.02, 0.945, "Where the Cubs actually save money on Pete Crow-Armstrong",
         fontsize=17, fontweight="bold", color=INK)
fig.text(0.02, 0.895,
         "The two free agent years the extension buys out are worth about \\$9M in present value.",
         fontsize=11.5, color="#495057")
fig.text(0.02, 0.858,
         "The arbitration years the Cubs locked in are worth \\$24M.",
         fontsize=11.5, color="#495057")
fig.text(0.02, 0.035,
         "Contract terms: AP and MLB.com, March 2026. Counterfactual assumes 6.5 WAR true talent entering age 25, standard aging, "
         "\\$9.0M per win in 2027 inflating 3% a year,",
         fontsize=8.5, color="#6C757D")
fig.text(0.02, 0.010,
         "arbitration at 25/40/60% of open-market value, and a hypothetical eight-year free agent deal covering ages 29 to 36. "
         "A model, not a forecast.",
         fontsize=8.5, color="#6C757D")
plt.savefig("./pca_savings_by_year.png", dpi=200, facecolor="white")
plt.close()

# ---------------- Chart 2 ----------------
gross = np.load("../model/mc_gross.npy")
save = np.load("../model/mc_save.npy")

fig, ax = plt.subplots(figsize=(11, 5.8))
fig.subplots_adjust(top=0.74, bottom=0.20, left=0.05, right=0.97)

items = [("Surplus value\nvalue produced minus salary paid", gross, BLUE),
         ("Savings from the extension itself\nversus keeping him year to year", save, RED)]

for i, (name, arr, color) in enumerate(items):
    p10, p50, p90 = np.percentile(arr, [10, 50, 90])
    y = len(items) - 1 - i
    ax.hlines(y, p10, p90, color=color, alpha=0.28, linewidth=30)
    ax.plot([p50], [y], "o", color=color, markersize=15, zorder=3)
    ax.text(p50, y + 0.26, _fmt(p50), ha="center", fontsize=16,
            fontweight="bold", color=color)
    ax.text(p10, y - 0.30, _fmt(p10), ha="center", fontsize=10, color="#6C757D")
    ax.text(p90, y - 0.30, _fmt(p90), ha="center", fontsize=10, color="#6C757D")
    ax.text(-95, y, name, ha="left", va="center", fontsize=12, color=INK)

ax.axvline(0, color="#ADB5BD", linewidth=1, linestyle="--")
ax.set_xlim(-100, 285)
ax.set_ylim(-0.7, 1.7)
ax.set_yticks([])
ax.xaxis.set_major_formatter(money)
ax.set_xlabel("Present value to the Cubs, 2027 through 2032, discounted to 2026 at 6%", fontsize=11)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#E9ECEF")
ax.set_axisbelow(True)

fig.text(0.02, 0.935, "Two true numbers that answer different questions",
         fontsize=17, fontweight="bold", color=INK)
fig.text(0.02, 0.875,
         "Bars span the 10th to 90th percentile of 100,000 simulated career paths.",
         fontsize=11.5, color="#495057")
fig.text(0.02, 0.828,
         "The extension saves the Cubs money in 79% of them. It costs them money in 21%.",
         fontsize=11.5, color="#495057")
fig.text(0.02, 0.030,
         "Same assumptions as the year-by-year build. Simulation adds season-to-season variance, true-talent drift, "
         "a 10% annual chance of a major injury, and a small career-ending tail.",
         fontsize=8.5, color="#6C757D")
plt.savefig("./pca_two_numbers.png", dpi=200, facecolor="white")
plt.close()
print("ok")
