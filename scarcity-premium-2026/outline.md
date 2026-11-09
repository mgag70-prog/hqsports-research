# Outline: scarcity-premium-2026 (publish Friday Nov 6 afternoon)

Working H1: "Buyers paid 24% more than Forbes said the team was worth. The trophy teams didn't get the biggest premiums."
Alt H1: "Billionaires do overpay for teams. Just not for the ones you'd guess."
Alt H1 2: "33 team sales, 28 above Forbes. The Celtics and Mets went for almost exactly the estimate."
Cover line (verbatim in draft): "Sold above the estimate."
Dek (subtitle, under 150 characters): "In 33 control sales since 2012, buyers paid a median 24% over Forbes. The biggest premiums went to the Hornets and Padres, not the Celtics."

Data: data/control_sales_verified.csv (47 deals, 2011-2026, each re-sourced by an independent check), data/classification.csv (why deals are excluded), model/recompute.py (all checks pass), data/sales-computed.csv (output). Forbes values are from the Forbes list in force when each sale was announced (forbes.com blocked to us; figures from contemporaneous reports quoting the list or Forbes regional editions).

## The prompt for the piece
A reader-shared argument (don't name or quote the post): elite teams can't be replicated and there are more billionaires than teams, so when one comes up the auction blows past any estimate. Test it.

## 1. The answer (fig-01: each clean deal's premium, sorted, colored by league)
- 33 clean control sales, 2012-2026: median premium over the prior Forbes value 24.0%; 28 above, 5 below. Aggregate: $89.56B paid against $74.07B of Forbes value, 20.9% more.
- Clean = price and Forbes both found and checked; not a forced or bankruptcy sale; not sold by the league; not a staged deal where control passed later or a price set years earlier by option.
- Including every deal with both figures (43): median 26.9%. Excluded ones are named in section 5.

## 2. By league (fig-02: median by league with n)
- NHL 36.5% (7), NBA 25.0% (13), MLB 16.7% (7), NFL 16.0% (6). Small samples; say so.
- Ties to the cap piece (Oct 5): owners argue a cap lifts values; the leagues with caps don't show a consistently higher sale premium than MLB here. Careful, one line, no causal claim.

## 3. Trophy teams didn't get the biggest premiums (the test of the thesis)
- Celtics 2025: $6.1B vs Forbes $6.0B, +1.7%. Mets 2020: +0.8%. Commanders 2023: +8.0%. Mavericks 2023: -22.2% (below Forbes). Lakers 2025: +40.8% and Lakers 2026: +25.0% (but the 2026 deal is measured against Forbes' figure, which was Walter's own 2025 price; AP says $12B, others $12.5B, so +20% to +25%).
- Biggest premiums: Hornets 2023 +76.5%, Padres 2012 +74.7% (overstated: price included $200M of TV money), Devils 2013 +56.1%, Bills 2014 +49.7%, Suns 2022 +48.1%.
- Deals of $3B or more: median 24.5% (10 deals); under $3B: 18.7% (23). A little higher at the top, nothing like an auction frenzy.
- Seahawks 2026: $9.612B vs Forbes $6.7B, +43.5%, the newest big NFL data point.

## 4. When it happened (fig-03: median by period)
- 2012-2017: 34.5% (14). 2018-2022: 7.1% (7). 2023-2026: 20.0% (12). Forbes may have caught up in the middle years; don't overclaim.

## 5. What I left out and why
- Clippers 2014: $2.0B vs $575M, +247.8%: forced sale after the NBA banned Donald Sterling.
- Dodgers 2012 (bankruptcy auction, stadium and land included); Hornets 2012 and Coyotes 2013 (league was the seller); Utah 2024 (league-arranged).
- Staged or option-priced: Bucks 2023 (25% stake), Nets 2019 (2018 option price), Lightning 2024 (Vinik keeps control three years), Islanders 2014 (control passed 2016), Timberwolves 2021 (control passed in 2025 at the 2021 price, $1.5B, against Forbes' $3.1B: the clearest case of a buyer paying far less than Forbes).
- Caveats kept in the set: bundled assets (Jazz arena, Devils arena rights, Blues arena lease, Blazers blended price) push those premiums up; Kings 2013 baseline already reflected the Seattle bid; Senators stake ambiguity (90%); Panthers 2013 reported $250M vs $230M.

## 6. What the 24% means
- Forbes estimates are not prices. A 24% median gap says Forbes is conservative on the teams that actually sell, which is a selected group (teams sell when buyers want them).
- Minority stakes (Raiders, Browns, etc.) are not in this set; they typically price at a discount to control.

## 7. Prediction [MATT TO CONFIRM]
The next NBA, NFL or MLB control sale announced after this piece clears the most recent Forbes value for that team. Checkable at the next announcement.

## Figures (house style): fig-01 deal-by-deal premiums (33), fig-02 by league, fig-03 by period; optional fig-04 trophy deals vs the rest.
## Cover: flashy, no logos/team marks/readable text/model numbers; baseballs white with red stitching; idea: an auction paddle raised in a dark luxury room, or a gavel on a stack of gold over a stadium blueprint.
## Layout: house rule (dek in subtitle; About this piece; Sources bulleted linked; Not for publication). 1,400-1,900 words. paste-into-substack.html.
## Disclosure: held Cubs season tickets 1998 to 2021 (Cubs not in the set).
