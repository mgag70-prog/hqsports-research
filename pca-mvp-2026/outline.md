# Outline: Pete Crow-Armstrong's MVP season, and what it does to the extension math

Follow-up to "The Cubs Saved $29 Million on Pete Crow-Armstrong. Not $206 Million."
(Signal Hunter, September 14, 2026; cross-posted to Ledger & Whistle September 25, 2026).
Publication: Ledger & Whistle. Target: Monday, September 28, 2026, before the playoffs
open Tuesday.

Folder: `pca-mvp-2026/`. The model lives in `pca-extension-2026/model/` and is imported,
not copied. Model figures below were run September 28, 2026 by importing
`pca_sensitivity.run` at $9.0M per win and 100% capture. **All figures are provisional
until Claude Code recomputes them.**

---

## Working title options (Matt picks, Claude Code may propose better)

1. If Pete Crow-Armstrong were still the 2025 player, his extension would break even.
   He isn't.
2. Pete Crow-Armstrong's MVP season earned the Cubs nothing under his contract. It
   changed what they think they own.
3. The Cubs didn't get a dollar from Pete Crow-Armstrong's MVP year. They got an answer
   to the one question the extension depended on.

Subtitle direction: the season can't pay the Cubs directly because the contract starts in
2027. What it does is settle the input the September 14 model was most sensitive to.

---

## Construction note (up top, italic, like the other pieces)

- The model is the one published September 14, unchanged. Only the true-talent input
  moves. Every other assumption stays: $9.0M per win in 2027 inflating 3%, 6% discount
  rate, arbitration at 25/40/60% of open-market value, 2027 pre-arbitration salary of
  $1.0M, a hypothetical eight-year free agent deal for ages 29 through 36 at 100%
  capture, and the same aging curve.
- WAR scale: FanGraphs throughout, matching the September 14 piece, which cited his
  FanGraphs WAR. The 6.5 was a judgment-based regressed true-talent estimate, not a
  figure from any source, and the September 14 record doesn't tie it to a WAR scale.
  Say that plainly. Baseball Reference WAR appears once, for contrast, labeled, never
  blended.
- Season stats: Baseball Reference, final, page updated September 27, 2026, 11:50 PM.
  FanGraphs WAR, final, read September 28, 2026.

---

## 1. The season (short, facts only)

- Final line (Baseball Reference): 162 games, 726 PA, .280/.372/.570, 45 HR, 107 RBI,
  119 runs, 41 SB, 7 CS, 156 OPS+.
- 45 home runs tied Kyle Schwarber for the major league lead (AP, September 27, 2026).
- First 40/40 season in Cubs history and the seventh in MLB history, reached September
  24 against Miami, the night the Cubs clinched a postseason berth.
- fWAR by season (FanGraphs): 2024 2.6, 2025 5.4, 2026 10.6. 2026 components: Off 57.7,
  Def 23.2, BsR 8.3.
- Sunday: singled to open the finale and was pulled for a pinch runner.
- Optional, only if re-verified against final FanGraphs leaderboards: MLB.com (September
  15) cited a 3-fWAR gap over the No. 2 player, the first in 70 years.

One tight paragraph and a small stat block. Everyone ran the 40/40 story Thursday. It
isn't the point of this piece.

## 2. What the season is worth under the contract: nothing

- The extension covers 2027 through 2032. This season was paid at the pre-arbitration
  rate, extension or not.
- MVP escalators are keyed to 2027 through 2031 voting (contract details reported by Bob
  Nightengale, March 2026). A 2026 MVP triggers nothing.
- Escalator schedule: 2031 base rises $2,000,000 for each MVP in 2027 through 2030; 2032
  base rises $2,000,000 for each MVP in 2027 through 2031. Lesser amounts for 2nd
  through 10th ($1,000,000 for 2nd or 3rd, $750,000 for 4th or 5th, $500,000 for 6th
  through 10th).
- Maximum exposure, winning every MVP he can: $8,000,000 added in 2031 and $10,000,000
  in 2032. Present value to 2026 at 6%: $13.0M. The September 14 model left escalators
  out; this sizes what that could cost at most. **Claude Code: recompute with the
  model's own `pv()`.**

The point to land: the Cubs already paid for this season, at the pre-arbitration rate.
What the season buys them is information.

## 3. What it changes: the one input that matters

The September 14 piece showed extension savings are most sensitive to true talent.
Re-run at four readings:

| Reading (fWAR) | True talent entering 2027 | Extension savings (NPV) | Surplus value (NPV) |
|---|---|---|---|
| His 2025 season | 5.4 | $0.1M | $153.7M |
| September 14 base case | 6.5 | $28.6M | $205.9M |
| Two-season average of 5.4 and 10.6 | 8.0 | $68.0M | $277.1M |
| 2026 taken at face value | 10.6 | $136.4M | $400.6M |

Breakeven, savings of exactly zero: 5.397 of true talent.

The mechanism, from the same run: the counterfactual free agent AAV for 2031-32 rises
from $24.4M at 5.4 and $36.5M at 6.5 to $53.4M at 8.0 and $82.7M at 10.6. A better
player costs more in arbitration and far more as a 2031 free agent, and the extension
fixed both prices in March.

**Claude Code: generate this table from `run()`, never hand-type it.**

## 4. The breakeven is his 2025 season (the strongest point; judgment labeled)

- The extension's breakeven, 5.397, is his 2025 season on FanGraphs. If he were exactly
  the 2025 player for the next six years, the deal would be a wash: $0.1M. Every win of
  true talent above that is savings, roughly $26M to $27M per win in this range.
  **Claude Code: verify 5.397 by bisection and compute the per-win slope from the
  table.**
- Don't overstate the match. 5.4 against 5.397 is a coincidence of the model's inputs,
  not something anyone designed. Say so.
- Before this season, whether he was better than his 2025 was the whole question. This
  season is the evidence that he is.
- Why not just plug in 10.6 (judgment, labeled): one season is a sample, not true
  talent. The September 14 model regressed on purpose. The two-season average is plain
  arithmetic, not a projection system. The 10.6 row is a ceiling, shown for range, not
  a forecast.

## 5. Where the savings still come from

Same structure as September 14: savings live in arbitration and the two bought-out free
agent years, not in 2027, which remains a loss because the extension pays $10M against a
$1.0M renewal. **Claude Code: recompute the control-years and free-agent-years split at
8.0 and state whether the arbitration-first finding still holds.**

## 6. What would make this wrong

- WAR definitions. On Baseball Reference's scale his seasons are 5.9 and 9.8, a
  two-season average of 7.85 and savings of $64.0M. The breakeven point is weaker on
  that scale because 2025 clears 5.397 by half a win. Mention once so no reader thinks
  the scale was shopped.
- Aging curve. The model's curve declines after 27, steeper than a slugger's, because
  his value leaned on defense and speed. With 45 home runs and Off of 57.7, more of the
  value is now the bat, which may mean the curve is too steep and the savings are
  understated. Judgment.
- The labor regime. The owners' proposed $245.3M cap for 2027 would reset dollars per
  win and the free agent counterfactual at once. The CBA expires December 1, 2026,
  11:59 p.m. ET. Link the 1994 base-rate piece.
- Injury and the career-ending tail are in the Monte Carlo, not the deterministic table.
  Optional: rerun the Monte Carlo centered on 8.0 and report the median and the share of
  paths with positive savings. **Only if Claude Code runs it; don't estimate.**

## 7. What this predicts

His 2027 fWAR. At or above 6.5, the September 14 base case was conservative and the
savings are larger than published. At or below 5.4, the extension is roughly a wash and
2026 was the outlier. Checked against the 2027 final line, here. Add to the predictions
log.

## 8. The data

Same model, same repo, one new input. Link `pca-extension-2026/` and the new
`pca-mvp-2026/` folder with the script that produced the table. Credit Adam Niedbalski's
September 14 piece again as the original prompt.

---

## Figures (propose forms first, as usual)

- fig-02: extension savings as a function of true talent (fWAR), one line across
  roughly 4 to 11, a zero line, the 6.5, 8.0, and 10.6 readings marked, and his 2025
  (5.4) and 2026 (10.6) seasons marked on the talent axis. 2025 landing on the zero
  crossing is the picture.
- Cover: adapted from fig-02. 2025 at the zero line, 2026 far up the curve.

## Resolved before drafting

1. Final WAR from both sources, pulled September 28, 2026.
2. WAR scale: FanGraphs, matching the September 14 piece. The 6.5's scale was never
   recorded; the construction note says so.
