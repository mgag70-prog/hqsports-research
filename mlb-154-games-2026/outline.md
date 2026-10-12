# Outline: MLB's 154-game proposal (working, October 9, 2026)

Status: research done October 9 (morning). Draft Sunday, October 11. Computations in model/compute_notes.txt. Second piece in the lockout series after the season-ticket survey.

## The question
MLB proposed on October 8 to cut the regular season from 162 to 154 games from 2029, add a Monday national TV window, expand the Division Series to best-of-seven, and let top seeds pick opponents from 2027, all contingent on a salary cap. Who gives something up, and who gets something?

## Facts in hand (sources in the lockout memo and below)
- Proposal: MLB.com (Feinsand), AP, Forbes (Maury Brown), October 8, 2026. Salaries not cut; bonus and option thresholds prorated. Monday off except 1-2 national games. 4 split doubleheaders per team. Season ends a week earlier. Division Series best-of-seven from 2029, up to 8 more postseason games. MLBPA: every proposal contingent on a cap.
- History (SABR, "Schedule Changes Since 1876"): 154 games standard 1904-1960; 162 arrived with expansion (AL 1961, NL 1962). In 1946 owners floated 168 games partly to pay for player pension concessions; dropped after "heavy opposition from the public and the players."
- 2026 attendance, all 30 clubs (Baseball-Reference, data/attendance-2026-bref.csv): 71,752,722 total; 29,540 per game; every club had 80 or 81 home dates.
  - 4 fewer home dates at 2026 per-game attendance = 3,545,372 tickets league-wide, 4.94% of the season's gate count.
  - Dodgers lose 199,220 tickets; Athletics 39,468.
- Gate per home game, 2024, from MLB's internal gate report (Sportico, 2025): Dodgers $4.29M, Yankees $4.11M, Cubs $3.25M, Red Sox $2.93M, Astros $2.69M; bottom of the league about $500,000. So 4 home dates: Dodgers ~$17.2M, Yankees ~$16.4M, Cubs ~$13.0M, bottom clubs ~$2M (2024 dollars; gate only, before concessions and parking).
- Postseason gate and players (MLB.com glossary, "Postseason Share"): the players' pool gets 60% of gate from only the first three Division Series games and first four LCS and World Series games. Games 4 and 5 of a Division Series already fund no player pool; the proposed games 6 and 7 would add more gate outside the pool unless the CBA changes that rule. VERIFY whether the rule is in the CBA text and whether MLB's proposal changes it.
- Pay per game: salaries unchanged over 154 games = 162/154 = 5.2% more per game played.
- Revenue sharing: clubs pool 48% of net local revenue (gate is local). National TV and postseason money are central.

## Research added October 9 (morning)
- Sportico gate source: Kurt Badenhausen, Sportico, May 30, 2025, from MLB's internal gate report (2024 season). No league-total gate published there; only top five per-game figures plus "around $500,000 per game" at the bottom. Do not invent a league total; use the range.
- Postseason gate split (FanGraphs, Wendy Thurm, October 7, 2014, describing CBA rules): Commissioner's Office takes 15% of all postseason ticket revenue. Division Series Games 1-3: 60% players' pool, 25% to the two clubs. Division Series Games 4 and later: 0% pool, 85% to the two clubs. Same pattern for LCS and World Series after Game 4. Sportico (December 2025) confirms the 2025 pool is 60% of gate from the minimum games per series (two Wild Card, three DS, four LCS, four WS). VERIFY the 2022-26 CBA text if reachable; otherwise attribute to these two sources.
- 2025 players' pool: $128.2M (2024: $129.1M), Sportico December 2025. Implied gate from the 32 pool games: $213.7M, about $6.68M a game (ESTIMATE, average across rounds).
- Up to 8 added Division Series games (Games 6-7 in each of 4 series) at that average: about $53.4M of gate if every series went seven, 85% to clubs, 15% to the Commissioner, nothing to the players' pool under the current split. Realistically far less: only series that go long play Games 6-7.
- Compare: 4 lost home dates cost the Dodgers about $17.2M of gate on their own (2024 basis). The postseason add-back for all 30 clubs combined, in the best case, is about three Dodger-sized losses. The gate does not pay for the cut; TV has to.
- National TV now (all expire after 2028): Fox $728.6M/yr (2022-28), Turner $535M/yr (2022-28), ESPN ~$550M, NBC ~$200M, Netflix ~$50M (2026-28) = about $2.06B a year listed (Apple not verified, excluded). Boardroom (Shlomo Sprung, November 26, 2025): MLB will have "every single possible game up for bid" from 2029; Manfred would like to "nationalize" local rights too (author's reading). The 154-game start year matches that reset.
- Dollar value of a Monday national window: no reported figure found. Say so; don't estimate.
- 1961-62: SABR says only that expansion brought the 162-game schedule; no solid source yet on revenue motive. Keep to the SABR line plus the 1946 168-game episode.

## Angle
Eight fewer games is 3.5 million fewer tickets. The plan trades local gate, which clubs share at 48%, for national TV inventory (Mondays) and postseason games, which MLB sells centrally. Fans with plans lose 4 dates and nobody has said the price drops. Players keep their salaries and gain rest days but MLB tied it all to a cap.

## Still needed (as of October 9 morning; items 1-4 done or ruled out above)
1. League-total gate revenue (a recent year) to put the 3.5M tickets in dollars at the league level. Candidates: Forbes team revenue detail, Sportico, MLB statements.
2. Value of a national Monday window: any reporting on what the 2029 national deals are expected to bring, or what a comparable window sells for (NFL Monday Night Football, NBA).
3. Postseason gate per game (e.g., recent Division Series and LCS gate totals from MLB's postseason share releases) to size what up to 8 added games are worth.
4. Whether the 2022-26 CBA sets the players' pool games (Article VII?) and whether the proposal addresses it.
5. The 1961-62 change: contemporary reasons (expansion revenue, Maris asterisk) if a source is solid.
6. Season-ticket pricing: any club statement on 2029 plan pricing (expect none; say so).

## Figures (draft ideas)
- fig-01: 30 clubs, tickets lost from 4 home dates at 2026 attendance (bar, sorted).
- fig-02: what moves where: gate (local, shared 48%) down; national TV and postseason (central) up. Simple flow or two-column table.
- fig-03: postseason games by round now vs proposed, marking which games fund the players' pool.
- fig-04: schedule length 1904-2029 (154, 162, 154 proposed), with 1972 and 1981/1994-95/2020 short seasons marked.
