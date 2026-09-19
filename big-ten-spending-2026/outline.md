# Article outline: Big Ten roster spending against two years of results

Second piece off the `cfb-roster-budgets-2026` dataset. The first covered all
68 teams and argued money buys the top of the sport and explains little below
it. This one tests that inside one conference with the records attached, and
the result is sharper than the national version.

NFL pipeline angle deliberately excluded, held for a later piece.

## Working titles

1. In the Big Ten, money explains the top three teams and the bottom one. For
   the other fourteen it explains nothing.
2. Illinois has the fourth-best record in the Big Ten and the fourth-cheapest
   roster.
3. Penn State had the fifth-best record in the conference and paid about $50
   million to fire the coach who produced it.

Number 1 is the actual finding. Number 3 is the sharpest single fact.

---

## Section 1. Construction note, up top

- Budgets: The Athletic, September 16, 2026, Stewart Mandel, David Ubben, Sam
  Khan Jr. and the Athletic Colleges Team. More than 70 sources, with stated
  bias corrections: coaches undersell, administrators oversell, rivals inflate
  each other. Every figure is a range; midpoints are calculated here.
- Records: Sports Reference conference standings for 2024 and 2025, combined,
  including bowl and playoff games.
- Power 4 record is a secondary cut of the same two seasons, computed here
  game by game rather than taken from a source. **Footnote the definition,
  because it changes the answer:** Power 4 means ACC, Big Ten, Big 12, and SEC
  opponents plus Notre Dame. Conference championship and College Football
  Playoff games against those opponents count. Oregon State and Washington
  State do not count, since neither is in a Power 4 conference after
  realignment. A different set of choices produces a different table, so the
  choices are stated rather than assumed.
- **The timing problem, stated before any finding.** These are 2026 roster
  budgets against 2024 and 2025 results. Revenue sharing began in July 2025,
  so for most of the measured window the system that produced these budgets
  did not exist. The claim is not that 2026 money produced 2024 wins. The
  claim is that the conference's current payroll order and its recent results
  order agree at the extremes and nowhere else. Causation stays open.

## Section 2. The full table

Two-year record, 2024 and 2025 combined, against payroll rank of 18.

| # | Team | 2-yr | Win% | Budget | Payroll rank |
| --- | --- | --- | --- | --- | --- |
| 1 | Indiana | 27-2 | .931 | $36-40M | 4 |
| 2 | Oregon | 26-3 | .897 | $48-54M | 2 |
| 3 | Ohio State | 26-4 | .867 | $49-54M | 1 |
| 4 | Illinois | 19-7 | .731 | $19-23M | 15 |
| 5 | Penn State | 20-9 | .690 | $29-32M | 7 |
| 6 | Michigan | 17-9 | .654 | $36-40M | 5 |
| 7 | Iowa | 17-9 | .654 | $17-21M | 17 |
| 8 | USC | 16-10 | .615 | $37-40M | 3 |
| 9 | Minnesota | 16-10 | .615 | $18-22M | 16 |
| 10 | Washington | 15-11 | .577 | $21-25M | 13 |
| 11 | Nebraska | 14-12 | .538 | $31-35M | 6 |
| 12 | Rutgers | 12-13 | .480 | $20-23M | 14 |
| 13 | Northwestern | 11-14 | .440 | $21-25M | 12 |
| 14 | Wisconsin | 9-15 | .375 | $27-31M | 8 |
| 15 | Michigan St. | 9-15 | .375 | $21-25M | 11 |
| 16 | UCLA | 8-16 | .333 | $26-30M | 9 |
| 17 | Maryland | 8-16 | .333 | $21-25M | 10 |
| 18 | Purdue | 3-21 | .125 | $16-20M | 18 |

Penn State's 20-9 ranks below Illinois's 19-7 on win percentage despite more
wins, because it played more games. Say so in a line rather than leaving a
reader to wonder.

### The same two years, Power 4 games only

Raw record rewards a soft non-conference schedule. Illinois played Eastern
Illinois, Western Illinois, and Central Michigan across these two years;
Purdue played Indiana State and Ball State. Stripping those out is the obvious
check on whether the pattern above is real, and it mostly holds.

| # | Team | P4 record | Payroll rank | Gap |
| --- | --- | --- | --- | --- |
| 1 | Indiana | 21-2 | 4 | +3 |
| 2 | Oregon | 20-3 | 2 | 0 |
| 3 | Ohio State | 21-4 | 1 | -2 |
| 4 | Illinois | 14-8 | 15 | +11 |
| 5 | Penn State | 14-9 | 7 | +2 |
| 6 | Iowa | 13-9 | 17 | +11 |
| 7 | Michigan | 13-9 | 5 | -2 |
| 8 | Minnesota | 11-8 | 16 | +8 |
| 9 | USC | 13-10 | 3 | -6 |
| 10 | Washington | 9-10 | 13 | +3 |
| 11 | Nebraska | 10-12 | 6 | -5 |
| 12 | Northwestern | 7-11 | 12 | 0 |
| 13 | Rutgers | 7-13 | 14 | +1 |
| 14 | UCLA | 6-13 | 9 | -5 |
| 15 | Wisconsin | 5-15 | 8 | -7 |
| 16 | Michigan St. | 5-15 | 11 | -5 |
| 17 | Maryland | 3-16 | 10 | -7 |
| 18 | Purdue | 0-20 | 18 | 0 |

Ohio State has more Power 4 wins than Oregon but a lower win percentage, which
is why it sits third here. The table is ordered by win percentage throughout.

**Purdue is 0-20 against Power 4 opponents across two seasons.** Not one win.
That is a harder number than 3-21 overall and it makes the floor argument
without any interpretation attached.

This is also where Bielema's own claim gets checked. He said at Big Ten Media
Days that Illinois ranks fourth in the conference in Power 4 wins over two
years behind Indiana, Oregon, and Ohio State. Computed independently, that is
exactly right.

## Section 3. The correlation, and where it dies

The headline arithmetic:

- Across all 18 teams, the rank correlation between payroll and two-year
  record is 0.48. Positive, real, and modest.
- Remove the top three and Purdue, and the correlation for the remaining
  fourteen is **0.046**. That is nothing.
- Power 4 games only, the same test: 0.437 across all 18, and **-0.037** for
  the middle fourteen. Slightly negative, which in a sample this size means
  the same thing as zero. Taking the cupcakes out does not rescue the
  relationship.

The same thing in tiers:

- Top six by record: average payroll $38.3M
- Middle six: $25.8M
- Bottom six: $24.0M

The middle and the bottom of the Big Ten spend almost identically and are
separated by roughly four wins a season. The gap that matters is between the
top six and everyone else, not between the ninth-best team and the
seventeenth.

**The argument, and label it a judgment.** The Big Ten does not have a
spending-to-winning relationship. It has a threshold at the top, a floor at
the bottom where Purdue sits alone, and fourteen programs in between whose
payrolls tell you nothing about their records. What looks like a league-wide
correlation is three rich programs and one poor one doing all the work.

## Section 4. The programs that beat their payroll

Rank gap is payroll rank minus record rank. Positive means outperforming.

| Team | Record rank | P4 rank | Payroll rank | Gap (record) | Gap (P4) |
| --- | --- | --- | --- | --- | --- |
| Illinois | 4 | 4 | 15 | +11 | +11 |
| Iowa | 7 | 6 | 17 | +10 | +11 |
| Minnesota | 9 | 8 | 16 | +7 | +8 |

Three of the four cheapest rosters in the Big Ten are in the top nine by
record and the top eight against Power 4 opponents. The fourth is Purdue.

On Power 4 games Illinois and Iowa tie for the largest gap in the conference
at +11, which is worth saying plainly: the two programs that most outperform
their payroll are the 15th and 17th-largest payrolls in an eighteen-team
league.

**Lead with the tie.** On Power 4 games Illinois and Iowa share the largest
gap in the conference at +11, and they get there two different ways. Illinois
is a program that was not good and now is. Iowa is a program that has been the
same thing for 27 years. Both beat their payroll by the same margin, which is
the reason to treat this as a pattern rather than a story about one coach.

**Illinois gets the most room, because the change is the point.** 19-7 is a
program record across 133 years of Illinois football,
with back-to-back nine-win seasons for the first time. Bielema inherited a
program that had gone 17-39 under Lovie Smith from 2016 through 2020 and is
38-26 at Illinois, the second-best winning percentage in school history among
coaches with at least 50 games. Iowa and Minnesota are holding a level. Illinois
built one. Bielema was asked about
The Athletic putting him fourth-lowest at $19-23 million and said he had been
told the report came out but hadn't read it, so he didn't know whether it was
factual. That is the estimate caveat delivered by the subject of the estimate,
and it is worth more than any hedge the piece could write for itself. His
other claims check out: fourth-lowest by midpoint is right, and "half the Big
Ten is below $25 million" is exactly 9 of 18. One correction: he grouped
Nebraska with the $35 million-plus tier, but Nebraska is $31-35M, midpoint
$33.0M.

**Iowa is the stronger case and gets equal room.** 17-9 on the
second-cheapest roster in the conference, finishing above Michigan, USC,
Washington, and Nebraska over two years, in Ferentz's 26th and 27th seasons.
Illinois's run is new. Iowa's is the same thing it has been doing since 1999,
which makes it the better test of whether a cheap roster can hold position
rather than spike.

**What Bielema says the difference is, quoted not endorsed.** Players taking
less to stay, naming Te'Rah Edwards and an unnamed receiver he says had offers
for more money elsewhere. His framing of Josh Whitman's support. And the line
about trying to play by rules that he says don't always get obeyed nationally,
which is an allegation with nobody named: quote it, note it's unverifiable as
stated, build nothing on it.

**Minnesota is the third case and it should not be left as a table row.**
16-10 overall, eighth in Power 4 win percentage, 16th of 18 in payroll, a +8
gap. P.J. Fleck is in his tenth season and is the second-longest-tenured
active coach in the Big Ten behind Ferentz. Minnesota went 8-5 in both 2024
and 2025, which is the definition of holding a level rather than spiking.

Fleck responded to the same Athletic report Bielema was asked about, on his
radio show, and the quote is the Minnesota version of the same argument: if
you are not one of the teams with an accelerated amount of money, like the New
York Yankees, you have to get creative quickly and develop freshmen quickly.
He also described spending most of the roster budget on retention, naming the
players he wanted to keep. That is the same mechanism Bielema describes, from
a different program, unprompted, in the same week. Two coaches is not
evidence, but it is worth putting side by side.

**The pattern worth naming, and label it a hypothesis rather than a finding.**
The three programs that most outperform their payroll have the three longest
coaching tenures among them: Ferentz in his 27th season, Fleck in his tenth,
Bielema in his sixth. The three that most underperform it have all changed
coaches recently or are in the middle of doing so. Three teams is not a
mechanism, and continuity could as easily be a result of winning cheaply as a
cause of it. Say that, then put it on the table anyway, because it is the only
thing the three cheap overperformers visibly share.

**Competitive note, not for the piece.** The Star Tribune published a
cost-per-win analysis of Minnesota on roughly this subject in September 2026,
putting Fleck at about $5.1 million per win since 2017, fourth-lowest among
Big Ten public schools. Different method, different question, worth knowing it
exists before publishing.

## Section 5. The programs that lose to their payroll

| Team | Record rank | P4 rank | Payroll rank | Gap (record) | Gap (P4) |
| --- | --- | --- | --- | --- | --- |
| Wisconsin | 14 | 15 | 8 | -6 | -7 |
| Maryland | 17 | 17 | 10 | -7 | -7 |
| USC | 8 | 9 | 3 | -5 | -6 |
| UCLA | 16 | 14 | 9 | -7 | -5 |
| Nebraska | 11 | 11 | 6 | -5 | -5 |
| Michigan St. | 15 | 16 | 11 | -4 | -5 |

USC leads this section. Third-largest payroll in the Big Ten at $37-40
million, eighth-best record and ninth against Power 4 opponents. Nebraska is sixth in payroll and eleventh in
record, and has not posted a winning Big Ten record under Matt Rhule.

## Section 6. The firings came from the middle

Four coaching changes out of the 2025 season. One has to be excluded and the
exclusion stated: Michigan parted with Sherrone Moore **for cause**, over
credible evidence of an inappropriate relationship with a staff member, not
performance. It does not belong in a spending-and-results pattern.

The three performance firings:

| Program | Payroll rank | Record rank | What happened |
| --- | --- | --- | --- |
| Penn State | 7 | 5 | Fired James Franklin October 12, 2025 after an 0-3 Big Ten start; owed close to $50M |
| UCLA | 9 | 16 | Fired DeShaun Foster three weeks in at 0-3 |
| Michigan St. | 11 | 15 | Fired Jonathan Smith after 4-15 in two years |

None is a bottom-tier spender. Purdue, Iowa, and Minnesota, the three cheapest
rosters in the conference, all kept their coaches, and Iowa and Minnesota kept
theirs while finishing seventh and ninth.

**Penn State is the sharpest fact in the piece.** Franklin's teams went 20-9
across 2024 and 2025, fifth-best in the Big Ten, including a 13-3 season and a
College Football Playoff semifinal. He was fired seven games into 2025 and
owed close to $50 million. Penn State's entire 2026 roster costs $29-32
million.

The buyout exceeded the payroll. A program committed more money to stop
employing one coach than it committed to paying every player on the team, and
did it after two years that ranked fifth in the conference.

Label the comparison a judgment. Buyouts and roster budgets come from
different accounts on different schedules. Make the point anyway, because the
scale is real. Source the buyout figure to the Associated Press, October 12,
2025.

## Section 7. What would make this wrong

- Budgets are survey estimates, not filings. The coach at the center of the
  piece says he hasn't read the report and can't confirm it.
- The timing mismatch from section 1, restated plainly. Two of the four
  seasons predate revenue sharing.
- Two years is short. Illinois's 19-7 is a program record across 133 years,
  which is another way of saying it isn't the normal state of the program.
- The 2025 preseason media poll picked Penn State first, Ohio State second,
  Oregon third, Illinois fourth, Michigan fifth, Indiana sixth. Indiana won
  the national title and Penn State fired its coach in October. Expectation
  predicted poorly, which cuts against reading too much into any snapshot,
  this one included.
- A rank correlation on 18 teams is a small sample. The 0.046 figure for the
  middle fourteen is the absence of a relationship in this data, not proof
  that none exists.
- Bielema's roster-construction claims are unverifiable from outside the
  program.

## Section 8. What this predicts

If the threshold reading is right, the three top-payroll programs should stay
at the top in 2026 and Purdue should stay at the bottom, while the middle
fourteen reshuffle in a way payroll does not predict. Illinois, Iowa, and
Minnesota should not collapse toward their spending. If instead the middle
sorts itself by payroll this season, the pattern here was two years of noise.

Revisit at season's end and say which happened.

## Section 9. The data

Budgets in the committed CSV. A second file carries both seasons, the
two-year combined record, the Power 4 record, each rank, and the gap columns.
Coaching changes are not in either dataset; say where they came from. Restate
the Power 4 definition here so anyone recomputing it can match the method.

---

## Voice and standards

- No em dashes. Exact numbers, never rounded except when quoting an announced
  figure. Contractions. US spelling. Month Day, Year. Serial commas.
- Judgments labeled. The threshold argument in section 3 and the
  buyout-versus-payroll comparison in section 6 are judgments. The table, the
  correlations, and the rank gaps are arithmetic.
- Sources with as-of dates: The Athletic, September 16, 2026 for budgets;
  Sports Reference for standings; Associated Press, October 12, 2025 for the
  Franklin buyout; Michigan's own statement for the Moore language.
- Structure and facts from Claude, words from Matt.
