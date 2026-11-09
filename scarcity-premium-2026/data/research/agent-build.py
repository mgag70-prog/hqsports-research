import csv, statistics as st
W="https://en.wikipedia.org/wiki/Forbes_list_of_the_most_valuable_"
R=[
# league,team,buyer,announced,price,stake,implied,assets,forbes,list,pub,price_src,forbes_src,conf,notes
("NFL","Jacksonville Jaguars","Shahid Khan","2011-11-29",0.76,100,0.76,"Team only","0.725","Forbes NFL Valuations 2011","2011-09","https://www.christianpost.com/news/jacksonville-jaguars-sold-for-760m-florida-team-could-see-more-success-in-la.html; https://www.sportsbusinessdaily.com/Daily/Issues/2011/11/30/Franchises/Jaguars.aspx (2011-11-30)","not verified this pass (memory: $725M Sept 2011 list)","low","OUT OF RANGE by announcement (approved 2011-12-14; closed 2012-01-04). Some reports $770M. Excluded from medians."),
("NFL","Cleveland Browns","Jimmy & Dee Haslam","2012-08-02",1.05,100,1.05,"Team only","0.977","Forbes NFL Valuations 2011","2011-09","https://www.bloomberg.com/news/articles/2012-08-03/haslam-agrees-to-buy-cleveland-browns-for-more-than-1-billion (2012-08-03); https://www.espn.com/nfl/story/_/id/8225861/randy-lerner-sells-cleveland-browns-more-1b-sources-say","not verified this pass (memory: $977M Sept 2011 list; 2012 list published after deal)","low","Price reported as 'more than $1B'; $1.05B common; one outlet $1.1B. Approved 2012-10-16. Forbes figure unverified -> excluded."),
("NFL","Buffalo Bills","Terry & Kim Pegula","2014-09-09",1.4,100,1.4,"Team only","0.935","Forbes NFL Valuations 2014","2014-08",
 "not re-fetched this pass (widely reported $1.4B; approved 2014-10-08)",W+"NFL_teams (historical table, 2014 column)","medium","Forbes value from Wikipedia historical table (column offset checked against Cowboys/Commanders). Price well documented but URL not fetched here."),
("NFL","Carolina Panthers","David Tepper","2018-05-15",2.275,100,2.275,"Team only (stadium owned by city)","2.3","Forbes NFL Valuations 2017","2017-09",
 "https://www.espn.com/nfl/story/_/id/23509278 (2018-05-16); https://www.cnbc.com/2018/05/15/billionaire-hedge-fund-manager-david-tepper-reportedly-close-to-finalizing-deal-for-carolina-panthers-at-record-price.html (2018-05-15)",W+"NFL_teams (2017 column)","high","Early reports $2.2B; Bloomberg $2.3B; final $2.275B. Approved 2018-05-22, closed 2018-07-09."),
("NFL","Denver Broncos","Walton-Penner group","2022-06-07",4.65,100,4.65,"Team only","3.75","Forbes NFL Valuations 2021","2021-08-05",
 "not re-fetched this pass (widely reported; approved 2022-08-09)",W+"NFL_teams (2021 column); https://www.cbssports.com/nfl/news/most-valuable-nfl-franchises-revealed-cowboys-and-patriots-top-2021-ranking-bills-and-bengals-at-the-bottom/ (2021-08-05)","medium",""),
("NFL","Washington Commanders","Josh Harris group","2023-04-13",6.05,100,6.05,"Team only (incl. training facility; stadium leased)","5.6","Forbes NFL Valuations 2022","2022-08",
 "not re-fetched this pass (record $6.05B; signed 2023-05-12; approved/closed 2023-07-20)",W+"NFL_teams (2022 column)","medium","Agreement in principle 2023-04-13; formal agreement 2023-05-12."),
("NFL","Seattle Seahawks","Khosla family","2026-07-11",9.612,100,9.612,"not found (Sounders stake not mentioned)","6.7","Forbes NFL Valuations 2025","2025-08-28",
 "https://abc30.com/post/khosla-led-group-agrees-buy-seahawks-sources-say-96-billion/19507004/ (2026-07-14); https://www.kiro7.com/news/local/nfl-owners-approve-96-billion-seahawks-sale-khosla-family-full-sale-not-finalized-yet/SKPKXO7JFNH53KJMGPVUDNLFSA/ (2026-08-26); https://www.axios.com/2026/07/12/super-bowl-champion-seahawks-9-billion",
 "https://www.forbes.com/sites/justinteitelbaum/2025/08/28/the-nfls-most-valuable-teams-2025/; https://www.aol.com/articles/seattle-seahawks-sale-super-bowl-203848895.html","medium","NFL record. Approved 2026-08-26; closed ~2026-09-03. Seller: Paul G. Allen estate. Terms not officially disclosed (league sources)."),
("MLB","Los Angeles Dodgers","Guggenheim Baseball (Walter, Johnson, Kasten)","2012-03-27",2.15,100,2.15,"Yes: Dodger Stadium; parking-lot land in JV with McCourt","1.4","Forbes MLB Valuations 2012","2012-03",
 "https://www.mlbtraderumors.com/2012/03/dodgers-reach-agreement-to-be-sold-to-magickasten-group.html (2012-03-27); https://www.blackstone.com/news/press/guggenheim-baseball-management-acquires-los-angeles-dodgers",
 "https://www.laweekly.com/did-mark-walter-overpay-for-the-dodgers-forbes-puts-value-at-just-1-4-billion/","medium","Bankruptcy auction; closed 2012-05-01. Price includes stadium; McCourt kept stake in land JV."),
("MLB","San Diego Padres","O'Malley/Seidler/Fowler group","2012-08-07",0.8,100,0.8,"Unclear: price may count $200M Fox Sports SD TV payment","0.458","Forbes MLB Valuations 2012","2012-03",
 "https://ballparkdigest.com/201208075314/major-league-baseball/news/omalley-group-reaches-agreement-to-buy-padres (2012-08-07); https://www.heraldnet.com/sports/ex-dodger-owner-agrees-to-buy-padres-for-about-800m/",
 "not verified this pass (memory: $458M)","low","Approved 2012-08-16. Ballpark Digest notes price may be lower net of $200M TV payment."),
("MLB","Seattle Mariners","First Avenue Entertainment (John Stanton) from Nintendo","2016-04-27",1.4,"~55 (Nintendo kept 10% of its holding)",1.4,"not found (Mariners own majority of ROOT Sports NW; inclusion not confirmed)","1.2","Forbes MLB Valuations 2016","2016-03",
 "https://www.wtkr.com/2016/04/27/nintendo-sale-of-mariners-values-team-at-1-4-billion (2016-04-27)",W+"MLB_teams (2016 column)","medium","$1.4B is Nintendo's stated valuation; price for stake not disclosed. Control passed to existing minority owners."),
("MLB","Miami Marlins","Bruce Sherman / Derek Jeter","2017-08-11",1.2,100,1.2,"not found (debt assumption reported in some accounts)","0.94","Forbes MLB Valuations 2017","2017-04",
 "not re-fetched this pass (widely reported $1.2B; approved 2017-09-27; closed 2017-10-02)",W+"MLB_teams (2017 column)","medium",""),
("MLB","Kansas City Royals","John Sherman","2019-08-30",1.0,100,1.0,"Team only","1.0","Forbes MLB Valuations 2019","2019-04",
 "not re-fetched this pass (reported ~$1B; approved 2019-11)",W+"MLB_teams (2019 column)","medium","Some secondary sources put Forbes 2019 at $1.025B (premium -2.4%). Treat as flat."),
("MLB","New York Mets","Steve Cohen","2020-09-14",2.42,95,2.42,"No: SNY excluded","2.4","Forbes MLB Valuations 2020","2020-04",
 "https://www.sportico.com/leagues/baseball/2020/steve-cohen-deal-new-york-mets-1234612814/ (2020-09); https://www.axios.com/2020/09/15/steve-cohen-mets (2020-09-15)",W+"MLB_teams (2020 column)","medium","Cohen already held 8%; Wilpon/Katz kept 5%. $2.42B is the reported team valuation; some outlets $2.475B. Approved 2020-10-30."),
("MLB","Baltimore Orioles","David Rubenstein group","2024-01-30",1.725,"~40 initially; control on Peter Angelos's death",1.725,"not found (MASN stake not addressed)","1.713","Forbes MLB Valuations 2023","2023-03-23",
 "https://www.nbcwashington.com/news/sports/mlb/orioles-to-be-sold-by-angelos-family-for-1-725-billion-reports-say (2024-01-30)",
 "https://www.nbcwashington.com/news/sports/the-mlbs-most-valuable-franchises-heading-into-2023-season/3206695/ (2023-03-23, $1.7B); "+W+"MLB_teams (2023 composition table, $1.713B)","medium","Approved 2024-03-27. Forbes 2023 shows $1.7B (NBC rounding) vs $1.713B (Wikipedia); premium +0.7% to +1.5%."),
("MLB","Tampa Bay Rays","Patrick Zalupski group","2025-07-14",1.7,100,1.7,"No stadium (Tropicana Field city-owned)","1.25","Forbes MLB Valuations 2025","2025-03-26",
 "https://www.mlbtraderumors.com/2025/07/stuart-sternberg-has-agreed-to-sell-rays-to-patrick-zalupski-deal-expected-to-be-final-by-september.html (2025-07-14); https://www.clickorlando.com/sports/2025/06/18/jacksonville-area-billionaire-leads-group-trying-to-buy-tampa-bay-rays-for-17b-report/ (2025-06-18)",
 "https://www.draysbay.com/2025/3/26/24394482/tampa-bay-rays-valued-at-1-25-billion-ahead-of-2025-season (2025-03-26); https://stpetecatalyst.com/zaps/forbes-rays-still-worth-1-25-billion/","high","$1.7B first reported 2025-06-18; agreement in principle 2025-07-14; approved 2025-09-22/24; closed 2025-09-25."),
("NBA","New Orleans Hornets (Pelicans)","Tom Benson","2012-04-13",0.338,100,0.338,"Team only","0.285","Forbes NBA Valuations 2012","2012-01-25",
 "https://www.hoopsrumors.com/2012/04/tom-benson-frontrunner-to-buy-hornets.html (2012-04); https://www.cbssports.com/nba/news/saints-owner-tom-benson-to-become-sole-owner-of-new-orleans-hornets","https://www.nbcsportsbayarea.com/nba/nba-team-values-2012/1312958/ (2012-01-25)","medium","Seller: NBA (league-owned since 2010)."),
("NBA","Memphis Grizzlies","Robert Pera group","2012-06-11",0.377,100,0.377,"Team only","0.269","Forbes NBA Valuations 2012","2012-01-25",
 "https://www.nbcsports.com/nba/news/sale-of-grizzlies-to-robert-pera-finalized-for-377-million (2012-10-29); https://www.hoopsrumors.com/2012/10/robert-pera-completes-purchase-of-grizzlies.html","https://www.nbcsportsbayarea.com/nba/nba-team-values-2012/1312958/ (2012-01-25)","medium","Agreement date approximate (June 2012); approved 2012-10-25. Some early reports ~$350M."),
("NBA","Sacramento Kings","Vivek Ranadive group","2013-05-16",0.534,"~65 (Maloofs' stake)",0.534,"not found (arena not mentioned)","0.525","Forbes NBA Valuations 2013","2013-01-23",
 "https://www.si.com/nba/2013/05/31/sacramento-kings-sold-534-million-vivek-ranadive-george-maloof-joe-maloof-david-stern (2013-05-31)","https://hoopsrumors.com/2013/01/forbes-releases-nba-franchise-valuations.html (2013-01-23)","medium","CONFLICT: Forbes Jan-2013 list ($525M) already priced the rival Seattle bid; SI cites Forbes $300M (Jan-2012 list) -> +78% on that basis. Closed 2013-05-31."),
("NBA","Milwaukee Bucks","Wes Edens / Marc Lasry","2014-04-16",0.55,100,0.55,"No (Kohl pledged $100M toward new arena)","0.405","Forbes NBA Valuations 2014","2014-01-22",
 "not re-fetched this pass (widely reported $550M; approved 2014-05-16)","https://thescore.com/nba/news/414437 (2014-01-22)","medium",""),
("NBA","Los Angeles Clippers","Steve Ballmer","2014-05-29",2.0,100,2.0,"Team only","0.575","Forbes NBA Valuations 2014","2014-01-22",
 "https://fivethirtyeight.com/features/got-a-billion-dollars-buy-the-clippers; https://fortune.com/2014/06/05/american-sports-teams-all-worth-more-than-you-think (2014-06-05)","https://thescore.com/nba/news/414437 (2014-01-22)","medium","Forced sale (Sterling ban). Closed 2014-08-12."),
("NBA","Atlanta Hawks","Antony Ressler group","2015-06-24",0.85,100,0.85,"Includes arena operating rights (not verified)","0.825","Forbes NBA Valuations 2015","2015-01-21",
 "not re-fetched this pass (reported $850M)","https://hoopsrumors.com/2015/01/forbes-franchise-valuations.html (2015-01-21)","medium","Price and asset scope not re-verified this pass."),
("NBA","Houston Rockets","Tilman Fertitta","2017-09-05",2.2,100,2.2,"not found (Toyota Center lease not mentioned)","1.65","Forbes NBA Valuations 2017","2017-02",
 "https://www.si.com/nba/2017/09/05/houston-rockets-sale-tilman-fertitta-price-1 (2017-09-05); https://www.npr.org/sections/thetwo-way/2017/09/05/548644834/houston-rockets-set-to-get-a-new-owner-local-billionaire-tilman-fertitta","https://www.si.com/nba/2017/09/05/houston-rockets-sale-tilman-fertitta-price-1 (cites Forbes $1.65B)","high","Approved 2017-10-06."),
("NBA","Brooklyn Nets","Joe Tsai","2019-08-16",2.35,"51 (completing 100%; 49% bought 2018)",2.35,"Barclays Center bought separately; total ~$3.4B","2.35","Forbes NBA Valuations 2019","2019-02-06",
 "not re-fetched this pass (2018 option deal at $2.35B team valuation)","https://www.hoopsrumors.com/2019/02/forbes-releases-2019-nba-franchise-valuations.html (2019-02-06)","medium","Price fixed by the April 2018 minority deal, so this is not an arm's-length 2019 price. Approved 2019-09-18."),
("NBA","Utah Jazz","Ryan Smith","2020-10-28",1.66,100,1.66,"Yes: Vivint Arena + G League Stars","1.55","Forbes NBA Valuations 2020","2020-02-11",
 "not re-fetched this pass (reported $1.66B incl. arena)","https://www.hoopsrumors.com/2020/02/forbes-releases-2020-nba-franchise-valuations.html (2020-02-11)","medium","Arena included, so team-only premium is lower than shown."),
("NBA","Minnesota Timberwolves","Marc Lore / Alex Rodriguez","2021-04-10",1.5,"staged 20%/20%/40% to ~80%",1.5,"Includes WNBA Lynx","1.4","Forbes NBA Valuations 2021","2021-02-10",
 "https://www.espn.com/nba/story/_/id/45577217 (2025-06-24); https://www.hoopsrumors.com/2021/05/alex-rodriguez-marc-lore-reach-agreement-to-buy-timberwolves.html","https://hoopsrumors.com/2021/02/forbes-releases-2021-nba-franchise-valuations.html (2021-02-10)","medium","Control passed 2025-06 after arbitration at the same $1.5B. Against Forbes Oct-2024 ($3.1B) the closing price was -52%."),
("NBA","Phoenix Suns","Mat Ishbia","2022-12-20",4.0,100,4.0,"Includes WNBA Mercury","2.7","Forbes NBA Valuations 2022","2022-10-27",
 "not re-fetched this pass (widely reported $4B; approved 2023-02-07)","https://hoopsrumors.com/2022/10/forbes-releases-2022-nba-franchise-valuations.html (2022-10-27)","medium","Correction to the brief: Forbes Oct-2022 Suns = $2.7B, not $1.8B."),
("NBA","Milwaukee Bucks","Jimmy & Dee Haslam (from Lasry)","2023-04-26",0.875,25,3.5,"Team only","2.3","Forbes NBA Valuations 2022","2022-10-27",
 "https://sportsnaut.com/reports-haslams-buying-25-percent-stake-in-bucks; https://www.thedailyupside.com/marc-lasry-sells-stake-in-milwaukee-bucks-at-sky-high-valuation","https://hoopsrumors.com/2022/10/forbes-releases-2022-nba-franchise-valuations.html (2022-10-27)","medium","25% co-control stake (Haslams share control with Edens), not a majority. $0.875B derived from 25% x $3.5B."),
("NBA","Charlotte Hornets","Gabe Plotkin / Rick Schnall","2023-06-16",3.0,"majority (Jordan kept minority)",3.0,"Team only","1.7","Forbes NBA Valuations 2022","2022-10-27",
 "not re-fetched this pass (reported ~$3B; approved 2023-08)","https://hoopsrumors.com/2022/10/forbes-releases-2022-nba-franchise-valuations.html (2022-10-27)","medium",""),
("NBA","Dallas Mavericks","Adelson / Dumont family","2023-11-28",3.5,"majority (Cuban kept ~27%)",3.5,"No: arena not included","4.5","Forbes NBA Valuations 2023","2023-10-26",
 "https://www.nbcdfw.com/news/sports/nba/listing-the-most-valuable-nba-franchises-after-mark-cuban-sells-stake-of-mavericks/3399123 (2023-11-29)","same NBC DFW article, citing Forbes 2023-10-26","medium","Correction: Forbes Oct-2023 Mavs = $4.5B ($4.7B is the Oct-2024 list). Approved 2023-12-27. Only sale in set clearly below Forbes."),
("NBA","Boston Celtics","Bill Chisholm group","2025-03-20",6.1,"~51 now; remainder 2028",6.1,"No (TD Garden not owned)","6.0","Forbes NBA Valuations 2024","2024-10-24",
 "https://abc30.com/post/nba-approves-mark-walters-purchase-majority-stake-lakers/18091163/ (references $6.1B Celtics)","https://sportsnaut.com/nba-news-most-valuable-teams-list (2024-10-24); https://bleacherreport.com/articles/10140783-warriors-knicks-lakers-celtics-top-forbes-2024-list-of-most-valuable-nba-teams","medium","Second tranche reportedly priced higher (~$7.3B, not verified this pass)."),
("NBA","Los Angeles Lakers","Mark Walter (TWG)","2025-06-18",10.0,"majority (Buss kept >15%)",10.0,"Team only","7.1","Forbes NBA Valuations 2024","2024-10-24",
 "https://abc30.com/post/nba-approves-mark-walters-purchase-majority-stake-lakers/18091163/ (2025-10-30); https://www.local10.com/sports/2025/10/30/mark-walter-finalizes-his-purchase-of-a-majority-stake-in-the-los-angeles-lakers","https://sportsnaut.com/nba-news-most-valuable-teams-list (2024-10-24)","high","Approved and closed 2025-10-30. Jeanie Buss stays governor for at least 5 years."),
("NBA","Portland Trail Blazers","Tom Dundon group","2025-09-12",4.25,"80 at close; 20% by 2028",4.25,"not found (Moda Center not addressed)","3.5","Forbes NBA Valuations 2024","2024-10-24",
 "https://www.sportico.com/business/team-sales/2025/trail-blazers-sale-signed-dundon-group-billion-1234870717/ (2025-09); https://www.sportico.com/business/team-sales/2026/portland-trail-blazers-sale-tom-dundon-approved-1234888750/ (2026-03)","https://sportsnaut.com/nba-news-most-valuable-teams-list (2024-10-24)","medium","CONFLICT: $4.25B (2025) vs ~$4.1B 'blended' (Sportico at approval) -> +17% to +21%. Tentative deal 2025-08-13; approved 2026-03-30."),
("NBA","Los Angeles Lakers","Josh Kushner / Bob Iger (from Walter)","2026-08-11",12.5,"Walter's controlling stake (% not found)",12.5,"Lakers only","10.0","Forbes NBA Valuations 2025","2025-10-23",
 "https://abc7.com/post/sources-josh-kushner-bob-iger-buy-lakers-12b/19668024/ (2026-08-13); https://abc7.com/post/jeanie-buss-family-sells-last-ownership-stake-lakers-sources-say/19693599/ (2026-08-17)","https://www.forbes.com/sites/justinteitelbaum/2025/10/23/the-most-valuable-nba-teams-2025/","medium","PENDING NBA approval. Some headlines say $12B; ESPN/AP $12.5B. Buss 17.8% tag-along sale disputed; court date Dec 8."),
("NHL","St. Louis Blues","Tom Stillman group","2012 (agreement date not found)",0.13,100,0.13,"Yes: Scottrade Center ops, AHL Peoria, Peabody interest","0.157","Forbes NHL Valuations 2011","2011-11/12",
 "https://www.si.com/nhl/2012/05/10/new-stlouisbluesowner (2012-05-10)","same SI article (cites Forbes $157M)","low","Price 'believed to be' ~$130M; includes arena and other assets. Approved 2012-05-10."),
("NHL","Phoenix Coyotes","IceArizona (Gosbee/LeBlanc) from NHL","2013-06",0.17,100,0.17,"Team only (Glendale lease separate)","0.134","Forbes NHL Valuations 2012","2012-11-28",
 "not found this pass (memory: $170M)","https://nhlrumors.com/forbes-release-nhl-team-values-maple-leafs-valued-at-1-billion/2012/11/28 (2012-11-28)","low","Price not verified."),
("NHL","New Jersey Devils","Josh Harris / David Blitzer","2013-08-15",0.32,100,0.32,"Yes: Prudential Center operating rights; covers debt","0.205","Forbes NHL Valuations 2012","2012-11-28",
 "https://www.foxnews.com/sports/devil-of-a-deal-nhl-franchise-sold-to-harris (2013-08-15)","https://nhlrumors.com/forbes-release-nhl-team-values-maple-leafs-valued-at-1-billion/2012/11/28","medium","Reported as 'more than $320M' including arena rights and debt."),
("NHL","Florida Panthers","Vincent Viola","2013-09-26",0.25,100,0.25,"Includes arena management rights (not verified)","0.17","Forbes NHL Valuations 2012","2012-11-28",
 "https://www.nbcsports.com/nhl/news/official-panthers-sold-to-vincent-viola-for-230-million (2013-09-27); https://www.sportbusiness.com/news/nhl-florida-panthers-sold-for-250m/","https://nhlrumors.com/forbes-release-nhl-team-values-maple-leafs-valued-at-1-billion/2012/11/28","medium","CONFLICT: $250M headline vs $230M in URL slug -> +35% to +47%."),
("NHL","New York Islanders","Jon Ledecky / Scott Malkin","2014-08-19",0.485,"minority 2014; majority 2016",0.485,"No (Barclays lease)","0.195","Forbes NHL Valuations 2013","2013-11",
 "https://www.nbcsports.com/nhl/news/report-islanders-were-sold-for-485-million (2014-10-18); https://fortune.com/2014/08/19/new-york-islanders-sale-minority-stake (2014-08-19)",W+"NHL_teams (historical table, 2013 column)","medium","$485M comes from Forbes' own reporting after the deal. Staged control transfer (2016)."),
("NHL","Arizona Coyotes","Andrew Barroway (51%)","2014-10-10",None,51,None,"not found","0.2","Forbes NHL Valuations 2013","2013-11",
 "https://www.si.com/nhl/2014/10/12/ap-hkn-coyotes-ownership-1st-ld-writethru (2014-10-12)",W+"NHL_teams (2013 column)","low","Price/valuation not found."),
("NHL","Carolina Hurricanes","Tom Dundon (61%)","2017-12-07",0.308,61,0.505,"not found (PNC Arena lease not addressed)","0.37","Forbes NHL Valuations 2017","2017-12-05",
 "https://www.foxbusiness.com/markets/dundon-signs-purchase-agreement-to-buy-carolina-hurricanes (2017-12-07); https://thescore.com/nhl/news/1465414 (2018-01, '$505-million valuation')",
 "https://thescore.com/news/1439554 (Forbes 2017 list); https://lasvegassun.com/news/2017/dec/05/golden-knights-ranked-no-14-in-nhl-team-values/ (2017-12-05)","medium","CONFLICT: AP/FoxBiz cite Forbes $230M (the 2016 list) -> +120%. Stake price derived (61% x $505M). Closed 2018-01-11."),
("NHL","Arizona Coyotes","Alex Meruelo (95%)","2019-06-10",None,95,None,"not found","0.29","Forbes NHL Valuations 2018","2018-12",
 "https://thescore.com/nhl/news/1804238 (2019-07-29); https://arenadigest.com/2019/06/11/alex-meruelo-reportedly-close-to-purchasing-majority-stake-in-arizona-coyotes/",W+"NHL_teams (2018 column)","low","Price/valuation not found."),
("NHL","Pittsburgh Penguins","Fenway Sports Group","2021-11-17",0.9,"majority (Lemieux/Burkle kept minority)",0.9,"not found","0.65","Forbes NHL Valuations 2020","2020-12-09",
 "https://www.tsn.ca/fenway-sports-group-reaches-deal-to-buy-pittsburgh-penguins-1.1727820; https://www.bostonglobe.com/2021/12/09/sports/nhl-owners-approve-sale-pittsburgh-penguins-fenway-sports-group (2021-12-09)","https://www.thescore.com/nhl/news/2067187/rangers-maple-leafs-lead-list-of-nhls-most-valuable-franchises (Forbes 2020-12-09)","medium","Reported 'around' $900M. Approved 2021-12-09."),
("NHL","Ottawa Senators","Michael Andlauer","2023-06-14",0.95,100,0.95,"not found","0.8","Forbes NHL Valuations 2022","2022-12-14",
 "https://fortune.com/2023/06/14/ottawa-senators-acquired-canadian-businessman-michael-andlauer-nhl-hockey/ (2023-06-14); https://bleacherreport.com/articles/10090383-senators-950m-sale-to-michael-andlauer-officially-approved-by-nhl",
 "https://www.forbes.com/sites/mikeozanian/2022/12/14/nhl-team-values-2022-new-york-rangers-on-top-at-22-billion/; "+W+"NHL_teams (2022 column)","medium","NHL record at the time."),
("NHL","Utah (ex-Arizona Coyotes hockey assets)","Ryan Smith (SEG)","2024-04-18",1.2,100,1.2,"Hockey ops/roster only; Coyotes franchise rights kept by Meruelo","0.5","Forbes NHL Valuations 2023","2023-12-14",
 "https://www.sportico.com/business/team-sales/2024/ryan-smith-nhl-owner-coyotes-1234776017/ (2024-04); https://sports.yahoo.com/unique-1-2-billion-coyotes-195402279.html",
 "https://www.forbes.com/sites/mikeozanian/2023/12/14/the-most-valuable-nhl-teams-2023/; "+W+"NHL_teams (2023 column)","low","Not a standard control sale: league-brokered, priced like expansion; Meruelo got ~$1B. Excluded from medians."),
("NHL","Tampa Bay Lightning","Doug Ostrover / Marc Lipschultz","2024-10-03",0.9,"just over 50",1.8,"not found","1.25","Forbes NHL Valuations 2023","2023-12-14",
 "https://www.sportico.com/business/team-sales/2024/nhl-tampa-bay-lightning-sold-vinik-control-1234802503/ (2024-10); https://wusf.org/text/sports/2024-10-24/vinik-completes-sale-of-lightnings-majority-ownership-to-wall-street-billionaires (2024-10-24)",
 "https://www.forbes.com/sites/mikeozanian/2023/12/14/the-most-valuable-nhl-teams-2023/; "+W+"NHL_teams (2023 column)","medium","Majority economic stake now; Vinik keeps control/governor for 3 years. NHL approval ~Oct 1; closed 2024-10-24. Stake price derived."),
("NHL","Pittsburgh Penguins","Hoffmann family (from FSG)","2025-12-17",1.7,"majority (FSG kept minority)",1.7,"Yes: SportsNet Pittsburgh equity; music-venue JV stake","1.75","Forbes NHL Valuations 2025","2025-12-11",
 "https://www.bloomberg.com/news/articles/2025-12-17/fenway-agrees-to-sell-pittsburgh-penguins-to-hoffman-family (2025-12-17); https://www.sportico.com/business/team-sales/2026/nhl-approves-penguins-sale-hoffmann-family-1234936872/ (2026-06)",
 "https://www.forbes.com/sites/justinteitelbaum/2025/12/11/the-nhls-most-valuable-teams-2025/","medium","'Enterprise value' from anonymous source. Approved ~2026-06-23."),
]
# NBA Pistons 2011 reference row
R.append(("NBA","Detroit Pistons","Tom Gores (Platinum Equity)","2011-04",0.325,100,0.325,"Yes: Palace of Auburn Hills + DTE/Meadow Brook venues","not found","Forbes NBA Valuations 2011","2011-01","not re-fetched this pass (reported ~$325M incl. venues)","not found","low","OUT OF RANGE (2011). Reference only; excluded from medians."))
hdr="league,team,buyer,announced_date,price_reported_usd_b,stake_pct,implied_100pct_usd_b,includes_other_assets,prior_forbes_value_usd_b,forbes_list,forbes_pub_date,premium_pct,price_sources,forbes_sources,confidence,notes".split(",")
rows=[]
for r in R:
    lg,tm,by,ad,p,sk,imp,assets,fv,fl,fd,ps,fs,cf,nt=r
    prem=""
    try:
        if imp is not None: prem=round((imp/float(fv)-1)*100,1)
    except: pass
    rows.append([lg,tm,by,ad,"not found" if p is None else p,sk,"not found" if imp is None else imp,assets,fv,fl,fd,prem,ps,fs,cf,nt])
out="/tmp/claude-0/-home-claude/61cece63-4840-5231-8b2d-453405075085/scratchpad/out/control_sales_vs_forbes.csv"
with open(out,"w",newline="") as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
use=[x for x in rows if x[14] in("high","medium") and x[11]!="" and not x[3].startswith("2011")]
def yr(x):
    return int(x[3][:4])
def med(xs): return (round(st.median(xs),1),len(xs)) if xs else ("n/a",0)
print("ALL",med([x[11] for x in use]))
for lg in ["NFL","MLB","NBA","NHL"]: print(lg,med([x[11] for x in use if x[0]==lg]))
for a,b in [(2012,2017),(2018,2022),(2023,2026)]: print(a,b,med([x[11] for x in use if a<=yr(x)<=b]))
print("share above Forbes",sum(1 for x in use if x[11]>0),len(use))
for x in rows: print(x[0],x[1][:22],x[3],x[6],x[8],x[11],x[14])
