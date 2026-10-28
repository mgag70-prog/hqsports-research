# Outline: mlb-2027-cap-2026

Working H1: "The Dodgers are already $133 million over a 2027 salary cap, before they sign anyone."
Alt H1: "Five teams are over the owners' 2027 cap on contracts they've already signed."
Cover line (verbatim in draft): "Over the cap. Before the offseason."
Publish: Wednesday Oct 28, 2026. Series: follows the floor piece (both World Series clubs under the floor). The floor piece looked backward at 2026; this one looks at the money already committed to 2027, the first year of the owners' proposed cap.

All numbers: model/recompute.py (all checks pass). Basis: Spotrac 2027 projected luxury-tax payrolls (fetched Oct 27), which include player benefits ($18.5M), minor league and the pre-arb bonus pool. AP (Oct 24) says the owners' cap is "based on luxury tax payroll figures," so this is the right basis.

Two measures, always label which:
- Signed basis = guaranteed contracts + fixed items (benefits, minor league, bonus pool). No projections. Conservative.
- Projected = signed basis + Spotrac's projected arbitration and pre-arbitration salaries.

## Dek
The owners' proposed 2027 cap is $245.3 million. On contracts already signed, five clubs are over it. Add the arbitration raises Spotrac projects and it's eight, a combined $539.1 million over, before a single free agent signs this winter.

## Construction note (short, italic)
Spotrac projections as of Oct 27; arbitration figures are Spotrac's estimates, not awarded salaries. Rosters are incomplete (offseason), so payrolls will rise; that only widens the gaps at the top. Nobody has said how the proposal treats contracts already signed; this piece shows the size of the problem, not the rule that would solve it.

## 1. The Dodgers (fig-01)
- Guaranteed contracts alone: $355.84M, $110.5M over the cap before benefits.
- Signed basis $378.76M ($133.5M over); projected $393.81M ($148.5M over).
- Two players: Tucker $57.195M + Ohtani $46.08M (luxury-tax AAV, deferral-adjusted) = $103.28M, 42% of the cap. Tucker alone is 23.3% of it. [compute in script]

## 2. Everyone over the line (fig-02, all 30, two bars or bar + marker)
- Signed basis over cap: LAD (+$133.5M), PHI (+$41.9M), NYY (+$41.6M), NYM (+$31.5M), SD (+$1.2M). Total $249.6M.
- Projected adds BOS (+$45.8M), HOU (+$45.4M), TOR (+$9.9M): 8 clubs, $539.1M over.
- Ties to MLB's own count: MLB said 8 clubs' payrolls would decrease under the cap (per Pitcher List, June). The projected count is 8 too.

## 3. Contracts the proposal wouldn't allow (fig-03)
- Proposed limits (CBS June 25; AP Oct 24; Sportsnaut June 26): free agent changing teams, 5 years at 15% of the cap ($202M); re-signing "Cornerstone," 6 years at 16% ($265M); 5% raise cap; deferrals banned on new deals; max rules apply to free-agent years only.
- 15% of the 2027 cap is $36.795M; 16% is $39.248M.
- 8 players' 2027 luxury-tax figures are above 15%: Tucker $57.195M, Soto $51.0M, Ohtani $46.08M, Bellinger $44.75M, Bichette $42.0M, Wheeler $42.0M, Judge $40.0M, deGrom $37.0M. 7 are above 16% (all but deGrom).
- 18 contracts still running in 2027 are larger in total than $265M, the biggest deal the proposal would allow; Soto's $765M is 2.9 times it. [compute ratio in script]
- Careful: the proposal's max rules may not apply retroactively; Sportsnaut says existing deferrals are grandfathered. Say plainly that nobody has said what happens to these contracts.

## 4. The only precedent
- NHL 2005: when the league added a cap, every existing contract was cut 24% (from the cap-valuations piece). That's the one time a major league put a cap over contracts already signed. Don't predict MLB does the same; say what the precedent was.
- The question the owners' proposal hasn't answered publicly: grandfather (cap doesn't bite for years, Pitcher List's guess), roll back (NHL), or force trades/releases.

## 5. Bottom of the table, briefly (honest note)
- 12 clubs project under the $171.2M floor for 2027 right now (offseason, incomplete rosters). The Rays (projected $163.12M) still are; the Brewers' projected $192.41M is now above the floor, mostly on $58.0M of projected arbitration raises. Tie to the floor piece prediction honestly: the Brewers may clear the floor through arbitration alone. Note it as a point against the floor-piece prediction, not for it.

## 6. Quotes (attributed, short)
- Meyer: the cap proposal is a "nuclear bomb" (AP, Oct 24).
- Manfred: "Once every 40 years is not enough." (RG, Oct 24) on a small-market World Series; and "it's just that it's pretty rare" (AP).

## 7. Prediction on the record [MATT TO CONFIRM]
If the next agreement includes a hard cap, it includes a transition rule for contracts signed before it (grandfathering, a phase-in, or a rollback), and no club is forced to release a player to get under the cap in its first season. Checkable when the agreement's terms are published.

## Figures (house style; SVG + 1200px PNG; assert against data, draft, captions)
- fig-01: Dodgers 2027 stack: guaranteed (Tucker, Ohtani, rest), fixed items, projected arb/pre-arb, against the cap line.
- fig-02: all 30 clubs 2027 signed basis (solid) and projected (outline/marker), cap and floor lines; over-cap clubs labeled.
- fig-03: the 8 players above 15% of the cap, bars vs 15% and 16% lines.
- fig-04: 18 contracts above $265M vs the $265M max line (horizontal bars).

## Disclosure
Cubs: 2027 projected $209.35M, under the cap. One line only if relevant; per the published Wrigley piece Matt paid for the same four Wrigley seats for 18 years. Nothing else about Matt.

## Open at publication
- World Series status (Game 1: Brewers 3-2 on Oct 23). [UPDATE]
