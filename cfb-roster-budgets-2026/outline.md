# Article outline: money and results in the 2026 roster budget data

Working titles, each built on the finding rather than the anecdote:

1. Every one of the ten biggest rosters in college football is ranked. Below
   that, the money stops explaining anything.
2. Two conferences have a spending gap. Two conferences have one rich school.
3. Houston is ranked 22nd with the 61st biggest roster in college football.

Lead with 1 or 2. The Houston line is the sharper hook, but it shrinks the
whole piece to one team, and the piece isn't about one team.

---

## Section 1. The construction note, up top

Same placement as the SEC piece. This isn't a filings dataset, and the piece
has to say so before it says anything else.

- Source is The Athletic, published September 16, 2026, by Stewart Mandel,
  David Ubben, Sam Khan Jr. and the Athletic Colleges Team.
- Built from more than 70 sources: coaches, general managers, personnel
  directors, athletic directors, agents. At least one employee at every school
  was contacted.
- The Athletic states its own bias corrections, and I'd quote them rather than
  paraphrase, since it's rare for a survey piece to admit this much: coaches
  undersell their budgets, administrators oversell them, and everyone inflates
  what they think rivals are spending. The Athletic says it discounted
  rival-sourced figures for that reason.
- Figures cover money available to build the 2026 roster: athletic department
  revenue, revenue sharing, and booster or collective money. They exclude
  player income the program doesn't control, like national brand endorsements.
- Every published number is a range. Any midpoint in this piece is mine, not
  theirs.
- AP rankings are as of September 13, 2026.

Then say it in one sentence: this is an estimate dataset, not an audited one,
and everything below should be read at that confidence level.

## Section 2. At the top, money works perfectly

The finding, stated flat: all ten of the largest roster budgets belong to AP
ranked teams. No exceptions.

| School | Budget | AP |
| --- | --- | --- |
| Ohio State | $49-54M | 6 |
| Oregon | $48-54M | 21 |
| Texas | $45-55M | 1 |
| LSU | $47-50M | 7 |
| Texas A&M | $45-50M | 9 |
| Miami | $44-50M | 5 |
| Notre Dame | $41-48M | 3 |
| Ole Miss | $39-45M | 8 |
| Tennessee | $41-43M | 15 |
| Alabama | $38-42M | 10 |

Ranked teams average $35.5M and unranked teams average $22.4M, which is a
$13M gap on midpoints, and it's real.

Don't overclaim causation. The honest version is that the correlation at the
top is perfect in this one snapshot, and the reason to lead with it is that
it falls apart so quickly once you look past the tenth row.

## Section 3. Where it stops working

Of the 25 largest budgets, only 18 belong to ranked teams.

Seven teams spend top-25 money without a ranking to show for it. Five of
them, Florida through Clemson, are programs that don't usually go unranked;
Wisconsin and UCLA are on the list for the money alone. Call that a judgment
about the five, not a measurement:

- Florida, $31-41M, 15th in spending
- South Carolina, $32-35M, 16th
- Auburn, $31-35M, 17th
- Nebraska, $31-35M, 18th
- Clemson, $29-32M, 22nd
- Wisconsin, $27-31M, 23rd
- UCLA, $26-30M, 25th

Run it the other way and seven ranked teams sit outside the top 25 in
spending:

- BYU, AP 11, budget rank 41 of 68
- SMU, AP 16, rank 44
- Utah, AP 17, rank 51
- Iowa, AP 18, rank 55
- Houston, AP 22, rank 61
- Louisville, AP 23, rank 34
- Virginia, AP 25, rank 43

Houston is the extreme: 22nd in the country on the 61st largest roster budget
of 68.

Give Iowa its own beat. Ferentz builds from the offensive and defensive lines
out, keeps players on campus instead of reloading through the portal, and
has had 43 linemen drafted since 2000; the data shows that model still
producing a ranked team on a budget in the bottom fifth of the power
conferences. Ferentz material comes from CBS Sports, August 24, 2026, Brandon
Marcello.

## Section 4. The part nobody is separating

This is the argument, and it gets the most room.

The Athletic describes the ACC as a league with little separation in roster
cost. Measured by raw spread, the ACC is the widest conference in the
country: $36.5M top to bottom, against $33.5M in the Big Ten.

Both statements are true. Pull the single biggest spender out of each
conference and you can see why:

| Conference | Full spread | Minus top spender | Who that is |
| --- | --- | --- | --- |
| ACC | $36.5M | $20.0M | Miami |
| Big 12 | $25.0M | $8.5M | Texas Tech |
| Big Ten | $33.5M | $33.0M | Ohio State |
| SEC | $26.5M | $25.0M | Texas |

Standard deviation says the same thing. The ACC drops from $7.9M to $5.1M
without Miami and the Big 12 from $6.0M to $2.8M without Texas Tech, while
the Big Ten barely moves, $10.4M to $9.0M without Ohio State.

So: two different competitive structures wearing one label. The ACC and the
Big 12 are compressed fields with one rich outlier apiece. The Big Ten and
the SEC are stratified, a tier sitting on top of a tier. A conference where
one program is rich isn't the same problem as a conference where a third of
the league is, and nobody talking about spending gaps is drawing that line.

Use the Big Ten to show it. Ohio State at $49-54M and Oregon at $48-54M are a
tier rather than an outlier, and the fall from there to Purdue at $16-20M is
the widest functional range in the sport.

## Section 5. What would make this wrong

Mandatory, same as the previous pieces.

- These budgets are survey estimates. Other outlets polling other panels
  produced different figures for the same programs this year, and if The
  Athletic's panel skewed, every ratio here skews with it.
- AP rank on September 13 is two weeks into a season and still mostly
  preseason expectation. It's closer to a measure of what people expected
  than of what has happened, and that is the single largest weakness in the
  piece. Say it in those words.
- One season, one snapshot. A perfect top ten could be a coincidence of one
  year.
- Midpoints come from published ranges. Texas at $45-55M or Florida at
  $31-41M carries more uncertainty than the midpoint lets on.
- Texas Tech's figure reportedly doesn't reflect the roughly $3-4M freed when
  quarterback Brendan Sorsby left mid-2026. That matters because the Big 12
  finding in section 4 rests on Texas Tech.

## Section 6. What this predicts

Same convention as the SEC piece. If the reasoning holds, it should say
something checkable in advance.

If money mostly buys the top and explains little below it, the seven unranked
big spenders shouldn't converge on the ranked group as the season goes on,
and at least some of the seven cheap ranked teams should still be ranked in
December. If instead the big spenders climb and the cheap teams drop out by
November, then the September snapshot was measuring preseason expectation
and nothing structural, and this piece was built on noise. Commit to that in
print and revisit it when the season ends.

## Section 7. The data

Link the committed CSV in hqsports-research at
`cfb-roster-budgets-2026/data/cfb-roster-budgets-2026.csv`, with the README
carrying the source and the caveats. Same invitation as the SEC piece: take
it and check the work.

---

## Voice and standards

- No em dashes.
- Exact numbers, never rounded, except when quoting an announced figure.
- Contractions. US spelling. Dates as Month Day, Year.
- Judgments labeled as judgments, not measurements. The two-structures
  argument in section 4 is a judgment about what the spread means; the spread
  itself is arithmetic.
- Every stat traces to a named source with an as-of date.
- First-person admissions of uncertainty are deliberate. The estimate-versus-
  filing distinction is the most important one in the piece.
- Structure and facts from Claude, words from Matt. This is a spine for a
  voice pass, not a draft.
