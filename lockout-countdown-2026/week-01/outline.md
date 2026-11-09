# Outline: lockout countdown, week 1 (publish Thursday Nov 5, 2026)

Series: "Lockout countdown", weekly through Dec 1 (week 2 Wed Nov 11, week 3 Nov 18, week 4 Nov 25). Each week: a "days left" line, what changed at the table, one new angle. Week 1 is a day late (the Nov 4 Note announced it); say it plainly in one line or not at all — Matt's call in the voice pass.

Working H1: "26 days left. The owners moved their salary cap to 2028, and it catches the same 20 teams."
Alt H1: "The owners delayed the cap a year. The new lines land on the same clubs."
Cover line (verbatim in draft): "26 days. Same lines."
Dek (<150 chars, Substack subtitle): "MLB's new offer pushes the cap to 2028. On this year's payrolls, it would hit the same eight clubs over and twelve under."

All numbers: model/recompute.py (all pass) over data/context.csv, mlb-floor-2026/data/2026-vs-cap-floor.csv (2026 luxury-tax payrolls) and mlb-2027-cap-2026/data/2027-vs-cap.csv (2027 Spotrac projections).

## 1. What changed on Tuesday (Nov 3)
- MLB proposed delaying the cap to 2028; CBT thresholds unchanged for 2027; other 2027 offer elements stay (ESPN, Passan).
- New 2028 lines: $258.2M cap (up $12.9M from $245.3M), $180.2M floor (up $9.0M from $171.2M); 50-50 split of projected 2028 revenue.
- New floor flexibility: a team could spend as little as 90% of the floor in a year ($162.18M) if it meets a multi-year minimum.
- $282M of CBT proceeds to players in cash (IRS limits present-day distribution to about $72M); $900,000 minimum (some $1M); $65M pre-arb pool; all contingent on a cap and floor.
- Union: opposes any cap; says players lose more than $1B; quote (short). Union's counter: $300M CBT threshold, $1.5M minimum, $180M pre-arb pool.

## 2. Same lines, same clubs (fig-01: 30 clubs, 2026 payroll vs 2028 cap/floor and 90% line)
- On 2026 luxury-tax payrolls, the 2028 lines put 8 clubs over and 12 under, exactly ESPN's count (ESPN said 12 under including the Brewers, 8 over). Our data reproduces it.
- Over: LAD, NYM, NYY, PHI, TOR, BOS, CHC, SD; $511.8M above in all. Under: MIL, CIN, ATH, PIT, COL, MIN, WSH, CHW, TB, STL, CLE, MIA; $656.3M below in all.
- The 90% flexibility doesn't change 2026's list: all 12 were below $162.18M too.
- Disclosure: Cubs are among the 8 (held Cubs season tickets 1998 to 2021).

## 3. On 2027 projections (fig-02, short)
- Spotrac's 2027 projections: 7 over the 2028 cap, 12 under the floor, 9 under the 90% line. Signed contracts alone already put the Dodgers, Yankees, Phillies and Mets over $258.2M; the Dodgers are projected $135.6M over.
- The Brewers: projected $192.41M for 2027, $12.21M above the 2028 floor, on arbitration alone. Ties to the Ledger "at risk" call; one line.

## 4. What December 2 freezes (fig-03: calendar strip Nov 2 to Dec 9)
- Calendar: free agency opened Nov 2, 5 p.m. ET; QO ($23.15M) decisions Nov 11-15; 40-man/Rule 5 protection 6 p.m. ET Nov 17; non-tender Nov 20; GM Meetings Nov 9-12 Las Vegas; CBA expires 11:59 p.m. ET Dec 1; lockout expected Dec 2; Winter Meetings Dec 7-9 San Diego (most expect cancellation); Rule 5 draft at risk.
- A lockout: no contact between players and team staff, transaction freeze, no facility access.
- So the window to sign or trade a 40-man player is Nov 2 to Dec 1: 30 days. [compute in script]

## 5. Last time
- 2021-22: lockout Dec 2, 2021 to Mar 10, 2022, 99 days as widely reported; Opening Day moved from Mar 31 to Apr 14; 162 games preserved with postponed games made up (Cubs FAQ). One paragraph.
- ESPN's expectation this time: little bargaining in December, talks in mid-to-late January, a deal by early May to start around June; losing 60+ games extends most national TV contracts a year. Attribute; don't predict beyond.

## 6. Countdown tracker (recurring box each week)
- Days left: 26. Last proposal: MLB, Nov 3. Union's last counter: as reported Nov 3. Next dates: QO decisions Nov 11-15, Rule 5 protection Nov 17, non-tender Nov 20.

## 7. Prediction [MATT TO CONFIRM]
No new agreement by 11:59 p.m. ET Dec 1, and the owners lock out the players on Dec 2. Checkable Dec 2.

Layout per house rule: H1; dek (subtitle); body; About this piece; Sources (bulleted linked titles); Not for publication. 1,000-1,400 words. Three figures. Cover: flashy, no logos/readable text; baseballs white with red stitching; idea: a stadium scoreboard-style countdown light or a chained clubhouse door at dawn (no numbers rendered by the model; any number is composited type).
