#!/usr/bin/env python3
"""Check a Substack Notes file: every note under 600 characters, the stated count right, no em dashes,
hashtags or emoji, and every number in the text found in one of the source files given.

Usage: python3 tools/check_notes.py notes/<file>.md <source files...>
A number passes if it equals a CSV cell (to 0.05, so a rounded $16.5M matches 16.49), is a substring of a
CSV cell (dates, times, keys), or appears in a Markdown source verbatim or with M expanded to " million"."""
import csv, pathlib, re, sys

NUMBER = re.compile(r"\$?\d[\d,]*(?::\d{2})?(?:\.\d+)?(?:-\d+)?M?")
PHRASE = re.compile(r"\d{1,2}(?::\d{2})? (?:a|p)\.m\. ET|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}")
fails = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok: fails.append(name)

def load(path):
    p = pathlib.Path(path)
    if p.suffix == ".csv":
        return ("csv", [c for row in csv.reader(p.open()) for c in row])
    return ("text", re.sub(r"\s+", " ", p.read_text()))

def found(tok, sources):
    core = tok.replace("$", "").replace(",", "").rstrip("M")
    for name, (kind, data) in sources.items():
        if kind == "csv":
            for cell in data:
                if core == cell or core in cell:
                    return name
                try:
                    if abs(float(core) - float(cell)) <= 0.05: return name
                except ValueError:
                    pass
        else:
            if tok in data or tok.replace("M", " million") in data or core in data:
                return name
    return None

notes_path, *source_paths = sys.argv[1:]
sources = {p: load(p) for p in source_paths}
text = pathlib.Path(notes_path).read_text()
sections = re.split(r"^## ", text, flags=re.M)[1:]
check("notes file has five notes", len(sections) == 5, str(len(sections)))
for sec in sections:
    title, _, rest = sec.partition("\n")
    lines = [l for l in rest.strip().splitlines()]
    attach = [l for l in lines if l.startswith("Attach:")]
    count_line = [l for l in lines if re.fullmatch(r"\(\d+ characters\)", l.strip())]
    body = "\n".join(l for l in lines if not l.startswith("Attach:") and l not in count_line).strip()
    n = len(body)
    label = title.split(":")[0]
    check(f"{label}: has an Attach line", len(attach) == 1)
    check(f"{label}: {n} characters under 600", n < 600)
    stated = int(re.search(r"\d+", count_line[0]).group()) if count_line else -1
    check(f"{label}: stated count {stated} matches", stated == n)
    check(f"{label}: no em dashes", "—" not in body)
    check(f"{label}: no hashtags", not re.search(r"(^|\s)#\w", body))
    check(f"{label}: no emoji", all(ord(ch) < 0x2100 for ch in body))
    for tok in NUMBER.findall(body):
        tok = tok.rstrip(",")
        if tok.startswith("http") or len(tok.strip("$M")) == 0: continue
        src = found(tok, sources)
        check(f"{label}: {tok}", src is not None, src or "not in any source")
    for ph in PHRASE.findall(body):
        src = found(ph, sources)
        check(f"{label}: phrase {ph!r}", src is not None, src or "not in any source")
    for a in attach:
        path = re.search(r"`([^`]+)`", a)
        if path: check(f"{label}: attachment exists", pathlib.Path(path.group(1)).exists(), path.group(1))

if fails:
    print(f"\n{len(fails)} CHECK(S) FAILED: {fails}"); sys.exit(1)
print("\nALL CHECKS PASS")
