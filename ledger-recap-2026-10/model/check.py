#!/usr/bin/env python3
"""Checks for ledger-recap-2026-10/draft.md, "The Ledger: October 2026".

Every line of the publishable part (H1 through the closing question) is checked against the drafts of
the pieces that line links: each number must appear in one of them, and each quoted passage of three or
more words must appear in one of them verbatim. Lines in "What moved in October" can also draw on
notes/sources/2026-11-facts.md, the checked facts file for events no piece covers (the World Series result).
A number with no source is allowed only on a line carrying a [MATT TO CONFIRM] marker, and only if it is
listed in MARKED; the run prints each one.
Also checks the layout, the dek, the word count, the calls table and the cover image.

Usage: python3 ledger-recap-2026-10/model/check.py"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = (ROOT / "ledger-recap-2026-10/draft.md").read_text()
COVER = ROOT / "notes/the-ledger/header/option-B-1100x220.png"

# Published links to piece folders.
PIECES = {
    "penn-states-497-million-buyout-cost": "penn-state-buyout-2026",
    "i-paid-for-the-same-four-wrigley": "wrigley-season-tickets-2026",
    "baseballs-owners-want-a-salary-cap": "mlb-cap-valuations-2026",
    "four-mlb-teams-season-ticket-contracts": "mlb-lockout-2026",
    "eight-fewer-games-is-35-million-fewer": "mlb-154-games-2026",
    "no-big-ten-school-has-published-revenue": "illinois-revenue-sharing-2026",
    "baseballs-best-team-would-have-been": "mlb-floor-2026",
    "the-dodgers-are-already-133-million": "mlb-2027-cap-2026",
    "taxpayers-have-committed-135-billion": "stadium-subsidies-2026",
}
TEXT = {f: re.sub(r"\s+", " ", (ROOT / f / "draft.md").read_text()).replace("’", "'") for f in PIECES.values()}
FACTS = "notes/sources/2026-11-facts.md"
TEXT[FACTS] = re.sub(r"\s+", " ", (ROOT / FACTS).read_text()).replace("\u2019", "'")
MARKED = {}
STATUSES = {"Open", "On track", "At risk", "Hit", "Missed"}
NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:-\d+)?")
QUOTE = re.compile(r"\"([^\"]+)\"")

fails = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok: fails.append(name)

def linked(line):
    folders = []
    for url in re.findall(r"\]\(([^)]+)\)", line):
        for key, folder in PIECES.items():
            if key in url: folders.append(folder)
    return folders

def in_text(tok, text):
    tok = tok.rstrip(",.")
    for t in {tok, tok.lstrip("$")}:
        if re.search(rf"(?<![\d.]){re.escape(t)}(?![\d])", text): return True
    return False

public, _, rest = DRAFT.partition("\n## Sources\n")
sources_part, _, private = rest.partition("\n## Not for publication\n")
lines = [l for l in public.splitlines() if l.strip()]

# Layout
heads = re.findall(r"^## (.+)$", DRAFT, re.M)
check("section order", heads == ["What I published in October", "The calls on the record", "What moved in October", "Sources", "Not for publication"], str(heads))
check("H1", lines[0] == "# The Ledger: October 2026", lines[0])
dek = lines[1].strip("*")
check(f"dek under 150 characters ({len(dek)})", lines[1].startswith("*") and len(dek) < 150)
check("closing question", lines[-1].rstrip().endswith("?"), lines[-1][-60:])
check("no em dashes in the file", "—" not in DRAFT)
check("cover image exists", COVER.exists(), str(COVER.relative_to(ROOT)))

# Word count of the publishable text, links counted by their visible words
visible = re.sub(r"\]\([^)]+\)", "]", public)
visible = re.sub(r"^\|[-| ]+\|$", "", visible, flags=re.M)
words = len(re.findall(r"[A-Za-z0-9$][\w$.,%'/-]*", re.sub(r"[#*|\[\]]", " ", visible)))
check(f"word count {words} in 600 to 900", 600 <= words <= 900)

# Numbers and quotes, line by line, against the linked drafts
moved = public.split("## What moved in October")[1]
for line in lines[2:]:
    folders = linked(line) + ([FACTS] if line in moved else [])
    label = line[:50]
    scan = re.sub(r"\]\([^)]+\)", "]", line)
    for q in QUOTE.findall(scan):
        q = q.strip().rstrip(",.")
        if len(q.split()) < 3: continue
        src = next((f for f in folders if q in TEXT[f]), None)
        check(f"quote {q[:60]!r}", src is not None, src or f"not in {folders or 'any linked draft'}")
    for tok in NUMBER.findall(scan):
        tok = tok.rstrip(",.")
        src = next((f for f in folders if in_text(tok, TEXT[f])), None)
        if src:
            check(f"{tok}  ({label}...)", True, src)
        elif tok in MARKED and "[MATT TO CONFIRM" in line:
            print(f"MARK {tok}  [{MARKED[tok]}]")
        else:
            check(f"{tok}  ({label}...)", False, f"not in {folders or 'any linked draft: line links no piece'}")

# Published list: each piece once, in order of the PIECES table
pub = public.split("## What I published in October")[1].split("## ")[0]
pub_items = [l for l in pub.splitlines() if l.startswith("- ")]
check("nine pieces published", [linked(l)[0] for l in pub_items] == list(PIECES.values()), str(len(pub_items)))
for l in pub_items:
    title = re.match(r"- \[([^\]]+)\]", l).group(1)
    folder = linked(l)[0]
    h1 = re.search(r"^# (.+)$", (ROOT / folder / "draft.md").read_text(), re.M).group(1)
    check(f"link text is the {folder} headline", h1.startswith(title), title[:50])

# Calls table
rows = [l for l in public.splitlines() if l.startswith("| ") and not l.startswith("| Call")]
check("ten calls", len(rows) == 10, str(len(rows)))
covered = set()
for r in rows:
    cells = [c.strip() for c in r.strip("|").split("|")]
    call, piece, when, status = cells
    covered.update(linked(piece))
    head = status.split(".")[0]
    check(f"status {head!r} allowed", head in STATUSES)
    if head != "Open":
        check(f"{head} row gives a reason", len(status) > len(head) + 20 and status.endswith("."))
missing = set(PIECES.values()) - covered
check("every piece has a row in the table", not missing, ", ".join(sorted(missing)))
# Each quoted call must come from that piece's prediction section, not elsewhere in the draft
for r in rows:
    cells = [c.strip() for c in r.strip("|").split("|")]
    folder = linked(cells[1])[0]
    raw = (ROOT / folder / "draft.md").read_text().replace("’", "'")
    sect = re.search(r"^## (What this predicts|What I expect)\n(.+?)(?=^## )", raw, re.M | re.S)
    sect = re.sub(r"\s+", " ", sect.group(2)) if sect else ""
    for q in QUOTE.findall(cells[0]):
        q = q.strip().rstrip(",.")
        check(f"call quote from {folder} prediction section", q in sect, q[:50])

# Placeholders and marks are disclosed in Not for publication
for ph in set(re.findall(r"\[[A-Z_]+_URL\]", public)):
    check(f"{ph} listed in Not for publication", ph in private)
check("[MATT TO CONFIRM] listed in Not for publication", ("[MATT TO CONFIRM" not in public) or ("[MATT TO CONFIRM]" in private))
check("no placeholder links left", "_URL]" not in DRAFT)

if fails:
    print(f"\n{len(fails)} CHECK(S) FAILED"); sys.exit(1)
print(f"\nALL CHECKS PASS ({words} words; {len(MARKED)} marked number(s) printed as MARK above)")
