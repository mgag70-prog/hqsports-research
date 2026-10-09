"""Club-by-club classification of public season-ticket terms (fetched Oct 8, 2026 CT).
Every quote must appear verbatim in raw/<club>__<doc>.txt or the script fails."""
import csv, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
def norm(s): return re.sub(r"\s+", " ", s).strip()
# category codes:
# L_KEEP   names lockout; club keeps money, rolls it forward
# L_PRORATA names lockout; pro-rata credit or refund
# L_CREDIT names lockout; credit only
# L_NOLIAB names lockout; club excused, no remedy stated
# CR       does not name lockout; promises credit and/or refund for canceled-not-rescheduled games
# DISC     club or MLB decides / announced policy / exchange only
# FINAL    public STH terms say sales final; no canceled-game remedy found
# NONE     no public season-ticket terms page found
rows = [
 ("cubs","sth_terms","L_KEEP","yes","Fees due during a lockout; if under 41 home games, club keeps fees and applies them to the next season","none stated",
  "any fees paid by Licensee shall be retained by Club and applied to the following Season"),
 ("reds","sth_terms","L_PRORATA","yes","Fees abated pro rata per canceled home game; credit, or refund on written request","refund within 60 days of MLB-confirmed cancellation",
  "refunded within 60-days of the confirmed cancellation of games by the Office of the Commissioner of Major League Baseball"),
 ("dbacks","sth_terms","L_CREDIT","yes","Credit toward future games","none stated",
  "Club shall provide Member with a credit that can be applied to future Club games"),
 ("yankees","sth_terms","L_NOLIAB","yes","Club not liable for force majeure; tickets not refundable","none stated",
  "obligated to settle or vote to settle any strike, lockout or work stoppage or other labor disturbance"),
 ("brewers","sth_terms","CR","no","Credit or refund of tickets and parking for canceled games not rescheduled","email within 48 hours; no payment deadline",
  "For any cancelled games that are not replaced or rescheduled, account holders will receive an account credit or a refund equal to the paid value of the relevant tickets and parking."),
 ("royals","sth_terms","CR","no","Credit or refund of tickets and parking for canceled games not rescheduled","none stated",
  "For any cancelled games that are not replaced or rescheduled, account holders will receive an account credit or a refund equal to the paid value of the relevant tickets and parking."),
 ("giants","sth_terms","CR","no","Credit; refund if requested within 30 days","fan must request within 30 days",
  "if Account Holder prefers a refund instead of a credit, may request one within thirty (30) days of the cancellation"),
 ("angels","sth_terms","CR","no","Exchange or refund for canceled games not rescheduled","fan must request within 30 days or waive",
  "Refunds must be requested within thirty (30) days of the announced cancellation of the Event or the refund is forever waived."),
 ("phillies","sth_terms","CR","no","Credit; cash refund only after opting out of renewal","refund of unused credit at end of season, on request",
  "If Account Holder subsequently opts out of the renewal of their season ticket plan in accordance with this Agreement, upon Account Holder's written request, Club will issue a refund in respect of any such unused credits remaining at the end of the applicable season."),
 ("braves","general_terms","CR","no","General ticket terms: automatic refund to card, no credits (season terms say all sales final but bind members to ticket terms on cancellation)","none stated",
  "a refund will automatically be posted to the payment card used for payment of the ticket. No credits will be issued"),
 ("bluejays","general_terms","CR","no","General ticket terms: automatic refund, no credits (no public season-ticket terms page found)","as soon as 60 days from game date",
  "will be automatically refunded for the amount paid on account of this ticket in as soon as sixty (60) days from the Game date"),
 ("cardinals","general_terms","DISC","no","Subject to the club's announced policy for the event","none stated",
  "this ticket will be subject to Event Hosts’ announced policy for the Event"),
 ("tigers","general_terms","DISC","no","Refunds or credits at club's discretion","none stated",
  "if not rescheduled/resumed, refunds or credits will be as determined in Club’s discretion"),
 ("marlins","general_terms","DISC","no","MLB entities decide whether any refunds are issued","none stated",
  "the MLB Entities will determine in their sole discretion whether any refunds will be issued"),
 ("dodgers","general_terms","DISC","no","Exchange for a future game; no cash refund or credit","none stated",
  "may be exchanged at Dodger Stadium, at any time after the date of the Cancelled Game"),
 ("twins","general_terms","DISC","no","Rules posted on twins.com; may be amended without notice","none stated",
  "Rules regulating cancellation or rescheduling of games and use of RAIN CHECKS will be posted on www.twins.com"),
 ("whitesox","general_terms","DISC","no","Points to rainout policy on website","none stated",
  "see the Rainout Policy posted on the Chicago White Sox ticket portion of its website"),
 ("rockies","general_terms","DISC","no","Rain check exchange within current season","none stated",
  "Holder may exchange this RAIN CHECK for a ticket of the same value (subject to availability) for any game during the current regular season"),
 ("mariners","sth_terms","DISC","no","Membership fees not refunded for cancellations; ticket remedy not stated on page","none stated",
  "The Seattle Mariners are not responsible for refunding all or any portion of your Membership fees"),
 ("padres","sth_terms","DISC","no","Membership fees not refunded for cancellations; ticket remedy not stated on page","none stated",
  "The San Diego Padres are not responsible for refunding all or any portion of your Membership fees"),
 ("orioles","sth_terms","DISC","no","Membership fees not refunded for cancellations; ticket remedy not stated on page","none stated",
  "The Club is not responsible for refunding all or any portion of your Membership fees"),
 ("astros","sth_terms","FINAL","no","All sales final; remedy stated only for unplayed postseason games","none stated",
  "All Ticket sales are final and no refunds or exchanges will be made, except as expressly provided in this Agreement."),
 ("redsox","sth_terms","FINAL","no","All sales final, no refunds","none stated",
  "ALL TICKET SALES ARE FINAL AND NO REFUNDS WILL BE MADE."),
 ("pirates","sth_terms","FINAL","no","All sales final; remedy stated only for unplayed postseason games","none stated",
  "All Account sales are final and no refunds or exchanges will be made, except as expressly provided in this Agreement."),
 ("guardians","sth_terms","FINAL","no","All sales final; club may cancel tickets for any reason","none stated",
  "All Ticket sales are final and no refunds or exchanges will be made."),
 ("nationals","sth_terms","FINAL","no","Annual commitment; remedy stated only for unplayed postseason games","none stated",
  "you will receive a credit on your account equal to the value of the Postseason Tickets you purchased for the Unplayed Postseason Games"),
 ("rays","sth_terms","FINAL","no","No canceled-game clause found on public policies page","none stated",""),
 ("rangers","general_terms","FINAL","no","No canceled-game clause found in public ticket terms; no season-ticket terms page found","none stated",""),
 ("mets","sth_terms","NONE","no","Member Clubhouse terms page has no canceled-game clause; no season-ticket agreement found","none stated",""),
 ("athletics","sth_page","NONE","no","No public season-ticket terms page found","none stated",""),
]
src = {(r["club"], r["doc_type"]): r["url"] for r in csv.DictReader(open(root/"data/source-urls.csv"))}
bad = 0
for club, doc, *_ , q in rows:
    if q and norm(q) not in norm((root/f"raw/{club}__{doc}.txt").read_text()):
        print("QUOTE NOT FOUND:", club, q[:60]); bad += 1
assert len({r[0] for r in rows}) == 30, "need 30 clubs"
assert bad == 0
with open(root/"data/club-terms.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["club","doc_type","category","names_lockout","canceled_game_remedy","refund_timing","quote","url","fetched"])
    for club, doc, cat, nl, rem, tim, q in rows:
        w.writerow([club, doc, cat, nl, rem, tim, q, src[(club, doc)], "2026-10-08"])
from collections import Counter
c = Counter(r[2] for r in rows); print(dict(c)); print("lockout named:", sum(r[3]=="yes" for r in rows))
