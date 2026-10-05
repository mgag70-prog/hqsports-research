# Outline: Does a salary cap make a franchise worth more?

Publication: Ledger & Whistle. Folder: `mlb-cap-valuations-2026/`. First piece of the
lockout series. Researched October 4, 2026. **All growth rates and ratios are
provisional until Claude Code recomputes them from `data/forbes-avg-team-value.csv`.**

---

## Working titles (Matt picks)

1. The NHL got its salary cap in 2005. For the next seven years, baseball teams gained
   value faster.
2. Baseball owners want hockey's salary cap. Hockey's cap didn't close the value gap. TV
   money did.
3. A salary cap didn't make hockey teams worth more. Baseball's owners are betting it will.

Subtitle direction: the owners' case for a cap is partly a valuation case. The one clean
test in the record, the NHL after 2005, doesn't support it on the timeline that matters.

---

## Construction note (italic, up top)

- Values are Forbes' annual estimates of average team value, not sale prices. Forbes
  changed method over the period (enterprise value from about 2013) and lists the two
  leagues at different times of year (NHL in Nov–Dec, MLB in Mar–Apr). Every figure
  carries its list year.
- A few early MLB averages are computed from Forbes' team-by-team tables as reprinted by
  Sports Business Journal; the CSV flags each one. The 2016 NHL average is from a
  secondary report.
- One league is not a control group. This is a comparison of two series, not a model.

## 1. What the owners asked for, and the argument my friends made

- AP (May 28, 2026): $245.3M cap for 2027, $171.2M floor, players at 50% of baseball
  revenue, local media revenue pooled and split equally in place of the current
  revenue-sharing plan, seven-year term.
- The argument from my group of friends, stated as theirs: owners want to look like the
  other leagues because it drives up franchise values. Expansion means more money to
  owners. Baseball lacks a cohesive TV package and revenue sharing.
- The gap they're pointing at is real. Forbes, March 20, 2026: MLB average $2.9B, 7.0x
  revenue; NBA 12.9x, NFL 10.7x, NHL 9x. (Forbes' September 9, 2026 NFL list puts the NFL
  at 13.4x.)

## 2. The clean test: the NHL in 2005

- Lockout began September 2004, cancelled the 2004-05 season (February 16, 2005), ended
  July 2005. First-year cap $39M, floor $21.5M, players' share 54% rising in tiers to 57%;
  existing contracts cut 24% (NHL.com CBA FAQ; Monthly Labor Review, December 2005).
- Before the cap, 1999 to 2004 lists: NHL average value $135M to $163M, 3.84% a year;
  MLB $220.2M to $295M, 6.02% a year.
- After the cap, 2004 to 2011 lists: NHL $163M to $240M, +47.2%, 5.68% a year; MLB $295M
  to $523M, +77.3%, 8.52% a year.
- MLB's average team was worth 1.81 times the NHL's in 2004 and 2.18 times in 2011. The
  gap widened under the cap.
- Revenue multiples, the owners' real target: Forbes put MLB at 2.5x (March 2011 list)
  and the NHL at 2.5x (2012 list, as stated in Forbes 2014). Seven years into the cap,
  the multiples were the same.
- Context that helps the cap case and must be stated: NHL teams lost a combined $96M
  before the lockout and made $96M after it (Forbes 2007). The cap fixed hockey's
  operating losses. It didn't make hockey teams outgrow baseball's.

## 3. When hockey did catch up

- 2012 to 2025 lists: NHL $282M to $2.2B, 17.12% a year; MLB $605M (2012) to $2.6B
  (2025), 11.87% a year. The MLB/NHL ratio fell from 2.83 (2020) to 1.18 (2025).
- NHL multiple: 2.5x (2012), 4.0x (2014), 5.6x (2022), 8.5x (2024), 8.9x (2025).
- What happened in those years, as timeline: NBC 10-year deal (2011, about $200M a year);
  Rogers 12-year, C$5.2B (announced November 2013); the 2012-13 lockout moved players to
  50%; Vegas expansion fee $500M (2017); ESPN and Turner deals (2021, about $625M a year
  against about $300M before). On baseball's side, the regional sports network collapse.
  **Claude Code: date Diamond Sports' bankruptcy filing from a primary source.**
- Judgment, labeled: the catch-up lines up with national television money in hockey and
  local television trouble in baseball. It doesn't line up with the cap, which the NHL had
  for sixteen years before the gap closed.

## 4. "Baseball doesn't have revenue sharing"

- It does, between clubs: each club pools 48% of prior-year net local revenue (Atlanta
  Braves Holdings 10-K, FY2025; Forbes 2016). It has a competitive balance tax (2026
  threshold $244M).
- What baseball doesn't have is a fixed player share of revenue. That's what the 50%
  split adds.
- The part of the owners' proposal that looks most like hockey isn't the cap. It's
  pooling local media money, which turns a team-by-team TV business into a league one.
- Ties to the Wrigley piece: ticket money stays local under the proposal.

## 5. Expansion

- 1998 fee: $130M a team. Manfred floated "more than $2 billion" in 2021. NHL Vegas paid
  $500M in 2017. **Claude Code: verify Seattle's NHL fee and whether expansion fees are
  shared with players in any league's revenue definition, from primary sources; drop the
  sharing point if it can't be sourced.**
- The point to land: an expansion fee is a one-time payment to existing owners, and it's
  priced off the franchise values the cap is supposed to lift.

## 6. What the research says

- No peer-reviewed study found that directly estimates a cap's effect on franchise
  values. Büschemann and Deutscher (2011, International Journal of Sport Finance) find
  NHL team efficiency improved after the 2005 CBA. Dietl, Franck, Lang and Rathke (2012,
  Contemporary Economic Policy) model a revenue-based cap raising club surplus. A 2026
  Claremont McKenna undergraduate thesis (Cioe) estimates a cap premium in value growth for
  the NFL and NBA; label it as an unreviewed thesis.

## 7. What would make this wrong

- Forbes values are estimates; method changed around 2013.
- Hockey started from a distressed base: percentage growth after 2005 was off teams losing
  money, which flatters neither side cleanly.
- Different list timing, the Canadian dollar, and expansion (Vegas, Seattle) move the NHL
  average.
- NBA and NFL caps predate Forbes' series (NFL 1994, NBA 1984), so they can't serve as a
  before-and-after test.
- The cap may matter through a channel this doesn't measure: lenders and buyers pricing
  cost certainty into debt and sale terms.

## 8. What this predicts (Matt picks one)

- If the next CBA adds a cap but not pooled local media, MLB's Forbes multiple stays below
  the NHL's through the March 2029 list. If it pools local media, the gap closes faster
  than it did after hockey's cap. Checkable on the 2028 and 2029 lists.

## 9. The data

`data/forbes-avg-team-value.csv`: Forbes average team value by list year, NHL 1999–2025,
MLB 1999–2026, with revenue and stated multiples where published, source URL per row.

---

## Figures (3 to 4)

- fig-01: average team value, NHL and MLB, indexed to the 2004 list = 100, with the 2005
  cap marked. The picture is MLB's line above hockey's for the seven years after the cap.
- fig-02: MLB average value divided by NHL average value, by list year, with events
  marked (2005 cap, 2013 Rogers, 2021 ESPN/Turner, MLB regional TV collapse). Peak 2.83
  in 2020, 1.18 in 2025.
- fig-03: annual growth before and after the cap: paired bars for 1999–2004 and 2004–2011,
  NHL and MLB.
- fig-04: revenue multiples by league, Forbes March 2026 (MLB 7.0x, NHL 9x, NFL 10.7x,
  NBA 12.9x), with the 2011-12 point where MLB and NHL were both 2.5x.
- Cover: fal.ai, house template, or a photo if Matt has one.
