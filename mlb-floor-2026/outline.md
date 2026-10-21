# Outline: mlb-floor-2026

Working H1: "Baseball's best team would have been under the owners' salary floor."
Alt H1: "The Brewers won 103 games and a pennant on a payroll the owners want to make illegal."
Cover line (must appear verbatim in draft): "Under the floor. In the World Series."
Publish: Wednesday Oct 21 or Thursday Oct 22, after the ALCS ends, before World Series Game 1 (Fri Oct 23, Milwaukee).
Series: lockout series, after the season-ticket survey (Oct 9) and 154-game piece (Oct 12); ties to the cap-valuations piece (Oct 5).

All numbers: model/recompute.py (all checks pass). Payrolls are Spotrac 2026 luxury-tax payrolls, end of regular season, read October 19, 2026; they include player benefits ($18M line item on Spotrac's team tax pages), which puts them on the same basis as the owners' cap and floor ("including benefits expenses," CBS May 28). The four final-four figures are each within $1M of the MLB figures CBS published October 13.

## Dek
On May 28 the owners proposed a $245.3 million cap and a $171.2 million floor for 2027. Measured against 2026 payrolls, the Brewers, baseball's best team at 103-59, were $16.5 million under that floor. The Rays (98-64) were $58.0 million under it. The Dodgers, the team the Brewers swept, were $187.8 million over the cap.

## Construction note (italic, short)
- Spotrac tax payrolls, end of 2026 regular season, read Oct 19; include player benefits; same basis as the proposal.
- The cap and floor are 2027 figures; the comparison applies them to 2026 payrolls. Illustrative, not a forecast of 2027 payrolls.
- The proposal ties the cap to 50% of revenue, so the lines would move year to year.

## 1. The final four, against the lines (fig-01)
- LAD $433.06M (1st) | MIL $154.71M (19th) | TB $113.23M (27th) | CLE $92.58M (29th).
- LAD is $72.5M more than the other three combined.
- Under the proposal, three of the four would be under the floor. The Brewers would have to add $16.5M, the Rays $58.0M, the Guardians $78.6M. The Dodgers would have to cut $187.8M.
- NLCS: Brewers swept the two-time defending champion Dodgers 4-0 (Oct 11-15), their first NL pennant (MLB.com).
- ALCS: [UPDATE: winner, date]. Either way, both pennant winners were under the owners' floor.

## 2. All 30 clubs (fig-02)
- 9 over the cap, 12 under the floor, 9 inside.
- Moving everyone inside the lines: over-cap clubs cut $627.3M, under-floor clubs add $548.3M, net $79.0M less for players.
- Place it among the claims: MLB said players gain $39M; the union (Bruce Meyer) said players lose more than $500M; CBS's May estimate from Cot's early-season numbers was an $18.7M cut. State as theirs; ours uses end-of-season payrolls.

## 3. Wins vs payroll (fig-03): be fair
- Honest counterpoint: on average the 9 over-cap clubs won 88.3 games, the 12 under-floor clubs 80.0. Spending still buys wins on average. Do not hide this.
- But: the best record (MIL 103) and third-best (TB 98) were under the floor; LAD (100) second.
- Postseason: 12 clubs; 7 over the cap, 4 under the floor (MIL, TB, CLE, CHW), 1 inside (HOU).
- Every series this October between an under-floor club and an over-cap club went to the under-floor club: Rays over Yankees (ALDS), Brewers over Padres (NLDS), Brewers over Dodgers (NLCS). Three series. Too small to prove anything; say so (CBS's Snyder made this point Oct 13: one October proves nothing about a cap).

## 4. What a floor does that the owners don't say
- A floor is a spending requirement on the cheapest clubs. The four clubs at the bottom of the 2026 tax table (TB, STL, CLE, MIA) would need to add $58.0M (TB), $62.4M (STL), $78.6M (CLE) and $86.8M (MIA). (STL $62.4M, MIA $86.8M; from data/2026-vs-cap-floor.csv)
- The owners' pitch is competitive balance (MLB social posts, July; Manfred). Two of the most competitive teams in baseball got there under the floor.
- The cap side does the cutting: nine clubs, $627.3M.
- The point: the floor and the cap are sold together, but they hit different clubs, and the cap side is bigger.

## 5. Prediction on the record [MATT TO CONFIRM]
If the next CBA includes a cap and floor, at least one of the Brewers, Rays or Guardians has to raise its payroll in the first season to reach the floor. Checkable when the next agreement's terms and the first season's tax payrolls are published.

## Figures (house style, navy #16284A, red #D4553D, paper #F7F5F0; SVG + 1200px PNG; assert against data, draft, captions)
- fig-01: final four horizontal bars vs cap and floor lines (LAD, MIL, TB, CLE), labels with $ and record.
- fig-02: all 30 clubs sorted by tax payroll, cap and floor lines, final four in red, others navy/gray by status.
- fig-03: scatter wins vs tax payroll, cap and floor vertical lines, postseason clubs marked, label MIL, TB, CLE, LAD, NYM (most expensive non-playoff: NYM $359.48M, 74-88).
- fig-04 (optional): diverging bars, change to comply by club (adds vs cuts), totals $548.3M and $627.3M.

## Cover
Flashy, full bleed (Matt's new standard). Idea: a ballpark scoreboard or an empty dugout floor with a painted foul-line-style "floor" line; or a stack of baseballs below a red line. No team logos, uniforms, numbers or readable text. Cover line in big type: "Under the floor. In the World Series."

## Disclosure
Per the published Wrigley piece (Oct 4), Matt paid for the same four Wrigley seats for 18 years. Cubs are over the cap here ($269.22M). One line if relevant; state nothing else about Matt without a source.

## Sources
See data/context.csv and data/sources.md.
