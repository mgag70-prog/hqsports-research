# College Football Roster Budgets, 2026 Season

## Source

*The Athletic*, "Does your college football roster cost $8M or $50M? Here's
our report on 68 teams." By Stewart Mandel, David Ubben, Sam Khan Jr., and the
Athletic Colleges Team. Designed and developed by Emily Giambalvo and Yuriko
Schumacher. Published September 16, 2026.

Retrieved via Nimble extraction and cross-checked against ten screenshots of
the interactive on September 16, 2026. The interactive's chart data does not
resolve to extractable text through Nimble, so the numbers in this dataset
were transcribed directly from the screenshots rather than pulled
programmatically. AP rankings are as of September 13, 2026, per the
interactive's own overlay.

## What these numbers are, and are not

This is not a filing-based dataset. It does not belong in the same
evidentiary category as the conference distributions data, which comes from
audited Form 990s. These are estimated ranges built from more than 70
sources: coaches, general managers, personnel directors, athletic directors,
and agents. The Athletic states its own bias-correction logic directly:

- Few people inside a program know the school's exact number, and many who do
  won't share it, even anonymously.
- Coaches tend to undersell their own budgets, to manage fan expectations or
  keep players from asking for more.
- Administrators tend to oversell, to look like effective fundraisers.
- Programs routinely inflate what they believe rivals are spending, to argue
  internally for bigger budgets. The Athletic says it weighted rival-reported
  figures more skeptically for this reason.

Every number in this dataset is a range, not a point estimate. `budget_mid_
millions` is the midpoint of that range, calculated here, not reported by the
source. The Athletic's own scatter chart plots this same midpoint under the
label "Middle of each team's estimated range."

The dollar figures represent money a school had at its disposal to build its
2026 roster: athletic department revenue, revenue sharing, and outside
booster or collective money combined. They explicitly exclude player income
the football program does not control or manage, such as national brand
endorsement deals.

## Coverage

68 teams: all Power 4 conference members plus Notre Dame. Group of 5 and FCS
programs are not covered by the source and are not in this dataset.

## Columns

| Column | Description |
| --- | --- |
| `school` | Team name as given by the source |
| `conference` | SEC, Big Ten, ACC, Big 12, or Independent |
| `budget_low_millions` | Low end of The Athletic's estimated range |
| `budget_high_millions` | High end of The Athletic's estimated range |
| `budget_mid_millions` | Midpoint, calculated as (low + high) / 2 |
| `ap_rank_2026_09_13` | AP Top 25 rank as of September 13, 2026, where applicable, blank otherwise |

## Known limits

- Conference averages reported by the source (SEC $33-38M, Big Ten $27-31M,
  ACC $21-25M, Big 12 $18-22M) are not a simple mean of the low or high ends
  in this file. The source does not disclose its exact averaging method, and
  a recomputation from this dataset should not be presented as matching the
  source's own stated average without flagging the difference.
- The source's playoff-odds breakdown (five buckets from "at least 50%" down
  to "less than 5%," each with an average budget range) is reported only as
  group averages with team counts, not as a per-team bucket assignment. This
  dataset does not attempt to infer which bucket an individual team falls
  into. Any piece that wants that mapping needs Austin Mock's underlying
  Playoff projection, not this chart.
- Texas Tech's estimate reportedly does not reflect the mid-2026 departure of
  transfer quarterback Brendan Sorsby, which the source says shaved
  $3-4 million off the program's effective spend this season.
- No number here is a payroll disclosure. Treat every figure as a
  triangulated estimate, current as of the September 16, 2026 publication
  date, not a stable or auditable fact.
