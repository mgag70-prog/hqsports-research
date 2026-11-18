# College basketball special edition (publish Tuesday November 17, 2026)

First college basketball piece. Every number from data/csc-revshare.csv, data/context.csv or model/recompute.py. No ordinals.

## Angle
The College Sports Commission's own payment data shows the SEC paid fewer than half of its men's basketball players any revenue share last season, and its median player got $0. In the Big 12, 79.0% got paid and the median player got $100,000. Same $20.5 million cap; very different choices about who gets it.

Working H1: More than half the SEC's men's basketball players got no revenue share last season. In the Big 12, the median player got $100,000.
Working dek: The College Sports Commission's payment data shows each power conference split the $20.5 million cap its own way.
Cover line (verbatim in draft): $0 for the median player.

## 1. The data (short, up top)
- CSC's School Revenue Share Compensation Report: payments recorded in CAPS. Basketball window July 1, 2025 to April 6, 2026 (payments due after April 6 not included). Percentiles by conference, "with $0" (every rostered athlete) and "without $0" (only those paid).
- It's the first look at who actually gets paid. Schools don't publish this: link the Illinois piece (Illinois denied my records request; no Big Ten school publishes revenue sharing by sport in dollars). This is conference-level, not school-level.

## 2. Men's basketball by conference
- Share of roster paid: Big 12 79.0% (196 of 248), ACC 61.2% (169 of 276), Big Ten 59.4% (165 of 278), SEC 45.1% (114 of 253).
- Median rostered player: Big 12 $100,000, Big Ten $48,000, ACC $38,000, SEC $0.
- But the SEC pays the players it pays: its paid 25th percentile is $117,500, the highest of the four; paid median $175,000. Concentrated vs spread.
- Top end (90th percentile, all players): Big 12 $579,000, ACC $500,500, Big Ten $462,500, SEC $339,500 (lowest).
- Across the four, 61.0% of men's basketball players were paid. Outside the four (Non-A4), 62.8%.

## 3. Football comparison (one section, short)
- Power-conference football: 75.1% of rostered players paid or scheduled to be paid in 2026 (5,817 of 7,743 across positions). Quarterback 90th percentile $1,266,500, 2.2 times the top Big 12 basketball figure.
- Caveat: football window is calendar 2026 including scheduled payments and contingent incentives; basketball is payments made through April 6. Don't add or compare totals.
- Judgment, labeled: the SEC's basketball numbers look like a football-first league spending its cap where its money comes from. The data doesn't show school budgets, so this is a read, not a finding.

## 4. Women's basketball (short)
- Big Ten paid 79.4% of women's players, median $31,000; SEC 46.0%, median $0. Big Ten is the outlier on the women's side the way the Big 12 is on the men's.

## 5. What this can't tell you
- No totals and no school-level numbers; percentiles only; payments due after April 6 missing (SEC schools that pay late in the year would look smaller). Excludes scholarships, cost of attendance, Alston and third-party NIL (NIL Go is a separate report).

## 6. Prediction [MATT TO CONFIRM]
When the CSC publishes 2026-27 basketball numbers, the SEC is again the power conference that pays the smallest share of its men's basketball roster.

## Figures
- fig-01: share of men's basketball roster paid, by conference (four bars + Non-A4), with the median rostered player labeled.
- fig-02: paid-only percentile ranges (25th/50th/75th/90th) by conference, showing the SEC's high floor.

## About this piece
Construction note: data scraped from the CSC's interactive report on November 17, 2026 (script output in raw/); percentiles suppressed below CSC's sample thresholds. Disclosure: Illinois football fan (not an alum). (Standard line.)
