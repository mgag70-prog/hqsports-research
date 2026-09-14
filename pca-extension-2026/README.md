# Pete Crow-Armstrong extension: surplus value versus extension savings

Model, data, and figures behind *The Cubs Saved $29 Million on Pete Crow-Armstrong.
Not $206 Million.* (September 14, 2026).

## What is here

`model/`
- `PCA_Extension_Model.xlsx` — the valuation model as an editable workbook. Every input
  is on the Assumptions tab. Change one and every other tab recalculates.
- `pca_model.py` — the same model in Python, plus a 100,000-path Monte Carlo over
  true-talent uncertainty, season-to-season variance, injury, and a career-ending tail.
- `pca_sensitivity.py` — two-way sensitivity grids over true talent and dollars per win.
- `build_workbook.py` — generates the workbook from the same assumptions.

`data/`
- `pca_2026_gamelog_by_batting_order.csv` — all 150 games through September 13, 2026,
  with batting order position, transcribed from Baseball Reference game logs. Every
  season total reconciles to Baseball Reference.
- `pca_2026_splits_by_batting_order.csv` — the game log aggregated by lineup spot.

`figures/`
- `pca_savings_by_year.png` — what the Cubs pay versus what they would have paid, by year.
- `pca_two_numbers.png` — surplus value versus extension savings, with simulation bands.
- `pca_arbitration_stat_card.png` — the broadcast stat card rebuilt with an arbitration column.
- HTML sources and build scripts for each.

## Contract facts

Six years, $115 million, covering 2027 through 2032, signed March 24, 2026. $5 million
signing bonus payable by May 15, 2026. Salaries of $10 million in 2027, 2028, and 2029,
$20 million in 2030, $30 million in 2031 and 2032. No club options. MVP escalators on the
2031 and 2032 bases keyed to 2027 through 2031 voting. Service time 1.170 at signing,
which put free agency after the 2030 season. Sources: Associated Press, MLB.com, Spotrac,
Baseball Reference.

## Base-case assumptions

| Input | Value |
|---|---|
| True talent WAR entering 2027 (age 25) | 6.5 |
| Market rate per win, 2027 | $9.0 million |
| Annual inflation in dollars per win | 3.0% |
| Discount rate | 6.0% |
| 2027 pre-arbitration salary, no extension | $1.0 million |
| Arbitration share of open-market value (arb 1 / 2 / 3) | 25% / 40% / 60% |
| Hypothetical free agent deal after 2030 | 8 years, ages 29 through 36 |
| Share of projected value captured in that deal | 100% |

Aging curve: +0.0 at 25, +0.3 at 26, +0.3 at 27, then declining, steeper than a
slugger's because the value leans on defense and speed. Full curve on the Assumptions tab.

## Headline results, present value to 2026

| | Base case | Simulation median | 10th to 90th pct | Positive in |
|---|---|---|---|---|
| Surplus value (production minus salary) | $205.9M | $171M | $88M to $251M | 98.0% |
| Extension savings (versus no extension) | $28.6M | $20M | -$15M to $52M | 78.5% |

Of the $28.6 million: $19.1 million from the four control years, $9.4 million from the
two bought-out free agent years. 2027 alone is a $9.0 million loss.

## Reproduce

    cd model
    python3 pca_model.py          # base case, Monte Carlo, writes base_case.json
    python3 pca_sensitivity.py    # sensitivity grids
    python3 build_workbook.py     # regenerates the xlsx

Requires numpy, pandas, openpyxl, matplotlib. The figure scripts in `figures/` need
Playwright with Chromium for the HTML-rendered cards.

## Not modeled

MVP escalators, the $1 million assignment bonus on any trade, the pre-arbitration bonus
pool, off-field revenue, and a salary cap, which would reset both the market rate per win
and the free agent counterfactual at once.

## A judgment, not a measurement

The arbitration column on the stat card reflects which categories salary arbitration
filings and panels have historically treated as load-bearing. Reasonable people would
grade some rows differently.
