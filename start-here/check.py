#!/usr/bin/env python3
"""Check start-here/draft.md: every number appears in the draft.md of the piece it sits beside, every link
resolves to a URL listed in outline.md, house rules hold, and the paste page matches the draft.
Usage: python3 check.py   (exits 1 on any failure)"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DRAFT, OUTLINE, PASTE = HERE / "draft.md", HERE / "outline.md", HERE / "paste-into-substack.html"
PIECES = {  # Substack URL -> the piece whose draft.md must hold every number in that list item
    "https://ledgerandwhistle.substack.com/p/the-median-buyer-paid-24-more-than": "scarcity-premium-2026",
    "https://ledgerandwhistle.substack.com/p/taxpayers-have-committed-135-billion": "stadium-subsidies-2026",
    "https://ledgerandwhistle.substack.com/p/i-paid-for-the-same-four-wrigley": "wrigley-season-tickets-2026",
    "https://ledgerandwhistle.substack.com/p/pete-crow-armstrong-was-paid-894000": "pca-mvp-award-2026",
    "https://ledgerandwhistle.substack.com/p/13-days-left-and-mlb-took-its-salary": "lockout-countdown-2026/week-03",
}
NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
WORDS = r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b"
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
fails = []


def check(label, got, want):
    ok = got == want
    print(("ok   " if ok else "FAIL ") + f"{label}: {got!r}" + ("" if ok else f" (want {want!r})"))
    if not ok:
        fails.append(label)


def numbers(text):
    """Number tokens in prose, with link targets removed and trailing commas or periods dropped."""
    return {n.rstrip(",.") for n in NUM.findall(LINK.sub(r"\1", text))}


raw = DRAFT.read_text()
outline_urls = set(re.findall(r"https?://[^\s)]+", OUTLINE.read_text()))
title, subtitle = raw.splitlines()[0], raw.splitlines()[2]
body = raw.split("\n---\n", 1)[1]

# -- links --
links = LINK.findall(raw)
check("links in draft", len(links), 6)
for text, url in links:
    check(f"link in outline: {url}", url in outline_urls, True)
check("every Substack URL in the outline is linked", set(PIECES) <= {u for _, u in links}, True)
for url, piece in PIECES.items():
    h1 = (REPO / piece / "draft.md").read_text().splitlines()[0][2:]
    text = next(t for t, u in links if u == url)
    check(f"link text opens {piece}'s H1", h1.startswith(text), True)

# -- numbers --
items = re.findall(r"^\d+\. (.+)$", body, re.M)
check("five list items", len(items), 5)
for item in items:
    url = LINK.search(item)[2]
    src = (REPO / PIECES[url] / "draft.md").read_text()
    have = numbers(src)
    for n in sorted(numbers(item)):
        check(f"{PIECES[url]} has {n}", n in have, True)
    for w in sorted(set(re.findall(WORDS, item, re.I))):
        check(f"{PIECES[url]} has '{w}'", re.search(rf"\b{w}\b", src, re.I) is not None, True)
rest = re.sub(r"^\d+\. .+$", "", body, flags=re.M)
check("no numbers outside the five list items", sorted(numbers(rest)), [])
check("no numbers in title or subtitle", sorted(numbers(title + subtitle)), [])
check("no stale counts (a number before calls/subscribers/readers/pieces/posts)",
      re.findall(r"\d[\d,]* (?:calls|subscribers|readers|pieces|posts|predictions)", raw), [])

# -- house rules --
sub = subtitle.strip("*")
print(f"subtitle: {len(sub)} characters"); check("subtitle under 150 characters", len(sub) < 150, True)
check("title", title, "# Start here")
check("em dashes", raw.count("—"), 0)
check("ordinals", re.findall(r"\b\d+(?:st|nd|rd|th)\b", raw), [])
first_section = body.split("\n## ", 1)[0]
check("week card slot right after the first section", first_section.strip().endswith("[Insert image: week card]"), True)
words = len(re.findall(r"[\w$][\w'$%.,:-]*", LINK.sub(r"\1", re.sub(r"^\[Insert [^\]]+\]$", "", body, flags=re.M))))
print(f"body: {words} words"); check("about 300 words (270-330)", 270 <= words <= 330, True)
check("personal piece flagged", "This is the personal one" in raw, True)
check("lockout piece flagged as part of the countdown", "weekly countdown to the lockout" in raw, True)
check("reply invitation", "Reply and tell me." in raw, True)

# -- paste page --
if PASTE.exists():
    page = PASTE.read_text()
    check("paste: live links match the draft", re.findall(r'<a href="([^"]+)">', page), [u for _, u in links])
    check("paste: no raw markdown links", "](" in page, False)
    check("paste: week card slot", "[Insert image: week card" in page, True)
    check("paste: subscribe slot", "[Insert subscribe button]" in page, True)
else:
    check("paste page exists (run build_paste.py)", False, True)
check(".gitignore lists the paste page", "start-here/paste-into-substack.html" in (REPO / ".gitignore").read_text().splitlines(), True)

print(f"\n{len(fails)} CHECK(S) FAILED: {fails}" if fails else "\nALL CHECKS PASS")
sys.exit(1 if fails else 0)
