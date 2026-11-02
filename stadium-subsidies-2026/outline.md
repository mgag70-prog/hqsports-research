# Outline: stadium-subsidies-2026

Working H1: "Taxpayers have committed $13.5 billion to 19 stadiums and arenas still being built. Voters approved about one-eighth of it."
Alt H1: "The public pays for the building. The owner keeps the team, and the team is worth more."
Alt H1 2: "38 stadiums and arenas, $18.3 billion of public money, three public votes."
Cover line (verbatim in draft): "Public money. Private stadium."
Publish: Friday Oct 30 afternoon or Saturday Oct 31 morning. Detailed piece (Matt asked for thorough). Target 2,200-2,800 words. Layout per house rule: dek goes in the Substack subtitle (keep under ~150 characters), body, then "About this piece" (construction note + disclosure), then "Sources" (bulleted, linked titles), then "Not for publication".

All numbers: model/recompute.py over data/projects.csv (38 USD projects with both a total cost and a public figure: opened 2015-2026, under construction, or approved; major leagues; new venues and renovations of roughly $400M+ plus smaller ones where documented), data/asks.csv (failed or pending asks), data/evidence.csv (the research). Every figure in projects.csv was checked against data/research/ (agent inventories) and, for headline deals, an independent verification (data/research/verification.md). Canadian projects (Calgary, Edmonton, Ottawa, Rogers Centre) kept out of the USD totals; mention Calgary in a line if useful.

## Dek (subtitle, under 150 characters)
"Across 38 recent stadium and arena deals, taxpayers put in $18.3 billion. The deals still being built ask for more of the bill, not less."

## 1. The bill (fig-01: the 38 projects, public vs private bars, sorted by public $)
- 38 projects, $49.5B total cost, $18.3B public (37.1%).
- 8 privately financed ($12.0B): SoFi, Chase Center, Intuit Dome, Climate Pledge, T-Mobile Arena, Honda Center (renovation), Wells Fargo Center (renovation), Wrigley 1060 Project (with a federal historic tax credit approved, amount claimed not verified). Note "private" still often means public land or infrastructure (Intuit land from Inglewood; Chase Center transit; SoFi league loans/waivers; Broncos' $159M infrastructure).
- 30 took public money; median public share among them 60.0%; 17 are majority public.
- Biggest public checks: Chiefs $1.8B (60% of $3B), Titans $1.26B (60%), Royals $1.14B (60%), Commanders about $1.1B (29.7%), Rays $876M (37.1%), Bills $850M (40.5%), Thunder $850M (94.4%).

## 2. The newest deals ask the public for more (fig-02: median public share, new venues opened 2015-2026 vs new venues under construction/approved)
- New venues opened 2015-2026: median public share 37.8% (14). New venues now under construction or approved: 60.0% (9).
- Renovations run higher still; most now-approved renovation deals are majority public (Brewers 82%, Panthers 81.2%, Pacers 81.9% opened 2022, Grizzlies ~91%, Lightning 76%, Sharks 76.5%, Bengals 74.5%).
- Pipeline (under construction + approved): 19 projects, $13.5B public.
- Context, stated as Bradbury's: his median public share by opening decade fell from about 72% (1990s) to 47% (2010s) and 38% (2020s), while median public cost rose ($605M in the 2010s, 2024 dollars). Our pipeline is the deals opening 2027-2032; it does not contradict his decade series, it adds the next one. Be careful: small sample, say so.
- Four NFL stadiums in the pipeline (Titans, Browns, Commanders, Chiefs) carry $5.0B of public money between them. Bradbury: six newest NFL stadiums with announced budgets, $5.74B.

## 3. What the public number leaves out (short list, each sourced)
- Interest: Raiders $750M principal becomes about $1.35B; Detroit's bonds about $713M vs $324M; Kansas City estimates the city's $600M at about $1.117B with interest (KCUR).
- Property tax: Propheter, 105 venues would have owed $654.3M more in 2022; about $18B present value over current leases; about $7.5B of it would have gone to K-12 schools.
- Federal: tax-exempt bonds cost the Treasury $4.3B in lost revenue for 57 stadiums since 2000 (National Tax Journal 2020). Bills to end it (H.R. 2434 / S. 1192, 2025) [RECHECK status before publishing].
- Maintenance and operating subsidies: Pacers about $800M public over 25 years vs a $295M capital figure; Bills state maintenance; Jaguars $150M maintenance inside the $775M.
- Land: Commanders' federal land transfer; Rays' $180M state college money on the site.

## 4. Why it keeps happening
- Elected bodies approve 96% of stadium proposals; 58% of referendums pass; 6 of 39 proposals 2005-2017 went to voters (Bradbury, The Conversation, Sept 2026; credit his article).
- Leagues control the supply of teams, so the threat to move is credible. Examples from the data: Chargers left San Diego after Measure C failed (43% yes, needed two-thirds, 2016); Coyotes left after Tempe voters said no (56% no, 2023); Chiefs: Jackson County voters rejected the tax 58% to 42% (Apr 2024), then Kansas committed about $1.8B; Capitals/Wizards: Virginia's $1.5B ask died Mar 27, 2024 and DC committed $515M within weeks.
- The pitch vs the research: more than 130 studies over 30+ years find no large local economic gain (J. Economic Surveys 2023); 24 of 34 IGM economists agreed subsidies likely cost taxpayers more than local benefits, 1 disagreed (83% confidence-weighted). Civic pride is real but measured at about 13% of construction cost (contingent valuation studies). Cobb County: about $15M a year net shortfall from Truist Park (Bradbury 2022).
- Public opinion: Illinois voters oppose public money for a Bears stadium 58% to 32% (Emerson, Jan 2026).

## 5. Who votes, and the honest complication
- Of the 38, three had a public vote on the deal: Rangers (about 60% yes, 2016), Thunder (71% yes, 2023), Spurs (Prop B 52% yes, 2025). All three passed. The Thunder's 94.4% public share is the highest in the set and voters chose it. Say that plainly: a referendum is not a guarantee taxpayers say no.
- In recompute: public $ in the three voted deals as a share of total public $ (rangers 500 + thunder 850 + spurs 800 = 2,150 of 18,336.5 = 11.7%). [Add to recompute.] For the pipeline only: thunder + spurs = 1,650 of 13,524.5 = 12.2%. Use whichever the H1 cites; fix H1 wording to match ("about one-eighth").

## 6. Who keeps the gains (fig-03: public contribution as a share of the team's Forbes value, subsidized teams in data/team-values.csv)
- Forbes values (NFL list Sept 9 2026, NBA Oct 16 2026, MLB Mar 20 2026). Estimates, not sale prices; say so.
- Public money as a share of the team's value: Royals 69.5% ($1.14B vs $1.64B), Rays 51.5% ($876M vs $1.7B; Zalupski's group paid $1.7B in 2025), Brewers 26.3%, Diamondbacks 25.5%, Chiefs 20.5%, A's 19.0%, Thunder 17.3%, Titans 14.8%. In baseball the public is paying for a building worth a large share of what the team itself is worth.
- What owners paid vs Forbes now: Browns $1.05B (2012) to $9.0B (8.6x); Bills $1.4B (2014) to $8.15B (5.8x); Jaguars about $0.76B estimated (2011) to $8.05B (10.6x); Commanders $6.05B (2023) to $9.8B (1.6x in three years); Thunder group $0.35B for the Sonics (2006) to $4.9B (14.0x). Don't claim the stadium caused the gain; every NFL team is worth at least $8B per Forbes. Do say the owner keeps the appreciation; the public keeps the bonds.
- Owner wealth, briefly and only where Forbes publishes it: e.g., Tepper $28.5B with $650M from Charlotte; Hunt family $25.6B (whole family; say so) with $1.8B from Kansas; contrast Ballmer $156B and Kroenke $27.6B, who paid their own way. Also note owners whose team is most of their wealth (Strunk $2.8B vs Titans $8.5B; Davis $3.3B vs Raiders $10.3B): that's the honest version of "we can't build it ourselves."
- Research: new stadiums raised NFL teams' local revenue 85%, luxury-box revenue 623% and franchise value 35% on average (Brown et al. 2004; seven teams, 1990s data, say so).
- Fewer seats, higher prices: Bills' new stadium has 60,108 seats, down from 71,608. Matheson (Fortune, June 2026): "No one has ever built a new stadium and provided more affordable tickets" (opening of his sentence).
- The building is public, the team is private: owners typically keep naming rights, premium seating, and surrounding development rights (Commanders exclusive development rights; Royals' $1B ballpark village private; Braves' Battery).

## 7. The ones that paid their own way
- SoFi (Kroenke), Chase Center (Warriors), Intuit Dome (Ballmer), Climate Pledge (OVG), Honda Center (Samuelis), Wells Fargo Center (Comcast). What they share: very large markets or very rich owners, and in San Francisco and Inglewood, voters or councils that had refused or never offered construction money. Still note land/infrastructure help.

## 8. What's still being asked (fig-04: table of open asks)
- Bears: Indiana SB 27 (about $1B district tax revenue estimated, not appropriated); Arlington Heights stalled; no deal as of Oct 14, 2026. Chicago lakefront ask ($2.4B of $4.75B) shelved May 2025.
- Broncos: "entirely privately funded," with about $159M public infrastructure committed.
- Salt Lake City: up to $900M state money if MLB expands there by 2032. Portland: up to $800M in bonds if awarded a team.
- Kansas City: April 6, 2027 charter vote on stadium funding.

## 9. Prediction on the record [MATT TO CONFIRM]
Of the projects in this set still in the pipeline, at least one public contribution grows before the building opens (overruns, added infrastructure, or a renegotiated share), and none shrinks. Checkable at each opening, 2027-2032.

## About this piece (bottom)
- Construction note: definitions (public = state, county and city construction money as reported, not interest, maintenance, lost property tax or land unless stated); 38 USD projects; nominal dollars as reported, not adjusted; sources per row in projects.csv; headline deals independently verified.
- Disclosure: Matt is an Illinois football fan and held Cubs season tickets 1998 to 2021 (per Wrigley piece). The Bears section touches Illinois; Wrigley is in the private list. One line.

## Sources (bottom, bulleted, linked titles)
From projects.csv, asks.csv and evidence.csv; one bullet per source actually cited.

## Not for publication
Alternates, open items, RECHECK items (No Tax Subsidies Act status; Browns injunction status; Bears status day-of).
