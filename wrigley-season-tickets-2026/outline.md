# Outline: Twenty-four years of Cubs season-ticket invoices

Publication: Ledger & Whistle. Folder: `wrigley-season-tickets-2026/`. First piece of the
fan-side run into the lockout series. Researched October 3, 2026. **All figures are
provisional until Claude Code recomputes them from `data/`.**

---

## Working titles (Matt picks)

1. I paid for the same four Wrigley seats for 18 years. After inflation, the price rose 13%
   in the first 11 and 45% in the last six.
2. My Cubs tickets kept pace with inflation until 2016. Then they didn't.
3. Twenty-four years of Cubs season-ticket invoices, and the year the price changed.

Subtitle direction: one fan's invoices are the only clean price series on the most opaque
revenue line in baseball. Inflation was the same in both periods. The price wasn't.

---

## Construction note (italic, up top)

- The data is my own: season-ticket invoices, 1998 through 2021. Two seats in Section 213
  from 1998 through 2003, four seats in Section 105
  field box from 2004 through 2021. Different seats, so the like-for-like series is 2004
  through 2021.
- Totals from 1998 through 2014 are rounded by me, some by as much as a couple of
  thousand dollars. 2015 ($23,398) and every year after are exact. So year-to-year moves
  before 2015 can't be read; only the endpoints can. Claude Code: show how far the
  2004-2015 rate moves if 2004 is off by $1,000 either way.
- Real figures use BLS CPI-U annual averages, stated in 2021 dollars.
- Disclosure: I'm a Cubs fan, I held these seats for 24 years, and I gave them up after
  2021 over how the 2020 refunds were handled. Read the 2020 section with that in mind.

## 1. The seats and the numbers

- 1998: two seats in Section 213, $8,000, $4,000 a seat. 2003: $10,000, $5,000 a seat.
- 2004: four Section 105 field box seats, $16,500, $4,125 a seat. 2021: $38,751,
  $9,687.75 a seat, about $119.60 a seat per home date over 81 games.
- Playoff tickets bought in 2015 ($7,510) and 2016 ($8,430) only.
- Small stat block or table built as a graphic (tables don't paste into Substack).

## 2. Eleven years near inflation, 2004 to 2015

- Nominal: $16,500 (rounded) to $23,398 (exact), 3.2% a year. CPI over the same years: 2.1% a year.
- Real (2021 dollars): $23,669 to $26,750, up 13.0%, 1.1% a year.
- The dips in the spreadsheet in 2011 and 2012 are rounding, not price cuts. Don't
  claim any single-year move before 2015. Context, Claude Code to verify from Baseball
  Reference: the Cubs' records in 2010 through 2014 and attendance.
- Ownership: the Ricketts family took control in late 2009. ABC7 (November 16, 2015)
  reported the 2016 increase as the first significant one of the Ricketts era. That
  matches these invoices.

## 3. Six years at 6.4% a year above inflation, 2015 to 2021

- Real: $26,750 to $38,751, up 44.9%, 6.4% a year. CPI ran 2.3% a year, about what it
  ran in 2004 to 2015. Inflation doesn't explain the change.
- Year by year, nominal: 2016 +15.1%, 2017 +8.1%, 2018 +8.4%, 2019 +4.9%, 2020 +8.2%,
  2021 +8.3%.
- 2016 against what the Cubs announced (ABC7, November 16, 2015): average increase 10.4%;
  club box infield 12.8%; the Cubs cited the 97-win 2015 season. My seats rose 15.1%
  ($23,398 to $26,924.80, both exact). The tier name for Section 105 isn't recoverable:
  the Cubs moved to pricing games by tier (premium, standard, value; exact names not
  recalled), so compare only to the announced average and say why.
- What happened in those years, as timeline, not cause: 97 wins and the NLCS in 2015,
  the World Series in 2016, the 1060 Project renovation (Claude Code to date from primary
  reporting), Marquee Sports Network's launch in 2020.
- Judgment, labeled: the price followed winning up and didn't come back down. The
  invoices can show the timing. They can't show the reason.

## 4. 2020

- Billed $35,790, up 8.2%, for a season played without fans. Refunded.
- My experience: the first batch of refunds arrived within 30 days, which matches the
  Cubs' published terms for April through June cancellations (credit card within three
  weeks, check within four; Bleed Cubbie Blue, June 11, 2020). Everything after that
  took many months. No exact dates; say "many months, by my account."
- Claude Code: look for reporting on the Cubs' refunds for July through September 2020
  games and the remaining balance, to see whether the published terms covered them.
- One documented difference: credit bonus for keeping the money with the team. Cubs 5%;
  Braves, Red Sox, and Dodgers 10% (TicketNews, May 1, 2020). Friends' faster refunds at
  other clubs are anecdote; include only as "friends who held seats elsewhere told me,"
  or leave out.

## 5. Why I stopped

- Short, Matt's voice. Gave up the seats in 2022 after 24 years. Total paid, 1998 to
  2021: $491,330.80 before refunds, plus $15,940 in playoff tickets. **Matt: OK to
  publish the total?**

## 6. Where this money goes, and the lockout

- Season tickets are local revenue. Under the current CBA, each club pools 48% of net
  local revenue and the pool is split equally (**Claude Code: verify against the CBA's
  revenue sharing article; Insider Sport, June 2, 2026, is secondary**).
- The owners' May 28, 2026 proposal: $245.3 million cap, $171.2 million floor, 50/50
  split with players. The fight is over the player share. The fan's side of the ledger
  isn't on the table.
- Sets up the next piece: does a salary cap make a franchise worth more (NHL after 2005).

## 7. What would make this wrong

- One set of seats isn't the market. A fan in the bleachers or the upper deck saw a
  different path; the 2016 announcement shows increases by tier varied from 12.8% to
  43.3%.
- Rounding before 2016 blurs single years.
- The Cubs re-tiered sections over this period (2016 added "terrace box corner"). If
  Section 105 was reclassified, part of a jump is a tier change, not a price change.
- 2020 and 2021 per-game cost is distorted by the shortened, fanless 2020 season and
  capacity limits early in 2021.

## 8. What this predicts (Matt picks one)

- The Cubs' 2027 season-ticket renewal prices go up even with a lockout threatening the
  season, and the renewal terms say nothing about refund timing for canceled games.
  Checkable when renewals go out.

## 8b. The data

`data/cubs-season-tickets.csv` (invoices, precision flagged per row) and
`data/cpi-u-annual.csv` (BLS). Script computes every figure above.

---

## Figures (3 to 4)

- fig-01: price per seat, 1998 to 2021, nominal, two series with a visible break at 2004
  (Section 213, then Section 105). Shows the seat change honestly.
- fig-02: Section 105 four-seat total in 2021 dollars, 2004 to 2021, with 2015 marked
  and the two real growth rates labeled (1.1% and 6.4% a year). The picture.
- fig-03: annual nominal price change against CPI change, bars by year, 2005 to 2021.
- fig-04 (optional): the 2016 increase: my seats 15.1%, Cubs average 10.4%, club box
  infield 12.8%, as a graphic.
- Cover: fal.ai, house template.

## Open for Matt

Resolved October 3, 2026: pre-2015 figures rounded (dips are rounding), Section 105 tier
not recoverable, 2015 exact at $23,398, 2020 first batch within 30 days and the rest
many months later, total OK to publish.
